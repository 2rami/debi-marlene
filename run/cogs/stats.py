"""
서버 통계 수집 Cog

멤버 수, 메시지 수, 활동 로그를 수집하여 GCS에 저장합니다.
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import logging
from collections import defaultdict

from run.core.config import load_settings, save_settings

logger = logging.getLogger(__name__)


class StatsCog(commands.Cog):
    """서버 통계 수집 Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # 메모리 캐시 (주기적으로 GCS에 저장)
        self.message_counts = defaultdict(lambda: defaultdict(int))  # guild_id -> user_id -> count
        self.daily_messages = defaultdict(int)  # guild_id -> count
        self.member_logs = defaultdict(list)  # guild_id -> [log entries]
        self.save_stats_task.start()

    def cog_unload(self):
        self.save_stats_task.cancel()

    @tasks.loop(minutes=5)
    async def save_stats_task(self):
        """5분마다 통계를 GCS에 저장"""
        await self._save_stats_to_gcs()

    @save_stats_task.before_loop
    async def before_save_stats(self):
        await self.bot.wait_until_ready()

    async def _save_stats_to_gcs(self):
        """통계를 GCS에 저장"""
        if not self.message_counts and not self.member_logs:
            return

        try:
            settings = load_settings()
            today = datetime.now().strftime('%Y-%m-%d')

            for guild_id_str, user_counts in self.message_counts.items():
                if guild_id_str not in settings.get('guilds', {}):
                    continue

                guild_settings = settings['guilds'][guild_id_str]

                # stats 구조 초기화
                if 'stats' not in guild_settings:
                    guild_settings['stats'] = {
                        'daily': {},
                        'members': {},
                        'logs': []
                    }

                stats = guild_settings['stats']

                # 일별 통계
                if today not in stats['daily']:
                    guild = self.bot.get_guild(int(guild_id_str))
                    stats['daily'][today] = {
                        'messages': 0,
                        'member_count': guild.member_count if guild else 0,
                        'active_users': 0
                    }

                stats['daily'][today]['messages'] += self.daily_messages.get(guild_id_str, 0)
                stats['daily'][today]['active_users'] = len(user_counts)

                # 멤버별 메시지 수
                for user_id_str, count in user_counts.items():
                    if user_id_str not in stats['members']:
                        stats['members'][user_id_str] = {'messages': 0, 'name': ''}
                    stats['members'][user_id_str]['messages'] += count

                # 30일 이전 데이터 정리
                cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                stats['daily'] = {k: v for k, v in stats['daily'].items() if k >= cutoff}

            # 멤버 로그 저장
            for guild_id_str, logs in self.member_logs.items():
                if guild_id_str not in settings.get('guilds', {}):
                    continue

                guild_settings = settings['guilds'][guild_id_str]
                if 'stats' not in guild_settings:
                    guild_settings['stats'] = {'daily': {}, 'members': {}, 'logs': []}

                guild_settings['stats']['logs'].extend(logs)
                # 최근 1000개만 유지
                guild_settings['stats']['logs'] = guild_settings['stats']['logs'][-1000:]

            save_settings(settings, silent=True)

            # 캐시 초기화
            self.message_counts.clear()
            self.daily_messages.clear()
            self.member_logs.clear()

        except Exception as e:
            logger.error(f"[Stats] 통계 저장 실패: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """메시지 수 카운트"""
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)
        user_id = str(message.author.id)

        self.message_counts[guild_id][user_id] += 1
        self.daily_messages[guild_id] += 1

        # 멤버 이름 업데이트 (나중에 조회용)
        settings = load_settings()
        if guild_id in settings.get('guilds', {}):
            guild_settings = settings['guilds'][guild_id]
            if 'stats' in guild_settings and 'members' in guild_settings['stats']:
                if user_id in guild_settings['stats']['members']:
                    guild_settings['stats']['members'][user_id]['name'] = message.author.display_name

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """멤버 입장 로그"""
        if member.bot:
            return

        guild_id = str(member.guild.id)
        self.member_logs[guild_id].append({
            'type': 'join',
            'user_id': str(member.id),
            'user_name': member.display_name,
            'timestamp': datetime.now().isoformat()
        })

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """멤버 퇴장 로그"""
        if member.bot:
            return

        guild_id = str(member.guild.id)
        self.member_logs[guild_id].append({
            'type': 'leave',
            'user_id': str(member.id),
            'user_name': member.display_name,
            'timestamp': datetime.now().isoformat()
        })

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """역할 변경 로그"""
        if before.bot:
            return

        # 역할 변경 감지
        added_roles = set(after.roles) - set(before.roles)
        removed_roles = set(before.roles) - set(after.roles)

        if not added_roles and not removed_roles:
            return

        guild_id = str(after.guild.id)

        if added_roles:
            self.member_logs[guild_id].append({
                'type': 'role_add',
                'user_id': str(after.id),
                'user_name': after.display_name,
                'roles': [r.name for r in added_roles],
                'timestamp': datetime.now().isoformat()
            })

        if removed_roles:
            self.member_logs[guild_id].append({
                'type': 'role_remove',
                'user_id': str(after.id),
                'user_name': after.display_name,
                'roles': [r.name for r in removed_roles],
                'timestamp': datetime.now().isoformat()
            })

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """메시지 삭제 로그"""
        if not message.guild or message.author.bot:
            return

        guild_id = str(message.guild.id)
        self.member_logs[guild_id].append({
            'type': 'message_delete',
            'user_id': str(message.author.id),
            'user_name': message.author.display_name,
            'channel': message.channel.name,
            'timestamp': datetime.now().isoformat()
        })

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """메시지 수정 로그"""
        if not after.guild or after.author.bot:
            return

        if before.content == after.content:
            return

        guild_id = str(after.guild.id)
        self.member_logs[guild_id].append({
            'type': 'message_edit',
            'user_id': str(after.author.id),
            'user_name': after.author.display_name,
            'channel': after.channel.name,
            'timestamp': datetime.now().isoformat()
        })


async def setup(bot: commands.Bot):
    await bot.add_cog(StatsCog(bot))

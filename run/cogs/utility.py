"""
유틸리티 Cog

기타 명령어: 피드백, 공지, 핑
"""

import time
import discord
from discord import app_commands
from discord.ext import commands

from run.core import config
from run.utils.command_logger import log_command_usage

class UtilityCog(commands.Cog, name="기타"):
    """기타 유틸리티 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot_start_time = time.time()

    @commands.command(name="핑")
    async def ping(self, ctx: commands.Context):
        """봇 상태 확인 (프리픽스 명령어)"""
        # WebSocket 지연시간
        ws_latency = round(self.bot.latency * 1000)

        # API 지연시간 측정
        start = time.monotonic()
        msg = await ctx.send("측정 중...")
        api_latency = round((time.monotonic() - start) * 1000)

        # 업타임 계산
        uptime_sec = int(time.time() - self.bot_start_time)
        hours, remainder = divmod(uptime_sec, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}시간 {minutes}분 {seconds}초"

        # 서버/유저 수
        guild_count = len(self.bot.guilds)
        member_count = sum(g.member_count for g in self.bot.guilds if g.member_count)

        embed = discord.Embed(color=0x2ECC71)
        embed.add_field(name="WebSocket", value=f"{ws_latency}ms", inline=True)
        embed.add_field(name="API", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="업타임", value=uptime_str, inline=True)
        embed.add_field(name="서버", value=f"{guild_count}개", inline=True)
        embed.add_field(name="유저", value=f"{member_count:,}명", inline=True)

        await msg.edit(content=None, embed=embed)

    @app_commands.command(name="도움말", description="데비&마를렌이 할 수 있는 모든 명령어")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="데비&마를렌 명령어",
            description="이터널리턴 전적 + AI 대화 + 음성/음악 + 퀴즈를 한 봇에서.\n자연어로 말 걸어도 봇이 알아들어요. 예: `데비야 전적 보여줘`",
            color=0xFFB6C1,
        )
        embed.add_field(
            name="AI 대화",
            value=(
                "`/대화` — 데비&마를렌과 대화 (이터널리턴 정보·잡담·검색 자동)\n"
                "채널에서 `데비야` `마를렌아` 호명해도 응답"
            ),
            inline=False,
        )
        embed.add_field(
            name="이터널리턴",
            value=(
                "`/전적` — 플레이어 전적 검색\n"
                "`/통계` — 캐릭터별 통계 (다이아+)\n"
                "`/시즌` — 현재 시즌 정보\n"
                "`/동접` — 현재 동접자 수"
            ),
            inline=False,
        )
        embed.add_field(
            name="음성·음악",
            value=(
                "`/tts` — 봇이 음성 채널에 입장 (TTS)\n"
                "`/음악` — YouTube 음악 재생\n"
                "`/듣기` — 음성채널에서 유저 음성 듣기\n"
                "`/듣기중지` — 듣기 중지"
            ),
            inline=False,
        )
        embed.add_field(
            name="재미",
            value=(
                "`/퀴즈` — 퀴즈 게임 (이터널리턴 / 노래)\n"
                "`/크레딧` — 내 크레딧 지갑 (도박·출석은 대시보드)"
            ),
            inline=False,
        )
        embed.add_field(
            name="설정·기타",
            value=(
                "`/설정` — 서버 설정 (공지·TTS·알림·대시보드)\n"
                "`/피드백` — 봇 개발자에게 피드백"
            ),
            inline=False,
        )
        embed.set_footer(text="문의·버그 제보는 /피드백")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        try:
            await log_command_usage(
                command_name="도움말",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
            )
        except Exception:
            pass

    @app_commands.command(name="피드백", description="봇 개발자에게 피드백을 보냅니다")
    @app_commands.describe(내용="보낼 피드백 내용")
    async def feedback(self, interaction: discord.Interaction, 내용: str):
        OWNER_ID = config.OWNER_ID

        if not OWNER_ID:
            return await interaction.response.send_message(
                "죄송해요, 피드백 기능이 아직 설정되지 않았어요.",
                ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        await log_command_usage(
            command_name="피드백",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id if interaction.guild else None,
            guild_name=interaction.guild.name if interaction.guild else None,
            channel_id=interaction.channel_id,
            channel_name=interaction.channel.name if interaction.channel else None,
            args={"내용": 내용[:50] + "..." if len(내용) > 50 else 내용}
        )

        try:
            owner = await self.bot.fetch_user(int(OWNER_ID))
            embed = discord.Embed(title="새로운 피드백 도착!", description=내용, color=0xFFB6C1)
            embed.set_author(
                name=f"{interaction.user.name} ({interaction.user.id})",
                icon_url=interaction.user.display_avatar.url
            )
            if interaction.guild:
                embed.add_field(name="서버", value=f"{interaction.guild.name} ({interaction.guild.id})", inline=False)
            else:
                embed.add_field(name="서버", value="개인 메시지(DM)", inline=False)
            await owner.send(embed=embed)

            # 피드백 보낸 사람한테 봇이 DM (웹패널에서 확인 가능)
            try:
                from run.core.bot import gateway_dm_messages
                from datetime import datetime, timezone
                dm_msg = await interaction.user.send(
                    f"**[피드백 접수]**\n"
                    f"보낸 내용: {내용}\n\n"
                    f"피드백이 개발자에게 전달되었습니다!"
                )
                # gateway_dm_messages에 추가 (웹패널 표시용)
                gateway_dm_messages.append({
                    'id': str(dm_msg.id),
                    'content': dm_msg.content,
                    'author': {
                        'id': str(self.bot.user.id),
                        'username': self.bot.user.display_name,
                        'avatar': self.bot.user.display_avatar.url
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'type': 'dm_sent'
                })
            except Exception:
                pass

            await interaction.followup.send("소중한 피드백 고마워요! 개발자에게 잘 전달했어요.", ephemeral=True)
        except (ValueError, discord.NotFound):
            await interaction.followup.send("죄송해요, 개발자 정보를 찾을 수 없어서 피드백을 보낼 수 없어요.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("개발자에게 DM을 보낼 수 없도록 설정되어 있어 전달에 실패했어요.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"피드백 전송 중 오류가 발생했어요: {e}", ephemeral=True)



async def setup(bot: commands.Bot):
    await bot.add_cog(UtilityCog(bot))

#!/usr/bin/env python3
"""
Discord Gateway 서비스 - BotClient처럼 실시간 Discord 연결
실제 Discord 클라이언트처럼 Gateway WebSocket 연결로 실시간 데이터 수집
"""

import discord
import asyncio
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import sys
import os

# config 모듈 import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from run import config
except ImportError:
    import config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscordGatewayService:
    """Discord Gateway WebSocket 연결을 통한 실시간 데이터 서비스"""
    
    def __init__(self, token: str):
        # 모든 Privileged Intents 활성화 (BotClient처럼)
        intents = discord.Intents.all()  # 모든 인텐트 활성화
        
        self.client = discord.Client(intents=intents)
        self.token = token
        self.guild_data = {}
        self.user_data = {}
        self.dm_messages = []  # DM 메시지 저장
        self.command_logs = []  # 명령어 사용 기록
        self.ready = False
        self.last_update = None
        
        # 이벤트 핸들러 등록
        self.setup_event_handlers()
        
    def setup_event_handlers(self):
        """Discord 이벤트 핸들러 설정"""
        
        @self.client.event
        async def on_ready():
            logger.info(f'🤖 Discord Gateway 연결 완료: {self.client.user}')
            logger.info(f'📊 연결된 서버 수: {len(self.client.guilds)}')
            
            # 모든 서버 데이터 수집
            await self.collect_all_guild_data()
            self.ready = True
            self.last_update = datetime.now()
            
            logger.info(f'✅ 초기 데이터 수집 완료')
            
        @self.client.event
        async def on_guild_join(guild):
            logger.info(f'🏠 새 서버 참가: {guild.name} ({guild.id})')
            await self.update_guild_data(guild)
            
        @self.client.event
        async def on_guild_remove(guild):
            logger.info(f'🚪 서버 나감: {guild.name} ({guild.id})')
            if str(guild.id) in self.guild_data:
                del self.guild_data[str(guild.id)]
                
        @self.client.event
        async def on_member_join(member):
            logger.info(f'👋 멤버 참가: {member} -> {member.guild.name}')
            await self.update_guild_data(member.guild)
            
        @self.client.event
        async def on_member_remove(member):
            logger.info(f'👋 멤버 탈퇴: {member} -> {member.guild.name}')
            await self.update_guild_data(member.guild)
            
        @self.client.event
        async def on_presence_update(before, after):
            # 온라인 상태 변화 감지
            if before.status != after.status:
                await self.update_guild_data(after.guild)
                
        @self.client.event
        async def on_message(message):
            # 봇 자신의 메시지는 무시
            if message.author == self.client.user:
                return

            # DM 메시지 처리
            if isinstance(message.channel, discord.DMChannel):
                dm_data = {
                    'id': str(message.id),
                    'content': message.content,
                    'author': {
                        'id': str(message.author.id),
                        'username': message.author.display_name,
                        'avatar': message.author.display_avatar.url
                    },
                    'timestamp': message.created_at.isoformat(),
                    'type': 'dm_received'
                }

                self.dm_messages.append(dm_data)

                # 최대 500개까지만 저장 (메모리 절약)
                if len(self.dm_messages) > 500:
                    self.dm_messages = self.dm_messages[-400:]

                logger.info(f'💌 DM 수신: {message.author.display_name} - {message.content[:50]}...')

                # DM 채널이 private_channels에 없다면 강제로 DM 채널을 생성/가져오기
                try:
                    if message.channel not in self.client.private_channels:
                        logger.info(f'🔄 DM 채널을 private_channels에 추가 중: {message.author.display_name}')
                        # create_dm()을 호출해서 채널을 캐시에 추가
                        await message.author.create_dm()
                        logger.info(f'✅ DM 채널이 private_channels에 추가됨: {len(self.client.private_channels)}개')
                except Exception as e:
                    logger.error(f'❌ DM 채널 추가 실패: {e}')

                # GCS에 DM 채널 정보 저장
                try:
                    settings = config.load_settings()
                    user_id = str(message.author.id)

                    # users 키가 없으면 생성
                    if 'users' not in settings:
                        settings['users'] = {}

                    # 해당 유저가 없으면 생성
                    if user_id not in settings['users']:
                        settings['users'][user_id] = {}

                    # DM 채널 ID 저장
                    settings['users'][user_id]['dm_channel_id'] = str(message.channel.id)
                    settings['users'][user_id]['user_name'] = message.author.display_name
                    settings['users'][user_id]['last_dm'] = datetime.now().isoformat()

                    # GCS에 저장
                    config.save_settings(settings)
                    logger.info(f'💾 DM 채널 정보 GCS에 저장: {message.author.display_name} ({message.channel.id})')
                except Exception as e:
                    logger.error(f'❌ DM 채널 정보 GCS 저장 실패: {e}')
            
            # 명령어 사용 기록 (서버 메시지 중 명령어)
            if message.content.startswith(('/목록', '/놀이', '/추천', '/탈출', '/유튜브')):
                command_data = {
                    'id': str(message.id),
                    'command': message.content.split()[0],
                    'full_content': message.content,
                    'author': {
                        'id': str(message.author.id),
                        'username': message.author.display_name,
                        'avatar': message.author.display_avatar.url
                    },
                    'guild': {
                        'id': str(message.guild.id) if message.guild else None,
                        'name': message.guild.name if message.guild else 'DM'
                    },
                    'channel': {
                        'id': str(message.channel.id),
                        'name': message.channel.name if hasattr(message.channel, 'name') else 'DM'
                    },
                    'timestamp': message.created_at.isoformat()
                }
                
                self.command_logs.append(command_data)
                
                # 최대 1000개까지만 저장
                if len(self.command_logs) > 1000:
                    self.command_logs = self.command_logs[-800:]
                    
                logger.info(f'⚡ 명령어 사용: {message.author.display_name} - {message.content}')
                
    async def collect_all_guild_data(self):
        """모든 서버의 데이터를 수집"""
        for guild in self.client.guilds:
            await self.update_guild_data(guild)
            
    async def update_guild_data(self, guild: discord.Guild):
        """특정 서버의 데이터 업데이트"""
        try:
            # 온라인 멤버 수 계산
            online_members = 0
            offline_members = 0
            
            for member in guild.members:
                if member.status == discord.Status.offline:
                    offline_members += 1
                else:
                    online_members += 1
                    
            # 채널 정보 수집
            text_channels = []
            for channel in guild.text_channels:
                text_channels.append({
                    'id': str(channel.id),
                    'name': channel.name,
                    'position': channel.position,
                    'type': 'text'
                })
                
            # 서버 데이터 업데이트
            self.guild_data[str(guild.id)] = {
                'id': str(guild.id),
                'name': guild.name,
                'member_count': guild.member_count,  # 정확한 멤버 수!
                'online_count': online_members,      # 실시간 온라인 수!
                'offline_count': offline_members,
                'icon': guild.icon.url if guild.icon else None,
                'owner_id': str(guild.owner_id) if guild.owner_id else None,
                'created_at': guild.created_at.isoformat(),
                'channels': text_channels[:20],  # 최대 20개 채널
                'last_updated': datetime.now().isoformat(),
                'data_source': 'Gateway WebSocket'
            }
            
            logger.debug(f'📊 {guild.name}: {guild.member_count}명 (온라인: {online_members})')
            
        except Exception as e:
            logger.error(f'❌ 서버 데이터 업데이트 실패 {guild.name}: {e}')
            
    def get_channel_messages_sync(self, channel_id: str, limit: int = 50) -> List[Dict]:
        """채널의 메시지 가져오기 (동기 버전)"""
        try:
            channel = self.client.get_channel(int(channel_id))
            if not channel:
                logger.warning(f'채널 {channel_id}를 찾을 수 없음')
                return []

            # 비동기 작업을 Discord 클라이언트의 이벤트 루프에서 실행
            future = asyncio.run_coroutine_threadsafe(
                self._get_channel_messages_async(channel_id, limit),
                self.client.loop
            )

            # 결과 대기 (최대 10초)
            try:
                messages = future.result(timeout=10)
                return messages
            except asyncio.TimeoutError:
                logger.error(f'❌ 메시지 로드 타임아웃 {channel_id}')
                return []

        except Exception as e:
            logger.error(f'❌ 메시지 로드 실패 {channel_id}: {e}')
            return []

    async def _get_channel_messages_async(self, channel_id: str, limit: int = 50) -> List[Dict]:
        """채널의 메시지 가져오기 (비동기 내부 함수)"""
        try:
            channel = self.client.get_channel(int(channel_id))
            if not channel:
                return []

            messages = []
            async for message in channel.history(limit=limit):
                messages.append({
                    'id': str(message.id),
                    'content': message.content,
                    'author': {
                        'id': str(message.author.id),
                        'username': message.author.display_name,
                        'avatar': message.author.display_avatar.url
                    },
                    'timestamp': message.created_at.isoformat(),
                    'attachments': [
                        {
                            'url': att.url,
                            'filename': att.filename,
                            'size': att.size,
                            'content_type': att.content_type
                        } for att in message.attachments
                    ],
                    'embeds': [embed.to_dict() for embed in message.embeds]
                })

            # 시간순 정렬 (최신이 아래)
            messages.reverse()
            return messages

        except Exception as e:
            logger.error(f'❌ 내부 메시지 로드 실패 {channel_id}: {e}')
            return []

    async def get_channel_messages(self, channel_id: str, limit: int = 50) -> List[Dict]:
        """채널의 메시지 가져오기 (BotClient처럼) - 비동기 버전"""
        return await self._get_channel_messages_async(channel_id, limit)
            
    async def send_message(self, channel_id: str, content: str) -> Optional[Dict]:
        """채널에 메시지 전송"""
        try:
            channel = self.client.get_channel(int(channel_id))
            if not channel:
                return None
                
            message = await channel.send(content)
            
            return {
                'id': str(message.id),
                'content': message.content,
                'author': {
                    'id': str(message.author.id),
                    'username': message.author.display_name,
                    'avatar': message.author.display_avatar.url
                },
                'timestamp': message.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f'❌ 메시지 전송 실패 {channel_id}: {e}')
            return None
            
    async def get_dm_channels(self) -> List[Dict]:
        """봇이 접근할 수 있는 DM 채널 목록 가져오기 (Gateway private_channels + GCS)"""
        try:
            dm_channels = []
            seen_channel_ids = set()

            # 1. Gateway의 private_channels에서 실제로 열려있는 DM 채널 가져오기
            logger.info(f'🔍 Gateway private_channels 확인 중...')

            # GCS에 저장할 새 채널 목록
            settings = config.load_settings()
            if 'users' not in settings:
                settings['users'] = {}
            settings_changed = False

            for channel in self.client.private_channels:
                if isinstance(channel, discord.DMChannel):
                    try:
                        recipient = channel.recipient
                        if recipient:
                            channel_id = str(channel.id)
                            user_id = str(recipient.id)
                            seen_channel_ids.add(channel_id)

                            dm_channels.append({
                                'id': channel_id,
                                'type': 'dm',
                                'recipient': {
                                    'id': user_id,
                                    'username': recipient.display_name,
                                    'avatar': recipient.display_avatar.url
                                },
                                'last_message_id': None
                            })

                            # Gateway에서 가져온 채널도 GCS에 저장
                            if user_id not in settings['users']:
                                settings['users'][user_id] = {}

                            if settings['users'][user_id].get('dm_channel_id') != channel_id:
                                settings['users'][user_id]['dm_channel_id'] = channel_id
                                settings['users'][user_id]['user_name'] = recipient.display_name
                                settings['users'][user_id]['last_updated'] = datetime.now().isoformat()
                                settings_changed = True
                                logger.info(f'💾 Gateway DM 채널 GCS에 저장: {recipient.display_name} ({channel_id})')
                            else:
                                logger.info(f'✅ Gateway DM 채널: {recipient.display_name} (이미 GCS에 있음)')
                    except Exception as e:
                        logger.error(f'⚠️ Gateway DM 채널 처리 실패: {e}')
                        continue

            # 변경사항이 있으면 GCS에 저장
            if settings_changed:
                try:
                    config.save_settings(settings)
                    logger.info(f'✅ Gateway DM 채널 정보 GCS 저장 완료')
                except Exception as e:
                    logger.error(f'❌ Gateway DM 채널 정보 GCS 저장 실패: {e}')

            # 2. GCS에서 DM 채널 정보 추가 로드 (중복 제거)
            settings = config.load_settings()
            users = settings.get('users', {})

            for user_id, user_info in users.items():
                if 'dm_channel_id' in user_info:
                    channel_id = user_info['dm_channel_id']

                    # 이미 Gateway에서 로드한 채널이면 스킵
                    if channel_id in seen_channel_ids:
                        continue

                    try:
                        # Discord API로 유저 정보 가져오기
                        user = await self.client.fetch_user(int(user_id))

                        dm_channels.append({
                            'id': channel_id,
                            'type': 'dm',
                            'recipient': {
                                'id': str(user.id),
                                'username': user_info.get('user_name', user.display_name),
                                'avatar': user.display_avatar.url
                            },
                            'last_message_id': None
                        })
                        seen_channel_ids.add(channel_id)
                        logger.info(f'✅ GCS DM 채널: {user_info.get("user_name", "Unknown")}')
                    except Exception as e:
                        logger.error(f'⚠️ GCS 유저 정보 가져오기 실패 ({user_id}): {e}')
                        continue

            logger.info(f'📦 총 {len(dm_channels)}개 DM 채널 로드 완료 (Gateway: {len([c for c in dm_channels if c["id"] not in [u.get("dm_channel_id") for u in users.values() if "dm_channel_id" in u]])}개, GCS: {len([c for c in dm_channels if c["id"] in [u.get("dm_channel_id") for u in users.values() if "dm_channel_id" in u]])}개)')
            return dm_channels
        except Exception as e:
            logger.error(f'❌ DM 채널 목록 로드 실패: {e}')
            return []
            
    async def send_dm(self, user_id: str, content: str) -> Optional[Dict]:
        """사용자에게 DM 전송"""
        try:
            user = self.client.get_user(int(user_id))
            if not user:
                # 사용자를 찾을 수 없으면 fetch 시도
                user = await self.client.fetch_user(int(user_id))

            if not user:
                logger.error(f'❌ 사용자를 찾을 수 없음: {user_id}')
                return None

            message = await user.send(f"[웹패널] {content}")

            # DM 전송 성공 시 channel ID를 GCS에 저장
            try:
                settings = config.load_settings()
                if 'users' not in settings:
                    settings['users'] = {}

                if user_id not in settings['users']:
                    settings['users'][user_id] = {}

                # DM 채널 ID 저장
                settings['users'][user_id]['dm_channel_id'] = str(message.channel.id)
                settings['users'][user_id]['user_name'] = user.display_name
                settings['users'][user_id]['last_dm_sent'] = datetime.now().isoformat()

                config.save_settings(settings)
                logger.info(f'💾 DM 전송 후 채널 정보 GCS에 저장: {user.display_name} ({message.channel.id})')
            except Exception as e:
                logger.error(f'❌ DM 채널 정보 GCS 저장 실패: {e}')

            return {
                'id': str(message.id),
                'content': message.content,
                'author': {
                    'id': str(message.author.id),
                    'username': message.author.display_name,
                    'avatar': message.author.display_avatar.url
                },
                'timestamp': message.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f'❌ DM 전송 실패 {user_id}: {e}')
            return None
            
    def get_guild_data(self) -> Dict:
        """모든 서버 데이터 반환"""
        return self.guild_data.copy()

    def get_guild(self, guild_id: str) -> Optional[Dict]:
        """특정 서버 데이터 반환"""
        return self.guild_data.get(guild_id)

    def is_ready(self) -> bool:
        """Gateway 연결 준비 상태"""
        return self.ready and self.client.is_ready()

    def get_guild_members_sync(self, guild_id: str, channel_id: str = None) -> List[Dict]:
        """서버 멤버 목록 가져오기 (동기 버전)

        Args:
            guild_id: 서버 ID
            channel_id: 채널 ID (선택사항, 지정하면 해당 채널 접근 가능한 멤버만 반환)
        """
        try:
            guild = self.client.get_guild(int(guild_id))
            if not guild:
                logger.warning(f'서버 {guild_id}를 찾을 수 없음')
                return []

            # 채널 지정 시 해당 채널 가져오기
            channel = None
            if channel_id:
                channel = guild.get_channel(int(channel_id))
                if not channel:
                    logger.warning(f'채널 {channel_id}를 찾을 수 없음')

            members = []
            for member in guild.members:
                # 채널이 지정된 경우 권한 확인
                if channel:
                    perms = channel.permissions_for(member)
                    if not perms.view_channel:
                        continue  # 채널을 볼 수 없는 멤버는 제외

                status = 'online'
                if member.status == discord.Status.offline:
                    status = 'offline'
                elif member.status == discord.Status.idle:
                    status = 'idle'
                elif member.status == discord.Status.dnd:
                    status = 'dnd'

                # 멤버의 최상위 역할 색상 찾기
                role_color = None
                for role in reversed(member.roles):  # 역순으로 순회 (최상위 역할부터)
                    if role.color.value != 0:  # 색상이 설정된 역할 찾기
                        role_color = f'#{role.color.value:06x}'
                        break

                members.append({
                    'id': str(member.id),
                    'username': member.name,
                    'display_name': member.display_name,
                    'discriminator': member.discriminator,
                    'avatar': member.display_avatar.url,
                    'status': status,
                    'bot': member.bot,
                    'roles': [str(role.id) for role in member.roles],
                    'role_color': role_color,
                    'top_role': str(member.top_role.id) if member.top_role else None,
                    'joined_at': member.joined_at.isoformat() if member.joined_at else None
                })

            return members

        except Exception as e:
            logger.error(f'❌ 멤버 목록 로드 실패 {guild_id}: {e}')
            return []

    def get_guild_roles_sync(self, guild_id: str) -> List[Dict]:
        """서버 역할 목록 가져오기 (동기 버전)"""
        try:
            guild = self.client.get_guild(int(guild_id))
            if not guild:
                logger.warning(f'서버 {guild_id}를 찾을 수 없음')
                return []

            roles = []
            for role in guild.roles:
                roles.append({
                    'id': str(role.id),
                    'name': role.name,
                    'color': f'#{role.color.value:06x}' if role.color.value != 0 else None,
                    'position': role.position,
                    'permissions': role.permissions.value,
                    'hoist': role.hoist,  # 역할을 멤버 목록에서 따로 표시할지
                    'mentionable': role.mentionable,
                    'member_count': len(role.members)
                })

            return sorted(roles, key=lambda x: x['position'], reverse=True)

        except Exception as e:
            logger.error(f'❌ 역할 목록 로드 실패 {guild_id}: {e}')
            return []
        
    def get_stats(self) -> Dict:
        """전체 통계 반환"""
        if not self.ready:
            return {
                'status': '연결 중...',
                'guilds': 0,
                'total_members': 0,
                'online_members': 0,
                'dm_messages': 0,
                'command_uses': 0
            }
            
        total_members = sum(g['member_count'] for g in self.guild_data.values())
        online_members = sum(g['online_count'] for g in self.guild_data.values())
        
        return {
            'status': '🟢 실시간 연결',
            'guilds': len(self.guild_data),
            'total_members': total_members,
            'online_members': online_members,
            'dm_messages': len(self.dm_messages),
            'command_uses': len(self.command_logs),
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'data_source': 'Discord Gateway WebSocket'
        }
        
    def get_dm_messages(self, limit: int = 100) -> List[Dict]:
        """수신된 DM 메시지 목록 반환 (최신순)"""
        return sorted(self.dm_messages, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
    def get_command_logs(self, limit: int = 100) -> List[Dict]:
        """명령어 사용 기록 반환 (최신순)"""
        return sorted(self.command_logs, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
    def get_recent_activity(self) -> Dict:
        """최근 활동 요약"""
        from datetime import datetime, timedelta
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        recent_dms = [dm for dm in self.dm_messages 
                     if datetime.fromisoformat(dm['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None) > one_hour_ago]
        recent_commands = [cmd for cmd in self.command_logs 
                          if datetime.fromisoformat(cmd['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None) > one_hour_ago]
        
        daily_dms = [dm for dm in self.dm_messages 
                    if datetime.fromisoformat(dm['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None) > one_day_ago]
        daily_commands = [cmd for cmd in self.command_logs 
                         if datetime.fromisoformat(cmd['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None) > one_day_ago]
        
        return {
            'last_hour': {
                'dm_messages': len(recent_dms),
                'command_uses': len(recent_commands)
            },
            'last_24h': {
                'dm_messages': len(daily_dms),
                'command_uses': len(daily_commands)
            },
            'most_used_commands': self._get_command_stats(),
            'active_users': self._get_active_users()
        }
        
    def _get_command_stats(self) -> List[Dict]:
        """명령어 사용 통계"""
        command_counts = {}
        for log in self.command_logs:
            cmd = log['command']
            if cmd in command_counts:
                command_counts[cmd] += 1
            else:
                command_counts[cmd] = 1
                
        return sorted([{'command': cmd, 'count': count} 
                      for cmd, count in command_counts.items()], 
                     key=lambda x: x['count'], reverse=True)[:10]
        
    def _get_active_users(self) -> List[Dict]:
        """활성 사용자 통계"""
        user_activity = {}
        
        # DM 활동
        for dm in self.dm_messages:
            user_id = dm['author']['id']
            if user_id not in user_activity:
                user_activity[user_id] = {
                    'id': user_id,
                    'username': dm['author']['username'],
                    'avatar': dm['author']['avatar'],
                    'dm_count': 0,
                    'command_count': 0
                }
            user_activity[user_id]['dm_count'] += 1
            
        # 명령어 활동
        for cmd in self.command_logs:
            user_id = cmd['author']['id']
            if user_id not in user_activity:
                user_activity[user_id] = {
                    'id': user_id,
                    'username': cmd['author']['username'],
                    'avatar': cmd['author']['avatar'],
                    'dm_count': 0,
                    'command_count': 0
                }
            user_activity[user_id]['command_count'] += 1
            
        return sorted(list(user_activity.values()), 
                     key=lambda x: x['dm_count'] + x['command_count'], 
                     reverse=True)[:20]
        
    async def start(self):
        """Gateway 서비스 시작"""
        try:
            logger.info(f'🚀 Discord Gateway 서비스 시작...')
            await self.client.start(self.token)
        except Exception as e:
            logger.error(f'❌ Gateway 시작 실패: {e}')
            raise
            
    async def close(self):
        """Gateway 연결 종료"""
        if not self.client.is_closed():
            await self.client.close()
            logger.info('🔌 Discord Gateway 연결 종료')

# 전역 서비스 인스턴스
_gateway_service: Optional[DiscordGatewayService] = None

def get_gateway_service() -> Optional[DiscordGatewayService]:
    """전역 Gateway 서비스 인스턴스 반환"""
    return _gateway_service

async def start_gateway_service(token: str):
    """Gateway 서비스 시작 (비동기)"""
    global _gateway_service
    
    if _gateway_service:
        await _gateway_service.close()
        
    _gateway_service = DiscordGatewayService(token)
    await _gateway_service.start()

def start_gateway_service_thread(token: str):
    """Gateway 서비스를 별도 스레드에서 시작"""
    def run_service():
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(start_gateway_service(token))
        except Exception as e:
            logger.error(f'❌ Gateway 서비스 스레드 오류: {e}')
        finally:
            loop.close()
    
    thread = threading.Thread(target=run_service, daemon=True)
    thread.start()
    logger.info('🧵 Gateway 서비스 스레드 시작됨')
    
    # 연결 대기
    max_wait = 30  # 최대 30초 대기
    waited = 0
    while waited < max_wait:
        if _gateway_service and _gateway_service.is_ready():
            logger.info('✅ Gateway 서비스 준비 완료')
            return True
        time.sleep(1)
        waited += 1
        
    logger.warning('⚠️ Gateway 서비스 연결 대기 시간 초과')
    return False
"""
Discord 봇 인스턴스 및 이벤트 핸들러

이 모듈에는 봇 인스턴스와 모든 이벤트 핸들러가 포함되어 있습니다.
"""

import asyncio
import aiohttp
import discord
import os
import json
import time
from discord.ext import commands, tasks
from datetime import datetime

from run.core import config
from run.services.eternal_return.api_client import initialize_game_data, set_bot_instance
from run.services import youtube_service
from run.views.welcome_view import WelcomeLayoutView

# Opus 라이브러리 로드 (음성 채널 지원)
if not discord.opus.is_loaded():
    import platform
    _opus_paths = {
        'Windows': ['opus', 'libopus-0', 'libopus',
                    os.path.join(os.environ.get('CONDA_PREFIX', ''), 'Library', 'bin', 'opus.dll'),
                    os.path.expanduser('~/miniconda3/Library/bin/opus.dll')],
        'Darwin': ['/opt/homebrew/lib/libopus.dylib', '/usr/local/lib/libopus.dylib'],
        'Linux': ['libopus.so.0', 'libopus.so', '/usr/lib/x86_64-linux-gnu/libopus.so.0'],
    }
    for path in _opus_paths.get(platform.system(), ['opus']):
        try:
            discord.opus.load_opus(path)
            print(f"[완료] Opus 로드: {path}", flush=True)
            break
        except Exception as e:
            print(f"[Opus] {path} -> {e}", flush=True)
    if not discord.opus.is_loaded():
        print("[경고] Opus 로드 실패 - 음성 기능 제한", flush=True)


# Discord 봇 설정
intents = discord.Intents.all()  # 모든 Intents 활성화 (Gateway 기능용)


class DebiMarleneBot(commands.Bot):
    async def setup_hook(self):
        """봇 연결 전 Cog 등록 (bot.run() 내부에서 호출됨)"""
        from run.cogs import setup_all_cogs
        await setup_all_cogs(self)

    async def close(self):
        """봇 종료 시 TTS 사용 중인 채널에 재시작 알림 전송"""
        try:
            from run.services.voice_manager import voice_manager
            for guild_id, vc in list(voice_manager.voice_clients.items()):
                if vc.is_connected():
                    guild = vc.guild
                    guild_settings = config.get_guild_settings(guild.id)
                    tts_channel_id = guild_settings.get("tts_channel_id")
                    if tts_channel_id:
                        channel = guild.get_channel(int(tts_channel_id))
                        if channel:
                            try:
                                await channel.send(
                                    "봇이 재시작됩니다. 업데이트 후 `/tts`를 다시 입력해주세요!"
                                )
                            except Exception:
                                pass
        except Exception as e:
            print(f"[경고] 종료 알림 전송 실패: {e}", flush=True)
        await super().close()


bot = DebiMarleneBot(command_prefix='!', intents=intents, help_command=None)

# Gateway 데이터 저장용 전역 변수
gateway_guild_data = {}  # 서버 데이터
gateway_dm_messages = []  # DM 메시지

# 환영 메시지를 보낸 서버를 추적하는 세트 (세션 중 중복 방지용)
welcomed_guilds = set()
# 환영 메시지 전송 시간을 추적 (빠른 중복 이벤트 방지)
welcome_timestamps = {}
# YouTube 태스크 시작 여부 (on_ready 중복 호출 방지)
_youtube_task_started = False
# 스티키 메시지
_sticky_cooldowns = {}
STICKY_COOLDOWN_SECONDS = 5


async def update_guild_data_to_gcs(guild: discord.Guild):
    """특정 서버 데이터를 GCS에 업데이트"""
    try:
        # 서버 데이터
        guild_data = {
            'id': str(guild.id),
            'name': guild.name,
            'member_count': guild.member_count,
            'icon': guild.icon.url if guild.icon else None,
            'owner_id': str(guild.owner_id) if guild.owner_id else None,
            'last_updated': datetime.now().isoformat(),
            'data_source': 'Bot Gateway'
        }

        # 전역 변수에 저장
        gateway_guild_data[str(guild.id)] = guild_data

        # GCS에 저장
        settings = config.load_settings()
        if 'guilds' not in settings:
            settings['guilds'] = {}

        # 기존 설정 유지하면서 실시간 데이터만 업데이트
        if str(guild.id) in settings['guilds']:
            settings['guilds'][str(guild.id)].update({
                'GUILD_NAME': guild.name,
                '멤버수': guild.member_count,
                'GUILD_ICON_HASH': guild.icon.key if guild.icon else None,
                'last_updated': datetime.now().isoformat()
            })
        else:
            settings['guilds'][str(guild.id)] = {
                'GUILD_NAME': guild.name,
                '멤버수': guild.member_count,
                'GUILD_ICON_HASH': guild.icon.key if guild.icon else None,
                'last_updated': datetime.now().isoformat()
            }

        config.save_settings(settings)
        print(f"[정보] 서버 데이터 GCS 저장: {guild.name} ({guild.member_count}명)")

    except Exception as e:
        print(f"[오류] 서버 데이터 업데이트 실패 {guild.name}: {e}")


async def update_server_info_to_gcs():
    """서버 정보를 GCS settings.json에 업데이트"""
    try:
        # 사용자 정보 수집
        users_data = []
        seen_user_ids = set()

        # YouTube 구독자 정보
        subscribers = config.get_youtube_subscribers()
        for user_id in subscribers:
            if user_id not in seen_user_ids:
                seen_user_ids.add(user_id)
                try:
                    # bot.fetch_user 사용하여 API로 실제 정보 가져오기
                    user = await bot.fetch_user(user_id)
                    if user:
                        # display_name 사용하여 실제 닉네임/이름 가져오기
                        user_name = user.display_name or user.global_name or user.name
                        users_data.append({
                            'id': str(user_id),
                            'name': user_name,
                            'type': 'YouTube 구독자',
                            'last_seen': '2025-08-25',
                            'servers': ['구독자 (개인 메시지)']
                        })
                    else:
                        users_data.append({
                            'id': str(user_id),
                            'name': f"User_{str(user_id)[-4:]}",
                            'type': 'YouTube 구독자',
                            'last_seen': '알 수 없음',
                            'servers': ['구독자 (개인 메시지)']
                        })
                except:
                    users_data.append({
                        'id': str(user_id),
                        'name': f"User_{str(user_id)[-4:]}",
                        'type': 'YouTube 구독자',
                        'last_seen': '알 수 없음',
                        'servers': ['구독자 (개인 메시지)']
                    })

        # 실제 서버 멤버들 중에서 봇과 상호작용한 사용자들 추가
        interaction_users = config.get_interaction_users()  # 실제 상호작용한 사용자 목록

        for user_id in interaction_users:
            if user_id not in seen_user_ids:
                seen_user_ids.add(user_id)
                try:
                    user = await bot.fetch_user(user_id)
                    if user:
                        user_name = user.display_name or user.global_name or user.name
                        # 해당 사용자가 속한 서버들 찾기
                        user_servers = []
                        for guild in bot.guilds:
                            try:
                                member = guild.get_member(user_id)
                                if member:
                                    user_servers.append(guild.name)
                            except:
                                pass

                        users_data.append({
                            'id': str(user_id),
                            'name': user_name,
                            'type': '일반 사용자',
                            'last_seen': '2025-08-25',
                            'servers': user_servers if user_servers else ['알 수 없음']
                        })
                except:
                    users_data.append({
                        'id': str(user_id),
                        'name': f"User_{str(user_id)[-4:]}",
                        'type': '일반 사용자',
                        'last_seen': '알 수 없음',
                        'servers': ['알 수 없음']
                    })

        server_data = {
            'updated_at': datetime.now().isoformat(),
            'total_servers': len(bot.guilds),
            'total_members': sum(guild.member_count for guild in bot.guilds),
            'total_users': len(users_data),
            'servers': [],
            'users': users_data
        }

        for guild in bot.guilds:
            # 공지 채널 설정 확인
            guild_settings = config.get_guild_settings(guild.id)
            announcement_channel_id = guild_settings.get('ANNOUNCEMENT_CHANNEL_ID')
            announcement_channel_name = "미설정"
            announcement_display = "미설정"

            if announcement_channel_id:
                try:
                    channel = guild.get_channel(announcement_channel_id)
                    if channel:
                        announcement_channel_name = f"#{channel.name}"
                        announcement_display = f"#{channel.name} (ID: {announcement_channel_id})"
                    else:
                        announcement_channel_name = f"채널 ID: {announcement_channel_id} (접근불가)"
                        announcement_display = f"채널 ID: {announcement_channel_id} (접근불가)"
                except:
                    announcement_channel_name = f"채널 ID: {announcement_channel_id}"
                    announcement_display = f"채널 ID: {announcement_channel_id}"

            server_info = {
                'id': str(guild.id),
                'name': guild.name,
                'member_count': guild.member_count,
                'joined_at': guild.me.joined_at.isoformat() if guild.me.joined_at else None,
                'announcement_channel': announcement_channel_name,
                'announcement_channel_display': announcement_display,
                'announcement_channel_id': announcement_channel_id,
                'status': '활성' if announcement_channel_id else '설정 필요',
                'is_configured': bool(announcement_channel_id)
            }

            server_data['servers'].append(server_info)

        # GCS settings.json 업데이트 (로컬 파일 저장 제거)
        try:
            current_settings = config.load_settings()

            # 각 서버의 실제 정보를 settings.json의 guilds에 업데이트
            for server in server_data['servers']:
                guild_id = server['id']
                if guild_id in current_settings.get('guilds', {}):
                    # 기존 설정 유지하면서 실제 정보 업데이트
                    current_settings['guilds'][guild_id].update({
                        'GUILD_NAME': server['name'],
                        '멤버수': server['member_count'],
                        '가입일': server['joined_at'],
                        '상태': server['status'],
                        '마지막_업데이트': datetime.now().isoformat()
                    })

            config.save_settings(current_settings, silent=True)
        except Exception as e:
            print(f"[오류] GCS settings.json 업데이트 실패: {e}", flush=True)

    except Exception as e:
        print(f"[오류] 웹 패널 데이터 저장 실패: {e}", flush=True)


# ========== CommandNotFound 에러 핸들러 ==========

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """슬래시 커맨드 에러 처리"""
    if isinstance(error, discord.app_commands.CommandNotFound):
        cmd_name = interaction.data.get("name", "?") if interaction.data else "?"
        guild_name = interaction.guild.name if interaction.guild else "DM"
        user_name = interaction.user.display_name or interaction.user.name
        print(f"[경고] 존재하지 않는 커맨드: /{cmd_name} (유저: {user_name}, 서버: {guild_name})", flush=True)
        try:
            await interaction.response.send_message(
                "이 명령어는 더 이상 사용할 수 없어요!\n"
                "새 명령어: /tts, /음악, /전적, /통계, /시즌, /동접, /퀴즈, /설정, /피드백",
                ephemeral=True
            )
        except Exception:
            pass
        return
    raise error


async def _clear_guild_commands():
    """모든 길드의 잔여 커맨드를 초기화합니다."""
    cleared = 0
    for guild in bot.guilds:
        try:
            guild_commands = await bot.tree.fetch_commands(guild=guild)
            if guild_commands:
                bot.tree.clear_commands(guild=guild)
                await bot.tree.sync(guild=guild)
                cleared += 1
        except Exception:
            pass
    if cleared:
        print(f"[완료] {cleared}개 서버의 옛날 길드 커맨드 초기화 완료", flush=True)


# ========== 봇 이벤트 핸들러 ==========

@bot.event
async def on_ready():
    """봇 준비 완료 시 실행 (RESUME 재연결 시에도 호출됨)"""
    import sys
    print(f'[봇] {bot.user} 봇이 시작되었습니다!', flush=True)
    sys.stdout.flush()

    guild_count = len(bot.guilds)
    total_members = sum(guild.member_count for guild in bot.guilds if guild.member_count)
    print(f"[정보] 현재 {guild_count}개 서버에 연결되었습니다, 총 {total_members}명 사용자", flush=True)
    sys.stdout.flush()

    # 최초 1회만 실행 (RESUME 재연결 시 중복 실행 방지)
    if hasattr(bot, '_ready_once'):
        print("[정보] RESUME 재연결 - 초기화 건너뜀", flush=True)
        return
    bot._ready_once = True

    # 삭제된 서버 정리 (현재 접속 중인 서버는 건너뜀)
    try:
        active_ids = [g.id for g in bot.guilds]
        config.cleanup_removed_servers(active_guild_ids=active_ids)
    except Exception as e:
        print(f"[경고] 삭제된 서버 정리 실패: {e}", flush=True)

    # 모든 명령어에 allowed_installs/allowed_contexts 설정 (프로필에 명령어 표시)
    installs = discord.app_commands.AppInstallationType(guild=True, user=True)
    contexts = discord.app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True)
    for cmd in bot.tree.get_commands():
        cmd.allowed_installs = installs
        cmd.allowed_contexts = contexts

    # 글로벌 명령어 동기화
    try:
        synced = await bot.tree.sync()
        print(f"[완료] 명령어 동기화 완료 ({len(synced)}개)", flush=True)
    except Exception as e:
        print(f"[오류] 명령어 동기화 실패: {e}", flush=True)

    # 길드별 잔여 커맨드 초기화 (이전 버전에서 등록된 옛날 커맨드 제거)
    asyncio.create_task(_clear_guild_commands())

    # 무거운 초기화를 백그라운드로 실행 (이벤트 루프 차단 방지)
    asyncio.create_task(_background_init())


async def _background_init():
    """봇 시작 후 백그라운드에서 실행되는 무거운 초기화 작업들"""
    import sys

    # TTS 서비스 초기화
    try:
        tts_engine = os.environ.get("TTS_ENGINE", "modal")
        print(f"[TTS] 초기화 시작 (엔진: {tts_engine})...", flush=True)
        from run.cogs.voice import get_tts_service
        await get_tts_service("debi")
        await get_tts_service("marlene")
        print(f"[TTS] 초기화 완료! (Debi, Marlene, 엔진: {tts_engine})", flush=True)
    except Exception as e:
        print(f"[TTS] 초기화 실패: {e}", flush=True)

    # settings.json에 기존 서버들의 이름 정보를 한 번에 업데이트
    # GCS 호출은 동기적이라 to_thread()로 이벤트 루프 차단 방지
    settings = await asyncio.to_thread(config.load_settings)

    for guild in bot.guilds:
        try:
            guild_id_str = str(guild.id)

            if guild_id_str not in settings.get('guilds', {}):
                settings.setdefault('guilds', {})[guild_id_str] = {}

            guild_settings = settings['guilds'][guild_id_str]

            announcement_channel_name = None
            chat_channel_name = None

            if guild_settings.get('ANNOUNCEMENT_CHANNEL_ID'):
                announcement_channel = guild.get_channel(guild_settings['ANNOUNCEMENT_CHANNEL_ID'])
                if announcement_channel:
                    announcement_channel_name = announcement_channel.name

            if guild_settings.get('CHAT_CHANNEL_ID'):
                chat_channel = guild.get_channel(guild_settings['CHAT_CHANNEL_ID'])
                if chat_channel:
                    chat_channel_name = chat_channel.name

            guild_settings['GUILD_NAME'] = guild.name
            if announcement_channel_name:
                guild_settings['ANNOUNCEMENT_CHANNEL_NAME'] = announcement_channel_name
            if chat_channel_name:
                guild_settings['CHAT_CHANNEL_NAME'] = chat_channel_name
        except Exception as e:
            print(f"[경고] {guild.name} 서버 정보 업데이트 실패: {e}", flush=True)

    await asyncio.to_thread(config.save_settings, settings)

    # 기존 사용자들의 이름 정보 업데이트
    settings = await asyncio.to_thread(config.load_settings)
    existing_users = settings.get("users", {})

    for user_id_str, user_data in existing_users.items():
        if "user_name" not in user_data or not user_data["user_name"]:
            try:
                user_id = int(user_id_str)
                user = await bot.fetch_user(user_id)
                if user:
                    user_name = user.display_name or user.global_name or user.name
                    await asyncio.to_thread(config.log_user_interaction, user_id, user_name)
            except Exception as e:
                print(f"  -> [경고] 사용자 {user_id_str} 이름 업데이트 실패: {e}", flush=True)

    # 웹 패널을 위한 봇 인스턴스 저장
    try:
        set_bot_instance(bot)
    except Exception as e:
        print(f"[경고] 웹 패널용 봇 인스턴스 등록 실패: {e}", flush=True)

    # GCS에 서버 정보 업데이트
    try:
        await update_server_info_to_gcs()
    except Exception as e:
        print(f"[경고] GCS 서버 정보 업데이트 실패: {e}", flush=True)

    # 서버 정보 정기 업데이트 태스크 시작
    try:
        if not update_server_info_periodic.is_running():
            update_server_info_periodic.start()
    except Exception as e:
        print(f"[경고] 서버 정보 업데이트 태스크 시작 실패: {e}", flush=True)

    try:
        await initialize_game_data()
        print("[완료] 게임 데이터 초기화 완료.", flush=True)

        global _youtube_task_started
        if not _youtube_task_started:
            youtube_service.set_bot_instance(bot)
            await youtube_service.initialize_youtube()
            if not youtube_service.check_new_videos.is_running():
                youtube_service.check_new_videos.start()
            _youtube_task_started = True

        # 패치노트 체커 시작
        from run.services.patchnote_service import start_patchnote_checker
        start_patchnote_checker(bot)

        # 쿠폰 크롤링 서비스 시작
        from run.services.coupon_service import start_coupon_service
        start_coupon_service(bot)

        # 정기적 서버 수 로깅 태스크 시작
        if not periodic_guild_logging.is_running():
            periodic_guild_logging.start()

        # 이모지 맵 로드
        from run.utils.emoji_utils import load_emoji_map, EmojiAutoUpdater
        await load_emoji_map(bot)

        bot.emoji_auto_updater = EmojiAutoUpdater(bot)

        # 기존 음성 연결 복구 (봇 재시작/RESUME 후 voice_manager에 등록)
        from run.services.voice_manager import voice_manager
        for vc in bot.voice_clients:
            if vc.is_connected() and vc.guild:
                guild_id = str(vc.guild.id)
                voice_manager.voice_clients[guild_id] = vc
                voice_manager.current_type[guild_id] = None
                print(f"[음성] 기존 연결 복구: {vc.guild.name} / {vc.channel.name}", flush=True)

        # 동접수 상태 업데이트 태스크 시작
        if not update_presence.is_running():
            update_presence.start()
            print("[완료] 동접수 상태 업데이트 태스크 시작 (5분 간격)", flush=True)

        print("[완료] 모든 초기화 완료!", flush=True)
        sys.stdout.flush()

    except Exception as e:
        print(f"[오류] 데이터 초기화 중 일부 실패 (봇은 계속 실행): {e}", flush=True)
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        sys.stdout.flush()


STEAM_PLAYER_COUNT_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=1049590"


@tasks.loop(minutes=5)
async def update_presence():
    """5분마다 이터널리턴 동접수를 가져와 봇 상태에 표시"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(STEAM_PLAYER_COUNT_URL, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("response", {}).get("result") == 1:
                        count = data["response"]["player_count"]
                        activity = discord.CustomActivity(name=f"이터널리턴 동접 {count:,}명")
                        await bot.change_presence(activity=activity)
    except Exception as e:
        print(f"[경고] 동접수 상태 업데이트 실패: {e}", flush=True)


@bot.event
async def on_guild_join(guild: discord.Guild):
    """서버 참가 시"""
    import sys
    import time

    current_time = time.time()
    print(f"[완료] 새로운 서버에 초대되었습니다: {guild.name} (ID: {guild.id}) - 멤버 {guild.member_count}명", flush=True)
    sys.stdout.flush()

    # 재참가 서버라면 removed_servers에서 제거 (다음 재시작 때 cleanup 방지)
    config.unmark_removed_server(guild.id)

    # 빠른 중복 이벤트 방지 (30초 이내 같은 서버 초대 무시)
    if guild.id in welcome_timestamps:
        time_diff = current_time - welcome_timestamps[guild.id]
        if time_diff < 30:  # 30초 이내라면 중복으로 간주
            print(f"[경고] 빠른 중복 이벤트 감지 ({time_diff:.1f}초 전): {guild.name} (ID: {guild.id})", flush=True)
            return

    settings = config.load_settings()
    guild_id_str = str(guild.id)

    # 재초대된 서버가 아니면 중복 체크 (재초대된 경우는 환영 메시지를 다시 보냄)
    is_reinvited = guild_id_str in settings.get("guilds", {}) and settings["guilds"][guild_id_str].get("STATUS") == "삭제됨"
    if not is_reinvited and guild.id in welcomed_guilds:
        print(f"[경고] 현재 세션에서 이미 환영 메시지를 보낸 서버입니다: {guild.name} (ID: {guild.id})", flush=True)
        return

    # 서버를 환영 메시지 목록에 추가 (현재 세션 중복 방지)
    welcomed_guilds.add(guild.id)
    welcome_timestamps[guild.id] = current_time

    # 삭제됨 상태인 서버라면 상태 초기화
    if guild_id_str in settings.get("guilds", {}) and settings["guilds"][guild_id_str].get("STATUS") == "삭제됨":
        # 삭제됨 상태와 관련 필드들 제거하여 정상 상태로 복구
        guild_settings = settings["guilds"][guild_id_str].copy()
        guild_settings.pop("STATUS", None)
        guild_settings.pop("REMOVED_AT", None)
        print(f"[갱신] 삭제됨 상태 초기화: {guild.name} (ID: {guild.id})", flush=True)

        # 업데이트된 설정으로 저장
        config.save_guild_settings(
            guild.id,
            guild_name=guild.name,
            announcement_id=guild_settings.get("ANNOUNCEMENT_CHANNEL_ID"),
            announcement_channel_name=guild_settings.get("ANNOUNCEMENT_CHANNEL_NAME"),
            chat_id=guild_settings.get("CHAT_CHANNEL_ID"),
            chat_channel_name=guild_settings.get("CHAT_CHANNEL_NAME")
        )
    else:
        # settings.json에 새로운 서버 정보 추가 (자동 설정 없이)
        config.save_guild_settings(
            guild.id,
            guild_name=guild.name
        )

    # Audit Log에서 봇을 초대한 사람 찾기
    inviter = None
    try:
        async for entry in guild.audit_log(action=discord.AuditLogAction.bot_add, limit=5):
            if entry.target and entry.target.id == bot.user.id:
                inviter = entry.user
                break
    except discord.Forbidden:
        print(f"[경고] Audit Log 권한 없음: {guild.name} (ID: {guild.id})", flush=True)
    except Exception as e:
        print(f"[경고] Audit Log 조회 실패: {e}", flush=True)

    # 초대자를 못 찾으면 서버 소유자에게 발송
    if not inviter:
        inviter = guild.owner
        print(f"[정보] 초대자를 찾을 수 없어 서버 소유자에게 DM 발송: {inviter}", flush=True)

    if inviter:
        try:
            view = WelcomeLayoutView(guild)
            await inviter.send(view=view)
            print(f"[완료] 환영 DM 전송: {inviter.name} (서버: {guild.name})", flush=True)
        except discord.Forbidden:
            print(f"[경고] DM 전송 불가 (차단/비허용): {inviter.name}", flush=True)
        except Exception as e:
            print(f"[오류] 환영 DM 전송 실패: {e}", flush=True)

    # 서버 참가 시 GCS 실시간 업데이트
    try:
        await update_server_info_to_gcs()
    except Exception as e:
        print(f"[경고] 서버 참가 GCS 업데이트 실패: {e}", flush=True)


@bot.event
async def on_guild_remove(guild: discord.Guild):
    """서버에서 봇이 제거될 때 설정 삭제 및 로깅"""
    import sys
    print(f"[오류] 서버에서 제거되었습니다: {guild.name} (ID: {guild.id})", flush=True)

    try:
        # 삭제된 서버 정보를 GCS에 저장
        config.save_removed_server(guild.id, guild.name, guild.member_count)
    except Exception as e:
        print(f"[경고] 삭제된 서버 저장 실패: {e}", flush=True)

    try:
        # config.py의 remove_guild_settings 함수 호출 (삭제됨 표시 추가)
        if not config.remove_guild_settings(guild.id):
            print(f"[경고] 서버 삭제됨 표시 추가 실패: {guild.name} (ID: {guild.id})", flush=True)
    except Exception as e:
        print(f"[오류] 서버 삭제됨 표시 추가 중 예외 발생: {e}", flush=True)
        import traceback
        traceback.print_exc()

    # 서버 탈퇴 시 GCS 실시간 업데이트
    try:
        await update_server_info_to_gcs()
    except Exception as e:
        print(f"[경고] 서버 탈퇴 GCS 업데이트 실패: {e}", flush=True)

    sys.stdout.flush()


@bot.event
async def on_voice_state_update(member, before, after):
    """음성 채널 상태 변경 시 - 봇 혼자 남으면 idle 타이머 시작"""
    from run.services.voice_manager import voice_manager

    # 봇 자신이 음성 채널에 연결/해제된 경우 voice_manager 동기화
    if member.id == bot.user.id:
        if after.channel and not before.channel:
            # 봇이 음성 채널에 들어감 (RESUME 포함)
            guild_id = str(after.channel.guild.id)
            vc = after.channel.guild.voice_client
            if vc and guild_id not in voice_manager.voice_clients:
                voice_manager.voice_clients[guild_id] = vc
                voice_manager.current_type[guild_id] = None
                print(f"[음성] 연결 동기화: {after.channel.name}", flush=True)
        elif before.channel and not after.channel:
            # 봇이 음성 채널에서 나감 (퇴장, 킥, 연결 끊김 등)
            guild_id = str(before.channel.guild.id)
            voice_manager.voice_clients.pop(guild_id, None)
            voice_manager.current_type.pop(guild_id, None)
            voice_manager.tts_interrupting.pop(guild_id, None)
            voice_manager.music_restart_callbacks.pop(guild_id, None)
            voice_manager.play_finished_events.pop(guild_id, None)
            voice_manager.cancel_idle_timer(guild_id)
            print(f"[음성] 연결 해제 정리: {before.channel.name}", flush=True)
        return

    # 사용자가 봇이 있는 채널에서 나간 경우 (퇴장 또는 다른 채널로 이동)
    if before.channel and before.channel != after.channel:
        guild_id = str(before.channel.guild.id)
        vc = voice_manager.get_voice_client(guild_id)

        if vc and vc.is_connected() and vc.channel.id == before.channel.id:
            non_bot_members = [m for m in before.channel.members if not m.bot]
            if not non_bot_members:
                # 퀴즈 진행 중이면 자동 종료
                from run.services.quiz.quiz_manager import QuizManager
                if QuizManager.has_active_session(guild_id):
                    from run.services.quiz.song_quiz import SongQuiz
                    session = QuizManager.get_session(guild_id)
                    if session and session.quiz_type == "song":
                        SongQuiz.stop_playback(guild_id)
                    QuizManager.end_session(guild_id)
                voice_manager.start_idle_timer(guild_id)

    # 사용자가 봇이 있는 채널에 들어온 경우 (입장 또는 다른 채널에서 이동)
    if after.channel and after.channel != before.channel:
        guild_id = str(after.channel.guild.id)
        vc = voice_manager.get_voice_client(guild_id)

        if vc and vc.is_connected() and vc.channel.id == after.channel.id:
            voice_manager.cancel_idle_timer(guild_id)


async def _handle_sticky_message(message):
    """스티키 메시지 처리: 채널에 새 메시지가 오면 스티키 메시지를 다시 전송"""
    channel_id_str = str(message.channel.id)
    guild_id_str = str(message.guild.id)

    # 쿨다운 체크 (채널별)
    now = time.time()
    last_sent = _sticky_cooldowns.get(channel_id_str, 0)
    if now - last_sent < STICKY_COOLDOWN_SECONDS:
        return

    # GCS에서 설정 로드 (캐시 우회)
    try:
        settings = await asyncio.to_thread(config.load_settings, True)
    except Exception as e:
        print(f"[스티키] 설정 로드 실패: {e}", flush=True)
        return

    sticky_messages = settings.get('guilds', {}).get(guild_id_str, {}).get('sticky_messages', [])
    if not sticky_messages:
        return

    # 이 채널에 활성화된 스티키 메시지 모두 찾기
    matching = [(i, sm) for i, sm in enumerate(sticky_messages)
                if str(sm.get('channelId', '')) == channel_id_str and sm.get('enabled')]

    if not matching:
        return

    # 쿨다운 설정
    _sticky_cooldowns[channel_id_str] = now

    changed = False
    for idx, sticky in matching:
        # 이전 스티키 메시지 삭제
        old_message_id = sticky.get('lastMessageId')
        if old_message_id:
            try:
                old_msg = await message.channel.fetch_message(int(old_message_id))
                await old_msg.delete()
            except (discord.NotFound, discord.HTTPException):
                pass
            except Exception as e:
                print(f"[스티키] 이전 메시지 삭제 실패: {e}", flush=True)

        # 새 스티키 메시지 전송 (silent)
        try:
            new_msg = await message.channel.send(sticky['content'], silent=True)
            sticky_messages[idx]['lastMessageId'] = str(new_msg.id)
            changed = True
        except Exception as e:
            print(f"[스티키] 메시지 전송 실패: {e}", flush=True)

    # GCS에 lastMessageId 업데이트 (한 번만)
    if changed:
        try:
            await asyncio.to_thread(config.save_settings, settings, True)
        except Exception as e:
            print(f"[스티키] 설정 저장 실패: {e}", flush=True)


@bot.event
async def on_message(message):
    """메시지 수신 시"""
    # 봇 자신의 메시지는 무시
    if message.author == bot.user:
        await bot.process_commands(message)
        return

    # 봇 메시지는 스티키 포함 모든 처리 스킵
    if message.author.bot:
        await bot.process_commands(message)
        return

    # 스티키 메시지 처리 (서버 메시지만)
    if message.guild:
        try:
            await _handle_sticky_message(message)
        except Exception as e:
            print(f"[스티키] 처리 오류: {e}", flush=True)

    # TTS 메시지 처리 (서버 메시지만)
    if message.guild:
        try:
            from run.cogs.voice import handle_tts_message
            await handle_tts_message(message)
        except Exception as e:
            import logging, traceback
            logging.error(f"TTS 메시지 처리 오류: {e}")

    # DM 메시지 처리 (실제 내용이 있는 메시지만)
    if isinstance(message.channel, discord.DMChannel):
        # 메시지 내용이 비어있으면 무시
        if not message.content or not message.content.strip():
            return

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

        gateway_dm_messages.append(dm_data)

        # 최대 500개까지만 저장
        if len(gateway_dm_messages) > 500:
            gateway_dm_messages[:] = gateway_dm_messages[-400:]

        print(f'[DM] 수신: {message.author.display_name} - {message.content[:100]}')

        # GCS에 사용자 DM 정보 저장 (통합)
        try:
            config.save_user_dm_interaction(
                user_id=message.author.id,
                channel_id=message.channel.id,
                user_name=message.author.display_name
            )
            print(f'[완료] DM 사용자 정보 저장 완료: {message.author.display_name}')
        except Exception as e:
            print(f'[오류] DM 정보 저장 실패: {e}')


# ========== 정기 태스크 ==========

@tasks.loop(minutes=30)
async def update_server_info_periodic():
    """30분마다 GCS에 서버 정보를 업데이트"""
    try:
        await update_server_info_to_gcs()
    except Exception as e:
        print(f"[오류] 정기 GCS 서버 정보 업데이트 실패: {e}")


@tasks.loop(minutes=60)
async def periodic_guild_logging():
    """1시간마다 서버 수 로깅"""
    import sys
    guild_count = len(bot.guilds)
    total_members = sum(guild.member_count for guild in bot.guilds if guild.member_count)
    sys.stdout.flush()

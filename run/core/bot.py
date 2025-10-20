"""
Discord 봇 인스턴스 및 이벤트 핸들러

이 모듈에는 봇 인스턴스와 모든 이벤트 핸들러가 포함되어 있습니다.
"""

import discord
import os
import json
from discord.ext import commands, tasks
from datetime import datetime

from run.core import config
from run.services.eternal_return.api_client import initialize_game_data, set_bot_instance
from run.services import youtube_service
from run.views.welcome_view import WelcomeView


# Discord 봇 설정
intents = discord.Intents.all()  # 모든 Intents 활성화 (Gateway 기능용)
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Gateway 데이터 저장용 전역 변수
gateway_guild_data = {}  # 서버 데이터
gateway_dm_messages = []  # DM 메시지

# 환영 메시지를 보낸 서버를 추적하는 세트 (세션 중 중복 방지용)
welcomed_guilds = set()
# 환영 메시지 전송 시간을 추적 (빠른 중복 이벤트 방지)
welcome_timestamps = {}


async def update_guild_data_to_gcs(guild: discord.Guild):
    """특정 서버 데이터를 GCS에 업데이트"""
    try:
        # 온라인/오프라인 멤버 수 계산
        online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)
        offline_members = guild.member_count - online_members

        # 서버 데이터
        guild_data = {
            'id': str(guild.id),
            'name': guild.name,
            'member_count': guild.member_count,
            'online_count': online_members,
            'offline_count': offline_members,
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
                '서버이름': guild.name,
                '멤버수': guild.member_count,
                'GUILD_ICON_HASH': guild.icon.key if guild.icon else None,
                'last_updated': datetime.now().isoformat()
            })
        else:
            settings['guilds'][str(guild.id)] = {
                '서버이름': guild.name,
                '멤버수': guild.member_count,
                'GUILD_ICON_HASH': guild.icon.key if guild.icon else None,
                'last_updated': datetime.now().isoformat()
            }

        config.save_settings(settings)
        print(f"📊 서버 데이터 GCS 저장: {guild.name} ({guild.member_count}명)")

    except Exception as e:
        print(f"❌ 서버 데이터 업데이트 실패 {guild.name}: {e}")


async def save_server_info_for_web_panel():
    """웹 패널용 서버 정보를 JSON 파일로 저장"""
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

        print(f"DEBUG: 실제 사용자 수집 완료 - YouTube 구독자: {len(subscribers)}, 상호작용 사용자: {len(interaction_users)}, 총: {len(users_data)}")

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

        # JSON 파일로 저장
        web_panel_data_path = os.path.join(os.path.dirname(__file__), '..', 'web_panel_data.json')
        with open(web_panel_data_path, 'w', encoding='utf-8') as f:
            json.dump(server_data, f, ensure_ascii=False, indent=2)

        try:
            current_settings = config.load_settings()

            # 각 서버의 실제 정보를 settings.json의 guilds에 업데이트
            for server in server_data['servers']:
                guild_id = server['id']
                if guild_id in current_settings.get('guilds', {}):
                    # 기존 설정 유지하면서 실제 정보 업데이트
                    current_settings['guilds'][guild_id].update({
                        '서버이름': server['name'],
                        '멤버수': server['member_count'],
                        '가입일': server['joined_at'],
                        '상태': server['status'],
                        '마지막_업데이트': datetime.now().isoformat()
                    })

            config.save_settings(current_settings, silent=True)
        except Exception as e:
            print(f"settings.json 업데이트 실패: {e}", flush=True)

        print(f"📊 웹 패널 데이터 저장: {len(server_data['servers'])}개 서버, {server_data['total_members']:,}명", flush=True)

    except Exception as e:
        print(f"❌ 웹 패널 데이터 저장 실패: {e}", flush=True)


# ========== 봇 이벤트 핸들러 ==========

@bot.event
async def on_ready():
    """봇 준비 완료 시 실행"""
    import sys
    print(f'🤖 {bot.user} 봇이 시작되었습니다!', flush=True)
    sys.stdout.flush()

    guild_count = len(bot.guilds)
    total_members = sum(guild.member_count for guild in bot.guilds if guild.member_count)
    print(f"📊 현재 {guild_count}개 서버에 연결되었습니다, 총 {total_members}명 사용자", flush=True)
    print(f"📊 정기 체크: 현재 {guild_count}개 서버에 연결, 총 {total_members}명 사용자", flush=True)
    sys.stdout.flush()

    # settings.json에 기존 서버들의 이름 정보를 한 번에 업데이트
    print("📝 기존 서버들의 정보를 settings.json에 업데이트 중...", flush=True)

    # 모든 서버 정보를 모아서 한 번에 저장
    settings = config.load_settings()
    updated_count = 0

    for guild in bot.guilds:
        try:
            guild_id_str = str(guild.id)

            # 기존 설정 가져오기
            if guild_id_str not in settings.get('guilds', {}):
                settings.setdefault('guilds', {})[guild_id_str] = {}

            guild_settings = settings['guilds'][guild_id_str]

            # 채널 정보 업데이트
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

            # 서버 정보 직접 업데이트 (저장은 나중에 한 번만)
            guild_settings['GUILD_NAME'] = guild.name
            if announcement_channel_name:
                guild_settings['ANNOUNCEMENT_CHANNEL_NAME'] = announcement_channel_name
            if chat_channel_name:
                guild_settings['CHAT_CHANNEL_NAME'] = chat_channel_name

            updated_count += 1
        except Exception as e:
            print(f"⚠️ {guild.name} 서버 정보 업데이트 실패: {e}", flush=True)

    # 한 번만 저장
    config.save_settings(settings)
    print(f"✅ {updated_count}개 서버 정보 업데이트 완료", flush=True)
    sys.stdout.flush()

    # 처음 몇 개 서버 정보 로깅 (디버깅용)
    for i, guild in enumerate(bot.guilds[:5]):
        print(f"서버 {i+1}: {guild.name} (ID: {guild.id}) - 멤버 {guild.member_count}명", flush=True)
        sys.stdout.flush()

    if guild_count > 5:
        print(f"... 외 {guild_count - 5}개 서버", flush=True)
        sys.stdout.flush()

    # 기존 사용자들의 이름 정보 업데이트
    print("📝 기존 사용자들의 이름 정보를 settings.json에 업데이트 중...", flush=True)
    settings = config.load_settings()
    existing_users = settings.get("users", {})
    user_update_count = 0

    for user_id_str, user_data in existing_users.items():
        if "user_name" not in user_data or not user_data["user_name"]:
            try:
                user_id = int(user_id_str)
                user = await bot.fetch_user(user_id)
                if user:
                    user_name = user.display_name or user.global_name or user.name
                    config.log_user_interaction(user_id, user_name)
                    user_update_count += 1
                    print(f"  -> 사용자 {user_id} 이름 업데이트: {user_name}", flush=True)
            except Exception as e:
                print(f"  -> ⚠️ 사용자 {user_id_str} 이름 업데이트 실패: {e}", flush=True)

    print(f"✅ {user_update_count}개 사용자 이름 업데이트 완료", flush=True)
    sys.stdout.flush()

    # 웹 패널을 위한 봇 인스턴스 저장
    try:
        set_bot_instance(bot)
        print("🌐 웹 패널용 봇 인스턴스 등록 완료", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"⚠️ 웹 패널용 봇 인스턴스 등록 실패: {e}", flush=True)
        sys.stdout.flush()

    # 웹 패널용 서버 정보 JSON 파일로 저장
    try:
        await save_server_info_for_web_panel()
        print("💾 웹 패널용 서버 정보 저장 완료", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"⚠️ 서버 정보 저장 실패: {e}", flush=True)
        sys.stdout.flush()

    # 서버 정보 정기 업데이트 태스크 시작
    try:
        update_server_info.start()
        print("🔄 서버 정보 정기 업데이트 태스크 시작 (30분 간격)", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"⚠️ 서버 정보 업데이트 태스크 시작 실패: {e}", flush=True)
        sys.stdout.flush()

    try:
        print("🔧 명령어 동기화 시작...", flush=True)
        sys.stdout.flush()

        # 명령어 동기화 (기존 명령어 업데이트)
        synced = await bot.tree.sync()
        print(f"✅ 명령어 동기화 완료: {len(synced)}개 명령어", flush=True)

        print("✅ 모든 명령어 동기화 완료.", flush=True)
        sys.stdout.flush()

        print("🔧 게임 데이터 초기화 시작...", flush=True)
        sys.stdout.flush()
        await initialize_game_data()
        print("✅ 게임 데이터 초기화 완료.", flush=True)
        sys.stdout.flush()

        print("🔧 유튜브 서비스 설정 시작...", flush=True)
        sys.stdout.flush()
        youtube_service.set_bot_instance(bot)
        print("🔧 유튜브 API 초기화 시작...", flush=True)
        sys.stdout.flush()
        await youtube_service.initialize_youtube()
        print("🔧 유튜브 체크 루프 시작...", flush=True)
        sys.stdout.flush()
        youtube_service.check_new_videos.start()

        # 정기적 서버 수 로깅 태스크 시작
        periodic_guild_logging.start()
        print("🔧 정기 서버 수 로깅 시작...", flush=True)
        sys.stdout.flush()

        print("✅ 모든 초기화 완료!", flush=True)
        sys.stdout.flush()

    except Exception as e:
        print(f"❌ CRITICAL: 데이터 초기화 중 봇 시작 실패: {e}", flush=True)
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        await bot.close()


@bot.event
async def on_guild_join(guild: discord.Guild):
    """서버 참가 시"""
    import sys
    import time

    current_time = time.time()
    print(f"✅ 새로운 서버에 초대되었습니다: {guild.name} (ID: {guild.id}) - 멤버 {guild.member_count}명", flush=True)
    sys.stdout.flush()

    # 빠른 중복 이벤트 방지 (30초 이내 같은 서버 초대 무시)
    if guild.id in welcome_timestamps:
        time_diff = current_time - welcome_timestamps[guild.id]
        if time_diff < 30:  # 30초 이내라면 중복으로 간주
            print(f"⚠️ 빠른 중복 이벤트 감지 ({time_diff:.1f}초 전): {guild.name} (ID: {guild.id})", flush=True)
            return

    settings = config.load_settings()
    guild_id_str = str(guild.id)

    # 재초대된 서버가 아니면 중복 체크 (재초대된 경우는 환영 메시지를 다시 보냄)
    is_reinvited = guild_id_str in settings.get("guilds", {}) and settings["guilds"][guild_id_str].get("STATUS") == "삭제됨"
    if not is_reinvited and guild.id in welcomed_guilds:
        print(f"⚠️ 현재 세션에서 이미 환영 메시지를 보낸 서버입니다: {guild.name} (ID: {guild.id})", flush=True)
        return

    # 서버를 환영 메시지 목록에 추가 (현재 세션 중복 방지)
    welcomed_guilds.add(guild.id)
    welcome_timestamps[guild.id] = current_time
    print(f"DEBUG: 서버 {guild.id}를 환영 메시지 목록에 추가", flush=True)

    # 삭제됨 상태인 서버라면 상태 초기화
    if guild_id_str in settings.get("guilds", {}) and settings["guilds"][guild_id_str].get("STATUS") == "삭제됨":
        # 삭제됨 상태와 관련 필드들 제거하여 정상 상태로 복구
        guild_settings = settings["guilds"][guild_id_str].copy()
        guild_settings.pop("STATUS", None)
        guild_settings.pop("REMOVED_AT", None)
        print(f"🔄 삭제됨 상태 초기화: {guild.name} (ID: {guild.id})", flush=True)

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
    print(f"📝 settings.json에 서버 정보 저장 완료: {guild.name}", flush=True)

    target_channel = guild.system_channel
    if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                target_channel = channel
                break

    if target_channel:
        try:
            profile_image = discord.File("assets/profile.webp", filename="profile.webp")

            if is_reinvited:
                # 재초대된 서버용 메시지
                embed = discord.Embed(
                    title="다시 만나게 되어 반가워.",
                    description="우리를 다시 불러주어서 정말 기뻐! 이전 설정을 그대로 유지하고 있었어.",
                    color=0xDC143C  # 빨강
                )
                embed.set_thumbnail(url="attachment://profile.webp")
                embed.add_field(name="데비", value="> 또 만나니까 정말 좋아!", inline=False)
                embed.add_field(name="마를렌", value="> 이전처럼 열심히 도와줄게.", inline=False)
                embed.add_field(name="⚙️ 설정 확인", value="이전 **공지 채널**과 **채팅 채널** 설정을 확인하고 싶으시다면\n아래 버튼을 눌러줘!", inline=False)
            else:
                # 새로운 서버용 메시지
                embed = discord.Embed(title="데비&마를렌", description="디스코드 이터널리턴 전적검색 봇", color=0x0000FF)  # 파랑
                embed.set_thumbnail(url="attachment://profile.webp")
                embed.add_field(name="데비", value="> 와, 새로운 곳이다! 여기서도 우리 팀워크를 보여주자!", inline=False)
                embed.add_field(name="마를렌", value="> 흥, 데비 언니... 너무 들뜨지 마. 일단 상황부터 파악해야지.", inline=False)
                embed.add_field(name="⚙️ 초기 설정 안내", value="유튜브 알림 **공지 채널**과 전적 검색 **채팅 채널** 설정이 필요해요.\n아래 버튼을 눌러 바로 시작할 수 있습니다!", inline=False)

            view = WelcomeView()
            await target_channel.send(file=profile_image, embed=embed, view=view)

            message_type = "재초대 환영" if is_reinvited else "초기 환영"
            print(f"✅ {message_type} 메시지 전송 완료: {guild.name} (ID: {guild.id})", flush=True)
        except Exception as e:
            print(f"❌ 환영 메시지 전송 중 오류 발생: {e}")


@bot.event
async def on_guild_remove(guild: discord.Guild):
    """서버에서 봇이 제거될 때 설정 삭제 및 로깅"""
    import sys
    print(f"❌ 서버에서 제거되었습니다: {guild.name} (ID: {guild.id})", flush=True)

    try:
        # config.py의 remove_guild_settings 함수 호출 (삭제됨 표시 추가)
        if config.remove_guild_settings(guild.id):
            print(f"✅ 서버에 삭제됨 표시가 추가되었습니다: {guild.name} (ID: {guild.id})", flush=True)
        else:
            print(f"⚠️ 서버 삭제됨 표시 추가 실패: {guild.name} (ID: {guild.id})", flush=True)
    except Exception as e:
        print(f"❌ 서버 삭제됨 표시 추가 중 예외 발생: {e}", flush=True)
        import traceback
        traceback.print_exc()

    sys.stdout.flush()


@bot.event
async def on_message(message):
    """메시지 수신 시"""
    # 봇 자신의 메시지는 무시
    if message.author == bot.user:
        await bot.process_commands(message)
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

        gateway_dm_messages.append(dm_data)

        # 최대 500개까지만 저장
        if len(gateway_dm_messages) > 500:
            gateway_dm_messages[:] = gateway_dm_messages[-400:]

        print(f'💌 DM 수신: {message.author.display_name} - {message.content[:500]}...')

        # GCS에 DM 채널 정보 저장
        try:
            settings = config.load_settings()
            user_id = str(message.author.id)

            if 'users' not in settings:
                settings['users'] = {}

            if user_id not in settings['users']:
                settings['users'][user_id] = {}

            # DM 채널 ID 저장
            settings['users'][user_id]['dm_channel_id'] = str(message.channel.id)
            settings['users'][user_id]['user_name'] = message.author.display_name
            settings['users'][user_id]['last_dm'] = datetime.now().isoformat()

            config.save_settings(settings)
            print(f'💾 DM 채널 정보 GCS 저장: {message.author.display_name} ({message.channel.id})')
        except Exception as e:
            print(f'❌ DM 채널 정보 GCS 저장 실패: {e}')


# ========== 정기 태스크 ==========

@tasks.loop(minutes=30)
async def update_server_info():
    """30분마다 서버 정보를 업데이트"""
    try:
        await save_server_info_for_web_panel()
    except Exception as e:
        print(f"❌ 정기 서버 정보 업데이트 실패: {e}")


@tasks.loop(minutes=60)
async def periodic_guild_logging():
    """1시간마다 서버 수 로깅"""
    import sys
    guild_count = len(bot.guilds)
    total_members = sum(guild.member_count for guild in bot.guilds if guild.member_count)
    print(f"📊 정기 체크: 현재 {guild_count}개 서버에 연결, 총 {total_members}명 사용자", flush=True)
    sys.stdout.flush()

import asyncio
import discord
from discord.ext import tasks
from googleapiclient.discovery import build

from run.core.config import YOUTUBE_API_KEY, ETERNAL_RETURN_CHANNEL_ID, get_guild_settings
from run.core import config

youtube = None
bot_instance = None
_notification_lock = asyncio.Lock()

def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot

def _fetch_non_live_videos_sync():
    """업로드 플레이리스트에서 라이브 제외 최신 영상 목록을 동기로 가져옵니다.

    googleapiclient 는 동기 블로킹이라 반드시 asyncio.to_thread 로 호출해야
    이벤트 루프가 막히지 않습니다 (안 그러면 슬래시 명령 defer 가 3초 초과해 만료됨).
    """
    channel_response = youtube.channels().list(part='contentDetails', id=ETERNAL_RETURN_CHANNEL_ID).execute()
    if not channel_response.get('items'):
        return []
    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    playlist_response = youtube.playlistItems().list(part='snippet', playlistId=uploads_playlist_id, maxResults=10).execute()
    items = playlist_response.get('items', [])
    if not items:
        return []
    non_live = []
    for item in items:
        vid = item['snippet']['resourceId']['videoId']
        detail = youtube.videos().list(part='snippet,liveStreamingDetails', id=vid).execute().get('items', [{}])[0]
        if 'liveStreamingDetails' not in detail:
            non_live.append(item)
    return non_live

async def initialize_youtube():
    global youtube
    if YOUTUBE_API_KEY:
        try:
            youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
            print("[완료] 유튜브 API 초기화 완료 - 채널 메시지 기반 중복 체크 사용")
        except Exception as e:
            print(f"[오류] 유튜브 API 초기화 실패: {e}")
            youtube = None
    else:
        print("[경고] YOUTUBE_API_KEY가 설정되지 않아 유튜브 관련 기능을 비활성화합니다.")
        youtube = None

async def check_video_duration(video_id):
    if not youtube:
        return False
    try:
        video_response = await asyncio.to_thread(
            lambda: youtube.videos().list(part='contentDetails', id=video_id).execute()
        )

        if video_response['items']:
            duration = video_response['items'][0]['contentDetails']['duration']
            import re
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
            if match:
                hours, minutes, seconds = (int(g or 0) for g in match.groups())
                total_seconds = hours * 3600 + minutes * 60 + seconds
                return total_seconds <= 60
        return False
    except Exception as e:
        print(f"[오류] 영상 길이 체크 오류: {e}")
        return False

async def get_last_sent_video_id_from_channel(channel):
    if not channel or not bot_instance:
        return None
    import re
    pattern = re.compile(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})')
    try:
        async for message in channel.history(limit=50):
            if message.author.id != bot_instance.user.id:
                continue
            # _send_notification 은 영상 URL 을 메시지 content 로 보냄 (embed.url 은 미설정)
            # → content 를 먼저 검사해야 중복 체크가 실제로 작동함
            if message.content:
                match = pattern.search(message.content)
                if match:
                    return match.group(1)
            for embed in message.embeds:
                if embed.url:
                    match = pattern.search(embed.url)
                    if match:
                        return match.group(1)
    except discord.Forbidden:
        print(f"[오류] 채널 '{channel.name}'의 메시지를 읽을 권한이 없습니다.")
    except Exception as e:
        print(f"[오류] 채널 '{channel.name}'에서 마지막 영상 ID 확인 중 오류: {e}")
    return None

async def _send_notification(channel_or_user, video_id, snippet, is_shorts=None):
    """지정된 채널 또는 유저에게 알림을 보냅니다.

    is_shorts 를 미리 넘기면 영상 길이 API 를 전송 대상마다 중복 호출하지 않음.
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        if is_shorts is None:
            is_shorts = await check_video_duration(video_id)

        # 쇼츠면 데비, 일반 영상이면 마를렌
        if is_shorts:
            char_color = 0x0000FF  # 파랑
            char_image = "https://panel.debimarlene.com/assets/debi.png"
            author_text = "데비가 새로운 쇼츠를 발견했어!"
            action_text = "새로운 쇼츠를 발견했어!"
        else:
            char_color = 0xDC143C  # 빨강
            char_image = "https://panel.debimarlene.com/assets/marlen.png"
            author_text = "마를렌이 새로운 영상을 가져왔어."
            action_text = "새로운 영상을 가져왔어."

        embed = discord.Embed(
            title=f"**{snippet['title']}**",
            url=video_url,
            description=snippet.get('description', '')[:150] + '...' if snippet.get('description') else action_text,
            color=char_color
        )
        embed.set_author(name=author_text, icon_url=char_image)
        embed.set_thumbnail(url=snippet['thumbnails']['high']['url'])

        # DM 메시지 전송
        sent_message = await channel_or_user.send(video_url)
        await channel_or_user.send(embed=embed)

        # User에게 DM을 보낸 경우, 채널 정보를 GCS에 저장
        if isinstance(channel_or_user, (discord.User, discord.Member)) and sent_message:
            try:
                from datetime import datetime
                user_name = channel_or_user.display_name or channel_or_user.global_name or channel_or_user.name
                user_id = str(channel_or_user.id)
                channel_id = str(sent_message.channel.id)

                # settings.json에 DM 채널 정보 저장
                settings = await asyncio.to_thread(config.load_settings)
                if 'users' not in settings:
                    settings['users'] = {}

                if user_id not in settings['users']:
                    settings['users'][user_id] = {}

                # DM 채널 정보 업데이트
                settings['users'][user_id]['dm_channel_id'] = channel_id
                settings['users'][user_id]['user_name'] = user_name
                settings['users'][user_id]['last_dm'] = datetime.now().isoformat()

                # GCS에 저장
                await asyncio.to_thread(config.save_settings, settings)
                print(f"  -> [저장] DM 채널 정보 GCS에 저장: {user_name} ({channel_id})")
            except Exception as save_error:
                print(f"  -> [경고] DM 채널 정보 저장 실패 (메시지는 전송됨): {save_error}")

        return True
    except discord.Forbidden:
        target_name = channel_or_user.name if hasattr(channel_or_user, 'name') else channel_or_user.id
        print(f"  -> [오류] 전송 실패: '{target_name}'에게 메시지를 보낼 권한이 없습니다.")
        return False
    except Exception as e:
        target_name = channel_or_user.name if hasattr(channel_or_user, 'name') else channel_or_user.id
        print(f"  -> [오류] 전송 실패: '{target_name}' 처리 중 오류 발생: {e}")
        return False

@tasks.loop(minutes=10)
async def check_new_videos():
    if not youtube or not bot_instance:
        return

    # Lock으로 동시 실행 방지 (on_ready 중복 호출 대비)
    if _notification_lock.locked():
        print("[유튜브] 이전 알림 작업이 아직 진행 중 - 스킵")
        return

    async with _notification_lock:
        try:
            # 1. 최신 영상 정보 가져오기 (동기 API → to_thread 로 루프 블로킹 방지)
            non_live_videos = await asyncio.to_thread(_fetch_non_live_videos_sync)
            if not non_live_videos: return

            # 2. 최신 영상을 원자적으로 선점(claim) — 전송 *전에* LAST_CHECKED 를 전진시킨다.
            #    이렇게 해야:
            #      - 멀티프로세스(VM+로컬/배포 중 구컨테이너)가 동시에 돌아도 단 1개만 전송
            #      - 전송 도중 게이트웨이 1006 으로 재시작돼도 재처리(중복 burst) 안 함
            #    claimed=False 면 이미 다른 실행이 처리 중/완료 → 전송 스킵.
            latest = non_live_videos[0]
            latest_video_id = latest['snippet']['resourceId']['videoId']
            latest_title = latest['snippet'].get('title', '제목 없음')
            claimed, last_checked_id = await asyncio.to_thread(
                config.claim_latest_video_id, latest_video_id, latest_title
            )
            if not claimed:
                return

            found_idx = None
            for idx, item in enumerate(non_live_videos):
                if item['snippet']['resourceId']['videoId'] == last_checked_id:
                    found_idx = idx
                    break

            # last_checked 가 playlist 10개 밖으로 밀려났거나 첫 실행이면 최신 1개만 (스팸 방지)
            if found_idx is None:
                videos_to_send = [non_live_videos[0]]
            else:
                videos_to_send = list(reversed(non_live_videos[:found_idx]))

            print(f"[유튜브] 신규 영상 {len(videos_to_send)}개 처리 시작")

            # 3. 동시 전송 폭주 방지 — 무제한 gather 는 길드 수백 × (history 조회+전송) 이
            #    Discord REST 429 폭발 + 게이트웨이 하트비트 누락(1006 끊김 → 봇 재시작)을 유발
            send_semaphore = asyncio.Semaphore(10)

            async def send_to_guild(guild, video_id, snippet, is_shorts):
                """개별 서버에 알림을 보내는 비동기 함수"""
                async with send_semaphore:
                    guild_settings = await asyncio.to_thread(config.get_guild_settings, guild.id)
                    channel_id = guild_settings.get("ANNOUNCEMENT_CHANNEL_ID")
                    if channel_id:
                        channel = bot_instance.get_channel(int(channel_id))
                        if channel:
                            last_sent_id = await get_last_sent_video_id_from_channel(channel)
                            if last_sent_id != video_id:
                                print(f"  -> 서버 '{guild.name}' (ID: {guild.id})의 #{channel.name} (ID: {channel_id}) 채널에 새 영상 전송")
                                await _send_notification(channel, video_id, snippet, is_shorts)
                            else:
                                print(f"  -> 서버 '{guild.name}' (ID: {guild.id}): 이미 전송된 영상")
                        else:
                            print(f"  -> 서버 '{guild.name}' (ID: {guild.id}): 채널 ID {channel_id}를 찾을 수 없음")
                    else:
                        print(f"  -> 서버 '{guild.name}' (ID: {guild.id}): 공지 채널 미설정")

            async def send_to_user(user_id, video_id, snippet, is_shorts):
                """개별 사용자에게 DM을 보내는 비동기 함수"""
                async with send_semaphore:
                    try:
                        user = await bot_instance.fetch_user(user_id)

                        # DM 채널 ID 확인 (GCS에 저장된 정보)
                        settings = await asyncio.to_thread(config.load_settings)
                        user_settings = settings.get('users', {}).get(str(user_id), {})
                        dm_channel_id = user_settings.get('dm_channel_id')

                        # DM 채널이 있으면 중복 체크 (실패 시 fresh DM으로 fallback — _send_notification 끝에서 dm_channel_id 자동 갱신)
                        if dm_channel_id:
                            try:
                                dm_channel = await bot_instance.fetch_channel(int(dm_channel_id))
                                last_sent_id = await get_last_sent_video_id_from_channel(dm_channel)
                                if last_sent_id == video_id:
                                    print(f"  -> 구독자 '{user.name}#{user.discriminator}' (ID: {user_id}): 이미 전송된 영상")
                                    return
                            except Exception as channel_error:
                                print(f"  -> [경고] DM 채널 {dm_channel_id} 확인 실패 (새로 전송 시도): {channel_error}")

                        print(f"  -> 구독자 '{user.name}#{user.discriminator}' (ID: {user_id})에게 DM 전송")
                        await _send_notification(user, video_id, snippet, is_shorts)
                    except discord.NotFound:
                        print(f"  -> [오류] 구독자 ID({user_id})를 찾을 수 없습니다. 목록에서 제거를 고려해보세요.")
                    except Exception as e:
                        print(f"  -> [오류] 구독자 ID({user_id}) 처리 중 오류: {e}")

            # 4. 각 영상을 순차로 전송 (길드/구독자는 세마포로 제한 동시)
            subscribers = await asyncio.to_thread(config.get_youtube_subscribers)
            print(f"  총 {len(subscribers)}명의 개인 구독자, {len(bot_instance.guilds)}개 서버")

            for video in videos_to_send:
                v_id = video['snippet']['resourceId']['videoId']
                v_snippet = video['snippet']
                print(f"- 영상 처리: {v_snippet.get('title', '')[:40]}")

                # 쇼츠 여부는 영상당 1회만 — 전엔 전송 대상(수백)마다 중복 호출해 스레드풀 포화
                v_is_shorts = await check_video_duration(v_id)

                guild_tasks = [send_to_guild(guild, v_id, v_snippet, v_is_shorts) for guild in bot_instance.guilds]
                user_tasks = [send_to_user(user_id, v_id, v_snippet, v_is_shorts) for user_id in subscribers]
                all_tasks = guild_tasks + user_tasks
                if all_tasks:
                    await asyncio.gather(*all_tasks, return_exceptions=True)

            # 5. LAST_CHECKED 는 전송 전 claim 단계에서 이미 latest 로 저장됨.
            #    (전송 후 저장 구조였다면 전송 중 재시작 시 중복 burst 발생 → claim 으로 선반영)
            print(f"[완료] 신규 영상 {len(videos_to_send)}개 전송. 최신 ID({latest_video_id}) 저장됨(claim).")

        except Exception as e:
            print(f"[오류] 유튜브 영상 확인 중 심각한 오류 발생: {e}")
            import traceback
            traceback.print_exc()


async def manual_check_new_videos():
    """수동으로 유튜브 새 영상을 확인하는 함수 (테스트용)"""
    if not youtube or not bot_instance:
        raise Exception("유튜브 API 또는 봇 인스턴스가 초기화되지 않았습니다.")
    
    print("[시작] 유튜브 새 영상 수동 체크 시작")
    try:
        # 1. 최신 영상 정보 가져오기 (동기 API → to_thread)
        non_live_videos = await asyncio.to_thread(_fetch_non_live_videos_sync)
        if not non_live_videos:
            raise Exception("일반 영상을 찾을 수 없습니다. (라이브 제외)")

        latest_video = non_live_videos[0]
        video_id = latest_video['snippet']['resourceId']['videoId']
        snippet = latest_video['snippet']

        # 2. 서버 채널에 공지 전송 (각 채널별 중복 체크)
        sent_channels = 0
        print("- 서버 채널 공지 시작")
        for guild in bot_instance.guilds:
            guild_settings = await asyncio.to_thread(config.get_guild_settings, guild.id)
            channel_id = guild_settings.get("ANNOUNCEMENT_CHANNEL_ID")
            if channel_id:
                channel = bot_instance.get_channel(int(channel_id))
                if channel:
                    last_sent_id = await get_last_sent_video_id_from_channel(channel)
                    if last_sent_id != video_id:
                        print(f"  -> 서버 '{guild.name}'에 새 영상 전송")
                        await _send_notification(channel, video_id, snippet)
                        sent_channels += 1
        
        # 4. 개인 구독자에게 DM 전송
        sent_dms = 0
        print("- 개인 구독자 DM 전송 시작")
        subscribers = await asyncio.to_thread(config.get_youtube_subscribers)
        for user_id in subscribers:
            try:
                user = await bot_instance.fetch_user(user_id)

                # DM 채널 ID 확인 (GCS에 저장된 정보)
                settings = await asyncio.to_thread(config.load_settings)
                user_settings = settings.get('users', {}).get(str(user_id), {})
                dm_channel_id = user_settings.get('dm_channel_id')

                # DM 채널이 있으면 중복 체크
                if dm_channel_id:
                    try:
                        dm_channel = await bot_instance.fetch_channel(int(dm_channel_id))
                        last_sent_id = await get_last_sent_video_id_from_channel(dm_channel)
                        if last_sent_id == video_id:
                            print(f"  -> 구독자 '{user.name}': 이미 전송된 영상")
                            continue
                    except Exception as channel_error:
                        print(f"  -> [경고] DM 채널 확인 실패 (새로 전송 시도): {channel_error}")

                print(f"  -> 구독자 '{user.name}'에게 DM 전송")
                await _send_notification(user, video_id, snippet)
                sent_dms += 1
            except Exception as e:
                print(f"  -> [오류] 구독자 ID({user_id}) 처리 중 오류: {e}")

        # 5. 마지막으로 확인한 영상 ID와 제목 저장
        video_title = snippet.get('title', '제목 없음') if snippet else '제목 없음'
        await asyncio.to_thread(config.save_last_video_info, video_id, video_title)
        print(f"[완료] 새 영상 ID({video_id}), 제목({video_title})을 전역 설정에 저장했습니다.")
        
        return f"테스트 완료! 영상: {video_title}\n서버 {sent_channels}개, DM {sent_dms}개 전송"

    except Exception as e:
        print(f"[오류] 유튜브 영상 확인 중 심각한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise e
    finally:
        print("[시작] 유튜브 새 영상 수동 체크 종료\n")

async def manual_check_for_user(user):
    """특정 사용자에게만 유튜브 새 영상 테스트를 전송하는 함수"""
    if not youtube or not bot_instance:
        raise Exception("유튜브 API 또는 봇 인스턴스가 초기화되지 않았습니다.")
    
    print(f"[시작] 사용자 '{user.name}'에 대한 유튜브 테스트 시작")
    try:
        # 1. 최신 영상 정보 가져오기 (동기 API → to_thread)
        non_live_videos = await asyncio.to_thread(_fetch_non_live_videos_sync)
        if not non_live_videos:
            raise Exception("일반 영상을 찾을 수 없습니다. (라이브 제외)")

        latest_video = non_live_videos[0]
        video_id = latest_video['snippet']['resourceId']['videoId']
        snippet = latest_video['snippet']

        # 2. DM 채널에서 중복 확인
        settings = await asyncio.to_thread(config.load_settings)
        user_settings = settings.get('users', {}).get(str(user.id), {})
        dm_channel_id = user_settings.get('dm_channel_id')

        if dm_channel_id:
            try:
                dm_channel = await bot_instance.fetch_channel(int(dm_channel_id))
                last_sent_id = await get_last_sent_video_id_from_channel(dm_channel)
                if last_sent_id == video_id:
                    return f"테스트 결과: 이미 전송된 영상입니다.\n영상: {snippet['title'][:50]}..."
            except Exception as channel_error:
                print(f"  -> [경고] DM 채널 확인 실패 (새로 전송 시도): {channel_error}")

        # 3. 해당 사용자에게 테스트 전송
        print(f"  -> 사용자 '{user.name}'에게 테스트 영상 전송")
        success = await _send_notification(user, video_id, snippet)

        if success:
            return f"테스트 완료! 영상: {snippet['title'][:50]}...\n사용자 '{user.name}'에게 전송 성공"
        else:
            return f"테스트 실패! 영상: {snippet['title'][:50]}...\n사용자 '{user.name}'에게 전송 실패"

    except Exception as e:
        print(f"[오류] 사용자 유튜브 테스트 중 오류 발생: {e}")
        raise e
    finally:
        print("[시작] 사용자 유튜브 테스트 종료\n")

async def manual_check_for_guild(guild):
    """특정 서버에만 유튜브 새 영상 테스트를 전송하는 함수"""
    if not youtube or not bot_instance:
        raise Exception("유튜브 API 또는 봇 인스턴스가 초기화되지 않았습니다.")
    
    print(f"[시작] 서버 '{guild.name}'에 대한 유튜브 테스트 시작")
    try:
        # 1. 최신 영상 정보 가져오기 (동기 API → to_thread)
        non_live_videos = await asyncio.to_thread(_fetch_non_live_videos_sync)
        if not non_live_videos:
            raise Exception("일반 영상을 찾을 수 없습니다. (라이브 제외)")

        latest_video = non_live_videos[0]
        video_id = latest_video['snippet']['resourceId']['videoId']
        snippet = latest_video['snippet']

        # 2. 해당 서버의 공지 채널 확인 및 전송
        guild_settings = await asyncio.to_thread(config.get_guild_settings, guild.id)
        channel_id = guild_settings.get("ANNOUNCEMENT_CHANNEL_ID")
        
        if not channel_id:
            return f"테스트 실패! 서버 '{guild.name}'에 공지 채널이 설정되지 않았습니다."
        
        channel = bot_instance.get_channel(int(channel_id))
        if not channel:
            return f"테스트 실패! 설정된 공지 채널을 찾을 수 없습니다."

        # 3. 채널 메시지 기반 중복 체크 (실제 알림과 동일한 방식)
        last_sent_id = await get_last_sent_video_id_from_channel(channel)
        if last_sent_id == video_id:
            return f"테스트 결과: 이미 전송된 영상입니다.\n영상: {snippet['title'][:50]}...\n채널: #{channel.name}"
        
        # 4. 테스트 전송
        print(f"  -> 서버 '{guild.name}' (ID: {guild.id})의 #{channel.name} (ID: {channel_id}) 채널에 테스트 영상 전송")
        success = await _send_notification(channel, video_id, snippet)
        
        if success:
            return f"테스트 완료! 영상: {snippet['title'][:50]}...\n서버: {guild.name}\n채널: #{channel.name}\n전송 성공"
        else:
            return f"테스트 실패! 영상: {snippet['title'][:50]}...\n서버: {guild.name}\n채널: #{channel.name}\n전송 실패 (권한 부족?)"

    except Exception as e:
        print(f"[오류] 서버 유튜브 테스트 중 오류 발생: {e}")
        raise e
    finally:
        print(f"[시작] 서버 '{guild.name}' 유튜브 테스트 종료\n")

@check_new_videos.before_loop
async def before_check():
    await bot_instance.wait_until_ready()

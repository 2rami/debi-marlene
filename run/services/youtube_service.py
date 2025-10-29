import discord
from discord.ext import tasks
from googleapiclient.discovery import build

from run.core.config import YOUTUBE_API_KEY, ETERNAL_RETURN_CHANNEL_ID, get_guild_settings
from run.core import config

youtube = None
bot_instance = None

def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot

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
        video_response = youtube.videos().list(
            part='contentDetails',
            id=video_id
        ).execute()
        
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
    try:
        async for message in channel.history(limit=50):
            if message.author.id == bot_instance.user.id and message.embeds:
                for embed in message.embeds:
                    if embed.url and ('youtube.com/watch?v=' in embed.url or 'youtu.be/' in embed.url):
                        import re
                        match = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', embed.url)
                        if match:
                            return match.group(1)
    except discord.Forbidden:
        print(f"[오류] 채널 '{channel.name}'의 메시지를 읽을 권한이 없습니다.")
    except Exception as e:
        print(f"[오류] 채널 '{channel.name}'에서 마지막 영상 ID 확인 중 오류: {e}")
    return None

async def _send_notification(channel_or_user, video_id, snippet):
    """지정된 채널 또는 유저에게 알림을 보냅니다."""
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        is_shorts = await check_video_duration(video_id)

        # 쇼츠면 데비, 일반 영상이면 마를렌
        if is_shorts:
            char_name = "데비"
            char_color = 0x0000FF  # 파랑
            char_image = "https://raw.githubusercontent.com/2rami/debi-marlene/main/assets/debi.png"
            action_text = "새로운 쇼츠를 발견했어!"
        else:
            char_name = "마를렌"
            char_color = 0xDC143C  # 빨강
            char_image = "https://raw.githubusercontent.com/2rami/debi-marlene/main/assets/marlen.png"
            action_text = "새로운 영상을 가져왔어."

        embed = discord.Embed(
            title=f"**{snippet['title']}**",
            description=snippet.get('description', '')[:150] + '...' if snippet.get('description') else action_text,
            color=char_color
        )
        embed.set_author(name=f"{char_name}이(가) {action_text}", icon_url=char_image)
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
                settings = config.load_settings()
                if 'users' not in settings:
                    settings['users'] = {}

                if user_id not in settings['users']:
                    settings['users'][user_id] = {}

                # DM 채널 정보 업데이트
                settings['users'][user_id]['dm_channel_id'] = channel_id
                settings['users'][user_id]['user_name'] = user_name
                settings['users'][user_id]['last_dm'] = datetime.now().isoformat()

                # GCS에 저장
                config.save_settings(settings)
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

    try:
        # 1. 최신 영상 정보 가져오기
        channel_response = youtube.channels().list(part='contentDetails', id=ETERNAL_RETURN_CHANNEL_ID).execute()
        if not channel_response.get('items'): return
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        playlist_response = youtube.playlistItems().list(part='snippet', playlistId=uploads_playlist_id, maxResults=10).execute()
        if not playlist_response.get('items'): return

        non_live_videos = [item for item in playlist_response['items'] if 'liveStreamingDetails' not in youtube.videos().list(part='snippet,liveStreamingDetails', id=item['snippet']['resourceId']['videoId']).execute().get('items', [{}])[0]]
        if not non_live_videos: return

        latest_video = non_live_videos[0]
        video_id = latest_video['snippet']['resourceId']['videoId']
        snippet = latest_video['snippet']

        # 2. 서버별 알림 작업을 비동기로 생성 (각 채널별 중복 체크)
        import asyncio
        
        async def send_to_guild(guild, video_id, snippet):
            """개별 서버에 알림을 보내는 비동기 함수"""
            guild_settings = config.get_guild_settings(guild.id)
            channel_id = guild_settings.get("ANNOUNCEMENT_CHANNEL_ID")
            if channel_id:
                channel = bot_instance.get_channel(int(channel_id))
                if channel:
                    last_sent_id = await get_last_sent_video_id_from_channel(channel)
                    if last_sent_id != video_id:
                        print(f"  -> 서버 '{guild.name}' (ID: {guild.id})의 #{channel.name} (ID: {channel_id}) 채널에 새 영상 전송")
                        await _send_notification(channel, video_id, snippet)
                    else:
                        print(f"  -> 서버 '{guild.name}' (ID: {guild.id}): 이미 전송된 영상")
                else:
                    print(f"  -> 서버 '{guild.name}' (ID: {guild.id}): 채널 ID {channel_id}를 찾을 수 없음")
            else:
                print(f"  -> 서버 '{guild.name}' (ID: {guild.id}): 공지 채널 미설정")
        
        async def send_to_user(user_id, video_id, snippet):
            """개별 사용자에게 DM을 보내는 비동기 함수"""
            try:
                user = await bot_instance.fetch_user(user_id)
                print(f"  -> 구독자 '{user.name}#{user.discriminator}' (ID: {user_id})에게 DM 전송")
                await _send_notification(user, video_id, snippet)
            except discord.NotFound:
                print(f"  -> [오류] 구독자 ID({user_id})를 찾을 수 없습니다. 목록에서 제거를 고려해보세요.")
            except Exception as e:
                print(f"  -> [오류] 구독자 ID({user_id}) 처리 중 오류: {e}")
        
        # 3. 서버 채널과 개인 DM 모두 동시에 전송
        print("- 서버 채널 및 개인 구독자 동시 알림 시작")
        
        # 서버 알림 작업 생성
        guild_tasks = [send_to_guild(guild, video_id, snippet) for guild in bot_instance.guilds]
        
        # 개인 구독자 DM 작업 생성
        subscribers = config.get_youtube_subscribers()
        print(f"  총 {len(subscribers)}명의 개인 구독자, {len(bot_instance.guilds)}개 서버")
        user_tasks = [send_to_user(user_id, video_id, snippet) for user_id in subscribers]
        
        # 모든 작업을 동시에 실행
        all_tasks = guild_tasks + user_tasks
        if all_tasks:
            await asyncio.gather(*all_tasks, return_exceptions=True)

        # 5. 마지막으로 확인한 영상 ID와 제목 저장
        video_title = snippet.get('title', '제목 없음') if snippet else '제목 없음'
        config.save_last_video_info(video_id, video_title)
        print(f"[완료] 새 영상 ID({video_id}), 제목({video_title})을 전역 설정에 저장했습니다.")

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
        # 1. 최신 영상 정보 가져오기
        channel_response = youtube.channels().list(part='contentDetails', id=ETERNAL_RETURN_CHANNEL_ID).execute()
        if not channel_response.get('items'): 
            raise Exception("채널 정보를 가져올 수 없습니다.")
            
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        playlist_response = youtube.playlistItems().list(part='snippet', playlistId=uploads_playlist_id, maxResults=10).execute()
        if not playlist_response.get('items'): 
            raise Exception("플레이리스트 정보를 가져올 수 없습니다.")

        non_live_videos = [item for item in playlist_response['items'] if 'liveStreamingDetails' not in youtube.videos().list(part='snippet,liveStreamingDetails', id=item['snippet']['resourceId']['videoId']).execute().get('items', [{}])[0]]
        if not non_live_videos: 
            raise Exception("일반 영상을 찾을 수 없습니다. (라이브 제외)")

        latest_video = non_live_videos[0]
        video_id = latest_video['snippet']['resourceId']['videoId']
        snippet = latest_video['snippet']

        # 2. 서버 채널에 공지 전송 (각 채널별 중복 체크)
        sent_channels = 0
        print("- 서버 채널 공지 시작")
        for guild in bot_instance.guilds:
            guild_settings = config.get_guild_settings(guild.id)
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
        subscribers = config.get_youtube_subscribers()
        for user_id in subscribers:
            try:
                user = await bot_instance.fetch_user(user_id)
                print(f"  -> 구독자 '{user.name}'에게 DM 전송")
                await _send_notification(user, video_id, snippet)
                sent_dms += 1
            except Exception as e:
                print(f"  -> [오류] 구독자 ID({user_id}) 처리 중 오류: {e}")

        # 5. 마지막으로 확인한 영상 ID와 제목 저장
        video_title = snippet.get('title', '제목 없음') if snippet else '제목 없음'
        config.save_last_video_info(video_id, video_title)
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
        # 1. 최신 영상 정보 가져오기
        channel_response = youtube.channels().list(part='contentDetails', id=ETERNAL_RETURN_CHANNEL_ID).execute()
        if not channel_response.get('items'): 
            raise Exception("채널 정보를 가져올 수 없습니다.")
            
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        playlist_response = youtube.playlistItems().list(part='snippet', playlistId=uploads_playlist_id, maxResults=10).execute()
        if not playlist_response.get('items'): 
            raise Exception("플레이리스트 정보를 가져올 수 없습니다.")

        non_live_videos = [item for item in playlist_response['items'] if 'liveStreamingDetails' not in youtube.videos().list(part='snippet,liveStreamingDetails', id=item['snippet']['resourceId']['videoId']).execute().get('items', [{}])[0]]
        if not non_live_videos: 
            raise Exception("일반 영상을 찾을 수 없습니다. (라이브 제외)")

        latest_video = non_live_videos[0]
        video_id = latest_video['snippet']['resourceId']['videoId']
        snippet = latest_video['snippet']

        # 2. 해당 사용자에게 테스트 전송
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
        # 1. 최신 영상 정보 가져오기
        channel_response = youtube.channels().list(part='contentDetails', id=ETERNAL_RETURN_CHANNEL_ID).execute()
        if not channel_response.get('items'): 
            raise Exception("채널 정보를 가져올 수 없습니다.")
            
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        playlist_response = youtube.playlistItems().list(part='snippet', playlistId=uploads_playlist_id, maxResults=10).execute()
        if not playlist_response.get('items'): 
            raise Exception("플레이리스트 정보를 가져올 수 없습니다.")

        non_live_videos = [item for item in playlist_response['items'] if 'liveStreamingDetails' not in youtube.videos().list(part='snippet,liveStreamingDetails', id=item['snippet']['resourceId']['videoId']).execute().get('items', [{}])[0]]
        if not non_live_videos: 
            raise Exception("일반 영상을 찾을 수 없습니다. (라이브 제외)")

        latest_video = non_live_videos[0]
        video_id = latest_video['snippet']['resourceId']['videoId']
        snippet = latest_video['snippet']

        # 2. 해당 서버의 공지 채널 확인 및 전송
        guild_settings = config.get_guild_settings(guild.id)
        channel_id = guild_settings.get("ANNOUNCEMENT_CHANNEL_ID")
        
        if not channel_id:
            return f"테스트 실패! 서버 '{guild.name}'에 공지 채널이 설정되지 않았습니다."
        
        channel = bot_instance.get_channel(channel_id)
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

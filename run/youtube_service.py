import discord
from discord.ext import tasks
from googleapiclient.discovery import build
from run.config import YOUTUBE_API_KEY, ETERNAL_RETURN_CHANNEL_ID, characters
from run import config

youtube = None
last_checked_video_id = None
bot_instance = None

def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot

async def initialize_youtube():
    global youtube
    try:
        if YOUTUBE_API_KEY:
            youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        else:
            youtube = None
    except:
        youtube = None

async def check_video_duration(video_id):
    """영상 길이를 체크해서 쇼츠인지 판단 (60초 이하면 쇼츠)"""
    try:
        video_response = youtube.videos().list(
            part='contentDetails',
            id=video_id
        ).execute()
        
        if video_response['items']:
            duration = video_response['items'][0]['contentDetails']['duration']
            print(f"영상 길이 원본: {duration}")
            
            # PT1M = 1분, PT30S = 30초 형태로 옴
            import re
            # PT숫자H숫자M숫자S, PT숫자M숫자S, PT숫자S 등 다양한 형태 파싱
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)
                total_seconds = hours * 3600 + minutes * 60 + seconds
                print(f"파싱된 시간: {hours}시간 {minutes}분 {seconds}초 (총 {total_seconds}초)")
                is_short = total_seconds <= 60  # 60초 이하면 쇼츠
                print(f"쇼츠 판정: {is_short}")
                return is_short
        return False
    except Exception as e:
        print(f"영상 길이 체크 오류: {e}")
        return False

@tasks.loop(minutes=10)  # 30분 -> 10분으로 단축
async def check_new_videos():
    global last_checked_video_id, bot_instance
    
    print("=== 유튜브 체크 시작 ===")
    print(f"youtube 객체: {youtube is not None}")
    print(f"ANNOUNCEMENT_CHANNEL_ID: {config.ANNOUNCEMENT_CHANNEL_ID}")
    print(f"bot_instance: {bot_instance is not None}")
    print(f"last_checked_video_id: {last_checked_video_id}")
    
    if not youtube or not config.ANNOUNCEMENT_CHANNEL_ID or not bot_instance:
        print("필수 조건 중 하나가 없어서 종료")
        return
    
    try:
        # 채널의 uploads 플레이리스트에서 최신 영상들 가져오기 (더 정확함)
        # 먼저 채널 정보를 가져와서 uploads 플레이리스트 ID 얻기
        channel_response = youtube.channels().list(
            part='contentDetails',
            id=ETERNAL_RETURN_CHANNEL_ID
        ).execute()
        
        if not channel_response['items']:
            print("채널 정보를 찾을 수 없음")
            return
            
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        print(f"Uploads 플레이리스트 ID: {uploads_playlist_id}")
        
        # uploads 플레이리스트에서 최신 영상들 가져오기
        playlist_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=10  # 라이브 제외를 위해 더 많이 가져오기
        ).execute()
        
        print(f"플레이리스트 결과 개수: {len(playlist_response.get('items', []))}")
        
        if not playlist_response['items']:
            print("플레이리스트에서 영상을 찾을 수 없음")
            return
        
        # 라이브가 아닌 일반 영상/쇼츠만 필터링
        non_live_videos = []
        for item in playlist_response['items']:
            video_id_temp = item['snippet']['resourceId']['videoId']
            
            # 각 영상의 라이브 여부 확인
            video_details = youtube.videos().list(
                part='snippet,liveStreamingDetails',
                id=video_id_temp
            ).execute()
            
            if video_details['items']:
                video_info = video_details['items'][0]
                # 라이브가 아닌 경우만 추가
                if 'liveStreamingDetails' not in video_info:
                    non_live_videos.append(item)
                    print(f"일반 영상/쇼츠 발견: {item['snippet']['title']}")
                else:
                    print(f"라이브 영상 제외: {item['snippet']['title']}")
        
        if not non_live_videos:
            print("라이브가 아닌 영상을 찾을 수 없음")
            return
            
        # 가장 최신 일반 영상 선택
        latest_video = non_live_videos[0]
        video_id = latest_video['snippet']['resourceId']['videoId']
        snippet = latest_video['snippet']
        
        print(f"최신 영상 ID: {video_id}")
        print(f"최신 영상 제목: {snippet['title']}")
        print(f"게시 시간: {snippet['publishedAt']}")
        print(f"영상 ID 비교: 현재={last_checked_video_id}, 최신={video_id}")
        
        if last_checked_video_id != video_id:
            print("새로운 영상 발견! 전송 시작...")
            last_checked_video_id = video_id # 새로운 영상이므로 ID를 즉시 업데이트

            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # 영상 상세 정보 가져오기 (설명 포함)
            video_details = youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            video_description = ""
            if video_details['items']:
                full_description = video_details['items'][0]['snippet'].get('description', '')
                # 설명의 첫 100글자만 가져오기 (너무 길면 임베드에서 잘림)
                video_description = full_description[:100] + "..." if len(full_description) > 100 else full_description
            
            # 쇼츠인지 확인
            is_shorts = await check_video_duration(video_id)
            print(f"쇼츠 여부: {is_shorts}")
            print(f"영상 설명: {video_description}")
            
            # 쇼츠와 일반 영상 구분해서 임베드 생성
            if is_shorts:
                embed = discord.Embed(
                    title=f"**{snippet['title']}**",
                    description=video_description if video_description else "새로운 쇼츠가 올라왔어!",
                    color=characters["debi"]["color"]  # 데비 파란색
                )
                embed.set_author(
                    name="데비가 새로운 쇼츠를 발견했어!",
                    icon_url=characters["debi"]["image"]
                )
            else:
                embed = discord.Embed(
                    title=f"**{snippet['title']}**",
                    description=video_description if video_description else "새로운 영상이 올라왔어!",
                    color=characters["marlene"]["color"]  # 마를렌 빨간색
                )
                embed.set_author(
                    name="마를렌이 새로운 영상을 가져왔어!",
                    icon_url=characters["marlene"]["image"]
                )
            
            channel = bot_instance.get_channel(config.ANNOUNCEMENT_CHANNEL_ID)
            print(f"채널 객체: {channel}")
            if channel:
                # 먼저 링크만 보내서 재생 가능한 임베드 생성
                await channel.send(video_url)
                # 그 다음에 캐릭터 임베드 전송
                await channel.send(embed=embed)
                print("YouTube 재생 임베드 + 캐릭터 임베드 전송 완료!")
            else:
                print("채널을 찾을 수 없음")
        else:
            print("기존에 알고 있던 영상이므로 전송하지 않음")
        
    except Exception as e:
        print(f"유튜브 영상 확인 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    print("=== 유튜브 체크 끝 ===\n")
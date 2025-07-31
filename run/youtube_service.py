import discord
from discord.ext import tasks
from googleapiclient.discovery import build
from run.config import YOUTUBE_API_KEY, ETERNAL_RETURN_CHANNEL_ID
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

@tasks.loop(minutes=30)
async def check_youtube_shorts():
    global last_checked_video_id, bot_instance
    
    if not youtube or not config.ANNOUNCEMENT_CHANNEL_ID or not bot_instance:
        return
    
    try:
        search_response = youtube.search().list(
            part='snippet',
            channelId=ETERNAL_RETURN_CHANNEL_ID,
            maxResults=1,
            order='date',
            type='video'
        ).execute()
        
        if not search_response['items']:
            return
        
        latest_video = search_response['items'][0]
        video_id = latest_video['id']['videoId']
        
        if last_checked_video_id == video_id:
            return
        
        video_response = youtube.videos().list(
            part='snippet,contentDetails',
            id=video_id
        ).execute()
        
        if not video_response['items']:
            return
        
        video_details = video_response['items'][0]
        duration = video_details['contentDetails']['duration']
        
        if 'PT' in duration and 'M' not in duration:
            seconds = int(duration.replace('PT', '').replace('S', ''))
            if seconds <= 180:
                snippet = latest_video['snippet']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                embed = discord.Embed(
                    title="새로운 이터널 리턴 쇼츠",
                    description=f"**{snippet['title']}**\n\n{video_url}",
                    color=0xFF0000
                )
                embed.set_author(name="이터널 리턴 공식 채널")
                
                if 'thumbnails' in snippet:
                    embed.set_image(url=snippet['thumbnails']['medium']['url'])
                
                channel = bot_instance.get_channel(config.ANNOUNCEMENT_CHANNEL_ID)
                if channel:
                    await channel.send(embed=embed)
                
                last_checked_video_id = video_id
        
        last_checked_video_id = video_id
        
    except:
        pass
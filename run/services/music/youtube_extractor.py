"""
YouTube 오디오 추출기

yt-dlp를 사용하여 YouTube에서 오디오 스트림 URL을 추출합니다.
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Optional
import discord

logger = logging.getLogger(__name__)

try:
    import yt_dlp
except ImportError:
    yt_dlp = None
    logger.warning("yt-dlp가 설치되지 않았습니다. pip install yt-dlp")


@dataclass
class Song:
    """재생할 곡 정보"""
    url: str                      # YouTube URL
    title: str                    # 곡 제목
    duration: int                 # 재생 시간 (초)
    thumbnail: str                # 썸네일 URL
    requester: discord.Member     # 요청한 사용자
    stream_url: str               # 실제 오디오 스트림 URL


class YouTubeExtractor:
    """YouTube에서 오디오 정보를 추출하는 클래스"""

    COOKIE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'cookies.txt')

    @classmethod
    def _get_options(cls) -> dict:
        opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'no_color': True,
            'noprogress': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android'],
                }
            },
        }
        cookie_path = os.path.abspath(cls.COOKIE_PATH)
        if os.path.exists(cookie_path):
            opts['cookiefile'] = cookie_path
        return opts

    @classmethod
    async def extract_info(
        cls,
        query: str,
        requester: discord.Member
    ) -> Optional[Song]:
        """
        YouTube URL 또는 검색어로 곡 정보를 추출합니다.

        Args:
            query: YouTube URL 또는 검색어
            requester: 요청한 사용자

        Returns:
            Song 객체 또는 None (실패 시)
        """
        if yt_dlp is None:
            logger.error("yt-dlp가 설치되지 않았습니다")
            return None

        # URL인지 검색어인지 판단
        if not query.startswith(('http://', 'https://')):
            query = f"ytsearch:{query}"

        try:
            # 비동기로 실행 (블로킹 방지)
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None,
                lambda: cls._extract_with_ytdlp(query)
            )

            if info is None:
                return None

            # 검색 결과인 경우 첫 번째 결과 사용
            if 'entries' in info:
                if not info['entries']:
                    return None
                info = info['entries'][0]

            # Song 객체 생성
            return Song(
                url=info.get('webpage_url', info.get('url', query)),
                title=info.get('title', '알 수 없는 제목'),
                duration=info.get('duration', 0) or 0,
                thumbnail=info.get('thumbnail', ''),
                requester=requester,
                stream_url=info.get('url', '')
            )

        except Exception as e:
            logger.error(f"YouTube 정보 추출 실패: {e}")
            return None

    @classmethod
    def _extract_with_ytdlp(cls, query: str) -> Optional[dict]:
        """yt-dlp로 정보 추출 (동기 함수)"""
        try:
            with yt_dlp.YoutubeDL(cls._get_options()) as ydl:
                return ydl.extract_info(query, download=False)
        except Exception as e:
            logger.error(f"yt-dlp 추출 오류: {e}")
            return None

    @classmethod
    async def refresh_stream_url(cls, song: Song) -> Optional[str]:
        """
        만료된 스트림 URL을 새로 가져옵니다.

        Args:
            song: 기존 Song 객체

        Returns:
            새로운 스트림 URL 또는 None
        """
        if yt_dlp is None:
            return None

        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None,
                lambda: cls._extract_with_ytdlp(song.url)
            )

            if info and 'url' in info:
                return info['url']

        except Exception as e:
            logger.error(f"스트림 URL 갱신 실패: {e}")

        return None


def format_duration(seconds: int) -> str:
    """초를 MM:SS 또는 HH:MM:SS 형식으로 변환"""
    if seconds <= 0:
        return "라이브"

    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"

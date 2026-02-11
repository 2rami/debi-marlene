"""
노래 맞추기 퀴즈

YouTube에서 노래 클립을 재생하고 채팅으로 제목/가수를 맞추는 게임입니다.
"""

import asyncio
import difflib
import logging
import random
import re
from dataclasses import dataclass
from typing import Optional, List

import discord

from run.services.music.youtube_extractor import YouTubeExtractor
from run.services.voice_manager import voice_manager, FFMPEG_PATH

logger = logging.getLogger(__name__)

CLIP_DURATION = 25  # 클립 재생 시간 (초)
ANSWER_TIMEOUT = 30  # 정답 입력 제한 시간 (초)
HINT_DELAY = 15  # 힌트 제공까지 대기 시간 (초)
SIMILARITY_THRESHOLD = 0.7  # 유사도 기준


SKIP_KEYWORDS = {"스킵", "넘기기", "skip", "pass", "넘겨"}


@dataclass
class SongEntry:
    title: str
    artist: str
    query: str  # YouTube 검색어
    aliases: Optional[List[str]] = None  # 아티스트/제목 대체 이름 (한글 등)


# 내장 곡 목록 (초기 데이터)
SONG_LIST: List[SongEntry] = [
    # K-pop
    SongEntry("Ditto", "NewJeans", "NewJeans Ditto", ["뉴진스"]),
    SongEntry("Super Shy", "NewJeans", "NewJeans Super Shy", ["뉴진스", "슈퍼샤이"]),
    SongEntry("Hype Boy", "NewJeans", "NewJeans Hype Boy", ["뉴진스", "하이프보이"]),
    SongEntry("APT.", "ROSE", "ROSE APT Bruno Mars", ["로제", "브루노마스"]),
    SongEntry("Supernova", "aespa", "aespa Supernova", ["에스파", "슈퍼노바"]),
    SongEntry("Next Level", "aespa", "aespa Next Level", ["에스파", "넥스트레벨"]),
    SongEntry("Love Dive", "IVE", "IVE Love Dive", ["아이브", "러브다이브"]),
    SongEntry("HEYA", "IVE", "IVE HEYA", ["아이브", "해야"]),
    SongEntry("Magnetic", "ILLIT", "ILLIT Magnetic", ["아일릿"]),
    SongEntry("SPOT!", "ZICO", "ZICO SPOT Jennie", ["지코", "제니"]),
    SongEntry("Butter", "BTS", "BTS Butter", ["방탄소년단", "방탄", "버터"]),
    SongEntry("Dynamite", "BTS", "BTS Dynamite", ["방탄소년단", "방탄", "다이너마이트"]),
    SongEntry("How Sweet", "NewJeans", "NewJeans How Sweet", ["뉴진스"]),
    SongEntry("GODS", "NewJeans", "NewJeans GODS", ["뉴진스"]),
    SongEntry("Drama", "aespa", "aespa Drama", ["에스파", "드라마"]),
    SongEntry("Kitsch", "IVE", "IVE Kitsch", ["아이브", "키치"]),
    SongEntry("Panorama", "IZ*ONE", "IZ*ONE Panorama", ["아이즈원", "파노라마"]),
    SongEntry("Antifragile", "LE SSERAFIM", "LE SSERAFIM Antifragile", ["르세라핌"]),
    SongEntry("EASY", "LE SSERAFIM", "LE SSERAFIM EASY", ["르세라핌"]),
    SongEntry("Queencard", "(G)I-DLE", "GIDLE Queencard", ["여자아이들", "아이들", "퀸카"]),
    SongEntry("TOMBOY", "(G)I-DLE", "GIDLE TOMBOY", ["여자아이들", "아이들", "톰보이"]),
    SongEntry("Pink Venom", "BLACKPINK", "BLACKPINK Pink Venom", ["블랙핑크", "블핑"]),
    SongEntry("Shut Down", "BLACKPINK", "BLACKPINK Shut Down", ["블랙핑크", "블핑"]),
    SongEntry("OMG", "NewJeans", "NewJeans OMG", ["뉴진스"]),
    SongEntry("Candy", "NCT DREAM", "NCT DREAM Candy", ["엔시티드림", "엔시티"]),
    # Anime / Game OST
    SongEntry("Idol", "YOASOBI", "YOASOBI Idol Oshi no Ko", ["요아소비", "아이돌"]),
    SongEntry("Zankyosanka", "Aimer", "Aimer 残響散歌 Demon Slayer", ["에메", "잔향산가"]),
    SongEntry("Shinunoga E-Wa", "Fujii Kaze", "Fujii Kaze Shinunoga E-Wa", ["후지이카제", "후지카제"]),
    SongEntry("Kick Back", "Kenshi Yonezu", "Kenshi Yonezu Kick Back Chainsaw Man", ["요네즈켄시", "켄시요네즈", "요네즈 켄시"]),
    SongEntry("Unravel", "TK from Ling tosite sigure", "TK Unravel Tokyo Ghoul", ["언라벨"]),
    SongEntry("Gurenge", "LiSA", "LiSA Gurenge Demon Slayer", ["리사", "홍련화"]),
    SongEntry("Pretender", "Official HIGE DANdism", "Official HIGE DANdism Pretender", ["히게단", "히게단디즘"]),
    SongEntry("Cry Baby", "Official HIGE DANdism", "Official HIGE DANdism Cry Baby", ["히게단", "히게단디즘", "크라이베이비"]),
    SongEntry("Racing into the Night", "YOASOBI", "YOASOBI 夜に駆ける", ["요아소비", "밤을달리다", "밤을 달리다", "요루니카게루"]),
    SongEntry("Kaikai Kitan", "Eve", "Eve Kaikai Kitan Jujutsu Kaisen", ["이브", "괴괴기담"]),
    # Pop
    SongEntry("Blinding Lights", "The Weeknd", "The Weeknd Blinding Lights", ["위켄드", "더위켄드"]),
    SongEntry("Shape of You", "Ed Sheeran", "Ed Sheeran Shape of You", ["에드시런"]),
    SongEntry("Levitating", "Dua Lipa", "Dua Lipa Levitating", ["두아리파"]),
    SongEntry("Flowers", "Miley Cyrus", "Miley Cyrus Flowers", ["마일리사이러스"]),
    SongEntry("Anti-Hero", "Taylor Swift", "Taylor Swift Anti-Hero", ["테일러스위프트"]),
    SongEntry("As It Was", "Harry Styles", "Harry Styles As It Was", ["해리스타일스"]),
    SongEntry("Cruel Summer", "Taylor Swift", "Taylor Swift Cruel Summer", ["테일러스위프트"]),
    SongEntry("Die With A Smile", "Lady Gaga", "Lady Gaga Bruno Mars Die With A Smile", ["레이디가가", "브루노마스"]),
    SongEntry("Espresso", "Sabrina Carpenter", "Sabrina Carpenter Espresso", ["사브리나카펜터"]),
    SongEntry("Greedy", "Tate McRae", "Tate McRae Greedy", ["테이트맥레이"]),
]


def _normalize(text: str) -> str:
    """비교용 텍스트 정규화"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s가-힣]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def is_skip_command(user_input: str) -> bool:
    """스킵 명령어인지 판정합니다."""
    return _normalize(user_input) in SKIP_KEYWORDS


def _match_target(normalized: str, target: str) -> bool:
    """정규화된 입력과 대상 문자열을 비교합니다."""
    if not target:
        return False
    if target in normalized or normalized in target:
        return True
    ratio = difflib.SequenceMatcher(None, normalized, target).ratio()
    return ratio >= SIMILARITY_THRESHOLD


def check_answer(user_input: str, song: SongEntry) -> Optional[str]:
    """사용자 입력이 정답인지 판정합니다.

    Returns:
        "title" - 제목을 맞힌 경우
        "artist" - 가수를 맞힌 경우
        None - 정답이 아닌 경우
    """
    normalized = _normalize(user_input)
    if not normalized:
        return None

    # 제목 체크
    if _match_target(normalized, _normalize(song.title)):
        return "title"

    # 가수 체크
    if _match_target(normalized, _normalize(song.artist)):
        return "artist"

    # 별명 체크 (제목 또는 가수 대체)
    if song.aliases:
        for alias in song.aliases:
            if _match_target(normalized, _normalize(alias)):
                return "artist"

    return None


def is_correct_answer(user_input: str, song: SongEntry) -> bool:
    """하위 호환용 래퍼."""
    return check_answer(user_input, song) is not None


def get_hint(song: SongEntry) -> str:
    """힌트를 생성합니다."""
    artist = song.artist
    if len(artist) > 1:
        return f"가수: {artist[0]}{'_' * (len(artist) - 1)}"
    return f"가수: {'_' * 3}"


class SongQuiz:
    """노래 퀴즈 게임 로직"""

    def __init__(self, guild_id: str, total_questions: int):
        self.guild_id = guild_id
        self.total_questions = total_questions
        self._used_indices: set = set()

    def pick_song(self) -> Optional[SongEntry]:
        """중복 없이 랜덤 곡을 선택합니다."""
        available = [i for i in range(len(SONG_LIST)) if i not in self._used_indices]
        if not available:
            # 전부 사용했으면 리셋
            self._used_indices.clear()
            available = list(range(len(SONG_LIST)))

        idx = random.choice(available)
        self._used_indices.add(idx)
        return SONG_LIST[idx]

    @staticmethod
    async def get_stream_url(song: SongEntry, bot_user: discord.Member) -> Optional[str]:
        """YouTube에서 스트림 URL을 가져옵니다."""
        result = await YouTubeExtractor.extract_info(song.query, bot_user)
        if result:
            return result.stream_url
        return None

    @staticmethod
    async def play_clip(guild_id: str, stream_url: str, duration: int) -> bool:
        """음성 채널에서 노래 클립을 재생합니다."""
        vc = voice_manager.get_voice_client(guild_id)
        if not vc or not vc.is_connected():
            return False

        # 랜덤 시작 지점 (최소 10초부터, 안전 마진 확보)
        start = random.randint(10, max(10, duration - CLIP_DURATION - 10))
        if duration < 60:
            start = 0

        before_options = (
            f'-ss {start} -t {CLIP_DURATION} '
            '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
            '-user_agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"'
        )

        try:
            audio_source = discord.FFmpegPCMAudio(
                stream_url,
                executable=FFMPEG_PATH,
                before_options=before_options,
                options='-vn',
            )

            play_finished = asyncio.Event()

            def after_play(error):
                if error:
                    logger.error(f"노래 클립 재생 오류: {error}")
                play_finished.set()

            vc.play(audio_source, after=after_play)
            # 클립 끝날 때까지 기다리되, 최대 CLIP_DURATION + 5초
            await asyncio.wait_for(play_finished.wait(), timeout=CLIP_DURATION + 5)
            return True

        except asyncio.TimeoutError:
            if vc.is_playing():
                vc.stop()
            return True
        except Exception as e:
            logger.error(f"노래 클립 재생 실패: {e}")
            return False

    @staticmethod
    def stop_playback(guild_id: str):
        """재생 중인 오디오를 중지합니다."""
        vc = voice_manager.get_voice_client(guild_id)
        if vc and vc.is_playing():
            vc.stop()

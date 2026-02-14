"""
퀴즈 게임 세션 관리

서버별 퀴즈 세션을 관리합니다.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict

logger = logging.getLogger(__name__)


@dataclass
class QuizSession:
    """퀴즈 게임 세션"""
    guild_id: str
    channel_id: int
    quiz_type: str  # "song" | "er"
    total_questions: int
    current_question: int = 0
    scores: Dict[int, int] = field(default_factory=dict)
    title_scores: Dict[int, int] = field(default_factory=dict)
    artist_scores: Dict[int, int] = field(default_factory=dict)
    is_active: bool = True
    _stop_event: asyncio.Event = field(default_factory=asyncio.Event, repr=False)

    def add_score(self, user_id: int, points: int = 1):
        """유저 점수를 추가합니다."""
        self.scores[user_id] = self.scores.get(user_id, 0) + points

    def add_title_score(self, user_id: int):
        """제목 맞힌 점수를 추가합니다."""
        self.title_scores[user_id] = self.title_scores.get(user_id, 0) + 1
        self.add_score(user_id)

    def add_artist_score(self, user_id: int):
        """가수 맞힌 점수를 추가합니다."""
        self.artist_scores[user_id] = self.artist_scores.get(user_id, 0) + 1
        self.add_score(user_id)

    def get_rankings(self) -> list:
        """점수 순으로 정렬된 랭킹을 반환합니다."""
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)


class QuizManager:
    """서버별 퀴즈 세션 관리자"""

    _sessions: Dict[str, QuizSession] = {}

    @classmethod
    def start_session(
        cls,
        guild_id: str,
        channel_id: int,
        quiz_type: str,
        total_questions: int
    ) -> QuizSession:
        """새 퀴즈 세션을 시작합니다."""
        session = QuizSession(
            guild_id=guild_id,
            channel_id=channel_id,
            quiz_type=quiz_type,
            total_questions=total_questions,
        )
        cls._sessions[guild_id] = session
        logger.info(f"퀴즈 세션 시작: {guild_id} ({quiz_type}, {total_questions}문제)")
        return session

    @classmethod
    def end_session(cls, guild_id: str) -> Optional[QuizSession]:
        """퀴즈 세션을 종료하고 결과를 반환합니다."""
        session = cls._sessions.pop(guild_id, None)
        if session:
            session.is_active = False
            session._stop_event.set()
            logger.info(f"퀴즈 세션 종료: {guild_id}")
        return session

    @classmethod
    def get_session(cls, guild_id: str) -> Optional[QuizSession]:
        """현재 진행 중인 세션을 반환합니다."""
        return cls._sessions.get(guild_id)

    @classmethod
    def has_active_session(cls, guild_id: str) -> bool:
        """진행 중인 세션이 있는지 확인합니다."""
        session = cls._sessions.get(guild_id)
        return session is not None and session.is_active

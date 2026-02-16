"""
퀴즈 데이터 GCS 저장소

퀴즈 결과(세션 히스토리, 리더보드)와 곡 목록을 GCS에 저장/로드합니다.
GCS 키: quiz_data.json (settings.json과 분리)
"""

import json
import logging
import random
import string
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

GCS_BUCKET = 'debi-marlene-settings'
GCS_QUIZ_KEY = 'quiz_data.json'
MAX_SESSIONS_PER_GUILD = 50


def _get_gcs_client():
    """GCS 클라이언트를 가져옵니다. (봇의 config 모듈 재사용)"""
    from run.core.config import get_gcs_client
    return get_gcs_client()


def load_quiz_data() -> dict:
    """GCS에서 quiz_data.json을 로드합니다."""
    try:
        client = _get_gcs_client()
        if not client:
            return {"songs": [], "guilds": {}}

        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_QUIZ_KEY)

        if not blob.exists():
            return {"songs": [], "guilds": {}}

        data = json.loads(blob.download_as_text())
        return data
    except Exception as e:
        logger.error(f"퀴즈 데이터 로드 실패: {e}")
        return {"songs": [], "guilds": {}}


def save_quiz_data(data: dict) -> bool:
    """GCS에 quiz_data.json을 저장합니다."""
    try:
        client = _get_gcs_client()
        if not client:
            return False

        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_QUIZ_KEY)
        blob.upload_from_string(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type='application/json',
        )
        return True
    except Exception as e:
        logger.error(f"퀴즈 데이터 저장 실패: {e}")
        return False


def save_quiz_result(guild_id: str, session) -> bool:
    """퀴즈 결과를 GCS에 저장하고 리더보드를 업데이트합니다.

    Args:
        guild_id: 서버 ID
        session: QuizSession 객체 (scores, title_scores, artist_scores 등)
    """
    if not session.scores:
        return False

    try:
        data = load_quiz_data()
        guilds = data.setdefault("guilds", {})
        guild_data = guilds.setdefault(guild_id, {"sessions": [], "leaderboard": {}})

        # 세션 기록 추가
        session_id = f"{int(datetime.now(timezone.utc).timestamp())}_{_random_id()}"
        winner_id = None
        if session.scores:
            winner_id = str(max(session.scores, key=session.scores.get))

        session_record = {
            "id": session_id,
            "quiz_type": session.quiz_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_questions": session.total_questions,
            "participants": len(session.scores),
            "scores": {str(k): v for k, v in session.scores.items()},
            "winner_id": winner_id,
        }

        if session.quiz_type == "song":
            session_record["title_scores"] = {str(k): v for k, v in session.title_scores.items()}
            session_record["artist_scores"] = {str(k): v for k, v in session.artist_scores.items()}

        sessions = guild_data.setdefault("sessions", [])
        sessions.append(session_record)

        # 최근 50개만 유지
        if len(sessions) > MAX_SESSIONS_PER_GUILD:
            guild_data["sessions"] = sessions[-MAX_SESSIONS_PER_GUILD:]

        # 리더보드 업데이트
        leaderboard = guild_data.setdefault("leaderboard", {})
        for user_id, score in session.scores.items():
            uid = str(user_id)
            entry = leaderboard.setdefault(uid, {
                "display_name": "",
                "total_games": 0,
                "total_score": 0,
                "song_games": 0,
                "er_games": 0,
                "wins": 0,
                "title_correct": 0,
                "artist_correct": 0,
            })
            entry["total_games"] += 1
            entry["total_score"] += score

            if session.quiz_type == "song":
                entry["song_games"] += 1
                entry["title_correct"] += session.title_scores.get(user_id, 0)
                entry["artist_correct"] += session.artist_scores.get(user_id, 0)
            else:
                entry["er_games"] += 1

            if winner_id and uid == winner_id:
                entry["wins"] += 1

        save_quiz_data(data)
        logger.info(f"퀴즈 결과 저장 완료: {guild_id} ({session.quiz_type})")
        return True

    except Exception as e:
        logger.error(f"퀴즈 결과 저장 실패: {e}")
        return False


def update_leaderboard_names(guild_id: str, members: Dict[int, str]):
    """리더보드의 display_name을 업데이트합니다.

    Args:
        members: {user_id: display_name} 매핑
    """
    try:
        data = load_quiz_data()
        guild_data = data.get("guilds", {}).get(guild_id)
        if not guild_data:
            return

        leaderboard = guild_data.get("leaderboard", {})
        updated = False
        for user_id, name in members.items():
            uid = str(user_id)
            if uid in leaderboard and leaderboard[uid].get("display_name") != name:
                leaderboard[uid]["display_name"] = name
                updated = True

        if updated:
            save_quiz_data(data)
    except Exception as e:
        logger.error(f"리더보드 이름 업데이트 실패: {e}")


def load_song_list() -> Optional[List[dict]]:
    """GCS에서 곡 목록을 로드합니다. 없으면 None 반환."""
    try:
        data = load_quiz_data()
        songs = data.get("songs", [])
        return songs if songs else None
    except Exception as e:
        logger.error(f"곡 목록 로드 실패: {e}")
        return None


def _random_id(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

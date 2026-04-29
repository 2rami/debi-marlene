"""
퀴즈 데이터 Firestore 저장소

Firestore 구조:
  quiz/global                            - { songs: [...] }            # 글로벌 곡 목록
  quiz/{guild_id}                        - { songs, leaderboard }      # 서버별
  quiz/{guild_id}/sessions/{session_id}  - 개별 세션 기록 (최근 50개 유지)
"""

import asyncio
import logging
import random
import string
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

QUIZ_COLLECTION = 'quiz'
GLOBAL_DOC = 'global'
SESSIONS_SUBCOLLECTION = 'sessions'
MAX_SESSIONS_PER_GUILD = 50


def _get_fs():
    """봇의 config 모듈 Firestore 클라이언트 재사용."""
    from run.core.config import get_firestore_client
    return get_firestore_client()


# ─────── 저수준 helper ───────

def _get_global_songs() -> list:
    fs = _get_fs()
    if not fs:
        return []
    snap = fs.collection(QUIZ_COLLECTION).document(GLOBAL_DOC).get()
    if not snap.exists:
        return []
    return snap.to_dict().get('songs', []) or []


def _set_global_songs(songs: list) -> bool:
    fs = _get_fs()
    if not fs:
        return False
    fs.collection(QUIZ_COLLECTION).document(GLOBAL_DOC).set({'songs': songs}, merge=True)
    return True


def _get_guild_doc(guild_id: str) -> dict:
    """길드 문서 (songs + leaderboard). 없으면 빈 dict."""
    fs = _get_fs()
    if not fs:
        return {}
    snap = fs.collection(QUIZ_COLLECTION).document(str(guild_id)).get()
    if not snap.exists:
        return {}
    return snap.to_dict() or {}


def _set_guild_fields(guild_id: str, fields: dict) -> bool:
    fs = _get_fs()
    if not fs:
        return False
    fs.collection(QUIZ_COLLECTION).document(str(guild_id)).set(fields, merge=True)
    return True


def _list_guild_sessions(guild_id: str) -> list:
    """길드의 sessions subcollection 전체 (timestamp asc)."""
    fs = _get_fs()
    if not fs:
        return []
    docs = fs.collection(QUIZ_COLLECTION).document(str(guild_id)) \
        .collection(SESSIONS_SUBCOLLECTION).stream()
    sessions = [d.to_dict() for d in docs]
    sessions.sort(key=lambda s: s.get('timestamp', ''))
    return sessions


def _add_guild_session(guild_id: str, session_record: dict) -> bool:
    """세션 추가 + 50개 초과 시 가장 오래된 것 삭제."""
    fs = _get_fs()
    if not fs:
        return False
    sub = fs.collection(QUIZ_COLLECTION).document(str(guild_id)).collection(SESSIONS_SUBCOLLECTION)
    sub.document(session_record['id']).set(session_record)

    # 초과분 정리 (timestamp asc 로 가장 오래된 것부터 삭제)
    all_docs = list(sub.stream())
    if len(all_docs) > MAX_SESSIONS_PER_GUILD:
        all_docs.sort(key=lambda d: d.to_dict().get('timestamp', ''))
        for old in all_docs[: len(all_docs) - MAX_SESSIONS_PER_GUILD]:
            old.reference.delete()
    return True


# ─────── 외부 API ───────

def save_quiz_result(guild_id: str, session) -> bool:
    """퀴즈 결과 저장 + 리더보드 업데이트."""
    if not session.scores:
        return False

    try:
        gid = str(guild_id)
        guild_doc = _get_guild_doc(gid)
        leaderboard = guild_doc.get('leaderboard', {}) or {}

        session_id = f"{int(datetime.now(timezone.utc).timestamp())}_{_random_id()}"
        winner_id = str(max(session.scores, key=session.scores.get)) if session.scores else None

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

        _add_guild_session(gid, session_record)

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

        _set_guild_fields(gid, {'leaderboard': leaderboard})
        logger.info(f"퀴즈 결과 저장 완료: {gid} ({session.quiz_type})")
        return True

    except Exception as e:
        logger.error(f"퀴즈 결과 저장 실패: {e}")
        return False


def update_leaderboard_names(guild_id: str, members: Dict[int, str]):
    """리더보드 display_name 업데이트."""
    try:
        gid = str(guild_id)
        guild_doc = _get_guild_doc(gid)
        leaderboard = guild_doc.get('leaderboard', {}) or {}
        if not leaderboard:
            return

        updated = False
        for user_id, name in members.items():
            uid = str(user_id)
            if uid in leaderboard and leaderboard[uid].get('display_name') != name:
                leaderboard[uid]['display_name'] = name
                updated = True

        if updated:
            _set_guild_fields(gid, {'leaderboard': leaderboard})
    except Exception as e:
        logger.error(f"리더보드 이름 업데이트 실패: {e}")


def load_song_list(guild_id: Optional[str] = None) -> Optional[List[dict]]:
    """곡 목록 로드. 서버별 우선, 없으면 글로벌."""
    try:
        if guild_id:
            guild_songs = (_get_guild_doc(str(guild_id)) or {}).get('songs')
            if guild_songs:
                return guild_songs
        songs = _get_global_songs()
        return songs if songs else None
    except Exception as e:
        logger.error(f"곡 목록 로드 실패: {e}")
        return None


def load_global_songs() -> list:
    """글로벌 곡 목록."""
    try:
        return _get_global_songs()
    except Exception as e:
        logger.error(f"글로벌 곡 목록 로드 실패: {e}")
        return []


def save_global_songs(songs: list) -> bool:
    """글로벌 곡 목록 저장."""
    try:
        return _set_global_songs(songs)
    except Exception as e:
        logger.error(f"글로벌 곡 목록 저장 실패: {e}")
        return False


def load_guild_songs(guild_id: str) -> Optional[List[dict]]:
    """서버별 곡 목록. 없으면 None."""
    try:
        return (_get_guild_doc(str(guild_id)) or {}).get('songs')
    except Exception as e:
        logger.error(f"서버 곡 목록 로드 실패: {e}")
        return None


def save_guild_songs(guild_id: str, songs: List[dict]) -> bool:
    """서버별 곡 목록 저장."""
    try:
        return _set_guild_fields(str(guild_id), {'songs': songs})
    except Exception as e:
        logger.error(f"서버 곡 목록 저장 실패: {e}")
        return False


def init_guild_songs_from_global(guild_id: str) -> List[dict]:
    """글로벌 곡 목록을 서버별로 복사하여 초기화."""
    import copy
    global_songs = _get_global_songs()
    guild_songs = copy.deepcopy(global_songs)
    _set_guild_fields(str(guild_id), {'songs': guild_songs})
    return guild_songs


def get_guild_leaderboard(guild_id: str) -> dict:
    return (_get_guild_doc(str(guild_id)) or {}).get('leaderboard', {}) or {}


def get_guild_sessions(guild_id: str) -> list:
    """서버 세션 히스토리 (timestamp asc). 호출자가 reverse 가능."""
    return _list_guild_sessions(str(guild_id))


# ─────── async wrappers ───────

async def async_save_quiz_result(guild_id: str, session) -> bool:
    try:
        return await asyncio.to_thread(save_quiz_result, guild_id, session)
    except Exception as e:
        logger.error(f"퀴즈 결과 비동기 저장 실패: {e}")
        return False


async def async_update_leaderboard_names(guild_id: str, members: Dict[int, str]):
    try:
        await asyncio.to_thread(update_leaderboard_names, guild_id, members)
    except Exception as e:
        logger.error(f"리더보드 이름 비동기 업데이트 실패: {e}")


def _random_id(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

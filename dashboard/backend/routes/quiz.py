"""
Quiz Dashboard Routes

퀴즈 통계/랭킹 조회 및 곡 목록 CRUD API.
저장소는 run.services.quiz.quiz_storage (Firestore) 를 통해 통일.
"""

import logging
from flask import Blueprint, jsonify, session, request
from functools import wraps

from run.services.quiz import quiz_storage

logger = logging.getLogger(__name__)

quiz_bp = Blueprint('quiz', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        guild_id = kwargs.get('guild_id')
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        if guild_id and guild_id not in user.get('admin_servers', []):
            return jsonify({'error': 'Forbidden'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ---------- 퀴즈 통계 ----------

@quiz_bp.route('/<guild_id>/stats')
@admin_required
def get_quiz_stats(guild_id):
    """서버 퀴즈 통계 (리더보드 + 최근 세션)"""
    leaderboard = quiz_storage.get_guild_leaderboard(guild_id)
    sessions = quiz_storage.get_guild_sessions(guild_id)

    sorted_leaderboard = sorted(
        leaderboard.items(),
        key=lambda x: x[1].get('total_score', 0),
        reverse=True,
    )

    return jsonify({
        'leaderboard': [
            {'user_id': uid, **stats}
            for uid, stats in sorted_leaderboard
        ],
        'recent_sessions': sessions[-5:][::-1],
        'total_sessions': len(sessions),
    })


@quiz_bp.route('/<guild_id>/sessions')
@admin_required
def get_quiz_sessions(guild_id):
    """서버 퀴즈 세션 히스토리 (최신순)"""
    sessions = quiz_storage.get_guild_sessions(guild_id)
    return jsonify({'sessions': sessions[::-1]})


# ---------- 서버별 곡 목록 관리 ----------

def _ensure_guild_songs(guild_id):
    """서버별 곡 목록 보장. 없으면 글로벌에서 복사."""
    songs = quiz_storage.load_guild_songs(guild_id)
    if songs is not None:
        return songs
    return quiz_storage.init_guild_songs_from_global(guild_id)


@quiz_bp.route('/<guild_id>/songs')
@admin_required
def get_guild_songs(guild_id):
    """서버별 곡 목록 조회"""
    songs = _ensure_guild_songs(guild_id)
    return jsonify({'songs': songs, 'count': len(songs)})


@quiz_bp.route('/<guild_id>/songs', methods=['POST'])
@admin_required
def add_guild_song(guild_id):
    """서버별 곡 추가"""
    body = request.json
    if not body:
        return jsonify({'error': 'Request body required'}), 400

    title = body.get('title', '').strip()
    artist = body.get('artist', '').strip()
    query = body.get('query', '').strip()
    aliases = body.get('aliases', [])

    if not title or not artist or not query:
        return jsonify({'error': 'title, artist, query are required'}), 400

    songs = _ensure_guild_songs(guild_id)
    song = {'title': title, 'artist': artist, 'query': query}
    if aliases:
        song['aliases'] = [a.strip() for a in aliases if a.strip()]
    title_aliases = body.get('title_aliases', [])
    if title_aliases:
        song['title_aliases'] = [a.strip() for a in title_aliases if a.strip()]

    songs.append(song)
    quiz_storage.save_guild_songs(guild_id, songs)
    return jsonify({'success': True, 'song': song, 'index': len(songs) - 1})


@quiz_bp.route('/<guild_id>/songs/<int:index>', methods=['PUT'])
@admin_required
def update_guild_song(guild_id, index):
    """서버별 곡 수정"""
    body = request.json
    if not body:
        return jsonify({'error': 'Request body required'}), 400

    songs = _ensure_guild_songs(guild_id)
    if index < 0 or index >= len(songs):
        return jsonify({'error': 'Invalid index'}), 404

    title = body.get('title', '').strip()
    artist = body.get('artist', '').strip()
    query = body.get('query', '').strip()
    aliases = body.get('aliases', [])

    if not title or not artist or not query:
        return jsonify({'error': 'title, artist, query are required'}), 400

    songs[index] = {'title': title, 'artist': artist, 'query': query}
    if aliases:
        songs[index]['aliases'] = [a.strip() for a in aliases if a.strip()]
    title_aliases = body.get('title_aliases', [])
    if title_aliases:
        songs[index]['title_aliases'] = [a.strip() for a in title_aliases if a.strip()]

    quiz_storage.save_guild_songs(guild_id, songs)
    return jsonify({'success': True, 'song': songs[index]})


@quiz_bp.route('/<guild_id>/songs/<int:index>', methods=['DELETE'])
@admin_required
def delete_guild_song(guild_id, index):
    """서버별 곡 삭제"""
    songs = _ensure_guild_songs(guild_id)
    if index < 0 or index >= len(songs):
        return jsonify({'error': 'Invalid index'}), 404

    removed = songs.pop(index)
    quiz_storage.save_guild_songs(guild_id, songs)
    return jsonify({'success': True, 'removed': removed})


@quiz_bp.route('/<guild_id>/songs/reset', methods=['POST'])
@admin_required
def reset_guild_songs(guild_id):
    """서버 곡 목록을 글로벌 목록에서 다시 복사"""
    songs = quiz_storage.init_guild_songs_from_global(guild_id)
    return jsonify({'success': True, 'count': len(songs)})

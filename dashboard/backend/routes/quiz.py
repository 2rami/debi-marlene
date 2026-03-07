"""
Quiz Dashboard Routes

퀴즈 통계/랭킹 조회 및 곡 목록 CRUD API
"""

import json
import logging
from flask import Blueprint, jsonify, session, request
from functools import wraps

logger = logging.getLogger(__name__)

quiz_bp = Blueprint('quiz', __name__)

GCS_BUCKET = 'debi-marlene-settings'
GCS_QUIZ_KEY = 'quiz_data.json'
gcs_client = None


def get_gcs_client():
    global gcs_client
    if gcs_client is None:
        try:
            from google.cloud import storage
            gcs_client = storage.Client(project='ironic-objectivist-465713-a6')
        except Exception as e:
            logger.error(f'GCS 클라이언트 생성 실패: {e}')
            gcs_client = False
    return gcs_client if gcs_client != False else None


def load_quiz_data():
    client = get_gcs_client()
    if client:
        try:
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_QUIZ_KEY)
            if not blob.exists():
                return {"songs": [], "guilds": {}}
            return json.loads(blob.download_as_text())
        except Exception as e:
            logger.error(f'퀴즈 데이터 로드 실패: {e}')
    return {"songs": [], "guilds": {}}


def save_quiz_data(data):
    client = get_gcs_client()
    if client:
        try:
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_QUIZ_KEY)
            blob.upload_from_string(json_data, content_type='application/json')
            return True
        except Exception as e:
            logger.error(f'퀴즈 데이터 저장 실패: {e}')
    return False


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
    data = load_quiz_data()
    guild_data = data.get('guilds', {}).get(guild_id, {})

    leaderboard = guild_data.get('leaderboard', {})
    sessions = guild_data.get('sessions', [])

    # 리더보드를 총 점수 기준 내림차순 정렬
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
    """서버 퀴즈 세션 히스토리"""
    data = load_quiz_data()
    guild_data = data.get('guilds', {}).get(guild_id, {})
    sessions = guild_data.get('sessions', [])

    return jsonify({
        'sessions': sessions[::-1],
    })


# ---------- 서버별 곡 목록 관리 ----------

def _get_guild_songs(data, guild_id):
    """서버별 곡 목록을 가져옵니다. 없으면 글로벌에서 복사하여 초기화."""
    import copy
    guild_data = data.get('guilds', {}).get(guild_id, {})
    songs = guild_data.get('songs')
    if songs is not None:
        return songs

    # 글로벌 목록에서 복사하여 초기화
    global_songs = data.get('songs', [])
    guild_songs = copy.deepcopy(global_songs)
    guilds = data.setdefault('guilds', {})
    gd = guilds.setdefault(guild_id, {})
    gd['songs'] = guild_songs
    save_quiz_data(data)
    return guild_songs


@quiz_bp.route('/<guild_id>/songs')
@admin_required
def get_guild_songs(guild_id):
    """서버별 곡 목록 조회"""
    data = load_quiz_data()
    songs = _get_guild_songs(data, guild_id)
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

    data = load_quiz_data()
    songs = _get_guild_songs(data, guild_id)

    song = {
        'title': title,
        'artist': artist,
        'query': query,
    }
    if aliases:
        song['aliases'] = [a.strip() for a in aliases if a.strip()]
    title_aliases = body.get('title_aliases', [])
    if title_aliases:
        song['title_aliases'] = [a.strip() for a in title_aliases if a.strip()]

    songs.append(song)
    save_quiz_data(data)
    return jsonify({'success': True, 'song': song, 'index': len(songs) - 1})


@quiz_bp.route('/<guild_id>/songs/<int:index>', methods=['PUT'])
@admin_required
def update_guild_song(guild_id, index):
    """서버별 곡 수정"""
    body = request.json
    if not body:
        return jsonify({'error': 'Request body required'}), 400

    data = load_quiz_data()
    songs = _get_guild_songs(data, guild_id)

    if index < 0 or index >= len(songs):
        return jsonify({'error': 'Invalid index'}), 404

    title = body.get('title', '').strip()
    artist = body.get('artist', '').strip()
    query = body.get('query', '').strip()
    aliases = body.get('aliases', [])

    if not title or not artist or not query:
        return jsonify({'error': 'title, artist, query are required'}), 400

    songs[index] = {
        'title': title,
        'artist': artist,
        'query': query,
    }
    if aliases:
        songs[index]['aliases'] = [a.strip() for a in aliases if a.strip()]
    title_aliases = body.get('title_aliases', [])
    if title_aliases:
        songs[index]['title_aliases'] = [a.strip() for a in title_aliases if a.strip()]

    save_quiz_data(data)
    return jsonify({'success': True, 'song': songs[index]})


@quiz_bp.route('/<guild_id>/songs/<int:index>', methods=['DELETE'])
@admin_required
def delete_guild_song(guild_id, index):
    """서버별 곡 삭제"""
    data = load_quiz_data()
    songs = _get_guild_songs(data, guild_id)

    if index < 0 or index >= len(songs):
        return jsonify({'error': 'Invalid index'}), 404

    removed = songs.pop(index)
    save_quiz_data(data)
    return jsonify({'success': True, 'removed': removed})


@quiz_bp.route('/<guild_id>/songs/reset', methods=['POST'])
@admin_required
def reset_guild_songs(guild_id):
    """서버 곡 목록을 글로벌 목록에서 다시 복사"""
    import copy
    data = load_quiz_data()
    global_songs = data.get('songs', [])

    guilds = data.setdefault('guilds', {})
    gd = guilds.setdefault(guild_id, {})
    gd['songs'] = copy.deepcopy(global_songs)
    save_quiz_data(data)
    return jsonify({'success': True, 'count': len(gd['songs'])})

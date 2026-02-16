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


# ---------- 곡 목록 관리 ----------

@quiz_bp.route('/songs')
@login_required
def get_songs():
    """곡 목록 조회"""
    data = load_quiz_data()
    songs = data.get('songs', [])

    # GCS에 곡이 없으면 기본 곡 목록 반환
    if not songs:
        songs = _get_default_songs()

    return jsonify({'songs': songs, 'count': len(songs)})


@quiz_bp.route('/songs', methods=['POST'])
@login_required
def add_song():
    """곡 추가"""
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
    songs = data.setdefault('songs', [])

    # 기본 목록으로 초기화 (비어있으면)
    if not songs:
        songs.extend(_get_default_songs())
        data['songs'] = songs

    song = {
        'title': title,
        'artist': artist,
        'query': query,
    }
    if aliases:
        song['aliases'] = [a.strip() for a in aliases if a.strip()]

    songs.append(song)
    save_quiz_data(data)

    return jsonify({'success': True, 'song': song, 'index': len(songs) - 1})


@quiz_bp.route('/songs/<int:index>', methods=['PUT'])
@login_required
def update_song(index):
    """곡 수정"""
    body = request.json
    if not body:
        return jsonify({'error': 'Request body required'}), 400

    data = load_quiz_data()
    songs = data.get('songs', [])

    if not songs:
        songs = _get_default_songs()
        data['songs'] = songs

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

    save_quiz_data(data)
    return jsonify({'success': True, 'song': songs[index]})


@quiz_bp.route('/songs/<int:index>', methods=['DELETE'])
@login_required
def delete_song(index):
    """곡 삭제"""
    data = load_quiz_data()
    songs = data.get('songs', [])

    if not songs:
        songs = _get_default_songs()
        data['songs'] = songs

    if index < 0 or index >= len(songs):
        return jsonify({'error': 'Invalid index'}), 404

    removed = songs.pop(index)
    save_quiz_data(data)
    return jsonify({'success': True, 'removed': removed})


@quiz_bp.route('/songs/reset', methods=['POST'])
@login_required
def reset_songs():
    """곡 목록을 기본값으로 초기화"""
    data = load_quiz_data()
    data['songs'] = _get_default_songs()
    save_quiz_data(data)
    return jsonify({'success': True, 'count': len(data['songs'])})


def _get_default_songs():
    """봇의 기본 곡 목록을 dict 리스트로 반환"""
    return [
        {"title": "Ditto", "artist": "NewJeans", "query": "NewJeans Ditto", "aliases": ["뉴진스"]},
        {"title": "Super Shy", "artist": "NewJeans", "query": "NewJeans Super Shy", "aliases": ["뉴진스", "슈퍼샤이"]},
        {"title": "Hype Boy", "artist": "NewJeans", "query": "NewJeans Hype Boy", "aliases": ["뉴진스", "하이프보이"]},
        {"title": "APT.", "artist": "ROSE", "query": "ROSE APT Bruno Mars", "aliases": ["로제", "브루노마스"]},
        {"title": "Supernova", "artist": "aespa", "query": "aespa Supernova", "aliases": ["에스파", "슈퍼노바"]},
        {"title": "Next Level", "artist": "aespa", "query": "aespa Next Level", "aliases": ["에스파", "넥스트레벨"]},
        {"title": "Love Dive", "artist": "IVE", "query": "IVE Love Dive", "aliases": ["아이브", "러브다이브"]},
        {"title": "HEYA", "artist": "IVE", "query": "IVE HEYA", "aliases": ["아이브", "해야"]},
        {"title": "Magnetic", "artist": "ILLIT", "query": "ILLIT Magnetic", "aliases": ["아일릿"]},
        {"title": "SPOT!", "artist": "ZICO", "query": "ZICO SPOT Jennie", "aliases": ["지코", "제니"]},
        {"title": "Butter", "artist": "BTS", "query": "BTS Butter", "aliases": ["방탄소년단", "방탄", "버터"]},
        {"title": "Dynamite", "artist": "BTS", "query": "BTS Dynamite", "aliases": ["방탄소년단", "방탄", "다이너마이트"]},
        {"title": "How Sweet", "artist": "NewJeans", "query": "NewJeans How Sweet", "aliases": ["뉴진스"]},
        {"title": "GODS", "artist": "NewJeans", "query": "NewJeans GODS", "aliases": ["뉴진스"]},
        {"title": "Drama", "artist": "aespa", "query": "aespa Drama", "aliases": ["에스파", "드라마"]},
        {"title": "Kitsch", "artist": "IVE", "query": "IVE Kitsch", "aliases": ["아이브", "키치"]},
        {"title": "Panorama", "artist": "IZ*ONE", "query": "IZ*ONE Panorama", "aliases": ["아이즈원", "파노라마"]},
        {"title": "Antifragile", "artist": "LE SSERAFIM", "query": "LE SSERAFIM Antifragile", "aliases": ["르세라핌"]},
        {"title": "EASY", "artist": "LE SSERAFIM", "query": "LE SSERAFIM EASY", "aliases": ["르세라핌"]},
        {"title": "Queencard", "artist": "(G)I-DLE", "query": "GIDLE Queencard", "aliases": ["여자아이들", "아이들", "퀸카"]},
        {"title": "TOMBOY", "artist": "(G)I-DLE", "query": "GIDLE TOMBOY", "aliases": ["여자아이들", "아이들", "톰보이"]},
        {"title": "Pink Venom", "artist": "BLACKPINK", "query": "BLACKPINK Pink Venom", "aliases": ["블랙핑크", "블핑"]},
        {"title": "Shut Down", "artist": "BLACKPINK", "query": "BLACKPINK Shut Down", "aliases": ["블랙핑크", "블핑"]},
        {"title": "OMG", "artist": "NewJeans", "query": "NewJeans OMG", "aliases": ["뉴진스"]},
        {"title": "Candy", "artist": "NCT DREAM", "query": "NCT DREAM Candy", "aliases": ["엔시티드림", "엔시티"]},
        {"title": "Idol", "artist": "YOASOBI", "query": "YOASOBI Idol Oshi no Ko", "aliases": ["요아소비", "아이돌"]},
        {"title": "Zankyosanka", "artist": "Aimer", "query": "Aimer 残響散歌 Demon Slayer", "aliases": ["에메", "잔향산가"]},
        {"title": "Shinunoga E-Wa", "artist": "Fujii Kaze", "query": "Fujii Kaze Shinunoga E-Wa", "aliases": ["후지이카제", "후지카제"]},
        {"title": "Kick Back", "artist": "Kenshi Yonezu", "query": "Kenshi Yonezu Kick Back Chainsaw Man", "aliases": ["요네즈켄시", "켄시요네즈", "요네즈 켄시"]},
        {"title": "Unravel", "artist": "TK from Ling tosite sigure", "query": "TK Unravel Tokyo Ghoul", "aliases": ["언라벨"]},
        {"title": "Gurenge", "artist": "LiSA", "query": "LiSA Gurenge Demon Slayer", "aliases": ["리사", "홍련화"]},
        {"title": "Pretender", "artist": "Official HIGE DANdism", "query": "Official HIGE DANdism Pretender", "aliases": ["히게단", "히게단디즘"]},
        {"title": "Cry Baby", "artist": "Official HIGE DANdism", "query": "Official HIGE DANdism Cry Baby", "aliases": ["히게단", "히게단디즘", "크라이베이비"]},
        {"title": "Racing into the Night", "artist": "YOASOBI", "query": "YOASOBI 夜に駆ける", "aliases": ["요아소비", "밤을달리다", "밤을 달리다", "요루니카게루"]},
        {"title": "Kaikai Kitan", "artist": "Eve", "query": "Eve Kaikai Kitan Jujutsu Kaisen", "aliases": ["이브", "괴괴기담"]},
        {"title": "Blinding Lights", "artist": "The Weeknd", "query": "The Weeknd Blinding Lights", "aliases": ["위켄드", "더위켄드"]},
        {"title": "Shape of You", "artist": "Ed Sheeran", "query": "Ed Sheeran Shape of You", "aliases": ["에드시런"]},
        {"title": "Levitating", "artist": "Dua Lipa", "query": "Dua Lipa Levitating", "aliases": ["두아리파"]},
        {"title": "Flowers", "artist": "Miley Cyrus", "query": "Miley Cyrus Flowers", "aliases": ["마일리사이러스"]},
        {"title": "Anti-Hero", "artist": "Taylor Swift", "query": "Taylor Swift Anti-Hero", "aliases": ["테일러스위프트"]},
        {"title": "As It Was", "artist": "Harry Styles", "query": "Harry Styles As It Was", "aliases": ["해리스타일스"]},
        {"title": "Cruel Summer", "artist": "Taylor Swift", "query": "Taylor Swift Cruel Summer", "aliases": ["테일러스위프트"]},
        {"title": "Die With A Smile", "artist": "Lady Gaga", "query": "Lady Gaga Bruno Mars Die With A Smile", "aliases": ["레이디가가", "브루노마스"]},
        {"title": "Espresso", "artist": "Sabrina Carpenter", "query": "Sabrina Carpenter Espresso", "aliases": ["사브리나카펜터"]},
        {"title": "Greedy", "artist": "Tate McRae", "query": "Tate McRae Greedy", "aliases": ["테이트맥레이"]},
    ]

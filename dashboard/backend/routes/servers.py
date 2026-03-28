"""
Server Management Routes
"""

import os
import json
import logging
import requests
from flask import Blueprint, jsonify, session, request
from functools import wraps
try:
    from dashboard_logger import log_action as log_dashboard_action
except ImportError:
    from dashboard.backend.dashboard_logger import log_action as log_dashboard_action

logger = logging.getLogger(__name__)

servers_bp = Blueprint('servers', __name__)

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_API_URL = 'https://discord.com/api/v10'

# GCS 설정
GCS_BUCKET = os.getenv('GCS_BUCKET_NAME', 'debi-marlene-settings')
GCS_KEY = 'settings.json'
gcs_client = None

def get_gcs_client():
    """GCS 클라이언트를 가져옵니다."""
    global gcs_client
    if gcs_client is None:
        try:
            from google.cloud import storage
            gcs_client = storage.Client(project=os.getenv('GCP_PROJECT_ID'))
        except Exception as e:
            logger.error(f'GCS 클라이언트 생성 실패: {e}')
            gcs_client = False
    return gcs_client if gcs_client != False else None

def load_gcs_settings():
    """GCS에서 설정을 로드합니다."""
    client = get_gcs_client()
    if client:
        try:
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_KEY)
            settings_data = blob.download_as_text()
            return json.loads(settings_data)
        except Exception as e:
            logger.error(f'GCS 설정 로드 실패: {e}')
    return {"guilds": {}, "users": {}, "global": {}}

def save_gcs_settings(settings):
    """GCS에 설정을 저장합니다."""
    client = get_gcs_client()
    if client:
        try:
            json_data = json.dumps(settings, indent=2, ensure_ascii=False)
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_KEY)
            blob.upload_from_string(json_data, content_type='application/json')
            return True
        except Exception as e:
            logger.error(f'GCS 설정 저장 실패: {e}')
    return False

def get_guild_features(guild_id):
    """서버의 대시보드 기능 설정을 가져옵니다."""
    settings = load_gcs_settings()
    guild_settings = settings.get('guilds', {}).get(str(guild_id), {})

    # 대시보드 기능 설정 (dashboard_features 키에 저장)
    features = guild_settings.get('dashboard_features', {})

    # 봇에서 설정한 값 가져오기
    announcement_channel_id = guild_settings.get('ANNOUNCEMENT_CHANNEL_ID')
    chat_channel_id = guild_settings.get('CHAT_CHANNEL_ID')
    tts_channel_id = guild_settings.get('tts_channel_id')
    tts_voice = guild_settings.get('tts_voice', 'edge_sunhi')

    # 기본값과 병합 (봇에서 설정한 채널이 있으면 enabled: True)
    default_features = {
        'announcement': {
            'enabled': bool(announcement_channel_id),
            'channelId': announcement_channel_id
        },
        'chatChannel': {
            'enabled': bool(chat_channel_id),
            'channelId': chat_channel_id
        },
        'welcome': {'enabled': False, 'channelId': None, 'message': '', 'imageEnabled': False},
        'goodbye': {'enabled': False, 'channelId': None, 'message': '', 'imageEnabled': False},
        'tts': {
            'enabled': bool(tts_channel_id),
            'channelId': tts_channel_id,
            'character': guild_settings.get('tts_voice', 'edge_sunhi'),
            'userVoices': guild_settings.get('user_voices', {})
        },
        'autoresponse': {'enabled': False, 'rules': []},
        'filter': {'enabled': False, 'action': 'delete', 'words': []},
        'moderation': {'enabled': False, 'warnThreshold': 3},
        'tickets': {'enabled': False, 'categoryId': None},
        'logs': {
            'enabled': False,
            'channelId': None,
            'events': {
                'memberJoin': True,
                'memberLeave': True,
                'messageDelete': True,
                'messageEdit': False,
                'roleChange': False,
                'channelChange': False,
                'ban': True,
                'kick': True,
                'warn': True
            }
        },
    }

    # 저장된 설정으로 기본값 덮어쓰기
    for key, default_value in default_features.items():
        if key in features:
            if isinstance(default_value, dict):
                default_features[key] = {**default_value, **features[key]}
            else:
                default_features[key] = features[key]

    return default_features

def save_guild_features(guild_id, features):
    """서버의 대시보드 기능 설정을 저장합니다."""
    settings = load_gcs_settings()
    guild_id_str = str(guild_id)

    if 'guilds' not in settings:
        settings['guilds'] = {}
    if guild_id_str not in settings['guilds']:
        settings['guilds'][guild_id_str] = {}

    # dashboard_features 키에 저장
    if 'dashboard_features' not in settings['guilds'][guild_id_str]:
        settings['guilds'][guild_id_str]['dashboard_features'] = {}

    # 기존 설정과 병합
    for key, value in features.items():
        settings['guilds'][guild_id_str]['dashboard_features'][key] = value

    # 봇 호환성: 봇이 사용하는 키에도 저장
    # 공지 채널
    if 'announcement' in features:
        if features['announcement'].get('channelId') and features['announcement'].get('enabled'):
            settings['guilds'][guild_id_str]['ANNOUNCEMENT_CHANNEL_ID'] = features['announcement']['channelId']
        elif not features['announcement'].get('enabled'):
            settings['guilds'][guild_id_str]['ANNOUNCEMENT_CHANNEL_ID'] = None

    # 채팅 채널 (봇 명령어 제한)
    if 'chatChannel' in features:
        if features['chatChannel'].get('channelId') and features['chatChannel'].get('enabled'):
            settings['guilds'][guild_id_str]['CHAT_CHANNEL_ID'] = int(features['chatChannel']['channelId'])
        else:
            settings['guilds'][guild_id_str].pop('CHAT_CHANNEL_ID', None)

    # TTS 채널
    if 'tts' in features:
        if features['tts'].get('channelId'):
            settings['guilds'][guild_id_str]['tts_channel_id'] = features['tts']['channelId']
        else:
            settings['guilds'][guild_id_str].pop('tts_channel_id', None)

    # TTS 서버 기본 목소리
    if 'tts' in features:
        if features['tts'].get('character'):
            settings['guilds'][guild_id_str]['tts_voice'] = features['tts']['character']
        # 유저별 목소리
        if 'userVoices' in features['tts']:
            settings['guilds'][guild_id_str]['user_voices'] = features['tts']['userVoices']

    return save_gcs_settings(settings)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin permission for the guild"""
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

def discord_bot_request(endpoint, method='GET', data=None):
    """Make a request to Discord API using bot token"""
    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
        'Content-Type': 'application/json',
    }

    url = f'{DISCORD_API_URL}{endpoint}'

    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    elif method == 'PATCH':
        response = requests.patch(url, headers=headers, json=data)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f'Unsupported method: {method}')

    return response

@servers_bp.route('/servers')
@login_required
def get_servers():
    """Get list of servers the user can manage"""
    user = session.get('user')
    admin_servers = user.get('admin_servers', [])
    access_token = user.get('access_token')

    # Get bot's guilds
    bot_response = discord_bot_request('/users/@me/guilds')
    bot_guilds = {}
    if bot_response.ok:
        bot_guilds = {g['id']: g for g in bot_response.json()}
    else:
        logger.error(f'Failed to get bot guilds: {bot_response.text}')

    # Get user's guilds with their info (with_counts=true for member count)
    user_guilds_response = requests.get(
        f'{DISCORD_API_URL}/users/@me/guilds?with_counts=true',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if not user_guilds_response.ok:
        logger.error(f'Failed to get user guilds: {user_guilds_response.text}')
        return jsonify({'servers': []})

    user_guilds = {g['id']: g for g in user_guilds_response.json()}

    # Include all admin servers (with or without bot)
    servers = []
    for guild_id in admin_servers:
        if guild_id in user_guilds:
            guild = user_guilds[guild_id]
            has_bot = guild_id in bot_guilds
            servers.append({
                'id': guild['id'],
                'name': guild['name'],
                'icon': guild.get('icon'),
                'memberCount': guild.get('approximate_member_count', 0),
                'isAdmin': True,
                'hasBot': has_bot,
            })

    return jsonify({
        'servers': servers,
        'botClientId': DISCORD_CLIENT_ID,
    })

@servers_bp.route('/servers/<guild_id>')
@admin_required
def get_server(guild_id):
    """Get server details and settings"""
    # Get guild info from Discord
    response = discord_bot_request(f'/guilds/{guild_id}')
    if not response.ok:
        return jsonify({'error': 'Server not found'}), 404

    guild = response.json()

    # GCS에서 설정 가져오기
    features = get_guild_features(guild_id)

    return jsonify({
        'id': guild['id'],
        'name': guild['name'],
        'icon': guild.get('icon'),
        'features': features,
    })

@servers_bp.route('/servers/<guild_id>/settings', methods=['PATCH'])
@admin_required
def update_server_settings(guild_id):
    """Update server settings"""
    data = request.json
    features = data.get('features', {})

    logger.info(f'Updating settings for guild {guild_id}: {features}')

    # GCS에 설정 저장
    success = save_guild_features(guild_id, features)

    if success:
        # 대시보드 액션 로그 기록
        user = session.get('user', {})
        log_dashboard_action(
            action_type='settings_update',
            user_id=user.get('id'),
            user_name=user.get('username'),
            guild_id=guild_id,
            details={'features': list(features.keys())}
        )
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to save settings'}), 500

@servers_bp.route('/servers/<guild_id>/channels')
@admin_required
def get_server_channels(guild_id):
    """Get server channels"""
    response = discord_bot_request(f'/guilds/{guild_id}/channels')
    if not response.ok:
        return jsonify({'error': 'Failed to get channels'}), 500

    channels = response.json()

    # Filter and format channels
    formatted = []
    for ch in channels:
        if ch['type'] in [0, 2, 4]:  # Text, Voice, Category
            formatted.append({
                'id': ch['id'],
                'name': ch['name'],
                'type': ch['type'],
                'parentId': ch.get('parent_id'),
                'position': ch.get('position', 0),
            })

    return jsonify({'channels': sorted(formatted, key=lambda x: x['position'])})

@servers_bp.route('/servers/<guild_id>/members')
@admin_required
def get_server_members(guild_id):
    """서버 멤버 목록 + 목소리 설정 조회"""
    # Discord API에서 멤버 가져오기 (최대 100명)
    response = discord_bot_request(f'/guilds/{guild_id}/members?limit=100')
    if not response.ok:
        return jsonify({'error': 'Failed to get members'}), 500

    members_data = response.json()

    # GCS에서 유저별 목소리 설정 가져오기
    settings = load_gcs_settings()
    guild_settings = settings.get('guilds', {}).get(str(guild_id), {})
    user_voices = guild_settings.get('user_voices', {})
    server_default = guild_settings.get('tts_voice', 'edge_sunhi')

    members = []
    for m in members_data:
        user = m.get('user', {})
        if user.get('bot'):
            continue
        user_id = user['id']
        members.append({
            'id': user_id,
            'username': user.get('username', ''),
            'displayName': m.get('nick') or user.get('global_name') or user.get('username', ''),
            'avatar': user.get('avatar'),
            'voice': user_voices.get(user_id, None),
        })

    return jsonify({
        'members': members,
        'serverDefault': server_default,
    })

@servers_bp.route('/servers/<guild_id>/members/<user_id>/voice', methods=['PATCH'])
@admin_required
def update_member_voice(guild_id, user_id):
    """유저 목소리 설정 변경"""
    data = request.json
    voice = data.get('voice')  # 'debi', 'marlene', 'alex', or None (server default)

    settings = load_gcs_settings()
    guild_id_str = str(guild_id)

    if 'guilds' not in settings:
        settings['guilds'] = {}
    if guild_id_str not in settings['guilds']:
        settings['guilds'][guild_id_str] = {}
    if 'user_voices' not in settings['guilds'][guild_id_str]:
        settings['guilds'][guild_id_str]['user_voices'] = {}

    if voice and voice in ['debi', 'marlene', 'alex']:
        settings['guilds'][guild_id_str]['user_voices'][user_id] = voice
    else:
        settings['guilds'][guild_id_str]['user_voices'].pop(user_id, None)

    if save_gcs_settings(settings):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to save'}), 500

@servers_bp.route('/servers/<guild_id>/roles')
@admin_required
def get_server_roles(guild_id):
    """Get server roles"""
    response = discord_bot_request(f'/guilds/{guild_id}/roles')
    if not response.ok:
        return jsonify({'error': 'Failed to get roles'}), 500

    roles = response.json()

    # Format roles
    formatted = []
    for role in roles:
        formatted.append({
            'id': role['id'],
            'name': role['name'],
            'color': role['color'],
            'position': role['position'],
            'permissions': role['permissions'],
        })

    return jsonify({'roles': sorted(formatted, key=lambda x: -x['position'])})

@servers_bp.route('/bot/stats')
def get_bot_stats():
    """Get bot statistics (public endpoint)"""
    # Get bot's guilds count (with_counts=true for member count)
    response = discord_bot_request('/users/@me/guilds?with_counts=true')
    servers = 0
    users = 0

    if response.ok:
        guilds = response.json()
        servers = len(guilds)

        # Get member count for each guild
        for guild in guilds:
            users += guild.get('approximate_member_count', 0)

    return jsonify({
        'stats': {
            'users': users,
            'servers': servers,
            'commands': 17,
        },
        'botClientId': DISCORD_CLIENT_ID,
    })


# ============== 임베드 전송 ==============
@servers_bp.route('/servers/<guild_id>/embed', methods=['POST'])
@admin_required
def send_embed(guild_id):
    """채널에 임베드 메시지 전송"""
    data = request.json
    channel_id = data.get('channelId')
    embed_data = data.get('embed', {})

    if not channel_id:
        return jsonify({'error': 'Channel ID required'}), 400

    # Discord embed 형식으로 변환
    embed = {}
    if embed_data.get('title'):
        embed['title'] = embed_data['title']
    if embed_data.get('description'):
        embed['description'] = embed_data['description']
    if embed_data.get('color'):
        # hex to int
        color = embed_data['color'].lstrip('#')
        embed['color'] = int(color, 16)
    if embed_data.get('footer'):
        embed['footer'] = {'text': embed_data['footer']}
    if embed_data.get('thumbnail'):
        embed['thumbnail'] = {'url': embed_data['thumbnail']}
    if embed_data.get('image'):
        embed['image'] = {'url': embed_data['image']}
    if embed_data.get('author', {}).get('name'):
        embed['author'] = {
            'name': embed_data['author']['name'],
            'icon_url': embed_data['author'].get('iconUrl')
        }
    if embed_data.get('fields'):
        embed['fields'] = [
            {'name': f['name'], 'value': f['value'], 'inline': f.get('inline', False)}
            for f in embed_data['fields'] if f.get('name') and f.get('value')
        ]

    # Discord API로 메시지 전송
    response = discord_bot_request(
        f'/channels/{channel_id}/messages',
        method='POST',
        data={'embeds': [embed]}
    )

    if response.ok:
        return jsonify({'success': True, 'messageId': response.json().get('id')})
    else:
        logger.error(f'Failed to send embed: {response.text}')
        return jsonify({'error': 'Failed to send embed'}), 500


# ============== 투표 ==============
@servers_bp.route('/servers/<guild_id>/poll', methods=['POST'])
@admin_required
def create_poll(guild_id):
    """투표 생성"""
    data = request.json
    channel_id = data.get('channelId')
    question = data.get('question')
    options = data.get('options', [])
    duration = data.get('duration', 24)  # hours
    multiple = data.get('multiple', False)

    if not channel_id or not question or len(options) < 2:
        return jsonify({'error': 'Invalid poll data'}), 400

    # 숫자 이모지
    number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    # 옵션 텍스트 생성
    options_text = '\n'.join([
        f'{number_emojis[i]} {opt}' for i, opt in enumerate(options[:10])
    ])

    embed = {
        'title': f'📊 {question}',
        'description': options_text,
        'color': 0x5865F2,
        'footer': {
            'text': f'{"복수 선택 가능 | " if multiple else ""}{duration}시간 후 종료'
        }
    }

    # 메시지 전송
    response = discord_bot_request(
        f'/channels/{channel_id}/messages',
        method='POST',
        data={'embeds': [embed]}
    )

    if not response.ok:
        logger.error(f'Failed to create poll: {response.text}')
        return jsonify({'error': 'Failed to create poll'}), 500

    message_id = response.json().get('id')

    # 리액션 추가
    for i in range(len(options[:10])):
        emoji = number_emojis[i]
        discord_bot_request(
            f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me',
            method='PUT'
        )

    return jsonify({'success': True, 'messageId': message_id})


# ============== 경품추첨 ==============
@servers_bp.route('/servers/<guild_id>/giveaway', methods=['POST'])
@admin_required
def create_giveaway(guild_id):
    """경품추첨 생성"""
    import time

    data = request.json
    channel_id = data.get('channelId')
    prize = data.get('prize')
    winners = data.get('winners', 1)
    duration = data.get('duration', 24)  # hours

    if not channel_id or not prize:
        return jsonify({'error': 'Invalid giveaway data'}), 400

    end_time = int(time.time()) + (duration * 3600)

    embed = {
        'title': '🎉 경품추첨',
        'description': f'**{prize}**\n\n🎁 당첨자 수: {winners}명\n⏰ 종료: <t:{end_time}:R>\n\n참여하려면 아래 🎉 반응을 클릭하세요!',
        'color': 0xFF6B6B,
        'footer': {
            'text': f'{duration}시간 후 자동 추첨'
        }
    }

    # 메시지 전송
    response = discord_bot_request(
        f'/channels/{channel_id}/messages',
        method='POST',
        data={'embeds': [embed]}
    )

    if not response.ok:
        logger.error(f'Failed to create giveaway: {response.text}')
        return jsonify({'error': 'Failed to create giveaway'}), 500

    message_id = response.json().get('id')

    # 🎉 리액션 추가
    discord_bot_request(
        f'/channels/{channel_id}/messages/{message_id}/reactions/🎉/@me',
        method='PUT'
    )

    # GCS에 경품추첨 정보 저장 (나중에 봇이 추첨할 때 사용)
    settings = load_gcs_settings()
    guild_id_str = str(guild_id)
    if 'guilds' not in settings:
        settings['guilds'] = {}
    if guild_id_str not in settings['guilds']:
        settings['guilds'][guild_id_str] = {}
    if 'giveaways' not in settings['guilds'][guild_id_str]:
        settings['guilds'][guild_id_str]['giveaways'] = []

    settings['guilds'][guild_id_str]['giveaways'].append({
        'messageId': message_id,
        'channelId': channel_id,
        'prize': prize,
        'winners': winners,
        'endTime': end_time,
        'ended': False
    })
    save_gcs_settings(settings)

    return jsonify({'success': True, 'messageId': message_id})


# ============== 고정 메시지 ==============
@servers_bp.route('/servers/<guild_id>/sticky', methods=['GET'])
@admin_required
def get_sticky_messages(guild_id):
    """고정 메시지 목록 조회"""
    settings = load_gcs_settings()
    guild_settings = settings.get('guilds', {}).get(str(guild_id), {})
    sticky_messages = guild_settings.get('sticky_messages', [])

    return jsonify({'stickyMessages': sticky_messages})


@servers_bp.route('/servers/<guild_id>/sticky', methods=['POST'])
@admin_required
def create_sticky_message(guild_id):
    """고정 메시지 생성"""
    import uuid

    data = request.json
    channel_id = data.get('channelId')
    content = data.get('content')

    if not channel_id or not content:
        return jsonify({'error': 'Channel ID and content required'}), 400

    # 채널 이름 가져오기
    channel_response = discord_bot_request(f'/channels/{channel_id}')
    channel_name = 'unknown'
    if channel_response.ok:
        channel_name = channel_response.json().get('name', 'unknown')

    sticky_id = str(uuid.uuid4())[:8]

    # GCS에 저장
    settings = load_gcs_settings()
    guild_id_str = str(guild_id)
    if 'guilds' not in settings:
        settings['guilds'] = {}
    if guild_id_str not in settings['guilds']:
        settings['guilds'][guild_id_str] = {}
    if 'sticky_messages' not in settings['guilds'][guild_id_str]:
        settings['guilds'][guild_id_str]['sticky_messages'] = []

    settings['guilds'][guild_id_str]['sticky_messages'].append({
        'id': sticky_id,
        'channelId': channel_id,
        'channelName': channel_name,
        'content': content,
        'enabled': True,
        'lastMessageId': None
    })

    if save_gcs_settings(settings):
        # 즉시 메시지 전송
        response = discord_bot_request(
            f'/channels/{channel_id}/messages',
            method='POST',
            data={'content': content}
        )
        if response.ok:
            # lastMessageId 업데이트
            message_id = response.json().get('id')
            for sm in settings['guilds'][guild_id_str]['sticky_messages']:
                if sm['id'] == sticky_id:
                    sm['lastMessageId'] = message_id
                    break
            save_gcs_settings(settings)

        return jsonify({'success': True, 'id': sticky_id})
    else:
        return jsonify({'error': 'Failed to save'}), 500


@servers_bp.route('/servers/<guild_id>/sticky/<sticky_id>', methods=['PATCH'])
@admin_required
def update_sticky_message(guild_id, sticky_id):
    """고정 메시지 수정"""
    data = request.json

    settings = load_gcs_settings()
    guild_id_str = str(guild_id)
    sticky_messages = settings.get('guilds', {}).get(guild_id_str, {}).get('sticky_messages', [])

    for sm in sticky_messages:
        if sm['id'] == sticky_id:
            if 'enabled' in data:
                sm['enabled'] = data['enabled']
            if 'content' in data:
                sm['content'] = data['content']
            break

    if save_gcs_settings(settings):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to save'}), 500


@servers_bp.route('/servers/<guild_id>/sticky/<sticky_id>', methods=['DELETE'])
@admin_required
def delete_sticky_message(guild_id, sticky_id):
    """고정 메시지 삭제"""
    settings = load_gcs_settings()
    guild_id_str = str(guild_id)

    if guild_id_str in settings.get('guilds', {}):
        sticky_messages = settings['guilds'][guild_id_str].get('sticky_messages', [])
        settings['guilds'][guild_id_str]['sticky_messages'] = [
            sm for sm in sticky_messages if sm['id'] != sticky_id
        ]

        if save_gcs_settings(settings):
            return jsonify({'success': True})

    return jsonify({'error': 'Failed to delete'}), 500


# ============== 환영/작별 이미지 ==============
@servers_bp.route('/servers/<guild_id>/welcome-image', methods=['POST'])
@admin_required
def upload_welcome_image(guild_id):
    """환영/작별 배경 이미지 업로드"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400

    file = request.files['image']
    image_type = request.form.get('type', 'welcome')  # welcome or goodbye

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 파일 크기 체크 (3MB)
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)

    if size > 3 * 1024 * 1024:
        return jsonify({'error': 'File too large (max 3MB)'}), 400

    # 확장자 체크
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return jsonify({'error': 'Invalid file type (png, jpg, jpeg only)'}), 400

    try:
        client = get_gcs_client()
        if not client:
            return jsonify({'error': 'Storage not available'}), 500

        bucket = client.bucket(GCS_BUCKET)
        blob_name = f'welcome_images/{guild_id}_{image_type}_bg.png'
        blob = bucket.blob(blob_name)

        # 이미지 저장
        blob.upload_from_file(file, content_type='image/png')

        # 공개 URL 생성
        image_url = f'https://storage.googleapis.com/{GCS_BUCKET}/{blob_name}'

        return jsonify({'success': True, 'url': image_url})

    except Exception as e:
        logger.error(f'이미지 업로드 실패: {e}')
        return jsonify({'error': 'Upload failed'}), 500


@servers_bp.route('/servers/<guild_id>/welcome-image', methods=['DELETE'])
@admin_required
def delete_welcome_image(guild_id):
    """환영/작별 배경 이미지 삭제"""
    image_type = request.args.get('type', 'welcome')

    try:
        client = get_gcs_client()
        if not client:
            return jsonify({'error': 'Storage not available'}), 500

        bucket = client.bucket(GCS_BUCKET)
        blob_name = f'welcome_images/{guild_id}_{image_type}_bg.png'
        blob = bucket.blob(blob_name)

        if blob.exists():
            blob.delete()

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f'이미지 삭제 실패: {e}')
        return jsonify({'error': 'Delete failed'}), 500


@servers_bp.route('/servers/<guild_id>/welcome-image-config', methods=['PATCH'])
@admin_required
def update_welcome_image_config(guild_id):
    """환영/작별 이미지 설정 업데이트 (위치, 크기, 색상 등)"""
    data = request.json
    image_type = data.get('type', 'welcome')
    config = data.get('config', {})

    settings = load_gcs_settings()
    guild_id_str = str(guild_id)

    if 'guilds' not in settings:
        settings['guilds'] = {}
    if guild_id_str not in settings['guilds']:
        settings['guilds'][guild_id_str] = {}
    if 'dashboard_features' not in settings['guilds'][guild_id_str]:
        settings['guilds'][guild_id_str]['dashboard_features'] = {}

    config_key = f'{image_type}_image_config'
    settings['guilds'][guild_id_str]['dashboard_features'][config_key] = config

    if save_gcs_settings(settings):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to save'}), 500


# ============== 환영 메시지 테스트 전송 ==============
@servers_bp.route('/servers/<guild_id>/welcome-test', methods=['POST'])
@admin_required
def send_welcome_test(guild_id):
    """환영 메시지 테스트 전송 (프론트엔드에서 캡쳐한 이미지를 Discord로 전송)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No image file'}), 400

    file = request.files['file']
    channel_id = request.form.get('channelId')

    if not channel_id:
        return jsonify({'error': 'Channel ID required'}), 400

    try:
        import requests as req

        headers = {
            'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
        }
        url = f'{DISCORD_API_URL}/channels/{channel_id}/messages'

        files = {
            'file': ('welcome.png', file.stream, 'image/png')
        }
        payload = {
            'content': '[테스트] 환영 메시지 미리보기'
        }

        response = req.post(url, headers=headers, data=payload, files=files)

        if response.ok:
            return jsonify({'success': True, 'messageId': response.json().get('id')})
        else:
            logger.error(f'테스트 전송 실패: {response.text}')
            return jsonify({'error': 'Failed to send'}), 500

    except Exception as e:
        logger.error(f'테스트 전송 실패: {e}')
        return jsonify({'error': str(e)}), 500


@servers_bp.route('/servers/<guild_id>/welcome-preview', methods=['POST'])
@admin_required
def preview_welcome_image(guild_id):
    """환영 이미지 미리보기 생성"""
    import sys
    import os

    # 봇 모듈 경로 추가
    for p in ['/app', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))]:
        if p not in sys.path:
            sys.path.insert(0, p)

    try:
        import asyncio
        from run.services.welcome import WelcomeImageGenerator

        data = request.json
        config = data.get('config', {})
        is_welcome = data.get('type', 'welcome') == 'welcome'

        # 배경 이미지 가져오기
        background = None
        try:
            client = get_gcs_client()
            if client:
                bucket = client.bucket(GCS_BUCKET)
                image_type = 'welcome' if is_welcome else 'goodbye'
                blob_name = f'welcome_images/{guild_id}_{image_type}_bg.png'
                blob = bucket.blob(blob_name)
                if blob.exists():
                    background = blob.download_as_bytes()
        except Exception as e:
            logger.warning(f'배경 이미지 로드 실패: {e}')

        # 이미지 생성
        generator = WelcomeImageGenerator()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            image_bytes = loop.run_until_complete(generator.generate(
                user_name='예시 유저',
                user_avatar_url='https://cdn.discordapp.com/embed/avatars/0.png',
                server_name='예시 서버',
                member_count=100,
                is_welcome=is_welcome,
                config=config,
                background_image=background,
            ))
        finally:
            loop.close()

        import base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{image_base64}'
        })

    except Exception as e:
        logger.error(f'미리보기 생성 실패: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============== 서버 통계 ==============
@servers_bp.route('/servers/<guild_id>/stats')
@admin_required
def get_server_stats(guild_id):
    """서버 통계 조회"""
    settings = load_gcs_settings()
    guild_settings = settings.get('guilds', {}).get(str(guild_id), {})
    stats = guild_settings.get('stats', {
        'daily': {},
        'members': {},
        'logs': []
    })

    # 일별 통계를 날짜순으로 정렬
    daily_sorted = sorted(stats.get('daily', {}).items())

    # 멤버 통계 (상위 20명)
    members = stats.get('members', {})
    top_members = sorted(
        [{'id': k, **v} for k, v in members.items()],
        key=lambda x: x.get('messages', 0),
        reverse=True
    )[:20]

    return jsonify({
        'daily': [{'date': k, **v} for k, v in daily_sorted],
        'topMembers': top_members,
        'logs': stats.get('logs', [])[-100:]  # 최근 100개
    })


@servers_bp.route('/servers/<guild_id>/stats/logs')
@admin_required
def get_server_logs(guild_id):
    """서버 활동 로그 조회"""
    settings = load_gcs_settings()
    guild_settings = settings.get('guilds', {}).get(str(guild_id), {})
    stats = guild_settings.get('stats', {})

    log_type = request.args.get('type')  # join, leave, role_add, role_remove, message_delete, message_edit
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 100))

    logs = stats.get('logs', [])

    # 필터링
    if log_type:
        logs = [l for l in logs if l.get('type') == log_type]
    if user_id:
        logs = [l for l in logs if l.get('user_id') == user_id]

    # 최신순 정렬
    logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]

    return jsonify({'logs': logs})


@servers_bp.route('/servers/<guild_id>/stats/member/<user_id>')
@admin_required
def get_member_stats(guild_id, user_id):
    """특정 멤버 통계 조회"""
    settings = load_gcs_settings()
    guild_settings = settings.get('guilds', {}).get(str(guild_id), {})
    stats = guild_settings.get('stats', {})

    # 멤버 정보
    member_stats = stats.get('members', {}).get(user_id, {'messages': 0, 'name': ''})

    # 해당 멤버의 로그
    logs = [l for l in stats.get('logs', []) if l.get('user_id') == user_id]
    logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:50]

    return jsonify({
        'member': member_stats,
        'logs': logs
    })


# ============== 온보딩 ==============
@servers_bp.route('/servers/<guild_id>/onboarding')
@admin_required
def get_onboarding(guild_id):
    """서버 온보딩 설정 조회"""
    # Discord API로 온보딩 설정 가져오기
    response = discord_bot_request(f'/guilds/{guild_id}/onboarding')

    if response.ok:
        onboarding = response.json()
        return jsonify({
            'enabled': onboarding.get('enabled', False),
            'mode': onboarding.get('mode', 0),  # 0=DEFAULT, 1=ADVANCED
            'prompts': onboarding.get('prompts', []),
            'defaultChannelIds': onboarding.get('default_channel_ids', []),
        })
    elif response.status_code == 404:
        # 온보딩이 설정되지 않은 서버
        return jsonify({
            'enabled': False,
            'mode': 0,
            'prompts': [],
            'defaultChannelIds': [],
        })
    else:
        logger.error(f'온보딩 조회 실패: {response.text}')
        return jsonify({'error': 'Failed to get onboarding'}), 500


@servers_bp.route('/servers/<guild_id>/onboarding', methods=['PUT'])
@admin_required
def update_onboarding(guild_id):
    """서버 온보딩 설정 수정"""
    data = request.json

    # Discord API 형식으로 변환
    payload = {
        'enabled': data.get('enabled', False),
        'mode': data.get('mode', 0),
        'prompts': data.get('prompts', []),
        'default_channel_ids': data.get('defaultChannelIds', []),
    }

    response = discord_bot_request(
        f'/guilds/{guild_id}/onboarding',
        method='PUT',
        data=payload
    )

    if response.ok:
        return jsonify({'success': True})
    else:
        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
        logger.error(f'온보딩 수정 실패: {response.text}')
        return jsonify({
            'error': error_data.get('message', 'Failed to update onboarding'),
            'code': error_data.get('code')
        }), response.status_code


@servers_bp.route('/servers/<guild_id>/onboarding/prompts', methods=['POST'])
@admin_required
def add_onboarding_prompt(guild_id):
    """온보딩 프롬프트(질문) 추가"""
    data = request.json

    # 현재 온보딩 설정 가져오기
    response = discord_bot_request(f'/guilds/{guild_id}/onboarding')
    if not response.ok:
        return jsonify({'error': 'Failed to get current onboarding'}), 500

    onboarding = response.json()
    prompts = onboarding.get('prompts', [])

    # 새 프롬프트 추가
    new_prompt = {
        'type': data.get('type', 0),  # 0=MULTIPLE_CHOICE, 1=DROPDOWN
        'title': data.get('title', ''),
        'single_select': data.get('singleSelect', True),
        'required': data.get('required', True),
        'in_onboarding': True,
        'options': data.get('options', [])
    }
    prompts.append(new_prompt)

    # 업데이트
    payload = {
        'enabled': onboarding.get('enabled', False),
        'mode': onboarding.get('mode', 0),
        'prompts': prompts,
        'default_channel_ids': onboarding.get('default_channel_ids', []),
    }

    update_response = discord_bot_request(
        f'/guilds/{guild_id}/onboarding',
        method='PUT',
        data=payload
    )

    if update_response.ok:
        return jsonify({'success': True})
    else:
        logger.error(f'프롬프트 추가 실패: {update_response.text}')
        return jsonify({'error': 'Failed to add prompt'}), 500


@servers_bp.route('/servers/<guild_id>/onboarding/prompts/<prompt_id>', methods=['DELETE'])
@admin_required
def delete_onboarding_prompt(guild_id, prompt_id):
    """온보딩 프롬프트(질문) 삭제"""
    # 현재 온보딩 설정 가져오기
    response = discord_bot_request(f'/guilds/{guild_id}/onboarding')
    if not response.ok:
        return jsonify({'error': 'Failed to get current onboarding'}), 500

    onboarding = response.json()
    prompts = onboarding.get('prompts', [])

    # 해당 프롬프트 제거
    prompts = [p for p in prompts if str(p.get('id')) != str(prompt_id)]

    # 업데이트
    payload = {
        'enabled': onboarding.get('enabled', False),
        'mode': onboarding.get('mode', 0),
        'prompts': prompts,
        'default_channel_ids': onboarding.get('default_channel_ids', []),
    }

    update_response = discord_bot_request(
        f'/guilds/{guild_id}/onboarding',
        method='PUT',
        data=payload
    )

    if update_response.ok:
        return jsonify({'success': True})
    else:
        logger.error(f'프롬프트 삭제 실패: {update_response.text}')
        return jsonify({'error': 'Failed to delete prompt'}), 500


# ============== 채널 청소 ==============
@servers_bp.route('/servers/<guild_id>/channels/<channel_id>/purge', methods=['POST'])
@admin_required
def purge_channel(guild_id, channel_id):
    """채널의 메시지를 일괄 삭제합니다 (14일 이내 메시지만, 최대 500개씩)"""
    import time as time_module
    from datetime import datetime, timezone, timedelta

    max_count = request.json.get('count', 100)  # 기본 100개
    if max_count > 1000:
        max_count = 1000

    deleted_total = 0
    fourteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)

    try:
        while deleted_total < max_count:
            # 메시지 가져오기 (최대 100개)
            fetch_count = min(100, max_count - deleted_total)
            response = discord_bot_request(
                f'/channels/{channel_id}/messages?limit={fetch_count}'
            )
            if not response.ok:
                break

            messages = response.json()
            if not messages:
                break

            # 14일 이내 메시지만 필터링
            valid_ids = []
            for msg in messages:
                msg_time = datetime.fromisoformat(msg['timestamp'].replace('+00:00', '+00:00'))
                if msg_time.tzinfo is None:
                    msg_time = msg_time.replace(tzinfo=timezone.utc)
                if msg_time > fourteen_days_ago:
                    valid_ids.append(msg['id'])

            if not valid_ids:
                break

            if len(valid_ids) == 1:
                # 1개면 개별 삭제
                discord_bot_request(
                    f'/channels/{channel_id}/messages/{valid_ids[0]}',
                    method='DELETE'
                )
                deleted_total += 1
            else:
                # 2개 이상이면 bulk-delete
                resp = discord_bot_request(
                    f'/channels/{channel_id}/messages/bulk-delete',
                    method='POST',
                    data={'messages': valid_ids}
                )
                if not resp.ok:
                    logger.error(f'bulk-delete 실패: {resp.status_code} {resp.text}')
                    break
                deleted_total += len(valid_ids)

            # 레이트 리밋 대응
            time_module.sleep(1)

        return jsonify({
            'deleted': deleted_total,
            'message': f'{deleted_total}개 메시지 삭제 완료'
        })

    except Exception as e:
        logger.error(f'채널 청소 오류: {e}')
        return jsonify({
            'error': str(e),
            'deleted': deleted_total
        }), 500


# ============== 알림 설정 ==============


@servers_bp.route('/servers/<guild_id>/notifications')
@admin_required
def get_notification_settings(guild_id):
    """알림 설정 조회"""
    settings = load_gcs_settings()
    guild_settings = settings.get('guilds', {}).get(str(guild_id), {})
    notification_settings = guild_settings.get('notification_settings', {})

    patch_note = notification_settings.get('patchNote', {
        'enabled': False,
        'channelId': None,
    })

    coupon_config = notification_settings.get('coupon', {
        'enabled': False,
        'channelId': None,
    })

    return jsonify({
        'patchNote': patch_note,
        'coupon': coupon_config,
    })


@servers_bp.route('/servers/<guild_id>/notifications/patchnote', methods=['POST'])
@admin_required
def update_patchnote_notification(guild_id):
    """패치노트 알림 채널 설정"""
    data = request.json
    channel_id = data.get('channelId')
    enabled = data.get('enabled', False)

    if enabled and not channel_id:
        return jsonify({'error': 'channelId is required when enabling'}), 400

    settings = load_gcs_settings()
    guild_id_str = str(guild_id)

    if 'guilds' not in settings:
        settings['guilds'] = {}
    if guild_id_str not in settings['guilds']:
        settings['guilds'][guild_id_str] = {}
    if 'notification_settings' not in settings['guilds'][guild_id_str]:
        settings['guilds'][guild_id_str]['notification_settings'] = {}

    settings['guilds'][guild_id_str]['notification_settings']['patchNote'] = {
        'enabled': enabled,
        'channelId': channel_id if enabled else None,
    }

    if save_gcs_settings(settings):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to save settings'}), 500


@servers_bp.route('/servers/<guild_id>/notifications/coupon', methods=['POST'])
@admin_required
def update_coupon_notification(guild_id):
    """쿠폰 알림 채널 설정"""
    data = request.json
    channel_id = data.get('channelId')
    enabled = data.get('enabled', False)

    settings = load_gcs_settings()
    guild_id_str = str(guild_id)

    if 'guilds' not in settings:
        settings['guilds'] = {}
    if guild_id_str not in settings['guilds']:
        settings['guilds'][guild_id_str] = {}
    if 'notification_settings' not in settings['guilds'][guild_id_str]:
        settings['guilds'][guild_id_str]['notification_settings'] = {}

    settings['guilds'][guild_id_str]['notification_settings']['coupon'] = {
        'enabled': enabled,
        'channelId': channel_id if enabled else None,
    }

    if save_gcs_settings(settings):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to save settings'}), 500


@servers_bp.route('/servers/<guild_id>/community-check')
@admin_required
def check_community_status(guild_id):
    """서버의 커뮤니티 기능 활성화 여부 확인"""
    response = discord_bot_request(f'/guilds/{guild_id}')
    if not response.ok:
        return jsonify({'error': 'Failed to get guild info'}), 500

    guild = response.json()
    features = guild.get('features', [])

    return jsonify({
        'isCommunity': 'COMMUNITY' in features,
        'features': features
    })

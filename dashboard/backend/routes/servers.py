"""
Server Management Routes
"""

import os
import json
import logging
import requests
from flask import Blueprint, jsonify, session, request
from functools import wraps

logger = logging.getLogger(__name__)

servers_bp = Blueprint('servers', __name__)

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_API_URL = 'https://discord.com/api/v10'

# GCS 설정
GCS_BUCKET = 'debi-marlene-settings'
GCS_KEY = 'settings.json'
gcs_client = None

def get_gcs_client():
    """GCS 클라이언트를 가져옵니다."""
    global gcs_client
    if gcs_client is None:
        try:
            from google.cloud import storage
            gcs_client = storage.Client(project='ironic-objectivist-465713-a6')
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

    # 기본값과 병합
    default_features = {
        'announcement': {'enabled': False, 'channelId': guild_settings.get('ANNOUNCEMENT_CHANNEL_ID')},
        'welcome': {'enabled': False, 'channelId': None, 'message': '', 'imageEnabled': False},
        'goodbye': {'enabled': False, 'channelId': None, 'message': '', 'imageEnabled': False},
        'tts': {'enabled': False, 'channelId': None, 'character': 'debi'},
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

    # 공지 채널은 기존 형식으로도 저장 (봇 호환성)
    if 'announcement' in features and features['announcement'].get('channelId'):
        settings['guilds'][guild_id_str]['ANNOUNCEMENT_CHANNEL_ID'] = features['announcement']['channelId']

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

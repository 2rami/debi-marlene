"""
Server Management Routes
"""

import os
import logging
import requests
from flask import Blueprint, jsonify, session, request
from functools import wraps

logger = logging.getLogger(__name__)

servers_bp = Blueprint('servers', __name__)

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_API_URL = 'https://discord.com/api/v10'

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

    # Get bot's guilds
    response = discord_bot_request('/users/@me/guilds')
    if not response.ok:
        logger.error(f'Failed to get bot guilds: {response.text}')
        return jsonify({'servers': []})

    bot_guilds = {g['id']: g for g in response.json()}

    # Filter to only guilds where user is admin and bot is present
    servers = []
    for guild_id in admin_servers:
        if guild_id in bot_guilds:
            guild = bot_guilds[guild_id]
            servers.append({
                'id': guild['id'],
                'name': guild['name'],
                'icon': guild.get('icon'),
                'memberCount': guild.get('approximate_member_count', 0),
                'isAdmin': True,
            })

    return jsonify({'servers': servers})

@servers_bp.route('/servers/<guild_id>')
@admin_required
def get_server(guild_id):
    """Get server details and settings"""
    # Get guild info from Discord
    response = discord_bot_request(f'/guilds/{guild_id}')
    if not response.ok:
        return jsonify({'error': 'Server not found'}), 404

    guild = response.json()

    # TODO: Get settings from Firestore
    features = {
        'announcement': {'enabled': False, 'channelId': None},
        'welcome': {'enabled': False, 'channelId': None, 'message': ''},
        'tts': {'enabled': False, 'channelId': None, 'character': 'debi'},
        'autoresponse': {'enabled': False},
        'filter': {'enabled': False, 'action': 'delete'},
        'moderation': {'enabled': False, 'warnThreshold': 3},
        'tickets': {'enabled': False, 'categoryId': None},
    }

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

    # TODO: Save settings to Firestore
    logger.info(f'Updating settings for guild {guild_id}: {data}')

    return jsonify({'success': True})

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

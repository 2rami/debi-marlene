"""
Discord OAuth2 Authentication Routes
"""

import os
import logging
import requests
from flask import Blueprint, redirect, request, session, jsonify, url_for

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

# Discord OAuth2 configuration
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:3002/api/auth/callback')
DISCORD_API_URL = 'https://discord.com/api/v10'
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3002')

@auth_bp.route('/discord')
def discord_login():
    """Redirect to Discord OAuth2 authorization page"""
    scope = 'identify email guilds'

    auth_url = (
        f'https://discord.com/api/oauth2/authorize'
        f'?client_id={DISCORD_CLIENT_ID}'
        f'&redirect_uri={DISCORD_REDIRECT_URI}'
        f'&response_type=code'
        f'&scope={scope}'
    )

    return redirect(auth_url)

@auth_bp.route('/callback')
def discord_callback():
    """Handle Discord OAuth2 callback"""
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        logger.error(f'Discord OAuth error: {error}')
        return redirect(f'{FRONTEND_URL}/?error=oauth_failed')

    if not code:
        return redirect(f'{FRONTEND_URL}/?error=no_code')

    try:
        # Exchange code for tokens
        token_response = requests.post(
            f'{DISCORD_API_URL}/oauth2/token',
            data={
                'client_id': DISCORD_CLIENT_ID,
                'client_secret': DISCORD_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': DISCORD_REDIRECT_URI,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        token_response.raise_for_status()
        tokens = token_response.json()

        access_token = tokens['access_token']

        # Get user info
        user_response = requests.get(
            f'{DISCORD_API_URL}/users/@me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_response.raise_for_status()
        user_data = user_response.json()

        # Get user's guilds
        guilds_response = requests.get(
            f'{DISCORD_API_URL}/users/@me/guilds',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        guilds_response.raise_for_status()
        guilds_data = guilds_response.json()

        # Filter guilds where user has admin permission
        admin_guilds = [
            g['id'] for g in guilds_data
            if (int(g.get('permissions', 0)) & 0x8) == 0x8  # ADMINISTRATOR permission
        ]

        # Store in session
        session['user'] = {
            'id': user_data['id'],
            'username': user_data['username'],
            'avatar': user_data.get('avatar'),
            'email': user_data.get('email'),
            'access_token': access_token,
            'admin_servers': admin_guilds,
        }

        logger.info(f'User {user_data["username"]} logged in')
        return redirect(f'{FRONTEND_URL}/dashboard')

    except requests.RequestException as e:
        logger.error(f'Discord OAuth request failed: {e}')
        return redirect(f'{FRONTEND_URL}/?error=oauth_failed')

@auth_bp.route('/me')
def get_current_user():
    """Get current logged in user"""
    user = session.get('user')

    if not user:
        return jsonify({'user': None}), 200

    # TODO: Get premium status from Firestore
    premium_status = {
        'isActive': False,
        'plan': None,
        'expiresAt': None,
    }

    return jsonify({
        'user': {
            'id': user['id'],
            'username': user['username'],
            'avatar': user['avatar'],
            'email': user.get('email'),
            'premium': premium_status,
            'adminServers': user.get('admin_servers', []),
        }
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout current user"""
    session.pop('user', None)
    return jsonify({'success': True})

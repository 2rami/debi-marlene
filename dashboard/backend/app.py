"""
Debi Marlene Dashboard Backend
Flask API server for Discord bot dashboard
"""

import os
import logging
from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables BEFORE importing routes
# (routes read os.getenv at module level)
load_dotenv()

from routes.auth import auth_bp
from routes.servers import servers_bp
from routes.quiz import quiz_bp
from routes.me import me_bp
from routes.portfolio import portfolio_bp
from routes.credits import credits_bp
from routes.credits_topup import credits_topup_bp
from routes.blocked_users import blocked_bp
from routes.og_key import og_key_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'debi-marlene-dashboard-secret-key')

# nginx/Cloudflare 뒤에서 실제 스킴/호스트(X-Forwarded-*)를 신뢰하도록.
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Session configuration
# SameSite=Lax: SPA 와 /api 가 동일 출처(nginx 프록시)이고, OAuth 콜백은 top-level 리다이렉트라
#               쿠키 세팅/재전송 모두 커버됨.
# Secure: 프로덕션(HTTPS)에서만. 로컬 개발(http)에서 True 면 쿠키가 유실돼 무한로그인 발생.
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') != 'development'
app.config['SESSION_COOKIE_HTTPONLY'] = True
# session.permanent=True 일 때 쿠키 만료 기간. 이 값이 있어야 세션 전용 쿠키가 아닌 영속 쿠키가 됨.
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# CORS configuration
CORS(app,
     origins=[
         'http://localhost:3000',
         'http://localhost:3001',
         'http://localhost:3002',
         'http://localhost:5173',
         'https://debimarlene.com',
         'https://debi-marlene.com',
     ],
     supports_credentials=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(servers_bp, url_prefix='/api')
app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
app.register_blueprint(me_bp, url_prefix='/api/me')
app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
app.register_blueprint(credits_bp, url_prefix='/api/credits')
app.register_blueprint(credits_topup_bp, url_prefix='/api/credits/topup')
app.register_blueprint(blocked_bp, url_prefix='/api')
app.register_blueprint(og_key_bp, url_prefix='/api/og-key')

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok'})

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f'Server error: {e}')
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8081))
    debug = os.getenv('FLASK_ENV') == 'development'

    logger.info(f'Starting Dashboard Backend on port {port}')
    app.run(host='0.0.0.0', port=port, debug=debug)

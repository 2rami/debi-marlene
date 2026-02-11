"""
Debi Marlene Dashboard Backend
Flask API server for Discord bot dashboard
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from routes.auth import auth_bp
from routes.servers import servers_bp
from routes.premium import premium_bp

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'debi-marlene-dashboard-secret-key')

# Session configuration
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') != 'development'
app.config['SESSION_COOKIE_HTTPONLY'] = True

# CORS configuration
CORS(app,
     origins=[
         'http://localhost:3000',
         'http://localhost:3001',
         'http://localhost:3002',
         'http://localhost:5173',
         'https://debimarlene.com',
     ],
     supports_credentials=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(servers_bp, url_prefix='/api')
app.register_blueprint(premium_bp, url_prefix='/api/premium')

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

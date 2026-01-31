"""
Premium & Payment Routes
Toss Payments integration for subscription management
"""

import os
import base64
import logging
import requests
from flask import Blueprint, jsonify, session, request
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

premium_bp = Blueprint('premium', __name__)

# Toss Payments configuration
TOSS_SECRET_KEY = os.getenv('TOSS_SECRET_KEY')
TOSS_API_URL = 'https://api.tosspayments.com/v1'

# Pricing
PLANS = {
    'monthly': {
        'name': '월간 프리미엄',
        'amount': 9900,
        'period_days': 30,
    },
    'yearly': {
        'name': '연간 프리미엄',
        'amount': 99000,
        'period_days': 365,
    },
}

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_toss_auth_header():
    """Get Toss Payments authorization header"""
    encoded = base64.b64encode(f'{TOSS_SECRET_KEY}:'.encode()).decode()
    return {'Authorization': f'Basic {encoded}'}

@premium_bp.route('/plans')
def get_plans():
    """Get available subscription plans"""
    return jsonify({
        'plans': [
            {
                'id': 'monthly',
                'name': PLANS['monthly']['name'],
                'amount': PLANS['monthly']['amount'],
                'period': '월',
            },
            {
                'id': 'yearly',
                'name': PLANS['yearly']['name'],
                'amount': PLANS['yearly']['amount'],
                'period': '년',
            },
        ]
    })

@premium_bp.route('/status')
@login_required
def get_premium_status():
    """Get user's premium status"""
    user = session.get('user')

    # TODO: Get premium status from Firestore
    return jsonify({
        'premium': {
            'isActive': False,
            'plan': None,
            'expiresAt': None,
        }
    })

@premium_bp.route('/checkout', methods=['POST'])
@login_required
def create_checkout():
    """Create payment checkout session"""
    user = session.get('user')
    data = request.json

    plan_id = data.get('plan')
    if plan_id not in PLANS:
        return jsonify({'error': 'Invalid plan'}), 400

    plan = PLANS[plan_id]

    # Generate unique order ID
    order_id = f'debi_{user["id"]}_{plan_id}_{int(datetime.now().timestamp())}'

    return jsonify({
        'orderId': order_id,
        'amount': plan['amount'],
        'orderName': plan['name'],
        'customerKey': f'ckey_{user["id"]}',
    })

@premium_bp.route('/confirm', methods=['POST'])
@login_required
def confirm_payment():
    """Confirm payment after Toss Payments widget success"""
    user = session.get('user')
    data = request.json

    payment_key = data.get('paymentKey')
    order_id = data.get('orderId')
    amount = data.get('amount')

    if not all([payment_key, order_id, amount]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Confirm payment with Toss API
        response = requests.post(
            f'{TOSS_API_URL}/payments/confirm',
            headers={
                **get_toss_auth_header(),
                'Content-Type': 'application/json',
            },
            json={
                'paymentKey': payment_key,
                'orderId': order_id,
                'amount': amount,
            }
        )

        if not response.ok:
            error_data = response.json()
            logger.error(f'Toss payment confirmation failed: {error_data}')
            return jsonify({'error': error_data.get('message', 'Payment failed')}), 400

        payment_data = response.json()

        # Determine plan from amount
        plan_id = 'monthly' if amount == 9900 else 'yearly'
        plan = PLANS[plan_id]

        # Calculate expiration
        expires_at = datetime.now() + timedelta(days=plan['period_days'])

        # TODO: Save to Firestore
        # - Update user premium status
        # - Save payment record
        logger.info(f'Payment confirmed for user {user["id"]}: {plan_id}')

        return jsonify({
            'success': True,
            'premium': {
                'isActive': True,
                'plan': plan_id,
                'expiresAt': expires_at.isoformat(),
            }
        })

    except requests.RequestException as e:
        logger.error(f'Toss API request failed: {e}')
        return jsonify({'error': 'Payment confirmation failed'}), 500

@premium_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """Handle Toss Payments webhooks"""
    data = request.json

    event_type = data.get('eventType')
    logger.info(f'Received Toss webhook: {event_type}')

    if event_type == 'PAYMENT_STATUS_CHANGED':
        # Handle payment status changes
        payment = data.get('data', {})
        status = payment.get('status')

        if status == 'CANCELED':
            # Handle cancellation
            pass
        elif status == 'PARTIAL_CANCELED':
            # Handle partial cancellation
            pass

    elif event_type == 'BILLING_KEY_DELETED':
        # Handle subscription cancellation
        pass

    return jsonify({'success': True})

@premium_bp.route('/cancel', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel premium subscription"""
    user = session.get('user')

    # TODO: Cancel subscription in Firestore
    # - Mark as canceled
    # - Keep access until expiration

    logger.info(f'Subscription canceled for user {user["id"]}')

    return jsonify({'success': True})

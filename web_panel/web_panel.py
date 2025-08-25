#!/usr/bin/env python3
"""
데비&마를렌 봇 웹 관리 패널
Discord 봇을 웹 인터페이스로 관리할 수 있는 대시보드
"""

import os
import json
import psutil
import asyncio
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 봇 설정 모듈 import
from run import config
from run.api_clients import get_bot_instance
from aws_integration import get_aws_bot_manager

app = Flask(__name__)
CORS(app)

# Jinja2 필터 추가
@app.template_filter('tojson')
def tojson_filter(obj):
    return json.dumps(obj)

# 전역 변수로 봇 인스턴스 저장
bot_instance = None

def get_system_stats():
    """시스템 리소스 사용량 조회"""
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'uptime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_percent': 0,
            'uptime': 'Unknown',
            'error': str(e)
        }

def get_bot_stats():
    """봇 통계 정보 조회 (AWS 배포 버전 기반)"""
    try:
        # AWS에서 배포된 봇 상태 조회
        aws_manager = get_aws_bot_manager()
        deployment_status = aws_manager.get_bot_status()
        
        # 실제 서버 수 조회 - 여러 방법 시도
        real_server_count = None
        server_count_method = "설정 파일"
        
        # 1. 봇 인스턴스에서 직접 조회 (가장 정확)
        bot = get_bot_instance()
        if bot and hasattr(bot, 'guilds'):
            real_server_count = len(bot.guilds)
            server_count_method = "봇 인스턴스 (실시간)"
        else:
            # 2. CloudWatch 로그에서 파싱
            try:
                log_data = aws_manager.get_real_guild_count_from_logs()
                if log_data:
                    real_server_count = log_data['guild_count']
                    server_count_method = f"CloudWatch 로그 ({log_data.get('individual_guilds_found', 0)}개 개별 서버 발견)"
            except:
                pass
        
        # 3. 설정 파일 기반 (폴백)
        settings = config.load_settings()
        settings_server_count = len(settings.get('guilds', {}))
        if real_server_count is None:
            real_server_count = settings_server_count
            server_count_method = "설정 파일 (불완전)"
        
        # 서버 수 차이가 있으면 경고 표시
        server_count_warning = None
        if real_server_count != settings_server_count:
            server_count_warning = f"설정 파일({settings_server_count})과 실제({real_server_count}) 서버 수가 다릅니다"
        
        subscribers_count = len(config.get_youtube_subscribers())
        
        # 배포 상태 기반으로 봇 상태 결정
        if deployment_status.get('running_tasks', 0) > 0:
            bot_status = f"🟢 실행 중 ({deployment_status.get('running_tasks')}개 태스크)"
        else:
            bot_status = "🔴 중지됨"
        
        # AWS 리소스 사용량 조회
        resource_usage = aws_manager.get_resource_usage()
        
        # 실제 멤버 수 계산 (봇 인스턴스 사용 가능한 경우)
        total_members = real_server_count * 100  # 기본 추정값
        if bot and hasattr(bot, 'guilds'):
            total_members = sum(guild.member_count for guild in bot.guilds if guild.member_count)
        
        return {
            'status': bot_status,
            'total_servers': real_server_count,
            'total_members': total_members,
            'subscribers_count': subscribers_count,
            'server_count_method': server_count_method,
            'server_count_warning': server_count_warning,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'deployment': {
                'running_tasks': deployment_status.get('running_tasks', 0),
                'desired_tasks': deployment_status.get('desired_tasks', 0),
                'last_deployment': deployment_status.get('last_deployment', 'Unknown'),
                'task_definition': deployment_status.get('task_definition', 'Unknown')
            },
            'resources': {
                'cpu_utilization': resource_usage.get('cpu_utilization', 0),
                'memory_utilization': resource_usage.get('memory_utilization', 0)
            }
        }
    except Exception as e:
        # AWS 연결 실패 시 기본 정보로 폴백
        settings = config.load_settings()
        return {
            'status': "⚠️ AWS 연결 실패",
            'total_servers': len(settings.get('guilds', {})),
            'total_members': len(settings.get('guilds', {})) * 100,
            'subscribers_count': len(config.get_youtube_subscribers()),
            'server_count_method': "설정 파일 (AWS 오류)",
            'server_count_warning': "AWS 연결 실패로 정확한 서버 수를 확인할 수 없습니다",
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e)
        }

@app.route('/')
def dashboard():
    """메인 대시보드 페이지"""
    system_stats = get_system_stats()
    bot_stats = get_bot_stats()
    
    return render_template('dashboard.html', 
                         system_stats=system_stats,
                         bot_stats=bot_stats)

@app.route('/api/stats')
def api_stats():
    """API: 실시간 통계 데이터"""
    return jsonify({
        'system': get_system_stats(),
        'bot': get_bot_stats()
    })

@app.route('/servers')
def servers():
    """서버 관리 페이지 (설정 기반)"""
    try:
        settings = config.load_settings()
        servers_data = []
        
        # 설정 파일의 guilds에서 서버 정보 추출
        guilds = settings.get('guilds', {})
        
        for guild_id, guild_settings in guilds.items():
            servers_data.append({
                'id': guild_id,
                'name': f"서버 {guild_id[:8]}...",  # 임시 이름
                'member_count': 100,  # 임시 멤버 수
                'announcement_channel': {
                    'id': guild_settings.get('ANNOUNCEMENT_CHANNEL_ID'),
                    'name': f"channel-{guild_settings.get('ANNOUNCEMENT_CHANNEL_ID', 'none')}" if guild_settings.get('ANNOUNCEMENT_CHANNEL_ID') else None
                },
                'chat_channel': {
                    'id': guild_settings.get('CHAT_CHANNEL_ID'), 
                    'name': f"channel-{guild_settings.get('CHAT_CHANNEL_ID', 'none')}" if guild_settings.get('CHAT_CHANNEL_ID') else None
                },
                'channels': [
                    {'id': 1234567890, 'name': 'general', 'type': 'text'},
                    {'id': 1234567891, 'name': 'announcements', 'type': 'text'},
                    {'id': 1234567892, 'name': 'chat', 'type': 'text'}
                ]  # 임시 채널 목록
            })
        
        # 개인 사용자 정보 (유튜브 구독자 + 일반 사용자)
        all_users = config.get_all_users()
        subscribers_data = []
        general_users_data = []
        
        for user in all_users:
            user_info = {
                'id': user['id'],
                'name': f"사용자 {user['id']}",
                'display_name': f"User {user['id']}",
                'youtube_subscribed': user.get('youtube_subscribed', False),
                'first_interaction': user.get('first_interaction'),
                'last_seen': user.get('last_seen'),
                'server_admin': user.get('server_admin', False)
            }
            
            if user.get('youtube_subscribed'):
                subscribers_data.append(user_info)
            else:
                general_users_data.append(user_info)
        
        return render_template('servers.html', 
                             servers=servers_data,
                             subscribers=subscribers_data,
                             general_users=general_users_data)
    except Exception as e:
        return render_template('servers.html', 
                             servers=[], 
                             subscribers=[],
                             general_users=[],
                             error=str(e))

@app.route('/announce')
def announce():
    """공지 전송 페이지"""
    return render_template('announce.html')

@app.route('/api/announce', methods=['POST'])
def api_announce():
    """API: 공지 전송"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        send_to_channels = data.get('send_to_channels', True)
        send_to_subscribers = data.get('send_to_subscribers', True)
        send_to_admins = data.get('send_to_admins', False)
        
        if not message:
            return jsonify({'success': False, 'error': '메시지가 비어있습니다.'})
        
        bot = get_bot_instance()
        if not bot:
            return jsonify({'success': False, 'error': '봇 인스턴스를 찾을 수 없습니다.'})
        
        # 공지 전송 로직 (비동기로 처리)
        async def send_announcements():
            sent_count = 0
            errors = []
            
            # 서버별 공지 전송
            if send_to_channels:
                for guild in bot.guilds:
                    try:
                        guild_settings = config.get_guild_settings(guild.id)
                        announcement_channel_id = guild_settings.get('ANNOUNCEMENT_CHANNEL_ID')
                        
                        if announcement_channel_id:
                            channel = guild.get_channel(announcement_channel_id)
                            if channel:
                                await channel.send(f"📢 **공지사항**\n\n{message}")
                                sent_count += 1
                            else:
                                errors.append(f"서버 '{guild.name}': 공지 채널을 찾을 수 없음")
                        else:
                            errors.append(f"서버 '{guild.name}': 공지 채널이 설정되지 않음")
                    except Exception as e:
                        errors.append(f"서버 '{guild.name}': {str(e)}")
            
            # 개인 구독자 DM 전송
            if send_to_subscribers:
                subscribers = config.get_youtube_subscribers()
                for user_id in subscribers:
                    try:
                        user = bot.get_user(user_id)
                        if user:
                            await user.send(f"📢 **공지사항**\n\n{message}")
                            sent_count += 1
                    except Exception as e:
                        errors.append(f"구독자 {user_id}: {str(e)}")
            
            # 서버 관리자 DM 전송
            if send_to_admins:
                for guild in bot.guilds:
                    try:
                        # Discord에서 실제 관리자 권한 확인
                        for member in guild.members:
                            if member.guild_permissions.administrator or member.guild_permissions.manage_guild:
                                try:
                                    await member.send(f"👑 **[{guild.name}] 관리자 공지**\n\n{message}")
                                    sent_count += 1
                                    # 관리자 정보를 config에 저장
                                    config.set_server_admin(member.id, guild.id, True)
                                except Exception as e:
                                    errors.append(f"관리자 {member.display_name} ({guild.name}): {str(e)}")
                    except Exception as e:
                        errors.append(f"서버 '{guild.name}' 관리자 조회 오류: {str(e)}")
            
            return {'sent_count': sent_count, 'errors': errors}
        
        # 이벤트 루프에서 실행
        if bot.loop and not bot.loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(send_announcements(), bot.loop)
            result = future.result(timeout=30)
            
            return jsonify({
                'success': True,
                'sent_count': result['sent_count'],
                'errors': result['errors']
            })
        else:
            return jsonify({'success': False, 'error': '봇이 실행되지 않았습니다.'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/server/settings', methods=['POST'])
def api_update_server_settings():
    """API: 서버 설정 업데이트"""
    try:
        data = request.json
        guild_id = int(data.get('guild_id'))
        announcement_channel_id = data.get('announcement_channel_id')
        chat_channel_id = data.get('chat_channel_id')
        
        # 설정 업데이트
        success = config.save_guild_settings(
            guild_id,
            announcement_id=int(announcement_channel_id) if announcement_channel_id else None,
            chat_id=int(chat_channel_id) if chat_channel_id else None
        )
        
        if success:
            return jsonify({'success': True, 'message': '설정이 저장되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '설정 저장에 실패했습니다.'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/logs')
def logs():
    """로그 확인 페이지"""
    return render_template('logs.html')

@app.route('/api/logs')
def api_logs():
    """API: 배포된 봇의 실제 로그 조회"""
    try:
        hours = request.args.get('hours', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        # AWS CloudWatch에서 실제 배포된 봇 로그 가져오기
        aws_manager = get_aws_bot_manager()
        logs = aws_manager.get_bot_logs(hours=hours, limit=limit)
        
        # 로그가 없으면 기본 로그 반환
        if not logs:
            logs = [
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'level': 'INFO',
                    'message': '배포된 봇 로그를 조회 중입니다...'
                },
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'level': 'WARNING', 
                    'message': 'CloudWatch 로그를 가져올 수 없습니다. AWS 권한을 확인하세요.'
                }
            ]
        
        return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'logs': [], 'error': str(e)})

# 새로운 AWS 관리 API들
@app.route('/api/aws/restart', methods=['POST'])
def api_restart_bot():
    """API: 배포된 봇 재시작"""
    try:
        aws_manager = get_aws_bot_manager()
        result = aws_manager.restart_bot()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/aws/stop', methods=['POST'])
def api_stop_bot():
    """API: 배포된 봇 중지"""
    try:
        aws_manager = get_aws_bot_manager()
        result = aws_manager.stop_bot()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/aws/start', methods=['POST'])
def api_start_bot():
    """API: 배포된 봇 시작"""
    try:
        aws_manager = get_aws_bot_manager()
        result = aws_manager.start_bot()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/aws/deployments')
def api_deployment_history():
    """API: 배포 히스토리 조회"""
    try:
        aws_manager = get_aws_bot_manager()
        history = aws_manager.get_deployment_history()
        return jsonify({'deployments': history})
    except Exception as e:
        return jsonify({'deployments': [], 'error': str(e)})

@app.route('/api/bot/real_guild_count')
def api_real_guild_count():
    """API: 실제 봇이 연결된 서버 수 조회 (여러 방법 시도)"""
    try:
        result = {
            'methods': {}
        }
        
        # 방법 1: 봇 인스턴스에서 직접 조회 (로컬에서만 가능)
        bot = get_bot_instance()
        if bot and hasattr(bot, 'guilds'):
            guilds = bot.guilds
            result['methods']['direct_bot_instance'] = {
                'guild_count': len(guilds),
                'guild_names': [f"{guild.name} (ID: {guild.id})" for guild in guilds[:10]],  # 최대 10개만
                'available': True
            }
        else:
            result['methods']['direct_bot_instance'] = {
                'guild_count': 0,
                'available': False,
                'error': '봇 인스턴스에 접근할 수 없음 (배포 환경)'
            }
        
        # 방법 2: AWS CloudWatch 로그에서 파싱
        try:
            aws_manager = get_aws_bot_manager()
            log_data = aws_manager.get_real_guild_count_from_logs()
            if log_data:
                result['methods']['cloudwatch_logs'] = {
                    'guild_count': log_data['guild_count'],
                    'individual_guilds_found': log_data['individual_guilds_found'],
                    'total_from_logs': log_data['total_from_logs'],
                    'sample_guild_ids': log_data['guild_ids'],
                    'available': True
                }
            else:
                result['methods']['cloudwatch_logs'] = {
                    'guild_count': 0,
                    'available': False,
                    'error': 'CloudWatch 로그에서 길드 정보를 찾을 수 없음'
                }
        except Exception as e:
            result['methods']['cloudwatch_logs'] = {
                'guild_count': 0,
                'available': False,
                'error': f'CloudWatch 조회 실패: {str(e)}'
            }
        
        # 방법 3: 설정 파일 기반 (기존 방식)
        settings = config.load_settings()
        result['methods']['settings_file'] = {
            'guild_count': len(settings.get('guilds', {})),
            'guild_ids': list(settings.get('guilds', {}).keys()),
            'available': True,
            'note': '설정 파일에 저장된 서버만 표시 (실제보다 적을 수 있음)'
        }
        
        # 가장 신뢰할 수 있는 방법 결정
        best_method = 'settings_file'
        best_count = result['methods']['settings_file']['guild_count']
        
        if result['methods']['direct_bot_instance']['available']:
            best_method = 'direct_bot_instance'
            best_count = result['methods']['direct_bot_instance']['guild_count']
        elif result['methods']['cloudwatch_logs']['available']:
            best_method = 'cloudwatch_logs'
            best_count = result['methods']['cloudwatch_logs']['guild_count']
        
        result['recommended'] = {
            'method': best_method,
            'guild_count': best_count,
            'confidence': 'high' if best_method == 'direct_bot_instance' else 'medium' if best_method == 'cloudwatch_logs' else 'low'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e), 'methods': {}})

if __name__ == '__main__':
    print("🌐 데비&마를렌 웹 관리 패널을 시작합니다...")
    print("📱 접속 주소: http://localhost:8080")
    
    # 개발 모드에서 실행
    app.run(host='0.0.0.0', port=8080, debug=True)
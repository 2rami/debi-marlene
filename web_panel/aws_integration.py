#!/usr/bin/env python3
"""
배포된 Discord 봇 AWS 통합 관리 클래스
ECS, CloudWatch, Secrets Manager를 통해 배포된 봇을 관리
"""

import boto3
import json
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

class AWSBotManager:
    """배포된 Discord 봇 AWS 관리 클래스"""
    
    def __init__(self, region='ap-northeast-2'):
        self.region = region
        self.ecs_client = boto3.client('ecs', region_name=region)
        self.logs_client = boto3.client('logs', region_name=region)
        self.sm_client = boto3.client('secretsmanager', region_name=region)
        
        # ECS 클러스터 및 서비스 정보
        self.cluster_name = 'debi-marlene-cluster'
        self.service_name = 'debi-marlene-bot'
        self.task_family = 'debi-marlene-bot'
        
    def get_bot_status(self):
        """배포된 봇의 현재 상태 조회"""
        try:
            # ECS 서비스 상태 확인
            response = self.ecs_client.describe_services(
                cluster=self.cluster_name,
                services=[self.service_name]
            )
            
            if response['services']:
                service = response['services'][0]
                running_count = service['runningCount']
                desired_count = service['desiredCount']
                
                if running_count > 0:
                    status = "🟢 실행 중"
                else:
                    status = "🔴 중지됨"
                
                return {
                    'status': status,
                    'running_tasks': running_count,
                    'desired_tasks': desired_count,
                    'last_deployment': service.get('deployments', [{}])[0].get('createdAt', 'Unknown'),
                    'task_definition': service.get('taskDefinition', 'Unknown')
                }
            else:
                return {
                    'status': '❌ 서비스 없음',
                    'running_tasks': 0,
                    'desired_tasks': 0,
                    'error': 'ECS 서비스를 찾을 수 없음'
                }
                
        except ClientError as e:
            return {
                'status': '❌ 오류',
                'error': str(e),
                'running_tasks': 0,
                'desired_tasks': 0
            }
    
    def get_bot_logs(self, hours=1, limit=100):
        """배포된 봇의 최근 로그 조회"""
        try:
            log_group = '/ecs/debi-marlene-bot'
            
            # 최근 시간 계산
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            response = self.logs_client.filter_log_events(
                logGroupName=log_group,
                startTime=int(start_time.timestamp() * 1000),
                endTime=int(end_time.timestamp() * 1000),
                limit=limit
            )
            
            logs = []
            for event in response.get('events', []):
                logs.append({
                    'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                    'level': 'INFO',  # CloudWatch에서는 레벨을 파싱해야 함
                    'message': event['message'].strip()
                })
            
            return logs[::-1]  # 최신순으로 정렬
            
        except ClientError as e:
            print(f"로그 조회 오류: {e}")
            return []
    
    def get_real_guild_count_from_logs(self, hours=2):
        """CloudWatch 로그에서 실제 연결된 서버 수 파싱"""
        try:
            log_group = '/ecs/debi-marlene-bot'
            
            # 최근 시간 계산 (조금 더 넓은 범위로 검색)
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 봇 시작 로그나 길드 관련 로그 검색
            response = self.logs_client.filter_log_events(
                logGroupName=log_group,
                startTime=int(start_time.timestamp() * 1000),
                endTime=int(end_time.timestamp() * 1000),
                filterPattern='[timestamp, level, message*guild* | message*서버* | message*봇이*시작* | message*ready*]',
                limit=200
            )
            
            guilds_found = set()
            total_guilds = None
            
            for event in response.get('events', []):
                message = event['message'].strip()
                
                # 다양한 패턴으로 서버 정보 파싱
                patterns_to_check = [
                    # 봇 시작 시 서버 수 로깅 패턴
                    r'(\d+)개.*서버',
                    r'(\d+).*guild',
                    r'Connected to (\d+) guilds',
                    r'총 (\d+)개 서버',
                    # 개별 서버 ID 패턴 (Guild ID: 숫자)
                    r'[Gg]uild.*?(\d{15,20})',
                    r'서버.*?(\d{15,20})',
                    # on_guild_join 로그 패턴
                    r'새로운 서버.*?(\d{15,20})',
                    r'초대되었습니다.*?(\d{15,20})'
                ]
                
                import re
                for pattern in patterns_to_check:
                    matches = re.findall(pattern, message)
                    for match in matches:
                        if len(match) >= 15:  # Discord 서버 ID 길이
                            guilds_found.add(match)
                        elif match.isdigit() and int(match) > 0 and int(match) < 10000:  # 서버 개수
                            if total_guilds is None or int(match) > total_guilds:
                                total_guilds = int(match)
            
            # 찾은 개별 서버 ID 개수와 로그에서 파싱한 총 서버 수 중 더 정확한 것 반환
            if guilds_found:
                parsed_count = len(guilds_found)
                return {
                    'guild_count': max(parsed_count, total_guilds or 0),
                    'individual_guilds_found': parsed_count,
                    'total_from_logs': total_guilds,
                    'guild_ids': list(guilds_found)[:10]  # 최대 10개만 표시
                }
            elif total_guilds:
                return {
                    'guild_count': total_guilds,
                    'individual_guilds_found': 0,
                    'total_from_logs': total_guilds,
                    'guild_ids': []
                }
            else:
                return None
            
        except ClientError as e:
            print(f"길드 수 파싱 오류: {e}")
            return None
    
    def restart_bot(self):
        """배포된 봇 재시작"""
        try:
            # ECS 서비스 강제 새 배포
            response = self.ecs_client.update_service(
                cluster=self.cluster_name,
                service=self.service_name,
                forceNewDeployment=True
            )
            
            return {
                'success': True,
                'message': '봇 재시작이 시작되었습니다.',
                'deployment_id': response['service']['deployments'][0]['id']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def stop_bot(self):
        """배포된 봇 중지"""
        try:
            response = self.ecs_client.update_service(
                cluster=self.cluster_name,
                service=self.service_name,
                desiredCount=0
            )
            
            return {
                'success': True,
                'message': '봇 중지가 시작되었습니다.'
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def start_bot(self):
        """배로된 봇 시작"""
        try:
            response = self.ecs_client.update_service(
                cluster=self.cluster_name,
                service=self.service_name,
                desiredCount=1
            )
            
            return {
                'success': True,
                'message': '봇 시작이 요청되었습니다.'
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_resource_usage(self):
        """배포된 봇의 리소스 사용량 조회"""
        try:
            # 실행 중인 태스크 정보 조회
            tasks_response = self.ecs_client.list_tasks(
                cluster=self.cluster_name,
                serviceName=self.service_name
            )
            
            if not tasks_response['taskArns']:
                return {
                    'cpu_utilization': 0,
                    'memory_utilization': 0,
                    'error': '실행 중인 태스크 없음'
                }
            
            # CloudWatch 메트릭으로 실제 사용량 조회 (구현 필요)
            # 임시로 기본값 반환
            return {
                'cpu_utilization': 15.5,
                'memory_utilization': 45.2,
                'network_in': 1024,
                'network_out': 512
            }
            
        except ClientError as e:
            return {
                'cpu_utilization': 0,
                'memory_utilization': 0,
                'error': str(e)
            }
    
    def update_secrets(self, secret_updates):
        """Secrets Manager의 봇 시크릿 업데이트"""
        try:
            results = {}
            
            for secret_name, new_value in secret_updates.items():
                try:
                    self.sm_client.update_secret(
                        SecretId=f"debi-marlene/{secret_name}",
                        SecretString=new_value
                    )
                    results[secret_name] = {'success': True, 'message': '업데이트 완료'}
                except ClientError as e:
                    results[secret_name] = {'success': False, 'error': str(e)}
            
            return results
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_deployment_history(self, limit=10):
        """배포 히스토리 조회"""
        try:
            response = self.ecs_client.describe_services(
                cluster=self.cluster_name,
                services=[self.service_name]
            )
            
            if response['services']:
                deployments = response['services'][0].get('deployments', [])
                
                history = []
                for deployment in deployments[:limit]:
                    history.append({
                        'id': deployment.get('id', 'Unknown'),
                        'status': deployment.get('status', 'Unknown'),
                        'task_definition': deployment.get('taskDefinition', '').split('/')[-1],
                        'created_at': deployment.get('createdAt', 'Unknown'),
                        'updated_at': deployment.get('updatedAt', 'Unknown'),
                        'running_count': deployment.get('runningCount', 0),
                        'desired_count': deployment.get('desiredCount', 0)
                    })
                
                return history
            
            return []
            
        except ClientError as e:
            print(f"배포 히스토리 조회 오류: {e}")
            return []

# 전역 인스턴스
aws_bot_manager = None

def get_aws_bot_manager():
    """AWS 봇 매니저 인스턴스 가져오기"""
    global aws_bot_manager
    if aws_bot_manager is None:
        aws_bot_manager = AWSBotManager()
    return aws_bot_manager
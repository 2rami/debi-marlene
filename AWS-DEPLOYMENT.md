# AWS ECS 배포 가이드

Discord 봇을 AWS ECS로 배포하는 방법입니다.

## 사전 준비

1. **AWS CLI 설치 및 설정**
   ```bash
   aws configure
   ```

2. **Docker 설치** (이미 되어있음)

3. **환경 변수 준비**
   - DISCORD_TOKEN
   - EternalReturn_API_KEY
   - CLAUDE_API_KEY
   - YOUTUBE_API_KEY

## 배포 단계

### 1. AWS 설정 수정

`deploy-aws.sh` 파일에서 다음 값들을 수정하세요:
```bash
AWS_REGION="us-east-1"           # 원하는 리전
AWS_ACCOUNT_ID="123456789012"    # AWS 계정 ID
```

### 2. ECS Task Definition 수정

`aws-ecs-task-definition.json` 파일에서:
- `YOUR_ACCOUNT_ID`: AWS 계정 ID
- `YOUR_ECR_REPO_URI`: ECR 리포지토리 URI
- 환경 변수들을 실제 값으로 변경

### 3. 배포 실행

```bash
./deploy-aws.sh
```

### 4. ECS 서비스 생성

AWS 콘솔 또는 CLI로 ECS 서비스를 생성:

```bash
# Task Definition 등록
aws ecs register-task-definition --cli-input-json file://aws-ecs-task-definition.json

# 서비스 생성
aws ecs create-service \
  --cluster debi-marlene-cluster \
  --service-name debi-marlene-service \
  --task-definition debi-marlene-bot \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

## 비용 예상

**ECS Fargate (최소 구성)**:
- CPU: 0.25 vCPU
- 메모리: 512 MB
- 월 예상 비용: 약 $6-8

## 모니터링

- **CloudWatch 로그**: `/ecs/debi-marlene-bot`
- **ECS 콘솔**: 서비스 상태 확인
- **CloudWatch 메트릭**: CPU/메모리 사용량

## 문제 해결

1. **봇이 시작되지 않는 경우**
   - CloudWatch 로그 확인
   - 환경 변수 확인

2. **메모리 부족**
   - Task Definition에서 메모리 증가 (512MB → 1024MB)

3. **네트워크 문제**
   - 보안 그룹에서 아웃바운드 트래픽 허용 확인
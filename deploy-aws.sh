#!/bin/bash

# AWS 배포 스크립트
set -e

# 변수 설정
AWS_REGION="ap-northeast-2"
AWS_ACCOUNT_ID="718942600976"
ECR_REPO_NAME="debi-marlene-bot"
CLUSTER_NAME="debi-marlene-cluster"
SERVICE_NAME="debi-marlene-service"

echo "🚀 AWS ECS로 Discord 봇 배포 시작..."

# 1. ECR 로그인
echo "📝 ECR 로그인 중..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. ECR 리포지토리 생성 (존재하지 않는 경우)
echo "📦 ECR 리포지토리 확인/생성 중..."
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION 2>/dev/null || \
aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION

# 3. Docker 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker build -t $ECR_REPO_NAME .

# 4. 이미지 태그 지정
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME"
docker tag $ECR_REPO_NAME:latest $ECR_URI:latest

# 5. ECR에 푸시
echo "📤 ECR에 이미지 푸시 중..."
docker push $ECR_URI:latest

# 6. ECS 클러스터 생성 (존재하지 않는 경우)
echo "🏗️ ECS 클러스터 확인/생성 중..."
aws ecs describe-clusters --clusters $CLUSTER_NAME --region $AWS_REGION 2>/dev/null || \
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION

# 7. CloudWatch 로그 그룹 생성
echo "📊 CloudWatch 로그 그룹 생성 중..."
aws logs create-log-group --log-group-name "/ecs/debi-marlene-bot" --region $AWS_REGION 2>/dev/null || true

echo "✅ 배포 완료!"
echo "📋 다음 단계:"
echo "1. aws-ecs-task-definition.json에서 YOUR_* 값들을 실제 값으로 수정하세요"
echo "2. ECS 콘솔에서 태스크 정의를 등록하고 서비스를 생성하세요"
echo "3. 또는 AWS CLI로 계속 진행하세요:"
echo "   aws ecs register-task-definition --cli-input-json file://aws-ecs-task-definition.json"
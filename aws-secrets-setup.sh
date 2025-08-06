#!/bin/bash

# AWS Secrets Manager에 시크릿 생성하는 스크립트
# 사용 전에 AWS CLI가 설정되어 있어야 합니다

echo "AWS Secrets Manager에 봇 시크릿들을 생성합니다..."

# Discord Token 시크릿 생성
aws secretsmanager create-secret \
    --name "debi-marlene/discord-token" \
    --description "Discord bot token for debi-marlene" \
    --secret-string "여기에_디스코드_토큰_입력" \
    --region ap-northeast-2

# EternalReturn API Key 시크릿 생성  
aws secretsmanager create-secret \
    --name "debi-marlene/eternalreturn-api-key" \
    --description "EternalReturn API key for debi-marlene" \
    --secret-string "여기에_EternalReturn_API_키_입력" \
    --region ap-northeast-2

# Claude API Key 시크릿 생성
aws secretsmanager create-secret \
    --name "debi-marlene/claude-api-key" \
    --description "Claude API key for debi-marlene" \
    --secret-string "여기에_Claude_API_키_입력" \
    --region ap-northeast-2

# YouTube API Key 시크릿 생성
aws secretsmanager create-secret \
    --name "debi-marlene/youtube-api-key" \
    --description "YouTube API key for debi-marlene" \
    --secret-string "여기에_YouTube_API_키_입력" \
    --region ap-northeast-2

echo "시크릿 생성이 완료되었습니다!"
echo "이제 실제 API 키 값들을 각 시크릿에 업데이트해주세요:"
echo ""
echo "aws secretsmanager update-secret --secret-id debi-marlene/discord-token --secret-string '실제_디스코드_토큰'"
echo "aws secretsmanager update-secret --secret-id debi-marlene/eternalreturn-api-key --secret-string '실제_EternalReturn_키'"
echo "aws secretsmanager update-secret --secret-id debi-marlene/claude-api-key --secret-string '실제_Claude_키'"
echo "aws secretsmanager update-secret --secret-id debi-marlene/youtube-api-key --secret-string '실제_YouTube_키'"
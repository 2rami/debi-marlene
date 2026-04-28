#!/usr/bin/env bash
# 로컬 검증용 — VM 배포 전에 거노 PC에서 직접 띄워보는 스크립트.
# 모든 secret 은 GCP Secret Manager / .env 에서 fetch.
set -euo pipefail

cd "$(dirname "$0")/.."
PROJECT="ironic-objectivist-465713-a6"

export COMPANION_BOT_TOKEN=$(gcloud secrets versions access latest --secret=companion-bot-token --project=$PROJECT)
export OWNER_ID=$(gcloud secrets versions access latest --secret=owner-id --project=$PROJECT)
export ANTHROPIC_API_KEY=$(grep -E '^(CLAUDE_API_KEY|ANTHROPIC_API_KEY)=' .env | head -1 | cut -d= -f2- | tr -d '"')
export MANAGED_COMPANION_AGENT_ID=$(grep '^MANAGED_COMPANION_AGENT_ID=' .env | cut -d= -f2-)
export MANAGED_COMPANION_ENV_ID=$(grep '^MANAGED_COMPANION_ENV_ID=' .env | cut -d= -f2-)

echo "=== companion-bot 시작 ==="
echo "  agent=$MANAGED_COMPANION_AGENT_ID"
echo "  env=$MANAGED_COMPANION_ENV_ID"
echo "  owner=$OWNER_ID"
echo "  token=...${COMPANION_BOT_TOKEN: -8}"
echo

exec .venv-dash/bin/python companion_bot/main.py

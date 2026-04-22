#!/usr/bin/env bash
# Google Cloud Secret Manager → 로컬 .env 파일 동기화.
#
# 용도: 맥/윈도우 양쪽 개발 환경에서 .env 값을 단일 소스(Secret Manager)로 유지.
# 사용법:
#   ./scripts/sync_env.sh pull           # Secret Manager → 로컬 파일 (기본)
#   ./scripts/sync_env.sh push           # 로컬 파일 → Secret Manager (새 버전 생성)
#   ./scripts/sync_env.sh pull unified   # .env 하나만 동기화
#
# 첫 실행 전:
#   gcloud auth login
#   gcloud config set project ironic-objectivist-465713-a6

set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# key:secret:file 매핑 (macOS bash 3.2 호환, 평면 문자열)
KEYS="unified solo-debi solo-marlene"

pair_for() {
    case "$1" in
        unified)      echo "debi-marlene-env:.env" ;;
        solo-debi)    echo "debi-marlene-env-solo-debi:.env.solo-debi" ;;
        solo-marlene) echo "debi-marlene-env-solo-marlene:.env.solo-marlene" ;;
        *) echo ""; return 1 ;;
    esac
}

pull_one() {
    local key="$1"
    local pair="$(pair_for "$key")" || { echo "[fail] unknown key: $key" >&2; return 1; }
    local secret="${pair%%:*}"
    local file="${pair##*:}"
    local tmp="${file}.tmp"
    if gcloud secrets versions access latest --secret="$secret" > "$tmp" 2>/dev/null; then
        mv "$tmp" "$file"
        chmod 600 "$file"
        echo "[pull] $secret → $file"
    else
        rm -f "$tmp"
        echo "[fail] $secret 접근 실패" >&2
        return 1
    fi
}

push_one() {
    local key="$1"
    local pair="$(pair_for "$key")" || { echo "[fail] unknown key: $key" >&2; return 1; }
    local secret="${pair%%:*}"
    local file="${pair##*:}"
    if [ ! -f "$file" ]; then
        echo "[skip] $file 없음" >&2
        return 0
    fi
    gcloud secrets versions add "$secret" --data-file="$file" > /dev/null
    echo "[push] $file → $secret (new version)"
}

ACTION="${1:-pull}"
TARGET="${2:-all}"

case "$ACTION" in
    pull|push) ;;
    *)
        echo "Usage: $0 [pull|push] [all|unified|solo-debi|solo-marlene]" >&2
        exit 2
        ;;
esac

if [ "$TARGET" = "all" ]; then
    for key in $KEYS; do
        "${ACTION}_one" "$key"
    done
else
    "${ACTION}_one" "$TARGET"
fi

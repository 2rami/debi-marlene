#!/usr/bin/env bash
# 맥미니 금고(~/.secrets/gcp-sm) ↔ 로컬 .env 파일 동기화.
#
# 용도: 맥/윈도우 양쪽 개발 환경에서 .env 값을 단일 소스로 유지.
# 2026-10-02 Secret Manager(월 ~₩1.8천)를 걷고 그 값을 미니 금고로 옮겼다 — 파일 이름이
# 옛 시크릿 이름 그대로다. 미니에 ssh 가 붙어야 한다(사내 VPN + ~/.ssh/config 의 Host).
# 사용법:
#   ./scripts/sync_env.sh pull           # 미니 금고 → 로컬 파일 (기본)
#   ./scripts/sync_env.sh push           # 로컬 파일 → 미니 금고 (직전 값은 <이름>.prev 로 남긴다)
#   ./scripts/sync_env.sh pull unified   # .env 하나만 동기화

set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VAULT_HOST="${SYNC_ENV_HOST:-nachoneko}"
VAULT_DIR=".secrets/gcp-sm"

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
    if scp -q "$VAULT_HOST:$VAULT_DIR/$secret" "$tmp" 2>/dev/null; then
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
    ssh "$VAULT_HOST" "cd $VAULT_DIR && { [ ! -e $secret ] || cp -p $secret $secret.prev; }" &&
        scp -q "$file" "$VAULT_HOST:$VAULT_DIR/$secret" &&
        ssh "$VAULT_HOST" "chmod 600 $VAULT_DIR/$secret"
    echo "[push] $file → $VAULT_HOST:$VAULT_DIR/$secret (직전 값 $secret.prev)"
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

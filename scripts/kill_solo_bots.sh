#!/usr/bin/env bash
# 솔로봇(debi-solo, marlene-solo) 로컬 python 프로세스 완전 종료.
#
# 왜 필요한가:
#   기존 `pkill -f "BOT_ENV_FILE=.env.solo-*"`는 shell wrapper만 매칭해 python child를 못 잡음.
#   (env var는 argv가 아니라 env block에 있어서 ps/pkill -f 매칭 실패)
#   결과로 좀비 python이 쌓여 같은 토큰으로 동시 연결 → 옛 코드 섞여서 작동하는 현상 발생.
#
# 이 스크립트는 `ps Ewwo`로 env block 내용까지 봐서 실제 솔로봇 python을 정확히 찾아 kill.

set -euo pipefail

ROLE="${1:-all}"  # all | debi | marlene

kill_by_env() {
    local needle="$1"
    local pids
    # ps Ewwo: env var 포함. macOS BSD ps 옵션.
    pids=$(ps Ewwo pid,command -ax 2>/dev/null | awk -v n="$needle" '
        $0 ~ n && $0 ~ /main\.py/ && tolower($0) ~ /python/ { print $1 }
    ')
    if [ -z "$pids" ]; then
        echo "[$needle] 실행 중 python 없음"
        return 0
    fi
    echo "[$needle] kill 대상: $pids"
    echo "$pids" | xargs -r kill -9
}

case "$ROLE" in
    debi)    kill_by_env "BOT_ENV_FILE=\.env\.solo-debi" ;;
    marlene) kill_by_env "BOT_ENV_FILE=\.env\.solo-marlene" ;;
    all)
        kill_by_env "BOT_ENV_FILE=\.env\.solo-debi"
        kill_by_env "BOT_ENV_FILE=\.env\.solo-marlene"
        ;;
    *)
        echo "Usage: $0 [all|debi|marlene]" >&2
        exit 2
        ;;
esac

sleep 1
echo "--- 잔여 python main.py ---"
pgrep -afi "python.*main\.py" || echo "(none)"

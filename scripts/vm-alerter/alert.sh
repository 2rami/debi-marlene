#!/bin/sh
# debi-marlene-bot VM 메모리 모니터 — 85% 5분 지속 시 Discord webhook 알림.
# alpine 컨테이너에서 영구 실행. /proc 은 host 마운트 (--pid=host).

set -eu

THRESHOLD="${THRESHOLD:-85}"        # 메모리 사용률 임계 (%)
SUSTAINED_MIN="${SUSTAINED_MIN:-5}" # 임계 초과 지속 분
COOLDOWN_MIN="${COOLDOWN_MIN:-30}"  # 알림 후 쿨다운 (스팸 방지)
INTERVAL_SEC=60                     # 체크 주기

if [ -z "${WEBHOOK_URL:-}" ]; then
  echo "ERROR: WEBHOOK_URL 환경변수 필요" >&2
  exit 1
fi

apk add --no-cache --quiet curl >/dev/null 2>&1 || true

count=0
cooldown=0

echo "[$(date -u)] alerter 시작 — 임계 ${THRESHOLD}% / ${SUSTAINED_MIN}분 지속 / 쿨다운 ${COOLDOWN_MIN}분"

while true; do
  if [ "$cooldown" -gt 0 ]; then
    cooldown=$((cooldown - 1))
  fi

  mem_pct=$(awk '/MemTotal/{t=$2} /MemAvailable/{a=$2} END{printf "%d", (t-a)*100/t}' /proc/meminfo)
  swap_kb=$(awk '/SwapTotal/{t=$2} /SwapFree/{f=$2} END{printf "%d", t-f}' /proc/meminfo)

  if [ "$mem_pct" -ge "$THRESHOLD" ]; then
    count=$((count + 1))
    echo "[$(date -u)] mem=${mem_pct}% (${count}/${SUSTAINED_MIN}분), swap=${swap_kb}KB"
    if [ "$count" -ge "$SUSTAINED_MIN" ] && [ "$cooldown" -le 0 ]; then
      mem_total_gb=$(awk '/MemTotal/{printf "%.1f", $2/1024/1024}' /proc/meminfo)
      mem_used_gb=$(awk '/MemTotal/{t=$2} /MemAvailable/{a=$2} END{printf "%.1f", (t-a)/1024/1024}' /proc/meminfo)
      msg="⚠ **debi-marlene-bot VM 메모리 ${mem_pct}%**\n사용 ${mem_used_gb}GB / 전체 ${mem_total_gb}GB\n${SUSTAINED_MIN}분 이상 지속됨. 사이즈업 검토 필요."
      curl -sS -X POST -H "Content-Type: application/json" \
        -d "$(printf '{"content":"%s"}' "$msg")" "$WEBHOOK_URL" \
        && echo "[$(date -u)] 알림 전송됨" \
        || echo "[$(date -u)] 알림 전송 실패"
      cooldown=$COOLDOWN_MIN
      count=0
    fi
  else
    if [ "$count" -gt 0 ]; then
      echo "[$(date -u)] mem=${mem_pct}% (정상 복귀, count 리셋)"
    fi
    count=0
  fi

  sleep $INTERVAL_SEC
done

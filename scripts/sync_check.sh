#!/usr/bin/env bash
# 로컬 .env × Secret Manager × VM 해시 3-way diff.
# 불일치 시 exit 1, 전부 일치면 0.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROJECT_ID="ironic-objectivist-465713-a6"
VM_NAME="debi-marlene-bot"
ZONE="asia-northeast3-a"
# VM 상의 env 파일은 /home/kasa/debi-marlene/ 또는 /home/2rami/debi-marlene/ 에
# 흩어져 있음 (배포 SSH 계정 혼재). sudo 로 양쪽 다 시도.
VM_CANDIDATE_DIRS=("/home/kasa/debi-marlene" "/home/2rami/debi-marlene")
SSH_TIMEOUT=10

# macOS/Linux 호환 sha256 함수
sha256_of_file() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

sha256_of_stdin() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum | awk '{print $1}'
    else
        shasum -a 256 | awk '{print $1}'
    fi
}

require_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "ERROR: '$1' 명령을 찾을 수 없습니다. PATH 확인 후 재실행." >&2
        exit 2
    fi
}

require_cmd gcloud

# gcloud 인증 체크
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q '@'; then
    echo "ERROR: gcloud 로그인 필요. 'gcloud auth login' 실행." >&2
    exit 2
fi

# project 확인
CUR_PROJECT="$(gcloud config get-value project 2>/dev/null || true)"
if [ "$CUR_PROJECT" != "$PROJECT_ID" ]; then
    echo "WARN: 현재 project=$CUR_PROJECT (기대: $PROJECT_ID). --project 플래그로 고정 실행." >&2
fi

TMPDIR_LOCAL="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_LOCAL"' EXIT

# (label, local_path, secret_name, vm_basename)
SETS=(
    "unified|.env|debi-marlene-env|.env"
    "solo-debi|.env.solo-debi|debi-marlene-env-solo-debi|.env.solo-debi"
    "solo-marlene|.env.solo-marlene|debi-marlene-env-solo-marlene|.env.solo-marlene"
)

# 두 후보 경로 순차로 시도. 둘 다 empty면 실패.
# 반환: stdout=내용, stderr=없음, return=성공 시 0, 실패 시 1
# 추가로 VM_FOUND_PATH 변수에 발견된 경로 세팅.
fetch_vm_env() {
    local basename="$1" out_file="$2"
    VM_FOUND_PATH=""
    local cmd=""
    # sudo cat 을 파이프로 이어서 첫 성공 시 종료
    cmd="for d in ${VM_CANDIDATE_DIRS[*]}; do"
    cmd+=' f="$d/'"$basename"'";'
    cmd+=' if sudo test -f "$f"; then echo "__PATH__=$f"; sudo cat "$f"; exit 0; fi;'
    cmd+=' done; exit 1'
    if gcloud compute ssh "$VM_NAME" --zone="$ZONE" --project="$PROJECT_ID" \
            --ssh-flag="-o ConnectTimeout=${SSH_TIMEOUT}" \
            --command="$cmd" \
            > "$out_file" 2>/dev/null; then
        # 첫 줄에서 경로 추출 후 제거
        VM_FOUND_PATH="$(head -1 "$out_file" | sed 's/^__PATH__=//')"
        tail -n +2 "$out_file" > "$out_file.body" && mv "$out_file.body" "$out_file"
        [ -s "$out_file" ] && return 0
    fi
    return 1
}

MISMATCH_COUNT=0
OK_COUNT=0

# key-level diff 출력 (주석/빈 줄 제외, 키 이름만 정렬 비교)
print_key_diff() {
    local a_label="$1" a_file="$2"
    local b_label="$3" b_file="$4"
    echo "  -- key-level diff ($a_label vs $b_label) --"
    # KEY=VALUE 기준 라인 필터 + sort
    local a_clean b_clean
    a_clean="$(mktemp)"; b_clean="$(mktemp)"
    grep -Ev '^[[:space:]]*(#|$)' "$a_file" | sort > "$a_clean" || true
    grep -Ev '^[[:space:]]*(#|$)' "$b_file" | sort > "$b_clean" || true
    diff -u "$a_clean" "$b_clean" | sed 's/^/    /' || true
    rm -f "$a_clean" "$b_clean"
}

echo "==== env 3-way sync-check (local × Secret Manager × VM) ===="
echo ""

for entry in "${SETS[@]}"; do
    IFS='|' read -r LABEL LOCAL_PATH SECRET_NAME VM_BASENAME <<< "$entry"
    echo "[$LABEL]"
    echo "  local : $LOCAL_PATH"
    echo "  sm    : $SECRET_NAME"

    # 로컬
    if [ ! -f "$LOCAL_PATH" ]; then
        echo "  STATUS: MISSING local ($LOCAL_PATH 없음)"
        MISMATCH_COUNT=$((MISMATCH_COUNT+1))
        echo ""
        continue
    fi
    LOCAL_HASH="$(sha256_of_file "$LOCAL_PATH")"

    # Secret Manager
    SM_FILE="$TMPDIR_LOCAL/sm-$LABEL"
    if ! gcloud secrets versions access latest --secret="$SECRET_NAME" --project="$PROJECT_ID" > "$SM_FILE" 2>/dev/null; then
        echo "  STATUS: FAIL Secret Manager 접근 실패 (권한/secret 이름 확인)"
        MISMATCH_COUNT=$((MISMATCH_COUNT+1))
        echo ""
        continue
    fi
    SM_HASH="$(sha256_of_file "$SM_FILE")"

    # VM — 두 후보 경로 탐색
    VM_FILE="$TMPDIR_LOCAL/vm-$LABEL"
    if ! fetch_vm_env "$VM_BASENAME" "$VM_FILE"; then
        echo "  vm    : (not found in ${VM_CANDIDATE_DIRS[*]})"
        echo "  STATUS: FAIL VM 파일 없음"
        MISMATCH_COUNT=$((MISMATCH_COUNT+1))
        echo ""
        continue
    fi
    echo "  vm    : $VM_NAME:$VM_FOUND_PATH"
    VM_HASH="$(sha256_of_file "$VM_FILE")"

    echo "  local sha256: ${LOCAL_HASH:0:12}..."
    echo "  sm    sha256: ${SM_HASH:0:12}..."
    echo "  vm    sha256: ${VM_HASH:0:12}..."

    if [ "$LOCAL_HASH" = "$SM_HASH" ] && [ "$SM_HASH" = "$VM_HASH" ]; then
        echo "  STATUS: OK (3-way match)"
        OK_COUNT=$((OK_COUNT+1))
    else
        echo "  STATUS: MISMATCH"
        if [ "$LOCAL_HASH" != "$SM_HASH" ]; then
            print_key_diff "local" "$LOCAL_PATH" "sm" "$SM_FILE"
        fi
        if [ "$SM_HASH" != "$VM_HASH" ]; then
            print_key_diff "sm" "$SM_FILE" "vm" "$VM_FILE"
        fi
        if [ "$LOCAL_HASH" != "$VM_HASH" ] && [ "$LOCAL_HASH" = "$SM_HASH" ]; then
            print_key_diff "local" "$LOCAL_PATH" "vm" "$VM_FILE"
        fi
        MISMATCH_COUNT=$((MISMATCH_COUNT+1))
    fi
    echo ""
done

# dashboard.env 는 Secret Manager에 없음 — 로컬 .env 와만 대비 (경고 레벨)
echo "[dashboard.env] (Secret Manager 미등록, 로컬 .env와 key-level 비교)"
DASH_VM_FILE="$TMPDIR_LOCAL/vm-dashboard"
DASH_CMD='for d in /home/kasa /home/2rami; do f="$d/dashboard.env"; if sudo test -f "$f"; then sudo cat "$f"; exit 0; fi; done; exit 1'
if gcloud compute ssh "$VM_NAME" --zone="$ZONE" --project="$PROJECT_ID" \
        --ssh-flag="-o ConnectTimeout=${SSH_TIMEOUT}" \
        --command="$DASH_CMD" \
        > "$DASH_VM_FILE" 2>/dev/null && [ -s "$DASH_VM_FILE" ]; then
    if [ -f ".env" ]; then
        # dashboard.env 는 .env 의 서브셋이 보통. 공통 키 값 일치만 확인.
        MISSING_OR_DIFF=0
        while IFS= read -r line; do
            key="${line%%=*}"
            val="${line#*=}"
            [ -z "$key" ] && continue
            if grep -q "^${key}=" .env 2>/dev/null; then
                local_val="$(grep "^${key}=" .env | head -1 | cut -d= -f2-)"
                if [ "$local_val" != "$val" ]; then
                    echo "  WARN: 키 '$key' 값 불일치 (local .env vs VM dashboard.env)"
                    MISSING_OR_DIFF=$((MISSING_OR_DIFF+1))
                fi
            fi
        done < <(grep -Ev '^[[:space:]]*(#|$)' "$DASH_VM_FILE")
        if [ "$MISSING_OR_DIFF" -eq 0 ]; then
            echo "  OK: dashboard.env 공통 키 전부 local .env와 일치"
        else
            echo "  WARN: dashboard.env $MISSING_OR_DIFF 개 키 값이 local .env와 다름 (경고만, exit 영향 없음)"
        fi
    else
        echo "  SKIP: 로컬 .env 없음 — 비교 불가"
    fi
else
    echo "  SKIP: VM dashboard.env 접근 실패 또는 파일 없음"
fi
echo ""

echo "==== 요약 ===="
echo "OK       : $OK_COUNT / ${#SETS[@]}"
echo "MISMATCH : $MISMATCH_COUNT"
if [ "$MISMATCH_COUNT" -gt 0 ]; then
    echo ""
    echo "조치:"
    echo "  - 로컬 → Secret Manager: ./scripts/sync_env.sh push"
    echo "  - Secret Manager → 로컬: ./scripts/sync_env.sh pull"
    echo "  - VM 동기화: VM에서 sync_env.sh pull 또는 수동 scp"
    exit 1
fi
exit 0

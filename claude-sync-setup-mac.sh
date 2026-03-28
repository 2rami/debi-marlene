#!/bin/bash
# Claude Code 설정 동기화 - Mac 셋업 스크립트
# Google Drive 데스크톱 앱 설치 + Windows 셋업 완료 후 실행
#
# 사용법: bash scripts/claude-sync-setup-mac.sh

set -e

# === 경로 설정 ===
# Google Drive 경로 자동 탐색
GDRIVE_BASE="$HOME/Library/CloudStorage"
GDRIVE=$(find "$GDRIVE_BASE" -maxdepth 1 -name "GoogleDrive-*" -type d 2>/dev/null | head -1)

if [ -n "$GDRIVE" ]; then
    GDRIVE="$GDRIVE/My Drive"
else
    # 폴백: 직접 경로
    GDRIVE="$HOME/Google Drive/My Drive"
fi

SYNC_DIR="$GDRIVE/claude-sync"
CLAUDE_DIR="$HOME/.claude"

# Mac에서의 프로젝트 폴더명 (Claude Code가 자동으로 만드는 이름)
MAC_PROJECT_NAME="Users-kasa-Desktop-momewomo-debi-marlene"
MAC_PROJECT_DIR="$CLAUDE_DIR/projects/$MAC_PROJECT_NAME"

# Google Drive 확인
if [ ! -d "$SYNC_DIR" ]; then
    echo "[오류] 동기화 폴더를 찾을 수 없음: $SYNC_DIR"
    echo ""
    echo "확인사항:"
    echo "  1. Google Drive 데스크톱 앱이 설치 + 로그인 되어있는지"
    echo "  2. Windows에서 먼저 셋업 스크립트를 실행했는지"
    echo "  3. Google Drive 동기화가 완료됐는지"
    echo ""
    echo "Google Drive 경로가 다르면 스크립트의 GDRIVE 변수를 수정하세요."
    exit 1
fi

echo "=== Claude Code 동기화 셋업 (Mac) ==="
echo "Google Drive: $GDRIVE"
echo "동기화 폴더: $SYNC_DIR"
echo ""

# === 1. ~/.claude 디렉토리 확인 ===
mkdir -p "$CLAUDE_DIR/projects"
mkdir -p "$CLAUDE_DIR/agents"

# === 2. 글로벌 CLAUDE.md 연결 ===
if [ -f "$SYNC_DIR/global/CLAUDE.md" ]; then
    # 기존 파일 백업
    if [ -f "$CLAUDE_DIR/CLAUDE.md" ] && [ ! -L "$CLAUDE_DIR/CLAUDE.md" ]; then
        mv "$CLAUDE_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md.bak"
        echo "[백업] 기존 CLAUDE.md -> CLAUDE.md.bak"
    fi
    ln -sf "$SYNC_DIR/global/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    echo "[연결] CLAUDE.md <- Google Drive"
else
    echo "[스킵] CLAUDE.md (Google Drive에 없음)"
fi

# === 3. 에이전트/스킬 연결 ===
if [ -d "$SYNC_DIR/agents/skills" ]; then
    if [ -d "$CLAUDE_DIR/agents/skills" ] && [ ! -L "$CLAUDE_DIR/agents/skills" ]; then
        mv "$CLAUDE_DIR/agents/skills" "$CLAUDE_DIR/agents/skills.bak"
        echo "[백업] 기존 agents/skills -> skills.bak"
    fi
    ln -sf "$SYNC_DIR/agents/skills" "$CLAUDE_DIR/agents/skills"
    echo "[연결] agents/skills <- Google Drive"
else
    echo "[스킵] agents/skills (Google Drive에 없음)"
fi

# === 4. 프로젝트 대화 기록 연결 ===
# 핵심: Mac 경로명으로 symlink -> Google Drive의 공유 폴더
if [ -d "$SYNC_DIR/projects/debi-marlene" ]; then
    if [ -d "$MAC_PROJECT_DIR" ] && [ ! -L "$MAC_PROJECT_DIR" ]; then
        mv "$MAC_PROJECT_DIR" "${MAC_PROJECT_DIR}.bak"
        echo "[백업] 기존 프로젝트 폴더 -> .bak"
    fi
    ln -sf "$SYNC_DIR/projects/debi-marlene" "$MAC_PROJECT_DIR"
    echo "[연결] 프로젝트 대화 기록 <- Google Drive"
    echo "  $MAC_PROJECT_DIR -> $SYNC_DIR/projects/debi-marlene"
else
    echo "[스킵] 프로젝트 폴더 (Google Drive에 없음 - Windows 셋업 먼저 실행)"
fi

echo ""
echo "=== 완료 ==="
echo ""
echo "이제 맥북에서 Claude Code를 열고 /resume 하면"
echo "윈도우에서 했던 대화가 보입니다!"
echo ""
echo "=== 추가 설정 ==="
echo ""
echo "settings.json은 OS별 경로가 달라서 동기화하지 않습니다."
echo "맥북용 settings.json을 별도로 설정하세요:"
echo "  claude config"
echo ""
echo "플러그인도 맥북에서 별도 설치 필요:"
echo "  claude plugins install context7"
echo "  claude plugins install frontend-design"
echo "  등등..."

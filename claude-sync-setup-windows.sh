#!/bin/bash
# Claude Code 설정 동기화 - Windows 셋업 스크립트
# Google Drive 데스크톱 앱 설치 후 실행
#
# 사용법: bash scripts/claude-sync-setup-windows.sh

set -e

# === 경로 설정 ===
GDRIVE="/g/My Drive"  # Google Drive 기본 마운트 (변경 시 수정)
SYNC_DIR="$GDRIVE/claude-sync"
CLAUDE_DIR="$HOME/.claude"
PROJECT_DIR="$CLAUDE_DIR/projects/c--Users-2rami-Desktop-KASA-debi-marlene"

# Google Drive 확인
if [ ! -d "$GDRIVE" ]; then
    echo "[오류] Google Drive 경로를 찾을 수 없음: $GDRIVE"
    echo "Google Drive 앱 설치 후 마운트 경로를 확인하고 GDRIVE 변수를 수정하세요."
    exit 1
fi

echo "=== Claude Code 동기화 셋업 (Windows) ==="
echo "Google Drive: $GDRIVE"
echo "동기화 폴더: $SYNC_DIR"
echo ""

# === 1. Google Drive에 동기화 폴더 생성 ===
mkdir -p "$SYNC_DIR/projects/debi-marlene"
mkdir -p "$SYNC_DIR/global"
mkdir -p "$SYNC_DIR/agents"

# === 2. 글로벌 CLAUDE.md 이동 ===
if [ -f "$CLAUDE_DIR/CLAUDE.md" ] && [ ! -L "$CLAUDE_DIR/CLAUDE.md" ]; then
    echo "[이동] CLAUDE.md -> Google Drive"
    cp "$CLAUDE_DIR/CLAUDE.md" "$SYNC_DIR/global/CLAUDE.md"
    rm "$CLAUDE_DIR/CLAUDE.md"
    ln -s "$SYNC_DIR/global/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
else
    echo "[스킵] CLAUDE.md (이미 symlink이거나 없음)"
fi

# === 3. 에이전트/스킬 이동 ===
if [ -d "$CLAUDE_DIR/agents/skills" ] && [ ! -L "$CLAUDE_DIR/agents/skills" ]; then
    echo "[이동] agents/skills -> Google Drive"
    cp -r "$CLAUDE_DIR/agents/skills" "$SYNC_DIR/agents/skills"
    rm -rf "$CLAUDE_DIR/agents/skills"
    ln -s "$SYNC_DIR/agents/skills" "$CLAUDE_DIR/agents/skills"
else
    echo "[스킵] agents/skills (이미 symlink이거나 없음)"
fi

# === 4. 프로젝트 대화 기록 + 메모리 이동 ===
if [ -d "$PROJECT_DIR" ] && [ ! -L "$PROJECT_DIR" ]; then
    echo "[이동] 프로젝트 대화 기록 (363MB) -> Google Drive"
    echo "  이 작업은 시간이 걸릴 수 있습니다..."
    cp -r "$PROJECT_DIR/"* "$SYNC_DIR/projects/debi-marlene/" 2>/dev/null || true
    rm -rf "$PROJECT_DIR"
    ln -s "$SYNC_DIR/projects/debi-marlene" "$PROJECT_DIR"
else
    echo "[스킵] 프로젝트 폴더 (이미 symlink이거나 없음)"
fi

echo ""
echo "=== 완료 ==="
echo ""
echo "Google Drive 동기화 폴더 구조:"
echo "  $SYNC_DIR/"
echo "    global/CLAUDE.md          <- 글로벌 설정"
echo "    agents/skills/            <- 커스텀 스킬"
echo "    projects/debi-marlene/    <- 대화 기록 + 메모리"
echo ""
echo "다음 단계: 맥북에서 claude-sync-setup-mac.sh 실행"

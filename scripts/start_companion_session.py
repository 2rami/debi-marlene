"""거노 companion agent 새 세션 자동 생성.

매번 Console 에서 Title/Agent/Env/Vault/Resources 입력하기 귀찮을 때 한 줄로 끝.

사용:
    python3 scripts/start_companion_session.py
    python3 scripts/start_companion_session.py --title "Drive 메모리 검색 테스트"

전제:
    .env 에 다음 키 존재:
      ANTHROPIC_API_KEY (또는 CLAUDE_API_KEY)
      MANAGED_COMPANION_AGENT_ID
      MANAGED_COMPANION_ENV_ID
"""

import argparse
import os
import sys
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent
BETA_HEADER = "managed-agents-2026-04-01"

# 거노 Vault 와 gws creds file. 한 번 셋업한 ID 그대로 재사용.
VAULT_DISPLAY_NAME = "guno-personal"
GWS_CREDS_FILE_ID = "file_011CaUhHddd8vsQghcwJb6Uo"
GWS_CREDS_MOUNT = "/mnt/session/uploads/gws-credentials.json"


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main():
    parser = argparse.ArgumentParser(description="companion 세션 한 방 생성")
    parser.add_argument("--title", default=None, help="세션 제목 (생략 시 timestamp)")
    args = parser.parse_args()

    _load_env(ROOT / ".env")

    api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    agent_id = os.getenv("MANAGED_COMPANION_AGENT_ID")
    env_id = os.getenv("MANAGED_COMPANION_ENV_ID")
    if not all([api_key, agent_id, env_id]):
        print("ERROR: .env 에 ANTHROPIC_API_KEY / MANAGED_COMPANION_AGENT_ID / MANAGED_COMPANION_ENV_ID 필요")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Vault id 조회 (display_name 매칭)
    vault_id = None
    for v in client.beta.vaults.list(extra_headers={"anthropic-beta": BETA_HEADER}):
        if getattr(v, "display_name", None) == VAULT_DISPLAY_NAME:
            vault_id = v.id
            break
    if not vault_id:
        print(f"WARN: Vault '{VAULT_DISPLAY_NAME}' 없음 — GitHub MCP 인증 안 될 수 있음")

    title = args.title or "companion (auto)"

    session = client.beta.sessions.create(
        title=title,
        agent={"type": "agent", "id": agent_id},
        environment_id=env_id,
        vault_ids=[vault_id] if vault_id else [],
        resources=[{
            "type": "file",
            "file_id": GWS_CREDS_FILE_ID,
            "mount_path": GWS_CREDS_MOUNT,
        }],
        extra_headers={"anthropic-beta": BETA_HEADER},
    )

    print(f"session_id : {session.id}")
    print(f"title      : {getattr(session, 'title', '?')}")
    print(f"console URL: https://console.anthropic.com/managed-agents/sessions/{session.id}")


if __name__ == "__main__":
    main()

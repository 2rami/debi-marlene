"""세션 재사용 검증 — 같은 session_id로 두 번 메시지 보냈을 때 컨텍스트 자동 유지되는지 확인.

사용법:
    python3 scripts/verify_session_reuse.py

필요 환경변수: CLAUDE_API_KEY, MANAGED_ENV_ID, MANAGED_AGENT_ID

결과:
    "WORKS"  → plan 그대로 진행 (영속 세션 + turn 50 archive→재생성)
    "BROKEN" → plan 수정 필요 (history 인라인 패턴 유지)

비용: 약 $0.01 (Claude Haiku 4.5, 짧은 메시지 2개)
"""

import asyncio
import os
import sys
from pathlib import Path

import anthropic


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env(Path(__file__).resolve().parent.parent / ".env")

API_KEY = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
ENV_ID = os.getenv("MANAGED_ENV_ID")
AGENT_ID = os.getenv("MANAGED_AGENT_ID")


async def send_and_collect(client, session_id, text):
    response_parts: list[str] = []
    stream_ctx = await client.beta.sessions.events.stream(session_id=session_id)
    async with stream_ctx as stream:
        await client.beta.sessions.events.send(
            session_id=session_id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": text}]}],
        )
        async for event in stream:
            ev_type = getattr(event, "type", None)
            if ev_type == "agent.message":
                for block in getattr(event, "content", []):
                    if getattr(block, "type", None) == "text":
                        response_parts.append(block.text)
            elif ev_type == "session.status_idle":
                stop_reason = getattr(event, "stop_reason", None)
                stop_type = getattr(stop_reason, "type", None) if stop_reason else None
                if stop_type != "requires_action":
                    break
            elif ev_type == "session.status_terminated":
                break
    return "".join(response_parts).strip()


async def main():
    if not (API_KEY and ENV_ID and AGENT_ID):
        print("ERROR: .env에 CLAUDE_API_KEY, MANAGED_ENV_ID, MANAGED_AGENT_ID 모두 필요")
        sys.exit(1)

    client = anthropic.AsyncAnthropic(api_key=API_KEY)

    print("=" * 60)
    print("Managed Agents 세션 재사용 검증")
    print("=" * 60)
    print()
    print("[1] 세션 생성 중...")
    session = await client.beta.sessions.create(
        agent=AGENT_ID,
        environment_id=ENV_ID,
        title="verify-session-reuse",
    )
    print(f"    session_id: {session.id}")
    print()

    print("[2] 첫 메시지: '내 이름은 거노야. 기억해.'")
    reply1 = await send_and_collect(client, session.id, "내 이름은 거노야. 기억해.")
    print(f"    응답: {reply1[:200]}")
    print()

    print("[3] 같은 세션에 두 번째 메시지: '내 이름이 뭐였지?'")
    reply2 = await send_and_collect(client, session.id, "내 이름이 뭐였지?")
    print(f"    응답: {reply2[:200]}")
    print()

    print("[4] 세션 archive 정리...")
    try:
        await client.beta.sessions.archive(session_id=session.id)
        print("    OK")
    except Exception as e:
        print(f"    archive 실패 (무시): {e}")
    print()

    print("=" * 60)
    if "거노" in reply2:
        print("RESULT: WORKS — 컨텍스트 자동 유지됨")
        print("        plan 그대로 진행 가능 (영속 세션 + turn 50 archive→재생성)")
    else:
        print("RESULT: BROKEN — 컨텍스트 안 이어짐")
        print("        plan 수정 필요 — history 인라인 패턴 유지")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

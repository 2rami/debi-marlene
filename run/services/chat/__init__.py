"""챗 서비스 진입점.

CHAT_BACKEND 환경변수로 3종 백엔드 선택:
    CHAT_BACKEND=modal    → Modal Gemma4 LoRA (기본값, LangGraph 파이프라인)
    CHAT_BACKEND=agent    → Claude Haiku 4.5 + Tool Use (봇 프로세스에서 loop)
    CHAT_BACKEND=managed  → Anthropic Managed Agents (Anthropic 서버가 loop)

Managed 사용 전 사전 작업:
    python3 scripts/setup_managed_agent.py   # 한 번만 실행해서 ID 발급
    # 출력된 MANAGED_ENV_ID, MANAGED_AGENT_ID를 .env에 저장
"""

import os

from .chat_client import ChatClient

__all__ = ["ChatClient", "get_chat_client"]


def get_chat_client():
    """CHAT_BACKEND 환경변수에 따라 적절한 클라이언트 인스턴스 반환.

    세 클라이언트 모두 동일한 `chat(message, history, context)` 인터페이스 구현.
    Modal은 `build_chat_agent(client)`로 LangGraph에 주입,
    Agent/Managed는 자체 에이전트 루프로 실행 (LangGraph 우회).
    """
    backend = os.getenv("CHAT_BACKEND", "modal").lower()
    if backend == "managed":
        from .managed_agents_client import ManagedAgentsClient
        return ManagedAgentsClient()
    if backend == "agent":
        from .claude_agent_client import ClaudeAgentClient
        return ClaudeAgentClient()
    return ChatClient()

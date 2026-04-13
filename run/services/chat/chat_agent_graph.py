"""LangGraph StateGraph for the keyword-triggered character chat flow.

The graph encapsulates the "information gathering + LLM call" portion of
`ChatCog._respond`, leaving Discord-specific side effects (typing indicators,
reply, V2 container posting) in the cog itself.

Flow:
    START
      ↓
    classify_intent   (cheap regex, 0 cost)
      ↓ conditional
    ┌─┴─┐
    ↓   ↓
  fetch_patchnote   skip_patchnote
    ↓   ↓
    └─┬─┘
      ↓
    fetch_memory      (GCS user corrections)
      ↓
    call_llm          (Modal Gemma4 LoRA via ChatClient)
      ↓
     END

Benefit over the previous linear flow: patchnote RAG is only called when the
user message contains patch-related keywords. Casual greetings skip the network
hop entirely, saving ~100~300ms per message.

Mermaid diagram can be regenerated via::

    from run.services.chat.chat_agent_graph import build_chat_agent
    from run.services.chat.chat_client import ChatClient
    graph = build_chat_agent(ChatClient())
    print(graph.get_graph().draw_mermaid())
"""

from __future__ import annotations

import re
import time
from typing import Any, Optional, TypedDict

from langgraph.graph import END, StateGraph

from .chat_client import ChatClient
from .chat_memory import get_corrections_prompt
from .patchnote_search import get_patch_context


# 패치/밸런스 관련 키워드. 정규식이라 LLM 호출 없이 0.1ms 내 분류 가능.
PATCH_KEYWORDS = re.compile(
    r"(패치|너프|버프|변경|밸런스|조정|상향|하향|OP|약해졌|강해졌|새\s*스킬|업데이트|노트)"
)


class ChatAgentState(TypedDict, total=False):
    # 입력
    user_message: str
    history: list[dict[str, str]]

    # 중간 상태 (노드들이 채움)
    intent: str
    patch_context: Optional[str]
    patch_info: Optional[dict[str, Any]]
    corrections: Optional[str]
    full_context: Optional[str]

    # 출력
    response: Optional[str]
    elapsed: float


# ────────────── Nodes ──────────────

async def classify_intent(state: ChatAgentState) -> dict:
    """규칙 기반 의도 분류. patch vs general."""
    msg = state["user_message"]
    intent = "patch" if PATCH_KEYWORDS.search(msg) else "general"
    return {"intent": intent}


async def fetch_patchnote(state: ChatAgentState) -> dict:
    """패치노트 RAG. intent == patch 일 때만 실행됨."""
    try:
        context, info = await get_patch_context(state["user_message"])
        return {"patch_context": context, "patch_info": info}
    except Exception:
        return {"patch_context": None, "patch_info": None}


async def skip_patchnote(state: ChatAgentState) -> dict:
    """잡담 intent일 때 RAG 건너뜀. 네트워크 비용 0."""
    return {"patch_context": None, "patch_info": None}


async def fetch_memory(state: ChatAgentState) -> dict:
    """GCS에서 사용자별 수정사항 로드 + 최종 컨텍스트 조립."""
    corrections = get_corrections_prompt()
    base = state.get("patch_context") or ""
    combined = base + (corrections or "")
    return {
        "corrections": corrections or None,
        "full_context": combined or None,
    }


def make_call_llm(client: ChatClient):
    """ChatClient 의존성을 주입받는 노드 팩토리."""

    async def call_llm(state: ChatAgentState) -> dict:
        t0 = time.time()
        response = await client.chat(
            state["user_message"],
            state.get("history", []),
            state.get("full_context"),
        )
        return {"response": response, "elapsed": time.time() - t0}

    return call_llm


# ────────────── Router ──────────────

def route_by_intent(state: ChatAgentState) -> str:
    """classify_intent 결과에 따라 다음 노드 선택."""
    return "fetch_patchnote" if state.get("intent") == "patch" else "skip_patchnote"


# ────────────── Graph builder ──────────────

def build_chat_agent(client: ChatClient):
    """chat_client를 주입받아 compile된 StateGraph 앱을 반환."""
    graph = StateGraph(ChatAgentState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("fetch_patchnote", fetch_patchnote)
    graph.add_node("skip_patchnote", skip_patchnote)
    graph.add_node("fetch_memory", fetch_memory)
    graph.add_node("call_llm", make_call_llm(client))

    graph.set_entry_point("classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "fetch_patchnote": "fetch_patchnote",
            "skip_patchnote": "skip_patchnote",
        },
    )
    graph.add_edge("fetch_patchnote", "fetch_memory")
    graph.add_edge("skip_patchnote", "fetch_memory")
    graph.add_edge("fetch_memory", "call_llm")
    graph.add_edge("call_llm", END)

    return graph.compile()

"""Claude Tool Use 기반 자율 판단형 챗 클라이언트 (에이전트 모드).

기존 LangGraph 구조(개발자가 경로 설계)와 대비되는 패턴 —
Claude가 유저 메시지를 보고 어떤 도구(패치노트 / 전적 조회)를 호출할지 스스로 결정.

수동 에이전트 루프:
1. Claude.messages.create(tools=...)
2. stop_reason == "tool_use"면 → 도구 실행 → 결과를 messages에 append → 다시 호출
3. stop_reason == "end_turn"면 → 최종 응답 반환

매 호출마다 `self.last_trace`에 결정 과정을 기록 (Phase 3 대시보드 시각화용).
"""

import json
import logging
from typing import Any, Optional

import anthropic

from .character_prompt import build_messages, build_system_blocks
from .claude_chat_client import ClaudeChatClient

logger = logging.getLogger(__name__)

# 도구 정의 — Claude가 보는 메타데이터.
# description을 잘 써야 Claude가 언제 쓸지 정확히 판단함.
TOOLS = [
    {
        "name": "search_patchnote",
        "description": (
            "이터널 리턴 최신 패치노트에서 특정 캐릭터나 키워드 관련 변경사항을 검색. "
            "유저가 '패치', '너프', '버프', '밸런스', '조정', '상향/하향' 같은 단어를 쓰거나 "
            "캐릭터 이름과 함께 '바뀐 거', '변경', '최근 패치' 같은 질문을 할 때 사용."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "캐릭터명이나 검색 키워드가 포함된 원본 메시지",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_player_stats",
        "description": (
            "이터널 리턴 플레이어의 현재 시즌 전적/통계/MMR을 dak.gg API에서 조회. "
            "유저가 특정 닉네임의 전적, 랭크, MMR, 승률, 주캐릭터 등을 물을 때 사용."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "nickname": {
                    "type": "string",
                    "description": "이터널 리턴 게임 닉네임 (한글/영문)",
                }
            },
            "required": ["nickname"],
        },
    },
]

MAX_TURNS = 5  # 무한루프 방지


class ClaudeAgentClient(ClaudeChatClient):
    """Tool Use를 지원하는 자율 판단형 Claude 클라이언트.

    `ClaudeChatClient`를 상속받아 `chat()` 만 오버라이드.
    `self.last_trace`에 실행 로그 저장 (대시보드 시각화용).
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key=api_key, model=model)
        self.last_trace: list[dict] = []

    async def chat(
        self,
        message: str,
        history: Optional[list] = None,
        context: Optional[str] = None,
        **_kwargs,
    ) -> Optional[str]:
        """에이전트 루프: Claude가 직접 도구 호출 여부/종류를 판단.

        **_kwargs: Managed Agents 전용 인자(discord_channel) 무시.
        """
        self.last_trace = []
        messages = build_messages(message, history)
        system = build_system_blocks(context)

        for turn in range(MAX_TURNS):
            try:
                response = await self._client.messages.create(
                    model=self._model,
                    max_tokens=1024,
                    system=system,
                    tools=TOOLS,
                    messages=messages,
                )
            except anthropic.APIError as e:
                logger.error("Claude API 에러 (에이전트 루프 turn %s): %s", turn, e)
                self.last_trace.append({"turn": turn, "type": "error", "detail": str(e)})
                return None

            # 토큰 usage 로깅
            usage = getattr(response, "usage", None)
            if usage:
                logger.info(
                    "Agent turn %s usage: in=%s cache_read=%s out=%s stop=%s",
                    turn,
                    getattr(usage, "input_tokens", "?"),
                    getattr(usage, "cache_read_input_tokens", 0),
                    getattr(usage, "output_tokens", "?"),
                    response.stop_reason,
                )

            if response.stop_reason == "end_turn":
                # Claude가 도구 없이 바로 답함 or 도구 결과 본 뒤 최종 답
                final_text = next(
                    (b.text for b in response.content if getattr(b, "type", None) == "text"),
                    None,
                )
                self.last_trace.append({"turn": turn, "type": "final_response", "text": final_text})
                return final_text

            if response.stop_reason != "tool_use":
                logger.warning("예기치 못한 stop_reason: %s", response.stop_reason)
                return None

            # Claude가 도구 호출을 원함 — 실행 + 결과 피드백
            tool_use_blocks = [
                b for b in response.content if getattr(b, "type", None) == "tool_use"
            ]
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_block in tool_use_blocks:
                tool_name = tool_block.name
                tool_input = tool_block.input
                self.last_trace.append({
                    "turn": turn,
                    "type": "tool_call",
                    "tool": tool_name,
                    "input": tool_input,
                })
                result = await self._execute_tool(tool_name, tool_input)
                self.last_trace.append({
                    "turn": turn,
                    "type": "tool_result",
                    "tool": tool_name,
                    "result_preview": str(result)[:200],
                })
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result if isinstance(result, str) else json.dumps(result, ensure_ascii=False),
                })

            messages.append({"role": "user", "content": tool_results})

        logger.warning("에이전트 루프가 MAX_TURNS(%s) 도달", MAX_TURNS)
        self.last_trace.append({"type": "max_turns_reached"})
        return None

    async def _execute_tool(self, name: str, tool_input: dict) -> Any:
        """도구 이름 → 실제 함수 호출."""
        try:
            if name == "search_patchnote":
                from .patchnote_search import get_patch_context
                query = tool_input.get("query", "")
                context, _info = await get_patch_context(query)
                return context or "관련 패치노트 항목을 찾지 못함."

            if name == "search_player_stats":
                from run.services.eternal_return.api_client import get_player_basic_data
                nickname = tool_input.get("nickname", "")
                data = await get_player_basic_data(nickname)
                if not data:
                    return f"'{nickname}' 플레이어를 찾을 수 없음."
                return self._summarize_player_data(data)

            return f"알 수 없는 도구: {name}"
        except Exception as e:
            logger.error("도구 %s 실행 실패: %s", name, e)
            return f"도구 실행 중 에러: {e}"

    def _summarize_player_data(self, data: dict) -> str:
        """Claude에게 넘길 플레이어 데이터 요약 (토큰 절약)."""
        nickname = data.get("nickname", "?")
        stats = data.get("stats", {})
        mmr = stats.get("mmr") or data.get("mmr")
        tier = data.get("tier") or stats.get("tier")
        win_rate = stats.get("winRate") or stats.get("win_rate")
        top1 = stats.get("top1") or stats.get("first") or stats.get("wins")
        top3 = stats.get("top3") or stats.get("top3Rate")
        total_games = stats.get("total") or stats.get("totalGames") or stats.get("games")
        most_char = (stats.get("most") or stats.get("mainCharacter")
                     or (stats.get("topCharacters", [{}])[0].get("name") if stats.get("topCharacters") else None))

        parts = [f"닉네임: {nickname}"]
        if mmr is not None:
            parts.append(f"MMR: {mmr}")
        if tier:
            parts.append(f"티어: {tier}")
        if win_rate is not None:
            parts.append(f"승률: {win_rate}%")
        if top1 is not None:
            parts.append(f"1등 횟수: {top1}")
        if top3 is not None:
            parts.append(f"TOP3율: {top3}%")
        if total_games is not None:
            parts.append(f"총 게임: {total_games}")
        if most_char:
            parts.append(f"주캐릭터: {most_char}")
        return " / ".join(parts)

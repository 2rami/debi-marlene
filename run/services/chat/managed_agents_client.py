"""Anthropic Managed Agents 기반 챗 클라이언트 (beta managed-agents-2026-04-01).

기존 Tool Use 패턴(ClaudeAgentClient)과 대비:
- Tool Use: 내 봇 프로세스에서 agent loop 직접 돌림 (manual while loop)
- Managed Agents: Anthropic 서버에서 agent loop 돌아감. 봇은 session 열고 이벤트 스트림 받아서
  custom_tool_use 이벤트 오면 호스트 측에서 실행하고 결과 보내는 역할만.

ONE-TIME SETUP (scripts/setup_managed_agent.py로 이미 실행):
    MANAGED_ENV_ID=env_...
    MANAGED_AGENT_ID=agent_...
    MANAGED_AGENT_VERSION=...

매 요청 (this file):
    1. sessions.create(agent=AGENT_ID, environment_id=ENV_ID)
    2. 스트림 open (stream-first 원칙 — skill의 Pattern 7)
    3. user.message 전송
    4. 이벤트 루프:
       - agent.message → 응답 텍스트 수집
       - agent.custom_tool_use → 호스트에서 실행 → user.custom_tool_result 전송
       - session.status_idle (stop_reason != "requires_action") → break
       - session.status_terminated → break
    5. 세션 archive (cleanup)
"""

import asyncio
import logging
import os
from typing import Any, Optional

import anthropic

logger = logging.getLogger(__name__)


class ManagedAgentsClient:
    """Managed Agents 세션 기반 클라이언트.

    ChatClient/ClaudeChatClient와 동일한 `chat(message, history, context)` 인터페이스.
    `self.last_trace`에 에이전트 판단 과정 기록 (면접 시연·대시보드 시각화용).
    """

    def __init__(self):
        api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "CLAUDE_API_KEY (or ANTHROPIC_API_KEY) 환경변수가 필요해."
            )
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

        self._agent_id = os.getenv("MANAGED_AGENT_ID")
        self._env_id = os.getenv("MANAGED_ENV_ID")
        if not self._agent_id or not self._env_id:
            raise RuntimeError(
                "MANAGED_AGENT_ID와 MANAGED_ENV_ID가 .env에 설정돼야 해.\n"
                "먼저 `python3 scripts/setup_managed_agent.py` 실행해서 ID 받아와."
            )

        self.last_trace: list[dict] = []

    async def chat(
        self,
        message: str,
        history: Optional[list] = None,
        context: Optional[str] = None,
        discord_channel: Optional[Any] = None,
        **_kwargs,
    ) -> Optional[str]:
        """Managed Agents 세션 1회 실행 후 데비&마를렌 응답 반환.

        discord_channel 이 있으면 search_player_stats 툴 호출 시
        해당 채널에 StatsLayoutView 임베드를 직접 전송.
        """
        self.last_trace = []
        # _execute_tool에서 접근할 수 있게 인스턴스 변수로 임시 저장
        self._current_channel = discord_channel

        # 1. 세션 생성 — agent는 미리 만들어진 ID 참조만 (절대 여기서 agents.create 호출 X)
        try:
            session = await self._client.beta.sessions.create(
                agent=self._agent_id,
                environment_id=self._env_id,
                title=f"chat-{message[:30]}",
            )
        except anthropic.APIError as e:
            logger.error("Managed Agents 세션 생성 실패: %s", e)
            return None

        self.last_trace.append({"type": "session_created", "session_id": session.id})
        logger.info("Managed session 생성: %s", session.id)

        # 맥락이 있으면 유저 메시지 앞에 붙임 (히스토리는 세션이 자동 누적 안 해주므로 포함)
        user_text = message
        if context:
            user_text = f"[참고 컨텍스트]\n{context}\n\n[유저 메시지]\n{message}"

        agent_text_parts: list[str] = []
        pending_tool_calls: list[dict] = []
        final_reached = False

        try:
            # 2. Stream-first: 스트림 먼저 열고 메시지 전송 (skill Pattern 7)
            # AsyncAnthropic의 events.stream()은 coroutine을 반환 → await로 풀고 context manager로 사용
            stream_ctx = await self._client.beta.sessions.events.stream(
                session_id=session.id
            )
            async with stream_ctx as stream:
                await self._client.beta.sessions.events.send(
                    session_id=session.id,
                    events=[
                        {
                            "type": "user.message",
                            "content": [{"type": "text", "text": user_text}],
                        }
                    ],
                )

                # 3. 이벤트 루프
                async for event in stream:
                    ev_type = getattr(event, "type", None)

                    if ev_type == "agent.message":
                        for block in getattr(event, "content", []):
                            if getattr(block, "type", None) == "text":
                                agent_text_parts.append(block.text)

                    elif ev_type == "agent.custom_tool_use":
                        tool_name = getattr(event, "name", None) or getattr(
                            event, "tool_name", None
                        )
                        tool_input = getattr(event, "input", {}) or {}
                        tool_event_id = event.id
                        self.last_trace.append(
                            {
                                "type": "tool_call",
                                "tool": tool_name,
                                "input": tool_input,
                            }
                        )
                        pending_tool_calls.append(
                            {
                                "id": tool_event_id,
                                "name": tool_name,
                                "input": tool_input,
                            }
                        )

                    elif ev_type == "session.status_terminated":
                        logger.warning("Session 비정상 종료")
                        break

                    elif ev_type == "session.status_idle":
                        # skill Pattern 5: idle 만으로 break X. stop_reason 확인.
                        stop_reason = getattr(event, "stop_reason", None)
                        stop_type = getattr(stop_reason, "type", None) if stop_reason else None

                        if stop_type == "requires_action":
                            # 도구 결과 대기 중 — 실행 후 결과 전송
                            if pending_tool_calls:
                                results = []
                                for call in pending_tool_calls:
                                    result_text = await self._execute_tool(
                                        call["name"], call["input"]
                                    )
                                    self.last_trace.append(
                                        {
                                            "type": "tool_result",
                                            "tool": call["name"],
                                            "result_preview": str(result_text)[:200],
                                        }
                                    )
                                    results.append(
                                        {
                                            "type": "user.custom_tool_result",
                                            "custom_tool_use_id": call["id"],
                                            "content": [
                                                {"type": "text", "text": result_text}
                                            ],
                                        }
                                    )
                                await self._client.beta.sessions.events.send(
                                    session_id=session.id,
                                    events=results,
                                )
                                pending_tool_calls = []
                            continue  # 루프 유지 — agent가 도구 결과 받고 마저 응답할 것

                        # end_turn, retries_exhausted → 종료
                        final_reached = True
                        break

        except anthropic.APIError as e:
            logger.error("Managed agent stream 에러: %s", e)
            self.last_trace.append({"type": "error", "detail": str(e)})
            return None

        # 4. 세션 정리 — race 방지 폴링 후 archive
        asyncio.create_task(self._cleanup_session(session.id))

        final_text = "".join(agent_text_parts).strip()
        self.last_trace.append(
            {"type": "final", "text_length": len(final_text), "reached": final_reached}
        )
        return final_text if final_text else None

    async def _cleanup_session(self, session_id: str) -> None:
        """세션 archive — idle 직후 상태 write race가 있어서 약간 폴링 후 시도."""
        try:
            for _ in range(5):
                s = await self._client.beta.sessions.retrieve(session_id=session_id)
                if getattr(s, "status", None) != "running":
                    break
                await asyncio.sleep(0.3)
            await self._client.beta.sessions.archive(session_id=session_id)
        except Exception as e:
            logger.debug("Session cleanup 실패 (무시): %s", e)

    async def _execute_tool(self, name: str, tool_input: dict) -> str:
        """도구 이름 → 실제 함수 호출. Tool Use 버전과 동일 로직."""
        try:
            if name == "search_patchnote":
                from .patchnote_search import get_patch_context
                query = tool_input.get("query", "")
                context, _info = await get_patch_context(query)
                return context or "관련 패치노트 항목을 찾지 못함."

            if name == "search_player_stats":
                from run.services.eternal_return.api_client import (
                    get_player_basic_data,
                    get_player_played_seasons,
                )
                import asyncio
                nickname = tool_input.get("nickname", "")
                data, played_seasons = await asyncio.gather(
                    get_player_basic_data(nickname),
                    get_player_played_seasons(nickname),
                    return_exceptions=True,
                )
                if isinstance(data, Exception) or not data:
                    return f"'{nickname}' 플레이어를 찾을 수 없음."
                if isinstance(played_seasons, Exception):
                    played_seasons = []

                # Discord 채널이 있으면 네이티브 /전적 Layout을 직접 전송
                channel = getattr(self, "_current_channel", None)
                if channel is not None:
                    try:
                        from run.views.stats_view import StatsLayoutView
                        view = StatsLayoutView(data, played_seasons)
                        await channel.send(view=view)
                        logger.info("StatsLayoutView 전송 완료: %s", nickname)
                    except Exception as e:
                        logger.warning("StatsLayoutView 전송 실패: %s", e)

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
        total_games = stats.get("total") or stats.get("totalGames") or stats.get("games")

        parts = [f"닉네임: {nickname}"]
        if mmr is not None:
            parts.append(f"MMR: {mmr}")
        if tier:
            parts.append(f"티어: {tier}")
        if win_rate is not None:
            parts.append(f"승률: {win_rate}%")
        if top1 is not None:
            parts.append(f"1등 횟수: {top1}")
        if total_games is not None:
            parts.append(f"총 게임: {total_games}")
        return " / ".join(parts)

    async def health_check(self) -> bool:
        return bool(self._agent_id and self._env_id)

    async def close(self) -> None:
        return None

"""Anthropic Managed Agents 기반 챗 클라이언트 (beta managed-agents-2026-04-01).

세션 재사용 패턴 (2026-04-20 리팩):
- (guild_id, user_id) → session_id를 SQLite에 영속 매핑
- 매 요청마다 새 session 만들지 않고 기존 session 재사용 → Anthropic이 컨텍스트 자동 유지
- turn 50 또는 6시간 idle 시 자동 회전 (요약→archive→새 세션 + summary inject)
- history 인자는 호환용으로 받기만 함 (Modal 폴백용). Managed 모드에선 무시.

매 요청 흐름:
    1. session_store.get_or_rotate_session() → session_id, optional summary
    2. user_text 빌드 (context + summary + 메시지)
    3. events.stream 열고 events.send 보내기
    4. 이벤트 루프 (agent.message / custom_tool_use / status_idle)
    5. session_store.bump_turn() → 다음 회전 트리거
"""

import asyncio
import logging
import os
import time
from typing import Any, Optional

import anthropic

from run.services.memory import session_store

logger = logging.getLogger(__name__)


class ManagedAgentsClient:
    """Managed Agents 세션 재사용 기반 클라이언트.

    `chat(message, history, context, discord_channel, guild_id, user_id)` 인터페이스.
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

        print(
            f"[CHAT] backend=managed agent={self._agent_id[:20]}... env={self._env_id[:20]}...",
            flush=True,
        )

        self.last_trace: list[dict] = []

    async def chat(
        self,
        message: str,
        history: Optional[list] = None,
        context: Optional[str] = None,
        discord_channel: Optional[Any] = None,
        guild_id: Optional[Any] = None,
        user_id: Optional[Any] = None,
        **_kwargs,
    ) -> Optional[str]:
        """세션 재사용 기반 응답. history는 호환용 (Managed 모드는 무시 — 세션이 자동 유지)."""
        self.last_trace = []
        self._current_channel = discord_channel
        self._current_guild_id = guild_id
        self._current_user_id = user_id

        try:
            session_id, summary = await session_store.get_or_rotate_session(
                guild_id, user_id,
                create_fn=self._create_session,
                archive_fn=self._archive_session,
                summarize_fn=self._summarize_session,
            )
        except anthropic.APIError as e:
            logger.error("session 매핑 실패: %s", e)
            return None

        self.last_trace.append({
            "type": "session_acquired",
            "session_id": session_id,
            "rotated": summary is not None,
        })
        if summary:
            logger.info("session 회전 직후 — summary inject (%d chars)", len(summary))

        parts = []
        if context:
            parts.append(f"[참고 컨텍스트]\n{context}")
        if summary:
            parts.append(f"[이전 대화 요약 — 컨텍스트 복원용]\n{summary}")
        parts.append(f"[지금 질문]\n{message}")
        user_text = "\n\n".join(parts)

        try:
            response = await self._send_and_collect(session_id, user_text)
        except anthropic.APIError as e:
            logger.error("session stream 에러 (session=%s): %s", session_id, e)
            self.last_trace.append({"type": "error", "detail": str(e)})
            return None

        session_store.bump_turn(guild_id, user_id)

        self.last_trace.append({
            "type": "final",
            "text_length": len(response or ""),
            "session_id": session_id,
        })
        return response

    # ─────────── session_store 콜백들 ───────────

    async def _create_session(self) -> str:
        session = await self._client.beta.sessions.create(
            agent=self._agent_id,
            environment_id=self._env_id,
            title=f"chat-{int(time.time())}",
        )
        logger.info("Managed session 생성: %s", session.id)
        return session.id

    async def _archive_session(self, session_id: str) -> None:
        # idle/status write race 회피 — 잠깐 폴링 후 archive
        for _ in range(5):
            try:
                s = await self._client.beta.sessions.retrieve(session_id=session_id)
                if getattr(s, "status", None) != "running":
                    break
            except Exception:
                break
            await asyncio.sleep(0.3)
        await self._client.beta.sessions.archive(session_id=session_id)
        logger.info("Managed session archive: %s", session_id)

    async def _summarize_session(self, session_id: str) -> str:
        """archive 직전 세션에 요약 요청 보내고 응답 받기. 다음 세션 prefix로 사용."""
        summary = await self._send_and_collect(
            session_id,
            "(시스템 요청) 지금까지 이 유저와의 대화 핵심을 3~5줄로 요약해줘. "
            "캐릭터 페르소나 묘사는 빼고 사실만 (유저 닉네임/캐릭터/관심사/언급한 게임 정보 등). "
            "다음 세션에서 이 요약을 보고 자연스럽게 이어가야 해.",
        )
        return summary or ""

    # ─────────── 공통 send/stream 루프 ───────────

    async def _send_and_collect(self, session_id: str, user_text: str) -> Optional[str]:
        """user_text 보내고 응답 텍스트 모아서 반환. custom tool round-trip 포함."""
        agent_text_parts: list[str] = []
        pending_tool_calls: list[dict] = []

        stream_ctx = await self._client.beta.sessions.events.stream(session_id=session_id)
        async with stream_ctx as stream:
            await self._client.beta.sessions.events.send(
                session_id=session_id,
                events=[
                    {
                        "type": "user.message",
                        "content": [{"type": "text", "text": user_text}],
                    }
                ],
            )

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
                    self.last_trace.append({
                        "type": "tool_call",
                        "tool": tool_name,
                        "input": tool_input,
                    })
                    pending_tool_calls.append({
                        "id": tool_event_id,
                        "name": tool_name,
                        "input": tool_input,
                    })

                elif ev_type == "session.status_terminated":
                    logger.warning("Session 비정상 종료: %s", session_id)
                    break

                elif ev_type == "session.status_idle":
                    stop_reason = getattr(event, "stop_reason", None)
                    stop_type = getattr(stop_reason, "type", None) if stop_reason else None

                    if stop_type == "requires_action":
                        if pending_tool_calls:
                            results = []
                            for call in pending_tool_calls:
                                result_text = await self._execute_tool(
                                    call["name"], call["input"]
                                )
                                self.last_trace.append({
                                    "type": "tool_result",
                                    "tool": call["name"],
                                    "result_preview": str(result_text)[:200],
                                })
                                results.append({
                                    "type": "user.custom_tool_result",
                                    "custom_tool_use_id": call["id"],
                                    "content": [{"type": "text", "text": result_text}],
                                })
                            await self._client.beta.sessions.events.send(
                                session_id=session_id,
                                events=results,
                            )
                            pending_tool_calls = []
                        continue

                    break

        text = "".join(agent_text_parts).strip()
        return text if text else None

    # ─────────── 도구 실행 (기존 그대로) ───────────

    async def _execute_tool(self, name: str, tool_input: dict) -> str:
        try:
            if name == "search_patchnote":
                from .patchnote_search import get_patch_context
                query = tool_input.get("query", "")
                context, _info = await get_patch_context(query)
                return context or "관련 패치노트 항목을 찾지 못함."

            if name == "remember_about_user":
                fact = (tool_input.get("fact") or "").strip()
                if not fact:
                    return "저장할 내용이 비어있어."
                from .chat_memory import add_correction
                add_correction(fact, guild_id=self._current_guild_id)
                return f"OK 기억함: {fact[:80]}"

            if name == "recall_about_user":
                from .chat_memory import get_corrections_prompt
                prompt_text = get_corrections_prompt(self._current_guild_id)
                if not prompt_text.strip():
                    return "저장된 정보 없음. 유저가 알려준 게 아직 없어."
                return prompt_text.strip()

            if name == "forget_about_user":
                fact = (tool_input.get("fact") or "").strip()
                if not fact:
                    return "삭제할 내용을 명시해."
                from run.services.memory.db import connect
                scope = str(self._current_guild_id) if self._current_guild_id else "dm"
                with connect() as conn:
                    cur = conn.execute(
                        "DELETE FROM corrections WHERE guild_id=? AND text=?",
                        (scope, fact),
                    )
                    deleted = cur.rowcount
                return f"OK 잊었어 ({deleted}개 삭제)" if deleted else "그런 내용 저장된 적 없음"

            if name == "get_conversation_stats":
                import time
                from run.services.memory import session_store
                sess = session_store.get_session(self._current_guild_id, self._current_user_id)
                if not sess:
                    return "세션 정보 없음 (방금 시작)"
                last_active_min = int((time.time() - sess["last_active"]) / 60)
                return (
                    f"턴 수: {sess['turn_count']} / "
                    f"마지막 활동: {last_active_min}분 전 / "
                    f"session_id: {sess['session_id']}"
                )

            if name == "reset_my_memory":
                # corrections는 guild 단위(공용)라 안 건드림. 세션만 reset → 컨텍스트 새로 시작.
                from run.services.memory import session_store
                session_store.delete_session(self._current_guild_id, self._current_user_id)
                return "OK 세션 메모리 초기화. 다음 메시지부터 컨텍스트 새로 시작."

            if name == "search_player_stats":
                from run.services.eternal_return.api_client import (
                    get_player_basic_data,
                    get_player_played_seasons,
                )
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

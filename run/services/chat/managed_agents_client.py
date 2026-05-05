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

from run.core import config as bot_config
from run.services.chat.persona import extract_persona_response
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

        self._identity = bot_config.BOT_IDENTITY

        # identity별 agent/env 라우팅.
        # - debi/marlene 솔로봇: 전용 agent (페르소나만 생성 → 체감 속도 2배, 토큰 절약)
        # - unified(기본): 기존 쌍둥이 agent (데비+마를렌 동시 생성)
        # env는 unified와 공유 기본값, 필요 시 identity별 env 오버라이드.
        if self._identity == "debi":
            self._agent_id = os.getenv("MANAGED_AGENT_ID_DEBI")
            self._env_id = os.getenv("MANAGED_ENV_ID_DEBI") or os.getenv("MANAGED_ENV_ID")
            id_env_name = "MANAGED_AGENT_ID_DEBI"
        elif self._identity == "marlene":
            self._agent_id = os.getenv("MANAGED_AGENT_ID_MARLENE")
            self._env_id = os.getenv("MANAGED_ENV_ID_MARLENE") or os.getenv("MANAGED_ENV_ID")
            id_env_name = "MANAGED_AGENT_ID_MARLENE"
        else:  # unified (기존봇)
            self._agent_id = os.getenv("MANAGED_AGENT_ID")
            self._env_id = os.getenv("MANAGED_ENV_ID")
            id_env_name = "MANAGED_AGENT_ID"

        if not self._agent_id or not self._env_id:
            raise RuntimeError(
                f"{id_env_name}와 MANAGED_ENV_ID가 .env에 설정돼야 해.\n"
                "unified: `python3 scripts/setup_managed_agent.py` 로 기존 agent ID.\n"
                "solo: `python3 scripts/create_solo_agents.py --apply` 로 Debi/Marlene agent 생성."
            )

        print(
            f"[CHAT] backend=managed identity={self._identity} agent={self._agent_id[:20]}... env={self._env_id[:20]}...",
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
            parts.append(
                "[동작 규칙]\n"
                "아래 [참고 컨텍스트]는 너희 둘이 이미 알고 있는 정보야. "
                "톤은 평소처럼 츤츤대고 장난쳐도 좋은데, 핵심 정보는 반드시 답변에 포함해. "
                '"모른다 / 정보 없다 / 또 같은 거 물어보네" 같은 회피·생략 금지. '
                "정보 먼저 짧게 전달한 뒤에 캐릭터 코멘트 붙이는 식으로."
            )
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

        # 솔로봇(BOT_IDENTITY='debi'/'marlene')은 자기 페르소나 대사만 추출해서 전송.
        # unified는 원본 그대로 (기존봇 동작 유지).
        if response and self._identity in ("debi", "marlene"):
            response = extract_persona_response(response, self._identity)

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
                add_correction(
                    fact,
                    guild_id=self._current_guild_id,
                    user_id=self._current_user_id,
                )
                return f"OK 기억함: {fact[:80]}"

            if name == "recall_about_user":
                from .chat_memory import get_corrections_prompt
                prompt_text = get_corrections_prompt(
                    self._current_guild_id,
                    self._current_user_id,
                )
                if not prompt_text.strip():
                    return "저장된 정보 없음. 유저가 알려준 게 아직 없어."
                return prompt_text.strip()

            if name == "forget_about_user":
                fact = (tool_input.get("fact") or "").strip()
                if not fact:
                    return "삭제할 내용을 명시해."
                from run.services.memory.db import connect
                from .chat_memory import _scope
                g, u = _scope(self._current_guild_id, self._current_user_id)
                with connect() as conn:
                    cur = conn.execute(
                        "DELETE FROM corrections WHERE guild_id=? AND user_id=? AND text=?",
                        (g, u, fact),
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
                from run.services.memory import session_store
                from .chat_memory import clear_corrections
                session_store.delete_session(self._current_guild_id, self._current_user_id)
                wiped = clear_corrections(self._current_guild_id, self._current_user_id)
                return (
                    f"OK 전부 초기화했어 (세션 + 저장된 기억 {wiped}개). "
                    "다음 메시지부터 너 관련 정보는 아무것도 몰라."
                )

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

            if name == "get_character_stats":
                from run.services.eternal_return.api_client import get_character_stats
                period = int(tool_input.get("period", 7) or 7)
                stats_data = await get_character_stats(dt=period, team_mode="SQUAD", tier="diamond_plus")
                if not stats_data:
                    return "캐릭터 통계 데이터를 가져오지 못함."

                channel = getattr(self, "_current_channel", None)
                if channel is not None:
                    try:
                        from run.views.character_view import CharacterStatsView
                        view = CharacterStatsView(stats_data, period=period)
                        await channel.send(view=view)
                        logger.info("CharacterStatsView 전송 완료 (period=%d)", period)
                    except Exception as e:
                        logger.warning("CharacterStatsView 전송 실패: %s", e)

                return self._summarize_character_stats(stats_data, period)

            if name == "get_season_info":
                from run.services.eternal_return.api_client import get_current_season_info
                info = get_current_season_info()
                season_name = info.get("name", "알 수 없음")
                day = info.get("day", 0)
                start_date = info.get("start_date")

                channel = getattr(self, "_current_channel", None)
                if channel is not None:
                    try:
                        import discord
                        desc_lines = [f"**{season_name}**"]
                        if day > 0:
                            desc_lines[0] += f" | {day}일차"
                        if start_date:
                            desc_lines.append(f"시작일: {start_date.strftime('%Y.%m.%d')}")
                        embed = discord.Embed(
                            title="이터널 리턴 시즌 정보",
                            description="\n".join(desc_lines),
                            color=0x4A90D9,
                        )
                        embed.set_thumbnail(
                            url="https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1049590/fa56f360467f675b777dd18a6315f00c84a7b9c4/header.jpg"
                        )
                        await channel.send(embed=embed)
                    except Exception as e:
                        logger.warning("시즌 Embed 전송 실패: %s", e)

                summary = f"현재 시즌: {season_name}"
                if day > 0:
                    summary += f" ({day}일차)"
                return summary

            if name == "get_online_players":
                import aiohttp
                STEAM_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=1049590"
                count = None
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(STEAM_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                            if resp.status == 200:
                                d = await resp.json()
                                if d.get("response", {}).get("result") == 1:
                                    count = d["response"]["player_count"]
                except Exception as e:
                    logger.warning("Steam API 호출 실패: %s", e)

                if count is None:
                    return "동접자 수를 가져오지 못함 (Steam API 오류)."

                channel = getattr(self, "_current_channel", None)
                if channel is not None:
                    try:
                        import discord
                        embed = discord.Embed(
                            title="이터널 리턴 동접자",
                            description=f"현재 **{count:,}**명이 플레이 중",
                            color=0x1B2838,
                        )
                        embed.set_thumbnail(
                            url="https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1049590/fa56f360467f675b777dd18a6315f00c84a7b9c4/header.jpg"
                        )
                        embed.set_footer(text="Steam 기준")
                        await channel.send(embed=embed)
                    except Exception as e:
                        logger.warning("동접 Embed 전송 실패: %s", e)

                return f"현재 동접자 {count:,}명 (Steam 기준)"

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

    def _summarize_character_stats(self, stats_data: dict, period: int) -> str:
        from run.services.eternal_return.api_client import game_data
        raw = stats_data.get("characterStatSnapshot", {}).get("characterStats", []) or []
        total_games_all = sum(c.get("count", 0) for c in raw)

        processed = []
        for c in raw:
            char_id = c.get("key", 0)
            games = c.get("count", 0)
            weapons = c.get("weaponStats", []) or []
            if weapons:
                wins = sum(w.get("win", 0) for w in weapons)
                wgames = sum(w.get("count", 0) for w in weapons)
                win_rate = (wins / wgames * 100) if wgames else 0
                tier_score = weapons[0].get("tierScore", 0)
            else:
                win_rate, tier_score = 0, 0
            pick_rate = (games / total_games_all * 100) if total_games_all else 0
            processed.append({
                "name": game_data.get_character_name(char_id) or f"#{char_id}",
                "win_rate": win_rate,
                "pick_rate": pick_rate,
                "tier_score": tier_score,
                "games": games,
            })

        processed.sort(key=lambda x: x["tier_score"], reverse=True)
        top = processed[:5]
        if not top:
            return f"최근 {period}일 캐릭터 통계 없음."

        lines = [f"최근 {period}일 다이아+ 티어순 상위 5:"]
        for i, c in enumerate(top, 1):
            lines.append(
                f"{i}. {c['name']} — 승률 {c['win_rate']:.1f}% / 픽률 {c['pick_rate']:.1f}%"
            )
        return "\n".join(lines)

    async def health_check(self) -> bool:
        return bool(self._agent_id and self._env_id)

    async def close(self) -> None:
        return None

"""거노 personal Discord 비서 봇 (companion-bot).

흐름:
    거노가 봇한테 DM 보냄
    → on_message 핸들러
    → owner 체크 (다른 사용자 메시지는 무시)
    → companion Managed Agent session 생성/재사용
    → events.send 로 user.message 보내고 events.stream 으로 응답 수신
    → DM 채널에 답장 (2000자 chunk 분할)

세션 관리:
    - per-user 세션 캐시 (이번 봇은 owner만 응답하니까 사실 1개)
    - 마지막 메시지 30분 후 자동 archive + 다음 메시지 시 새 세션
    - "/reset" 메시지면 즉시 archive + 새 세션

배포:
    - 작은 Python 컨테이너 (~150MB)
    - 같은 봇 VM에 docker-compose 로 옆에 띄움
    - debi-marlene 캐릭터 봇과 정체성 분리

전제 (env):
    COMPANION_BOT_TOKEN          # 새 봇 Discord token
    OWNER_ID                      # 거노 user id
    ANTHROPIC_API_KEY (or CLAUDE_API_KEY)
    MANAGED_COMPANION_AGENT_ID
    MANAGED_COMPANION_ENV_ID
    COMPANION_VAULT_ID            # vlt_011CaUeUYv5EUX5pAr7qZt4D (guno-personal)
    GWS_CREDS_FILE_ID             # file_011CaUhHddd8vsQghcwJb6Uo
    GCP_SA_FILE_ID                # file_011CaWSBEqH1pxdj3VykpyPt
    GH_BINARY_FILE_ID             # file_011CaXnuMf3ky51YLD8i9miY (gh 2.92.0 linux amd64)
    GH_TOKEN_FILE_ID              # file_011CaXnuEE4GRU2tXvzncY2v (PAT — github-pat-companion)
"""

from __future__ import annotations

import asyncio
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic
import discord
from anthropic import AsyncAnthropic
from discord import app_commands

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

BETA_HEADER = "managed-agents-2026-04-01"
TYPING_REFRESH_INTERVAL = 8     # discord typing indicator 8초마다 새로
DM_CHUNK_SIZE = 1900            # discord 메시지 2000자 제한 (여유 100자)
RESPONSE_TIMEOUT = 600          # agent 응답 최대 600초 (10분) — Firestore/GCP 도구 다중 호출 + cold-start 모두 흡수
SESSION_DB_PATH = os.getenv("SESSION_DB_PATH", "/data/companion_sessions.db")


def _env(*keys: str) -> str:
    """여러 키 후보 중 하나 찾기 — fallback."""
    for k in keys:
        v = os.getenv(k)
        if v:
            return v
    raise RuntimeError(f"환경변수 필요: {keys}")


# ─────────── Anthropic session helper ───────────

class CompanionClient:
    """1 user → 1 영구 세션. SQLite 에 매핑 영속 저장 (봇 재시작/컨테이너 교체에도 유지)."""

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        env_id: str,
        vault_id: Optional[str],
        gws_file_id: Optional[str],
        gcp_sa_file_id: Optional[str] = None,
        gh_binary_file_id: Optional[str] = None,
        gh_token_file_id: Optional[str] = None,
    ):
        self.client = AsyncAnthropic(api_key=api_key)
        self.agent_id = agent_id
        self.env_id = env_id
        self.vault_id = vault_id
        self.gws_file_id = gws_file_id
        self.gcp_sa_file_id = gcp_sa_file_id
        self.gh_binary_file_id = gh_binary_file_id
        self.gh_token_file_id = gh_token_file_id
        # /debug 용 런타임 상태
        self._last_msg_at: dict[int, float] = {}
        self._inflight: set[int] = set()
        # 디버그 모드 ON 인 user_id 집합 — Managed Agents 콘솔의 Debug 탭처럼
        # send_and_collect 가 받는 모든 이벤트(tool_use/thinking/error 등) 를 채팅에 송출
        self._debug_users: set[int] = set()
        self._db_path = Path(SESSION_DB_PATH)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS sessions (user_id INTEGER PRIMARY KEY, session_id TEXT NOT NULL)")
            conn.commit()

    def _db_get(self, user_id: int) -> Optional[str]:
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute("SELECT session_id FROM sessions WHERE user_id=?", (user_id,)).fetchone()
            return row[0] if row else None

    def _db_set(self, user_id: int, session_id: str) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO sessions(user_id, session_id) VALUES (?, ?)", (user_id, session_id))
            conn.commit()

    def _db_delete(self, user_id: int) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
            conn.commit()

    async def _create_session(self, user_id: int, title: str = "DM") -> str:
        resources = []
        if self.gws_file_id:
            resources.append({
                "type": "file",
                "file_id": self.gws_file_id,
                "mount_path": "/mnt/session/uploads/gws-credentials.json",
            })
        if self.gcp_sa_file_id:
            resources.append({
                "type": "file",
                "file_id": self.gcp_sa_file_id,
                "mount_path": "/mnt/session/uploads/gcp-sa.json",
            })
        if self.gh_binary_file_id:
            resources.append({
                "type": "file",
                "file_id": self.gh_binary_file_id,
                "mount_path": "/mnt/session/uploads/gh.tar.gz",
            })
        if self.gh_token_file_id:
            resources.append({
                "type": "file",
                "file_id": self.gh_token_file_id,
                "mount_path": "/mnt/session/uploads/gh-token.txt",
            })
        s = await self.client.beta.sessions.create(
            title=f"discord-dm:{user_id}:{title}",
            agent={"type": "agent", "id": self.agent_id},
            environment_id=self.env_id,
            vault_ids=[self.vault_id] if self.vault_id else [],
            resources=resources,
            extra_headers={"anthropic-beta": BETA_HEADER},
        )
        logger.info(f"new session for user {user_id}: {s.id}")
        return s.id

    async def reset(self, user_id: int) -> None:
        old_sid = self._db_get(user_id)
        if old_sid:
            self._db_delete(user_id)
            try:
                await self.client.beta.sessions.archive(
                    session_id=old_sid,
                    extra_headers={"anthropic-beta": BETA_HEADER},
                )
                logger.info(f"archived session {old_sid}")
            except Exception as e:
                logger.warning(f"archive 실패: {e}")

    async def get_session_id(self, user_id: int) -> str:
        sid = self._db_get(user_id)
        if sid:
            return sid
        sid = await self._create_session(user_id)
        self._db_set(user_id, sid)
        return sid

    def is_debug(self, user_id: int) -> bool:
        return user_id in self._debug_users

    def toggle_debug(self, user_id: int) -> bool:
        """디버그 모드 토글. 새 상태(ON=True / OFF=False) 반환."""
        if user_id in self._debug_users:
            self._debug_users.discard(user_id)
            return False
        self._debug_users.add(user_id)
        return True

    def debug_status(self, user_id: int) -> str:
        """현재 디버그 + 세션 상태 한 줄 요약 (토글 결과 메시지에 첨부)."""
        sid = self._db_get(user_id)
        last = self._last_msg_at.get(user_id)
        last_str = datetime.fromtimestamp(last).isoformat(sep=" ", timespec="seconds") if last else "(없음)"
        on = "ON" if user_id in self._debug_users else "OFF"
        return (
            "```\n"
            f"debug        : {on}\n"
            f"session_id   : {sid or '(없음)'}\n"
            f"agent_id     : {self.agent_id}\n"
            f"env_id       : {self.env_id}\n"
            f"gh_binary    : {self.gh_binary_file_id or '-'}\n"
            f"gh_token     : {self.gh_token_file_id or '-'}\n"
            f"timeout      : {RESPONSE_TIMEOUT}s\n"
            f"last_msg_at  : {last_str}\n"
            f"discord.py   : {discord.__version__}  anthropic: {anthropic.__version__}  python: {sys.version.split()[0]}\n"
            "```"
        )

    async def send_and_collect(self, user_id: int, text: str, event_callback=None) -> str:
        """user 메시지 보내고 agent 텍스트 응답 모아 반환. RESPONSE_TIMEOUT 초 timeout.

        event_callback: 선택. async callable(event) — Anthropic 세션 이벤트 받을 때마다 호출.
        디버그 모드 ON 일 때 채팅에 이벤트 송출하는 용도.
        """
        session_id = await self.get_session_id(user_id)
        agent_text_parts: list[str] = []
        self._last_msg_at[user_id] = time.time()
        self._inflight.add(user_id)

        async def _run():
            stream_ctx = await self.client.beta.sessions.events.stream(session_id=session_id)
            async with stream_ctx as stream:
                await self.client.beta.sessions.events.send(
                    session_id=session_id,
                    events=[{
                        "type": "user.message",
                        "content": [{"type": "text", "text": text}],
                    }],
                    extra_headers={"anthropic-beta": BETA_HEADER},
                )
                async for event in stream:
                    ev_type = getattr(event, "type", None)
                    if event_callback is not None:
                        try:
                            await event_callback(event)
                        except Exception:
                            logger.exception("event_callback 실패 (debug relay)")
                    if ev_type == "agent.message":
                        for block in getattr(event, "content", []):
                            if getattr(block, "type", None) == "text":
                                agent_text_parts.append(block.text)
                    elif ev_type == "session.status_idle":
                        stop_reason = getattr(event, "stop_reason", None)
                        stop_type = getattr(stop_reason, "type", None) if stop_reason else None
                        if stop_type == "end_turn":
                            return
                        if stop_type == "requires_action":
                            # agent_toolset / mcp_toolset 은 Anthropic 측에서 자동 처리.
                            # custom_tool 가 없으니 여기 안 옴. 혹시 오면 그냥 종료.
                            logger.warning("requires_action 발생 — custom tool 없음, 무시")
                            return
                    elif ev_type == "session.status_terminated":
                        logger.warning(f"session {session_id} 비정상 종료")
                        return

        try:
            await asyncio.wait_for(_run(), timeout=RESPONSE_TIMEOUT)
        except asyncio.TimeoutError:
            logger.warning(f"response timeout {RESPONSE_TIMEOUT}s")
            return "(응답 타임아웃 — 무거운 도구 호출 중일 수도 있음. 다시 물어봐)"
        finally:
            self._inflight.discard(user_id)

        return "".join(agent_text_parts).strip() or "(응답 비었음)"


# ─────────── Discord bot ───────────

def chunk_message(text: str, size: int = DM_CHUNK_SIZE) -> list[str]:
    """2000자 제한 회피 — 줄 단위 분할 우선, 안 되면 강제."""
    if len(text) <= size:
        return [text]
    chunks = []
    cur = []
    cur_len = 0
    for line in text.split("\n"):
        if cur_len + len(line) + 1 > size:
            if cur:
                chunks.append("\n".join(cur))
                cur = []
                cur_len = 0
            while len(line) > size:
                chunks.append(line[:size])
                line = line[size:]
        cur.append(line)
        cur_len += len(line) + 1
    if cur:
        chunks.append("\n".join(cur))
    return chunks


def _trunc(s: str, n: int = 280) -> str:
    s = (s or "").replace("\r", "")
    return s if len(s) <= n else s[:n] + "…"


def format_event(event) -> Optional[str]:
    """Anthropic 세션 이벤트 → Discord 채팅 한 줄. 무관한 이벤트는 None 반환해서 skip."""
    t = getattr(event, "type", None)
    if t == "session.status_running":
        return "▶ running"
    if t == "session.status_rescheduled":
        return "↻ rescheduled (retry)"
    if t == "session.status_idle":
        sr = getattr(event, "stop_reason", None)
        sr_t = getattr(sr, "type", None) if sr else "?"
        return f"■ idle ({sr_t})"
    if t == "session.status_terminated":
        return "✗ terminated"
    if t == "session.error":
        err = getattr(event, "error", None)
        msg = getattr(err, "message", None) if err else "?"
        return f"⚠ error: {_trunc(str(msg), 200)}"
    if t == "agent.thinking":
        return "… thinking"
    if t == "agent.message":
        parts = []
        for block in getattr(event, "content", []) or []:
            if getattr(block, "type", None) == "text":
                parts.append(getattr(block, "text", "") or "")
        body = _trunc("".join(parts), 200)
        return f"→ {body}" if body else None
    if t == "agent.tool_use":
        name = getattr(event, "name", "?")
        inp = getattr(event, "input", None) or {}
        if name == "bash" and isinstance(inp, dict) and "command" in inp:
            return f"$ {_trunc(inp['command'], 320)}"
        try:
            import json as _json
            return f"⚙ {name}({_trunc(_json.dumps(inp, ensure_ascii=False), 280)})"
        except Exception:
            return f"⚙ {name}(…)"
    if t == "agent.tool_result":
        is_err = getattr(event, "is_error", False)
        parts = []
        for block in getattr(event, "content", []) or []:
            if getattr(block, "type", None) == "text":
                parts.append(getattr(block, "text", "") or "")
        body = _trunc("".join(parts), 320)
        return f"{'✗' if is_err else '←'} {body}"
    if t == "agent.mcp_tool_use":
        name = getattr(event, "name", "?")
        srv = getattr(event, "mcp_server_name", "?")
        return f"⚙ mcp[{srv}].{name}"
    if t == "agent.mcp_tool_result":
        is_err = getattr(event, "is_error", False)
        parts = []
        for block in getattr(event, "content", []) or []:
            if getattr(block, "type", None) == "text":
                parts.append(getattr(block, "text", "") or "")
        body = _trunc("".join(parts), 320)
        return f"{'✗' if is_err else '←'} mcp: {body}" if body else "← mcp result"
    if t == "span.model_request_end":
        if getattr(event, "is_error", False):
            return "✗ model_request error"
        usage = getattr(event, "model_usage", None)
        if usage:
            i = getattr(usage, "input_tokens", 0)
            o = getattr(usage, "output_tokens", 0)
            cr = getattr(usage, "cache_read_input_tokens", 0)
            cw = getattr(usage, "cache_creation_input_tokens", 0)
            return f"✓ tokens in={i} out={o} cache_r={cr} cache_w={cw}"
        return None
    return None


class DebugRelay:
    """디버그 이벤트를 Discord 채널로 batched 송출. 1.5초 / 1700자 단위로 flush."""

    def __init__(self, channel: discord.abc.Messageable):
        self.channel = channel
        self._buffer: list[str] = []
        self._buf_len = 0
        self._lock = asyncio.Lock()
        self._timer: Optional[asyncio.Task] = None

    async def push(self, line: str) -> None:
        if not line:
            return
        async with self._lock:
            self._buffer.append(line)
            self._buf_len += len(line) + 1
            if self._buf_len > 1700:
                await self._flush_locked()
            elif self._timer is None or self._timer.done():
                self._timer = asyncio.create_task(self._delayed_flush())

    async def _delayed_flush(self) -> None:
        try:
            await asyncio.sleep(1.5)
        except asyncio.CancelledError:
            return
        async with self._lock:
            await self._flush_locked()

    async def _flush_locked(self) -> None:
        if not self._buffer:
            return
        chunk = "\n".join(self._buffer)
        self._buffer.clear()
        self._buf_len = 0
        chunk = chunk[:1900]
        try:
            await self.channel.send(f"```\n{chunk}\n```")
        except Exception:
            logger.exception("DebugRelay send 실패")

    async def close(self) -> None:
        if self._timer and not self._timer.done():
            self._timer.cancel()
        async with self._lock:
            await self._flush_locked()


class CompanionBot(discord.Client):
    def __init__(self, companion: CompanionClient, owner_id: int):
        intents = discord.Intents.default()
        intents.message_content = True  # DM content 읽으려면 필수
        intents.dm_messages = True
        super().__init__(intents=intents)
        self.companion = companion
        self.owner_id = owner_id
        # User Install 슬래시 명령어 등록용 — 길드 0개라도 DM에서 자동완성 뜨게 하려면 user install
        self.tree = app_commands.CommandTree(self)
        self._register_slash_commands()

    def _register_slash_commands(self):
        # owner 만 사용 가능. integration_types=user_install, contexts=DM/길드/그룹DM 모두
        @self.tree.command(
            name="debug",
            description="디버그 모드 토글 — agent 이벤트(tool_use/thinking/error) 채팅에 표시 (owner only)",
        )
        @app_commands.allowed_installs(guilds=False, users=True)
        @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
        async def debug_cmd(interaction: discord.Interaction):
            if interaction.user.id != self.owner_id:
                await interaction.response.send_message("(owner only)", ephemeral=True)
                return
            new_state = self.companion.toggle_debug(self.owner_id)
            label = "ON — 다음 메시지부터 이벤트 송출" if new_state else "OFF"
            await interaction.response.send_message(
                f"debug {label}\n{self.companion.debug_status(self.owner_id)}",
                ephemeral=True,
            )

        @self.tree.command(name="reset", description="현재 세션 archive + 새 컨텍스트로 (owner only)")
        @app_commands.allowed_installs(guilds=False, users=True)
        @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
        async def reset_cmd(interaction: discord.Interaction):
            if interaction.user.id != self.owner_id:
                await interaction.response.send_message("(owner only)", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True, thinking=True)
            await self.companion.reset(self.owner_id)
            await interaction.followup.send("(세션 리셋. 새 컨텍스트로 시작)", ephemeral=True)

    async def setup_hook(self):
        # 글로벌 sync — user install 명령어는 보통 수 분 안에 propagate
        try:
            synced = await self.tree.sync()
            logger.info(f"slash commands synced: {len(synced)}개 — {[c.name for c in synced]}")
        except Exception:
            logger.exception("tree.sync 실패")

    async def on_ready(self):
        logger.info(f"companion-bot ready as {self.user} (id={self.user.id})")
        # 거노한테 시작 알림 — 매번 보내면 시끄러우니 주석. 필요하면 활성화.
        # owner = await self.fetch_user(self.owner_id)
        # await owner.send("companion-bot 살아남")

    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return
        if not isinstance(msg.channel, discord.DMChannel):
            return  # DM만
        if msg.author.id != self.owner_id:
            logger.info(f"non-owner DM 무시: {msg.author.id}")
            return

        text = msg.content.strip()
        if not text:
            return

        # 명령어 처리
        if text.lower() in ("/reset", "!reset"):
            await self.companion.reset(self.owner_id)
            await msg.channel.send("(세션 리셋. 새 컨텍스트로 시작)")
            return
        if text.lower() in ("/debug", "!debug"):
            new_state = self.companion.toggle_debug(self.owner_id)
            label = "ON — 다음 메시지부터 이벤트 송출" if new_state else "OFF"
            await msg.channel.send(f"debug {label}\n{self.companion.debug_status(self.owner_id)}")
            return

        # typing indicator — discord.py context manager 가 장시간 응답에서 끊기는 케이스가 있어
        # TYPING_REFRESH_INTERVAL 마다 명시적 trigger_typing 으로 갱신하는 백그라운드 태스크로 교체.
        async def _keep_typing():
            try:
                while True:
                    await msg.channel.typing()
                    await asyncio.sleep(TYPING_REFRESH_INTERVAL)
            except asyncio.CancelledError:
                pass

        # 디버그 모드 ON 이면 이벤트 → 채팅 relay 준비
        debug_relay: Optional[DebugRelay] = None
        event_callback = None
        if self.companion.is_debug(self.owner_id):
            debug_relay = DebugRelay(msg.channel)

            async def event_callback(event):
                line = format_event(event)
                if line and debug_relay is not None:
                    await debug_relay.push(line)

        typing_task = asyncio.create_task(_keep_typing())
        try:
            response = await self.companion.send_and_collect(
                self.owner_id, text, event_callback=event_callback
            )
        except Exception as e:
            logger.exception("agent 호출 실패")
            await msg.channel.send(f"(에러) `{type(e).__name__}: {e}`")
            return
        finally:
            typing_task.cancel()
            if debug_relay is not None:
                await debug_relay.close()

        for chunk in chunk_message(response):
            await msg.channel.send(chunk)


def main():
    token = _env("COMPANION_BOT_TOKEN")
    owner_id = int(_env("OWNER_ID"))
    api_key = _env("CLAUDE_API_KEY", "ANTHROPIC_API_KEY")
    agent_id = _env("MANAGED_COMPANION_AGENT_ID")
    env_id = _env("MANAGED_COMPANION_ENV_ID")
    vault_id = os.getenv("COMPANION_VAULT_ID") or "vlt_011CaUeUYv5EUX5pAr7qZt4D"
    gws_file = os.getenv("GWS_CREDS_FILE_ID") or "file_011CaUhHddd8vsQghcwJb6Uo"
    gcp_sa_file = os.getenv("GCP_SA_FILE_ID") or "file_011CaWSBEqH1pxdj3VykpyPt"
    gh_binary_file = os.getenv("GH_BINARY_FILE_ID") or "file_011CaXnuMf3ky51YLD8i9miY"
    gh_token_file = os.getenv("GH_TOKEN_FILE_ID") or "file_011CaXnuEE4GRU2tXvzncY2v"

    companion = CompanionClient(
        api_key=api_key, agent_id=agent_id, env_id=env_id,
        vault_id=vault_id, gws_file_id=gws_file,
        gcp_sa_file_id=gcp_sa_file,
        gh_binary_file_id=gh_binary_file,
        gh_token_file_id=gh_token_file,
    )
    bot = CompanionBot(companion=companion, owner_id=owner_id)

    bot.run(token, log_handler=None)


if __name__ == "__main__":
    main()

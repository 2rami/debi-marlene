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
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Optional

import anthropic
import discord
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

BETA_HEADER = "managed-agents-2026-04-01"
SESSION_IDLE_TIMEOUT = 30 * 60  # 30분 무응답 시 archive
TYPING_REFRESH_INTERVAL = 8     # discord typing indicator 8초마다 새로
DM_CHUNK_SIZE = 1900            # discord 메시지 2000자 제한 (여유 100자)
RESPONSE_TIMEOUT = 90           # agent 응답 최대 90초


def _env(*keys: str) -> str:
    """여러 키 후보 중 하나 찾기 — fallback."""
    for k in keys:
        v = os.getenv(k)
        if v:
            return v
    raise RuntimeError(f"환경변수 필요: {keys}")


# ─────────── Anthropic session helper ───────────

class CompanionClient:
    """1 user → 1 long-lived session 관리. 30분 idle 후 archive."""

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        env_id: str,
        vault_id: Optional[str],
        gws_file_id: Optional[str],
    ):
        self.client = AsyncAnthropic(api_key=api_key)
        self.agent_id = agent_id
        self.env_id = env_id
        self.vault_id = vault_id
        self.gws_file_id = gws_file_id
        self._sessions: dict[int, dict] = {}  # user_id → {session_id, last_used}

    async def _create_session(self, user_id: int, title: str = "DM") -> str:
        resources = []
        if self.gws_file_id:
            resources.append({
                "type": "file",
                "file_id": self.gws_file_id,
                "mount_path": "/mnt/session/uploads/gws-credentials.json",
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
        meta = self._sessions.pop(user_id, None)
        if meta and meta.get("session_id"):
            try:
                await self.client.beta.sessions.archive(
                    session_id=meta["session_id"],
                    extra_headers={"anthropic-beta": BETA_HEADER},
                )
                logger.info(f"archived session {meta['session_id']}")
            except Exception as e:
                logger.warning(f"archive 실패: {e}")

    async def get_session_id(self, user_id: int) -> str:
        meta = self._sessions.get(user_id)
        now = time.time()
        if meta and now - meta["last_used"] < SESSION_IDLE_TIMEOUT:
            meta["last_used"] = now
            return meta["session_id"]
        if meta:
            await self.reset(user_id)
        sid = await self._create_session(user_id)
        self._sessions[user_id] = {"session_id": sid, "last_used": now}
        return sid

    async def send_and_collect(self, user_id: int, text: str) -> str:
        """user 메시지 보내고 agent 텍스트 응답 모아 반환. 90초 timeout."""
        session_id = await self.get_session_id(user_id)
        agent_text_parts: list[str] = []

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


class CompanionBot(discord.Client):
    def __init__(self, companion: CompanionClient, owner_id: int):
        intents = discord.Intents.default()
        intents.message_content = True  # DM content 읽으려면 필수
        intents.dm_messages = True
        super().__init__(intents=intents)
        self.companion = companion
        self.owner_id = owner_id

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

        # 응답 생성 + typing indicator 유지
        async with msg.channel.typing():
            try:
                response = await self.companion.send_and_collect(self.owner_id, text)
            except Exception as e:
                logger.exception("agent 호출 실패")
                await msg.channel.send(f"(에러) `{type(e).__name__}: {e}`")
                return

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

    companion = CompanionClient(
        api_key=api_key, agent_id=agent_id, env_id=env_id,
        vault_id=vault_id, gws_file_id=gws_file,
    )
    bot = CompanionBot(companion=companion, owner_id=owner_id)

    bot.run(token, log_handler=None)


if __name__ == "__main__":
    main()

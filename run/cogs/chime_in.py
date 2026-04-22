"""ChimeInCog — 솔로봇(BOT_IDENTITY='debi'/'marlene')이 다른 봇/유저 대화에 끼어들기.

동작 조건:
    - BOT_IDENTITY가 'debi' 또는 'marlene'인 프로세스에서만 listener 활성화.
    - 유저 메시지가 자기 페르소나를 호명한 경우(ChatCog가 처리)는 스킵.
    - 자기 자신의 메시지는 스킵 (무한 루프 방지).
    - 그 외 (다른 봇 메시지 / 호명 없는 유저 메시지)는 ChimeInDecider로 판단.

Decider 게이트: 쿨다운 → 봇 streak 캡 → 확률 → Claude judge.
통과 시 짧은 한 줄 대사를 채널에 전송.
"""

import logging
import os

import anthropic
import discord
from discord.ext import commands

from run.core import config
from run.services.chat.chime_decider import ChimeInDecider, has_keyword, is_question

logger = logging.getLogger(__name__)

CONTEXT_HISTORY_LIMIT = 5


class ChimeInCog(commands.Cog, name="끼어들기"):
    """솔로봇 전용 끼어들기. unified 모드에서는 no-op."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.identity = config.BOT_IDENTITY
        self.enabled = self.identity in ("debi", "marlene")
        self.decider: ChimeInDecider | None = None

        if not self.enabled:
            return

        api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ChimeInCog: CLAUDE_API_KEY 없음 — 비활성화")
            self.enabled = False
            return

        client = anthropic.AsyncAnthropic(api_key=api_key)
        self.decider = ChimeInDecider(self.identity, client)
        print(f"[CHIME_IN] activated identity={self.identity}", flush=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.enabled or self.decider is None:
            return

        # 자기 자신 메시지 무시 (무한 루프 방지)
        if message.author.id == self.bot.user.id:
            return

        # DM은 chime_in 대상 아님 (그룹 대화가 아니라서)
        if not message.guild:
            return

        # 서버별 대화 토글이 꺼져 있으면 스킵 (ChatCog와 동일 규칙)
        guild_settings = config.load_settings().get("guilds", {}).get(str(message.guild.id), {})
        if not guild_settings.get("chat_enabled", True):
            return

        gid, cid = message.guild.id, message.channel.id
        is_bot = message.author.bot

        if is_bot:
            self.decider.on_bot_message(gid, cid)
        else:
            # 유저 발화 → streak 리셋
            self.decider.on_user_message(gid, cid)

        # 솔로봇은 지정 채널에서만 반응. 비지정 채널은 완전 무반응.
        designated_channels = config.get_solo_chat_channels(gid, self.identity)
        if cid not in designated_channels:
            return

        # 키워드 호명은 ChatCog이 Managed Agent 경유로 처리(tool 사용). chime 스킵.
        # identity별로 분리 — 데비는 데비 호명만, 마를렌은 마를렌 호명만.
        if not is_bot and has_keyword(message.content, self.identity):
            return

        # 질문 vs 일반 채팅
        question_hit = not is_bot and is_question(message.content)

        # 최근 맥락 수집
        recent = await self._collect_context(message)

        # 타이핑 표시 — judge 호출 동안 Discord에 "입력 중..." 표시.
        async with message.channel.typing():
            reply = await self.decider.maybe_chime(
                gid, cid, recent,
                triggering_author=message.author.display_name,
                relaxed=True,
                question_hit=question_hit,
            )
        if reply:
            try:
                await message.channel.send(reply)
                print(f"[CHIME_IN] {self.identity} chimed: {reply[:60]}", flush=True)
            except discord.HTTPException as e:
                logger.warning("chime 전송 실패: %s", e)

    async def _collect_context(self, message: discord.Message) -> list[str]:
        """최근 메시지 N개 수집 (오래된 순). 방금 메시지는 마지막에 포함."""
        lines: list[str] = []
        try:
            async for m in message.channel.history(limit=CONTEXT_HISTORY_LIMIT, before=message):
                speaker = m.author.display_name
                content = (m.content or "").strip()
                if content:
                    lines.append(f"{speaker}: {content}")
        except discord.Forbidden:
            pass
        except Exception as e:
            logger.debug("history 수집 실패 (무시): %s", e)

        lines.reverse()
        # 방금 트리거 메시지
        if message.content:
            lines.append(f"{message.author.display_name}: {message.content.strip()}")
        return lines

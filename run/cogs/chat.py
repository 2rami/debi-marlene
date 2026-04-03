"""
대화 Cog

데비&마를렌 캐릭터 AI 대화: /대화
패치노트 검색 연동: "에이든 패치" -> 자동으로 패치노트 검색 후 답변
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Dict, List
import logging
import time

from run.services.chat import ChatClient
from run.services.chat.patchnote_search import get_patch_context
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

_histories: Dict[str, List[dict]] = {}
MAX_HISTORY = 5


def _history_key(guild_id, user_id: int) -> str:
    return f"{guild_id or 'dm'}:{user_id}"


class ChatCog(commands.Cog, name="대화"):
    """데비&마를렌 AI 대화"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = ChatClient()

    async def cog_unload(self):
        await self.client.close()

    @app_commands.command(name="대화", description="데비&마를렌에게 말 걸기")
    @app_commands.describe(메시지="하고 싶은 말")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def chat(self, interaction: discord.Interaction, 메시지: str):
        try:
            await interaction.response.defer(thinking=True)
        except (discord.errors.NotFound, discord.errors.HTTPException):
            return

        try:
            await log_command_usage("대화", interaction.user.id, interaction.user.display_name)
        except Exception:
            pass

        key = _history_key(interaction.guild_id, interaction.user.id)
        history = _histories.get(key, [])

        # 패치노트 검색 (패치/너프/버프 키워드 감지 시)
        context = None
        try:
            context = await get_patch_context(메시지)
        except Exception as e:
            logger.warning("패치 검색 실패: %s", e)

        t0 = time.time()
        response = await self.client.chat(메시지, history, context)
        elapsed = time.time() - t0

        ctx_tag = " [+patch]" if context else ""
        print(f"[대화] {elapsed:.1f}s{ctx_tag} | Q: {메시지[:30]} | A: {(response or '-')[:40]}", flush=True)

        if not response:
            try:
                await interaction.followup.send(
                    "추론 서버에 연결할 수 없습니다.", ephemeral=True
                )
            except Exception:
                pass
            return

        # 히스토리 저장
        history.append({"user": 메시지, "assistant": response})
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
        _histories[key] = history

        # 응답 전송
        embed = discord.Embed(description=response, color=0x7B68EE)
        # 패치 검색 결과가 있으면 별도 필드로 표시
        if context and ("변경" in context or "하향" in context or "상향" in context):
            # context에서 제목과 내용 분리
            ctx_lines = context.split("\n", 1)
            title = ctx_lines[0] if ctx_lines else ""
            detail = ctx_lines[1] if len(ctx_lines) > 1 else ""
            if detail:
                embed.add_field(
                    name=title,
                    value=detail[:300],
                    inline=False,
                )
        embed.set_footer(text=f"{interaction.user.display_name}: {메시지}")
        try:
            await interaction.followup.send(embed=embed)
        except discord.errors.NotFound:
            logger.warning("interaction 만료됨")
        except Exception as e:
            logger.error("followup 실패: %s", e)

    @app_commands.command(name="대화초기화", description="대화 히스토리 초기화")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def chat_reset(self, interaction: discord.Interaction):
        key = _history_key(interaction.guild_id, interaction.user.id)
        _histories.pop(key, None)
        try:
            await log_command_usage("대화초기화", interaction.user.id, interaction.user.display_name)
        except Exception:
            pass
        await interaction.response.send_message(
            "대화 히스토리가 초기화되었습니다.", ephemeral=True
        )

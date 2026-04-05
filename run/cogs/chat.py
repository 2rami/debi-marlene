"""
대화 Cog

데비&마를렌 캐릭터 AI 대화
키워드 트리거: 데비, 마를렌, 뎁마 등 이름/호칭이 포함된 메시지에 자동 반응
패치노트 검색 연동: "에이든 패치" -> V2 컴포넌트 표시
대화 메모리: 사용자 수정사항을 GCS에 저장하여 학습
"""

import discord
from discord.ext import commands
from typing import Dict, List, Optional
import logging
import re
import time

from run.services.chat import ChatClient
from run.services.chat.patchnote_search import get_patch_context
from run.services.chat.chat_memory import (
    detect_correction, add_correction, get_corrections_prompt,
)
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

_histories: Dict[str, List[dict]] = {}
MAX_HISTORY = 5

# 트리거 키워드: 이름 단독 + 호칭 형태
TRIGGER_WORDS = [
    "데비야", "데비나", "데비아",
    "마를렌아", "마를렌야", "마를렌나",
    "뎁마야", "뎁마아", "뎁마나",
]
TRIGGER_NAMES = ["데비", "마를렌", "뎁마"]

_trigger_pattern = re.compile(
    "|".join(re.escape(w) for w in TRIGGER_WORDS + TRIGGER_NAMES)
)


def _history_key(guild_id, user_id: int) -> str:
    return f"{guild_id or 'dm'}:{user_id}"


def _extract_message(content: str) -> str:
    """트리거 키워드를 제거하고 실제 메시지 부분만 추출"""
    cleaned = content
    for word in TRIGGER_WORDS:
        cleaned = cleaned.replace(word, "", 1)
    for name in TRIGGER_NAMES:
        cleaned = cleaned.replace(name, "", 1)
    cleaned = cleaned.strip()
    cleaned = cleaned.lstrip(",. ").strip()
    return cleaned


def _build_patch_view(patch_info: dict) -> discord.ui.LayoutView:
    """패치 변경사항을 V2 Container로 만들기"""
    view = discord.ui.LayoutView()

    title = patch_info["title"]
    char_name = patch_info["character"]
    changes = patch_info["changes"]

    lines = [f"### {title} - {char_name}"]

    for entry in changes:
        skill = entry["skill"]
        if skill != "기본":
            lines.append(f"\n**{skill}**")
        for change in entry["changes"]:
            tag = _detect_direction(change)
            lines.append(f"- {change}  {tag}")

    text = "\n".join(lines)
    container = discord.ui.Container(
        discord.ui.TextDisplay(text),
        accent_colour=discord.Colour(0x5865F2),
    )
    view.add_item(container)
    return view


def _detect_direction(change_text: str) -> str:
    """수치 변경의 방향 판별"""
    numbers = re.findall(r"([\d.]+)(?:%|초|개)?(?:\s*→\s*)([\d.]+)", change_text)
    if numbers:
        old, new = float(numbers[0][0]), float(numbers[0][1])
        if new > old:
            return "[상향]"
        elif new < old:
            return "[하향]"
    return "[조정]"


class ChatCog(commands.Cog, name="대화"):
    """데비&마를렌 AI 대화"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = ChatClient()

    async def cog_unload(self):
        await self.client.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not _trigger_pattern.search(message.content):
            return

        user_msg = _extract_message(message.content)
        if not user_msg:
            user_msg = message.content

        await self._respond(message, user_msg)

    async def _respond(self, message: discord.Message, user_msg: str):
        """키워드 트리거 응답"""
        guild_id = message.guild.id if message.guild else None

        try:
            await log_command_usage("대화", message.author.id, message.author.display_name)
        except Exception:
            pass

        key = _history_key(guild_id, message.author.id)
        history = _histories.get(key, [])

        # 수정 감지 → 저장
        if detect_correction(user_msg):
            add_correction(user_msg)
            print(f"[메모리] 수정 저장: {user_msg[:50]}", flush=True)

        # 패치노트 검색
        context = None
        patch_info = None
        try:
            context, patch_info = await get_patch_context(user_msg)
        except Exception as e:
            logger.warning("패치 검색 실패: %s", e)

        # 수정사항을 context에 합침 (Modal 서버의 시스템 프롬프트에 반영됨)
        corrections = get_corrections_prompt()
        if corrections:
            context = (context or "") + corrections

        # health check -> 콜드스타트 감지
        loading_msg = None
        is_cold = not await self.client.health_check()
        if is_cold:
            loading_msg = await message.reply("...잠깐만, 아직 덜 일어났어.", mention_author=False)

        # typing 표시 + 추론 요청
        async with message.channel.typing():
            t0 = time.time()
            response = await self.client.chat(user_msg, history, context)
            elapsed = time.time() - t0

        ctx_tag = " [+patch]" if patch_info else ""
        cold_tag = " [cold]" if is_cold else ""
        mem_tag = " [+mem]" if corrections else ""
        print(f"[대화] {elapsed:.1f}s{ctx_tag}{mem_tag}{cold_tag} | Q: {user_msg[:30]} | A: {(response or '-')[:40]}", flush=True)

        if not response:
            fail_text = "...연결이 안 돼."
            if loading_msg:
                await loading_msg.edit(content=fail_text)
            else:
                await message.reply(fail_text, mention_author=False)
            return

        # 히스토리 저장
        history.append({"user": user_msg, "assistant": response})
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
        _histories[key] = history

        # 캐릭터 대사 전송
        if loading_msg:
            await loading_msg.edit(content=response)
        else:
            await message.reply(response, mention_author=False)

        # 패치 변경사항이 있으면 V2 Container 추가 전송
        if patch_info and patch_info.get("changes"):
            try:
                patch_view = _build_patch_view(patch_info)
                await message.channel.send(view=patch_view)
            except Exception as e:
                logger.warning("패치 V2 전송 실패: %s", e)

    @commands.command(name="대화초기화")
    async def chat_reset(self, ctx: commands.Context):
        """대화 히스토리 초기화"""
        key = _history_key(ctx.guild.id if ctx.guild else None, ctx.author.id)
        _histories.pop(key, None)
        try:
            await log_command_usage("대화초기화", ctx.author.id, ctx.author.display_name)
        except Exception:
            pass
        await ctx.reply("대화 히스토리가 초기화되었습니다.", mention_author=False)

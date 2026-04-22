"""
대화 Cog

데비&마를렌 캐릭터 AI 대화.

진입점:
    - unified(기존봇): /대화 슬래시 커맨드만 (이 Cog의 chat_slash)
    - debi/marlene 솔로봇:
      - 지정 채널 + 호명 키워드 → on_message 경로로 Managed Agent 호출 (tool 사용 가능)
      - 지정 채널 + 비키워드 → ChimeInCog의 자율 판단만 (tool 없이 가벼운 응답)
      - 비지정 채널 → 완전 무반응

패치노트 검색 연동: "에이든 패치" -> V2 컴포넌트 표시
대화 메모리: (guild_id, user_id) 단위로 SQLite 저장, Claude 자율 도구로 관리
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Dict, List, Optional
import logging
import re

from run.services.chat import get_chat_client
from run.services.chat.chat_agent_graph import build_chat_agent
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

_histories: Dict[str, List[dict]] = {}
MAX_HISTORY = 5

# ========== 서버별 일일 대화 쿼터 ==========
# Managed Agents는 세션당 비용 있어서 스팸 방지 + 비용 한도 설정
# 봇 재시작 시 리셋됨 (단순화). GCS 저장 원하면 rate_limit.py 별도 생성 권장.
from datetime import datetime, timezone, timedelta
_KST = timezone(timedelta(hours=9))
DAILY_CHAT_LIMIT = 20  # 서버당 하루 최대 대화 수
_daily_counts: Dict[tuple, int] = {}  # {(guild_scope, YYYY-MM-DD): count}


def _chat_quota_key(guild_id) -> tuple:
    scope = str(guild_id) if guild_id else "dm"
    today = datetime.now(_KST).strftime("%Y-%m-%d")
    return (scope, today)


def _over_daily_quota(guild_id) -> bool:
    return _daily_counts.get(_chat_quota_key(guild_id), 0) >= DAILY_CHAT_LIMIT


def _inc_daily_quota(guild_id) -> int:
    key = _chat_quota_key(guild_id)
    _daily_counts[key] = _daily_counts.get(key, 0) + 1
    return _daily_counts[key]

from run.core import config as _bot_config
_IDENTITY = _bot_config.BOT_IDENTITY

# 프롬프트 인젝션 감지 패턴
_injection_patterns = re.compile(
    r"시스템\s*프롬프트|system\s*prompt|내부\s*설정|internal|"
    r"지금부터.*형식으로|모든\s*답변을|역할을?\s*바꿔|"
    r"너는\s*이제|from\s*now\s*on|ignore\s*previous|"
    r"<response>|<answer>|<internal|<thinking>",
    re.IGNORECASE,
)


def _history_key(guild_id, user_id: int) -> str:
    return f"{guild_id or 'dm'}:{user_id}"


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
        self.client = get_chat_client()
        self.chat_agent = build_chat_agent(self.client)
        # unified: /대화 슬래시 전용 (on_message 없음)
        # debi/marlene 솔로: 지정 채널 + 호명 키워드 시 on_message → Managed Agent (tool 사용)
        self.identity = _IDENTITY

    async def cog_unload(self):
        await self.client.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """솔로봇 전용 키워드 응답.

        지정 채널 + 호명 키워드 ('데비야' / '마를렌아' 등)가 매칭되면
        Managed Agent 경유로 응답 (tool: search_player_stats, get_character_stats 등 사용 가능).
        그 외 메시지(비키워드)는 ChimeInCog이 가벼운 judge로 처리.
        """
        if message.author.bot:
            return
        if self.identity not in ("debi", "marlene"):
            return
        if not message.guild:
            return

        from run.core import config as _cfg
        from run.services.chat.chime_decider import has_keyword as _has_keyword

        # 지정 채널 외에서는 완전 무반응
        designated = _cfg.get_solo_chat_channels(message.guild.id, self.identity)
        if message.channel.id not in designated:
            return

        # 키워드 호명이 아니면 여기서 처리 안 함 (ChimeInCog 담당).
        # identity별 분리 — 데비는 '데비/뎁마'만, 마를렌은 '마를렌/뎁마'만 반응.
        if not _has_keyword(message.content, self.identity):
            return

        # 대화 토글 확인
        guild_settings = _cfg.load_settings().get("guilds", {}).get(str(message.guild.id), {})
        if not guild_settings.get("chat_enabled", True):
            return

        # 프롬프트 인젝션 방어
        if _injection_patterns.search(message.content):
            await message.reply("...그런 건 안 통해.", mention_author=False)
            return

        await self._respond_via_agent(message, message.content)

    async def _respond_via_agent(self, message: discord.Message, user_msg: str):
        """Managed Agent 경유 응답 (tool 사용 가능)."""
        guild_id = message.guild.id if message.guild else None

        # 일일 쿼터
        if _over_daily_quota(guild_id):
            current = _daily_counts.get(_chat_quota_key(guild_id), 0)
            await message.reply(
                f"...오늘은 이미 {current}번 얘기해서 좀 쉴래. 내일 다시 불러. "
                f"(하루 {DAILY_CHAT_LIMIT}번 제한)",
                mention_author=False,
            )
            return

        try:
            await log_command_usage(
                "대화", message.author.id, message.author.display_name,
                guild_id=guild_id,
                guild_name=message.guild.name if message.guild else None,
                channel_id=message.channel.id,
                channel_name=getattr(message.channel, "name", "DM"),
            )
        except Exception:
            pass

        current_count = _inc_daily_quota(guild_id)
        key = _history_key(guild_id, message.author.id)
        history = _histories.get(key, [])

        loading_msg = None
        is_cold = not await self.client.health_check()
        if is_cold:
            loading_msg = await message.reply("...잠깐만, 아직 덜 일어났어.", mention_author=False)

        async with message.channel.typing():
            result = await self.chat_agent.ainvoke({
                "user_message": user_msg,
                "history": history,
                "guild_id": guild_id,
                "user_id": message.author.id,
                "discord_channel": message.channel,
            })

        response = result.get("response")
        patch_info = result.get("patch_info")
        intent = result.get("intent", "general")

        quota_tag = f" [{current_count}/{DAILY_CHAT_LIMIT}]"
        print(
            f"[대화:{self.identity}] [{intent}]{quota_tag} Q: {user_msg[:30]} | A: {(response or '-')[:40]}",
            flush=True,
        )

        if not response:
            fail_text = "...연결이 안 돼."
            if loading_msg:
                await loading_msg.edit(content=fail_text)
            else:
                await message.reply(fail_text, mention_author=False)
            return

        history.append({"user": user_msg, "assistant": response})
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
        _histories[key] = history

        if loading_msg:
            await loading_msg.edit(content=response)
        else:
            await message.reply(response, mention_author=False)

        if patch_info and patch_info.get("changes"):
            try:
                patch_view = _build_patch_view(patch_info)
                await message.channel.send(view=patch_view)
            except Exception as e:
                logger.warning("패치 V2 전송 실패: %s", e)

    @app_commands.command(name="대화", description="데비&마를렌과 대화하기")
    @app_commands.describe(message="말하고 싶은 내용")
    async def chat_slash(self, interaction: discord.Interaction, message: str):
        """기존봇(unified) 전용 슬래시 명령어. 솔로봇은 키워드 트리거로 유도."""
        # 솔로봇은 슬래시 지원 X — 안내 메시지 (setup에서 tree 제거되지만 방어용)
        if self.identity in ("debi", "marlene"):
            await interaction.response.send_message(
                "이 봇은 지정한 채팅 채널에서 자동으로 끼어들어요. `/설정` 에서 응답 채널을 지정해 주세요.",
                ephemeral=True,
            )
            return

        guild_id = interaction.guild.id if interaction.guild else None
        user_id = interaction.user.id

        # 서버별 대화 토글 체크 — /설정의 "대화" 버튼으로 끌 수 있음
        if interaction.guild:
            from run.core import config
            guild_settings = config.load_settings().get("guilds", {}).get(str(interaction.guild.id), {})
            if not guild_settings.get("chat_enabled", True):
                await interaction.response.send_message(
                    "이 서버에서는 대화 기능이 꺼져 있어요. `/설정` 에서 켤 수 있어요.",
                    ephemeral=True,
                )
                return

        # 쿼터
        if _over_daily_quota(guild_id):
            current = _daily_counts.get(_chat_quota_key(guild_id), 0)
            await interaction.response.send_message(
                f"데비: ...오늘은 이미 {current}번 얘기해서 좀 쉴래.\n"
                f"마를렌: ...내일 다시 불러. (하루 {DAILY_CHAT_LIMIT}번 제한)",
                ephemeral=True,
            )
            return

        # 프롬프트 인젝션
        if _injection_patterns.search(message):
            await interaction.response.send_message(
                "데비: 뭔가 수상한 냄새가 나는데?\n마를렌: ...그런 건 안 통해.",
                ephemeral=True,
            )
            return

        # 3초 내 응답 필수 → defer로 "생각 중" 표시
        await interaction.response.defer()

        try:
            await log_command_usage(
                "대화", interaction.user.id, interaction.user.display_name,
                guild_id=guild_id,
                guild_name=interaction.guild.name if interaction.guild else None,
                channel_id=interaction.channel.id,
                channel_name=getattr(interaction.channel, 'name', 'DM'),
            )
        except Exception:
            pass

        current_count = _inc_daily_quota(guild_id)
        key = _history_key(guild_id, user_id)
        history = _histories.get(key, [])

        try:
            result = await self.chat_agent.ainvoke({
                "user_message": message,
                "history": history,
                "guild_id": guild_id,
                "user_id": user_id,
                "discord_channel": interaction.channel,
            })
        except Exception as e:
            logger.error("슬래시 /대화 실행 실패: %s", e)
            await interaction.followup.send("...연결이 안 돼.")
            return

        response = result.get("response")
        elapsed = result.get("elapsed", 0.0)
        patch_info = result.get("patch_info")
        corrections = result.get("corrections")
        intent = result.get("intent", "general")

        ctx_tag = " [+patch]" if patch_info else ""
        mem_tag = " [+mem]" if corrections else ""
        intent_tag = f" [{intent}]"
        quota_tag = f" [{current_count}/{DAILY_CHAT_LIMIT}]"
        print(
            f"[/대화] {elapsed:.1f}s{intent_tag}{ctx_tag}{mem_tag}{quota_tag} "
            f"| Q: {message[:30]} | A: {(response or '-')[:40]}",
            flush=True,
        )

        if not response:
            await interaction.followup.send("...연결이 안 돼.")
            return

        # 히스토리 저장
        history.append({"user": message, "assistant": response})
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
        _histories[key] = history

        # 응답 전송
        await interaction.followup.send(response)

        # 패치 V2 Container 추가
        if patch_info and patch_info.get("changes"):
            try:
                patch_view = _build_patch_view(patch_info)
                await interaction.followup.send(view=patch_view)
            except Exception as e:
                logger.warning("패치 V2 전송 실패: %s", e)

    @commands.command(name="대화초기화")
    async def chat_reset(self, ctx: commands.Context):
        """대화 히스토리 초기화. Managed Agents 세션 매핑도 끊어서 다음 호출 시 새 세션."""
        guild_id = ctx.guild.id if ctx.guild else None
        user_id = ctx.author.id
        key = _history_key(guild_id, user_id)
        _histories.pop(key, None)

        try:
            from run.services.memory import session_store
            session_store.delete_session(guild_id, user_id)
        except Exception as e:
            logger.warning("session_store.delete_session 실패 (무시): %s", e)

        try:
            await log_command_usage("대화초기화", ctx.author.id, ctx.author.display_name)
        except Exception:
            pass
        await ctx.reply("대화 히스토리가 초기화되었습니다.", mention_author=False)

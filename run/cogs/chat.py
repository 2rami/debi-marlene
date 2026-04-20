"""
대화 Cog

데비&마를렌 캐릭터 AI 대화
키워드 트리거: 데비, 마를렌, 뎁마 등 이름/호칭이 포함된 메시지에 자동 반응
    → 키워드는 LLM에게도 원문 그대로 전달 (페르소나 라우팅 신호로 사용)
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

# 트리거 키워드: BOT_IDENTITY 기준 분기.
# unified(기본): 기존봇 — 데비/마를렌/뎁마 전부.
# debi 솔로봇: 자기 이름만 반응. 마를렌 호칭은 무시 (끼어들기는 Phase 2 chime_in Cog 담당).
# marlene 솔로봇: 자기 이름만 반응.
from run.core import config as _bot_config
_IDENTITY = _bot_config.BOT_IDENTITY

if _IDENTITY == "debi":
    TRIGGER_WORDS = ["데비야", "데비나", "데비아"]
    TRIGGER_NAMES = ["데비"]
elif _IDENTITY == "marlene":
    TRIGGER_WORDS = ["마를렌아", "마를렌야", "마를렌나"]
    TRIGGER_NAMES = ["마를렌"]
else:  # unified (기존)
    TRIGGER_WORDS = [
        "데비야", "데비나", "데비아",
        "마를렌아", "마를렌야", "마를렌나",
        "뎁마야", "뎁마아", "뎁마나",
    ]
    TRIGGER_NAMES = ["데비", "마를렌", "뎁마"]

_trigger_pattern = re.compile(
    "|".join(re.escape(w) for w in TRIGGER_WORDS + TRIGGER_NAMES)
)

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
        # unified: /대화 슬래시 전용 (on_message 무시)
        # debi/marlene 솔로: 키워드 트리거 (on_message)만
        self.identity = _IDENTITY

    async def cog_unload(self):
        await self.client.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        # unified(기존봇)는 /대화 슬래시 전용 — 키워드 트리거 무시.
        # 솔로봇(debi/marlene)만 on_message 경로로 진입.
        if self.identity not in ("debi", "marlene"):
            return
        if not _trigger_pattern.search(message.content):
            return

        # 서버별 대화 토글 체크
        if message.guild:
            from run.core import config
            guild_settings = config.load_settings().get("guilds", {}).get(str(message.guild.id), {})
            if not guild_settings.get("chat_enabled", True):
                return

        if _injection_patterns.search(message.content):
            await message.reply("데비: 뭔가 수상한 냄새가 나는데?\n마를렌: ...그런 건 안 통해.", mention_author=False)
            return

        # 키워드 스트립 제거 (2026-04-21): LLM이 "데비야/마를렌아/뎁마" 호칭을 직접 보고
        # 어느 캐릭터를 호출했는지 페르소나 라우팅에 활용하도록 원문 그대로 전달.
        await self._respond(message, message.content)

    async def _respond(self, message: discord.Message, user_msg: str):
        """키워드 트리거 응답"""
        guild_id = message.guild.id if message.guild else None

        # 서버별 일일 쿼터 체크 (Managed Agents 비용 방지)
        if _over_daily_quota(guild_id):
            current = _daily_counts.get(_chat_quota_key(guild_id), 0)
            await message.reply(
                f"데비: ...오늘은 이미 {current}번 얘기해서 좀 쉴래.\n"
                f"마를렌: ...내일 다시 불러. (하루 {DAILY_CHAT_LIMIT}번 제한)",
                mention_author=False,
            )
            print(
                f"[쿼터] 서버 {guild_id or 'dm'} 일일 한도({DAILY_CHAT_LIMIT}) 도달 — 응답 스킵",
                flush=True,
            )
            return

        try:
            await log_command_usage(
                "대화", message.author.id, message.author.display_name,
                guild_id=guild_id,
                guild_name=message.guild.name if message.guild else None,
                channel_id=message.channel.id,
                channel_name=getattr(message.channel, 'name', 'DM'),
            )
        except Exception:
            pass

        # 쿼터 카운트 증가 (실제 LLM 호출 전 증가 → 실패해도 카운트 차감 안 함. 스팸 억제)
        current_count = _inc_daily_quota(guild_id)

        key = _history_key(guild_id, message.author.id)
        history = _histories.get(key, [])

        # corrections 저장은 이제 Claude의 remember_about_user 도구 자율 판단으로 옮김.
        # 봇 측 regex 트리거(detect_correction)는 false positive 많아서 제거 (2026-04-20).

        # health check -> 콜드스타트 감지 (Discord 쪽 side-effect라 그래프 외부에 둠)
        loading_msg = None
        is_cold = not await self.client.health_check()
        if is_cold:
            loading_msg = await message.reply("...잠깐만, 아직 덜 일어났어.", mention_author=False)

        # LangGraph StateGraph 실행: classify → (rag | skip) → memory → llm
        # guild_id: per-guild 메모리 스코프, discord_channel: Managed Agents가 StatsLayoutView 전송할 때 씀
        async with message.channel.typing():
            result = await self.chat_agent.ainvoke({
                "user_message": user_msg,
                "history": history,
                "guild_id": guild_id,
                "user_id": message.author.id,
                "discord_channel": message.channel,
            })

        response = result.get("response")
        elapsed = result.get("elapsed", 0.0)
        patch_info = result.get("patch_info")
        corrections = result.get("corrections")
        intent = result.get("intent", "general")

        ctx_tag = " [+patch]" if patch_info else ""
        cold_tag = " [cold]" if is_cold else ""
        mem_tag = " [+mem]" if corrections else ""
        intent_tag = f" [{intent}]"
        quota_tag = f" [{current_count}/{DAILY_CHAT_LIMIT}]"
        print(f"[대화] {elapsed:.1f}s{intent_tag}{ctx_tag}{mem_tag}{cold_tag}{quota_tag} | Q: {user_msg[:30]} | A: {(response or '-')[:40]}", flush=True)

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

    @app_commands.command(name="대화", description="데비&마를렌과 대화하기")
    @app_commands.describe(message="말하고 싶은 내용")
    async def chat_slash(self, interaction: discord.Interaction, message: str):
        """기존봇(unified) 전용 슬래시 명령어. 솔로봇은 키워드 트리거로 유도."""
        # 솔로봇은 슬래시 지원 X — 유저에게 키워드 트리거 사용 안내 (사실 setup 단계에서
        # tree.remove_command로 이 명령어 자체가 솔로 프로필에 노출되지 않지만, 방어용)
        if self.identity in ("debi", "marlene"):
            await interaction.response.send_message(
                "이 봇은 `데비야` 또는 `마를렌아` 로 호명해서 말 걸어봐.",
                ephemeral=True,
            )
            return

        guild_id = interaction.guild.id if interaction.guild else None
        user_id = interaction.user.id

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

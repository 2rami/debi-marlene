"""이탈 설문 LayoutView — 봇 추방 시 owner DM 으로 사유 수집 + 재초대 유도.

V2 제약: Container 는 top-level only (Container 중첩 금지).
허용 children = 1 ActionRow / 9 Section / 10 TextDisplay / 12 MediaGallery / 13 File / 14 Separator.

일러스트 자리: _ILLUST_URL 가 설정되면 상단에 MediaGallery 로 "가지마" 일러를 띄운다.
지금은 None — 거노가 일러 제작 후 URL 또는 attachment 로 교체.
"""
from __future__ import annotations

import asyncio
from typing import Optional

import discord

from run.services import churn as churn_service

_ACCENT = discord.Colour(0xFFB6C1)  # 기존 봇 톤(핑크)

# 일러 준비되면 외부 이미지 URL 또는 attachment:// 로 채움. None 이면 텍스트만.
_ILLUST_URL: Optional[str] = None

_SURVEY_TIMEOUT = 60 * 60 * 24 * 3  # 3일


class ChurnSurveyView(discord.ui.LayoutView):
    """봇 추방 시 owner 에게 DM 으로 보내는 이탈 사유 설문."""

    def __init__(
        self,
        *,
        guild_id: int,
        guild_name: Optional[str],
        owner_id: int,
        member_count: Optional[int] = None,
        installed_days: Optional[int] = None,
        invite_url: Optional[str] = None,
    ):
        super().__init__(timeout=_SURVEY_TIMEOUT)
        self.guild_id = guild_id
        self.guild_name = guild_name or "서버"
        self.owner_id = owner_id
        self.member_count = member_count
        self.installed_days = installed_days
        self.invite_url = invite_url
        self._selected: list[str] = []
        self._submitted = False
        self._select: Optional[discord.ui.Select] = None
        self._build()

    # ───────── 렌더 ─────────

    def _build(self) -> None:
        self.clear_items()

        info_children: list[discord.ui.Item] = []
        if _ILLUST_URL:
            info_children.append(
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=_ILLUST_URL))
            )
        info_children.append(
            discord.ui.TextDisplay(
                "## 더 자세히 알려주시겠어요?\n"
                f"**{self.guild_name}** 서버에서 저를 내보내셨네요.\n"
                "잠깐 시간 내서 이유를 알려주시면 봇 개선에 큰 도움이 돼요!\n"
                "-# 실수로 내보내신 거라면 아래 버튼으로 언제든 다시 추가할 수 있어요."
            )
        )
        info_container = discord.ui.Container(*info_children, accent_colour=_ACCENT)

        select = discord.ui.Select(
            placeholder="왜 내보내셨나요? (여러 개 선택 가능)",
            min_values=0,
            max_values=len(churn_service.CHURN_REASONS),
            options=[
                discord.SelectOption(label=label, value=value)
                for value, label in churn_service.CHURN_REASONS
            ],
        )
        select.callback = self._on_select
        self._select = select

        submit_btn = discord.ui.Button(label="제출", style=discord.ButtonStyle.primary)
        submit_btn.callback = self._on_submit

        ctrl_children: list[discord.ui.Item] = [
            discord.ui.ActionRow(select),
            discord.ui.ActionRow(submit_btn),
        ]
        if self.invite_url:
            rejoin_btn = discord.ui.Button(
                label="다시 추가하기",
                style=discord.ButtonStyle.link,
                url=self.invite_url,
            )
            ctrl_children.append(discord.ui.ActionRow(rejoin_btn))

        ctrl_container = discord.ui.Container(*ctrl_children, accent_colour=_ACCENT)

        self.add_item(info_container)
        self.add_item(ctrl_container)

    def _build_thanks(self) -> None:
        self.clear_items()
        thanks = discord.ui.TextDisplay(
            "## 소중한 의견 감사해요!\n"
            "알려주신 내용은 봇 개선에 그대로 반영돼요.\n"
            "-# 언제든 다시 찾아주세요!"
        )
        children: list[discord.ui.Item] = [thanks]
        if self.invite_url:
            rejoin_btn = discord.ui.Button(
                label="다시 추가하기",
                style=discord.ButtonStyle.link,
                url=self.invite_url,
            )
            children.append(discord.ui.ActionRow(rejoin_btn))
        self.add_item(discord.ui.Container(*children, accent_colour=_ACCENT))

    # ───────── 콜백 ─────────

    async def _on_select(self, interaction: discord.Interaction) -> None:
        self._selected = list(self._select.values) if self._select else []
        await interaction.response.defer()

    async def _on_submit(self, interaction: discord.Interaction) -> None:
        if self._submitted:
            await interaction.response.defer()
            return
        self._submitted = True

        await asyncio.to_thread(
            churn_service.save_churn_feedback,
            guild_id=self.guild_id,
            guild_name=self.guild_name,
            owner_id=self.owner_id,
            reasons=self._selected,
            member_count=self.member_count,
            installed_days=self.installed_days,
        )

        self._build_thanks()
        await interaction.response.edit_message(view=self)

    async def on_timeout(self) -> None:
        for item in self.walk_children():
            if isinstance(item, (discord.ui.Button, discord.ui.Select)):
                item.disabled = True

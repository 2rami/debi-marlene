"""크레딧 LayoutView — 잔고 + 안내 (도박/출석은 대시보드).

V2 제약: Container 는 top-level 만, children 에 중첩 금지.
허용 children type = 1 ActionRow / 9 Section / 10 TextDisplay / 12 MediaGallery
                  / 13 File / 14 Separator

구조:
  Container1 (accent=라임) — 헤더 + 잔고
   ├ Section(헤더 TextDisplay, accessory=Thumbnail("attachment://credit.png"))
     └ 썸네일 자산이 없는 배포처에서는 Section 없이 TextDisplay 만 (400 방지)
   ├ Separator (LARGE)
   └ TextDisplay 잔고/연속/공동
  Container2 (accent=다크그린) — 안내 + 액션
   ├ TextDisplay 도박/출석 대시보드 안내 (마크다운 링크)
   └ ActionRow [새로고침]

- 베팅/도박은 대시보드 전용 — 봇에서 베팅 ActionRow 제거
- ephemeral 제거 (channel-wide visible)
- 본인 외 새로고침 차단, 180s timeout
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import discord

from run.services import credits as credits_service
from run.services.credits_emoji import (  # format_emoji 는 호환용 re-export
    format_emoji, pick_thumbnail_path, ASSET_FILENAME,  # noqa: F401
)


# 색상
_ACCENT_LIME = discord.Colour(0xE5FC8A)
_ACCENT_GREEN = discord.Colour(0x326D1B)


class CreditsLayoutView(discord.ui.LayoutView):
    """`/크레딧` LayoutView — 잔고 디스플레이 + 대시보드 유도."""

    def __init__(
        self,
        *,
        user_id: int,
        user_name: str,
        guild_id: Optional[int],
        guild_name: Optional[str],
        emoji_str: str = "[C]",
    ):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.user_name = user_name
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.emoji_str = emoji_str
        self._balance = {
            "personal": 0, "streak_days": 0, "last_check_in": None,
            "checked_in_today": False, "daily_bet": 0,
        }
        self._guild_balance = 0
        self._thumb_path: Optional[Path] = None
        self._thumb_decided = False

    # ───────── 상태 fetch ─────────

    def _fetch_state_sync(self) -> None:
        self._balance = credits_service.get_balance(self.user_id)
        if self.guild_id is not None:
            self._guild_balance = credits_service.get_guild_balance(self.guild_id)
        else:
            self._guild_balance = 0

    @classmethod
    async def create(
        cls,
        *,
        user_id: int,
        user_name: str,
        guild_id: Optional[int],
        guild_name: Optional[str],
        emoji_str: str = "[C]",
    ) -> "CreditsLayoutView":
        """비동기 생성자 — Firestore fetch 만 off-thread."""
        instance = cls(
            user_id=user_id, user_name=user_name,
            guild_id=guild_id, guild_name=guild_name, emoji_str=emoji_str,
        )
        await instance._refresh_state()
        instance._build()
        return instance

    async def _refresh_state(self) -> None:
        await asyncio.to_thread(self._fetch_state_sync)

    # ───────── 렌더 ─────────

    def _build(self) -> None:
        self.clear_items()

        bal = self._balance
        personal = bal["personal"]
        streak = bal["streak_days"]
        checked_today = bal["checked_in_today"]
        emoji = self.emoji_str

        # ── 헤더 ──
        # 썸네일 유무를 여기서 한 번만 정하고 cog 는 thumbnail_file() 로 그 결정을 따른다.
        # 첨부 없이 Thumbnail 만 남으면 Discord 가 400(50035) 로 메시지를 통째로 거절한다.
        # 첨부는 최초 전송 때 확정되고 edit 으로 갈리지 않으므로 재빌드에서도 유지한다.
        if not self._thumb_decided:
            candidate = pick_thumbnail_path(personal)
            self._thumb_path = candidate if candidate.is_file() else None
            self._thumb_decided = True

        header_text = discord.ui.TextDisplay(
            f"## {emoji} {self.user_name}님의 크레딧 지갑"
        )
        if self._thumb_path is not None:
            header = discord.ui.Section(
                header_text,
                accessory=discord.ui.Thumbnail(media=f"attachment://{ASSET_FILENAME}"),
            )
        else:
            header = header_text

        # ── 개인 잔고 본문 ──
        personal_lines = [
            f"**보유 크레딧** · {emoji} {personal:,}",
            f"**연속 출석** · {streak}일 ({'완료' if checked_today else '오늘 미완료'})",
        ]
        stats_text = discord.ui.TextDisplay("\n".join(personal_lines))

        # ── 서버 공동 지갑 (DM 외 강조 — Separator + 헤딩) ──
        guild_section = None
        if self.guild_name:
            guild_section = discord.ui.TextDisplay(
                f"### {self.guild_name} 서버 공동 지갑\n"
                f"{emoji} **{self._guild_balance:,}**\n"
                f"-# 멤버들이 기부한 누적 크레딧"
            )

        # ── 안내 (대시보드 유도, 짧게 링크만) ──
        notice = discord.ui.TextDisplay(
            "**[출석체크](https://debimarlene.com)** · "
            "**[도박하러 가기](https://debimarlene.com)**"
        )

        # ── 액션 row ──
        refresh_btn = discord.ui.Button(
            label="새로고침",
            style=discord.ButtonStyle.secondary,
        )
        refresh_btn.callback = self._on_refresh
        action_row = discord.ui.ActionRow(refresh_btn)

        # ── Separator (각 인스턴스 신선하게 — 동일 객체 공유 시 V2 검증 충돌 방지) ──
        def sep_large():
            return discord.ui.Separator(
                visible=True, spacing=discord.SeparatorSpacing.large,
            )

        wallet_children = [header, sep_large(), stats_text]
        if guild_section is not None:
            wallet_children.append(sep_large())
            wallet_children.append(guild_section)

        wallet_container = discord.ui.Container(
            *wallet_children,
            accent_colour=_ACCENT_LIME,
        )
        notice_container = discord.ui.Container(
            notice,
            action_row,
            accent_colour=_ACCENT_GREEN,
        )
        self.add_item(wallet_container)
        self.add_item(notice_container)

    # ───────── 첨부 ─────────

    def thumbnail_file(self) -> Optional[discord.File]:
        """헤더 썸네일 첨부. 자산이 없으면 None — 그 경우 view 도 Thumbnail 을 안 넣는다."""
        if self._thumb_path is None:
            return None
        return discord.File(str(self._thumb_path), filename=ASSET_FILENAME)

    # ───────── 권한 가드 ─────────

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "이건 다른 사람의 지갑이에요. `/크레딧` 으로 본인 지갑을 여세요.",
                ephemeral=True,
            )
            return False
        return True

    # ───────── 콜백 ─────────

    async def _on_refresh(self, interaction: discord.Interaction):
        await self._refresh_state()
        self._build()
        await interaction.response.edit_message(view=self)

    async def on_timeout(self) -> None:
        for item in (self.walk_children() if hasattr(self, "walk_children") else []):
            if isinstance(item, discord.ui.Button):
                item.disabled = True

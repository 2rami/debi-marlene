"""크레딧 LayoutView — 잔고 + 안내 (도박/출석은 대시보드).

V2 제약: Container 는 top-level 만, children 에 중첩 금지.
허용 children type = 1 ActionRow / 9 Section / 10 TextDisplay / 12 MediaGallery
                  / 13 File / 14 Separator

구조:
  Container1 (accent=라임) — 헤더 + 잔고
   ├ Section(헤더 TextDisplay, accessory=Thumbnail("attachment://credit.png"))
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
from typing import Optional

import discord

from run.services import credits as credits_service
from run.services.credits_emoji import format_emoji  # noqa: F401  (호환용 export)


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

        # ── 헤더 (Section + Thumbnail: 우측에 큰 크레딧 이미지) ──
        header = discord.ui.Section(
            discord.ui.TextDisplay(
                f"## {emoji} {self.user_name}님의 크레딧 지갑"
            ),
            accessory=discord.ui.Thumbnail(media="attachment://credit.png"),
        )

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

        # ── 안내 (출석/도박 대시보드 유도) ──
        notice = discord.ui.TextDisplay(
            f"**출석체크** · 매일 +{credits_service.DAILY_CHECK_IN} "
            f"(연속 3일 +{credits_service.STREAK_3_BONUS} · 7일 +{credits_service.STREAK_7_BONUS})\n"
            f"**도박 / 뽑기** · 70% 0배 / 20% 2배 / 8% 3배 / 2% 10배 (일일 한도 50)\n\n"
            f"두 기능 모두 대시보드에서 → **[debimarlene.com](https://debimarlene.com)**"
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

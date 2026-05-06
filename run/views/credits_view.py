"""크레딧 LayoutView — V2 Components.

V2 제약: Container 는 top-level 만, children 에 중첩 금지 (Discord API 50035).
허용 children type = 1 ActionRow / 9 Section / 10 TextDisplay / 12 MediaGallery
                  / 13 File / 14 Separator

구조 (Container 두 개 top-level 로 분리):
  Container1 (accent=라임) — 헤더 + 잔고
   ├ TextDisplay "## {emoji} {유저}님의 크레딧 지갑"
   ├ Separator (LARGE)
   └ TextDisplay 잔고/연속/공동 묶음
  Container2 (accent=다크그린) — 도박
   ├ TextDisplay "### 도박 / 뽑기"
   ├ TextDisplay 확률표 + 일일 한도
   ├ ActionRow [5][10][50][ALL IN]
   ├ Separator (SMALL)
   ├ TextDisplay 마지막 결과
   ├ Separator (LARGE)
   ├ TextDisplay 출석 안내 (대시보드 마크다운 링크)
   └ ActionRow [새로고침]

- 텍스트 `─────` X — Separator 컴포넌트
- 이모지 X (크레딧 application emoji 만)
- 본인 외 클릭 차단, 180s timeout
"""

from __future__ import annotations

import asyncio
from typing import Optional

import discord

from run.services import credits as credits_service
from run.services.credits_emoji import format_emoji


_BET_PRESETS = [5, 10, 50]

# 색상
_ACCENT_LIME = discord.Colour(0xE5FC8A)
_ACCENT_GREEN = discord.Colour(0x326D1B)


def _format_result_text(last: dict | None) -> str:
    """마지막 베팅 결과 라인."""
    if not last:
        return "-# 아직 베팅 안 함 — 아래 버튼으로 시작"
    if not last.get("ok"):
        reason = last.get("reason", "실패")
        return f"-# 마지막 결과 · 실패 ({reason})"
    bet = last["bet"]
    mult = last["multiplier"]
    payout = last["payout"]
    net = last["net"]
    sign = "+" if net >= 0 else ""
    if mult == 0:
        tag = "[꽝]"
    elif mult == 10:
        tag = "[JACKPOT 10x]"
    elif mult == 3:
        tag = "[3x]"
    elif mult == 2:
        tag = "[2x]"
    else:
        tag = f"[{mult}x]"
    return f"**{tag}** {bet} → {payout} (순익 {sign}{net})"


class CreditsLayoutView(discord.ui.LayoutView):
    """`/크레딧` LayoutView — V2 Component 분할 구조."""

    def __init__(
        self,
        *,
        user_id: int,
        user_name: str,
        guild_id: Optional[int],
        guild_name: Optional[str],
        emoji_str: str = "[C]",
    ):
        # 메인 loop 에서 인스턴스화 — discord.py LayoutView.__init__ 가 running loop 요구.
        super().__init__(timeout=180)
        self.user_id = user_id
        self.user_name = user_name
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.emoji_str = emoji_str
        self._last_result: dict | None = None
        # state — create() 가 fetch 해서 채움
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
        """비동기 생성자 — Firestore fetch 만 off-thread, 인스턴스화는 메인 loop."""
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
        daily_bet = bal["daily_bet"]
        daily_cap = credits_service.GACHA_DAILY_BET_CAP
        remaining_cap = max(0, daily_cap - daily_bet)
        emoji = self.emoji_str

        # ── 헤더 (Section + Thumbnail: 우측에 큰 크레딧 이미지) ──
        # cog 가 동일 파일명 'credit.png' 을 discord.File 로 첨부 → attachment:// URI 로 참조
        header = discord.ui.Section(
            discord.ui.TextDisplay(
                f"## {emoji} {self.user_name}님의 크레딧 지갑"
            ),
            accessory=discord.ui.Thumbnail(media="attachment://credit.png"),
        )

        # ── 잔고 본문 (sub-Container 금지 → 단일 TextDisplay) ──
        stats_lines = [
            f"**보유 크레딧** · {emoji} {personal:,}",
            f"**연속 출석** · {streak}일 ({'완료' if checked_today else '오늘 미완료'})",
        ]
        if self.guild_name:
            stats_lines.append(
                f"**{self.guild_name} 공동 지갑** · {emoji} {self._guild_balance:,}"
            )
        stats_text = discord.ui.TextDisplay("\n".join(stats_lines))

        # ── 도박 섹션 ──
        gamble_title = discord.ui.TextDisplay("### 도박 / 뽑기")
        gamble_meta = discord.ui.TextDisplay(
            f"확률 · 70% 0배 / 20% 2배 / 8% 3배 / 2% 10배\n"
            f"오늘 베팅 누계 · **{daily_bet} / {daily_cap}** "
            f"(남은 한도 {remaining_cap})"
        )

        # 베팅 버튼 row
        bet_buttons = []
        for amt in _BET_PRESETS:
            disabled = amt > personal or amt > remaining_cap or remaining_cap <= 0
            btn = discord.ui.Button(
                label=str(amt),
                style=discord.ButtonStyle.primary,
                disabled=disabled,
            )
            btn.callback = self._make_bet_callback(amt)
            bet_buttons.append(btn)

        allin_amt = min(personal, remaining_cap)
        allin_disabled = allin_amt <= 0
        allin_btn = discord.ui.Button(
            label=f"ALL IN ({allin_amt})" if not allin_disabled else "ALL IN",
            style=discord.ButtonStyle.danger,
            disabled=allin_disabled,
        )
        if not allin_disabled:
            allin_btn.callback = self._make_bet_callback(allin_amt)
        bet_buttons.append(allin_btn)
        bet_row = discord.ui.ActionRow(*bet_buttons)

        result_line = discord.ui.TextDisplay(_format_result_text(self._last_result))

        # ── 출석 안내 (대시보드 유도) ──
        attend_notice = discord.ui.TextDisplay(
            f"매일 출석체크 +{credits_service.DAILY_CHECK_IN} "
            f"(연속 3일 +{credits_service.STREAK_3_BONUS} · 7일 +{credits_service.STREAK_7_BONUS})\n"
            f"→ [debimarlene.com](https://debimarlene.com)"
        )

        # ── 액션 row (새로고침) ──
        refresh_btn = discord.ui.Button(
            label="새로고침",
            style=discord.ButtonStyle.secondary,
        )
        refresh_btn.callback = self._on_refresh
        action_row = discord.ui.ActionRow(refresh_btn)

        # ── Separator helpers ──
        sep_large = lambda: discord.ui.Separator(  # noqa: E731
            visible=True, spacing=discord.SeparatorSpacing.large,
        )
        sep_small = lambda: discord.ui.Separator(  # noqa: E731
            visible=False, spacing=discord.SeparatorSpacing.small,
        )

        # 두 Container 를 top-level 로 (V2 중첩 금지 회피)
        wallet_container = discord.ui.Container(
            header,
            sep_large(),
            stats_text,
            accent_colour=_ACCENT_LIME,
        )
        gamble_container = discord.ui.Container(
            gamble_title,
            gamble_meta,
            bet_row,
            sep_small(),
            result_line,
            sep_large(),
            attend_notice,
            action_row,
            accent_colour=_ACCENT_GREEN,
        )
        self.add_item(wallet_container)
        self.add_item(gamble_container)

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

    def _make_bet_callback(self, amount: int):
        async def cb(interaction: discord.Interaction):
            result = await asyncio.to_thread(
                credits_service.gacha, self.user_id, amount,
            )
            self._last_result = result
            await self._refresh_state()
            self._build()
            await interaction.response.edit_message(view=self)
        return cb

    async def _on_refresh(self, interaction: discord.Interaction):
        await self._refresh_state()
        self._build()
        await interaction.response.edit_message(view=self)

    async def on_timeout(self) -> None:
        # ephemeral followup edit 까다로워 그대로 둠 — 다음 클릭 시 새 view.
        for item in (self.walk_children() if hasattr(self, "walk_children") else []):
            if isinstance(item, discord.ui.Button):
                item.disabled = True

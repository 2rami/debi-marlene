"""
캐릭터 통계 UI (CharacterStatsLayoutView)

/통계 명령어에서 사용하는 Components V2 기반 UI.
캐릭터별 승률, 픽률 등을 페이지네이션으로 볼 수 있어요.
"""
import discord
from typing import Dict, Any, List

from run.services.eternal_return.api_client import game_data, get_character_stats
from run.utils.emoji_utils import get_character_emoji, get_char_tier_emoji


class CharacterStatsView(discord.ui.LayoutView):
    """
    캐릭터 통계 Components V2 UI

    캐릭터별 통계를 10개씩 페이지로 나눠서 보여줘요.
    버튼으로 페이지 이동, 기간/정렬 전환이 가능해요.
    """
    def __init__(self, stats_data: Dict[str, Any], period: int, page: int = 0, sort_by: str = "tier"):
        super().__init__(timeout=120)
        self.stats_data = stats_data
        self.period = period
        self.page = page
        self.sort_by = sort_by
        self.max_items_per_page = 10

        self._process_and_sort_data()
        self._build_layout()

    def _process_and_sort_data(self):
        """데이터 가공 및 정렬"""
        raw_stats = self.stats_data.get("characterStatSnapshot", {}).get("characterStats", [])
        total_games_all = sum(c.get("count", 0) for c in raw_stats)

        self.processed_chars = []
        for char_stat in raw_stats:
            char_id = char_stat.get("key", 0)
            games = char_stat.get("count", 0)

            weapon_stats = char_stat.get("weaponStats", [])
            if weapon_stats:
                total_wins = sum(w.get("win", 0) for w in weapon_stats)
                total_weapon_games = sum(w.get("count", 0) for w in weapon_stats)
                win_rate = (total_wins / total_weapon_games * 100) if total_weapon_games > 0 else 0
                tier_score = weapon_stats[0].get("tierScore", 0)
                tier = weapon_stats[0].get("tier", "?")
            else:
                win_rate = 0
                tier_score = 0
                tier = "?"

            pick_rate = (games / total_games_all * 100) if total_games_all > 0 else 0

            self.processed_chars.append({
                "char_id": char_id,
                "char_key": game_data.get_character_key(char_id),
                "name": game_data.get_character_name(char_id),
                "games": games,
                "win_rate": win_rate,
                "pick_rate": pick_rate,
                "tier_score": tier_score,
                "tier": tier
            })

        if self.sort_by == "winrate":
            self.processed_chars.sort(key=lambda x: x["win_rate"], reverse=True)
        elif self.sort_by == "pickrate":
            self.processed_chars.sort(key=lambda x: x["pick_rate"], reverse=True)
        else:
            self.processed_chars.sort(key=lambda x: x["tier_score"], reverse=True)

        self.total_pages = max(1, (len(self.processed_chars) - 1) // self.max_items_per_page + 1)

    def _build_layout(self):
        """V2 레이아웃 구성"""
        self.clear_items()

        sort_names = {"tier": "티어순", "winrate": "승률순", "pickrate": "픽률순"}
        sort_name = sort_names.get(self.sort_by, "티어순")

        start_idx = self.page * self.max_items_per_page
        end_idx = start_idx + self.max_items_per_page
        page_chars = self.processed_chars[start_idx:end_idx]

        lines = [f"## 캐릭터 통계 - {sort_name}\n"]
        for i, char in enumerate(page_chars, start_idx + 1):
            char_emoji = get_character_emoji(char["char_key"]) if char["char_key"] else ""
            tier_emoji = get_char_tier_emoji(char["tier"]) if char["tier"] != "?" else ""

            name = char["name"]
            win_rate = char["win_rate"]
            pick_rate = char["pick_rate"]

            lines.append(f"### `{i:2d}` {char_emoji} {name} {tier_emoji}")
            if self.sort_by == "winrate":
                lines.append(f"-# 승률 **{win_rate:.1f}%** | 픽률 {pick_rate:.1f}%")
            elif self.sort_by == "pickrate":
                lines.append(f"-# 픽률 **{pick_rate:.1f}%** | 승률 {win_rate:.1f}%")
            else:
                lines.append(f"-# 승률 {win_rate:.1f}% | 픽률 {pick_rate:.1f}%")

        # 메타 정보
        meta = self.stats_data.get("meta", {})
        patch = meta.get("patch", 0)
        tier_game_count = self.stats_data.get("characterStatSnapshot", {}).get("tierGameCount", 0)

        patch_str = str(patch)
        if len(patch_str) >= 3:
            patch_version = f"{patch_str[0]}.{patch_str[1:]}"
            patch_version = patch_version.rstrip('0').rstrip('.')
        else:
            patch_version = patch_str

        lines.append(f"\n-# 다이아+ | {self.period}일 | 패치 {patch_version} | {tier_game_count:,}게임 | {self.page + 1}/{self.total_pages}")

        text = "\n".join(lines)
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(text),
            accent_colour=discord.Colour(0x00CED1)
        ))

        # 페이지 이동 + 기간 버튼
        prev_btn = discord.ui.Button(label="◀", style=discord.ButtonStyle.primary, custom_id="cs_prev", disabled=self.page == 0)
        prev_btn.callback = self._on_prev
        next_btn = discord.ui.Button(label="▶", style=discord.ButtonStyle.primary, custom_id="cs_next", disabled=self.page >= self.total_pages - 1)
        next_btn.callback = self._on_next

        period_3d = discord.ui.Button(
            label="3일", custom_id="cs_3d",
            style=discord.ButtonStyle.primary if self.period == 3 else discord.ButtonStyle.secondary
        )
        period_3d.callback = self._on_3d
        period_7d = discord.ui.Button(
            label="7일", custom_id="cs_7d",
            style=discord.ButtonStyle.primary if self.period == 7 else discord.ButtonStyle.secondary
        )
        period_7d.callback = self._on_7d

        self.add_item(discord.ui.Container(
            discord.ui.ActionRow(prev_btn, period_3d, period_7d, next_btn)
        ))

        # 정렬 버튼
        sort_tier = discord.ui.Button(
            label="티어순", custom_id="cs_sort_tier",
            style=discord.ButtonStyle.primary if self.sort_by == "tier" else discord.ButtonStyle.secondary
        )
        sort_tier.callback = self._on_sort_tier
        sort_wr = discord.ui.Button(
            label="승률순", custom_id="cs_sort_wr",
            style=discord.ButtonStyle.primary if self.sort_by == "winrate" else discord.ButtonStyle.secondary
        )
        sort_wr.callback = self._on_sort_wr
        sort_pr = discord.ui.Button(
            label="픽률순", custom_id="cs_sort_pr",
            style=discord.ButtonStyle.primary if self.sort_by == "pickrate" else discord.ButtonStyle.secondary
        )
        sort_pr.callback = self._on_sort_pr

        self.add_item(discord.ui.Container(
            discord.ui.ActionRow(sort_tier, sort_wr, sort_pr)
        ))

    async def _on_prev(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            self._build_layout()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.defer()

    async def _on_next(self, interaction: discord.Interaction):
        if self.page < self.total_pages - 1:
            self.page += 1
            self._build_layout()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.defer()

    async def _on_3d(self, interaction: discord.Interaction):
        if self.period == 3:
            await interaction.response.defer()
            return
        await interaction.response.defer()
        new_data = await get_character_stats(dt=3, team_mode="SQUAD", tier="diamond_plus")
        if new_data:
            self.stats_data = new_data
            self.period = 3
            self.page = 0
            self._process_and_sort_data()
            self._build_layout()
            await interaction.edit_original_response(view=self)

    async def _on_7d(self, interaction: discord.Interaction):
        if self.period == 7:
            await interaction.response.defer()
            return
        await interaction.response.defer()
        new_data = await get_character_stats(dt=7, team_mode="SQUAD", tier="diamond_plus")
        if new_data:
            self.stats_data = new_data
            self.period = 7
            self.page = 0
            self._process_and_sort_data()
            self._build_layout()
            await interaction.edit_original_response(view=self)

    async def _on_sort_tier(self, interaction: discord.Interaction):
        if self.sort_by == "tier":
            await interaction.response.defer()
            return
        self.sort_by = "tier"
        self.page = 0
        self._process_and_sort_data()
        self._build_layout()
        await interaction.response.edit_message(view=self)

    async def _on_sort_wr(self, interaction: discord.Interaction):
        if self.sort_by == "winrate":
            await interaction.response.defer()
            return
        self.sort_by = "winrate"
        self.page = 0
        self._process_and_sort_data()
        self._build_layout()
        await interaction.response.edit_message(view=self)

    async def _on_sort_pr(self, interaction: discord.Interaction):
        if self.sort_by == "pickrate":
            await interaction.response.defer()
            return
        self.sort_by = "pickrate"
        self.page = 0
        self._process_and_sort_data()
        self._build_layout()
        await interaction.response.edit_message(view=self)

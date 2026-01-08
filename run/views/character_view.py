"""
캐릭터 통계 UI (CharacterStatsView)

이 파일은 /통계 명령어에서 사용하는 UI를 담당해요.
캐릭터별 승률, 픽률 등을 페이지네이션으로 볼 수 있어요.
"""
import discord
from typing import Dict, Any, List

from run.services.eternal_return.api_client import game_data, get_character_stats


class CharacterStatsView(discord.ui.View):
    """
    캐릭터 통계 페이지네이션 UI

    캐릭터별 통계를 10개씩 페이지로 나눠서 보여줘요.
    버튼으로 페이지 이동, 기간/정렬 전환이 가능해요.
    """
    def __init__(self, stats_data: Dict[str, Any], period: int, page: int = 0, sort_by: str = "tier"):
        super().__init__(timeout=120)
        self.stats_data = stats_data
        self.period = period
        self.page = page
        self.sort_by = sort_by  # "tier", "winrate", "pickrate"
        self.max_items_per_page = 10

        self._process_and_sort_data()
        self.update_buttons()

    def _process_and_sort_data(self):
        """데이터 가공 및 정렬"""
        raw_stats = self.stats_data.get("characterStatSnapshot", {}).get("characterStats", [])
        total_games_all = sum(c.get("count", 0) for c in raw_stats)

        self.processed_chars = []
        for char_stat in raw_stats:
            char_id = char_stat.get("key", 0)
            games = char_stat.get("count", 0)

            # 무기 스탯에서 승률/티어 계산
            weapon_stats = char_stat.get("weaponStats", [])
            if weapon_stats:
                # 모든 무기 합산
                total_wins = sum(w.get("win", 0) for w in weapon_stats)
                total_weapon_games = sum(w.get("count", 0) for w in weapon_stats)
                win_rate = (total_wins / total_weapon_games * 100) if total_weapon_games > 0 else 0

                # 첫 번째 무기의 티어 점수 사용
                tier_score = weapon_stats[0].get("tierScore", 0)
                tier = weapon_stats[0].get("tier", "?")
            else:
                win_rate = 0
                tier_score = 0
                tier = "?"

            pick_rate = (games / total_games_all * 100) if total_games_all > 0 else 0

            self.processed_chars.append({
                "char_id": char_id,
                "name": game_data.get_character_name(char_id),
                "games": games,
                "win_rate": win_rate,
                "pick_rate": pick_rate,
                "tier_score": tier_score,
                "tier": tier
            })

        # 정렬
        if self.sort_by == "winrate":
            self.processed_chars.sort(key=lambda x: x["win_rate"], reverse=True)
        elif self.sort_by == "pickrate":
            self.processed_chars.sort(key=lambda x: x["pick_rate"], reverse=True)
        else:  # tier
            self.processed_chars.sort(key=lambda x: x["tier_score"], reverse=True)

        self.total_pages = max(1, (len(self.processed_chars) - 1) // self.max_items_per_page + 1)

    def update_buttons(self):
        """버튼 상태 업데이트"""
        self.prev_button.disabled = self.page == 0
        self.next_button.disabled = self.page >= self.total_pages - 1

        # 기간 버튼 스타일
        self.period_3d_button.style = discord.ButtonStyle.primary if self.period == 3 else discord.ButtonStyle.secondary
        self.period_7d_button.style = discord.ButtonStyle.primary if self.period == 7 else discord.ButtonStyle.secondary

        # 정렬 버튼 스타일
        self.sort_tier_button.style = discord.ButtonStyle.primary if self.sort_by == "tier" else discord.ButtonStyle.secondary
        self.sort_winrate_button.style = discord.ButtonStyle.primary if self.sort_by == "winrate" else discord.ButtonStyle.secondary
        self.sort_pickrate_button.style = discord.ButtonStyle.primary if self.sort_by == "pickrate" else discord.ButtonStyle.secondary

    def create_embed(self) -> discord.Embed:
        """현재 페이지의 캐릭터 통계 임베드 생성"""
        sort_names = {"tier": "티어순", "winrate": "승률순", "pickrate": "픽률순"}
        sort_name = sort_names.get(self.sort_by, "티어순")

        embed = discord.Embed(
            title=f"캐릭터 통계 - {sort_name}",
            description="",
            color=0x00CED1
        )

        start_idx = self.page * self.max_items_per_page
        end_idx = start_idx + self.max_items_per_page
        page_chars = self.processed_chars[start_idx:end_idx]

        lines = []
        for i, char in enumerate(page_chars, start_idx + 1):
            name = char["name"]
            tier = char["tier"]
            win_rate = char["win_rate"]
            pick_rate = char["pick_rate"]
            games = char["games"]

            # 정렬 기준에 따라 강조 표시
            if self.sort_by == "winrate":
                lines.append(f"`{i:2d}` **{name}** - 승률 **{win_rate:.1f}%** | 픽률 {pick_rate:.1f}% | {tier}티어")
            elif self.sort_by == "pickrate":
                lines.append(f"`{i:2d}` **{name}** - 픽률 **{pick_rate:.1f}%** | 승률 {win_rate:.1f}% | {tier}티어")
            else:  # tier
                lines.append(f"`{i:2d}` **{name}** - {tier}티어 | 승률 {win_rate:.1f}% | 픽률 {pick_rate:.1f}%")

        embed.description = "\n".join(lines)

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

        embed.set_footer(text=f"다이아+ | {self.period}일 | 패치 {patch_version} | {tier_game_count:,}게임 | {self.page + 1}/{self.total_pages}")

        return embed

    # Row 0: 페이지 이동 + 기간
    @discord.ui.button(label="◀", style=discord.ButtonStyle.primary, row=0)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="▶", style=discord.ButtonStyle.primary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.total_pages - 1:
            self.page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="3일", style=discord.ButtonStyle.secondary, row=0)
    async def period_3d_button(self, interaction: discord.Interaction, button: discord.ui.Button):
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
            self.update_buttons()
            await interaction.edit_original_response(embed=self.create_embed(), view=self)

    @discord.ui.button(label="7일", style=discord.ButtonStyle.primary, row=0)
    async def period_7d_button(self, interaction: discord.Interaction, button: discord.ui.Button):
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
            self.update_buttons()
            await interaction.edit_original_response(embed=self.create_embed(), view=self)

    # Row 1: 정렬 기준
    @discord.ui.button(label="티어순", style=discord.ButtonStyle.primary, row=1)
    async def sort_tier_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.sort_by == "tier":
            await interaction.response.defer()
            return

        self.sort_by = "tier"
        self.page = 0
        self._process_and_sort_data()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="승률순", style=discord.ButtonStyle.secondary, row=1)
    async def sort_winrate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.sort_by == "winrate":
            await interaction.response.defer()
            return

        self.sort_by = "winrate"
        self.page = 0
        self._process_and_sort_data()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="픽률순", style=discord.ButtonStyle.secondary, row=1)
    async def sort_pickrate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.sort_by == "pickrate":
            await interaction.response.defer()
            return

        self.sort_by = "pickrate"
        self.page = 0
        self._process_and_sort_data()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

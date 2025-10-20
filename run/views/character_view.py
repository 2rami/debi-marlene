"""
캐릭터 통계 UI (CharacterStatsView)

이 파일은 /통계 명령어에서 사용하는 UI를 담당해요.
캐릭터별 승률, 픽률 등을 페이지네이션으로 볼 수 있어요.
"""
import discord
from typing import Dict, Any

from run.services.eternal_return.api_client import game_data


class CharacterStatsView(discord.ui.View):
    """
    캐릭터 통계 페이지네이션 UI

    캐릭터별 통계를 10개씩 페이지로 나눠서 보여줘요.
    ◀ ▶ 버튼으로 페이지를 넘길 수 있어요.
    """
    def __init__(self, stats_data: Dict[str, Any], tier: str, period: int, page: int = 0):
        super().__init__(timeout=60)
        self.stats_data = stats_data
        self.tier = tier
        self.period = period
        self.page = page
        self.max_items_per_page = 10

        character_stats = stats_data.get("characterStatSnapshot", {}).get("characterStats", [])
        self.total_pages = (len(character_stats) - 1) // self.max_items_per_page + 1

        # 버튼 업데이트
        self.update_buttons()

    def update_buttons(self):
        """페이지에 따라 버튼 활성화/비활성화"""
        # 이전 페이지 버튼
        self.prev_button.disabled = self.page == 0
        # 다음 페이지 버튼
        self.next_button.disabled = self.page >= self.total_pages - 1

    def create_embed(self) -> discord.Embed:
        """현재 페이지의 캐릭터 통계 임베드 생성"""
        tier_names = {
            "all": "전체",
            "diamond_plus": "다이아+",
            "unranked": "언랭크",
            "iron": "아이언",
            "bronze": "브론즈",
            "silver": "실버",
            "gold": "골드",
            "platinum": "플래티넘",
            "diamond": "다이아몬드"
        }
        tier_name = tier_names.get(self.tier, self.tier)

        embed = discord.Embed(
            title=f"🏆 캐릭터 통계 ({tier_name} / {self.period}일) - 페이지 {self.page + 1}/{self.total_pages}",
            color=0x00ff00
        )

        character_stats = self.stats_data.get("characterStatSnapshot", {}).get("characterStats", [])
        start_idx = self.page * self.max_items_per_page
        end_idx = start_idx + self.max_items_per_page
        page_stats = character_stats[start_idx:end_idx]

        description_lines = []
        for i, char_stat in enumerate(page_stats, start_idx + 1):
            char_id = char_stat.get("key", 0)
            char_name = game_data.get_character_name(char_id)
            count = char_stat.get("count", 0)

            # 승률 계산 (첫 번째 무기 스탯 기준)
            weapon_stats = char_stat.get("weaponStats", [])
            if weapon_stats:
                weapon = weapon_stats[0]
                wins = weapon.get("win", 0)
                total_games = weapon.get("count", 1)
                win_rate = (wins / total_games * 100) if total_games > 0 else 0
                tier_score = weapon.get("tierScore", 0)
                tier = weapon.get("tier", "?")

                description_lines.append(
                    f"`{i:2d}` **{char_name}** `{tier}티어` "
                    f"`{win_rate:.1f}%` ({count:,}게임)"
                )
            else:
                description_lines.append(f"`{i:2d}` **{char_name}** ({count:,}게임)")

        embed.description = "\n".join(description_lines)

        # 메타 정보 추가
        meta = self.stats_data.get("meta", {})
        patch = meta.get("patch", 0)
        tier_game_count = self.stats_data.get("characterStatSnapshot", {}).get("tierGameCount", 0)

        # 패치 버전 변환 (8040 -> 8.4)
        patch_str = str(patch)
        if len(patch_str) >= 3:
            patch_version = f"{patch_str[0]}.{patch_str[1:]}"
            # 끝의 0 제거 (예: 8.40 -> 8.4)
            patch_version = patch_version.rstrip('0').rstrip('.')
        else:
            patch_version = patch_str

        embed.set_footer(text=f"패치 {patch_version} | 총 {tier_game_count:,}게임 분석")

        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """이전 페이지로"""
        if self.page > 0:
            self.page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """다음 페이지로"""
        if self.page < self.total_pages - 1:
            self.page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()

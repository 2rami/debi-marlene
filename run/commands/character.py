"""
/통계 명령어

이터널 리턴 캐릭터별 통계를 보여줍니다.
다이아+ 티어 기준, 3일/7일 버튼으로 전환 가능.
"""

import discord

from run.services.eternal_return.api_client import get_character_stats
from run.views.character_view import CharacterStatsView
from run.utils.command_logger import log_command_usage


async def setup_character_command(bot):
    """
    /통계 명령어를 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """

    @bot.tree.command(name="통계", description="이터널 리턴 캐릭터별 통계를 보여줍니다 (다이아+ 기준)")
    async def character_stats(interaction: discord.Interaction):

        await interaction.response.defer()

        # 명령어 사용 로깅
        await log_command_usage(
            command_name="통계",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id if interaction.guild else None,
            guild_name=interaction.guild.name if interaction.guild else None,
            args={}
        )

        try:
            # 다이아+ / 7일 기본값
            stats_data = await get_character_stats(dt=7, team_mode="SQUAD", tier="diamond_plus")

            if not stats_data:
                await interaction.edit_original_response(content="캐릭터 통계 데이터를 가져올 수 없습니다.")
                return

            # CharacterStatsView를 사용하여 페이지네이션과 함께 표시
            view = CharacterStatsView(stats_data, period=7)
            embed = view.create_embed()
            await interaction.edit_original_response(embed=embed, view=view)

        except Exception as e:
            print(f"[오류] 캐릭터 통계 명령어 오류: {e}")
            import traceback
            traceback.print_exc()
            await interaction.edit_original_response(content="캐릭터 통계를 처리하는 중 오류가 발생했습니다.")

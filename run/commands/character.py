"""
/통계 명령어

이터널 리턴 캐릭터별 통계를 보여줍니다.
"""

import discord
from discord import app_commands

from run.services.eternal_return.api_client import get_character_stats
from run.views.character_view import CharacterStatsView


async def setup_character_command(bot):
    """
    /통계 명령어를 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """

    @bot.tree.command(name="통계", description="이터널 리턴 캐릭터별 통계를 보여줍니다")
    @app_commands.describe(
        티어="통계를 볼 티어 (기본: diamond_plus)",
        기간="통계 기간 (기본: 7일)"
    )
    @app_commands.choices(티어=[
        app_commands.Choice(name="다이아+", value="diamond_plus"),
        app_commands.Choice(name="전체", value="all"),
        app_commands.Choice(name="언랭크", value="unranked"),
        app_commands.Choice(name="아이언", value="iron"),
        app_commands.Choice(name="브론즈", value="bronze"),
        app_commands.Choice(name="실버", value="silver"),
        app_commands.Choice(name="골드", value="gold"),
        app_commands.Choice(name="플래티넘", value="platinum"),
        app_commands.Choice(name="다이아몬드", value="diamond")
    ])
    @app_commands.choices(기간=[
        app_commands.Choice(name="3일", value=3),
        app_commands.Choice(name="7일", value=7)
    ])
    async def character_stats(interaction: discord.Interaction, 티어: str = "diamond_plus", 기간: int = 7):

        await interaction.response.defer()

        try:
            import sys
            print(f"캐릭터 통계 요청: dt={기간}, tier={티어}", flush=True)
            sys.stdout.flush()
            stats_data = await get_character_stats(dt=기간, team_mode="SQUAD", tier=티어)
            print(f"캐릭터 통계 응답: {stats_data is not None}", flush=True)
            sys.stdout.flush()
            if not stats_data:
                await interaction.edit_original_response(content="[오류] 캐릭터 통계 데이터를 가져올 수 없습니다.")
                return

            # CharacterStatsView를 사용하여 페이지네이션과 함께 표시
            view = CharacterStatsView(stats_data, 티어, 기간)
            embed = view.create_embed()
            await interaction.edit_original_response(embed=embed, view=view)

        except Exception as e:
            print(f"캐릭터 통계 명령어 오류: {e}")
            import traceback
            traceback.print_exc()
            await interaction.edit_original_response(content=f"[오류] 캐릭터 통계를 처리하는 중 오류가 발생했습니다: {str(e)}")

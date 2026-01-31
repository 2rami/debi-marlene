"""
/추천 명령어

티어별 승률 높은 실험체를 추천합니다.
"""

import discord
from discord import app_commands

from run.services.eternal_return.api_client import get_character_stats, game_data
from run.utils.command_logger import log_command_usage

# 티어 한글 이름 매핑
TIER_NAMES = {
    "diamond_plus": "다이아+",
    "all": "전체",
    "unranked": "언랭크",
    "iron": "아이언",
    "bronze": "브론즈",
    "silver": "실버",
    "gold": "골드",
    "platinum": "플래티넘",
    "diamond": "다이아몬드"
}


async def setup_recommend_command(bot):
    """
    /추천 명령어를 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """

    @bot.tree.command(name="추천", description="티어별 승률 높은 실험체 Top 5를 추천합니다.")
    @app_commands.describe(
        티어="추천받을 티어 (기본: 다이아+)"
    )
    @app_commands.choices(티어=[
        app_commands.Choice(name="다이아+", value="diamond_plus"),
        app_commands.Choice(name="전체", value="all"),
        app_commands.Choice(name="아이언", value="iron"),
        app_commands.Choice(name="브론즈", value="bronze"),
        app_commands.Choice(name="실버", value="silver"),
        app_commands.Choice(name="골드", value="gold"),
        app_commands.Choice(name="플래티넘", value="platinum"),
        app_commands.Choice(name="다이아몬드", value="diamond")
    ])
    async def recommend(interaction: discord.Interaction, 티어: str = "diamond_plus"):
        await interaction.response.defer()

        # 명령어 사용 로깅
        await log_command_usage(
            command_name="추천",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id if interaction.guild else None,
            guild_name=interaction.guild.name if interaction.guild else None,
            channel_id=interaction.channel_id,
            channel_name=interaction.channel.name if interaction.channel else None,
            args={"티어": 티어}
        )

        try:
            # 7일 기준 통계 가져오기
            stats_data = await get_character_stats(dt=7, team_mode="SQUAD", tier=티어)

            if not stats_data:
                embed = discord.Embed(
                    title="오류",
                    description="실험체 통계 데이터를 가져올 수 없습니다.",
                    color=0xFF0000
                )
                await interaction.followup.send(embed=embed)
                return

            # API 응답 구조: characterStatSnapshot.characterStats[]
            character_stats = stats_data.get("characterStatSnapshot", {}).get("characterStats", [])

            if not character_stats:
                embed = discord.Embed(
                    title="오류",
                    description="실험체 통계 데이터가 없습니다.",
                    color=0xFF0000
                )
                await interaction.followup.send(embed=embed)
                return

            # 각 캐릭터의 승률 계산 및 정리
            processed_chars = []
            total_games_all = sum(c.get("count", 0) for c in character_stats)

            for char_stat in character_stats:
                char_id = char_stat.get("key", 0)
                games = char_stat.get("count", 0)

                if games < 100:  # 최소 게임 수 필터
                    continue

                # 무기 스탯에서 승률 계산 (모든 무기 합산)
                weapon_stats = char_stat.get("weaponStats", [])
                total_wins = sum(w.get("win", 0) for w in weapon_stats)
                total_weapon_games = sum(w.get("count", 0) for w in weapon_stats)

                win_rate = (total_wins / total_weapon_games * 100) if total_weapon_games > 0 else 0
                pick_rate = (games / total_games_all * 100) if total_games_all > 0 else 0

                processed_chars.append({
                    "char_id": char_id,
                    "games": games,
                    "win_rate": win_rate,
                    "pick_rate": pick_rate
                })

            # 승률 기준 내림차순 정렬
            sorted_chars = sorted(processed_chars, key=lambda x: x["win_rate"], reverse=True)

            # Top 5 추출
            top5 = sorted_chars[:5]

            # 임베드 생성
            tier_name = TIER_NAMES.get(티어, 티어)
            embed = discord.Embed(
                title=f"실험체 추천 - {tier_name}",
                description="최근 7일 승률 기준 Top 5",
                color=0x00CED1
            )

            # Top 5 실험체 정보 추가
            for i, char in enumerate(top5, 1):
                char_id = char["char_id"]
                char_name = game_data.get_character_name(char_id) if char_id else "알 수 없음"

                win_rate = char["win_rate"]
                pick_rate = char["pick_rate"]
                games = char["games"]

                # 각 실험체 정보를 필드로 추가
                embed.add_field(
                    name=f"#{i} {char_name}",
                    value=f"승률 **{win_rate:.1f}%** | 픽률 {pick_rate:.1f}% | {games:,}판",
                    inline=False
                )

            embed.set_footer(text="DAK.GG 기준 | 스쿼드 랭크")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"[오류] 추천 명령어 오류: {e}")
            import traceback
            traceback.print_exc()
            embed = discord.Embed(
                title="오류",
                description="실험체 추천 중 오류가 발생했습니다.",
                color=0xFF0000
            )
            await interaction.followup.send(embed=embed)

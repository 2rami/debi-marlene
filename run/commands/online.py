"""
/동접 명령어

Steam API로 이터널 리턴 현재 동접자 수를 조회합니다.
"""

import discord
import aiohttp

from run.utils.command_logger import log_command_usage

# 이터널 리턴 Steam App ID
ETERNAL_RETURN_APP_ID = 1049590
STEAM_API_URL = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={ETERNAL_RETURN_APP_ID}"


async def get_player_count() -> int | None:
    """Steam API로 현재 동접자 수를 가져옵니다."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(STEAM_API_URL, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("response", {}).get("result") == 1:
                        return data["response"]["player_count"]
                return None
    except Exception as e:
        print(f"[오류] Steam API 호출 실패: {e}")
        return None


async def setup_online_command(bot):
    """
    /동접 명령어를 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """

    @bot.tree.command(name="동접", description="이터널 리턴 현재 동접자 수를 확인합니다.")
    async def online(interaction: discord.Interaction):
        await interaction.response.defer()

        # 명령어 사용 로깅
        await log_command_usage(
            command_name="동접",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id if interaction.guild else None,
            guild_name=interaction.guild.name if interaction.guild else None,
            channel_id=interaction.channel_id,
            channel_name=interaction.channel.name if interaction.channel else None,
            args={}
        )

        player_count = await get_player_count()

        if player_count is not None:
            # 숫자에 천 단위 콤마 추가
            formatted_count = f"{player_count:,}"

            embed = discord.Embed(
                title="이터널 리턴 동접자",
                description=f"현재 **{formatted_count}**명이 플레이 중",
                color=0x1B2838  # Steam 색상
            )
            embed.set_thumbnail(url="https://cdn.cloudflare.steamstatic.com/steam/apps/1049590/header.jpg")
            embed.set_footer(text="Steam 기준")

            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="오류",
                description="동접자 수를 가져올 수 없습니다. 잠시 후 다시 시도해주세요.",
                color=0xFF0000
            )
            await interaction.followup.send(embed=embed)

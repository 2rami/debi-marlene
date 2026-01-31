"""
유틸리티 Cog

기타 명령어: 피드백
"""

import discord
from discord import app_commands
from discord.ext import commands

from run.core import config
from run.utils.command_logger import log_command_usage


class UtilityCog(commands.Cog, name="기타"):
    """기타 유틸리티 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="피드백", description="봇 개발자에게 피드백을 보냅니다")
    @app_commands.describe(내용="보낼 피드백 내용")
    async def feedback(self, interaction: discord.Interaction, 내용: str):
        OWNER_ID = config.OWNER_ID

        if not OWNER_ID:
            return await interaction.response.send_message(
                "죄송해요, 피드백 기능이 아직 설정되지 않았어요.",
                ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        await log_command_usage(
            command_name="피드백",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id if interaction.guild else None,
            guild_name=interaction.guild.name if interaction.guild else None,
            channel_id=interaction.channel_id,
            channel_name=interaction.channel.name if interaction.channel else None,
            args={"내용": 내용[:50] + "..." if len(내용) > 50 else 내용}
        )

        try:
            owner = await self.bot.fetch_user(int(OWNER_ID))
            embed = discord.Embed(title="새로운 피드백 도착!", description=내용, color=0xFFB6C1)
            embed.set_author(
                name=f"{interaction.user.name} ({interaction.user.id})",
                icon_url=interaction.user.display_avatar.url
            )
            if interaction.guild:
                embed.add_field(name="서버", value=f"{interaction.guild.name} ({interaction.guild.id})", inline=False)
            else:
                embed.add_field(name="서버", value="개인 메시지(DM)", inline=False)
            await owner.send(embed=embed)
            await interaction.followup.send("소중한 피드백 고마워요! 개발자에게 잘 전달했어요.", ephemeral=True)
        except (ValueError, discord.NotFound):
            await interaction.followup.send("죄송해요, 개발자 정보를 찾을 수 없어서 피드백을 보낼 수 없어요.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("개발자에게 DM을 보낼 수 없도록 설정되어 있어 전달에 실패했어요.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"피드백 전송 중 오류가 발생했어요: {e}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(UtilityCog(bot))

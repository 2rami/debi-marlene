"""
유튜브 & 설정 Cog

/설정 명령어: 서버 설정 통합 UI (공지 채널, TTS, DM 알림, 대시보드)
"""

import discord
from discord import app_commands
from discord.ext import commands

from run.core import config
from run.views.settings_view import SettingsLayoutView
from run.utils.command_logger import log_command_usage


class YoutubeCog(commands.Cog, name="유튜브"):
    """유튜브 알림 및 서버 설정 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="설정", description="서버 설정을 관리합니다 (공지 채널, TTS, 알림, 대시보드)")
    async def settings_command(self, interaction: discord.Interaction):
        try:
            await log_command_usage(
                command_name="설정",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
                args={}
            )

            if not interaction.guild:
                await interaction.response.send_message(
                    "서버에서만 사용할 수 있는 명령어예요!",
                    ephemeral=True
                )
                return

            is_admin = interaction.user.guild_permissions.administrator
            view = SettingsLayoutView(interaction.guild, interaction.user.id, is_admin)
            await interaction.response.send_message(view=view, ephemeral=True)

        except Exception as e:
            print(f"[오류] 설정 명령어 오류: {e}", flush=True)
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(f"오류가 발생했어요: {e}", ephemeral=True)
                else:
                    await interaction.response.send_message(f"오류가 발생했어요: {e}", ephemeral=True)
            except:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(YoutubeCog(bot))

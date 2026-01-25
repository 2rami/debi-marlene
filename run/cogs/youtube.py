"""
유튜브 Cog

유튜브 알림 명령어: 알림, 테스트
"""

import discord
from discord import app_commands
from discord.ext import commands

from run.core import config
from run.utils.command_logger import log_command_usage


class YoutubeCog(commands.GroupCog, group_name="유튜브"):
    """유튜브 알림 관련 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="알림", description="[개인] 새 영상 알림을 DM으로 받거나 해제합니다")
    @app_commands.describe(받기="알림을 받을지 여부")
    async def subscribe_youtube(self, interaction: discord.Interaction, 받기: bool):
        try:
            await log_command_usage(
                command_name="유튜브알림",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                args={"받기": 받기}
            )

            user_name = interaction.user.display_name or interaction.user.global_name or interaction.user.name
            config.set_youtube_subscription(interaction.user.id, 받기, user_name)
            message = "[완료] 이제부터 새로운 영상이 올라오면 DM으로 알려드릴게요!" if 받기 else "[완료] 유튜브 DM 알림을 해제했습니다."
            await interaction.response.send_message(message, ephemeral=True)
        except Exception as e:
            print(f"[오류] 유튜브알림 명령어 오류: {e}", flush=True)
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(f"오류가 발생했어요: {e}", ephemeral=True)
                else:
                    await interaction.response.send_message(f"오류가 발생했어요: {e}", ephemeral=True)
            except Exception as followup_error:
                print(f"[오류] 유튜브알림 오류 메시지 전송 실패: {followup_error}", flush=True)

    @app_commands.command(name="테스트", description="[관리자] 새 영상 확인을 수동으로 테스트합니다")
    @app_commands.default_permissions(administrator=True)
    async def youtube_test(self, interaction: discord.Interaction):
        OWNER_ID = config.OWNER_ID

        is_owner = OWNER_ID and interaction.user.id == int(OWNER_ID)

        if interaction.guild:
            if not is_owner and not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("이 명령어는 서버 관리자만 사용할 수 있어요!", ephemeral=True)
                return

            if not is_owner:
                guild_settings = config.get_guild_settings(interaction.guild.id)
                chat_channel_id = guild_settings.get("CHAT_CHANNEL_ID")
                if chat_channel_id and interaction.channel.id != chat_channel_id:
                    allowed_channel = self.bot.get_channel(chat_channel_id)
                    await interaction.response.send_message(f"이 명령어는 {allowed_channel.mention} 채널에서만 사용할 수 있어요!", ephemeral=True)
                    return

        await interaction.response.defer(ephemeral=True)

        await log_command_usage(
            command_name="유튜브테스트",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id if interaction.guild else None,
            guild_name=interaction.guild.name if interaction.guild else None,
            args={}
        )

        try:
            from run.services import youtube_service

            if not interaction.guild:
                result = await youtube_service.manual_check_for_user(interaction.user)
                await interaction.followup.send(f"[완료] 개인 유튜브 테스트 완료!\n```{result}```", ephemeral=True)
            else:
                result = await youtube_service.manual_check_for_guild(interaction.guild)
                await interaction.followup.send(f"[완료] 서버 유튜브 테스트 완료!\n```{result}```", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"[오류] 유튜브 테스트 중 오류 발생: {e}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(YoutubeCog(bot))

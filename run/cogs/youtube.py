"""
유튜브 Cog

유튜브 알림 명령어: /알림
설정, 테스트는 버튼으로 제공
"""

import discord
from discord import app_commands
from discord.ext import commands

from run.core import config
from run.views.settings_view import SettingsView
from run.utils.command_logger import log_command_usage


class YoutubeCog(commands.Cog, name="유튜브"):
    """유튜브 알림 관련 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="알림", description="유튜브 새 영상 알림을 관리합니다")
    async def youtube_notify(self, interaction: discord.Interaction):
        try:
            await log_command_usage(
                command_name="알림",
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.name,
                guild_id=interaction.guild.id if interaction.guild else None,
                guild_name=interaction.guild.name if interaction.guild else None,
                channel_id=interaction.channel_id,
                channel_name=interaction.channel.name if interaction.channel else None,
                args={}
            )

            is_subscribed = config.is_youtube_subscribed(interaction.user.id)
            dm_status = "켜짐" if is_subscribed else "꺼짐"

            if interaction.guild:
                # 서버에서 사용: 공지 채널 + DM 알림 상태 표시
                guild_settings = config.get_guild_settings(interaction.guild.id)
                channel_id = guild_settings.get("ANNOUNCEMENT_CHANNEL_ID")
                if channel_id:
                    channel = interaction.guild.get_channel(int(channel_id))
                    channel_text = f"#{channel.name}" if channel else "설정된 채널을 찾을 수 없음"
                else:
                    channel_text = "미설정"

                embed = discord.Embed(
                    title="유튜브 알림",
                    description=f"공지 채널: **{channel_text}**\nDM 알림: **{dm_status}**",
                    color=0xFF0000
                )
            else:
                # DM에서 사용: DM 알림 상태만 표시
                embed = discord.Embed(
                    title="유튜브 알림",
                    description=f"DM 알림: **{dm_status}**",
                    color=0xFF0000
                )

            is_admin = interaction.guild and interaction.user.guild_permissions.administrator
            view = YoutubeNotifyView(interaction.user.id, is_subscribed, is_admin, interaction.guild)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        except Exception as e:
            print(f"[오류] 알림 명령어 오류: {e}", flush=True)
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(f"오류가 발생했어요: {e}", ephemeral=True)
                else:
                    await interaction.response.send_message(f"오류가 발생했어요: {e}", ephemeral=True)
            except:
                pass


class YoutubeNotifyView(discord.ui.View):
    """유튜브 알림 관리 버튼"""

    def __init__(self, user_id: int, is_subscribed: bool, is_admin: bool, guild):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.guild = guild

        # DM 알림 토글 버튼
        if is_subscribed:
            self.toggle_btn = discord.ui.Button(
                label="DM 알림 끄기", style=discord.ButtonStyle.secondary
            )
        else:
            self.toggle_btn = discord.ui.Button(
                label="DM 알림 켜기", style=discord.ButtonStyle.primary
            )
        self.toggle_btn.callback = self._toggle_dm
        self.add_item(self.toggle_btn)

        # 관리자 전용 버튼
        if is_admin and guild:
            settings_btn = discord.ui.Button(
                label="채널 설정", style=discord.ButtonStyle.secondary
            )
            settings_btn.callback = self._open_settings
            self.add_item(settings_btn)

            test_btn = discord.ui.Button(
                label="테스트", style=discord.ButtonStyle.secondary
            )
            test_btn.callback = self._run_test
            self.add_item(test_btn)

    async def _toggle_dm(self, interaction: discord.Interaction):
        user_name = interaction.user.display_name or interaction.user.global_name or interaction.user.name
        is_subscribed = config.is_youtube_subscribed(interaction.user.id)
        new_state = not is_subscribed
        config.set_youtube_subscription(interaction.user.id, new_state, user_name)

        dm_status = "켜짐" if new_state else "꺼짐"
        msg = "새로운 영상이 올라오면 DM으로 알려드릴게요!" if new_state else "DM 알림을 해제했습니다."

        if self.guild:
            guild_settings = config.get_guild_settings(self.guild.id)
            channel_id = guild_settings.get("ANNOUNCEMENT_CHANNEL_ID")
            if channel_id:
                channel = self.guild.get_channel(int(channel_id))
                channel_text = f"#{channel.name}" if channel else "설정된 채널을 찾을 수 없음"
            else:
                channel_text = "미설정"
            description = f"공지 채널: **{channel_text}**\nDM 알림: **{dm_status}**\n{msg}"
        else:
            description = f"DM 알림: **{dm_status}**\n{msg}"

        embed = discord.Embed(
            title="유튜브 알림",
            description=description,
            color=0xFF0000
        )

        # 버튼 상태 업데이트
        if new_state:
            self.toggle_btn.label = "DM 알림 끄기"
            self.toggle_btn.style = discord.ButtonStyle.secondary
        else:
            self.toggle_btn.label = "DM 알림 켜기"
            self.toggle_btn.style = discord.ButtonStyle.primary

        await interaction.response.edit_message(embed=embed, view=self)

    async def _open_settings(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("관리자만 사용할 수 있어요!", ephemeral=True)
            return

        embed = discord.Embed(
            title="서버 설정",
            description="아래 버튼으로 유튜브 공지 채널과 명령어 전용 채널을 설정하세요.",
            color=0x7289DA
        )
        embed.add_field(name="[#] 공지 채널", value="유튜브 새 영상 알림이 올라갈 채널입니다. (필수)", inline=False)
        embed.add_field(name="[*] 채팅 채널", value="봇의 명령어를 사용할 특정 채널입니다. (선택)", inline=False)
        view = SettingsView(interaction.guild)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def _run_test(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("관리자만 사용할 수 있어요!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            from run.services import youtube_service
            if not self.guild:
                result = await youtube_service.manual_check_for_user(interaction.user)
            else:
                result = await youtube_service.manual_check_for_guild(self.guild)
            await interaction.followup.send(f"테스트 완료!\n```{result}```", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"테스트 중 오류: {e}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(YoutubeCog(bot))

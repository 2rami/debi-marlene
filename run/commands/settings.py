"""
/설정 명령어

서버의 유튜브 알림 채널과 채팅 채널을 설정합니다.
"""

import discord
from discord import app_commands

from run.views.settings_view import SettingsView


async def setup_settings_command(bot):
    """
    /설정 명령어를 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """

    @bot.tree.command(name="설정", description="[관리자] 서버의 유튜브 알림 채널을 설정합니다.")
    @app_commands.default_permissions(administrator=True)
    async def settings(interaction: discord.Interaction):
        try:

            # 서버에서만 사용 가능
            if not interaction.guild:
                await interaction.response.send_message("이 명령어는 서버에서만 사용할 수 있어요!", ephemeral=True)
                return

            # 관리자 권한 체크
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("이 명령어는 서버 관리자만 사용할 수 있어요!", ephemeral=True)
                return

            # SettingsView를 사용해서 선택 UI 표시
            embed = discord.Embed(
                title="[설정] 서버 설정",
                description="아래 버튼으로 유튜브 공지 채널과 명령어 전용 채널을 설정하세요.",
                color=0x7289DA
            )
            embed.add_field(name="[#] 공지 채널", value="유튜브 새 영상 알림이 올라갈 채널입니다. (필수)", inline=False)
            embed.add_field(name="[*] 채팅 채널", value="`/전적` 등 봇의 명령어를 사용할 특정 채널입니다. 설정하지 않으면 모든 채널에서 사용 가능합니다. (선택)", inline=False)
            embed.add_field(name="[X] 알림 해제", value="설정된 유튜브 알림을 해제합니다. (공지 채널 설정 시 표시)", inline=False)
            view = SettingsView(interaction.guild)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        except Exception as e:
            print(f"[오류] 설정 명령어 오류: {e}", flush=True)
            try:
                if interaction.response.is_done():
                    await interaction.followup.send("설정 중 오류가 발생했습니다.", ephemeral=True)
                else:
                    await interaction.response.send_message("설정 중 오류가 발생했습니다.", ephemeral=True)
            except:
                pass

"""
/공지 명령어

봇 소유자가 설정된 공지 채널에 업데이트 메시지를 전송합니다.
"""

import discord
from discord import app_commands

from run.core.config import get_guild_settings, get_settings


async def setup_announcement_command(bot):
    """
    /공지 명령어를 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """

    @bot.tree.command(name="공지", description="[소유자 전용] 공지 채널에 업데이트 알림을 전송합니다.")
    @app_commands.describe(
        제목="공지 제목",
        내용="공지 내용"
    )
    async def announcement(interaction: discord.Interaction, 제목: str, 내용: str):
        try:
            # 봇 소유자만 사용 가능
            settings = get_settings()
            owner_id = settings.get('OWNER_ID')

            if str(interaction.user.id) != str(owner_id):
                await interaction.response.send_message("이 명령어는 봇 소유자만 사용할 수 있습니다.", ephemeral=True)
                return

            # 서버에서만 사용 가능
            if not interaction.guild:
                await interaction.response.send_message("이 명령어는 서버에서만 사용할 수 있어요!", ephemeral=True)
                return

            # 서버 설정 가져오기
            guild_settings = get_guild_settings(interaction.guild.id)
            announcement_channel_id = guild_settings.get('ANNOUNCEMENT_CHANNEL_ID')

            # 공지 채널이 설정되지 않은 경우
            if not announcement_channel_id:
                await interaction.response.send_message(
                    "공지 채널이 설정되지 않았습니다.\n`/설정` 명령어로 공지 채널을 먼저 설정해주세요.",
                    ephemeral=True
                )
                return

            # 공지 채널 가져오기
            announcement_channel = interaction.guild.get_channel(announcement_channel_id)

            # 채널이 존재하지 않거나 접근할 수 없는 경우
            if not announcement_channel:
                await interaction.response.send_message(
                    f"공지 채널(ID: {announcement_channel_id})을 찾을 수 없거나 접근할 수 없습니다.\n"
                    "`/설정` 명령어로 공지 채널을 다시 설정해주세요.",
                    ephemeral=True
                )
                return

            # 봇이 해당 채널에 메시지를 보낼 권한이 있는지 확인
            permissions = announcement_channel.permissions_for(interaction.guild.me)
            if not permissions.send_messages:
                await interaction.response.send_message(
                    f"공지 채널({announcement_channel.mention})에 메시지를 보낼 권한이 없습니다.\n"
                    "채널 권한을 확인해주세요.",
                    ephemeral=True
                )
                return

            # 공지 임베드 생성
            embed = discord.Embed(
                title=제목,
                description=내용,
                color=0xFF6B6B  # 부드러운 빨강색
            )

            # 타임스탬프 추가
            embed.timestamp = discord.utils.utcnow()

            # 공지 메시지 전송
            try:
                await announcement_channel.send(embed=embed)
                await interaction.response.send_message(
                    f"공지가 {announcement_channel.mention}에 전송되었습니다!",
                    ephemeral=True
                )
                print(f"[공지] {interaction.user.name}님이 공지 전송: {제목}", flush=True)

            except discord.Forbidden:
                await interaction.response.send_message(
                    f"공지 채널({announcement_channel.mention})에 메시지를 보낼 권한이 없습니다.",
                    ephemeral=True
                )
            except discord.HTTPException as e:
                await interaction.response.send_message(
                    f"메시지 전송 중 오류가 발생했습니다: {e}",
                    ephemeral=True
                )

        except Exception as e:
            print(f"[오류] 공지 명령어 오류: {e}", flush=True)
            try:
                if interaction.response.is_done():
                    await interaction.followup.send("공지 전송 중 오류가 발생했습니다.", ephemeral=True)
                else:
                    await interaction.response.send_message("공지 전송 중 오류가 발생했습니다.", ephemeral=True)
            except:
                pass

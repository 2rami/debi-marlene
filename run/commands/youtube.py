"""
유튜브 관련 명령어

/유튜브알림 - 개인 유튜브 알림 구독/해제
/유튜브테스트 - 관리자용 유튜브 알림 테스트
"""

import discord
from discord import app_commands

from run.core import config


async def setup_youtube_commands(bot):
    """
    유튜브 관련 명령어들을 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """

    @bot.tree.command(name="유튜브알림", description="[개인] 유튜브 새 영상 알림을 DM으로 받거나 해제합니다.")
    async def subscribe_youtube(interaction: discord.Interaction, 받기: bool):

        try:
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

    @bot.tree.command(name="유튜브테스트", description="[관리자] 유튜브 새 영상 확인을 수동으로 테스트합니다.")
    @app_commands.default_permissions(administrator=True)
    async def youtube_test(interaction: discord.Interaction):

        OWNER_ID = config.OWNER_ID

        # 개발자는 어디서든 사용 가능
        is_owner = OWNER_ID and interaction.user.id == int(OWNER_ID)

        if interaction.guild:
            # 서버에서는 관리자 권한 필요
            if not is_owner and not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("이 명령어는 서버 관리자만 사용할 수 있어요!", ephemeral=True)
                return

            # 채팅 채널 제한 체크 (개발자는 예외)
            if not is_owner:
                guild_settings = config.get_guild_settings(interaction.guild.id)
                chat_channel_id = guild_settings.get("CHAT_CHANNEL_ID")
                if chat_channel_id and interaction.channel.id != chat_channel_id:
                    allowed_channel = bot.get_channel(chat_channel_id)
                    await interaction.response.send_message(f"이 명령어는 {allowed_channel.mention} 채널에서만 사용할 수 있어요!", ephemeral=True)
                    return
        # DM에서는 누구나 사용 가능 (개인 테스트용)

        await interaction.response.defer(ephemeral=True)
        try:
            from run.services import youtube_service

            # 개인 DM에서 사용 시 해당 사용자에게만 테스트
            if not interaction.guild:
                result = await youtube_service.manual_check_for_user(interaction.user)
                await interaction.followup.send(f"[완료] 개인 유튜브 테스트 완료!\n```{result}```", ephemeral=True)
            else:
                # 서버에서 사용 시 해당 서버에만 테스트
                result = await youtube_service.manual_check_for_guild(interaction.guild)
                await interaction.followup.send(f"[완료] 서버 유튜브 테스트 완료!\n```{result}```", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"[오류] 유튜브 테스트 중 오류 발생: {e}", ephemeral=True)

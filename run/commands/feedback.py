"""
/피드백 명령어

봇 개발자에게 피드백을 보냅니다.
"""

import discord

from run.core import config


async def setup_feedback_command(bot):
    """
    /피드백 명령어를 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """

    @bot.tree.command(name="피드백", description="봇 개발자에게 피드백을 보냅니다.")
    async def feedback(interaction: discord.Interaction, 내용: str):

        OWNER_ID = config.OWNER_ID

        if not OWNER_ID:
            return await interaction.response.send_message(
                "죄송해요, 피드백 기능이 아직 설정되지 않았어요.",
                ephemeral=True
            )

        # defer로 처리 시간 확보
        await interaction.response.defer(ephemeral=True)

        try:
            owner = await bot.fetch_user(int(OWNER_ID))
            embed = discord.Embed(title="📬 새로운 피드백 도착!", description=내용, color=0xFFB6C1)
            embed.set_author(
                name=f"{interaction.user.name} ({interaction.user.id})",
                icon_url=interaction.user.display_avatar.url
            )
            if interaction.guild:
                embed.add_field(name="서버", value=f"{interaction.guild.name} ({interaction.guild.id})", inline=False)
            else:
                embed.add_field(name="서버", value="개인 메시지(DM)", inline=False)
            await owner.send(embed=embed)
            await interaction.followup.send("소중한 피드백 고마워요! 개발자에게 잘 전달했어요. ❤️", ephemeral=True)
        except (ValueError, discord.NotFound):
            await interaction.followup.send("죄송해요, 개발자 정보를 찾을 수 없어서 피드백을 보낼 수 없어요.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("개발자에게 DM을 보낼 수 없도록 설정되어 있어 전달에 실패했어요. 😥", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"피드백 전송 중 오류가 발생했어요: {e}", ephemeral=True)

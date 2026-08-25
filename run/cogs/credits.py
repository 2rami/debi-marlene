"""크레딧 슬래시 Cog.

`/크레딧` — V2 LayoutView (Container/Separator/ActionRow 분할) + application emoji.
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from run.views.credits_view import CreditsLayoutView
from run.services.credits_emoji import get_credit_emoji, format_emoji
from run.utils.command_logger import log_command_usage


class CreditsCog(commands.Cog, name="크레딧"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="크레딧", description="내 크레딧 지갑 (도박/출석은 대시보드)")
    async def credits(self, interaction: discord.Interaction):
        # ephemeral 제거 — 채널에 공개. 베팅 UI 가 봇에서 빠지면서 잔고 노출만 남아 OK.
        await interaction.response.defer()

        guild = interaction.guild

        # application emoji — 첫 호출 시 등록, 이후 캐시. 실패해도 [C] 폴백.
        emoji = await get_credit_emoji(self.bot)
        emoji_str = format_emoji(emoji)

        view = await CreditsLayoutView.create(
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=guild.id if guild else None,
            guild_name=guild.name if guild else None,
            emoji_str=emoji_str,
        )

        # 썸네일 분기·첨부 여부는 view 가 자기 잔고로 이미 정했다 — 여기서 다시 고르면
        # 렌더(Thumbnail)와 첨부가 갈려 400(50035) 이 난다.
        send_kwargs: dict = {"view": view}
        thumb = view.thumbnail_file()
        if thumb is not None:
            send_kwargs["file"] = thumb

        await interaction.followup.send(**send_kwargs)

        await log_command_usage(
            command_name="크레딧",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=guild.id if guild else None,
            guild_name=guild.name if guild else None,
            channel_id=interaction.channel_id,
            channel_name=interaction.channel.name if interaction.channel else None,
            args={},
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(CreditsCog(bot))

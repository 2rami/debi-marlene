"""이터널리턴 캐릭터 그림 Cog.

`/그림` — 참조 이미지(게임 스킨 아트)로 캐릭터를 붙잡고 배경·포즈만 새로 그린다.
요금은 **사용자 본인 OpenGateway 계정**에서 나간다. 봇은 키를 대신 들고 부를 뿐이다.
"""

from __future__ import annotations

import io
import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from run.services import og_keys
from run.services.imagegen import characters as chars_svc
from run.services.imagegen.gateway import generate_image, ImageGenError
from run.views.imagegen_view import NotConnectedView, GeneratingView, ResultView, FailedView
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

# 한 사람이 동시에 여러 장을 돌리지 못하게 막는다. 3분짜리라 연타하기 쉬운데,
# 그만큼 본인 카드에서 중복으로 나간다.
_in_flight: set[int] = set()


class ImageGenCog(commands.Cog, name="그림"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def character_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            hits = await chars_svc.search_characters(current, limit=25)
        except Exception:
            return []
        return [app_commands.Choice(name=c['name'], value=c['name']) for c in hits]

    @app_commands.command(name="그림", description="이터널리턴 캐릭터를 원하는 장면으로 그려요")
    @app_commands.describe(캐릭터="그릴 캐릭터", 요청="어떤 장면으로 그릴지 (예: 비 오는 밤 우산 쓴 모습)")
    @app_commands.autocomplete(캐릭터=character_autocomplete)
    async def draw(self, interaction: discord.Interaction, 캐릭터: str, 요청: str):
        user_id = interaction.user.id

        # 연결 안내는 남에게 보일 이유가 없다
        loop = asyncio.get_running_loop()
        api_key = await loop.run_in_executor(None, og_keys.get_key, user_id)
        if not api_key:
            return await interaction.response.send_message(view=NotConnectedView(), ephemeral=True)

        if user_id in _in_flight:
            return await interaction.response.send_message(
                view=FailedView('이미 그리는 중이에요.', '지금 것이 끝나면 다시 시도해 주세요.'),
                ephemeral=True,
            )

        character = await chars_svc.find_character(캐릭터)
        if not character:
            return await interaction.response.send_message(
                view=FailedView(f'`{캐릭터}` 라는 캐릭터를 못 찾았어요.', '목록에서 골라 주세요.'),
                ephemeral=True,
            )

        await interaction.response.defer()
        _in_flight.add(user_id)
        try:
            await interaction.edit_original_response(view=GeneratingView(character['name'], 요청))

            skin = character['skins'][0]  # 기본 스킨. 스킨 선택은 다음 단계
            reference = await chars_svc.get_reference_image(skin['image_url'])
            png = await generate_image(api_key, reference, 요청)

            await loop.run_in_executor(None, og_keys.record_use, user_id)
            status = await loop.run_in_executor(None, og_keys.get_status, user_id)

            filename = 'result.png'
            await interaction.edit_original_response(
                view=ResultView(
                    character['name'], 요청, filename,
                    calls=status.get('calls', 0), est_usd=status.get('est_usd', 0.0),
                    est_credits=status.get('est_credits', 0),
                ),
                attachments=[discord.File(io.BytesIO(png), filename=filename)],
            )
            guild = interaction.guild
            channel = interaction.channel
            await log_command_usage(
                "그림",
                user_id,
                interaction.user.display_name or interaction.user.name,
                guild_id=guild.id if guild else None,
                guild_name=guild.name if guild else None,
                channel_id=channel.id if channel else None,
                channel_name=getattr(channel, 'name', None),
                args={"캐릭터": character['name']},
            )

        except ImageGenError as e:
            await interaction.edit_original_response(view=FailedView(e.message, e.hint), attachments=[])
        except Exception as e:
            logger.exception('그림 생성 실패')
            await interaction.edit_original_response(
                view=FailedView('알 수 없는 문제가 생겼어요.', f'{type(e).__name__}'),
                attachments=[],
            )
        finally:
            _in_flight.discard(user_id)

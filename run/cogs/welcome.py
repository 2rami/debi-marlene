"""
환영/작별 메시지 Cog

멤버 입장/퇴장 시 설정된 채널에 메시지를 전송합니다.
- 텍스트 메시지 (변수 치환 지원)
- 이미지 메시지 (커스텀 이미지 생성)
"""

import io
import discord
from discord.ext import commands
import logging

from run.core.config import load_settings
from run.services.welcome import WelcomeImageGenerator

logger = logging.getLogger(__name__)


class WelcomeCog(commands.Cog):
    """환영/작별 메시지 Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.image_generator = WelcomeImageGenerator()

    def _replace_variables(self, text: str, member: discord.Member) -> str:
        """변수 치환"""
        guild = member.guild

        replacements = {
            '@user': member.mention,
            '@server': guild.name,
            '@membercount': str(guild.member_count),
            '{break}': '\n',
        }

        result = text
        for var, value in replacements.items():
            result = result.replace(var, value)

        # 채널 멘션 처리 (#channelname -> <#channel_id>)
        import re
        channel_pattern = r'#(\w+)'
        for match in re.finditer(channel_pattern, result):
            channel_name = match.group(1)
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                result = result.replace(f'#{channel_name}', channel.mention)

        return result

    async def _get_welcome_config(self, guild_id: int) -> dict:
        """서버의 환영 설정 가져오기"""
        settings = load_settings()
        guild_settings = settings.get('guilds', {}).get(str(guild_id), {})
        dashboard_features = guild_settings.get('dashboard_features', {})

        return dashboard_features.get('welcome', {
            'enabled': False,
            'channelId': None,
            'message': '',
            'imageEnabled': False,
        })

    async def _get_goodbye_config(self, guild_id: int) -> dict:
        """서버의 작별 설정 가져오기"""
        settings = load_settings()
        guild_settings = settings.get('guilds', {}).get(str(guild_id), {})
        dashboard_features = guild_settings.get('dashboard_features', {})

        return dashboard_features.get('goodbye', {
            'enabled': False,
            'channelId': None,
            'message': '',
            'imageEnabled': False,
        })

    async def _get_image_config(self, guild_id: int, is_welcome: bool = True) -> dict:
        """서버의 이미지 설정 가져오기"""
        settings = load_settings()
        guild_settings = settings.get('guilds', {}).get(str(guild_id), {})
        dashboard_features = guild_settings.get('dashboard_features', {})

        key = 'welcome_image_config' if is_welcome else 'goodbye_image_config'
        return dashboard_features.get(key, {})

    async def _get_background_image(self, guild_id: int, is_welcome: bool = True) -> bytes | None:
        """GCS에서 배경 이미지 다운로드"""
        try:
            from google.cloud import storage
            client = storage.Client(project='ironic-objectivist-465713-a6')
            bucket = client.bucket('debi-marlene-settings')

            key = 'welcome' if is_welcome else 'goodbye'
            blob_name = f'welcome_images/{guild_id}_{key}_bg.png'

            blob = bucket.blob(blob_name)
            if blob.exists():
                return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"[Welcome] 배경 이미지 다운로드 실패: {e}")

        return None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """멤버 입장 이벤트"""
        if member.bot:
            return

        guild = member.guild
        config = await self._get_welcome_config(guild.id)

        text_enabled = config.get('enabled', False)
        image_enabled = config.get('imageEnabled', False)

        if not text_enabled and not image_enabled:
            return

        channel_id = config.get('channelId')
        if not channel_id:
            return

        channel = guild.get_channel(int(channel_id))
        if not channel:
            logger.warning(f"[Welcome] 채널을 찾을 수 없음: {channel_id}")
            return

        try:
            files = []
            content = None

            # 이미지 메시지
            if image_enabled:
                avatar_url = member.display_avatar.url
                image_config = await self._get_image_config(guild.id, is_welcome=True)
                background = await self._get_background_image(guild.id, is_welcome=True)

                image_bytes = await self.image_generator.generate(
                    user_name=member.display_name,
                    user_avatar_url=avatar_url,
                    server_name=guild.name,
                    member_count=guild.member_count,
                    is_welcome=True,
                    config=image_config,
                    background_image=background,
                )

                files.append(discord.File(io.BytesIO(image_bytes), filename='welcome.png'))

            # 텍스트 메시지
            if text_enabled:
                message = config.get('message', '')
                if message:
                    content = self._replace_variables(message, member)
                else:
                    content = f"{member.mention}님, **{guild.name}**에 오신 것을 환영합니다!"

            await channel.send(content=content, files=files if files else None)
            logger.info(f"[Welcome] 환영 메시지 전송: {guild.name} - {member.name}")

        except Exception as e:
            logger.error(f"[Welcome] 환영 메시지 전송 실패: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """멤버 퇴장 이벤트"""
        if member.bot:
            return

        guild = member.guild
        config = await self._get_goodbye_config(guild.id)

        text_enabled = config.get('enabled', False)
        image_enabled = config.get('imageEnabled', False)

        if not text_enabled and not image_enabled:
            return

        channel_id = config.get('channelId')
        if not channel_id:
            return

        channel = guild.get_channel(int(channel_id))
        if not channel:
            logger.warning(f"[Welcome] 채널을 찾을 수 없음: {channel_id}")
            return

        try:
            files = []
            content = None

            # 이미지 메시지
            if image_enabled:
                avatar_url = member.display_avatar.url
                image_config = await self._get_image_config(guild.id, is_welcome=False)
                background = await self._get_background_image(guild.id, is_welcome=False)

                image_bytes = await self.image_generator.generate(
                    user_name=member.display_name,
                    user_avatar_url=avatar_url,
                    server_name=guild.name,
                    member_count=guild.member_count,
                    is_welcome=False,
                    config=image_config,
                    background_image=background,
                )

                files.append(discord.File(io.BytesIO(image_bytes), filename='goodbye.png'))

            # 텍스트 메시지
            if text_enabled:
                message = config.get('message', '')
                if message:
                    content = self._replace_variables(message, member)
                else:
                    content = f"**{member.display_name}**님이 서버를 떠났습니다."

            await channel.send(content=content, files=files if files else None)
            logger.info(f"[Welcome] 작별 메시지 전송: {guild.name} - {member.name}")

        except Exception as e:
            logger.error(f"[Welcome] 작별 메시지 전송 실패: {e}")


async def setup(bot: commands.Bot):
    """Cog 로드"""
    await bot.add_cog(WelcomeCog(bot))

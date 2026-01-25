"""
Discord 봇 Cog 모음

슬래시 명령어 자동완성에서 카테고리별로 분류됩니다.
"""

from run.cogs.eternal_return import EternalReturnCog
from run.cogs.voice import VoiceCog
from run.cogs.music import MusicCog
from run.cogs.youtube import YoutubeCog
from run.cogs.settings import SettingsCog
from run.cogs.utility import UtilityCog


async def setup_all_cogs(bot):
    """모든 Cog를 봇에 등록합니다."""
    await bot.add_cog(EternalReturnCog(bot))
    await bot.add_cog(VoiceCog(bot))
    await bot.add_cog(MusicCog(bot))
    await bot.add_cog(YoutubeCog(bot))
    await bot.add_cog(SettingsCog(bot))
    await bot.add_cog(UtilityCog(bot))

    print("[완료] 모든 Cog 등록 완료")


__all__ = [
    'setup_all_cogs',
    'EternalReturnCog',
    'VoiceCog',
    'MusicCog',
    'YoutubeCog',
    'SettingsCog',
    'UtilityCog',
]

"""
Discord 봇 명령어 모음

이 패키지에는 봇의 모든 슬래시 명령어가 포함되어 있습니다.
"""

from run.commands.stats import setup_stats_command
from run.commands.character import setup_character_command
from run.commands.settings import setup_settings_command
from run.commands.youtube import setup_youtube_commands
from run.commands.feedback import setup_feedback_command
from run.commands.voice import setup_voice_commands
from run.commands.announcement import setup_announcement_command


async def register_all_commands(bot):
    """
    모든 명령어를 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """
    await setup_stats_command(bot)
    await setup_character_command(bot)
    await setup_settings_command(bot)
    await setup_youtube_commands(bot)
    await setup_feedback_command(bot)
    await setup_voice_commands(bot)
    await setup_announcement_command(bot)

    print("[완료] 모든 명령어 등록 완료")


__all__ = [
    'register_all_commands',
    'setup_stats_command',
    'setup_character_command',
    'setup_settings_command',
    'setup_youtube_commands',
    'setup_feedback_command',
    'setup_voice_commands',
    'setup_announcement_command',
]

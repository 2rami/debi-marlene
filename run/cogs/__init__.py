"""
Discord 봇 Cog 모음

슬래시 명령어 자동완성에서 카테고리별로 분류됩니다.
"""

from run.cogs.chat import ChatCog
from run.cogs.chime_in import ChimeInCog
from run.core import config


async def setup_all_cogs(bot):
    """Cog 등록. BOT_IDENTITY에 따라 등록 범위가 달라짐.

    - unified(기존봇): 전체 Cog 등록 — voice_listen 등 무거운 모듈은 **lazy import**
      (솔로봇 프로세스에서 webrtcvad/pkg_resources 같은 불필요 의존성이 import되어
      크래시 나는 걸 방지). ChatCog, ChimeInCog는 솔로에서도 쓰므로 top-level import 유지.
    - debi/marlene 솔로봇: ChatCog + ChimeInCog만 등록 — 대화·끼어들기 전용.
    """
    identity = config.BOT_IDENTITY
    if identity in ("debi", "marlene"):
        await bot.add_cog(ChatCog(bot))
        await bot.add_cog(ChimeInCog(bot))
        # ChatCog의 @app_commands.command "대화"가 자동 등록되지만, 솔로봇은 키워드 트리거만
        # 쓰므로 tree에서 제거 → sync 시 솔로 프로필에 슬래시 명령어 노출 안 됨.
        try:
            bot.tree.remove_command("대화")
        except Exception:
            pass
        print(f"[완료] 솔로봇 Cog 등록 완료 (identity={identity}, chat+chime 전용)")
        return

    # unified (기존 데비&마를렌 봇): 전체 등록 — 여기서만 무거운 모듈 import
    from run.cogs.eternal_return import EternalReturnCog
    from run.cogs.voice import VoiceCog
    from run.cogs.music import MusicCog
    from run.cogs.youtube import YoutubeCog
    from run.cogs.utility import UtilityCog
    from run.cogs.welcome import WelcomeCog
    from run.cogs.stats import StatsCog
    from run.cogs.quiz import QuizCog
    from run.cogs.voice_listen import VoiceListenCog
    from run.cogs.credits import CreditsCog

    await bot.add_cog(EternalReturnCog(bot))
    await bot.add_cog(VoiceCog(bot))
    await bot.add_cog(MusicCog(bot))
    await bot.add_cog(YoutubeCog(bot))
    await bot.add_cog(UtilityCog(bot))
    await bot.add_cog(WelcomeCog(bot))
    await bot.add_cog(StatsCog(bot))
    await bot.add_cog(QuizCog(bot))
    await bot.add_cog(ChatCog(bot))
    await bot.add_cog(ChimeInCog(bot))
    await bot.add_cog(VoiceListenCog(bot))
    await bot.add_cog(CreditsCog(bot))

    print("[완료] 모든 Cog 등록 완료")


__all__ = [
    'setup_all_cogs',
    'ChatCog',
    'ChimeInCog',
]

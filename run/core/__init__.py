"""
Core module for Discord bot

이 패키지에는 봇 인스턴스, 설정, 이벤트 핸들러가 포함되어 있습니다.
"""

from run.core import config

# bot은 선택적 import (웹패널에서는 불필요)
try:
    from run.core.bot import bot
    __all__ = ['bot', 'config']
except ImportError:
    bot = None
    __all__ = ['config']

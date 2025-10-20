"""
Core module for Discord bot

이 패키지에는 봇 인스턴스, 설정, 이벤트 핸들러가 포함되어 있습니다.
"""

from run.core.bot import bot
from run.core import config

__all__ = ['bot', 'config']

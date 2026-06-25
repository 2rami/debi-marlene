"""이탈 설문 — 봇 추방 시 owner DM 으로 Discord Poll(투표) + 재초대 버튼.

Poll 은 Discord 가 서버사이드로 관리해 봇 재시작과 무관하고 "상호작용 실패"가
나지 않는다. 투표 결과는 on_raw_poll_vote_add 이벤트로 수집한다(run/core/bot.py).

재초대 버튼은 link button — 인터랙션을 발생시키지 않으므로 persistent 등록이
필요 없고 봇이 죽어도 작동한다.

일러스트: Poll/메시지엔 자유 이미지 첨부가 제한적이라, 일러는 추후 content 상단
첨부 또는 별도 메시지로 검토. 지금은 텍스트만.
"""
from __future__ import annotations

import os
from datetime import timedelta
from typing import Optional

import discord

from run.services import churn as churn_service

# 재초대 권한 비트(기존 on_guild_remove 값과 동일).
_INVITE_PERMISSIONS = 412317273088

# Poll 최대 기간(디스코드 상한 7일). churn 은 추방 직후 응답률이 가장 높음.
_POLL_DURATION = timedelta(days=7)


def invite_url_for(client: Optional[discord.Client]) -> Optional[str]:
    """재초대 OAuth URL. BOT_INVITE_URL 우선, 없으면 client 로 구성."""
    env = os.getenv("BOT_INVITE_URL")
    if env:
        return env
    if client and client.user:
        return (
            f"https://discord.com/oauth2/authorize"
            f"?client_id={client.user.id}&permissions={_INVITE_PERMISSIONS}"
            f"&scope=bot+applications.commands"
        )
    return None


def build_churn_poll() -> discord.Poll:
    """이탈 사유 투표 Poll. 복수 선택, 7일. answer 순서 = CHURN_REASONS 순서."""
    poll = discord.Poll(
        question="왜 내보내셨나요? (여러 개 선택 가능)",
        duration=_POLL_DURATION,
        multiple=True,
    )
    for _value, label in churn_service.CHURN_REASONS:
        poll.add_answer(text=label)
    return poll


class ChurnRejoinView(discord.ui.View):
    """재초대 link button 만 있는 뷰. link button 은 봇 재시작과 무관하게 작동."""

    def __init__(self, invite_url: Optional[str] = None):
        super().__init__(timeout=None)
        if invite_url:
            self.add_item(
                discord.ui.Button(
                    label="다시 추가하기",
                    style=discord.ButtonStyle.link,
                    url=invite_url,
                )
            )

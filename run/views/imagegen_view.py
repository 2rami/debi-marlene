"""이미지 생성 화면 — 연결 안내 / 그리는 중 / 결과.

Container 가 Embed 를 대신한다(V2). 결과 이미지는 첨부로 올리고 화면에서는
`attachment://` 로 가리킨다.
"""

from __future__ import annotations

import discord

from run.services.og_keys import KRW_PER_IMAGE

ACCENT_WAIT = 0x5B6EE1     # 대기 — 차분한 파랑
ACCENT_DONE = 0x4CAF7D     # 완료 — 초록
ACCENT_WARN = 0xE1A05B     # 안내·실패 — 주황

DASHBOARD_URL = 'https://debimarlene.com/settings'
OG_SIGNUP_URL = 'https://opengateway.ai'


class NotConnectedView(discord.ui.LayoutView):
    """키가 없을 때. 무엇을 하면 되는지만 짧게 — 길면 안 읽는다."""

    def __init__(self):
        super().__init__(timeout=None)
        box = discord.ui.Container(accent_colour=ACCENT_WARN)
        box.add_item(discord.ui.TextDisplay(
            '## 그림을 그리려면 연결이 한 번 필요해요\n'
            '이미지 생성은 **본인 계정으로 직접 결제**해요. '
            '봇이 대신 받지 않고, 쓴 만큼만 본인 카드에서 나가요.\n\n'
            '**1.** OpenGateway 에 가입하고 키를 받아요 (약 3분)\n'
            '**2.** 대시보드에 키를 붙여넣으면 끝이에요\n\n'
            f'-# 한 장에 약 {KRW_PER_IMAGE}원이에요. 5달러 넣으면 100장쯤 그려요.'
        ))
        box.add_item(discord.ui.Separator())
        row = discord.ui.ActionRow()
        row.add_item(discord.ui.Button(label='키 받으러 가기', style=discord.ButtonStyle.link, url=OG_SIGNUP_URL))
        row.add_item(discord.ui.Button(label='대시보드에서 연결', style=discord.ButtonStyle.link, url=DASHBOARD_URL))
        box.add_item(row)
        self.add_item(box)


class GeneratingView(discord.ui.LayoutView):
    """그리는 중. 3분이 걸리므로 얼마나 걸리는지를 반드시 밝힌다 —
    말 안 하면 먹통으로 읽고 다시 친다(그만큼 돈이 또 나간다)."""

    def __init__(self, character: str, request: str, cost_krw: int = KRW_PER_IMAGE):
        super().__init__(timeout=None)
        box = discord.ui.Container(accent_colour=ACCENT_WAIT)
        box.add_item(discord.ui.TextDisplay(
            f'## {character} 를 그리는 중이에요\n'
            f'> {request[:180]}\n\n'
            f'**약 3분** 걸려요. 다 되면 이 메시지가 그림으로 바뀌어요.\n'
            f'-# 약 {cost_krw}원 · 본인 OG 계정에서 결제돼요'
        ))
        self.add_item(box)


class ResultView(discord.ui.LayoutView):
    """완성. 이미지는 첨부로 올라가고 여기서는 가리키기만 한다."""

    def __init__(self, character: str, request: str, filename: str,
                 calls: int, est_usd: float, est_krw: int = 0):
        super().__init__(timeout=None)
        box = discord.ui.Container(accent_colour=ACCENT_DONE)
        box.add_item(discord.ui.TextDisplay(f'## {character}\n> {request[:180]}'))
        box.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(f'attachment://{filename}')
        ))
        box.add_item(discord.ui.TextDisplay(
            f'-# 지금까지 {calls}장 · 약 {est_krw:,}원 (${est_usd:.2f}, 본인 OG 계정)'
        ))
        self.add_item(box)


class FailedView(discord.ui.LayoutView):
    """실패. 무엇을 하면 되는지(hint)가 없으면 사용자는 그냥 떠난다."""

    def __init__(self, message: str, hint: str = ''):
        super().__init__(timeout=None)
        box = discord.ui.Container(accent_colour=ACCENT_WARN)
        text = f'## 그리지 못했어요\n{message}'
        if hint:
            text += f'\n\n{hint}'
        box.add_item(discord.ui.TextDisplay(text))
        self.add_item(box)

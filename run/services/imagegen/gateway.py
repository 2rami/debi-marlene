"""OpenGateway 이미지 생성 호출.

사용자 본인 API 키로 부른다 — 요금은 키 주인에게 청구되고 봇은 원가를 지지 않는다.
참조 이미지를 함께 보내는 `/v1/images/edits` 를 쓴다(마스크 편집이 아니라 참조 기반 생성).
"""

from __future__ import annotations

import base64
from typing import Optional

import aiohttp

OG_HOST = 'https://apis.opengateway.ai'
MODEL = 'openai/gpt-image-2'

# 실측 163초. 게이트웨이가 느린 게 아니라 모델이 그만큼 걸린다.
TIMEOUT_SEC = 300

# 참조가 캐릭터를 붙잡고 프롬프트가 상황을 바꾼다. "정체성은 두고 배경·포즈만" 을
# 명시해야 얼굴이 안 흔들린다(2026-08-25 실측으로 확인한 문구).
PROMPT_TEMPLATE = (
    '이 참조 이미지 속 캐릭터의 얼굴·헤어스타일·머리색·의상 디자인을 그대로 유지하면서, '
    '{request} 장면으로 다시 그려라. '
    '캐릭터의 정체성(생김새와 옷)은 절대 바꾸지 말고, 배경과 포즈만 새로 그린다. '
    '고품질 애니메이션 일러스트 스타일.'
)


class ImageGenError(Exception):
    """사용자에게 그대로 보여줄 수 있는 실패. `hint` 로 다음 행동을 알려 준다."""

    def __init__(self, message: str, *, hint: str = '', retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.retryable = retryable


def build_prompt(request: str) -> str:
    return PROMPT_TEMPLATE.format(request=request.strip())


def _explain(status: int, body: str) -> ImageGenError:
    """게이트웨이 응답을 사용자가 읽을 말로 옮긴다."""
    if status == 401:
        return ImageGenError(
            '키가 거부됐어요.',
            hint='키가 바뀌었을 수 있어요. 대시보드에서 다시 등록해 주세요.',
        )
    if status in (402, 403):
        # 잔액이 0 이면 키가 정지 상태가 되고, 충전하면 자동으로 풀린다
        return ImageGenError(
            '잔액이 부족하거나 키가 정지됐어요.',
            hint='opengateway.ai 에서 충전하면 바로 다시 쓸 수 있어요.',
        )
    if status == 413:
        return ImageGenError('참조 이미지가 너무 커요.', hint='잠시 뒤 다시 시도해 주세요.')
    if status == 429:
        return ImageGenError(
            '지금 요청이 몰렸어요.',
            hint='1분쯤 뒤에 다시 시도해 주세요.',
            retryable=True,
        )
    if status >= 500:
        return ImageGenError('생성 서버에 문제가 있어요.', hint='잠시 뒤 다시 시도해 주세요.', retryable=True)
    # 400 대는 대개 프롬프트가 정책에 걸린 경우다
    snippet = (body or '')[:160]
    return ImageGenError('그림을 만들지 못했어요.', hint=f'요청을 바꿔서 다시 해 보세요. ({snippet})')


async def generate_image(
    api_key: str,
    reference_jpeg: bytes,
    request: str,
    *,
    size: str = '1024x1024',
    quality: str = 'high',
) -> bytes:
    """PNG 바이트를 돌려준다. 실패는 ImageGenError 로 올린다."""
    form = aiohttp.FormData()
    # filename·MIME 이 없으면 게이트웨이가 400 을 준다(파트 형식 검증)
    form.add_field('image', reference_jpeg, filename='ref.jpg', content_type='image/jpeg')
    form.add_field('model', MODEL)
    form.add_field('prompt', build_prompt(request))
    form.add_field('size', size)
    form.add_field('n', '1')
    form.add_field('quality', quality)
    # input_fidelity 는 보내지 않는다 — gpt-image-2 는 항상 고충실도라 값을 받지 않는다

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{OG_HOST}/v1/images/edits',
                headers={'Authorization': f'Bearer {api_key}'},
                data=form,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT_SEC),
            ) as r:
                body = await r.text()
                if r.status != 200:
                    raise _explain(r.status, body)
                import json
                payload = json.loads(body)
    except aiohttp.ClientError as e:
        raise ImageGenError('생성 서버에 닿지 못했어요.', hint='잠시 뒤 다시 시도해 주세요.', retryable=True) from e
    except TimeoutError as e:
        raise ImageGenError('시간이 너무 오래 걸렸어요.', hint='잠시 뒤 다시 시도해 주세요.', retryable=True) from e

    try:
        return base64.b64decode(payload['data'][0]['b64_json'])
    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise ImageGenError('응답을 읽지 못했어요.', hint='잠시 뒤 다시 시도해 주세요.', retryable=True) from e


async def verify_key(api_key: str) -> tuple[bool, str]:
    """등록할 때 키가 살아 있는지 본다.

    그림을 한 장 뽑아 보면 확실하지만 3분이 걸리고 돈이 나간다. 모델 목록 조회는
    공짜이고 인증만 확인하면 되므로 그걸로 가른다.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{OG_HOST}/v1/models',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=aiohttp.ClientTimeout(total=20),
            ) as r:
                if r.status == 200:
                    return True, ''
                if r.status == 401:
                    return False, '키가 올바르지 않아요.'
                if r.status in (402, 403):
                    return False, '키는 맞지만 잔액이 없거나 정지 상태예요. 충전 후 다시 시도해 주세요.'
                return False, f'확인하지 못했어요 (HTTP {r.status}).'
    except Exception as e:
        return False, f'확인 중 오류가 났어요: {e}'

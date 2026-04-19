"""Anthropic Claude API를 직접 호출하는 ChatClient.

Modal(Gemma4 LoRA) 대안 백엔드. 인터페이스(`chat`, `health_check`, `close`)는
`ChatClient`와 동일해서 `build_chat_agent(client)`에 그대로 주입 가능.

캐릭터 일관성: LoRA 파인튜닝 대신 시스템 프롬프트 + few-shot으로 유도.
비용 최적화: 시스템 프롬프트에 cache_control 적용 (5분 TTL, 2번째 호출부터 읽기비용 90% 절감).
"""

import logging
import os
from typing import Optional

import anthropic

from .character_prompt import build_messages, build_system_blocks

logger = logging.getLogger(__name__)

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_CHAT_MODEL", "claude-haiku-4-5")
CLAUDE_MAX_TOKENS = int(os.getenv("CLAUDE_CHAT_MAX_TOKENS", "512"))


class ClaudeChatClient:
    """Anthropic Claude API 기반 캐릭터 챗 클라이언트."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key or CLAUDE_API_KEY
        self._model = model or CLAUDE_MODEL
        if not self._api_key:
            raise RuntimeError(
                "CLAUDE_API_KEY(또는 ANTHROPIC_API_KEY) 환경변수가 설정되어 있지 않아."
            )
        self._client = anthropic.AsyncAnthropic(api_key=self._api_key)

    async def chat(
        self,
        message: str,
        history: Optional[list] = None,
        context: Optional[str] = None,
        **_kwargs,
    ) -> Optional[str]:
        """유저 메시지를 받아 데비&마를렌 캐릭터 응답을 반환.

        Modal ChatClient와 시그니처 호환.
        **_kwargs: Managed Agents가 쓰는 discord_channel 같은 것 받아서 무시.
        """
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=CLAUDE_MAX_TOKENS,
                system=build_system_blocks(context),
                messages=build_messages(message, history),
            )
        except anthropic.APIError as e:
            logger.error("Claude API 에러: %s", e)
            return None
        except Exception as e:
            logger.error("Claude 호출 실패: %s", e)
            return None

        # 토큰 사용량 로깅 (캐시 히트 확인용)
        usage = getattr(response, "usage", None)
        if usage:
            logger.info(
                "Claude usage: in=%s cache_read=%s cache_create=%s out=%s",
                getattr(usage, "input_tokens", "?"),
                getattr(usage, "cache_read_input_tokens", 0),
                getattr(usage, "cache_creation_input_tokens", 0),
                getattr(usage, "output_tokens", "?"),
            )

        # content block 중 text 블록만 추출
        for block in response.content:
            if getattr(block, "type", None) == "text":
                return block.text
        return None

    async def health_check(self) -> bool:
        """키 유효성만 빠르게 확인."""
        return bool(self._api_key)

    async def close(self):
        """AsyncAnthropic은 명시적 close 불필요 — 인터페이스 호환 위해 no-op."""
        return None

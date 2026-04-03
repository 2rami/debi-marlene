"""
데비&마를렌 챗 클라이언트

로컬 MLX 추론 서버(finetune/inference_server.py)에 HTTP 요청
"""

import aiohttp
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

CHAT_API_URL = os.getenv("CHAT_API_URL", "http://localhost:5050")


class ChatClient:
    """비동기 HTTP 클라이언트 - 추론 서버 호출"""

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60)
            )
        return self._session

    async def chat(self, message: str, history: list = None, context: str = None) -> Optional[str]:
        """메시지를 보내고 캐릭터 응답을 받음"""
        session = await self._get_session()
        payload = {"message": message}
        if history:
            payload["history"] = history
        if context:
            payload["context"] = context

        try:
            async with session.post(
                f"{CHAT_API_URL}/chat", json=payload
            ) as resp:
                if resp.status != 200:
                    logger.error("추론 서버 에러: %s", resp.status)
                    return None
                data = await resp.json()
                return data.get("response")
        except aiohttp.ClientError as e:
            logger.error("추론 서버 연결 실패: %s", e)
            return None

    async def health_check(self) -> bool:
        """서버 상태 확인"""
        session = await self._get_session()
        try:
            async with session.get(f"{CHAT_API_URL}/health") as resp:
                return resp.status == 200
        except aiohttp.ClientError:
            return False

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

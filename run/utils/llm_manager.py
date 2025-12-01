"""
LLM 관리 클래스
Ollama를 사용하여 로컬 LLM과 통신
"""

from collections import defaultdict, deque
from typing import Dict, List, Optional
import aiohttp
import logging

logger = logging.getLogger(__name__)


class LLMManager:
    """
    로컬 LLM 관리 클래스

    채널별 대화 기록을 관리하고 LLM과 통신합니다.
    """

    def __init__(
        self,
        model: str = 'qwen2.5:7b',
        max_history: int = 20,
        ollama_url: str = 'http://localhost:11434'
    ):
        """
        Args:
            model: 사용할 LLM 모델 이름
            max_history: 채널당 저장할 최대 대화 기록 수
            ollama_url: Ollama 서버 URL
        """
        self.model = model
        self.max_history = max_history
        self.ollama_url = ollama_url

        # 채널별 대화 기록 (최근 N개만 유지)
        self.conversations: Dict[int, deque] = defaultdict(
            lambda: deque(maxlen=max_history)
        )

        logger.info(f"LLM Manager 초기화: model={model}, max_history={max_history}")

    def add_message(
        self,
        channel_id: int,
        role: str,
        content: str,
        username: Optional[str] = None
    ):
        """
        대화 기록에 메시지 추가

        Args:
            channel_id: 디스코드 채널 ID
            role: 'user' 또는 'assistant'
            content: 메시지 내용
            username: 사용자 이름 (옵션)
        """
        msg_content = content
        if username and role == 'user':
            msg_content = f"{username}: {content}"

        message = {
            'role': role,
            'content': msg_content
        }

        self.conversations[channel_id].append(message)
        logger.debug(f"메시지 추가 [채널={channel_id}]: {role} - {msg_content[:50]}...")

    async def get_response(
        self,
        channel_id: int,
        user_message: str,
        username: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        LLM 응답 생성

        Args:
            channel_id: 디스코드 채널 ID
            user_message: 사용자 메시지
            username: 사용자 이름
            system_prompt: 시스템 프롬프트 (옵션)

        Returns:
            LLM의 응답 텍스트
        """
        # 사용자 메시지 추가
        self.add_message(channel_id, 'user', user_message, username)

        # 대화 기록 준비
        messages = list(self.conversations[channel_id])

        # 시스템 프롬프트가 있으면 맨 앞에 추가
        if system_prompt and (not messages or messages[0]['role'] != 'system'):
            messages.insert(0, {
                'role': 'system',
                'content': system_prompt
            })

        try:
            # Ollama API 호출
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.ollama_url}/api/chat',
                    json={
                        'model': self.model,
                        'messages': messages,
                        'stream': False
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API 오류: {response.status} - {error_text}")
                        raise Exception(f"LLM API 오류: {response.status}")

                    result = await response.json()
                    reply = result['message']['content']

                    # 봇 응답도 기록에 추가
                    self.add_message(channel_id, 'assistant', reply)

                    logger.info(f"LLM 응답 생성 완료 [채널={channel_id}]: {len(reply)} 글자")
                    return reply

        except aiohttp.ClientError as e:
            logger.error(f"Ollama 서버 연결 실패: {e}")
            raise Exception("LLM 서버에 연결할 수 없습니다. Ollama가 실행 중인지 확인하세요.")

        except Exception as e:
            logger.error(f"LLM 응답 생성 실패: {e}")
            raise

    def clear_history(self, channel_id: int):
        """
        특정 채널의 대화 기록 삭제

        Args:
            channel_id: 디스코드 채널 ID
        """
        if channel_id in self.conversations:
            del self.conversations[channel_id]
            logger.info(f"대화 기록 삭제 [채널={channel_id}]")

    def get_history_count(self, channel_id: int) -> int:
        """
        채널의 대화 기록 개수 반환

        Args:
            channel_id: 디스코드 채널 ID

        Returns:
            대화 기록 개수
        """
        return len(self.conversations.get(channel_id, []))

    def change_model(self, model: str):
        """
        사용 중인 모델 변경

        Args:
            model: 새로운 모델 이름
        """
        old_model = self.model
        self.model = model
        logger.info(f"모델 변경: {old_model} -> {model}")

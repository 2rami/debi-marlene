"""
Qwen3-TTS FastAPI 서버

파인튜닝된 Qwen3-TTS 모델을 API로 제공합니다.
Discord 봇에서 HTTP 요청으로 TTS를 호출할 수 있습니다.

실행:
    python qwen3_tts_api.py

또는:
    uvicorn qwen3_tts_api:app --host 0.0.0.0 --port 8100
"""

import os
import io
import uuid
import asyncio
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

import torch
import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 설정
MODEL_PATH = os.environ.get(
    "QWEN3_TTS_MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "tests", "qwen3_tts_test", "checkpoint-epoch-9")
)
MODEL_PATH = os.path.abspath(MODEL_PATH)

TEMP_DIR = os.environ.get("TTS_TEMP_DIR", "/tmp/tts_output")
os.makedirs(TEMP_DIR, exist_ok=True)

# FastAPI 앱
app = FastAPI(
    title="Qwen3-TTS API",
    description="파인튜닝된 Qwen3-TTS 음성 합성 API",
    version="1.0.0"
)

# 전역 모델 (서버 시작 시 로드)
tts_model = None
executor = ThreadPoolExecutor(max_workers=2)


class TTSRequest(BaseModel):
    """TTS 요청 모델"""
    text: str
    speaker: str = "debi"
    format: str = "wav"  # wav, mp3


class TTSResponse(BaseModel):
    """TTS 응답 모델"""
    success: bool
    message: str
    audio_url: Optional[str] = None


def load_model():
    """모델 로드 (동기)"""
    global tts_model

    if tts_model is not None:
        return

    from qwen_tts import Qwen3TTSModel

    logger.info(f"Qwen3-TTS 모델 로드 중: {MODEL_PATH}")

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    # attention 구현 선택
    try:
        import flash_attn
        attn_impl = "flash_attention_2"
    except ImportError:
        attn_impl = "eager"

    logger.info(f"Device: {device}, Attention: {attn_impl}")

    tts_model = Qwen3TTSModel.from_pretrained(
        MODEL_PATH,
        device_map=device,
        torch_dtype=dtype,
        attn_implementation=attn_impl,
    )

    logger.info("모델 로드 완료!")
    logger.info(f"지원 화자: {tts_model.get_supported_speakers()}")


def generate_speech_sync(text: str, speaker: str) -> tuple:
    """음성 생성 (동기)"""
    global tts_model

    if tts_model is None:
        raise RuntimeError("모델이 로드되지 않았습니다")

    wavs, sr = tts_model.generate_custom_voice(
        text=text,
        speaker=speaker,
    )

    return wavs[0], sr


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 로드"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, load_model)


@app.get("/")
async def root():
    """서버 상태 확인"""
    return {
        "status": "running",
        "model_loaded": tts_model is not None,
        "model_path": MODEL_PATH,
        "cuda_available": torch.cuda.is_available(),
    }


@app.get("/speakers")
async def get_speakers():
    """사용 가능한 화자 목록"""
    if tts_model is None:
        raise HTTPException(status_code=503, detail="모델 로딩 중")

    return {
        "speakers": tts_model.get_supported_speakers()
    }


@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    텍스트를 음성으로 변환

    Returns:
        WAV 파일 스트리밍 응답
    """
    if tts_model is None:
        raise HTTPException(status_code=503, detail="모델 로딩 중")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="텍스트가 비어있습니다")

    if len(request.text) > 500:
        raise HTTPException(status_code=400, detail="텍스트가 너무 깁니다 (최대 500자)")

    try:
        # 스레드에서 음성 생성
        loop = asyncio.get_event_loop()
        audio_data, sample_rate = await loop.run_in_executor(
            executor,
            generate_speech_sync,
            request.text,
            request.speaker
        )

        # WAV 바이트로 변환
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, format="WAV")
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=tts_{uuid.uuid4().hex[:8]}.wav"
            }
        )

    except Exception as e:
        logger.error(f"TTS 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts/file")
async def text_to_speech_file(request: TTSRequest) -> TTSResponse:
    """
    텍스트를 음성 파일로 변환 (파일 경로 반환)

    Returns:
        생성된 파일 경로
    """
    if tts_model is None:
        raise HTTPException(status_code=503, detail="모델 로딩 중")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="텍스트가 비어있습니다")

    try:
        # 스레드에서 음성 생성
        loop = asyncio.get_event_loop()
        audio_data, sample_rate = await loop.run_in_executor(
            executor,
            generate_speech_sync,
            request.text,
            request.speaker
        )

        # 파일 저장
        filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
        filepath = os.path.join(TEMP_DIR, filename)
        sf.write(filepath, audio_data, sample_rate)

        return TTSResponse(
            success=True,
            message="음성 생성 완료",
            audio_url=filepath
        )

    except Exception as e:
        logger.error(f"TTS 생성 실패: {e}")
        return TTSResponse(
            success=False,
            message=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    # 서버 실행
    uvicorn.run(
        "qwen3_tts_api:app",
        host="0.0.0.0",
        port=8100,
        reload=False,
        log_level="info"
    )

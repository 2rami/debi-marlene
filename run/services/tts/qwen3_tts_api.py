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
from typing import Optional, Dict
from concurrent.futures import ThreadPoolExecutor

import torch
import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 설정 - 화자별 모델 경로
BASE_PATH = os.environ.get("QWEN3_TTS_MODEL_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "tests", "qwen3_tts_test")
)

# 로컬 경로가 없으면 허깅페이스 repo id 로 그대로 넘긴다 — 파인튜닝 산출물의 정본이
# 드라이브가 아니라 허깅페이스에 있다(드라이브 사본은 가중치가 비어 있었다).
SPEAKER_MODELS = {
    "debi": os.environ.get("QWEN3_TTS_DEBI") or os.path.join(BASE_PATH, "checkpoint-epoch-9"),
    "marlene": os.environ.get("QWEN3_TTS_MARLENE") or os.path.join(BASE_PATH, "checkpoint-epoch-27"),
}

TEMP_DIR = os.environ.get("TTS_TEMP_DIR", "/tmp/tts_output")
os.makedirs(TEMP_DIR, exist_ok=True)

# FastAPI 앱
app = FastAPI(
    title="Qwen3-TTS API",
    description="파인튜닝된 Qwen3-TTS 음성 합성 API (Debi & Marlene)",
    version="1.1.0"
)

# 화자별 모델 (서버 시작 시 로드)
tts_models: Dict[str, any] = {}
executor = ThreadPoolExecutor(max_workers=2)

# GPU 설정
device = None
dtype = None
attn_impl = None


class TTSRequest(BaseModel):
    """TTS 요청 모델"""
    text: str
    speaker: str = "debi"
    format: str = "wav"


class TTSResponse(BaseModel):
    """TTS 응답 모델"""
    success: bool
    message: str
    audio_url: Optional[str] = None


def init_device():
    """디바이스 초기화"""
    global device, dtype, attn_impl

    if torch.cuda.is_available():
        device, dtype = "cuda:0", torch.bfloat16
    elif torch.backends.mps.is_available():
        # float16 은 샘플링에서 확률 텐서가 inf/nan 으로 넘쳐 죽는다(M4 실측).
        # bfloat16 은 지수 범위가 float32 와 같아 그 문제가 없고, 대역폭이 절반이라
        # float32 보다 빠르다(데비 RTF 2.44 -> 1.97). 메모리도 절반이라 마를렌(1.92B)이
        # 16GB 에 들어가는 것도 이 갈래 덕이다.
        device, dtype = "mps", torch.bfloat16
    else:
        device, dtype = "cpu", torch.float32

    # flash-attn 은 CUDA 전용 빌드다. 다른 디바이스에서는 쳐다보지도 않는다.
    attn_impl = "eager"
    if device.startswith("cuda"):
        try:
            import flash_attn  # noqa: F401
            attn_impl = "flash_attention_2"
        except ImportError:
            pass

    logger.info(f"Device: {device}, Dtype: {dtype}, Attention: {attn_impl}")


def load_model_for_speaker(speaker: str):
    """특정 화자 모델 로드 (동기)"""
    global tts_models

    if speaker in tts_models:
        return tts_models[speaker]

    if speaker not in SPEAKER_MODELS:
        raise ValueError(f"지원하지 않는 화자: {speaker}")

    model_path = SPEAKER_MODELS[speaker]

    # 슬래시 하나짜리 이름은 허깅페이스 repo id 로 본다. 그 외에는 실제 경로여야 한다.
    is_repo_id = not os.path.isabs(model_path) and model_path.count("/") == 1
    if not is_repo_id and not os.path.exists(model_path):
        raise FileNotFoundError(f"모델 경로가 없습니다: {model_path}")

    from qwen_tts import Qwen3TTSModel

    logger.info(f"[{speaker}] 모델 로드 중: {model_path}")

    model = Qwen3TTSModel.from_pretrained(
        model_path,
        device_map=device,
        torch_dtype=dtype,
        attn_implementation=attn_impl,
    )

    tts_models[speaker] = model
    logger.info(f"[{speaker}] 모델 로드 완료! 지원 화자: {model.get_supported_speakers()}")

    return model


def load_all_models():
    """모든 화자 모델 로드"""
    init_device()

    # 메모리가 빠듯한 기계(16GB 맥미니)에서는 첫 요청 때 화자별로 올린다.
    if os.environ.get("QWEN3_TTS_LAZY", "").lower() in ("1", "true", "yes"):
        logger.info("지연 로드 모드 — 첫 요청 때 화자별로 올립니다")
        return

    for speaker in SPEAKER_MODELS.keys():
        try:
            load_model_for_speaker(speaker)
        except Exception as e:
            logger.error(f"[{speaker}] 모델 로드 실패: {e}")


def generate_speech_sync(text: str, speaker: str) -> tuple:
    """음성 생성 (동기)"""
    # 화자에 맞는 모델 가져오기
    if speaker not in tts_models:
        # 모델이 로드되지 않았으면 로드
        load_model_for_speaker(speaker)

    model = tts_models[speaker]

    wavs, sr = model.generate_custom_voice(
        text=text,
        speaker=speaker,
    )

    return wavs[0], sr


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모든 모델 로드"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, load_all_models)


@app.get("/")
async def root():
    """서버 상태 확인"""
    return {
        "status": "running",
        "models_loaded": list(tts_models.keys()),
        "available_speakers": list(SPEAKER_MODELS.keys()),
        "cuda_available": torch.cuda.is_available(),
    }


@app.get("/speakers")
async def get_speakers():
    """사용 가능한 화자 목록"""
    return {
        "speakers": list(SPEAKER_MODELS.keys()),
        "loaded": list(tts_models.keys())
    }


@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    텍스트를 음성으로 변환

    Returns:
        WAV 파일 스트리밍 응답
    """
    if request.speaker not in SPEAKER_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 화자: {request.speaker}. 사용 가능: {list(SPEAKER_MODELS.keys())}"
        )

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="텍스트가 비어있습니다")

    if len(request.text) > 500:
        raise HTTPException(status_code=400, detail="텍스트가 너무 깁니다 (최대 500자)")

    try:
        loop = asyncio.get_event_loop()
        audio_data, sample_rate = await loop.run_in_executor(
            executor,
            generate_speech_sync,
            request.text,
            request.speaker
        )

        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, format="WAV")
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=tts_{request.speaker}_{uuid.uuid4().hex[:8]}.wav"
            }
        )

    except Exception as e:
        logger.error(f"TTS 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts/file")
async def text_to_speech_file(request: TTSRequest) -> TTSResponse:
    """텍스트를 음성 파일로 변환"""
    if request.speaker not in SPEAKER_MODELS:
        return TTSResponse(
            success=False,
            message=f"지원하지 않는 화자: {request.speaker}"
        )

    if not request.text.strip():
        return TTSResponse(success=False, message="텍스트가 비어있습니다")

    try:
        loop = asyncio.get_event_loop()
        audio_data, sample_rate = await loop.run_in_executor(
            executor,
            generate_speech_sync,
            request.text,
            request.speaker
        )

        filename = f"tts_{request.speaker}_{uuid.uuid4().hex[:8]}.wav"
        filepath = os.path.join(TEMP_DIR, filename)
        sf.write(filepath, audio_data, sample_rate)

        return TTSResponse(
            success=True,
            message="음성 생성 완료",
            audio_url=filepath
        )

    except Exception as e:
        logger.error(f"TTS 생성 실패: {e}")
        return TTSResponse(success=False, message=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "qwen3_tts_api:app",
        host="0.0.0.0",
        port=8100,
        reload=False,
        log_level="info"
    )

"""Edge TTS Local Server - 속도 테스트용"""
import io
import time
import asyncio
import edge_tts
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

VOICES = {
    "debi": "ko-KR-SunHiNeural",
    "marlene": "ko-KR-InJoonNeural",
}

class TTSRequest(BaseModel):
    text: str
    speaker: str = "debi"
    style: str = "[calm]"
    guild_name: Optional[str] = None
    channel_name: Optional[str] = None
    user_name: Optional[str] = None

@app.post("/tts")
async def tts(req: TTSRequest):
    if not req.text.strip():
        return {"error": "Text is empty"}

    voice = VOICES.get(req.speaker, VOICES["debi"])
    t0 = time.time()

    comm = edge_tts.Communicate(req.text[:500], voice)
    buf = io.BytesIO()
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])

    elapsed = time.time() - t0
    print(f"[Edge TTS] {req.speaker} | {elapsed:.2f}s | {req.text[:50]}")

    # mp3 그대로 반환 (봇의 ffmpeg가 재생 시 변환)
    return Response(content=buf.getvalue(), media_type="audio/mpeg")

@app.get("/health")
def health():
    return {"status": "running", "engine": "Edge TTS"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8201)

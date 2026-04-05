# Voice System Architecture

Debi Marlene 봇의 음성 시스템 전체 구조.
음성 수신(STT) + 음성 합성(TTS) 두 파이프라인으로 구성.

---

## 전체 흐름

```
[사용자가 음성채널에서 말함]
        |
        v
   Discord Voice Gateway (Opus 패킷)
        |
        v
   ListenSink (voice_listen.py)
   - DAVE 복호화
   - Opus -> PCM 디코딩
   - SpeechBuffer에 축적
        |
        v
   말 멈춤 감지 (1.5초 무음)
        |
        v
   WAV 변환 -> Base64 인코딩
        |
        v
   Gemma 4 E4B (Modal A10G)
   - 16kHz mono로 리샘플링
   - 오디오 + 텍스트 멀티모달 추론
   - 캐릭터 대사 생성 (데비 & 마를렌)
        |
        v
   응답 텍스트를 TTS로 변환
        |
        v
   CosyVoice3 (Modal T4)
   - 파인튜닝된 캐릭터 음성 합성
   - 24kHz mono WAV 출력
        |
        v
   48kHz stereo PCM 변환
        |
        v
   Discord Voice로 재생
```

---

## 1. 음성 수신 (Speech-to-Text)

### 1-1. Discord 오디오 수신

Discord 음성 채널의 오디오를 받으려면 일반 `VoiceClient`가 아니라 `VoiceRecvClient`를 써야 한다.
`discord-ext-voice-recv` 라이브러리가 이걸 지원한다.

```
파일: run/cogs/voice_listen.py
명령어: /듣기
```

```python
# VoiceRecvClient로 연결해야 오디오 수신 가능
vc = await voice_channel.connect(
    cls=voice_recv.VoiceRecvClient,
    self_deaf=False,    # 자신을 귀머거리로 설정하면 안 됨
    reconnect=False,
)
vc.listen(ListenSink(...))  # Sink가 패킷을 받음
```

### 1-2. ListenSink - 오디오 패킷 처리

`ListenSink`는 Discord에서 오는 Opus 패킷을 받아서 처리하는 핵심 클래스.

```
파일: run/cogs/voice_listen.py (ListenSink, line 105-265)
```

**패킷 수신 흐름:**

1. `wants_opus()` -> `True` 반환: raw Opus 패킷을 직접 받겠다는 의미
2. `write()` -> 매 Opus 패킷마다 호출됨
3. `_write_inner()` -> 실제 처리 로직

**DAVE 복호화:**

Discord는 2024년부터 DAVE(Discord Audio/Video Encryption)를 사용한다.
봇이 받는 Opus 패킷은 이중 암호화되어 있어서, DAVE 세션으로 한 겹 더 복호화해야 한다.

```python
# DAVE 복호화 (voice_listen.py, line 156-167)
dave = vc._connection.dave_session
if dave:
    decrypted = dave.decrypt(uid, MediaType.audio, encrypted_data)
```

**무음 필터링:**

Opus 코덱의 무음 프레임(`b'\xf8\xff\xfe'`)은 버린다.

### 1-3. SpeechBuffer - 사용자별 음성 버퍼

```
파일: run/cogs/voice_listen.py (SpeechBuffer, line 48-103)
```

사용자마다 별도의 `SpeechBuffer`가 생성된다.
Opus 패킷을 디코딩해서 PCM 청크로 쌓는다.

```python
class SpeechBuffer:
    def write_opus(self, opus_data):
        pcm = self.decoder.decode(opus_data)  # Opus -> PCM
        self.chunks.append(pcm)
```

**오디오 스펙:**

| 항목 | 값 |
|------|-----|
| 샘플레이트 | 48,000 Hz |
| 채널 | 2 (스테레오) |
| 비트 깊이 | 16-bit (signed LE) |
| 최소 길이 | 0.5초 |
| 최대 길이 | 25초 |

### 1-4. VAD (Voice Activity Detection)

Discord 자체 VAD 이벤트를 활용한다.
별도 VAD 모델을 돌리지 않고, Discord Gateway가 보내주는 speaking 이벤트를 사용.

```
on_voice_member_speaking_start -> SpeechBuffer 시작
on_voice_member_speaking_stop  -> 1.5초 대기 후 처리
```

1.5초 무음이 지속되면 발화가 끝났다고 판단하고 `_delayed_process()`가 실행된다.

### 1-5. 음성 -> Gemma 4 전송

```
파일: run/cogs/voice_listen.py (process_speech, line 391-436)
```

1. `SpeechBuffer.to_wav_bytes()` -> 48kHz stereo WAV
2. Base64 인코딩
3. HTTP POST로 Gemma 4 서버에 전송

```python
audio_b64 = base64.b64encode(wav_bytes).decode()
payload = {
    "audio_base64": audio_b64,
    "message": "사용자가 음성으로 말한 내용을 듣고 캐릭터로 대답해줘",
}
# POST -> Modal Gemma4Audio 엔드포인트
```

---

## 2. 오디오 이해 모델 (Gemma 4)

### 2-1. 모델 정보

```
파일: run/services/chat/gemma4_modal_server.py (Gemma4Audio, line 172-325)
```

| 항목 | 값 |
|------|-----|
| 모델 | `google/gemma-4-E4B-it` |
| 타입 | 멀티모달 (텍스트 + 오디오) |
| 파인튜닝 | LoRA 어댑터 (캐릭터 대화) |
| GPU | NVIDIA A10G (Modal Serverless) |
| 정밀도 | bfloat16 |
| 최대 오디오 | 30초 |

Gemma 4 E4B는 구글의 멀티모달 모델로, 텍스트뿐 아니라 오디오 입력을 직접 이해할 수 있다.
별도의 STT(Whisper 등)를 거치지 않고 오디오를 바로 모델에 넣는다.
이건 "omni" 방식이라고 부르는데, 오디오의 톤/감정까지 이해할 수 있다는 장점이 있다.

### 2-2. 추론 파이프라인

```python
# 1. Base64 WAV -> 파일로 저장
audio_bytes = base64.b64decode(audio_b64)

# 2. librosa로 로드 (16kHz mono로 리샘플링)
audio_data, sr = librosa.load(audio_path, sr=16000, mono=True)

# 3. 멀티모달 입력 구성
messages = [{
    "role": "user",
    "content": [
        {"type": "audio", "audio": audio_data},   # 오디오
        {"type": "text", "text": prompt},          # 텍스트 프롬프트
    ],
}]

# 4. 토크나이즈 + 추론
inputs = processor.apply_chat_template(messages, sampling_rate=16000, ...)
output = model.generate(**inputs, max_new_tokens=120, temperature=0.5)
```

**핵심 포인트:**
- Discord 오디오는 48kHz stereo인데, Gemma 4는 16kHz mono를 기대한다
- `librosa.load(sr=16000, mono=True)`가 자동으로 리샘플링 + 모노 변환을 해준다
- 모델이 오디오를 직접 이해하므로 STT 단계가 없다 (end-to-end)

### 2-3. LoRA 어댑터

캐릭터 대화 스타일을 학습시킨 LoRA 어댑터를 로드한다.

```python
# 파인튜닝된 어댑터가 있으면 적용
if os.path.exists(ADAPTER_VOLUME_PATH):
    from peft import PeftModel
    self.model = PeftModel.from_pretrained(self.model, ADAPTER_VOLUME_PATH)
```

어댑터는 Modal Volume(`gemma4-chat-cache`)에 저장되어 있다.

### 2-4. 캐릭터 시스템 프롬프트

```python
SYSTEM_PROMPT = (
    "너는 이터널 리턴의 쌍둥이 실험체 데비&마를렌이야. 한국어로만 대답해.\n"
    "데비(언니): 활발, 천진난만, 장난기. 직설적이고 솔직한 10대 소녀 말투.\n"
    "마를렌(동생): 냉소적이지만 자연스러운 10대 소녀. 말이 짧고 차분함.\n"
    "형식: 데비: (대사) + 마를렌: (대사). 각자 1-2문장으로 짧게."
)
```

### 2-5. Cold Start

Modal Serverless 특성상 첫 요청 시 컨테이너를 띄워야 한다.

| 항목 | 값 |
|------|-----|
| Cold start | ~50-60초 |
| Warm 추론 | 0.7-2.5초 |
| Scale down | 120초 무요청 시 |
| 최대 컨테이너 | 1개 |
| 동시 입력 | 2개 (`@modal.concurrent`) |

---

## 3. 음성 합성 (Text-to-Speech)

### 3-1. TTS 엔진 구조

```
run/services/tts/
  tts_service.py              # TTS 오케스트레이터
  cosyvoice3_modal_server.py  # Modal 서버 (CosyVoice3)
  cosyvoice3_client.py        # Modal HTTP 클라이언트
  audio_utils.py              # PCM 변환
  audio_player.py             # Discord 재생
  edge_tts_client.py          # 폴백 TTS (Microsoft)
```

### 3-2. CosyVoice3 모델

```
파일: run/services/tts/cosyvoice3_modal_server.py
```

| 항목 | 값 |
|------|-----|
| 베이스 모델 | `FunAudioLLM/Fun-CosyVoice3-0.5B-2512` |
| 파인튜닝 | LLM SFT only (Flow/HiFiGAN 고정) |
| 학습 데이터 | 이터널 리턴 캐릭터 음성 |
| HF 레포 | `2R4mi/cosyvoice3-debi-marlene` (private) |
| GPU | NVIDIA T4 (Modal) |
| 출력 | 24kHz mono WAV |

CosyVoice3는 Alibaba/FunAudioLLM의 음성 합성 모델이다.
LLM 부분만 SFT(Supervised Fine-Tuning)로 학습시켜서 캐릭터 음색을 재현한다.

**음성 생성 과정:**

```python
def _generate_full(self, text, speaker="debi", style="[calm]"):
    ref_wav = self._get_reference_wav(speaker)  # 레퍼런스 음성
    instruction = f"You are a helpful assistant.<|endofprompt|>{style}"

    for result in self.model.inference_instruct2(
        text, instruction, ref_wav, stream=False
    ):
        output_wav = result["tts_speech"]

    # 24kHz mono WAV로 저장
    audio = output_wav.numpy().flatten()
    sf.write(buffer, audio, 24000, format="WAV")
```

**사용 가능한 화자:**

| 화자 | 설명 | 엔진 |
|------|------|------|
| debi | 데비 (활발한 언니) | CosyVoice3 |
| marlene | 마를렌 (차분한 동생) | CosyVoice3 |
| alex | 알렉스 | CosyVoice3 (별도 서버) |
| edge_sunhi | 선희 (여성) | Edge TTS |
| edge_injoon | 인준 (남성) | Edge TTS |
| edge_hyunsu | 현수 (남성, 다국어) | Edge TTS |

### 3-3. 오디오 포맷 변환

CosyVoice3 출력(24kHz mono)을 Discord 재생 포맷(48kHz stereo)으로 변환한다.

```python
# cosyvoice3_client.py, _wav_to_discord_pcm()

# 1. 24kHz -> 48kHz 리샘플링
mono_pcm, _ = audioop.ratecv(mono_pcm, 2, 1, 24000, 48000, None)

# 2. mono -> stereo (좌우 채널 복제)
stereo_pcm = audioop.tostereo(mono_pcm, 2, 1, 1)

# 3. 앞부분 무음 제거 (threshold > 500)
for i in range(0, len(stereo_pcm) - 4, 4):
    left = abs(struct.unpack_from('<h', stereo_pcm, i)[0])
    if left > 500:
        return stereo_pcm[i:]
```

### 3-4. TTS 캐싱

같은 텍스트를 반복 생성하지 않기 위해 캐시를 사용한다.

```python
# tts_service.py
cache_key = hashlib.md5(f"{engine}:{speaker}:{text}".encode()).hexdigest()
cache_path = os.path.join("/tmp/tts_cache", f"{cache_key}.pcm")

# 캐시 히트 -> 즉시 반환 (생성 0초)
# 캐시 미스 -> 생성 후 저장
```

| 항목 | 값 |
|------|-----|
| 캐시 경로 | `/tmp/tts_cache/` |
| 캐시 키 | MD5(엔진:화자:텍스트) |
| 최대 파일 수 | 2,000개 |
| 포맷 | 48kHz stereo PCM (Discord 즉시 재생 가능) |

### 3-5. 폴백 전략

CosyVoice3 서버가 응답하지 않으면 Edge TTS(Microsoft 무료 TTS)로 폴백한다.

```
CosyVoice3 시도 (120초 타임아웃, 503시 2회 재시도)
        |
        실패
        |
        v
Edge TTS 폴백 (Microsoft 클라우드, 지연 거의 없음)
```

---

## 4. Discord 재생

### 4-1. 재생 큐

서버(길드)마다 독립적인 재생 큐가 있다.
TTS 생성은 병렬로 하지만, 재생은 순차적으로 한다.

```
파일: run/cogs/voice.py
```

```python
# 서버별 큐
tts_playback_queues: Dict[str, asyncio.Queue] = {}

# 재생 워커 (서버당 1개)
async def _playback_worker(guild_id):
    while True:
        future = await queue.get()       # TTS 생성 완료 대기
        audio_path = await future
        await voice_manager.play_tts(guild_id, audio_path)  # 순차 재생
```

### 4-2. 음악과 TTS 공존

음악 재생 중에 TTS가 들어오면:

1. 음악 일시정지
2. TTS 재생
3. TTS 끝나면 음악 재개

### 4-3. 긴 텍스트 처리

300자가 넘는 텍스트는 TTS 생성하지 않고 대체 대사를 재생한다.

```python
if len(text) > 300:
    text = random.choice([
        "너무 길어서 못 읽겠어요.",
        "힘들어서 못 말하겠어.",
    ])
```

---

## 5. 오디오 포맷 요약

파이프라인 각 단계에서의 오디오 포맷:

```
Discord Voice    48kHz stereo Opus (암호화)
     |
DAVE 복호화      48kHz stereo Opus
     |
Opus Decode      48kHz stereo 16-bit PCM
     |
WAV 직렬화       48kHz stereo 16-bit WAV
     |
Base64 전송      48kHz stereo WAV (JSON body)
     |
Gemma 4 입력     16kHz mono float32 (librosa)
     |
[텍스트 응답 생성]
     |
CosyVoice3 출력  24kHz mono 16-bit WAV
     |
Discord 재생     48kHz stereo 16-bit PCM
```

---

## 6. Modal 서버 배포

### 엔드포인트

| 서비스 | GPU | Cold Start | Warm 추론 |
|--------|-----|------------|-----------|
| Gemma4 Chat (텍스트) | A10G | ~50초 | 0.3-1초 |
| Gemma4 Audio (음성이해) | A10G | ~50초 | 0.7-2.5초 |
| CosyVoice3 debi/marlene | T4 | ~58초 | RTF 1.5-2.2x |
| CosyVoice3 alex | T4 | ~58초 | RTF 1.5-2.2x |

RTF(Real-Time Factor): 1초 오디오 생성에 걸리는 시간. 2.0x면 1초 오디오를 만드는 데 2초.

### Volume (영구 저장소)

| Volume 이름 | 용도 |
|-------------|------|
| `gemma4-chat-cache` | Gemma 4 모델 가중치, LoRA 어댑터 |
| `cosyvoice3-model-cache` | CosyVoice3 모델, 레퍼런스 WAV |

### Scale Down 정책

요청이 없으면 120초 후 컨테이너가 내려간다.
다음 요청 시 cold start가 발생한다 (모델 로딩 ~50-60초).

---

## 7. 주요 파일 위치

| 컴포넌트 | 파일 |
|----------|------|
| 음성 수신 명령어 | `run/cogs/voice_listen.py` |
| ListenSink / SpeechBuffer | `run/cogs/voice_listen.py` |
| Gemma 4 Modal 서버 | `run/services/chat/gemma4_modal_server.py` |
| TTS 오케스트레이터 | `run/services/tts/tts_service.py` |
| CosyVoice3 Modal 서버 | `run/services/tts/cosyvoice3_modal_server.py` |
| CosyVoice3 클라이언트 | `run/services/tts/cosyvoice3_client.py` |
| 오디오 포맷 변환 | `run/services/tts/audio_utils.py` |
| Discord 재생 | `run/services/tts/audio_player.py` |
| 음성채널 관리 | `run/services/voice_manager.py` |
| TTS 명령어 / 메시지 핸들러 | `run/cogs/voice.py` |
| Edge TTS 폴백 | `run/services/tts/edge_tts_client.py` |

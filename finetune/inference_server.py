"""
데비&마를렌 추론 서버 (MLX)

로컬 Mac에서 실행. 봇이 HTTP로 호출.
사용법: cd finetune && .venv/bin/python3 inference_server.py
"""

import re
import time
import logging
from pathlib import Path

from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- 모델 (lazy load) ---
_model = None
_tokenizer = None
_sampler = None

MODEL_DIR = str(Path(__file__).parent / "thinker_mlx_4bit")

SYSTEM_PROMPT = (
    "너는 이터널 리턴의 쌍둥이 실험체 데비&마를렌이야. 한국어로만 대답해.\n"
    "데비(언니): 활발, 천진난만, 장난기. 말 끝에 ~!를 자주 붙임. 직설적이고 솔직함.\n"
    '마를렌(동생): 냉소적, 과묵, 신중. 말이 짧고 차분함. "..."으로 시작하기도 함.\n'
    "형식: 데비: (대사) + 마를렌: (대사). 각자 1-2문장으로 짧게."
)

# 중국어/일본어 문자 제거 패턴 (한글, ASCII, 한국 특수문자는 유지)
CJK_PATTERN = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff]+")
# 영어 단어 (2글자 이상 연속 영문) 제거 - 단, 일반적 약어는 유지
EN_PATTERN = re.compile(r"[A-Za-z]{3,}")


def load_model():
    global _model, _tokenizer, _sampler
    if _model is not None:
        return

    from mlx_lm import load
    from mlx_lm.sample_utils import make_sampler

    logger.info("모델 로딩: %s", MODEL_DIR)
    _model, _tokenizer = load(MODEL_DIR)
    _sampler = make_sampler(temp=0.5, top_p=0.9, min_p=0.05)
    logger.info("모델 로드 완료")


def clean_response(text: str) -> str:
    """중국어/일본어/영어 혼입 제거 + 반복 제거 + 깨진 텍스트 정리"""
    # CJK 한자 제거
    text = CJK_PATTERN.sub("", text)
    # 긴 영어 단어 제거
    text = EN_PATTERN.sub("", text)
    # 반복 패턴 제거 (같은 2~6글자가 3번 이상 반복)
    text = re.sub(r"(.{2,6})\1{2,}", r"\1", text)
    # 빈 줄 정리
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line in ("데비:", "마를렌:"):
            continue
        lines.append(line)
    return "\n".join(lines)


def generate_response(user_message: str, history: list = None, context: str = None) -> str:
    """사용자 메시지에 대한 캐릭터 응답 생성"""
    from mlx_lm import generate

    load_model()

    system = SYSTEM_PROMPT
    if context:
        ctx = context[:400]
        system += f"\n\n[게임 정보]\n{ctx}\n구체적인 수치와 스킬 이름을 포함해서 대답해. 없으면 없다고 해."

    messages = [{"role": "system", "content": system}]

    # 대화 히스토리 추가 (최근 5턴)
    if history:
        for h in history[-5:]:
            messages.append({"role": "user", "content": h["user"]})
            messages.append({"role": "assistant", "content": h["assistant"]})

    messages.append({"role": "user", "content": user_message})

    prompt = _tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    max_tok = 120 if context else 80
    response = generate(
        _model, _tokenizer, prompt=prompt, max_tokens=max_tok, sampler=_sampler
    )

    return clean_response(response)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    history = data.get("history", [])
    context = data.get("context")

    if not message:
        return jsonify({"error": "message required"}), 400

    start = time.time()
    response = generate_response(message, history, context)
    elapsed = time.time() - start

    logger.info("[%.1fs] Q: %s -> A: %s", elapsed, message[:50], response[:80])
    return jsonify({"response": response, "elapsed": round(elapsed, 2)})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running", "model": MODEL_DIR})


if __name__ == "__main__":
    load_model()
    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)

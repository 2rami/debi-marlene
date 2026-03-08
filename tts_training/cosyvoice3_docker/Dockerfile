# =============================================================================
# CosyVoice3 Fine-Tuning (neosun/cosyvoice base - 의존성 전부 포함)
# GPU: RTX 4070 Ti (12GB VRAM)
# =============================================================================
FROM neosun/cosyvoice:v3.4.0

# -----------------------------------------------------------------------------
# Pretrained model 다운로드 (Fun-CosyVoice3-0.5B)
# 이미지에 포함시켜서 실행 시 재다운로드 없음
# -----------------------------------------------------------------------------
RUN python3 -c "\
from huggingface_hub import snapshot_download; \
snapshot_download( \
    repo_id='FunAudioLLM/Fun-CosyVoice3-0.5B-2512', \
    local_dir='pretrained_models/Fun-CosyVoice3-0.5B', \
    ignore_patterns=['*.md', '*.txt'] \
)"

# 학습에 필요한 추가 패키지 (이미지에 없을 수 있음)
RUN pip install pandas pyworld 2>/dev/null || true

# examples 디렉토리 준비
RUN mkdir -p examples/libritts/cosyvoice3/conf \
             examples/libritts/cosyvoice3/data

COPY train.sh /workspace/train.sh
RUN sed -i 's/\r$//' /workspace/train.sh && chmod +x /workspace/train.sh

CMD ["bash", "/workspace/train.sh"]

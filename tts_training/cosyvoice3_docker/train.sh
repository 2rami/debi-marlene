#!/bin/bash
# =============================================================================
# CosyVoice3 Fine-Tuning Pipeline (Docker Container)
#
# Volume mounts:
#   /data    -> cosyvoice3_data/ (train/, dev/ with wavs, text, wav.scp, etc.)
#   /output  -> cosyvoice3_output/ (checkpoints, test wavs, logs)
#
# GPU: RTX 4070 Ti 12GB
# =============================================================================
set -e

# CosyVoice 디렉토리 자동 감지
if [ -d "/app/cosyvoice" ]; then
    COSYVOICE_DIR="/app"
elif [ -d "/workspace/CosyVoice/cosyvoice" ]; then
    COSYVOICE_DIR="/workspace/CosyVoice"
else
    echo "ERROR: CosyVoice directory not found"
    exit 1
fi

PRETRAINED="$COSYVOICE_DIR/pretrained_models/Fun-CosyVoice3-0.5B"
TRAIN_DIR="$COSYVOICE_DIR/examples/libritts/cosyvoice3"
LOG_FILE="/output/train.log"

export PYTHONPATH="$COSYVOICE_DIR/third_party/Matcha-TTS:$COSYVOICE_DIR:${PYTHONPATH:-}"
export CUDA_VISIBLE_DEVICES="0"

mkdir -p /output
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=============================================="
echo " CosyVoice3 Fine-Tuning Pipeline"
echo " $(date '+%Y-%m-%d %H:%M:%S')"
echo " CosyVoice: $COSYVOICE_DIR"
echo "=============================================="
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo ""

# =============================================================================
# Step 1/10: Data Validation
# =============================================================================
echo "[Step 1/10] Data Validation"

for split in train dev; do
    DIR="/data/$split"
    if [ ! -d "$DIR" ]; then
        echo "  ERROR: $DIR not found"
        exit 1
    fi

    WAV_COUNT=$(ls "$DIR/wavs/"*.wav 2>/dev/null | wc -l)
    TEXT_COUNT=$(wc -l < "$DIR/text")
    SCP_COUNT=$(wc -l < "$DIR/wav.scp")

    echo "  $split: $WAV_COUNT wavs, $TEXT_COUNT texts, $SCP_COUNT wav.scp entries"

    if [ "$WAV_COUNT" -eq 0 ]; then
        echo "  ERROR: no wav files in $DIR/wavs/"
        exit 1
    fi

    for f in text wav.scp utt2spk spk2utt; do
        if [ ! -f "$DIR/$f" ]; then
            echo "  ERROR: $DIR/$f not found"
            exit 1
        fi
    done
done

# wav.scp 경로 변환 -> 컨테이너 절대경로
for split in train dev; do
    SCP="/data/$split/wav.scp"
    python3 -c "
lines = open('$SCP', 'r').readlines()
new_lines = []
for line in lines:
    parts = line.strip().split(' ', 1)
    if len(parts) != 2:
        continue
    utt_id, wav_path = parts
    filename = wav_path.replace('\\\\', '/').split('/')[-1]
    abs_path = '/data/$split/wavs/' + filename
    new_lines.append(f'{utt_id} {abs_path}\n')
open('$SCP', 'w').writelines(new_lines)
print(f'  $split/wav.scp: {len(new_lines)} entries -> absolute paths')
"
done

FIRST_WAV=$(head -1 /data/train/wav.scp | awk '{print $2}')
if [ ! -f "$FIRST_WAV" ]; then
    echo "  ERROR: wav not found: $FIRST_WAV"
    exit 1
fi
echo "  wav check: OK"
echo ""

# =============================================================================
# Step 2/10: Symlinks
# =============================================================================
echo "[Step 2/10] Creating symlinks"

cd "$TRAIN_DIR"
mkdir -p data
ln -sfn /data/train data/train
ln -sfn /data/dev data/dev

echo "  /data/train -> data/train"
echo "  /data/dev   -> data/dev"
echo ""

# =============================================================================
# Step 3/10: Speaker Embedding (CAMPlus, CPU)
# =============================================================================
echo "[Step 3/10] Extracting speaker embeddings (campplus)"

for split in train dev; do
    if [ -f "data/$split/utt2embedding.pt" ] && [ -f "data/$split/spk2embedding.pt" ]; then
        echo "  $split: already exists, skip"
        continue
    fi
    echo "  $split: extracting..."
    python3 "$COSYVOICE_DIR/tools/extract_embedding.py" \
        --dir "data/$split" \
        --onnx_path "$PRETRAINED/campplus.onnx" \
        --num_thread 4
done

for split in train dev; do
    ls -lh "data/$split/utt2embedding.pt" "data/$split/spk2embedding.pt" 2>/dev/null \
        | awk '{print "  "$NF": "$5}'
done
echo ""

# =============================================================================
# Step 4/10: Speech Token (speech_tokenizer_v3, GPU)
# =============================================================================
echo "[Step 4/10] Extracting speech tokens (GPU)"

for split in train dev; do
    if [ -f "data/$split/utt2speech_token.pt" ]; then
        echo "  $split: already exists, skip"
        continue
    fi
    echo "  $split: extracting..."
    python3 "$COSYVOICE_DIR/tools/extract_speech_token.py" \
        --dir "data/$split" \
        --onnx_path "$PRETRAINED/speech_tokenizer_v3.onnx"
done

for split in train dev; do
    ls -lh "data/$split/utt2speech_token.pt" 2>/dev/null \
        | awk '{print "  "$NF": "$5}'
done
echo ""

# =============================================================================
# Step 5/10: Parquet Conversion
# =============================================================================
echo "[Step 5/10] Converting to Parquet"

for split in train dev; do
    if [ -d "data/$split/parquet" ] && [ -f "data/$split/parquet/data.list" ]; then
        echo "  $split: already exists, skip"
        continue
    fi
    echo "  $split: converting..."
    mkdir -p "data/$split/parquet"
    python3 "$COSYVOICE_DIR/tools/make_parquet_list.py" \
        --num_utts_per_parquet 1000 \
        --num_processes 4 \
        --src_dir "data/$split" \
        --des_dir "data/$split/parquet"
done

cat data/train/parquet/data.list > data/train.data.list
cat data/dev/parquet/data.list > data/dev.data.list

echo "  train.data.list: $(cat data/train.data.list)"
echo "  dev.data.list: $(cat data/dev.data.list)"
echo ""

# =============================================================================
# Step 6/10: Config (cosyvoice3.yaml)
# =============================================================================
echo "[Step 6/10] Preparing config"

CONFIG="conf/cosyvoice3.yaml"
cp "$PRETRAINED/cosyvoice3.yaml" "$CONFIG"

python3 -c "
import re
with open('$CONFIG', 'r') as f:
    content = f.read()
content, n1 = re.subn(r'(max_epoch:\s*)\d+', r'\g<1>50', content)
content, n2 = re.subn(r'(log_interval:\s*)\d+', r'\g<1>10', content)
with open('$CONFIG', 'w') as f:
    f.write(content)
changes = []
if n1: changes.append('max_epoch -> 50')
if n2: changes.append('log_interval -> 10')
print('  Modified: ' + ', '.join(changes) if changes else '  No changes needed')
"

cat > conf/ds_stage2.json << 'DSEOF'
{
  "train_micro_batch_size_per_gpu": "auto",
  "gradient_accumulation_steps": "auto",
  "fp16": {"enabled": "auto"},
  "zero_optimization": {"stage": 2},
  "gradient_clipping": 5.0
}
DSEOF
echo "  Training: torch_ddp + AMP (no deepspeed)"

# llm.py 버그 패치: th_accuracy에서 speech_token_size+3 대신 logits.shape[-1] 사용
# 원인: 모델은 speech_token_size+200으로 embedding을 만드는데, accuracy 계산에서 +3으로 하드코딩
sed -i 's/self\.speech_token_size + 3/logits.shape[-1]/g' "$COSYVOICE_DIR/cosyvoice/llm/llm.py"
echo "  Patched: llm.py th_accuracy shape fix"
echo ""

# =============================================================================
# Step 7/10: Dry Run (1 epoch, 3min timeout)
# =============================================================================
echo "[Step 7/10] Dry Run (3 min timeout)"

DRY_EXIT=0
timeout 180 torchrun --nnodes=1 --nproc_per_node=1 \
    --rdzv_id=1986 --rdzv_backend="c10d" --rdzv_endpoint="localhost:1234" \
    "$COSYVOICE_DIR/cosyvoice/bin/train.py" \
    --train_engine torch_ddp \
    --config "$CONFIG" \
    --train_data data/train.data.list \
    --cv_data data/dev.data.list \
    --qwen_pretrain_path "$PRETRAINED/CosyVoice-BlankEN" \
    --model llm \
    --checkpoint "$PRETRAINED/llm.pt" \
    --model_dir "$(pwd)/exp/dryrun/llm/torch_ddp" \
    --tensorboard_dir "$(pwd)/tensorboard/dryrun" \
    --ddp.dist_backend nccl \
    --num_workers 2 \
    --prefetch 100 \
    --pin_memory \
    --use_amp \
    2>&1 | tee /tmp/dryrun.log || DRY_EXIT=$?

if [ $DRY_EXIT -eq 124 ]; then
    echo "  Timeout (expected) - checking if training started..."
fi

if grep -q "Epoch 0 TRAIN" /tmp/dryrun.log; then
    echo "  Dry Run: SUCCESS (training loop entered)"
    grep -E "(Epoch|loss|lr)" /tmp/dryrun.log | tail -5 | sed 's/^/    /'
else
    echo "  Dry Run: FAILED (training loop not reached)"
    tail -30 /tmp/dryrun.log | sed 's/^/    /'
    exit 1
fi

echo ""
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader | sed 's/^/  GPU Memory: /'
echo ""

rm -rf exp/dryrun tensorboard/dryrun

# =============================================================================
# Step 8/10: Full Training (LLM SFT)
# =============================================================================
echo "[Step 8/10] Full Training (LLM SFT, 50 epochs)"
echo "  Start: $(date '+%Y-%m-%d %H:%M:%S')"

# /output 볼륨에 직접 저장 -> 컨테이너 죽어도 체크포인트 보존
EXP_DIR="/output/checkpoints"
TB_DIR="/output/tensorboard"
mkdir -p "$EXP_DIR" "$TB_DIR"

torchrun --nnodes=1 --nproc_per_node=1 \
    --rdzv_id=1986 --rdzv_backend="c10d" --rdzv_endpoint="localhost:1234" \
    "$COSYVOICE_DIR/cosyvoice/bin/train.py" \
    --train_engine torch_ddp \
    --config "$CONFIG" \
    --train_data data/train.data.list \
    --cv_data data/dev.data.list \
    --qwen_pretrain_path "$PRETRAINED/CosyVoice-BlankEN" \
    --model llm \
    --checkpoint "$PRETRAINED/llm.pt" \
    --model_dir "$EXP_DIR" \
    --tensorboard_dir "$TB_DIR" \
    --ddp.dist_backend nccl \
    --num_workers 2 \
    --prefetch 100 \
    --pin_memory \
    --use_amp

echo "  End: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Checkpoints:"
ls -lh "$EXP_DIR"/*.pt 2>/dev/null | tail -10 | sed 's/^/    /'
echo ""

# =============================================================================
# Step 9/10: Checkpoint Averaging (Top 5 by validation)
# =============================================================================
echo "[Step 9/10] Checkpoint Averaging (top 5, val_best)"

python3 "$COSYVOICE_DIR/cosyvoice/bin/average_model.py" \
    --dst_model "$EXP_DIR/llm.pt" \
    --src_path "$EXP_DIR" \
    --num 5 \
    --val_best

echo "  Averaged model: $(ls -lh "$EXP_DIR/llm.pt" | awk '{print $5}')"
echo ""

# =============================================================================
# Step 10/10: Inference Test
# =============================================================================
echo "[Step 10/10] Inference Test"

python3 -c "
import os, sys, shutil
sys.path.insert(0, '$COSYVOICE_DIR/third_party/Matcha-TTS')
sys.path.insert(0, '$COSYVOICE_DIR')

PRETRAINED = '$PRETRAINED'
EXP_DIR = '$EXP_DIR'

llm_orig = os.path.join(PRETRAINED, 'llm.pt')
llm_bak = os.path.join(PRETRAINED, 'llm.pt.bak')
llm_ft = os.path.join(EXP_DIR, 'llm.pt')

if not os.path.exists(llm_bak):
    shutil.copy2(llm_orig, llm_bak)
shutil.copy2(llm_ft, llm_orig)
print('  Fine-tuned LLM applied')

from cosyvoice.cli.cosyvoice import CosyVoice3
import soundfile as sf

cosyvoice = CosyVoice3(PRETRAINED, load_trt=False)
print('  Model loaded')

test_sentences = [
    ('debi', '[excited]', '나한텐 일상이었어'),
    ('debi', '[sad]', '미안해, 다음엔 더 잘할게'),
    ('debi', '[happy]', '오~ 꽤하잖아!'),
    ('debi', '[calm]', '한숨 돌렸다 가자고. 시간은 충분하니까'),
    ('marlene', '[calm]', '안녕하세요. 오늘도 좋은 하루 되세요.'),
]

output_dir = '/output/test_outputs'
os.makedirs(output_dir, exist_ok=True)
wavs_dir = '/data/train/wavs/'

for i, (speaker, style, text) in enumerate(test_sentences):
    try:
        instruct_text = 'You are a helpful assistant.<|endofprompt|>'
        tts_text = f'{style}{text}'
        spk_wavs = sorted([f for f in os.listdir(wavs_dir) if f.startswith(speaker)])
        if not spk_wavs:
            print(f'  Test {i+1}: {speaker} - no reference wav')
            continue
        ref_wav = os.path.join(wavs_dir, spk_wavs[0])
        output_wav = None
        for result in cosyvoice.inference_instruct2(tts_text, instruct_text, ref_wav, stream=False):
            output_wav = result['tts_speech'].numpy()
        if output_wav is not None:
            out_path = f'{output_dir}/test_{i+1}_{speaker}_{style.strip(\"[]\")}.wav'
            sf.write(out_path, output_wav.flatten(), 24000)
            print(f'  Test {i+1}: {speaker} {style} -> saved')
    except Exception as e:
        print(f'  Test {i+1}: ERROR - {e}')
"
echo ""

# =============================================================================
# Save results to /output
# =============================================================================
echo "=== Saving results to /output ==="

mkdir -p /output/checkpoints
cp "$EXP_DIR"/*.pt /output/checkpoints/ 2>/dev/null || true

mkdir -p /output/final_model
for f in llm.pt flow.pt hift.pt campplus.onnx speech_tokenizer_v3.onnx cosyvoice3.yaml; do
    cp "$PRETRAINED/$f" /output/final_model/ 2>/dev/null
done
cp -r "$PRETRAINED/CosyVoice-BlankEN" /output/final_model/ 2>/dev/null || true

mkdir -p /output/final_model/references
for speaker in debi marlene; do
    FIRST=$(ls /data/train/wavs/${speaker}_*.wav 2>/dev/null | head -1)
    if [ -n "$FIRST" ]; then
        cp "$FIRST" "/output/final_model/references/${speaker}.wav"
    fi
done

cp -r "$TB_DIR" /output/tensorboard 2>/dev/null || true

echo "  Checkpoints  -> /output/checkpoints/"
echo "  Final model  -> /output/final_model/"
echo "  Test outputs -> /output/test_outputs/"
echo ""
echo "=============================================="
echo " Training Complete! $(date '+%Y-%m-%d %H:%M:%S')"
echo "=============================================="

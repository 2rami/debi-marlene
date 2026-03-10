#!/bin/bash
# =============================================================================
# CosyVoice3 Docker Fine-Tuning Runner
#
# Usage (Git Bash / WSL2 / terminal):
#   cd tts_training/cosyvoice3_docker
#   bash run.sh           # build + train
#   bash run.sh build     # build only
#   bash run.sh train     # train only (image must exist)
#   bash run.sh shell     # open shell in container (for debugging)
#
# Requirements:
#   - Docker Desktop (WSL2 backend, NVIDIA runtime)
#   - RTX 4070 Ti 12GB
#   - ../cosyvoice3_data/ (train/, dev/ with wavs)
# =============================================================================
set -e

IMAGE_NAME="cosyvoice3-train"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$PROJECT_DIR/cosyvoice3_data"
OUTPUT_DIR="$PROJECT_DIR/cosyvoice3_output"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# -----------------------------------------------------------------------------
# Pre-flight checks
# -----------------------------------------------------------------------------
preflight() {
    info "Pre-flight checks..."

    # Docker
    if ! docker info > /dev/null 2>&1; then
        error "Docker is not running. Start Docker Desktop first."
    fi

    # NVIDIA runtime
    if ! docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
        error "NVIDIA GPU not available in Docker. Check Docker Desktop -> Settings -> Resources -> WSL Integration"
    fi
    info "  Docker + NVIDIA runtime: OK"

    # Data directory
    if [ ! -d "$DATA_DIR/train/wavs" ] || [ ! -d "$DATA_DIR/dev/wavs" ]; then
        error "Data not found: $DATA_DIR/train/wavs and $DATA_DIR/dev/wavs required"
    fi

    TRAIN_COUNT=$(ls "$DATA_DIR/train/wavs/"*.wav 2>/dev/null | wc -l)
    DEV_COUNT=$(ls "$DATA_DIR/dev/wavs/"*.wav 2>/dev/null | wc -l)
    info "  Data: $TRAIN_COUNT train + $DEV_COUNT dev wavs"

    # Output directory
    mkdir -p "$OUTPUT_DIR"
    info "  Output: $OUTPUT_DIR"
    echo ""
}

# -----------------------------------------------------------------------------
# Build
# -----------------------------------------------------------------------------
build() {
    info "Building Docker image: $IMAGE_NAME"
    info "This will take 10-15 min on first build (downloads ~4GB)"
    info "Subsequent builds use Docker cache (< 1 min)"
    echo ""

    docker build \
        -t "$IMAGE_NAME" \
        -f "$SCRIPT_DIR/Dockerfile" \
        "$SCRIPT_DIR"

    echo ""
    info "Build complete: $IMAGE_NAME"
    docker images "$IMAGE_NAME" --format "  Size: {{.Size}}"
    echo ""
}

# -----------------------------------------------------------------------------
# Train
# -----------------------------------------------------------------------------
train() {
    info "Starting training..."
    info "  Data:   $DATA_DIR (mounted as /data)"
    info "  Output: $OUTPUT_DIR (mounted as /output)"
    info "  GPU:    $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'N/A')"
    echo ""
    info "Monitor progress:"
    info "  tail -f $OUTPUT_DIR/train.log"
    echo ""

    # --rm 제거: 비정상 종료 시 컨테이너 유지 (docker cp로 복구 가능)
    docker rm cosyvoice3-training 2>/dev/null || true
    docker run --gpus all \
        --shm-size 8g \
        --name cosyvoice3-training \
        -v "$DATA_DIR":/data \
        -v "$OUTPUT_DIR":/output \
        "$IMAGE_NAME" \
        bash /workspace/train.sh

    echo ""
    info "Training finished!"
    info "Results in: $OUTPUT_DIR"
    echo ""
    echo "  checkpoints/     - All training checkpoints"
    echo "  final_model/     - Ready for HuggingFace / Modal deploy"
    echo "  test_outputs/    - Generated test audio (play to evaluate)"
    echo "  train.log        - Full training log"
}

# -----------------------------------------------------------------------------
# Shell (for debugging)
# -----------------------------------------------------------------------------
shell() {
    info "Opening shell in container..."
    docker run --gpus all --rm -it \
        --shm-size 8g \
        -v "$DATA_DIR":/data \
        -v "$OUTPUT_DIR":/output \
        "$IMAGE_NAME" \
        bash
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
case "${1:-}" in
    build)
        preflight
        build
        ;;
    train)
        preflight
        train
        ;;
    shell)
        preflight
        shell
        ;;
    *)
        preflight
        build
        train
        ;;
esac

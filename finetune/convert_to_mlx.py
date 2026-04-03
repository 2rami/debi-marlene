#!/usr/bin/env python3
"""
Qwen2.5-Omni Thinker -> MLX 4-bit 변환 파이프라인

1. HuggingFace에서 Qwen2.5-Omni-7B safetensors 다운로드 (thinker 부분만)
2. thinker 텍스트 백본 추출 -> standalone Qwen2ForCausalLM으로 저장
3. PEFT LoRA adapter merge
4. MLX 4-bit 양자화 변환
5. 추론 테스트
"""

import json
import os
import sys
import shutil
from pathlib import Path
from collections import OrderedDict

os.environ.setdefault("HF_HOME", str(Path(__file__).parent / ".hf_cache"))

BASE_DIR = Path(__file__).parent
ADAPTER_DIR = BASE_DIR / "adapter"
THINKER_DIR = BASE_DIR / "thinker_base"
MERGED_DIR = BASE_DIR / "thinker_merged"
MLX_DIR = BASE_DIR / "thinker_mlx_4bit"

HF_MODEL = "Qwen/Qwen2.5-Omni-7B"

# thinker text backbone의 Qwen2 config (원본 config.json에서 추출)
QWEN2_CONFIG = {
    "architectures": ["Qwen2ForCausalLM"],
    "model_type": "qwen2",
    "hidden_act": "silu",
    "hidden_size": 3584,
    "intermediate_size": 18944,
    "vocab_size": 152064,
    "num_attention_heads": 28,
    "num_hidden_layers": 28,
    "num_key_value_heads": 4,
    "max_position_embeddings": 32768,
    "max_window_layers": 28,
    "rms_norm_eps": 1e-06,
    "rope_theta": 1000000.0,
    "rope_scaling": None,
    "use_cache": True,
    "use_sliding_window": False,
    "sliding_window": 32768,
    "tie_word_embeddings": False,
    "attention_dropout": 0.0,
    "torch_dtype": "bfloat16",
    "bos_token_id": 151643,
    "eos_token_id": 151645,
}


def step1_download():
    """HuggingFace에서 모델 파일 다운로드 (shard 1-4 + tokenizer)"""
    from huggingface_hub import snapshot_download

    cache_dir = BASE_DIR / ".hf_cache"
    marker = cache_dir / ".download_complete"
    if marker.exists():
        print("[Step 1] 이미 다운로드 완료")
        model_dir = snapshot_download(
            HF_MODEL,
            allow_patterns=[
                "model-0000[1-4]-of-00005.safetensors",
                "model.safetensors.index.json",
                "*.json", "merges.txt", "vocab.json",
                "tokenizer*", "*.jinja",
            ],
            local_dir=None,
            cache_dir=str(cache_dir),
        )
        return model_dir

    print("[Step 1] Qwen2.5-Omni-7B 다운로드 중 (shard 1-4, ~25GB)...")
    print("  파일 5(token2wav+talker)는 스킵합니다")
    model_dir = snapshot_download(
        HF_MODEL,
        allow_patterns=[
            "model-0000[1-4]-of-00005.safetensors",
            "model.safetensors.index.json",
            "*.json", "merges.txt", "vocab.json",
            "tokenizer*", "*.jinja",
        ],
        local_dir=None,
        cache_dir=str(cache_dir),
    )
    marker.touch()
    print(f"  다운로드 완료: {model_dir}")
    return model_dir


def step2_extract_thinker(model_dir: str):
    """safetensors에서 thinker 텍스트 백본만 추출"""
    if THINKER_DIR.exists() and (THINKER_DIR / "model.safetensors").exists():
        print("[Step 2] thinker 이미 추출됨")
        return

    import torch
    from safetensors import safe_open
    from safetensors.torch import save_file

    print("[Step 2] thinker 텍스트 백본 추출 중...")
    thinker_weights = OrderedDict()

    for i in range(1, 5):
        shard = Path(model_dir) / f"model-0000{i}-of-00005.safetensors"
        if not shard.exists():
            print(f"  [!] {shard.name} 없음, 스킵")
            continue
        print(f"  {shard.name} 로딩...")
        with safe_open(str(shard), framework="pt") as f:
            for key in f.keys():
                # thinker.model.* -> model.* (텍스트 백본)
                # thinker.lm_head.* -> lm_head.* (출력 헤드)
                if key.startswith("thinker.model.") or key.startswith("thinker.lm_head."):
                    new_key = key.replace("thinker.", "", 1)
                    thinker_weights[new_key] = f.get_tensor(key)

    print(f"  추출된 가중치: {len(thinker_weights)}개")

    # 저장
    THINKER_DIR.mkdir(exist_ok=True)

    # config.json
    with open(THINKER_DIR / "config.json", "w") as f:
        json.dump(QWEN2_CONFIG, f, indent=2)

    # model.safetensors
    print("  model.safetensors 저장 중...")
    save_file(thinker_weights, str(THINKER_DIR / "model.safetensors"))
    del thinker_weights

    # tokenizer 복사
    src = Path(model_dir)
    for name in ["tokenizer.json", "tokenizer_config.json", "merges.txt",
                  "vocab.json", "special_tokens_map.json", "added_tokens.json",
                  "chat_template.jinja"]:
        src_file = src / name
        if src_file.exists():
            shutil.copy2(src_file, THINKER_DIR / name)

    print(f"  저장 완료: {THINKER_DIR}")


def step3_merge_lora():
    """LoRA adapter를 base model에 merge"""
    if MERGED_DIR.exists() and (MERGED_DIR / "model.safetensors").exists():
        print("[Step 3] 이미 merge 완료")
        return

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    print("[Step 3] LoRA merge 중...")

    # adapter_config의 base_model_name_or_path를 우리 thinker 경로로 수정
    adapter_config_path = ADAPTER_DIR / "adapter_config.json"
    with open(adapter_config_path) as f:
        adapter_config = json.load(f)

    original_base = adapter_config["base_model_name_or_path"]
    adapter_config["base_model_name_or_path"] = str(THINKER_DIR)

    # 임시로 수정된 config 저장
    backup_config = json.dumps(json.load(open(adapter_config_path)), indent=2)
    with open(adapter_config_path, "w") as f:
        json.dump(adapter_config, f, indent=2)

    try:
        print("  base model 로딩...")
        model = AutoModelForCausalLM.from_pretrained(
            str(THINKER_DIR),
            torch_dtype=torch.bfloat16,
            device_map="cpu",
            low_cpu_mem_usage=True,
        )

        print("  LoRA adapter 적용...")
        model = PeftModel.from_pretrained(model, str(ADAPTER_DIR))

        print("  merge & unload...")
        model = model.merge_and_unload()

        print("  merged model 저장...")
        MERGED_DIR.mkdir(exist_ok=True)
        model.save_pretrained(str(MERGED_DIR), safe_serialization=True)

        tokenizer = AutoTokenizer.from_pretrained(str(THINKER_DIR))
        tokenizer.save_pretrained(str(MERGED_DIR))

        del model
        print(f"  저장 완료: {MERGED_DIR}")
    finally:
        # adapter_config 원래대로 복구
        with open(adapter_config_path, "w") as f:
            f.write(backup_config)


def step4_convert_mlx():
    """MLX 4-bit 양자화 변환"""
    if MLX_DIR.exists() and (MLX_DIR / "weights.npz").exists():
        print("[Step 4] 이미 MLX 변환 완료")
        return

    print("[Step 4] MLX 4-bit 변환 중...")
    ret = os.system(
        f"{sys.executable} -m mlx_lm.convert "
        f"--hf-path {MERGED_DIR} "
        f"-q --q-bits 4 "
        f"--mlx-path {MLX_DIR}"
    )
    if ret != 0:
        print("  [!] MLX 변환 실패")
        sys.exit(1)
    print(f"  변환 완료: {MLX_DIR}")


def step5_test():
    """추론 테스트"""
    print("[Step 5] 추론 테스트")
    print("=" * 50)
    from mlx_lm import load, generate

    model, tokenizer = load(str(MLX_DIR))

    system_prompt = (
        "너는 이터널리턴의 캐릭터 데비&마를렌이야. "
        "데비는 활발하고 장난기 많은 언니, 마를렌은 차분하고 말이 적은 동생이야. "
        "대답할 때 '데비:' '마를렌:' 형식으로 둘 다 말해."
    )

    questions = [
        "안녕!",
        "너 누구야?",
        "10킬 했어!",
        "계속 져...",
        "양궁장이네",
    ]

    for q in questions:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": q},
        ]
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        response = generate(model, tokenizer, prompt=prompt, max_tokens=200)
        print(f"Q: {q}")
        print(f"A: {response}")
        print("-" * 40)


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"

    if step in ("1", "download", "all"):
        model_dir = step1_download()
    if step in ("2", "extract", "all"):
        if step != "all":
            model_dir = step1_download()  # need model_dir
        step2_extract_thinker(model_dir)
    if step in ("3", "merge", "all"):
        step3_merge_lora()
    if step in ("4", "mlx", "all"):
        step4_convert_mlx()
    if step in ("5", "test", "all"):
        step5_test()

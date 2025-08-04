"""
데비 캐릭터 파인튜닝 스크립트
초보자도 쉽게 따라할 수 있도록 주석을 많이 달았어요!
"""

from unsloth import FastLanguageModel
import torch
from datasets import Dataset
import json
from trl import SFTTrainer
from transformers import TrainingArguments

# 1단계: 모델과 토크나이저 로드
print("🔥 모델 로딩중...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3.2-3b-instruct-bnb-4bit",  # 작고 빠른 모델
    max_seq_length=2048,
    dtype=None,  # 자동으로 감지
    load_in_4bit=True,  # 메모리 절약
)

# 2단계: LoRA 설정 (파인튜닝용)
print("⚙️ LoRA 설정중...")
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA 랭크 (높을수록 정확하지만 느림)
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

# 3단계: 데이터셋 로드
print("📚 데이터셋 로딩중...")
with open('training_data/debi_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 4단계: 데이터를 모델이 이해할 수 있는 형태로 변환
def format_prompt(sample):
    """대화 형태로 프롬프트 포맷팅"""
    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{sample['instruction']}<|eot_id|><|start_header_id|>user<|end_header_id|>

{sample['input']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{sample['output']}<|eot_id|>"""

# 데이터셋 변환
formatted_data = [{"text": format_prompt(sample)} for sample in data]
dataset = Dataset.from_list(formatted_data)

print(f"✅ 데이터셋 준비 완료! 총 {len(dataset)}개 샘플")

# 5단계: 트레이닝 설정
print("🏋️ 트레이닝 시작...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    dataset_num_proc=2,
    args=TrainingArguments(
        per_device_train_batch_size=2,  # 배치 크기 (메모리에 따라 조절)
        gradient_accumulation_steps=4,  # 그래디언트 누적
        warmup_steps=5,
        max_steps=30,  # 짧게 테스트용 (실제로는 100-500 추천)
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs/debi_model",  # 모델 저장할 폴더
        save_steps=10,
        save_total_limit=2,
    ),
)

# 6단계: 실제 파인튜닝 실행!
print("🚀 파인튜닝 시작! (시간이 좀 걸려요...)")
trainer_stats = trainer.train()

print("🎉 파인튜닝 완료!")
print(f"최종 loss: {trainer_stats.training_loss}")

# 7단계: 모델 저장
print("💾 모델 저장중...")
model.save_pretrained("debi_finetuned")
tokenizer.save_pretrained("debi_finetuned")

print("✅ 모든 작업 완료! 'debi_finetuned' 폴더에 저장됐어요!")

# 8단계: 테스트해보기
print("\n🧪 테스트 해보기:")
FastLanguageModel.for_inference(model)

test_input = "안녕하세요!"
inputs = tokenizer([format_prompt({"instruction": "You are Debi", "input": test_input, "output": ""})], 
                   return_tensors="pt").to("cuda")

outputs = model.generate(**inputs, max_new_tokens=64, use_cache=True)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"입력: {test_input}")
print(f"데비 응답: {response.split('assistant')[-1].strip()}")
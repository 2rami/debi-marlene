"""
마를렌 캐릭터 파인튜닝 스크립트
데비와 같은 방식이지만 마를렌 데이터로 학습
"""

from unsloth import FastLanguageModel
import torch
from datasets import Dataset
import json
from trl import SFTTrainer
from transformers import TrainingArguments

# 1단계: 모델과 토크나이저 로드
print("🔥 마를렌 모델 로딩중...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3.2-3b-instruct-bnb-4bit",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# 2단계: LoRA 설정
print("⚙️ LoRA 설정중...")
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

# 3단계: 마를렌 데이터셋 로드
print("📚 마를렌 데이터셋 로딩중...")
with open('training_data/marlene_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def format_prompt(sample):
    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{sample['instruction']}<|eot_id|><|start_header_id|>user<|end_header_id|>

{sample['input']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{sample['output']}<|eot_id|>"""

formatted_data = [{"text": format_prompt(sample)} for sample in data]
dataset = Dataset.from_list(formatted_data)

print(f"✅ 마를렌 데이터셋 준비 완료! 총 {len(dataset)}개 샘플")

# 4단계: 트레이닝
print("🏋️ 마를렌 트레이닝 시작...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    dataset_num_proc=2,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=30,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs/marlene_model",
        save_steps=10,
        save_total_limit=2,
    ),
)

# 5단계: 파인튜닝 실행
print("🚀 마를렌 파인튜닝 시작!")
trainer_stats = trainer.train()

print("🎉 마를렌 파인튜닝 완료!")
print(f"최종 loss: {trainer_stats.training_loss}")

# 6단계: 모델 저장
print("💾 마를렌 모델 저장중...")
model.save_pretrained("marlene_finetuned")
tokenizer.save_pretrained("marlene_finetuned")

print("✅ 마를렌 모델 완료! 'marlene_finetuned' 폴더에 저장됐어요!")

# 7단계: 테스트
print("\n🧪 마를렌 테스트:")
FastLanguageModel.for_inference(model)

test_input = "안녕하세요!"
inputs = tokenizer([format_prompt({"instruction": "You are Marlene", "input": test_input, "output": ""})], 
                   return_tensors="pt").to("cuda")

outputs = model.generate(**inputs, max_new_tokens=64, use_cache=True)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"입력: {test_input}")
print(f"마를렌 응답: {response.split('assistant')[-1].strip()}")
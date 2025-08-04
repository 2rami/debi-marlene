"""
로컬 파인튜닝된 모델을 사용하는 AI 유틸리티
Claude API 대신 로컬 모델 사용
"""

import discord
from typing import Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from run.config import characters

# 로컬 모델 로드
debi_model = None
debi_tokenizer = None
marlene_model = None  
marlene_tokenizer = None

async def initialize_local_models():
    """로컬 파인튜닝된 모델들 초기화"""
    global debi_model, debi_tokenizer, marlene_model, marlene_tokenizer
    
    try:
        print("🔥 데비 모델 로딩중...")
        debi_tokenizer = AutoTokenizer.from_pretrained("./debi_finetuned")
        debi_model = AutoModelForCausalLM.from_pretrained(
            "./debi_finetuned",
            torch_dtype=torch.float16,
            device_map="auto"
        )
        print("✅ 데비 모델 로드 완료!")
        
        print("🔥 마를렌 모델 로딩중...")
        marlene_tokenizer = AutoTokenizer.from_pretrained("./marlene_finetuned") 
        marlene_model = AutoModelForCausalLM.from_pretrained(
            "./marlene_finetuned",
            torch_dtype=torch.float16,
            device_map="auto"
        )
        print("✅ 마를렌 모델 로드 완료!")
        
    except Exception as e:
        print(f"❌ 로컬 모델 로드 실패: {e}")
        print("💡 먼저 파인튜닝을 실행해주세요!")

def format_prompt(character_name: str, user_message: str, context: str = "") -> str:
    """프롬프트 포맷팅 (파인튜닝할 때와 같은 형태)"""
    if character_name.lower() == "debi":
        instruction = "You are Debi from Eternal Return. Respond as the cheerful, energetic older twin sister."
    else:  # marlene
        instruction = "You are Marlene from Eternal Return. Respond as the cool, tsundere younger twin sister."
    
    full_input = user_message
    if context:
        full_input = f"게임 정보: {context}\n\n사용자: {user_message}"
    
    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{instruction}<|eot_id|><|start_header_id|>user<|end_header_id|>

{full_input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

async def generate_local_ai_response(character: Dict[str, Any], user_message: str, context: str = "") -> str:
    """로컬 파인튜닝된 모델로 AI 응답 생성"""
    character_name = character['name']
    
    # 캐릭터에 따라 적절한 모델 선택
    if character_name == "데비":
        if not debi_model or not debi_tokenizer:
            return "데비 모델이 아직 로드되지 않았어요. 잠시만 기다려주세요!"
        
        model = debi_model
        tokenizer = debi_tokenizer
        model_character = "debi"
        
    elif character_name == "마를렌":
        if not marlene_model or not marlene_tokenizer:
            return "마를렌 모델이 아직 로드되지 않았어요. 잠시만 기다려주세요!"
        
        model = marlene_model
        tokenizer = marlene_tokenizer  
        model_character = "marlene"
        
    else:
        return "알 수 없는 캐릭터입니다."
    
    try:
        # 프롬프트 생성
        prompt = format_prompt(model_character, user_message, context)
        
        # 토크나이징
        inputs = tokenizer(prompt, return_tensors="pt")
        
        # GPU 사용 가능하면 GPU로
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")
        
        # 응답 생성
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,  # 응답 길이
                temperature=0.7,     # 창의성 조절 (0~1)
                do_sample=True,      # 랜덤성 추가
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1  # 반복 방지
            )
        
        # 응답 디코딩
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # assistant 부분만 추출
        if "<|start_header_id|>assistant<|end_header_id|>" in full_response:
            response = full_response.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
        else:
            response = full_response[len(prompt):].strip()
        
        # 빈 응답 처리
        if not response:
            if character_name == "데비":
                return "와! 뭔가 말이 안 나와! 다시 말해줘!"
            else:  # 마를렌
                return "...뭐라고 말해야 할지 모르겠네."
        
        return response[:500]  # 너무 길면 자르기
        
    except Exception as e:
        print(f"로컬 AI 응답 생성 중 오류: {e}")
        if character_name == "데비":
            return "어? 뭔가 이상해! 다시 말해줘!"
        else:  # 마를렌
            return "...시스템에 문제가 있는 것 같네."

def create_character_embed(character: Dict[str, Any], title: str, description: str, user_message: str = None, author_image_override: str = None) -> discord.Embed:
    """캐릭터 임베드 생성 (기존과 동일)"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=character["color"]
    )
    
    embed.set_author(
        name=character["name"],
        icon_url=author_image_override or character["image"]
    )
    
    if user_message:
        embed.set_footer(text=f"메시지: {user_message}")
    
    return embed
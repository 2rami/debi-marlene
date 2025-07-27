import discord
from typing import Dict, Any, Optional
from anthropic import AsyncAnthropic
from config import CLAUDE_API_KEY, characters

# AI 클라이언트 초기화
anthropic_client: Optional[AsyncAnthropic] = None

async def initialize_claude_api():
    """Claude API 클라이언트 초기화"""
    global anthropic_client
    try:
        if CLAUDE_API_KEY:
            anthropic_client = AsyncAnthropic(api_key=CLAUDE_API_KEY)
            print("✅ Claude API 초기화 완료")
        else:
            print("⚠️ Claude API 키가 없습니다")
    except Exception as e:
        print(f"❌ Claude API 초기화 실패: {e}")

async def generate_ai_response(character: Dict[str, Any], user_message: str, context: str = "") -> str:
    """AI 응답 생성"""
    if not anthropic_client:
        return "AI 서비스가 일시적으로 이용할 수 없습니다."
    
    try:
        # 컨텍스트가 있으면 포함
        full_prompt = f"{character['ai_prompt']}\n\n"
        if context:
            full_prompt += f"게임 정보:\n{context}\n\n"
        full_prompt += f"사용자 메시지: {user_message}\n\n캐릭터의 성격에 맞게 자연스럽고 친근하게 답변해줘."
        
        message = await anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        
        return message.content[0].text
        
    except Exception as e:
        print(f"AI 응답 생성 중 오류: {e}")
        return f"{character['name']}이 잠시 말문이 막혔어요... 다시 말해주세요!"

def create_character_embed(character: Dict[str, Any], title: str, description: str, user_message: str = None, author_image_override: str = None) -> discord.Embed:
    """캐릭터 임베드 생성"""
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
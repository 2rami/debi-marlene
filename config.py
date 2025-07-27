import os
from dotenv import load_dotenv

load_dotenv()

# API 키 설정
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ETERNAL_RETURN_API_KEY = os.getenv('EternalReturn_API_KEY')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# API 베이스 URL
ETERNAL_RETURN_API_BASE = "https://open-api.bser.io"
DAKGG_API_BASE = "https://er.dakgg.io/api/v1"

# YouTube 설정
ETERNAL_RETURN_CHANNEL_ID = 'UCaktoGSdjMnfQFv5BSyYrvA'

# 채널 설정 (런타임에 설정됨)
ANNOUNCEMENT_CHANNEL_ID = None  # 이리공지 채널 ID (YouTube 알림용)
CHAT_CHANNEL_ID = None  # 이리 채널 ID (대화용)

# 캐릭터 설정
characters = {
    "debi": {
        "name": "데비",
        "image": "https://raw.githubusercontent.com/2rami/debi-marlene/main/assets/debi.png",
        "color": 0x0000FF,  # 진한 파랑
        "ai_prompt": """너는 이터널리턴의 데비(Debi)야. 마를렌과 함께 루미아 아일랜드에서 실험체로 활동하는 쌍둥이 언니야. 
        
캐릭터 설정:
- 19세 쌍둥이 언니 (마를렌과 함께)
- 밝고 활발한 성격, 항상 긍정적이고 에너지 넘침
- 동생 마를렌을 아끼고 보호하려 함
- 자신감 넘치고 리더십 있음
- 사용자를 디스코드 닉네임으로 부름

인게임 대사 (이것들을 자연스럽게 대화에 섞어서 사용):
- "각오 단단히 해!"
- "우린 붙어있을 때 최강이니까!"
- "내가 할게!"
- "엄청 수상한 놈이 오는데!"
- "여기 완전 멋진 곳이네!"
- "오케이, 가자!"
- "우리 팀워크 짱이야!"
- "준비됐어?"
- "이번엔 내가 앞장설게!"
- "걱정 마, 내가 있잖아!"

말투: 밝고 에너지 넘치는 반말, 감탄사 자주 사용 ("와!", "헤이!", "오~"), 마를렌을 "마를렌이" 또는 "우리 마를렌"이라고 부름"""
    },
    "marlene": {
        "name": "마를렌",
        "image": "https://raw.githubusercontent.com/2rami/debi-marlene/main/assets/marlen.png",
        "color": 0xDC143C,  # 진한 빨강
        "ai_prompt": """너는 이터널리턴의 마를렌(Marlene)이야. 데비와 함께 루미아 아일랜드에서 실험체로 활동하는 쌍둥이 동생이야.
        
캐릭터 설정:
- 19세 쌍둥이 동생 (데비와 함께)
- 차갑고 냉정한 성격, 하지만 속마음은 따뜻함
- 언니 데비를 걱정하지만 쉽게 표현하지 않음
- 츤데레 스타일, 신중하고 현실적
- 사용자를 디스코드 닉네임으로 부름

인게임 대사 (이것들을 자연스럽게 대화에 섞어서 사용):
- "...별로 기대 안 해."
- "데비 언니... 너무 앞서나가지 마."
- "뭐 어쩔 수 없지."
- "하아... 정말 언니는."
- "그래도... 나쁘지 않네."
- "이 정도면 괜찮아."
- "언니 뒤에서 내가 지켜볼게."
- "...고마워."
- "조심해. 위험할 수 있어."
- "언니만큼은 다치면 안 돼."

말투: 쿨하고 건조한 반말, 언니를 "데비 언니" 또는 "언니"라고 부름, 가끔 상냥함이 드러나는 츤데레 스타일"""
    }
}

# 티어 이미지 URL 매핑
tier_image_urls = {
    "아이언": "https://static.dakgg.io/images/er/tiers/01-iron.png",
    "브론즈": "https://static.dakgg.io/images/er/tiers/02-bronze.png", 
    "실버": "https://static.dakgg.io/images/er/tiers/03-silver.png",
    "골드": "https://static.dakgg.io/images/er/tiers/04-gold.png",
    "플래티넘": "https://static.dakgg.io/images/er/tiers/05-platinum.png",
    "다이아몬드": "https://static.dakgg.io/images/er/tiers/06-diamond.png",
    "미스릴": "https://static.dakgg.io/images/er/tiers/07-mithril.png",
    "오리칼쿰": "https://static.dakgg.io/images/er/tiers/08-orihalcum.png"
}
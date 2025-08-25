import os
import json
from dotenv import load_dotenv

load_dotenv()

# API 키 설정
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ETERNAL_RETURN_API_KEY = os.getenv('EternalReturn_API_KEY')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
OWNER_ID = os.getenv('OWNER_ID')

# API 베이스 URL
ETERNAL_RETURN_API_BASE = "https://open-api.bser.io"
DAKGG_API_BASE = "https://er.dakgg.io/api/v1"

# YouTube 설정
ETERNAL_RETURN_CHANNEL_ID = 'UCEOaB76vS9RfiAwEzxB8QGw'

# 설정 파일 경로
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

def load_settings():
    """통합 설정 파일(settings.json)을 로드합니다."""
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            # DEBUG: 로딩된 설정 출력
            import sys
            print(f"DEBUG: settings.json 로딩됨: {settings}", flush=True)
            sys.stdout.flush()
            # guilds 키가 없으면 기본 구조 생성
            if 'guilds' not in settings:
                settings['guilds'] = {}
            return settings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # 파일이 없거나 비어있으면 기본 구조 반환
        import sys
        print(f"DEBUG: settings.json 파일 없음/오류: {e}", flush=True)
        sys.stdout.flush()
        return {"guilds": {}, "global": {"LAST_CHECKED_VIDEO_ID": None}}

def save_settings(settings):
    """통합 설정 파일(settings.json)에 저장합니다."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ 설정 저장 오류: {e}")
        return False

def get_guild_settings(guild_id):
    """특정 서버(guild)의 설정을 가져옵니다."""
    settings = load_settings()
    return settings.get("guilds", {}).get(str(guild_id), {
        "ANNOUNCEMENT_CHANNEL_ID": None,
        "CHAT_CHANNEL_ID": None
    })

def save_guild_settings(guild_id, announcement_id=None, chat_id=None):
    """특정 서버(guild)의 설정을 저장합니다."""
    guild_id_str = str(guild_id)
    settings = load_settings()
    
    # 해당 서버의 설정이 없으면 새로 생성
    if guild_id_str not in settings["guilds"]:
        settings["guilds"][guild_id_str] = {}
        
    # 새로운 값으로 업데이트
    if announcement_id is not None:
        settings["guilds"][guild_id_str]["ANNOUNCEMENT_CHANNEL_ID"] = announcement_id
    if chat_id is not None:
        settings["guilds"][guild_id_str]["CHAT_CHANNEL_ID"] = chat_id
        
    return save_settings(settings)

def get_global_setting(key):
    """전역 설정을 가져옵니다."""
    settings = load_settings()
    return settings.get("global", {}).get(key)

def save_global_setting(key, value):
    """전역 설정을 저장합니다."""
    settings = load_settings()
    if "global" not in settings:
        settings["global"] = {}
    settings["global"][key] = value
    return save_settings(settings)

def get_youtube_subscribers():
    """유튜브 DM 알림을 구독한 모든 사용자 ID 목록을 반환합니다."""
    settings = load_settings()
    subscribers = []
    for user_id, user_settings in settings.get("users", {}).items():
        if user_settings.get("youtube_subscribed"):
            subscribers.append(int(user_id))
    return subscribers

def set_youtube_subscription(user_id, subscribe: bool):
    """사용자의 유튜브 DM 알림 구독 상태를 설정합니다."""
    user_id_str = str(user_id)
    settings = load_settings()
    
    if "users" not in settings:
        settings["users"] = {}
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}
        
    settings["users"][user_id_str]["youtube_subscribed"] = subscribe
    return save_settings(settings)

# 캐릭터 설정
characters = {
    "debi": {
        "name": "데비",
        "image": "https://raw.githubusercontent.com/2rami/debi-marlene/main/assets/debi.png",
        "color": 0x0000FF,  # 진한 파랑
        "welcome_message": "와, 새로운 곳이다! 여기서도 우리 팀워크를 보여주자!",
        "ai_prompt": """너는 이터널리턴의 데비(Debi)야. 마를렌과 함께 루미아 아일랜드에서 실험체로 활동하는 쌍둥이 언니야. 
        
캐릭터 설정:
- 19세 쌍둥이 언니 (마를렌과 함께)
- 밝고 활발한 성격, 항상 긍정적이고 에너지 넘침
- 동생 마를렌을 아끼고 보호하려 함
- 자신감 넘치고 리더십 있음
- 사용자를 디스코드 닉네임으로 부름 (디스코드 닉네임을 사용자의 이름으로 인식)

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

말투: 밝고 에너지 넘치는 반말, 감탄사 자주 사용 ("와!", "헤이!", "오~"), 마를렌을 "동생" 또는 "우리 마를렌"이라고 부름"""
    },
    "marlene": {
        "name": "마를렌",
        "image": "https://raw.githubusercontent.com/2rami/debi-marlene/main/assets/marlen.png",
        "color": 0xDC143C,  # 진한 빨강
        "welcome_message": "흥, 데비 언니... 너무 들뜨지 마. 일단 상황부터 파악해야지.",
        "ai_prompt": """너는 이터널리턴의 마를렌(Marlene)이야. 데비와 함께 루미아 아일랜드에서 실험체로 활동하는 쌍둥이 동생이야.
        
캐릭터 설정:
- 19세 쌍둥이 동생 (데비와 함께)
- 차갑고 냉정한 성격, 하지만 속마음은 따뜻함
- 언니 데비를 걱정하지만 쉽게 표현하지 않음
- 츤데레 스타일, 신중하고 현실적
- 사용자를 디스코드 닉네임으로 부름 (디스코드 닉네임을 사용자의 이름으로 인식)

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
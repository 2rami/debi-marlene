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

# 로컬 설정 파일 사용 안 함 (GCS만 사용)
# SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

# GCS 설정
GCS_BUCKET = 'debi-marlene-settings'
GCS_KEY = 'settings.json'
gcs_client = None

# 설정 캐시 (성능 개선)
settings_cache = None
cache_timestamp = 0
CACHE_DURATION = 5  # 5초 캐시

def get_gcs_client():
    """GCS 클라이언트를 가져옵니다."""
    global gcs_client
    if gcs_client is None:
        try:
            from google.cloud import storage
            gcs_client = storage.Client()
            # 버킷 접근 테스트
            bucket = gcs_client.bucket(GCS_BUCKET)
            bucket.exists()
            print(f"✅ GCS 연결 성공: {GCS_BUCKET}", flush=True)
        except Exception as e:
            print(f"⚠️ GCS 클라이언트 생성 실패: {e}", flush=True)
            gcs_client = False  # 실패를 명시적으로 표시
    return gcs_client if gcs_client != False else None

def load_settings():
    """GCS에서 설정 파일(settings.json)을 로드합니다."""
    global settings_cache, cache_timestamp
    import time

    current_time = time.time()

    # 캐시된 설정이 있고 아직 유효하면 사용
    if settings_cache is not None and (current_time - cache_timestamp) < CACHE_DURATION:
        return settings_cache.copy()

    # GCS에서 로드
    client = get_gcs_client()
    if client:
        try:
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_KEY)
            settings_data = blob.download_as_text()
            settings = json.loads(settings_data)
            print(f"✅ GCS에서 설정 로드 완료", flush=True)
            # guilds 키가 없으면 기본 구조 생성
            if 'guilds' not in settings:
                settings['guilds'] = {}
            # 캐시 업데이트
            settings_cache = settings.copy()
            cache_timestamp = current_time
            return settings
        except Exception as e:
            print(f"⚠️ GCS 로드 실패 (기본값 사용): {e}", flush=True)

    # GCS 실패 시 기본 구조 반환
    default_settings = {"guilds": {}, "users": {}, "global": {"LAST_CHECKED_VIDEO_ID": None}}
    settings_cache = default_settings.copy()
    cache_timestamp = current_time
    return default_settings

def save_settings(settings, silent=False):
    """GCS에 설정 파일(settings.json)을 저장합니다.

    Args:
        settings: 저장할 설정 데이터
        silent: True면 로그 출력 안 함 (대량 저장 시)
    """
    global settings_cache, cache_timestamp

    # 캐시 무효화
    settings_cache = None
    cache_timestamp = 0

    # GCS에만 저장
    client = get_gcs_client()
    if client:
        try:
            json_data = json.dumps(settings, indent=2, ensure_ascii=False)
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_KEY)
            blob.upload_from_string(json_data, content_type='application/json')
            if not silent:
                print(f"✅ GCS 설정 저장 완료", flush=True)
            return True
        except Exception as e:
            if not silent:
                print(f"❌ GCS 설정 저장 오류: {e}", flush=True)
            return False
    else:
        if not silent:
            print(f"❌ GCS 클라이언트 없음 - 설정 저장 실패", flush=True)
        return False

def get_guild_settings(guild_id):
    """특정 서버(guild)의 설정을 가져옵니다."""
    settings = load_settings()
    return settings.get("guilds", {}).get(str(guild_id), {
        "ANNOUNCEMENT_CHANNEL_ID": None,
        "CHAT_CHANNEL_ID": None
    })

def save_guild_settings(guild_id, announcement_id=None, chat_id=None, guild_name=None, announcement_channel_name=None, chat_channel_name=None, silent=False):
    """특정 서버(guild)의 설정을 저장합니다.

    Args:
        silent: True면 로그 출력 안 함 (대량 저장 시)
    """
    guild_id_str = str(guild_id)
    settings = load_settings()

    # 해당 서버의 설정이 없으면 새로 생성
    if guild_id_str not in settings["guilds"]:
        settings["guilds"][guild_id_str] = {}

    # 서버 이름 저장
    if guild_name is not None:
        settings["guilds"][guild_id_str]["GUILD_NAME"] = guild_name

    # 새로운 값으로 업데이트
    if announcement_id is not None:
        settings["guilds"][guild_id_str]["ANNOUNCEMENT_CHANNEL_ID"] = announcement_id
        if announcement_channel_name is not None:
            settings["guilds"][guild_id_str]["ANNOUNCEMENT_CHANNEL_NAME"] = announcement_channel_name
    if chat_id is not None:
        settings["guilds"][guild_id_str]["CHAT_CHANNEL_ID"] = chat_id
        if chat_channel_name is not None:
            settings["guilds"][guild_id_str]["CHAT_CHANNEL_NAME"] = chat_channel_name

    return save_settings(settings, silent=silent)

def remove_guild_settings(guild_id):
    """특정 서버(guild)에 삭제됨 표시를 추가합니다."""
    global settings_cache, cache_timestamp
    import time
    from datetime import datetime
    
    guild_id_str = str(guild_id)
    print(f"DEBUG: remove_guild_settings 호출됨 - 서버 ID: {guild_id}", flush=True)
    
    # 즉시 캐시 무효화 (빠른 반영을 위해)
    settings_cache = None
    cache_timestamp = 0
    print(f"DEBUG: 캐시 즉시 무효화 완료", flush=True)
    
    settings = load_settings()
    
    if guild_id_str in settings["guilds"]:
        print(f"DEBUG: 서버 설정 발견, 삭제됨 표시 추가 중: {guild_id_str}", flush=True)
        
        # 기존 설정에 삭제됨 표시 추가
        settings["guilds"][guild_id_str]["STATUS"] = "삭제됨"
        settings["guilds"][guild_id_str]["REMOVED_AT"] = datetime.now().isoformat()
        
        # 삭제 후 즉시 캐시 무효화 (저장 전에도)
        settings_cache = None
        cache_timestamp = 0
        
        print(f"DEBUG: save_settings 호출 전 - 삭제됨 표시된 설정: {settings['guilds'][guild_id_str]}", flush=True)
        result = save_settings(settings)
        print(f"DEBUG: 서버 삭제됨 표시 완료 결과: {result}", flush=True)
        
        # 저장 후 실제 확인
        print(f"DEBUG: 저장 후 확인 - 설정 다시 로드 중...", flush=True)
        verification_settings = load_settings()
        if guild_id_str in verification_settings["guilds"]:
            print(f"DEBUG: 확인 완료 - 저장된 설정: {verification_settings['guilds'][guild_id_str]}", flush=True)
        else:
            print(f"DEBUG: 확인 실패 - 서버 설정이 없음: {guild_id_str}", flush=True)
        
        # 저장 후 한 번 더 캐시 무효화 확인
        settings_cache = None
        cache_timestamp = 0
        print(f"DEBUG: 삭제됨 표시 후 최종 캐시 무효화 완료", flush=True)
        
        return result
    else:
        print(f"DEBUG: 서버 설정이 존재하지 않음: {guild_id_str}", flush=True)
    return True  # 이미 없는 경우도 성공으로 처리

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

def save_last_video_info(video_id, video_title=None):
    """마지막 체크된 비디오 정보를 저장합니다."""
    settings = load_settings()
    if "global" not in settings:
        settings["global"] = {}
    
    settings["global"]["LAST_CHECKED_VIDEO_ID"] = video_id
    if video_title:
        settings["global"]["LAST_CHECKED_VIDEO_TITLE"] = video_title
    
    return save_settings(settings)

def get_youtube_subscribers():
    """유튜브 DM 알림을 구독한 모든 사용자 ID 목록을 반환합니다."""
    settings = load_settings()
    subscribers = []
    for user_id, user_settings in settings.get("users", {}).items():
        if user_settings.get("youtube_subscribed"):
            subscribers.append(int(user_id))
    return subscribers

def log_user_interaction(user_id, user_name=None):
    """사용자가 봇과 상호작용했을 때 기록합니다."""
    settings = load_settings()
    if "users" not in settings:
        settings["users"] = {}
    
    user_id_str = str(user_id)
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}
    
    # 마지막 상호작용 시간 업데이트
    from datetime import datetime
    settings["users"][user_id_str]["last_interaction"] = datetime.now().isoformat()
    settings["users"][user_id_str]["interaction_count"] = settings["users"][user_id_str].get("interaction_count", 0) + 1
    
    # 사용자 이름 저장
    if user_name:
        settings["users"][user_id_str]["user_name"] = user_name
    
    save_settings(settings)

def get_interaction_users():
    """실제 봇과 상호작용한 사용자 ID 목록을 반환합니다."""
    settings = load_settings()
    interaction_users = []
    for user_id, user_settings in settings.get("users", {}).items():
        if user_settings.get("last_interaction"):  # 상호작용 기록이 있는 사용자만
            interaction_users.append(int(user_id))
    return interaction_users

def get_all_users():
    """모든 등록된 사용자 정보를 반환합니다."""
    settings = load_settings()
    users = []
    for user_id, user_settings in settings.get("users", {}).items():
        users.append({
            'id': int(user_id),
            'youtube_subscribed': user_settings.get("youtube_subscribed", False),
            'first_interaction': user_settings.get("first_interaction"),
            'last_seen': user_settings.get("last_seen"),
            'server_admin': user_settings.get("server_admin", False)
        })
    return users

def add_user_interaction(user_id, interaction_type="general"):
    """사용자 상호작용을 기록합니다."""
    user_id_str = str(user_id)
    settings = load_settings()
    
    if "users" not in settings:
        settings["users"] = {}
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}
    
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if "first_interaction" not in settings["users"][user_id_str]:
        settings["users"][user_id_str]["first_interaction"] = now
    
    settings["users"][user_id_str]["last_seen"] = now
    settings["users"][user_id_str]["interaction_type"] = interaction_type
    
    return save_settings(settings)

def set_youtube_subscription(user_id, subscribe: bool, user_name=None):
    """사용자의 유튜브 DM 알림 구독 상태를 설정합니다."""
    user_id_str = str(user_id)
    settings = load_settings()
    
    if "users" not in settings:
        settings["users"] = {}
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}
        
    settings["users"][user_id_str]["youtube_subscribed"] = subscribe
    
    # 사용자 이름 저장
    if user_name:
        settings["users"][user_id_str]["user_name"] = user_name
    
    # 상호작용도 기록
    add_user_interaction(user_id, "youtube_subscription")
    return save_settings(settings)

def get_server_admins(guild_id=None):
    """서버 관리자 목록을 반환합니다. guild_id가 주어지면 해당 서버의 관리자만 반환."""
    settings = load_settings()
    admins = []
    
    if guild_id:
        # 특정 서버의 관리자만 조회
        guild_str = str(guild_id)
        for user_id, user_settings in settings.get("users", {}).items():
            if user_settings.get("admin_servers", {}).get(guild_str):
                admins.append(int(user_id))
    else:
        # 모든 서버 관리자 조회
        for user_id, user_settings in settings.get("users", {}).items():
            if user_settings.get("admin_servers"):
                admins.append({
                    'user_id': int(user_id),
                    'admin_servers': list(user_settings.get("admin_servers", {}).keys())
                })
    
    return admins

def set_server_admin(user_id, guild_id, is_admin=True):
    """사용자를 특정 서버의 관리자로 설정하거나 해제합니다."""
    user_id_str = str(user_id)
    guild_str = str(guild_id)
    settings = load_settings()
    
    if "users" not in settings:
        settings["users"] = {}
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}
    if "admin_servers" not in settings["users"][user_id_str]:
        settings["users"][user_id_str]["admin_servers"] = {}
    
    settings["users"][user_id_str]["admin_servers"][guild_str] = is_admin
    
    # 상호작용 기록
    add_user_interaction(user_id, "admin_role_change")

    return save_settings(settings)

def save_dm_channel(user_id, channel_id, user_name=None):
    """사용자의 DM 채널 정보를 저장합니다."""
    user_id_str = str(user_id)
    settings = load_settings()

    if "users" not in settings:
        settings["users"] = {}
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}

    # DM 채널 ID 저장
    settings["users"][user_id_str]["dm_channel_id"] = str(channel_id)

    # 사용자 이름 저장
    if user_name:
        settings["users"][user_id_str]["user_name"] = user_name

    # 마지막 DM 시간 기록
    from datetime import datetime
    settings["users"][user_id_str]["last_dm"] = datetime.now().isoformat()

    print(f"✅ DM 채널 정보 저장: {user_name} ({user_id}) -> 채널 #{channel_id}")
    return save_settings(settings)

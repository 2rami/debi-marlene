import os
import json
from dotenv import load_dotenv

# override=False: app.py에서 이미 설정한 GOOGLE_APPLICATION_CREDENTIALS를 유지
load_dotenv(override=False)

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

# GCS 설정
GCS_BUCKET = 'debi-marlene-settings'
GCS_KEY = 'settings.json'
GCS_REMOVED_SERVERS_KEY = 'removed_servers.json'
GCS_COMMAND_LOGS_KEY = 'command_logs.json'
gcs_client = None

# 설정 캐시 (save 시에만 무효화)
settings_cache = None

def get_gcs_client():
    """GCS 클라이언트를 가져옵니다."""
    global gcs_client
    if gcs_client is None:
        try:
            # 디버깅: 환경변수 확인
            creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            print(f"[GCS] GOOGLE_APPLICATION_CREDENTIALS: {creds_path}", flush=True)

            if creds_path:
                if os.path.exists(creds_path):
                    print(f"[GCS] 인증 파일 존재함", flush=True)
                    # 파일 내용 일부 확인
                    with open(creds_path, 'r') as f:
                        content = f.read()
                        print(f"[GCS] 인증 파일 크기: {len(content)} bytes", flush=True)
                else:
                    print(f"[GCS] 인증 파일이 존재하지 않음!", flush=True)

            from google.cloud import storage
            # authorized_user credentials는 project_id가 없으므로 명시적으로 지정
            gcs_client = storage.Client(project='ironic-objectivist-465713-a6')
            print(f"[GCS] Client 생성 성공", flush=True)

            # 버킷 접근 테스트
            bucket = gcs_client.bucket(GCS_BUCKET)
            exists = bucket.exists()
            print(f"[GCS] 버킷 '{GCS_BUCKET}' 존재: {exists}", flush=True)

        except Exception as e:
            import traceback
            print(f"[GCS 오류] 클라이언트 생성 실패: {e}", flush=True)
            print(f"[GCS 오류] 상세: {traceback.format_exc()}", flush=True)
            gcs_client = False  # 실패를 명시적으로 표시
    return gcs_client if gcs_client != False else None

def load_settings(force_reload=False):
    """GCS 또는 로컬 백업에서 설정 파일을 로드합니다. (GCS 우선)"""
    global settings_cache

    # 캐시가 있으면 바로 반환 (save_settings에서만 무효화)
    if not force_reload and settings_cache is not None:
        return settings_cache.copy()

    # 1순위: GCS에서 로드
    client = get_gcs_client()
    if client:
        try:
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_KEY)
            settings_data = blob.download_as_text()
            settings = json.loads(settings_data)
            # guilds 키가 없으면 기본 구조 생성
            if 'guilds' not in settings:
                settings['guilds'] = {}
            # 캐시 업데이트
            settings_cache = settings.copy()
            return settings
        except Exception as e:
            print(f"[경고] GCS 로드 실패: {e}", flush=True)

    # 2순위: 로컬 백업 파일에서 로드 (GCS 실패 시 폴백)
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        backup_file = os.path.join(project_root, 'backups', 'settings_backup.json')

        if os.path.exists(backup_file):
            with open(backup_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            # guilds 키가 없으면 기본 구조 생성
            if 'guilds' not in settings:
                settings['guilds'] = {}
            # 캐시 업데이트
            settings_cache = settings.copy()
            print(f"[로컬] 설정 로드 완료 (GCS 실패 - 로컬 백업 사용)", flush=True)
            return settings
    except Exception as e:
        print(f"[경고] 로컬 백업 로드 실패: {e}", flush=True)

    # 모두 실패 시 기본 구조 반환
    print(f"[기본값] 새로운 설정 생성", flush=True)
    default_settings = {"guilds": {}, "users": {}, "global": {"LAST_CHECKED_VIDEO_ID": None}}
    settings_cache = default_settings.copy()
    return default_settings

def save_local_backup(settings):
    """로컬에 settings 백업을 저장합니다.

    Args:
        settings: 백업할 설정 데이터

    Returns:
        bool: 저장 성공 여부
    """
    import os

    try:
        # 프로젝트 루트 경로 가져오기
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        backup_dir = os.path.join(project_root, 'backups')
        backup_file = os.path.join(backup_dir, 'settings_backup.json')

        # backups 폴더가 없으면 생성
        os.makedirs(backup_dir, exist_ok=True)

        # JSON 파일로 저장
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"[경고] 로컬 백업 저장 실패: {e}", flush=True)
        return False

def save_settings(settings, silent=False):
    """GCS에 설정을 저장하고, 로컬 백업에도 저장합니다. (GCS 우선)

    Args:
        settings: 저장할 설정 데이터
        silent: True면 로그 출력 안 함 (대량 저장 시)
    """
    global settings_cache

    # 캐시 무효화
    settings_cache = None

    gcs_success = False

    # 1순위: GCS에 저장 (주 저장소)
    client = get_gcs_client()
    if client:
        try:
            json_data = json.dumps(settings, indent=2, ensure_ascii=False)
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_KEY)
            blob.upload_from_string(json_data, content_type='application/json')
            gcs_success = True
            if not silent:
                print(f"[GCS] 설정 저장 완료", flush=True)
        except Exception as e:
            if not silent:
                print(f"[경고] GCS 설정 저장 실패: {e}", flush=True)

    # 2순위: 로컬 백업에도 저장 (백업용)
    local_success = save_local_backup(settings)
    if not local_success and not silent:
        print(f"[경고] 로컬 백업 저장 실패", flush=True)

    # GCS 저장 성공 여부 반환 (주 저장소 기준)
    return gcs_success

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

def load_removed_servers():
    """GCS에서 삭제된 서버 목록을 로드합니다."""
    client = get_gcs_client()
    if client:
        try:
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_REMOVED_SERVERS_KEY)
            if blob.exists():
                data = blob.download_as_text()
                return json.loads(data)
        except Exception as e:
            print(f"[경고] 삭제된 서버 목록 로드 실패: {e}", flush=True)
    return {"removed_servers": []}


def unmark_removed_server(guild_id):
    """재참가한 서버를 removed_servers.json에서 제거합니다."""
    try:
        removed_data = load_removed_servers()
        guild_id_str = str(guild_id)
        original_count = len(removed_data.get("removed_servers", []))
        removed_data["removed_servers"] = [
            s for s in removed_data.get("removed_servers", [])
            if str(s.get("guild_id")) != guild_id_str
        ]
        new_count = len(removed_data["removed_servers"])
        if new_count < original_count:
            client = get_gcs_client()
            if client:
                bucket = client.bucket(GCS_BUCKET)
                blob = bucket.blob(GCS_REMOVED_SERVERS_KEY)
                blob.upload_from_string(
                    json.dumps(removed_data, indent=2, ensure_ascii=False),
                    content_type='application/json'
                )
                print(f"[완료] 재참가 서버 removed_servers에서 제거: {guild_id}", flush=True)
                return True
    except Exception as e:
        print(f"[오류] removed_servers 제거 실패: {e}", flush=True)
    return False


def save_removed_server(guild_id, guild_name, member_count=None):
    """삭제된 서버 정보를 GCS에 저장합니다."""
    from datetime import datetime

    try:
        removed_data = load_removed_servers()

        # 새로운 삭제 정보 추가
        removed_info = {
            "guild_id": str(guild_id),
            "guild_name": guild_name,
            "removed_at": datetime.now().isoformat(),
            "member_count": member_count
        }

        removed_data["removed_servers"].append(removed_info)

        # GCS에 저장
        client = get_gcs_client()
        if client:
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_REMOVED_SERVERS_KEY)
            blob.upload_from_string(
                json.dumps(removed_data, indent=2, ensure_ascii=False),
                content_type='application/json'
            )
            print(f"[완료] 삭제된 서버 기록 완료: {guild_name} (ID: {guild_id})", flush=True)
            return True
    except Exception as e:
        print(f"[오류] 삭제된 서버 저장 실패: {e}", flush=True)
        import traceback
        traceback.print_exc()
    return False


def remove_guild_settings(guild_id):
    """특정 서버(guild)에 삭제됨 표시를 추가합니다."""
    global settings_cache
    from datetime import datetime

    guild_id_str = str(guild_id)

    settings_cache = None
    settings = load_settings()

    if guild_id_str in settings["guilds"]:
        settings["guilds"][guild_id_str]["STATUS"] = "삭제됨"
        settings["guilds"][guild_id_str]["REMOVED_AT"] = datetime.now().isoformat()

        return save_settings(settings)

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
    """실제 DM을 보낸 사용자 ID 목록을 반환합니다."""
    settings = load_settings()
    interaction_users = []
    for user_id, user_settings in settings.get("users", {}).items():
        # interaction_count가 1 이상인 사용자만 (실제 DM을 보낸 사용자)
        if user_settings.get("interaction_count", 0) > 0:
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
    """사용자 상호작용을 기록합니다. (DM 외 용도 - interaction_count 증가 안 함)"""
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

    return save_settings(settings)


def is_youtube_subscribed(user_id) -> bool:
    """사용자의 유튜브 DM 알림 구독 상태를 확인합니다."""
    settings = load_settings()
    user_id_str = str(user_id)
    return settings.get("users", {}).get(user_id_str, {}).get("youtube_subscribed", False)


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

    return save_settings(settings)

def save_user_dm_interaction(user_id, channel_id, user_name=None):
    """DM을 보낸 사용자의 정보를 GCS에 저장합니다. (통합 함수)

    Args:
        user_id: 사용자 Discord ID
        channel_id: DM 채널 ID
        user_name: 사용자 이름 (선택)

    저장 내용:
        - DM 채널 정보
        - interaction count (DM 횟수)
        - 마지막 상호작용 시간
        - 사용자 이름
    """
    from datetime import datetime

    user_id_str = str(user_id)
    settings = load_settings()

    if "users" not in settings:
        settings["users"] = {}
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}

    user_data = settings["users"][user_id_str]

    # DM 채널 ID 저장
    user_data["dm_channel_id"] = str(channel_id)

    # 사용자 이름 저장
    if user_name:
        user_data["user_name"] = user_name

    # DM 시간 기록
    user_data["last_dm"] = datetime.now().isoformat()
    user_data["last_interaction"] = datetime.now().isoformat()

    # interaction count 증가 (DM을 보낸 횟수)
    user_data["interaction_count"] = user_data.get("interaction_count", 0) + 1

    return save_settings(settings, silent=True)


def save_dm_channel(user_id, channel_id, user_name=None):
    """[DEPRECATED] save_user_dm_interaction 사용 권장
    유튜브 서비스 등 기존 코드 호환성을 위해 유지"""
    return save_user_dm_interaction(user_id, channel_id, user_name)


def cleanup_removed_servers(active_guild_ids=None):
    """삭제된 서버를 settings.json에서 완전히 제거합니다.

    removed_servers.json에 기록된 서버들을 settings.json의 guilds에서 삭제합니다.
    active_guild_ids가 주어지면 현재 봇이 접속 중인 서버는 건너뜁니다.

    Returns:
        dict: 정리 결과 (removed_count, cleaned_servers)
    """
    active_ids = set(str(gid) for gid in (active_guild_ids or []))

    try:
        # 삭제된 서버 목록 로드
        removed_data = load_removed_servers()
        removed_servers = removed_data.get("removed_servers", [])

        if not removed_servers:
            print("[정보] 삭제된 서버가 없습니다.", flush=True)
            return {"removed_count": 0, "cleaned_servers": []}

        # 현재 설정 로드
        settings = load_settings()

        cleaned_servers = []
        removed_count = 0
        skipped = []

        for removed_server in removed_servers:
            guild_id = str(removed_server.get("guild_id"))
            guild_name = removed_server.get("guild_name", "알 수 없음")

            # 현재 봇이 접속 중인 서버는 건너뛰기 (재참가한 서버)
            if guild_id in active_ids:
                skipped.append(guild_name)
                continue

            # settings.json에서 해당 서버 삭제
            if guild_id in settings.get("guilds", {}):
                del settings["guilds"][guild_id]
                cleaned_servers.append({
                    "guild_id": guild_id,
                    "guild_name": guild_name,
                    "removed_at": removed_server.get("removed_at")
                })
                removed_count += 1
                print(f"[정리] 삭제된 서버 제거: {guild_name} (ID: {guild_id})", flush=True)

        # 변경사항 저장
        if removed_count > 0:
            save_settings(settings)
            print(f"[완료] {removed_count}개의 삭제된 서버 정리 완료", flush=True)
        else:
            print("[정보] 정리할 서버가 없습니다.", flush=True)

        if skipped:
            print(f"[정보] 재참가 서버 {len(skipped)}개 건너뜀: {', '.join(skipped)}", flush=True)

        # removed_servers.json에서 처리 완료된 항목 + 재참가 서버 제거
        remaining = [s for s in removed_servers if str(s.get("guild_id")) in active_ids]
        # 재참가 서버만 남기지 않고 전부 비우기 (처리 완료)
        removed_data["removed_servers"] = []
        try:
            client = get_gcs_client()
            if client:
                bucket = client.bucket(GCS_BUCKET)
                blob = bucket.blob(GCS_REMOVED_SERVERS_KEY)
                blob.upload_from_string(
                    json.dumps(removed_data, indent=2, ensure_ascii=False),
                    content_type='application/json'
                )
        except Exception:
            pass

        return {
            "removed_count": removed_count,
            "cleaned_servers": cleaned_servers
        }

    except Exception as e:
        print(f"[오류] 삭제된 서버 정리 실패: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return {"removed_count": 0, "cleaned_servers": [], "error": str(e)}

def save_command_log(log_entry):
    """명령어 사용 로그를 GCS에 저장합니다.

    Args:
        log_entry: 로그 항목 (dict)
            - command_name: 명령어 이름
            - user_id: 사용자 ID
            - user_name: 사용자 이름
            - guild_id: 서버 ID (optional)
            - guild_name: 서버 이름 (optional)
            - timestamp: ISO 형식 타임스탬프
            - args: 명령어 인자 (dict)
    """
    from datetime import datetime, timedelta, timezone

    KST = timezone(timedelta(hours=9))

    try:
        client = get_gcs_client()
        if not client:
            return False

        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_COMMAND_LOGS_KEY)

        # 기존 로그 로드 (없으면 빈 구조 생성)
        if blob.exists():
            logs_data = json.loads(blob.download_as_text())
        else:
            logs_data = {"logs": []}

        # 새 로그 추가
        logs_data["logs"].append(log_entry)

        # 30일 이상 된 로그 삭제 (로그 로테이션)
        cutoff_date = datetime.now(KST) - timedelta(days=30)
        def _parse_ts(ts_str):
            dt = datetime.fromisoformat(ts_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=KST)
            return dt
        logs_data["logs"] = [
            log for log in logs_data["logs"]
            if _parse_ts(log.get("timestamp", "2000-01-01")) > cutoff_date
        ]

        # GCS에 저장
        blob.upload_from_string(
            json.dumps(logs_data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )

        return True

    except Exception as e:
        print(f"[경고] 명령어 로그 저장 실패: {e}", flush=True)
        return False

def load_command_logs(filters=None):
    """명령어 사용 로그를 GCS에서 로드합니다.

    Args:
        filters: 필터 딕셔너리 (optional)
            - guild_id: 특정 서버의 로그만 (str)
            - user_id: 특정 사용자의 로그만 (str)
            - command_name: 특정 명령어의 로그만 (str)
            - start_date: 시작 날짜 (ISO 형식 str)
            - end_date: 종료 날짜 (ISO 형식 str)
            - limit: 최대 개수 (int)

    Returns:
        list: 필터링된 로그 항목 리스트 (최신순)
    """
    from datetime import datetime

    try:
        client = get_gcs_client()
        if not client:
            return []

        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_COMMAND_LOGS_KEY)

        if not blob.exists():
            return []

        logs_data = json.loads(blob.download_as_text())
        logs = logs_data.get("logs", [])

        # 필터 적용
        if filters:
            # 서버 ID 필터
            if filters.get("guild_id"):
                logs = [log for log in logs if log.get("guild_id") == str(filters["guild_id"])]

            # 사용자 ID 필터
            if filters.get("user_id"):
                logs = [log for log in logs if log.get("user_id") == str(filters["user_id"])]

            # 명령어 이름 필터
            if filters.get("command_name"):
                logs = [log for log in logs if log.get("command_name") == filters["command_name"]]

            # 날짜 범위 필터
            if filters.get("start_date"):
                start = datetime.fromisoformat(filters["start_date"])
                logs = [log for log in logs if datetime.fromisoformat(log["timestamp"]) >= start]

            if filters.get("end_date"):
                end = datetime.fromisoformat(filters["end_date"])
                logs = [log for log in logs if datetime.fromisoformat(log["timestamp"]) <= end]

        # 최신순 정렬 (타임스탬프 기준 내림차순) - limit 적용 전에 정렬해야 함
        logs.sort(key=lambda x: x["timestamp"], reverse=True)

        # 개수 제한 (정렬 후 적용)
        if filters and filters.get("limit"):
            logs = logs[:filters["limit"]]

        return logs

    except Exception as e:
        print(f"[경고] 명령어 로그 로드 실패: {e}", flush=True)
        return []

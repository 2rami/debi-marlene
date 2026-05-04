import os
import json
import threading
from dotenv import load_dotenv

# BOT_ENV_FILE이 지정되면 해당 파일을 로드 (솔로봇 로컬 테스트용 .env.solo-debi 등).
# 미지정 시 기본 .env. override=False로 이미 설정된 env(예: GOOGLE_APPLICATION_CREDENTIALS)는 유지.
_env_file = os.getenv('BOT_ENV_FILE', '.env')
load_dotenv(_env_file, override=False)

# 봇 페르소나 식별자 — 'unified'(기본, 기존 데비&마를렌 봇) | 'debi' | 'marlene'
# 솔로봇은 메모리 스코프 prefix로 기존봇과 격리 + 응답 파싱으로 자기 페르소나 대사만 추출.
BOT_IDENTITY = os.getenv('BOT_IDENTITY', 'unified').lower()

# API 키 설정
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ETERNAL_RETURN_API_KEY = os.getenv('EternalReturn_API_KEY')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
OWNER_ID = os.getenv('OWNER_ID')
DISCORD_LOG_WEBHOOK = os.getenv('DISCORD_LOG_WEBHOOK')

# API 베이스 URL
ETERNAL_RETURN_API_BASE = "https://open-api.bser.io"
DAKGG_API_BASE = "https://er.dakgg.io/api/v1"

# YouTube 설정
ETERNAL_RETURN_CHANNEL_ID = 'UCEOaB76vS9RfiAwEzxB8QGw'

# GCP 설정
# 명시적 default — gcloud config 의존 없이 안정적으로 동작
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'ironic-objectivist-465713-a6')
GCS_BUCKET = os.getenv('GCS_BUCKET_NAME', 'debi-marlene-settings')
GCS_KEY = 'settings.json'  # 레거시 fallback 전용

# 저장소 모드 (점진 전환용)
# - 'firestore': Firestore 단독 (이번 작업 기본값)
# - 'dual': Firestore + GCS 둘 다 쓰기 (안전 모드, 1주 dual-write 후 firestore 전환)
# - 'gcs': 레거시 (롤백용)
SETTINGS_BACKEND = os.getenv('SETTINGS_BACKEND', 'firestore').lower()

# 클라이언트 싱글톤
gcs_client = None
firestore_client = None
_gcs_client_lock = threading.Lock()
_firestore_client_lock = threading.Lock()

# 설정 캐시
# - listener 활성 시: snapshot callback 이 자동 동기화 → load_settings 는 read 0회
# - listener 비활성 시 (init 실패/dashboard 단발 호출): 기존처럼 lazy load
settings_cache = None
_cache_lock = threading.Lock()
_listeners_active = False
_listener_watches = []  # unsubscribe 용 핸들 보관
_first_snapshot_event = threading.Event()  # 첫 동기화 완료 대기


# ───────────────────── 클라이언트 초기화 ─────────────────────

def get_gcs_client():
    """GCS 클라이언트를 가져옵니다 (싱글톤, 스레드 안전). welcome_images / settings.json 레거시 fallback 용."""
    global gcs_client
    if gcs_client is not None:
        return gcs_client if gcs_client is not False else None

    with _gcs_client_lock:
        if gcs_client is not None:
            return gcs_client if gcs_client is not False else None

        try:
            from google.cloud import storage
            gcs_client = storage.Client(project=GCP_PROJECT_ID)
            print(f"[GCS] Client 생성 성공", flush=True)
        except Exception as e:
            import traceback
            print(f"[GCS 오류] 클라이언트 생성 실패: {e}", flush=True)
            print(f"[GCS 오류] 상세: {traceback.format_exc()}", flush=True)
            gcs_client = False
    return gcs_client if gcs_client != False else None


def get_firestore_client():
    """Firestore 클라이언트를 가져옵니다 (싱글톤, 스레드 안전). settings 의 단일 진실 소스."""
    global firestore_client
    if firestore_client is not None:
        return firestore_client if firestore_client is not False else None

    with _firestore_client_lock:
        if firestore_client is not None:
            return firestore_client if firestore_client is not False else None

        try:
            from google.cloud import firestore
            firestore_client = firestore.Client(project=GCP_PROJECT_ID)
            print(f"[Firestore] Client 생성 성공 (project={GCP_PROJECT_ID})", flush=True)
        except Exception as e:
            import traceback
            print(f"[Firestore 오류] 클라이언트 생성 실패: {e}", flush=True)
            print(f"[Firestore 오류] 상세: {traceback.format_exc()}", flush=True)
            firestore_client = False
    return firestore_client if firestore_client != False else None


# ───────────────────── 저장소: Firestore ─────────────────────

def _fs_load_all_settings():
    """Firestore 의 guilds / users / global 3컬렉션을 읽어 레거시 dict 형태로 조립."""
    fs = get_firestore_client()
    if not fs:
        return None

    try:
        guilds = {}
        for doc in fs.collection('guilds').stream():
            guilds[doc.id] = doc.to_dict() or {}

        users = {}
        for doc in fs.collection('users').stream():
            users[doc.id] = doc.to_dict() or {}

        global_doc = fs.collection('global').document('settings').get()
        global_settings = global_doc.to_dict() if global_doc.exists else {}

        return {
            'guilds': guilds,
            'users': users,
            'global': global_settings,
        }
    except Exception as e:
        print(f"[Firestore 경고] 전체 로드 실패: {e}", flush=True)
        return None


def _fs_save_all_settings(settings):
    """레거시 dict 를 3컬렉션으로 분산 저장. batch 로 부분 atomicity 보장."""
    fs = get_firestore_client()
    if not fs:
        return False

    try:
        guilds = settings.get('guilds', {}) or {}
        users = settings.get('users', {}) or {}
        global_settings = settings.get('global', {}) or {}

        # Firestore batch 한 번에 500 op 제한 → chunk 단위로 split
        all_ops = []
        for gid, gdata in guilds.items():
            if isinstance(gdata, dict):
                all_ops.append(('guilds', str(gid), gdata))
        for uid, udata in users.items():
            if isinstance(udata, dict):
                all_ops.append(('users', str(uid), udata))
        if global_settings:
            all_ops.append(('global', 'settings', global_settings))

        # 500 op 단위 batch 분할 (set with merge)
        for i in range(0, len(all_ops), 450):
            batch = fs.batch()
            for collection, doc_id, data in all_ops[i:i+450]:
                ref = fs.collection(collection).document(doc_id)
                batch.set(ref, data, merge=False)  # 전체 dict 저장 = 레거시 호환
            batch.commit()

        return True
    except Exception as e:
        print(f"[Firestore 경고] 전체 저장 실패: {e}", flush=True)
        return False


def _fs_get_guild(guild_id):
    """Firestore 에서 단일 길드 문서 읽기."""
    fs = get_firestore_client()
    if not fs:
        return None
    try:
        doc = fs.collection('guilds').document(str(guild_id)).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"[Firestore 경고] guild {guild_id} 로드 실패: {e}", flush=True)
        return None


def _fs_set_guild(guild_id, data, merge=True):
    """Firestore 에 단일 길드 문서 atomic 쓰기."""
    fs = get_firestore_client()
    if not fs:
        return False
    try:
        fs.collection('guilds').document(str(guild_id)).set(data, merge=merge)
        return True
    except Exception as e:
        print(f"[Firestore 경고] guild {guild_id} 저장 실패: {e}", flush=True)
        return False


def _fs_update_guild(guild_id, fields):
    """Firestore 단일 길드 문서 필드 업데이트 (atomic)."""
    fs = get_firestore_client()
    if not fs:
        return False
    try:
        fs.collection('guilds').document(str(guild_id)).set(fields, merge=True)
        return True
    except Exception as e:
        print(f"[Firestore 경고] guild {guild_id} 업데이트 실패: {e}", flush=True)
        return False


def _fs_delete_guild(guild_id):
    """Firestore 단일 길드 문서 삭제."""
    fs = get_firestore_client()
    if not fs:
        return False
    try:
        fs.collection('guilds').document(str(guild_id)).delete()
        return True
    except Exception as e:
        print(f"[Firestore 경고] guild {guild_id} 삭제 실패: {e}", flush=True)
        return False


def _fs_get_user(user_id):
    """Firestore 에서 단일 사용자 문서 읽기."""
    fs = get_firestore_client()
    if not fs:
        return None
    try:
        doc = fs.collection('users').document(str(user_id)).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"[Firestore 경고] user {user_id} 로드 실패: {e}", flush=True)
        return None


def _fs_update_user(user_id, fields):
    """Firestore 단일 사용자 문서 필드 업데이트 (atomic)."""
    fs = get_firestore_client()
    if not fs:
        return False
    try:
        fs.collection('users').document(str(user_id)).set(fields, merge=True)
        return True
    except Exception as e:
        print(f"[Firestore 경고] user {user_id} 업데이트 실패: {e}", flush=True)
        return False


def _fs_get_global():
    """Firestore global/settings 문서 읽기."""
    fs = get_firestore_client()
    if not fs:
        return None
    try:
        doc = fs.collection('global').document('settings').get()
        return doc.to_dict() if doc.exists else {}
    except Exception as e:
        print(f"[Firestore 경고] global 로드 실패: {e}", flush=True)
        return None


def _fs_update_global(fields):
    """Firestore global/settings 문서 필드 업데이트 (atomic)."""
    fs = get_firestore_client()
    if not fs:
        return False
    try:
        fs.collection('global').document('settings').set(fields, merge=True)
        return True
    except Exception as e:
        print(f"[Firestore 경고] global 업데이트 실패: {e}", flush=True)
        return False


# ───────────────────── Snapshot Listener (실시간 캐시 동기화) ─────────────────────
# 봇 시작 시 1회 init → 3 collection on_snapshot 등록 → 변경 시 자동 cache 갱신
# load_settings() 는 cache 만 반환, Firestore read 0회
# 변경 비용: 변경된 doc 만 청구 (전체 172 docs 매번 X)

def _on_guilds_snapshot(col_snapshot, changes, read_time):
    global settings_cache
    with _cache_lock:
        if settings_cache is None:
            settings_cache = {'guilds': {}, 'users': {}, 'global': {}}
        guilds = settings_cache.setdefault('guilds', {})
        for change in changes:
            doc_id = change.document.id
            if change.type.name == 'REMOVED':
                guilds.pop(doc_id, None)
            else:  # ADDED, MODIFIED
                guilds[doc_id] = change.document.to_dict() or {}
    _first_snapshot_event.set()


def _on_users_snapshot(col_snapshot, changes, read_time):
    global settings_cache
    with _cache_lock:
        if settings_cache is None:
            settings_cache = {'guilds': {}, 'users': {}, 'global': {}}
        users = settings_cache.setdefault('users', {})
        for change in changes:
            doc_id = change.document.id
            if change.type.name == 'REMOVED':
                users.pop(doc_id, None)
            else:
                users[doc_id] = change.document.to_dict() or {}


def _on_global_snapshot(doc_snapshot, changes, read_time):
    global settings_cache
    with _cache_lock:
        if settings_cache is None:
            settings_cache = {'guilds': {}, 'users': {}, 'global': {}}
        # global 은 단일 doc → snapshot list 에 1개만 옴
        for snap in doc_snapshot:
            if snap.exists:
                settings_cache['global'] = snap.to_dict() or {}
            else:
                settings_cache['global'] = {}


def init_settings_listeners(wait_first_snapshot_seconds=5):
    """3 collection 에 on_snapshot listener 등록.

    봇 startup 시 1회 호출. 호출 후 load_settings() 는 cache 만 참조 (Firestore read 0).
    변경은 Firestore SDK 가 push 로 받아서 callback 에서 cache 갱신.

    Returns:
        True = listener 등록 성공, False = 실패 (기존 lazy-load 동작 유지)
    """
    global _listeners_active, _listener_watches

    if _listeners_active:
        return True

    fs = get_firestore_client()
    if not fs:
        print("[Firestore listener] 클라이언트 없음 → 기존 lazy-load 모드 유지", flush=True)
        return False

    try:
        # 첫 snapshot 이 받기 전엔 cache 가 비어있음 → 명시적 초기화
        global settings_cache
        with _cache_lock:
            if settings_cache is None:
                settings_cache = {'guilds': {}, 'users': {}, 'global': {}}

        watches = [
            fs.collection('guilds').on_snapshot(_on_guilds_snapshot),
            fs.collection('users').on_snapshot(_on_users_snapshot),
            fs.collection('global').on_snapshot(_on_global_snapshot),
        ]
        _listener_watches = watches
        _listeners_active = True

        # 첫 snapshot 받을 때까지 짧게 대기 (ADDED 폭발로 cache 채워짐)
        if _first_snapshot_event.wait(timeout=wait_first_snapshot_seconds):
            with _cache_lock:
                gc = len(settings_cache.get('guilds', {}))
                uc = len(settings_cache.get('users', {}))
            print(f"[Firestore listener] 등록 완료, 첫 snapshot OK (guilds={gc}, users={uc})", flush=True)
        else:
            print(f"[Firestore listener] 등록됐지만 첫 snapshot 대기 timeout ({wait_first_snapshot_seconds}s)", flush=True)

        return True
    except Exception as e:
        import traceback
        print(f"[Firestore listener] 등록 실패: {e}", flush=True)
        print(f"[Firestore listener] 상세: {traceback.format_exc()}", flush=True)
        _listeners_active = False
        return False


def shutdown_settings_listeners():
    """봇 종료 시 listener unsubscribe (선택사항, 프로세스 종료로도 정리됨)."""
    global _listeners_active, _listener_watches
    for watch in _listener_watches:
        try:
            watch.unsubscribe()
        except Exception:
            pass
    _listener_watches = []
    _listeners_active = False


# ───────────────────── 저장소: GCS (레거시 fallback) ─────────────────────

def _gcs_load_settings():
    """레거시 fallback. GCS settings.json 로드."""
    client = get_gcs_client()
    if not client:
        return None
    try:
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_KEY)
        return json.loads(blob.download_as_text())
    except Exception as e:
        print(f"[GCS 경고] 레거시 로드 실패: {e}", flush=True)
        return None


def _gcs_save_settings(settings):
    """레거시 GCS 저장. dual-write 모드 또는 안전망 용."""
    client = get_gcs_client()
    if not client:
        return False
    try:
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_KEY)
        blob.upload_from_string(
            json.dumps(settings, indent=2, ensure_ascii=False),
            content_type='application/json',
        )
        return True
    except Exception as e:
        print(f"[GCS 경고] 레거시 저장 실패: {e}", flush=True)
        return False


# ───────────────────── 공개 API: 레거시 시그니처 유지 ─────────────────────

def load_settings(force_reload=False):
    """설정을 로드합니다.

    저장소 우선순위:
    1. Firestore (단일 진실 소스, 2026-04-27 이관)
    2. GCS settings.json (fallback, Firestore 실패 시)
    3. 로컬 backups/settings_backup.json (최후 fallback)

    listener 활성 시 force_reload 는 무시됨 (snapshot 으로 자동 동기화).
    """
    global settings_cache

    # listener 활성: cache 가 항상 최신 (snapshot 으로 push) → force_reload 무의미
    if _listeners_active:
        with _cache_lock:
            if settings_cache is not None:
                return settings_cache.copy()

    # 캐시 (단일 프로세스 내 마이크로 버스트 방지)
    if not force_reload and settings_cache is not None:
        return settings_cache.copy()

    # 1순위: Firestore
    if SETTINGS_BACKEND in ('firestore', 'dual'):
        fs_settings = _fs_load_all_settings()
        if fs_settings is not None:
            # guilds 키 보장
            if 'guilds' not in fs_settings:
                fs_settings['guilds'] = {}
            settings_cache = fs_settings.copy()
            return fs_settings

    # 2순위: GCS (레거시)
    gcs_settings = _gcs_load_settings()
    if gcs_settings is not None:
        if 'guilds' not in gcs_settings:
            gcs_settings['guilds'] = {}
        settings_cache = gcs_settings.copy()
        if SETTINGS_BACKEND == 'firestore':
            print(f"[경고] Firestore 실패 → GCS fallback 으로 로드", flush=True)
        return gcs_settings

    # 3순위: 로컬 백업
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        backup_file = os.path.join(project_root, 'backups', 'settings_backup.json')
        if os.path.exists(backup_file):
            with open(backup_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            if 'guilds' not in settings:
                settings['guilds'] = {}
            settings_cache = settings.copy()
            print(f"[로컬] 설정 로드 완료 (Firestore + GCS 실패 - 로컬 백업 사용)", flush=True)
            return settings
    except Exception as e:
        print(f"[경고] 로컬 백업 로드 실패: {e}", flush=True)

    # 모두 실패 시 기본 구조
    print(f"[기본값] 새로운 설정 생성", flush=True)
    default_settings = {"guilds": {}, "users": {}, "global": {"LAST_CHECKED_VIDEO_ID": None}}
    settings_cache = default_settings.copy()
    return default_settings


def save_local_backup(settings):
    """로컬에 settings 백업을 저장합니다 (재해 복구용)."""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        backup_dir = os.path.join(project_root, 'backups')
        backup_file = os.path.join(backup_dir, 'settings_backup.json')
        os.makedirs(backup_dir, exist_ok=True)
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[경고] 로컬 백업 저장 실패: {e}", flush=True)
        return False


def save_settings(settings, silent=False):
    """설정을 저장합니다.

    SETTINGS_BACKEND 에 따라 동작:
    - 'firestore' (기본): Firestore 만 저장 + 로컬 백업
    - 'dual': Firestore + GCS 둘 다 저장 (마이그레이션 안전 모드)
    - 'gcs': 레거시 GCS 만 (롤백용)

    레거시 시그니처 유지 — 기존 호출처 코드 변경 불필요.
    내부적으로 3 컬렉션 batch write 로 분산.
    """
    global settings_cache
    # listener 활성 시: write → snapshot callback 이 자동으로 cache 갱신 (read 1회)
    # listener 비활성 시: 기존처럼 무효화 (다음 load_settings 가 재로딩)
    if not _listeners_active:
        settings_cache = None

    primary_success = False

    if SETTINGS_BACKEND in ('firestore', 'dual'):
        primary_success = _fs_save_all_settings(settings)
        if primary_success and not silent:
            print(f"[Firestore] 설정 저장 완료", flush=True)
        elif not primary_success and not silent:
            print(f"[경고] Firestore 설정 저장 실패", flush=True)

    if SETTINGS_BACKEND in ('dual', 'gcs'):
        gcs_ok = _gcs_save_settings(settings)
        if SETTINGS_BACKEND == 'gcs':
            primary_success = gcs_ok
        if gcs_ok and not silent:
            print(f"[GCS] 설정 저장 완료 (mode={SETTINGS_BACKEND})", flush=True)

    # 로컬 백업 (항상)
    save_local_backup(settings)

    return primary_success


def get_guild_settings(guild_id):
    """특정 서버(guild)의 설정을 가져옵니다 (atomic 단일 문서 읽기)."""
    if SETTINGS_BACKEND in ('firestore', 'dual'):
        guild_data = _fs_get_guild(guild_id)
        if guild_data is not None:
            return guild_data
    # fallback
    settings = load_settings()
    return settings.get("guilds", {}).get(str(guild_id), {
        "ANNOUNCEMENT_CHANNEL_ID": None,
        "CHAT_CHANNEL_ID": None
    })


def save_guild_settings(guild_id, announcement_id=None, chat_id=None, guild_name=None,
                        announcement_channel_name=None, chat_channel_name=None, silent=False):
    """특정 서버(guild)의 설정을 저장합니다 (atomic 단일 문서 업데이트 → drift kill).

    Args:
        silent: True면 로그 출력 안 함 (대량 저장 시)
    """
    global settings_cache
    if not _listeners_active:
        settings_cache = None

    fields = {}
    if guild_name is not None:
        fields["GUILD_NAME"] = guild_name
    if announcement_id is not None:
        fields["ANNOUNCEMENT_CHANNEL_ID"] = announcement_id
        if announcement_channel_name is not None:
            fields["ANNOUNCEMENT_CHANNEL_NAME"] = announcement_channel_name
    if chat_id is not None:
        fields["CHAT_CHANNEL_ID"] = chat_id
        if chat_channel_name is not None:
            fields["CHAT_CHANNEL_NAME"] = chat_channel_name

    if not fields:
        return True

    if SETTINGS_BACKEND in ('firestore', 'dual'):
        ok = _fs_update_guild(guild_id, fields)
        if not silent:
            if ok:
                print(f"[Firestore] guild {guild_id} 업데이트", flush=True)
            else:
                print(f"[경고] Firestore guild {guild_id} 업데이트 실패", flush=True)
        if SETTINGS_BACKEND == 'firestore':
            return ok

    # dual / gcs 모드: GCS 도 업데이트 (전체 settings 통째로)
    settings = load_settings(force_reload=True)
    guild_id_str = str(guild_id)
    if guild_id_str not in settings.get("guilds", {}):
        settings.setdefault("guilds", {})[guild_id_str] = {}
    settings["guilds"][guild_id_str].update(fields)
    return save_settings(settings, silent=silent)


# ─────── 솔로봇 채널 지정 (debi/marlene 각자 응답할 채널 목록) ───────

def get_solo_chat_channels(guild_id, identity: str) -> list[int]:
    """특정 identity('debi'/'marlene')의 자율 응답 채널 ID 목록 반환."""
    gs = get_guild_settings(guild_id)
    raw = (gs.get("solo_chat_channels") or {}).get(identity, []) or []
    result = []
    for v in raw:
        try:
            result.append(int(v))
        except (TypeError, ValueError):
            continue
    return result


def set_solo_chat_channels(guild_id, identity: str, channel_ids: list[int]) -> bool:
    """특정 identity의 자율 응답 채널 목록을 저장 (atomic 단일 문서 업데이트)."""
    if identity not in ("debi", "marlene"):
        raise ValueError(f"identity는 'debi'/'marlene'만 허용: {identity}")

    global settings_cache
    if not _listeners_active:
        settings_cache = None

    if SETTINGS_BACKEND in ('firestore', 'dual'):
        # 기존 solo_chat_channels 가져와서 머지 (다른 identity 보존)
        existing = _fs_get_guild(guild_id) or {}
        solo = dict(existing.get("solo_chat_channels", {}) or {})
        solo[identity] = [int(c) for c in (channel_ids or [])]
        ok = _fs_update_guild(guild_id, {"solo_chat_channels": solo})
        if SETTINGS_BACKEND == 'firestore':
            return ok

    # dual / gcs 모드
    settings = load_settings(force_reload=True)
    guild_id_str = str(guild_id)
    if guild_id_str not in settings.get("guilds", {}):
        settings.setdefault("guilds", {})[guild_id_str] = {}
    guild_cfg = settings["guilds"][guild_id_str]
    solo_cfg = guild_cfg.setdefault("solo_chat_channels", {})
    solo_cfg[identity] = [int(c) for c in (channel_ids or [])]
    return save_settings(settings)


def remove_guild_settings(guild_id):
    """특정 서버(guild)에 삭제됨 표시를 추가합니다 (atomic)."""
    global settings_cache
    if not _listeners_active:
        settings_cache = None

    from datetime import datetime
    fields = {
        "STATUS": "삭제됨",
        "REMOVED_AT": datetime.now().isoformat(),
    }

    if SETTINGS_BACKEND in ('firestore', 'dual'):
        # 길드 문서가 있을 때만 마킹 (없으면 skip)
        existing = _fs_get_guild(guild_id)
        if existing is not None:
            ok = _fs_update_guild(guild_id, fields)
            if SETTINGS_BACKEND == 'firestore':
                return ok
        else:
            if SETTINGS_BACKEND == 'firestore':
                return True  # 이미 없는 경우 성공

    # dual / gcs
    settings = load_settings(force_reload=True)
    guild_id_str = str(guild_id)
    if guild_id_str in settings.get("guilds", {}):
        settings["guilds"][guild_id_str].update(fields)
        return save_settings(settings)
    return True


# ─────── 전역 설정 ───────

def get_global_setting(key):
    """전역 설정을 가져옵니다 (atomic 단일 필드 읽기)."""
    if SETTINGS_BACKEND in ('firestore', 'dual'):
        global_data = _fs_get_global()
        if global_data is not None:
            return global_data.get(key)
    settings = load_settings()
    return settings.get("global", {}).get(key)


def save_global_setting(key, value):
    """전역 설정을 저장합니다 (atomic 단일 필드 업데이트)."""
    global settings_cache
    if not _listeners_active:
        settings_cache = None

    if SETTINGS_BACKEND in ('firestore', 'dual'):
        ok = _fs_update_global({key: value})
        if SETTINGS_BACKEND == 'firestore':
            return ok

    # dual / gcs
    settings = load_settings(force_reload=True)
    if "global" not in settings:
        settings["global"] = {}
    settings["global"][key] = value
    return save_settings(settings)


def save_last_video_info(video_id, video_title=None):
    """마지막 체크된 비디오 정보를 저장합니다 (atomic)."""
    global settings_cache
    if not _listeners_active:
        settings_cache = None

    fields = {"LAST_CHECKED_VIDEO_ID": video_id}
    if video_title:
        fields["LAST_CHECKED_VIDEO_TITLE"] = video_title

    if SETTINGS_BACKEND in ('firestore', 'dual'):
        ok = _fs_update_global(fields)
        if SETTINGS_BACKEND == 'firestore':
            return ok

    settings = load_settings(force_reload=True)
    if "global" not in settings:
        settings["global"] = {}
    settings["global"].update(fields)
    return save_settings(settings)


# ─────── 사용자 설정 / 유튜브 구독 ───────

def get_youtube_subscribers():
    """유튜브 DM 알림을 구독한 모든 사용자 ID 목록을 반환합니다."""
    if SETTINGS_BACKEND in ('firestore', 'dual'):
        fs = get_firestore_client()
        if fs:
            try:
                subscribers = []
                query = fs.collection('users').where(filter=__import__('google.cloud.firestore_v1.base_query', fromlist=['FieldFilter']).FieldFilter('youtube_subscribed', '==', True))
                for doc in query.stream():
                    try:
                        subscribers.append(int(doc.id))
                    except (TypeError, ValueError):
                        continue
                return subscribers
            except Exception as e:
                print(f"[Firestore 경고] subscribers 쿼리 실패: {e}", flush=True)
    # fallback
    settings = load_settings()
    subscribers = []
    for user_id, user_settings in settings.get("users", {}).items():
        if user_settings.get("youtube_subscribed"):
            try:
                subscribers.append(int(user_id))
            except (TypeError, ValueError):
                continue
    return subscribers


def log_user_interaction(user_id, user_name=None):
    """사용자가 봇과 상호작용했을 때 기록합니다 (atomic)."""
    global settings_cache
    if not _listeners_active:
        settings_cache = None

    from datetime import datetime
    fields = {
        "last_interaction": datetime.now().isoformat(),
    }
    if user_name:
        fields["user_name"] = user_name

    if SETTINGS_BACKEND in ('firestore', 'dual'):
        # interaction_count 증가는 read-modify-write — 짧은 윈도우에 race 가능. 일단 단순 처리.
        existing = _fs_get_user(user_id) or {}
        fields["interaction_count"] = existing.get("interaction_count", 0) + 1
        ok = _fs_update_user(user_id, fields)
        if SETTINGS_BACKEND == 'firestore':
            return ok

    settings = load_settings(force_reload=True)
    if "users" not in settings:
        settings["users"] = {}
    user_id_str = str(user_id)
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}
    settings["users"][user_id_str]["last_interaction"] = datetime.now().isoformat()
    settings["users"][user_id_str]["interaction_count"] = settings["users"][user_id_str].get("interaction_count", 0) + 1
    if user_name:
        settings["users"][user_id_str]["user_name"] = user_name
    save_settings(settings)


def get_interaction_users():
    """실제 DM을 보낸 사용자 ID 목록을 반환합니다."""
    if SETTINGS_BACKEND in ('firestore', 'dual'):
        fs = get_firestore_client()
        if fs:
            try:
                users = []
                # interaction_count > 0 쿼리
                from google.cloud.firestore_v1.base_query import FieldFilter
                query = fs.collection('users').where(filter=FieldFilter('interaction_count', '>', 0))
                for doc in query.stream():
                    try:
                        users.append(int(doc.id))
                    except (TypeError, ValueError):
                        continue
                return users
            except Exception as e:
                print(f"[Firestore 경고] interaction_users 쿼리 실패: {e}", flush=True)
    # fallback
    settings = load_settings()
    interaction_users = []
    for user_id, user_settings in settings.get("users", {}).items():
        if user_settings.get("interaction_count", 0) > 0:
            try:
                interaction_users.append(int(user_id))
            except (TypeError, ValueError):
                continue
    return interaction_users


def get_all_users():
    """모든 등록된 사용자 정보를 반환합니다."""
    settings = load_settings()
    users = []
    for user_id, user_settings in settings.get("users", {}).items():
        try:
            uid_int = int(user_id)
        except (TypeError, ValueError):
            continue
        users.append({
            'id': uid_int,
            'youtube_subscribed': user_settings.get("youtube_subscribed", False),
            'first_interaction': user_settings.get("first_interaction"),
            'last_seen': user_settings.get("last_seen"),
            'server_admin': user_settings.get("server_admin", False)
        })
    return users


def add_user_interaction(user_id, interaction_type="general"):
    """사용자 상호작용을 기록합니다 (atomic, DM 외 용도 - interaction_count 증가 안 함)."""
    global settings_cache
    if not _listeners_active:
        settings_cache = None

    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if SETTINGS_BACKEND in ('firestore', 'dual'):
        existing = _fs_get_user(user_id) or {}
        fields = {
            "last_seen": now,
            "interaction_type": interaction_type,
        }
        if "first_interaction" not in existing:
            fields["first_interaction"] = now
        ok = _fs_update_user(user_id, fields)
        if SETTINGS_BACKEND == 'firestore':
            return ok

    settings = load_settings(force_reload=True)
    if "users" not in settings:
        settings["users"] = {}
    user_id_str = str(user_id)
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}
    if "first_interaction" not in settings["users"][user_id_str]:
        settings["users"][user_id_str]["first_interaction"] = now
    settings["users"][user_id_str]["last_seen"] = now
    settings["users"][user_id_str]["interaction_type"] = interaction_type
    return save_settings(settings)


def set_youtube_subscription(user_id, subscribe: bool, user_name=None):
    """사용자의 유튜브 DM 알림 구독 상태를 설정합니다 (atomic — drift kill)."""
    global settings_cache
    if not _listeners_active:
        settings_cache = None

    fields = {"youtube_subscribed": subscribe}
    if user_name:
        fields["user_name"] = user_name

    if SETTINGS_BACKEND in ('firestore', 'dual'):
        ok = _fs_update_user(user_id, fields)
        if SETTINGS_BACKEND == 'firestore':
            return ok

    settings = load_settings(force_reload=True)
    if "users" not in settings:
        settings["users"] = {}
    user_id_str = str(user_id)
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}
    settings["users"][user_id_str]["youtube_subscribed"] = subscribe
    if user_name:
        settings["users"][user_id_str]["user_name"] = user_name
    return save_settings(settings)


def is_youtube_subscribed(user_id) -> bool:
    """사용자의 유튜브 DM 알림 구독 상태를 확인합니다 (atomic 단일 필드 읽기)."""
    if SETTINGS_BACKEND in ('firestore', 'dual'):
        user_data = _fs_get_user(user_id)
        if user_data is not None:
            return bool(user_data.get("youtube_subscribed", False))
    settings = load_settings()
    user_id_str = str(user_id)
    return settings.get("users", {}).get(user_id_str, {}).get("youtube_subscribed", False)


# ─────── 서버 관리자 ───────

def get_server_admins(guild_id=None):
    """서버 관리자 목록을 반환합니다. guild_id가 주어지면 해당 서버의 관리자만 반환."""
    settings = load_settings()
    admins = []
    if guild_id:
        guild_str = str(guild_id)
        for user_id, user_settings in settings.get("users", {}).items():
            if user_settings.get("admin_servers", {}).get(guild_str):
                try:
                    admins.append(int(user_id))
                except (TypeError, ValueError):
                    continue
    else:
        for user_id, user_settings in settings.get("users", {}).items():
            if user_settings.get("admin_servers"):
                try:
                    admins.append({
                        'user_id': int(user_id),
                        'admin_servers': list(user_settings.get("admin_servers", {}).keys())
                    })
                except (TypeError, ValueError):
                    continue
    return admins


def set_server_admin(user_id, guild_id, is_admin=True):
    """사용자를 특정 서버의 관리자로 설정하거나 해제합니다 (atomic)."""
    global settings_cache
    if not _listeners_active:
        settings_cache = None

    guild_str = str(guild_id)

    if SETTINGS_BACKEND in ('firestore', 'dual'):
        existing = _fs_get_user(user_id) or {}
        admin_servers = dict(existing.get("admin_servers", {}) or {})
        admin_servers[guild_str] = is_admin
        ok = _fs_update_user(user_id, {"admin_servers": admin_servers})
        if SETTINGS_BACKEND == 'firestore':
            return ok

    user_id_str = str(user_id)
    settings = load_settings(force_reload=True)
    if "users" not in settings:
        settings["users"] = {}
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}
    if "admin_servers" not in settings["users"][user_id_str]:
        settings["users"][user_id_str]["admin_servers"] = {}
    settings["users"][user_id_str]["admin_servers"][guild_str] = is_admin
    return save_settings(settings)


# ─────── DM 채널 ───────

def save_user_dm_interaction(user_id, channel_id, user_name=None):
    """DM을 보낸 사용자의 정보를 저장합니다 (atomic — drift kill).

    Args:
        user_id: 사용자 Discord ID
        channel_id: DM 채널 ID
        user_name: 사용자 이름 (선택)

    저장 내용:
        - DM 채널 정보
        - interaction count (DM 횟수, 증가)
        - 마지막 상호작용 시간
        - 사용자 이름
    """
    global settings_cache
    if not _listeners_active:
        settings_cache = None

    from datetime import datetime
    now = datetime.now().isoformat()

    if SETTINGS_BACKEND in ('firestore', 'dual'):
        existing = _fs_get_user(user_id) or {}
        fields = {
            "dm_channel_id": str(channel_id),
            "last_dm": now,
            "last_interaction": now,
            "interaction_count": existing.get("interaction_count", 0) + 1,
        }
        if user_name:
            fields["user_name"] = user_name
        ok = _fs_update_user(user_id, fields)
        if SETTINGS_BACKEND == 'firestore':
            return ok

    user_id_str = str(user_id)
    settings = load_settings(force_reload=True)
    if "users" not in settings:
        settings["users"] = {}
    if user_id_str not in settings["users"]:
        settings["users"][user_id_str] = {}
    user_data = settings["users"][user_id_str]
    user_data["dm_channel_id"] = str(channel_id)
    if user_name:
        user_data["user_name"] = user_name
    user_data["last_dm"] = now
    user_data["last_interaction"] = now
    user_data["interaction_count"] = user_data.get("interaction_count", 0) + 1
    return save_settings(settings, silent=True)


def save_dm_channel(user_id, channel_id, user_name=None):
    """[DEPRECATED] save_user_dm_interaction 사용 권장. 호환성 유지."""
    return save_user_dm_interaction(user_id, channel_id, user_name)


# ─────── 명령어 로그 (Firestore command_logs 컬렉션) ───────
# expireAt 필드 + Firestore TTL 정책으로 30일 후 자동 삭제
# (TTL 정책 설정: gcloud firestore fields ttls update expireAt --collection-group=command_logs)

COMMAND_LOGS_COLLECTION = 'command_logs'
COMMAND_LOGS_TTL_DAYS = 30


def save_command_log(log_entry):
    """명령어 사용 로그를 Firestore 에 저장합니다.

    Args:
        log_entry: 로그 항목 (dict). timestamp 는 ISO 형식 str. 다른 키는 그대로 저장.
    """
    from datetime import datetime, timedelta, timezone
    fs = get_firestore_client()
    if not fs:
        return False
    try:
        doc = dict(log_entry)
        doc["expireAt"] = datetime.now(timezone.utc) + timedelta(days=COMMAND_LOGS_TTL_DAYS)
        fs.collection(COMMAND_LOGS_COLLECTION).add(doc)
        return True
    except Exception as e:
        print(f"[경고] 명령어 로그 저장 실패: {e}", flush=True)
        return False


def load_command_logs(filters=None):
    """명령어 사용 로그를 Firestore 에서 로드합니다.

    Args:
        filters: 필터 딕셔너리 (optional)
            - guild_id, user_id, command_name (str equality)
            - start_date, end_date (ISO 형식 str, timestamp 비교)
            - limit (int, 기본 1000)

    Returns:
        list: 필터링된 로그 항목 리스트 (timestamp desc)
    """
    fs = get_firestore_client()
    if not fs:
        return []
    try:
        query = fs.collection(COMMAND_LOGS_COLLECTION)
        filters = filters or {}
        if filters.get("guild_id"):
            query = query.where("guild_id", "==", str(filters["guild_id"]))
        if filters.get("user_id"):
            query = query.where("user_id", "==", str(filters["user_id"]))
        if filters.get("command_name"):
            query = query.where("command_name", "==", filters["command_name"])
        if filters.get("start_date"):
            query = query.where("timestamp", ">=", filters["start_date"])
        if filters.get("end_date"):
            query = query.where("timestamp", "<=", filters["end_date"])

        from google.cloud.firestore_v1 import Query as FsQuery
        query = query.order_by("timestamp", direction=FsQuery.DESCENDING)
        query = query.limit(int(filters.get("limit") or 1000))

        return [d.to_dict() for d in query.stream()]
    except Exception as e:
        print(f"[경고] 명령어 로그 로드 실패: {e}", flush=True)
        return []

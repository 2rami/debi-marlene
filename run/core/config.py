import os
import json
import time
import threading
from dotenv import load_dotenv

from run.core import store

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

# GCP 설정 — GCS(환영 이미지·settings.json 레거시) 전용. 문서 저장은 로컬 SQLite 로 옮겼다.
# 명시적 default — gcloud config 의존 없이 안정적으로 동작
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'ironic-objectivist-465713-a6')
GCS_BUCKET = os.getenv('GCS_BUCKET_NAME', 'debi-marlene-settings')
GCS_KEY = 'settings.json'  # 레거시 fallback 전용

# 저장소 모드
# - 'local': 맥미니 SQLite 단독 (기본, run/core/store.py)
# - 'dual': SQLite + GCS 둘 다 쓰기
# - 'gcs': 레거시 (롤백용)
SETTINGS_BACKEND = os.getenv('SETTINGS_BACKEND', 'local').lower()

# 클라이언트 싱글톤
gcs_client = None
_gcs_client_lock = threading.Lock()

# 레거시(GCS·로컬 백업) 경로로 읽었을 때만 쓰는 캐시. 로컬 저장소는 Mirror 가 맡는다.
settings_cache = None

# 봇은 메시지마다 서버 설정을 읽는다 — 다른 프로세스(대시보드·웹패널)가 바꾼 문서만 골라
# 다시 읽는 캐시라 매번 불러도 싸고, 바뀐 설정도 바로 보인다.
_settings_mirror = store.Mirror(('guilds', 'users', 'global'))


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


def get_db():
    """문서 저장소 (Firestore 와 같은 모양의 로컬 SQLite). 실패하면 None 대신 예외가 난다."""
    return store.client()


# ───────────────────── 저장소: 로컬 SQLite ─────────────────────

def _local_load_settings():
    """guilds / users / global 3컬렉션을 레거시 dict 형태로 조립."""
    with _settings_mirror.lock:
        _settings_mirror.sync()
        docs = _settings_mirror.docs
        return {
            'guilds': dict(docs['guilds']),
            'users': dict(docs['users']),
            'global': dict(docs['global'].get('settings') or {}),
        }


def _local_save_settings(settings):
    """레거시 dict 를 guilds/users 문서로 나눠 한 트랜잭션에 저장. 내용이 그대로인 문서는
    put_raw 가 건너뛴다 — 5분 통계 저장이 수백 문서를 통째로 다시 쓰지 않게.

    global/settings 문서는 여기서 저장하지 않는다 — SENT_VIDEO_IDS·coupons·
    last_patchnote_id 같은 누적 상태가 한 문서에 공존하는데, 전체저장이
    stale 캐시로 통째 덮으면 방금 claim/저장한 값이 롤백된다(유튜브 같은 영상 재전송의
    근본 원인). global 필드는 save_global_setting / claim_video_id 트랜잭션 등
    단일 필드 merge 경로로만 저장한다.
    """
    try:
        rows = []
        for col in ('guilds', 'users'):
            for doc_id, data in (settings.get(col, {}) or {}).items():
                if isinstance(data, dict):
                    rows.append((col, str(doc_id), store.encode(data)))
        with store.write_txn() as c:
            for col, doc_id, raw in rows:
                store.put_raw(c, col, doc_id, raw)
        return True
    except Exception as e:
        print(f"[저장소 경고] 전체 저장 실패: {e}", flush=True)
        return False


def _doc(col, doc_id):
    return store.client().collection(col).document(str(doc_id))


def _get_doc(col, doc_id):
    """단일 문서 읽기. 없으면 None, 실패해도 None."""
    try:
        snap = _doc(col, doc_id).get()
        return snap.to_dict() if snap.exists else None
    except Exception as e:
        print(f"[저장소 경고] {col}/{doc_id} 로드 실패: {e}", flush=True)
        return None


def _merge_doc(col, doc_id, fields):
    """단일 문서 필드 merge (atomic). 중첩 맵은 깊게 합친다."""
    try:
        _doc(col, doc_id).set(fields, merge=True)
        return True
    except Exception as e:
        print(f"[저장소 경고] {col}/{doc_id} 업데이트 실패: {e}", flush=True)
        return False


def update_guild_fields(guild_id, fields):
    """길드 문서 필드 merge. 웹패널 좀비 길드 정리처럼 필드 몇 개만 바꿀 때."""
    return _merge_doc('guilds', guild_id, fields)


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
    1. 로컬 SQLite (단일 진실 소스, 2026-10 Firestore 에서 이관)
    2. GCS settings.json (레거시 fallback, 1 실패 시)
    3. 로컬 backups/settings_backup.json (최후 fallback)

    1은 다른 프로세스가 바꾼 문서만 골라 다시 읽는 캐시라 늘 최신이다 — force_reload 는
    레거시 경로에만 의미가 있다.
    """
    global settings_cache

    if SETTINGS_BACKEND in ('local', 'dual'):
        try:
            return _local_load_settings()
        except Exception as e:
            print(f"[저장소 경고] 설정 로드 실패: {e}", flush=True)

    # 레거시 경로 캐시 (단일 프로세스 내 마이크로 버스트 방지)
    if not force_reload and settings_cache is not None:
        return settings_cache.copy()

    # 2순위: GCS (레거시)
    gcs_settings = _gcs_load_settings()
    if gcs_settings is not None:
        if 'guilds' not in gcs_settings:
            gcs_settings['guilds'] = {}
        settings_cache = gcs_settings.copy()
        if SETTINGS_BACKEND == 'local':
            print(f"[경고] 로컬 저장소 실패 → GCS fallback 으로 로드", flush=True)
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
            print(f"[로컬] 설정 로드 완료 (저장소 + GCS 실패 - 로컬 백업 사용)", flush=True)
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
    - 'local' (기본): 로컬 SQLite 만 저장 + 로컬 백업
    - 'dual': SQLite + GCS 둘 다 저장
    - 'gcs': 레거시 GCS 만 (롤백용)

    레거시 시그니처 유지 — 기존 호출처 코드 변경 불필요.
    """
    global settings_cache
    settings_cache = None

    primary_success = False

    if SETTINGS_BACKEND in ('local', 'dual'):
        primary_success = _local_save_settings(settings)
        if primary_success and not silent:
            print(f"[저장소] 설정 저장 완료", flush=True)
        elif not primary_success and not silent:
            print(f"[경고] 저장소 설정 저장 실패", flush=True)

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
    if SETTINGS_BACKEND in ('local', 'dual'):
        guild_data = _get_doc('guilds', guild_id)
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

    if SETTINGS_BACKEND in ('local', 'dual'):
        ok = update_guild_fields(guild_id, fields)
        if not silent:
            if ok:
                print(f"[저장소] guild {guild_id} 업데이트", flush=True)
            else:
                print(f"[경고] 저장소 guild {guild_id} 업데이트 실패", flush=True)
        if SETTINGS_BACKEND == 'local':
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
    settings_cache = None

    if SETTINGS_BACKEND in ('local', 'dual'):
        # merge 가 중첩 맵을 깊게 합치므로 다른 identity 목록은 그대로 남는다
        ok = update_guild_fields(guild_id, {"solo_chat_channels": {identity: [int(c) for c in (channel_ids or [])]}})
        if SETTINGS_BACKEND == 'local':
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
    settings_cache = None

    from datetime import datetime
    fields = {
        "STATUS": "삭제됨",
        "REMOVED_AT": datetime.now().isoformat(),
    }

    if SETTINGS_BACKEND in ('local', 'dual'):
        # 길드 문서가 있을 때만 마킹 (없으면 skip)
        existing = _get_doc('guilds', guild_id)
        if existing is not None:
            ok = update_guild_fields(guild_id, fields)
            if SETTINGS_BACKEND == 'local':
                return ok
        else:
            if SETTINGS_BACKEND == 'local':
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
    if SETTINGS_BACKEND in ('local', 'dual'):
        global_data = _get_doc('global', 'settings')
        if global_data is not None:
            return global_data.get(key)
    settings = load_settings()
    return settings.get("global", {}).get(key)


def save_global_setting(key, value):
    """전역 설정을 저장합니다 (atomic 단일 필드 업데이트)."""
    global settings_cache
    settings_cache = None

    if SETTINGS_BACKEND in ('local', 'dual'):
        ok = _merge_doc('global', 'settings', {key: value})
        if SETTINGS_BACKEND == 'local':
            return ok

    # dual / gcs
    settings = load_settings(force_reload=True)
    if "global" not in settings:
        settings["global"] = {}
    settings["global"][key] = value
    return save_settings(settings)


# 전송한 video_id 집합 — 최근 N개만 유지. playlist 는 최신 10개만 보므로 충분하다.
_SENT_IDS_KEY = "SENT_VIDEO_IDS"
_SENT_IDS_MAX = 100

# 유튜브 claim 이상(트랜잭션 실패/비원자 폴백/저장 실패)을 디스코드 웹훅으로 승격한다.
# print 는 컨테이너 재시작 시 소실돼 '같은 영상 N개' 중복의 원인 추적을 놓친다.
# 웹훅은 채널에 남으므로 재전송 직전(폴백 발동) 상태를 실시간 포착한다.
_last_yt_alert = {}


def _yt_alert(key, title, desc):
    """유튜브 claim 경고를 웹훅으로 전송. 같은 종류는 5분에 1회로 쓰로틀(10분 사이클 스팸 방지)."""
    now = time.time()
    if now - _last_yt_alert.get(key, 0) < 300:
        return
    _last_yt_alert[key] = now
    try:
        from run.services.webhook_logger import send_sync
        send_sync(title, desc, color=0xE67E22)
    except Exception:
        pass


def claim_video_id(video_id, video_title=None):
    """video_id 를 '전송함' 집합(SENT_VIDEO_IDS)에 원자적으로 추가하고 신규 여부를 반환.

      - 이미 집합에 있으면 (이전 실행/다른 프로세스가 처리 완료) -> False
      - 없으면 추가하고 -> True

    LAST_CHECKED_VIDEO_ID '경계' 방식과 달리 영상 ID 자체로 멱등 판정한다.
    이터널 리턴 채널은 라이브 스트림이 playlist 순서/포함 여부를 시간에 따라
    흔드는데, 경계 방식은 경계 영상이 목록에서 사라지면 추적이 깨져 같은 영상을
    재전송했다(2026-06-22 DZ3shVz9-IA 4시간 뒤 재전송 확인). ID 집합은 흔들려도 안전.
    반환: claimed(bool)
    """
    global settings_cache
    settings_cache = None

    if SETTINGS_BACKEND in ('local', 'dual'):
        try:
            ref = _doc('global', 'settings')

            @store.transactional
            def _claim(transaction):
                snapshot = ref.get(transaction=transaction)
                data = snapshot.to_dict() if snapshot.exists else {}
                sent = data.get(_SENT_IDS_KEY) or []
                if video_id in sent:
                    return False
                sent.append(video_id)
                fields = {
                    _SENT_IDS_KEY: sent[-_SENT_IDS_MAX:],
                    "LAST_CHECKED_VIDEO_ID": video_id,
                }
                if video_title:
                    fields["LAST_CHECKED_VIDEO_TITLE"] = video_title
                transaction.set(ref, fields, merge=True)
                return True

            return _claim(get_db().transaction())
        except Exception as e:
            print(f"[저장소 경고] claim_video_id 트랜잭션 실패: {e}", flush=True)
            _yt_alert(
                "tx_fail",
                "[유튜브 경고] claim 트랜잭션 실패",
                f"원자 claim 트랜잭션이 실패해 비원자 폴백으로 전환됩니다. **중복 위험.**\n"
                f"video_id=`{video_id}`\n에러: {type(e).__name__}: {e}",
            )
            # 트랜잭션 실패 시 아래 비원자 경로로 폴백

    # gcs / 폴백: 단일 프로세스 가정의 read-then-write (원자성 보장 없음).
    # local/dual 백엔드인데 여기까지 왔다는 건 원자 claim 이 불가능한
    # degraded 상태(트랜잭션 실패 — DB 잠김·디스크 오류)라는 뜻이므로 경고를 남긴다.
    if SETTINGS_BACKEND in ('local', 'dual'):
        print(f"[유튜브 경고] claim_video_id 비원자 폴백 사용 — 원자 claim 불가, "
              f"중복 위험 상태. video_id={video_id}", flush=True)
        _yt_alert(
            "nonatomic_fallback",
            "[유튜브 경고] 비원자 폴백 claim",
            f"원자 claim 불가 → 비원자 read-then-write 폴백. **중복 위험 상태.**\n"
            f"video_id=`{video_id}`",
        )
    settings = load_settings(force_reload=True)
    sent = (settings.get("global") or {}).get(_SENT_IDS_KEY) or []
    if video_id in sent:
        return False
    sent.append(video_id)
    fields = {
        _SENT_IDS_KEY: sent[-_SENT_IDS_MAX:],
        "LAST_CHECKED_VIDEO_ID": video_id,
    }
    if video_title:
        fields["LAST_CHECKED_VIDEO_TITLE"] = video_title
    # 저장이 실제로 성공했을 때만 claim 을 인정한다. 저장 실패인데 True 를 돌려주면
    # SENT_VIDEO_IDS 에 영상이 남지 않아 다음 10분 사이클이 같은 영상을 신규로 오인해
    # 재전송한다 — '같은 영상 N개' 중복 알림의 핵심 원인. 저장 실패 시 False(=이번엔 스킵)
    # 로 fail-closed 하고, 저장소가 복구되면 다음 사이클에 정상 claim + 전송된다.
    # 누락 1회가 중복 N회보다 안전하다.
    # global 은 전체 save_settings 가 저장하지 않으므로 단일 필드 merge 로 명시 저장한다.
    if SETTINGS_BACKEND in ('local', 'dual'):
        saved = _merge_doc('global', 'settings', fields)
    else:
        settings.setdefault("global", {}).update(fields)
        saved = save_settings(settings)
    if not saved:
        print(f"[유튜브 오류] SENT_VIDEO_IDS 저장 실패 → 전송 스킵(fail-closed)으로 재전송 폭주 차단. "
              f"video_id={video_id}", flush=True)
        _yt_alert(
            "save_fail",
            "[유튜브 오류] SENT_VIDEO_IDS 저장 실패",
            f"저장 실패 → 이번 전송 스킵(fail-closed). 저장소 복구 시 다음 사이클에 정상 전송됩니다.\n"
            f"video_id=`{video_id}`",
        )
        return False
    return True


def seed_sent_video_ids(video_ids):
    """첫 실행 마이그레이션: 현재 playlist 영상들을 '전송함' 으로 등록만 한다(전송 X).

    SENT_VIDEO_IDS 가 비어있는 첫 배포 때 playlist 전체(최대 10개)를 신규로 오인해
    전 서버에 폭탄 전송하는 것을 막는다. 이미 집합이 있으면 아무것도 하지 않는다.
    반환: seeded(bool) — 실제로 시드했으면 True (이번 사이클은 전송 스킵해야 함)
    """
    existing = get_global_setting(_SENT_IDS_KEY)
    if existing:  # 이미 운영 중 — 시드 불필요
        return False
    save_global_setting(_SENT_IDS_KEY, list(video_ids)[-_SENT_IDS_MAX:])
    return True


# ─────── 사용자 설정 / 유튜브 구독 ───────

def get_youtube_subscribers():
    """유튜브 DM 알림을 구독한 모든 사용자 ID 목록을 반환합니다."""
    if SETTINGS_BACKEND in ('local', 'dual'):
        try:
            subscribers = []
            query = get_db().collection('users').where('youtube_subscribed', '==', True)
            for doc in query.stream():
                try:
                    subscribers.append(int(doc.id))
                except (TypeError, ValueError):
                    continue
            return subscribers
        except Exception as e:
            print(f"[저장소 경고] subscribers 쿼리 실패: {e}", flush=True)
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
    settings_cache = None

    from datetime import datetime
    fields = {
        "last_interaction": datetime.now().isoformat(),
    }
    if user_name:
        fields["user_name"] = user_name

    if SETTINGS_BACKEND in ('local', 'dual'):
        fields["interaction_count"] = store.Increment(1)
        ok = _merge_doc('users', user_id, fields)
        if SETTINGS_BACKEND == 'local':
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
    if SETTINGS_BACKEND in ('local', 'dual'):
        try:
            users = []
            query = get_db().collection('users').where('interaction_count', '>', 0)
            for doc in query.stream():
                try:
                    users.append(int(doc.id))
                except (TypeError, ValueError):
                    continue
            return users
        except Exception as e:
            print(f"[저장소 경고] interaction_users 쿼리 실패: {e}", flush=True)
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
    settings_cache = None

    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if SETTINGS_BACKEND in ('local', 'dual'):
        try:
            with store.write_txn():  # first_interaction 을 「없을 때만」 넣는 읽고-쓰기를 한 번에
                existing = _get_doc('users', user_id) or {}
                fields = {
                    "last_seen": now,
                    "interaction_type": interaction_type,
                }
                if "first_interaction" not in existing:
                    fields["first_interaction"] = now
                ok = _merge_doc('users', user_id, fields)
        except Exception as e:
            print(f"[저장소 경고] users/{user_id} 상호작용 기록 실패: {e}", flush=True)
            ok = False
        if SETTINGS_BACKEND == 'local':
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
    settings_cache = None

    fields = {"youtube_subscribed": subscribe}
    if user_name:
        fields["user_name"] = user_name

    if SETTINGS_BACKEND in ('local', 'dual'):
        ok = _merge_doc('users', user_id, fields)
        if SETTINGS_BACKEND == 'local':
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
    if SETTINGS_BACKEND in ('local', 'dual'):
        user_data = _get_doc('users', user_id)
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
    settings_cache = None

    guild_str = str(guild_id)

    if SETTINGS_BACKEND in ('local', 'dual'):
        # merge 가 중첩 맵을 깊게 합치므로 이 서버 키 하나만 바뀐다
        ok = _merge_doc('users', user_id, {"admin_servers": {guild_str: is_admin}})
        if SETTINGS_BACKEND == 'local':
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
    settings_cache = None

    from datetime import datetime
    now = datetime.now().isoformat()

    if SETTINGS_BACKEND in ('local', 'dual'):
        fields = {
            "dm_channel_id": str(channel_id),
            "last_dm": now,
            "last_interaction": now,
            "interaction_count": store.Increment(1),
        }
        if user_name:
            fields["user_name"] = user_name
        ok = _merge_doc('users', user_id, fields)
        if SETTINGS_BACKEND == 'local':
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


# ─────── 명령어 로그 (command_logs 컬렉션) ───────
# expireAt 이 지나면 봇의 일일 정리(store.purge_expired)가 지운다 — Firestore TTL 정책 자리.

COMMAND_LOGS_COLLECTION = 'command_logs'
COMMAND_LOGS_TTL_DAYS = 30


def save_command_log(log_entry):
    """명령어 사용 로그를 저장합니다.

    Args:
        log_entry: 로그 항목 (dict). timestamp 는 ISO 형식 str. 다른 키는 그대로 저장.
    """
    from datetime import datetime, timedelta, timezone
    try:
        doc = dict(log_entry)
        doc["expireAt"] = datetime.now(timezone.utc) + timedelta(days=COMMAND_LOGS_TTL_DAYS)
        get_db().collection(COMMAND_LOGS_COLLECTION).add(doc)
        return True
    except Exception as e:
        print(f"[경고] 명령어 로그 저장 실패: {e}", flush=True)
        return False


def load_command_logs(filters=None):
    """명령어 사용 로그를 로드합니다.

    Args:
        filters: 필터 딕셔너리 (optional)
            - guild_id, user_id, command_name (str equality)
            - start_date, end_date (ISO 형식 str, timestamp 비교)
            - limit (int, 기본 1000)

    Returns:
        list: 필터링된 로그 항목 리스트 (timestamp desc)
    """
    try:
        query = get_db().collection(COMMAND_LOGS_COLLECTION)
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

        query = query.order_by("timestamp", direction=store.Query.DESCENDING)
        query = query.limit(int(filters.get("limit") or 1000))

        return [d.to_dict() for d in query.stream()]
    except Exception as e:
        print(f"[경고] 명령어 로그 로드 실패: {e}", flush=True)
        return []

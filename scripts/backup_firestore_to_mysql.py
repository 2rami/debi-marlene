"""Firestore → MySQL 일일 백업.

운영 진실 = Firestore. 이 스크립트는 분석/리포트/장애복구를 위한 정기 백업.

사용:
    python3 scripts/backup_firestore_to_mysql.py            # 1회 실행
    python3 scripts/backup_firestore_to_mysql.py --dry-run  # 카운트만

cron 예시 (매일 새벽 4시 KST):
    0 4 * * * cd /path/to/debi-marlene && python3 scripts/backup_firestore_to_mysql.py >> backup.log 2>&1

전제:
    docker compose -f docker-compose.mysql.yml up -d  # MySQL 컨테이너 실행 중
    pip install pymysql  # MySQL 드라이버
    GOOGLE_APPLICATION_CREDENTIALS 또는 gcloud ADC 인증 완료
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import firestore

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'ironic-objectivist-465713-a6')

# MySQL 연결 정보 (docker-compose.mysql.yml 기본값)
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USER', 'backup'),
    'password': os.getenv('MYSQL_PASSWORD', 'backup_pw'),
    'database': os.getenv('MYSQL_DATABASE', 'debi_marlene_backup'),
    'charset': 'utf8mb4',
}


def _json_default(o):
    """datetime 등 JSON 기본 미지원 타입 처리."""
    if isinstance(o, datetime):
        return o.isoformat()
    return str(o)


def backup_guilds(cur, fs, snapshot_at):
    """guilds 컬렉션 → guilds_backup 테이블."""
    count = 0
    for doc in fs.collection('guilds').stream():
        d = doc.to_dict() or {}
        cur.execute("""
            INSERT INTO guilds_backup
                (guild_id, guild_name, member_count, announcement_channel_id,
                 chat_channel_id, tts_channel_id, status, snapshot_at, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                guild_name=VALUES(guild_name),
                member_count=VALUES(member_count),
                announcement_channel_id=VALUES(announcement_channel_id),
                chat_channel_id=VALUES(chat_channel_id),
                tts_channel_id=VALUES(tts_channel_id),
                status=VALUES(status),
                snapshot_at=VALUES(snapshot_at),
                raw_json=VALUES(raw_json)
        """, (
            doc.id,
            d.get('GUILD_NAME'),
            d.get('멤버수') or d.get('member_count'),
            d.get('ANNOUNCEMENT_CHANNEL_ID'),
            d.get('CHAT_CHANNEL_ID'),
            d.get('tts_channel_id'),
            d.get('STATUS') or d.get('상태'),
            snapshot_at,
            json.dumps(d, ensure_ascii=False, default=_json_default),
        ))
        count += 1
    return count


def backup_users(cur, fs, snapshot_at):
    """users 컬렉션 → users_backup 테이블."""
    count = 0
    for doc in fs.collection('users').stream():
        d = doc.to_dict() or {}
        last_interaction = d.get('last_interaction')
        last_dm = d.get('last_dm')

        # ISO 문자열 → datetime 변환 (None 안전)
        def _parse(s):
            if not s:
                return None
            if isinstance(s, datetime):
                return s
            try:
                return datetime.fromisoformat(str(s).replace('Z', '+00:00'))
            except Exception:
                return None

        cur.execute("""
            INSERT INTO users_backup
                (user_id, user_name, youtube_subscribed, dm_channel_id,
                 interaction_count, last_interaction, last_dm, snapshot_at, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                user_name=VALUES(user_name),
                youtube_subscribed=VALUES(youtube_subscribed),
                dm_channel_id=VALUES(dm_channel_id),
                interaction_count=VALUES(interaction_count),
                last_interaction=VALUES(last_interaction),
                last_dm=VALUES(last_dm),
                snapshot_at=VALUES(snapshot_at),
                raw_json=VALUES(raw_json)
        """, (
            doc.id,
            d.get('user_name'),
            bool(d.get('youtube_subscribed', False)),
            d.get('dm_channel_id'),
            int(d.get('interaction_count', 0) or 0),
            _parse(last_interaction),
            _parse(last_dm),
            snapshot_at,
            json.dumps(d, ensure_ascii=False, default=_json_default),
        ))
        count += 1
    return count


def backup_global(cur, fs, snapshot_at):
    """global/settings 문서 → global_backup 테이블 (key 단위 분해)."""
    doc = fs.collection('global').document('settings').get()
    if not doc.exists:
        return 0

    data = doc.to_dict() or {}
    count = 0
    for key, value in data.items():
        cur.execute("""
            INSERT INTO global_backup (setting_key, setting_value, snapshot_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                setting_value=VALUES(setting_value),
                snapshot_at=VALUES(snapshot_at)
        """, (
            key,
            json.dumps(value, ensure_ascii=False, default=_json_default),
            snapshot_at,
        ))
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='카운트만 (MySQL 쓰기 없음)')
    args = parser.parse_args()

    started = datetime.now()
    print(f"=== Firestore → MySQL 백업 시작 {started.isoformat()} ===")

    # Firestore 연결
    fs = firestore.Client(project=GCP_PROJECT_ID)
    print(f"[OK] Firestore 연결 (project={GCP_PROJECT_ID})")

    if args.dry_run:
        # 카운트만
        guilds = sum(1 for _ in fs.collection('guilds').stream())
        users = sum(1 for _ in fs.collection('users').stream())
        global_doc = fs.collection('global').document('settings').get()
        global_count = len(global_doc.to_dict() or {}) if global_doc.exists else 0
        print(f"[DRY-RUN] guilds={guilds}, users={users}, global_keys={global_count}")
        return 0

    # MySQL 연결
    try:
        import pymysql
    except ImportError:
        print("[ERROR] pymysql 미설치. 'pip install pymysql' 후 재실행.", file=sys.stderr)
        return 1

    try:
        conn = pymysql.connect(**MYSQL_CONFIG, autocommit=False)
    except Exception as e:
        print(f"[ERROR] MySQL 연결 실패: {e}", file=sys.stderr)
        print("docker compose -f docker-compose.mysql.yml up -d 가 실행 중인지 확인", file=sys.stderr)
        return 1
    print(f"[OK] MySQL 연결 ({MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']})")

    snapshot_at = datetime.now()
    run_id = None
    try:
        with conn.cursor() as cur:
            # 백업 시작 기록
            cur.execute("""
                INSERT INTO backup_runs (started_at, status)
                VALUES (%s, 'running')
            """, (snapshot_at,))
            run_id = cur.lastrowid
            conn.commit()

            # 각 컬렉션 백업
            print("[1/3] guilds 백업...", flush=True)
            guilds_count = backup_guilds(cur, fs, snapshot_at)
            print(f"  → {guilds_count} 문서", flush=True)

            print("[2/3] users 백업...", flush=True)
            users_count = backup_users(cur, fs, snapshot_at)
            print(f"  → {users_count} 문서", flush=True)

            print("[3/3] global 백업...", flush=True)
            global_count = backup_global(cur, fs, snapshot_at)
            print(f"  → {global_count} 키", flush=True)

            # 완료 기록
            duration = int((datetime.now() - snapshot_at).total_seconds())
            cur.execute("""
                UPDATE backup_runs
                SET completed_at=NOW(), guilds_count=%s, users_count=%s,
                    global_count=%s, duration_seconds=%s, status='success'
                WHERE id=%s
            """, (guilds_count, users_count, global_count, duration, run_id))
            conn.commit()

            print(f"\n=== 완료. {duration}초 / guilds {guilds_count} + users {users_count} + global {global_count} ===")

    except Exception as e:
        # 실패 기록
        if run_id is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE backup_runs
                        SET completed_at=NOW(), status='failed', error_message=%s
                        WHERE id=%s
                    """, (str(e)[:500], run_id))
                    conn.commit()
            except Exception:
                pass

        print(f"[ERROR] 백업 실패: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())

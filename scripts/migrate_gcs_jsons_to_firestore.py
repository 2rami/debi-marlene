"""
GCS JSON → Firestore 일회성 마이그레이션

이관 대상:
  command_logs.json   → Firestore `command_logs` 컬렉션 (each log = doc, expireAt 30일)
  dashboard_logs.json → Firestore `dashboard_logs` 컬렉션 (each log = doc)
  quiz_data.json      → Firestore `quiz/global` + `quiz/{guild_id}` + sessions subcollection

사용법:
  python3 scripts/migrate_gcs_jsons_to_firestore.py --dry-run        # 미리보기
  python3 scripts/migrate_gcs_jsons_to_firestore.py                  # 실제 실행
  python3 scripts/migrate_gcs_jsons_to_firestore.py --only quiz      # 특정 항목만
  python3 scripts/migrate_gcs_jsons_to_firestore.py --only logs      # command + dashboard
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'ironic-objectivist-465713-a6')
GCS_BUCKET = os.getenv('GCS_BUCKET_NAME', 'debi-marlene-settings')

COMMAND_LOGS_KEY = 'command_logs.json'
DASHBOARD_LOGS_KEY = 'dashboard_logs.json'
QUIZ_DATA_KEY = 'quiz_data.json'

COMMAND_LOGS_COLLECTION = 'command_logs'
DASHBOARD_LOGS_COLLECTION = 'dashboard_logs'
QUIZ_COLLECTION = 'quiz'
GLOBAL_DOC = 'global'
SESSIONS_SUBCOLLECTION = 'sessions'

COMMAND_LOGS_TTL_DAYS = 30
FIRESTORE_BATCH_LIMIT = 400  # 500 한도 안전 마진


def _gcs_load(blob_name):
    from google.cloud import storage
    client = storage.Client(project=GCP_PROJECT_ID)
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(blob_name)
    if not blob.exists():
        print(f"  [skip] gs://{GCS_BUCKET}/{blob_name} 없음")
        return None
    return json.loads(blob.download_as_text())


def _fs_client():
    from google.cloud import firestore
    return firestore.Client(project=GCP_PROJECT_ID)


def _commit_batch(fs, ops):
    """ops = [(doc_ref, data), ...] — 400개 단위 batch commit."""
    total = 0
    for i in range(0, len(ops), FIRESTORE_BATCH_LIMIT):
        chunk = ops[i:i + FIRESTORE_BATCH_LIMIT]
        batch = fs.batch()
        for ref, data in chunk:
            batch.set(ref, data)
        batch.commit()
        total += len(chunk)
    return total


# ─────── command_logs ───────

def migrate_command_logs(dry_run=False):
    print("\n[command_logs]")
    data = _gcs_load(COMMAND_LOGS_KEY)
    if not data:
        return
    logs = data.get('logs', [])
    if not logs:
        print("  로그 없음")
        return

    print(f"  {len(logs)}개 로그 발견")
    if dry_run:
        print(f"  dry-run: '{COMMAND_LOGS_COLLECTION}' 컬렉션에 add 예정")
        return

    fs = _fs_client()
    coll = fs.collection(COMMAND_LOGS_COLLECTION)
    ops = []
    for log in logs:
        doc = dict(log)
        # expireAt — timestamp 기준 30일 (없으면 now 기준)
        try:
            ts = log.get('timestamp')
            base = datetime.fromisoformat(ts) if ts else datetime.now(timezone.utc)
            if base.tzinfo is None:
                base = base.replace(tzinfo=timezone.utc)
        except Exception:
            base = datetime.now(timezone.utc)
        doc['expireAt'] = base + timedelta(days=COMMAND_LOGS_TTL_DAYS)
        ops.append((coll.document(), doc))

    n = _commit_batch(fs, ops)
    print(f"  {n}개 이관 완료")


# ─────── dashboard_logs ───────

def migrate_dashboard_logs(dry_run=False):
    print("\n[dashboard_logs]")
    data = _gcs_load(DASHBOARD_LOGS_KEY)
    if data is None:
        return
    logs = data if isinstance(data, list) else data.get('logs', [])
    if not logs:
        print("  로그 없음")
        return

    print(f"  {len(logs)}개 로그 발견")
    if dry_run:
        print(f"  dry-run: '{DASHBOARD_LOGS_COLLECTION}' 컬렉션에 add 예정")
        return

    fs = _fs_client()
    coll = fs.collection(DASHBOARD_LOGS_COLLECTION)
    ops = [(coll.document(), dict(log)) for log in logs]
    n = _commit_batch(fs, ops)
    print(f"  {n}개 이관 완료")


# ─────── quiz_data ───────

def migrate_quiz_data(dry_run=False):
    print("\n[quiz_data]")
    data = _gcs_load(QUIZ_DATA_KEY)
    if not data:
        return

    global_songs = data.get('songs', [])
    guilds = data.get('guilds', {}) or {}
    print(f"  글로벌 곡 {len(global_songs)}개, 길드 {len(guilds)}개")

    total_sessions = sum(len(g.get('sessions', []) or []) for g in guilds.values())
    print(f"  총 세션 {total_sessions}개")

    if dry_run:
        print(f"  dry-run: quiz/global, quiz/{{guild_id}}, sessions subcollection 작성 예정")
        return

    fs = _fs_client()
    quiz_coll = fs.collection(QUIZ_COLLECTION)

    # 1) global songs
    quiz_coll.document(GLOBAL_DOC).set({'songs': global_songs}, merge=True)
    print(f"  quiz/global 작성 ({len(global_songs)}곡)")

    # 2) 길드별 songs + leaderboard + sessions
    for guild_id, gdata in guilds.items():
        gid = str(guild_id)
        songs = gdata.get('songs')
        leaderboard = gdata.get('leaderboard', {}) or {}
        sessions = gdata.get('sessions', []) or []

        fields = {'leaderboard': leaderboard}
        if songs is not None:
            fields['songs'] = songs
        quiz_coll.document(gid).set(fields, merge=True)

        if sessions:
            sub = quiz_coll.document(gid).collection(SESSIONS_SUBCOLLECTION)
            ops = []
            for s in sessions:
                sid = s.get('id') or f"legacy_{int(datetime.now(timezone.utc).timestamp())}_{len(ops)}"
                ops.append((sub.document(sid), s))
            _commit_batch(fs, ops)
        print(f"  quiz/{gid}: songs={len(songs) if songs else 0} leaderboard={len(leaderboard)} sessions={len(sessions)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='미리보기 (실제 쓰기 안 함)')
    parser.add_argument('--only', choices=['command', 'dashboard', 'logs', 'quiz'],
                        help='특정 항목만 이관')
    args = parser.parse_args()

    print(f"GCP_PROJECT={GCP_PROJECT_ID}  GCS_BUCKET={GCS_BUCKET}")
    print(f"모드: {'DRY-RUN' if args.dry_run else 'LIVE'}")

    targets = args.only
    run_command = targets in (None, 'command', 'logs')
    run_dashboard = targets in (None, 'dashboard', 'logs')
    run_quiz = targets in (None, 'quiz')

    if run_command:
        migrate_command_logs(args.dry_run)
    if run_dashboard:
        migrate_dashboard_logs(args.dry_run)
    if run_quiz:
        migrate_quiz_data(args.dry_run)

    print("\n완료")


if __name__ == '__main__':
    sys.exit(main())

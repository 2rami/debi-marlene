"""GCS settings.json → Firestore 3컬렉션 분리 마이그레이션.

기존 settings.json 한 덩어리를 guilds / users / global 컬렉션으로 분리한다.
멀티 컨테이너 lost update + dashboard split-brain 의 근본 해결을 위한 1회 작업.

사용:
    python3 scripts/migrate_settings_to_firestore.py --dry-run   # 미리보기
    python3 scripts/migrate_settings_to_firestore.py             # 실제 실행

전제:
    GOOGLE_APPLICATION_CREDENTIALS 환경변수 또는 gcloud auth application-default login 완료.
    Firestore 인스턴스 (default) 가 ironic-objectivist-465713-a6 프로젝트에 존재.

재실행 안전: set(merge=True) 사용. 누락 필드만 덮어쓰며 기존 필드 보존.
"""

import argparse
import json
import os
import sys
from typing import Any

# 프로젝트 루트를 import 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import firestore, storage

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'ironic-objectivist-465713-a6')
GCS_BUCKET = os.getenv('GCS_BUCKET_NAME', 'debi-marlene-settings')
GCS_KEY = 'settings.json'


def load_gcs_settings() -> dict:
    """GCS에서 settings.json 전체를 가져온다."""
    client = storage.Client(project=GCP_PROJECT_ID)
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(GCS_KEY)
    data = blob.download_as_text()
    return json.loads(data)


def split_settings(settings: dict) -> tuple[dict, dict, dict, list]:
    """settings.json 한 덩어리를 guilds / users / global 셋으로 분리.

    추가로 root level 에 stray guild ID(숫자 17자리+)가 있으면 guilds 로 병합한다.
    과거 잘못 쓰여진 데이터 보존.
    """
    guilds = dict(settings.get('guilds', {}) or {})
    users = settings.get('users', {}) or {}
    global_settings = settings.get('global', {}) or {}

    # Root level stray keys 처리: 숫자 ID(17자 이상)에 dict value 면 guild 로 간주
    KNOWN_TOP_KEYS = {'guilds', 'users', 'global'}
    stray_merged = []
    for key, value in settings.items():
        if key in KNOWN_TOP_KEYS:
            continue
        if isinstance(value, dict) and key.isdigit() and len(key) >= 17:
            # guild ID 같은 형태 — guilds 로 병합 (set merge 처럼)
            existing = guilds.get(key, {})
            if isinstance(existing, dict):
                merged = {**existing, **value}
                guilds[key] = merged
                stray_merged.append(key)
    return guilds, users, global_settings, stray_merged


def write_firestore(
    fs_client: firestore.Client,
    guilds: dict,
    users: dict,
    global_settings: dict,
    dry_run: bool,
) -> dict:
    """3개 컬렉션에 분산 쓰기. dry_run=True면 카운트만 반환."""
    stats = {
        'guilds_written': 0,
        'users_written': 0,
        'global_written': 0,
        'guilds_skipped': 0,
        'users_skipped': 0,
    }

    # guilds/{guild_id}
    for guild_id, guild_data in guilds.items():
        if not isinstance(guild_data, dict):
            stats['guilds_skipped'] += 1
            continue
        if not dry_run:
            fs_client.collection('guilds').document(str(guild_id)).set(guild_data, merge=True)
        stats['guilds_written'] += 1

    # users/{user_id}
    for user_id, user_data in users.items():
        if not isinstance(user_data, dict):
            stats['users_skipped'] += 1
            continue
        if not dry_run:
            fs_client.collection('users').document(str(user_id)).set(user_data, merge=True)
        stats['users_written'] += 1

    # global/settings (단일 문서)
    if global_settings:
        if not dry_run:
            fs_client.collection('global').document('settings').set(global_settings, merge=True)
        stats['global_written'] = 1

    return stats


def preview_sample(label: str, data: dict, max_items: int = 3) -> None:
    """샘플 미리보기 출력."""
    if not data:
        print(f"  [{label}] (없음)")
        return
    keys = list(data.keys())
    print(f"  [{label}] {len(keys)}개")
    for k in keys[:max_items]:
        v = data[k]
        if isinstance(v, dict):
            field_preview = ', '.join(list(v.keys())[:5])
            print(f"    - {k}: {{ {field_preview}{'...' if len(v) > 5 else ''} }}")
        else:
            print(f"    - {k}: {v}")
    if len(keys) > max_items:
        print(f"    ... 외 {len(keys) - max_items}개")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='실제 쓰기 없이 미리보기만')
    args = parser.parse_args()

    print('=' * 60)
    print('settings.json → Firestore 3컬렉션 마이그레이션')
    print(f'프로젝트: {GCP_PROJECT_ID}')
    print(f'GCS 소스: gs://{GCS_BUCKET}/{GCS_KEY}')
    print(f'모드: {"DRY-RUN (실제 쓰기 없음)" if args.dry_run else "실행"}')
    print('=' * 60)

    # 1. GCS 로드
    print('\n[1/3] GCS settings.json 로드...')
    try:
        settings = load_gcs_settings()
    except Exception as e:
        print(f'  실패: {e}')
        return 1
    print(f'  완료. 최상위 키: {list(settings.keys())}')

    # 2. 분리
    print('\n[2/3] 3개 컬렉션으로 분리...')
    guilds, users, global_settings, stray_merged = split_settings(settings)
    if stray_merged:
        print(f'  [정보] root level stray guild ID {len(stray_merged)}개 guilds 로 병합: {stray_merged}')
    preview_sample('guilds', guilds)
    preview_sample('users', users)
    preview_sample('global', {'settings': global_settings} if global_settings else {})

    # 3. Firestore 쓰기
    print('\n[3/3] Firestore 쓰기...')
    fs_client = firestore.Client(project=GCP_PROJECT_ID)
    stats = write_firestore(fs_client, guilds, users, global_settings, dry_run=args.dry_run)

    print('\n결과:')
    print(f"  guilds:  쓰기 {stats['guilds_written']}, 건너뜀 {stats['guilds_skipped']}")
    print(f"  users:   쓰기 {stats['users_written']}, 건너뜀 {stats['users_skipped']}")
    print(f"  global:  쓰기 {stats['global_written']}")

    if args.dry_run:
        print('\nDRY-RUN 완료. 실제 적용하려면 --dry-run 빼고 다시 실행.')
    else:
        print('\n마이그레이션 완료. Firestore 콘솔에서 확인:')
        print(f'  https://console.cloud.google.com/firestore/databases/-default-/data?project={GCP_PROJECT_ID}')

    return 0


if __name__ == '__main__':
    sys.exit(main())

"""GCS chat_memory/{guild}.json → SQLite migration (일회성).

GCS는 안 지움. 며칠 양쪽 비교 후 수동 정리 권장:
    gsutil rm -r gs://{BUCKET}/chat_memory/

사용법:
    python3 scripts/migrate_chat_memory_to_sqlite.py

전제:
    GOOGLE_APPLICATION_CREDENTIALS 또는 gcloud auth application-default login 완료
    GCS_BUCKET_NAME (default: debi-marlene-settings)
    BOT_DATA_DIR (default: ./data)
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env(ROOT / ".env")

from run.services.memory.db import connect  # noqa: E402

BUCKET = os.getenv("GCS_BUCKET_NAME", "debi-marlene-settings")
PREFIX = "chat_memory/"


def main():
    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(BUCKET)

    blobs = list(bucket.list_blobs(prefix=PREFIX))
    json_blobs = [b for b in blobs if b.name.endswith(".json")]

    print(f"GCS gs://{BUCKET}/{PREFIX} → {len(json_blobs)}개 JSON 파일 발견")
    print()

    total_inserted = 0
    total_dup = 0

    with connect() as conn:
        for blob in json_blobs:
            guild_id = Path(blob.name).stem
            try:
                data = json.loads(blob.download_as_text())
            except Exception as e:
                print(f"  guild={guild_id}: 파싱 실패 (스킵) — {e}")
                continue
            corrections = data.get("corrections", [])
            if not isinstance(corrections, list):
                print(f"  guild={guild_id}: corrections가 리스트 아님 (스킵)")
                continue

            inserted = 0
            dup = 0
            for text in corrections:
                if not isinstance(text, str) or not text.strip():
                    continue
                cur = conn.execute(
                    "INSERT OR IGNORE INTO corrections(guild_id, text) VALUES (?, ?)",
                    (guild_id, text),
                )
                if cur.rowcount > 0:
                    inserted += 1
                else:
                    dup += 1

            total_inserted += inserted
            total_dup += dup
            print(
                f"  guild={guild_id}: {inserted} new, {dup} dup "
                f"(GCS source: {len(corrections)})"
            )

    print()
    print(f"SUMMARY: {total_inserted} new + {total_dup} dup imported")
    print()
    print("GCS는 안 지웠음. 며칠 양쪽 비교 후 다음 명령으로 정리:")
    print(f"  gsutil rm -r gs://{BUCKET}/{PREFIX}")


if __name__ == "__main__":
    main()

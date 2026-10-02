"""로컬 문서 저장소 — Firestore 를 걷어낸 자리에 들어간 SQLite 한 파일.

봇·대시보드·웹패널 세 프로세스가 같은 맥미니에서 이 파일 하나를 같이 쓴다. 호출부가
Firestore 문법(collection/document/where/transaction/Increment ...)을 그대로 쓰도록
같은 모양의 얇은 층을 둔다. 이 레포가 실제로 쓰는 만큼만 있다.

- 문서는 (컬렉션 경로, id) 한 줄에 JSON 으로 든다. 하위 컬렉션은 경로다(`quiz/123/sessions`).
- 쓰기는 전부 BEGIN IMMEDIATE 로 줄을 세운다. 그래서 트랜잭션은 충돌이 없고 재시도도 없다 —
  Firestore 처럼 함수를 다시 돌리지 않는다.
- datetime 은 `$dt:` 를 붙인 UTC 문자열로 넣고 읽을 때 되살린다. 고정 형식이라 문자열
  비교가 곧 시각 비교여서 where·order_by 가 그대로 맞는다.
- 문서가 바뀔 때마다 트리거가 `changes` 에 한 줄 남긴다. 다른 프로세스가 바꾼 문서만 골라
  다시 읽는 캐시(Mirror)가 이걸 본다 — Firestore 리스너가 하던 일이다.
"""

from __future__ import annotations

import base64
import json
import os
import random
import sqlite3
import string
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Optional

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 세 프로세스가 각자 다른 cwd·심링크 경로로 뜬다. 같은 파일을 다른 이름으로 열면 -wal/-shm 이
# 갈라질 수 있어 실경로로 못박는다.
DB_PATH = os.path.realpath(os.getenv('STORE_DB_PATH') or os.path.join(_ROOT, 'data', 'store.db'))
BACKUP_DIR = os.path.realpath(os.getenv('STORE_BACKUP_DIR') or os.path.join(_ROOT, 'backups', 'store'))
BACKUP_KEEP_DAYS = 14

_DT_TAG = '$dt:'
_B64_TAG = '$b64:'
_AUTO_ID_CHARS = string.ascii_letters + string.digits

_SCHEMA = """
CREATE TABLE IF NOT EXISTS docs (
    col  TEXT NOT NULL,
    id   TEXT NOT NULL,
    data TEXT NOT NULL,
    PRIMARY KEY (col, id)
);
CREATE TABLE IF NOT EXISTS changes (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    col TEXT NOT NULL,
    id  TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON docs
BEGIN INSERT INTO changes(col, id) VALUES (NEW.col, NEW.id); END;
CREATE TRIGGER IF NOT EXISTS docs_au AFTER UPDATE ON docs
BEGIN INSERT INTO changes(col, id) VALUES (NEW.col, NEW.id); END;
CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON docs
BEGIN INSERT INTO changes(col, id) VALUES (OLD.col, OLD.id); END;
"""


class NotFound(Exception):
    """update 대상 문서가 없다 (Firestore 의 google.api_core.exceptions.NotFound 자리)."""


class StoreMissing(RuntimeError):
    """DB 파일이 없다. 빈 DB 를 새로 만들어 빈 설정으로 도는 것보다 멈추는 편이 낫다."""


# ───────────────────── 특수 값 ─────────────────────

class Increment:
    def __init__(self, value):
        self.value = value


class _Sentinel:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


SERVER_TIMESTAMP = _Sentinel('SERVER_TIMESTAMP')
DELETE_FIELD = _Sentinel('DELETE_FIELD')


def _resolve(value, current):
    if isinstance(value, Increment):
        return (current if isinstance(current, (int, float)) and not isinstance(current, bool) else 0) + value.value
    if value is SERVER_TIMESTAMP:
        return datetime.now(timezone.utc)
    if isinstance(value, dict):
        return {k: _resolve(v, None) for k, v in value.items() if v is not DELETE_FIELD}
    if isinstance(value, list):
        return [_resolve(v, None) for v in value]
    return value


# ───────────────────── 인코딩 ─────────────────────

def _json_default(o):
    if isinstance(o, datetime):
        if o.tzinfo is None:
            o = o.replace(tzinfo=timezone.utc)
        return _DT_TAG + o.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')
    if isinstance(o, (bytes, bytearray)):
        return _B64_TAG + base64.b64encode(bytes(o)).decode('ascii')
    raise TypeError(f'저장할 수 없는 값: {type(o).__name__}')


def encode(data) -> str:
    """정규형 JSON. 같은 내용이면 글자까지 같아서 「안 바뀐 문서」를 문자열 비교로 가린다."""
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                      default=_json_default, allow_nan=False)


def _revive(v):
    if isinstance(v, str):
        if v.startswith(_DT_TAG):
            try:
                return datetime.fromisoformat(v[len(_DT_TAG):])
            except ValueError:
                return v
        if v.startswith(_B64_TAG):
            try:
                return base64.b64decode(v[len(_B64_TAG):])
            except ValueError:
                return v
        return v
    if isinstance(v, dict):
        return {k: _revive(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_revive(x) for x in v]
    return v


def decode(raw: str):
    data = json.loads(raw)
    if '"' + _DT_TAG in raw or '"' + _B64_TAG in raw:
        data = _revive(data)
    return data


def encode_value(v):
    """쿼리 비교값을 저장 형식에 맞춘다 (datetime → 태그 문자열)."""
    if isinstance(v, datetime):
        return _json_default(v)
    return v


# ───────────────────── 연결 ─────────────────────

_local = threading.local()
_schema_lock = threading.Lock()
_schema_ready_pid = None


def _may_create() -> bool:
    return os.getenv('STORE_CREATE') == '1'


def wait_ready(poll: float = 2.0) -> None:
    """DB 파일이 생길 때까지 기다린다. 봇·대시보드·웹패널이 시작할 때 한 번 부른다.

    컷오버 중 새 코드가 import 보다 먼저 뜨면 아무것도 쓰지 않고 여기서 선다 — 이관 스크립트가
    파일을 놓는 순간 이어서 뜬다. 처음부터 빈 DB 로 시작하려면 STORE_CREATE=1.
    """
    waited = 0.0
    while not os.path.exists(DB_PATH) and not _may_create():
        if waited % 60 == 0:
            print(f'[저장소] {DB_PATH} 가 없다 — 이관(scripts/firestore_to_sqlite.py import)을 기다린다', flush=True)
        time.sleep(poll)
        waited += poll


def _connect() -> sqlite3.Connection:
    if not os.path.exists(DB_PATH) and not _may_create():
        raise StoreMissing(f'{DB_PATH} 가 없다. scripts/firestore_to_sqlite.py import 로 만들거나 '
                           f'빈 DB 로 시작하려면 STORE_CREATE=1')
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    conn.execute('PRAGMA synchronous=FULL')  # 크레딧 장부가 들어 있다 — 커밋은 디스크까지
    global _schema_ready_pid
    with _schema_lock:
        if _schema_ready_pid != os.getpid():
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('BEGIN IMMEDIATE')
            try:
                for stmt in _split_sql(_SCHEMA):
                    conn.execute(stmt)
                conn.execute('COMMIT')
            except BaseException:
                conn.execute('ROLLBACK')
                raise
            _schema_ready_pid = os.getpid()
    return conn


def _split_sql(script: str) -> list[str]:
    # executescript 는 열린 트랜잭션을 먼저 커밋해 버려서 쓸 수 없다. 트리거 본문의 ; 는
    # END; 까지 한 문장으로 묶는다.
    out, buf = [], []
    for line in script.strip().splitlines():
        buf.append(line)
        joined = '\n'.join(buf).strip()
        if joined.endswith(';') and (not joined.upper().startswith('CREATE TRIGGER') or joined.upper().endswith('END;')):
            out.append(joined)
            buf = []
    return out


def conn() -> sqlite3.Connection:
    """스레드별 연결. gunicorn 이 fork 한 워커는 부모 연결을 물려받으면 안 되므로 pid 도 본다."""
    c = getattr(_local, 'conn', None)
    if c is None or getattr(_local, 'pid', None) != os.getpid():
        c = _connect()
        _local.conn = c
        _local.pid = os.getpid()
    return c


@contextmanager
def write_txn():
    """쓰기 한 묶음. 바깥에 트랜잭션이 이미 열려 있으면 그 안에 savepoint 로 들어간다."""
    c = conn()
    if c.in_transaction:
        c.execute('SAVEPOINT w')
        try:
            yield c
        except BaseException:
            c.execute('ROLLBACK TO w')
            c.execute('RELEASE w')
            raise
        c.execute('RELEASE w')
        return
    c.execute('BEGIN IMMEDIATE')
    try:
        yield c
        c.execute('COMMIT')
    except BaseException:
        if c.in_transaction:
            c.execute('ROLLBACK')
        raise


@contextmanager
def read_txn():
    """여러 SELECT 를 한 시점의 모습으로 읽는다."""
    c = conn()
    if c.in_transaction:
        yield c
        return
    c.execute('BEGIN')
    try:
        yield c
    finally:
        c.execute('COMMIT')


def get_raw(c: sqlite3.Connection, col: str, doc_id: str) -> Optional[str]:
    row = c.execute('SELECT data FROM docs WHERE col = ? AND id = ?', (col, doc_id)).fetchone()
    return row[0] if row else None


def put_raw(c: sqlite3.Connection, col: str, doc_id: str, raw: str) -> None:
    # 내용이 같으면 UPDATE 를 건너뛴다 — 트리거가 안 돌아 다른 프로세스 캐시도 안 흔들린다.
    c.execute(
        'INSERT INTO docs(col, id, data) VALUES (?, ?, ?) '
        'ON CONFLICT(col, id) DO UPDATE SET data = excluded.data WHERE data IS NOT excluded.data',
        (col, doc_id, raw),
    )


def delete_raw(c: sqlite3.Connection, col: str, doc_id: str) -> None:
    c.execute('DELETE FROM docs WHERE col = ? AND id = ?', (col, doc_id))


# ───────────────────── 문서 연산 ─────────────────────

def _merge(current: dict, data: dict) -> dict:
    """set(merge=True). 중첩 맵은 깊게 합치고 빈 맵은 값으로 덮는다 (Firestore 와 같은 규칙)."""
    out = dict(current)
    for k, v in data.items():
        if v is DELETE_FIELD:
            out.pop(k, None)
        elif isinstance(v, dict) and v:
            base = out.get(k)
            out[k] = _merge(base if isinstance(base, dict) else {}, v)
        else:
            out[k] = _resolve(v, out.get(k))
    return out


def _apply_update(current: dict, fields: dict) -> dict:
    """update(). 키의 점은 중첩 경로이고, 값은 그 자리를 통째로 바꾼다."""
    out = json_copy(current)
    for path, v in fields.items():
        parts = path.split('.')
        node = out
        for p in parts[:-1]:
            nxt = node.get(p)
            if not isinstance(nxt, dict):
                nxt = {}
                node[p] = nxt
            node = nxt
        if v is DELETE_FIELD:
            node.pop(parts[-1], None)
        else:
            node[parts[-1]] = _resolve(v, node.get(parts[-1]))
    return out


def json_copy(d: dict) -> dict:
    out = {}
    for k, v in d.items():
        out[k] = json_copy(v) if isinstance(v, dict) else v
    return out


def _write_set(c, col, doc_id, data, merge):
    if merge:
        raw = get_raw(c, col, doc_id)
        new = _merge(decode(raw) if raw else {}, data)
    else:
        new = _resolve(data, None)
    put_raw(c, col, doc_id, encode(new))


def _write_update(c, col, doc_id, fields):
    raw = get_raw(c, col, doc_id)
    if raw is None:
        raise NotFound(f'{col}/{doc_id}')
    put_raw(c, col, doc_id, encode(_apply_update(decode(raw), fields)))


# ───────────────────── Firestore 모양 ─────────────────────

class DocumentSnapshot:
    def __init__(self, reference: 'DocumentReference', raw: Optional[str]):
        self.reference = reference
        self.id = reference.id
        self._raw = raw

    @property
    def exists(self) -> bool:
        return self._raw is not None

    def to_dict(self):
        return decode(self._raw) if self._raw is not None else None

    def get(self, field_path: str):
        node = self.to_dict() or {}
        for p in field_path.split('.'):
            if not isinstance(node, dict) or p not in node:
                raise KeyError(field_path)
            node = node[p]
        return node


class DocumentReference:
    def __init__(self, col: str, doc_id: str):
        self._col = col
        self.id = doc_id

    @property
    def path(self) -> str:
        return f'{self._col}/{self.id}'

    @property
    def parent(self) -> 'CollectionReference':
        return CollectionReference(self._col)

    def collection(self, name: str) -> 'CollectionReference':
        return CollectionReference(f'{self.path}/{name}')

    def get(self, transaction=None) -> DocumentSnapshot:
        return DocumentSnapshot(self, get_raw(conn(), self._col, self.id))

    def set(self, data: dict, merge: bool = False) -> None:
        with write_txn() as c:
            _write_set(c, self._col, self.id, data, merge)

    def update(self, fields: dict) -> None:
        with write_txn() as c:
            _write_update(c, self._col, self.id, fields)

    def delete(self) -> None:
        with write_txn() as c:
            delete_raw(c, self._col, self.id)


class FieldFilter:
    def __init__(self, field_path: str, op_string: str, value):
        self.field_path = field_path
        self.op_string = op_string
        self.value = value


def _json_path(field_path: str) -> str:
    parts = field_path.split('.')
    if any('"' in p for p in parts):
        raise ValueError(f'필드 이름에 " 를 쓸 수 없다: {field_path}')
    path = '$' + ''.join(f'."{p}"' for p in parts)
    return "'" + path.replace("'", "''") + "'"


def _type_guard(value) -> tuple[str, bool]:
    """(json_type 조건 목록, 값 비교가 필요한지). 타입이 다르면 Firestore 처럼 안 맞는다."""
    if isinstance(value, bool):
        return ("'true'" if value else "'false'"), False
    if value is None:
        return "'null'", False
    if isinstance(value, (int, float)):
        return "'integer','real'", True
    return "'text'", True


def _condition(field_path: str, op: str, value, params: list) -> str:
    p = _json_path(field_path)
    x, t = f'json_extract(data, {p})', f'json_type(data, {p})'
    if op == 'in':
        parts = [_condition(field_path, '==', v, params) for v in value]
        return '(' + ' OR '.join(parts) + ')' if parts else '0'
    if op == 'array-contains':
        types, compare = _type_guard(value)
        cond = f'j.type IN ({types})'
        if compare:
            cond += ' AND j.value = ?'
            params.append(encode_value(value))
        return f'EXISTS (SELECT 1 FROM json_each(data, {p}) j WHERE {cond})'
    if op == '!=':
        eq = _condition(field_path, '==', value, params)
        return f"({t} IS NOT NULL AND {t} != 'null' AND NOT {eq})"
    sql_op = {'==': '=', '<': '<', '<=': '<=', '>': '>', '>=': '>='}.get(op)
    if sql_op is None:
        raise ValueError(f'지원하지 않는 연산: {op}')
    types, compare = _type_guard(value)
    cond = f'{t} IN ({types})'
    if compare or sql_op != '=':
        cond += f' AND {x} {sql_op} ?'
        params.append(encode_value(value))
    return f'({cond})'


class Query:
    ASCENDING = 'ASCENDING'
    DESCENDING = 'DESCENDING'

    def __init__(self, col: str, filters=(), orders=(), limit_n=None):
        self._col = col
        self._filters = tuple(filters)
        self._orders = tuple(orders)
        self._limit = limit_n

    def where(self, field_path=None, op_string=None, value=None, *, filter=None) -> 'Query':
        f = filter or FieldFilter(field_path, op_string, value)
        return Query(self._col, self._filters + (f,), self._orders, self._limit)

    def order_by(self, field_path: str, direction: str = ASCENDING) -> 'Query':
        return Query(self._col, self._filters, self._orders + ((field_path, direction),), self._limit)

    def limit(self, count: int) -> 'Query':
        return Query(self._col, self._filters, self._orders, int(count))

    def stream(self, transaction=None):
        params: list = [self._col]
        where = ['col = ?']
        for f in self._filters:
            where.append(_condition(f.field_path, f.op_string, f.value, params))
        order = []
        for field_path, direction in self._orders:
            p = _json_path(field_path)
            where.append(f'json_type(data, {p}) IS NOT NULL')  # 필드가 없는 문서는 정렬에서 빠진다
            d = 'DESC' if direction == Query.DESCENDING else 'ASC'
            # 타입이 섞이면 Firestore 순서(null < bool < 숫자 < 문자열 < 배열 < 맵)를 먼저 따른다
            order.append(f"CASE json_type(data, {p}) WHEN 'null' THEN 0 WHEN 'false' THEN 1 WHEN 'true' THEN 1 "
                         f"WHEN 'integer' THEN 2 WHEN 'real' THEN 2 WHEN 'text' THEN 3 WHEN 'array' THEN 4 "
                         f"ELSE 5 END {d}")
            order.append(f'json_extract(data, {p}) {d}')
        last_dir = 'DESC' if self._orders and self._orders[-1][1] == Query.DESCENDING else 'ASC'
        order.append(f'id {last_dir}')
        sql = f'SELECT id, data FROM docs WHERE {" AND ".join(where)} ORDER BY {", ".join(order)}'
        if self._limit is not None:
            sql += f' LIMIT {int(self._limit)}'
        rows = conn().execute(sql, params).fetchall()
        for doc_id, raw in rows:
            yield DocumentSnapshot(DocumentReference(self._col, doc_id), raw)

    def get(self, transaction=None) -> list:
        return list(self.stream(transaction))


class CollectionReference(Query):
    def __init__(self, col: str):
        super().__init__(col)

    @property
    def id(self) -> str:
        return self._col.rsplit('/', 1)[-1]

    def document(self, doc_id: Optional[str] = None) -> DocumentReference:
        if doc_id is None:
            doc_id = ''.join(random.choices(_AUTO_ID_CHARS, k=20))
        return DocumentReference(self._col, str(doc_id))

    def add(self, data: dict, document_id: Optional[str] = None):
        ref = self.document(document_id)
        ref.set(data)
        return datetime.now(timezone.utc), ref


class WriteBatch:
    def __init__(self):
        self._ops = []

    def set(self, ref: DocumentReference, data: dict, merge: bool = False):
        self._ops.append(('set', ref, data, merge))

    def update(self, ref: DocumentReference, fields: dict):
        self._ops.append(('update', ref, fields, None))

    def delete(self, ref: DocumentReference):
        self._ops.append(('delete', ref, None, None))

    def commit(self):
        with write_txn() as c:
            for op, ref, data, merge in self._ops:
                _apply_op(c, op, ref, data, merge)
        self._ops = []


def _apply_op(c, op, ref, data, merge):
    if op == 'set':
        _write_set(c, ref._col, ref.id, data, merge)
    elif op == 'update':
        _write_update(c, ref._col, ref.id, data)
    else:
        delete_raw(c, ref._col, ref.id)


class Transaction:
    """transactional 이 연 IMMEDIATE 트랜잭션 안에서 바로 쓴다. 읽기도 같은 연결이라
    방금 쓴 것이 보인다 — Firestore 와 달리 「읽기 먼저」 제약이 없지만 지켜도 손해는 없다."""

    def set(self, ref: DocumentReference, data: dict, merge: bool = False):
        _write_set(conn(), ref._col, ref.id, data, merge)

    def update(self, ref: DocumentReference, fields: dict):
        _write_update(conn(), ref._col, ref.id, fields)

    def delete(self, ref: DocumentReference):
        delete_raw(conn(), ref._col, ref.id)


def transactional(fn):
    def wrapper(transaction: Transaction, *args, **kwargs):
        with write_txn():
            return fn(transaction, *args, **kwargs)
    return wrapper


class Client:
    def collection(self, path: str) -> CollectionReference:
        return CollectionReference(path)

    def document(self, path: str) -> DocumentReference:
        col, doc_id = path.rsplit('/', 1)
        return DocumentReference(col, doc_id)

    def batch(self) -> WriteBatch:
        return WriteBatch()

    def transaction(self) -> Transaction:
        return Transaction()

    def get_all(self, references: Iterable[DocumentReference], transaction=None):
        with read_txn() as c:
            snaps = [DocumentSnapshot(r, get_raw(c, r._col, r.id)) for r in references]
        yield from snaps


_client = Client()


def client() -> Client:
    return _client


# ───────────────────── 프로세스 캐시 ─────────────────────

class Mirror:
    """몇 컬렉션을 메모리에 들고 있다가, changes 를 보고 바뀐 문서만 다시 읽는다.

    봇은 메시지마다 서버 설정을 읽는다. 매번 수백 문서를 파싱할 수는 없고, 그렇다고 캐시를
    오래 들면 대시보드에서 바꾼 설정이 안 보인다. 확인은 max(seq) 한 번이라 싸다.
    """

    def __init__(self, cols: Iterable[str]):
        self.cols = tuple(cols)
        self.docs: dict[str, dict[str, Any]] = {c: {} for c in self.cols}
        self.seq: Optional[int] = None
        self.lock = threading.Lock()

    def sync(self) -> None:
        """호출자가 self.lock 을 쥐고 부른다."""
        with read_txn() as c:
            # max(seq) 가 아니라 sqlite_sequence 를 본다 — changes 를 비우거나 잘라내도
            # 마지막으로 매긴 번호는 남는다.
            row = c.execute("SELECT seq FROM sqlite_sequence WHERE name = 'changes'").fetchone()
            max_seq = row[0] if row else 0
            if self.seq is not None and max_seq == self.seq:
                return
            min_seq = c.execute('SELECT min(seq) FROM changes').fetchone()[0]
            # 처음이거나, 정리(prune)로 우리가 본 뒤의 기록이 잘려 나갔으면 통째로 다시 읽는다.
            if self.seq is None or min_seq is None or min_seq > self.seq + 1:
                for col in self.cols:
                    self.docs[col] = {
                        doc_id: decode(raw)
                        for doc_id, raw in c.execute('SELECT id, data FROM docs WHERE col = ?', (col,))
                    }
            else:
                marks = ','.join('?' * len(self.cols))
                touched = c.execute(
                    f'SELECT DISTINCT col, id FROM changes WHERE seq > ? AND col IN ({marks})',
                    (self.seq, *self.cols),
                ).fetchall()
                for col, doc_id in touched:
                    raw = get_raw(c, col, doc_id)
                    if raw is None:
                        self.docs[col].pop(doc_id, None)
                    else:
                        self.docs[col][doc_id] = decode(raw)
            self.seq = max_seq


# ───────────────────── 정리·백업 ─────────────────────

def purge_expired(now: Optional[datetime] = None) -> int:
    """expireAt 이 지난 문서 삭제 — Firestore TTL 정책(command_logs 30일 등)이 하던 일."""
    cutoff = encode_value(now or datetime.now(timezone.utc))
    with write_txn() as c:
        cur = c.execute(
            "DELETE FROM docs WHERE json_type(data, '$.\"expireAt\"') = 'text' "
            "AND json_extract(data, '$.\"expireAt\"') LIKE '$dt:%' "
            "AND json_extract(data, '$.\"expireAt\"') < ?",
            (cutoff,),
        )
        return cur.rowcount


def prune_changes(keep: int = 200_000) -> int:
    with write_txn() as c:
        cur = c.execute('DELETE FROM changes WHERE seq <= (SELECT max(seq) FROM changes) - ?', (keep,))
        return cur.rowcount


def backup(dest_dir: str = BACKUP_DIR, keep_days: int = BACKUP_KEEP_DAYS,
           today: Optional[str] = None) -> Optional[str]:
    """날짜별 사본 하나(`store-YYYY-MM-DD.db`). 오늘 것이 이미 있으면 아무것도 안 한다.

    sqlite3 CLI 의 .backup 과 같은 온라인 백업 API 라 다른 프로세스가 쓰는 중에도 안전하다.
    keep_days 보다 오래된 사본은 지운다. 새로 만들었으면 그 경로를 돌려준다.
    """
    os.makedirs(dest_dir, exist_ok=True)
    today = today or datetime.now().strftime('%Y-%m-%d')
    final = os.path.join(dest_dir, f'store-{today}.db')
    made = None
    if not os.path.exists(final):
        tmp = final + '.part'
        if os.path.exists(tmp):
            os.remove(tmp)
        dst = sqlite3.connect(tmp)
        try:
            conn().backup(dst)
            dst.execute('PRAGMA journal_mode=DELETE')  # 사본은 -wal 없이 파일 하나로 옮겨 다니게
            ok = dst.execute('PRAGMA quick_check').fetchone()[0]
        finally:
            dst.close()
        if ok != 'ok':
            os.remove(tmp)
            raise RuntimeError(f'백업 사본 검사 실패: {ok}')
        os.replace(tmp, final)
        made = final

    cutoff = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=keep_days)).strftime('%Y-%m-%d')
    for name in os.listdir(dest_dir):
        if name.startswith('store-') and name.endswith('.db') and name[6:16] < cutoff:
            os.remove(os.path.join(dest_dir, name))
    return made


def daily_maintenance() -> dict:
    """봇이 한 시간마다 부른다. 오늘 백업이 없을 때만 실제로 일한다 — 재시작이 잦아도 하루 한 번."""
    made = backup()
    if not made:
        return {'backup': None}
    return {'backup': made, 'expired': purge_expired(), 'changes_pruned': prune_changes()}


if __name__ == '__main__':
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'backup':
        print(daily_maintenance())
    elif cmd == 'stats':
        for col, n in conn().execute('SELECT col, count(*) FROM docs GROUP BY col ORDER BY col'):
            print(f'{col}\t{n}')
        print('db', DB_PATH)
    else:
        print('사용: python3 -m run.core.store backup|stats')

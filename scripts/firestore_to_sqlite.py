"""Firestore → 로컬 SQLite(run/core/store.py) 이관.

    python3 scripts/firestore_to_sqlite.py export [--out PATH]
        Firestore 전체(하위 컬렉션 포함)를 JSONL 한 파일로. 영구 보관용 원본이다.
    python3 scripts/firestore_to_sqlite.py import SRC [--db PATH]
        JSONL 을 SQLite 로. 옆에 임시 파일로 다 채운 뒤 이름을 바꿔 놓는다 — 시작하며
        DB 를 기다리던 봇·대시보드·웹패널(store.wait_ready)은 반쯤 찬 파일을 보지 않는다.
        이미 DB 가 있으면 거절한다(돌고 있는 프로세스 밑에서 파일을 바꾸면 안 된다).
    python3 scripts/firestore_to_sqlite.py verify SRC [--db PATH] [--live] [--sample N]
        SQLite 가 JSONL 과 문서 하나하나까지 같은지, 크레딧 합계가 같은지 본다.
        --live 면 지금의 Firestore 와도 대조한다(컷오버 직전 「멈춘 뒤 바뀐 게 없나」 확인).
    python3 scripts/firestore_to_sqlite.py pushback SRC --db PATH [--apply]
        되돌리기용. 컷오버 뒤 SQLite 에 쌓인 변경(SRC export 와 다른 문서·새 문서·지운 문서)을
        Firestore 에 되민다. Firestore 는 컷오버 때 export 그대로 멈춰 있으므로 그 차이가 곧
        컷오버 뒤의 쓰기 전부다. --apply 없이는 무엇을 쓸지만 보여 준다.

인증은 GOOGLE_APPLICATION_CREDENTIALS 또는 gcloud ADC. 이관이 끝나면 이 스크립트도
Firestore 패키지가 필요한 유일한 곳이 된다.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'ironic-objectivist-465713-a6')

# 잔액 합계를 따로 대조할 컬렉션 — 돈이라 문서 대조와 별개로 숫자를 눈으로 남긴다.
BALANCE_COLLECTIONS = ('credits', 'guild_credits')


def _store(db_path, create=False):
    # run.core 패키지를 거치면 봇 모듈까지 딸려 올라온다 — 저장소 파일만 직접 읽는다.
    if db_path:
        os.environ['STORE_DB_PATH'] = db_path
    if create:
        os.environ['STORE_CREATE'] = '1'
    import importlib.util
    spec = importlib.util.spec_from_file_location('store', os.path.join(ROOT, 'run', 'core', 'store.py'))
    store = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(store)
    return store


def _plain(v):
    """Firestore 전용 타입을 store 가 저장할 수 있는 값으로."""
    from google.cloud.firestore_v1.base_document import BaseDocumentReference as _BaseRef
    from google.cloud.firestore_v1._helpers import GeoPoint
    try:
        from google.cloud.firestore_v1.vector import Vector
    except ImportError:  # 구버전 SDK
        Vector = ()
    if isinstance(v, dict):
        return {k: _plain(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_plain(x) for x in v]
    if Vector and isinstance(v, Vector):
        return [float(x) for x in v.to_map_value()['value']]
    if isinstance(v, GeoPoint):
        return {'latitude': v.latitude, 'longitude': v.longitude}
    if isinstance(v, _BaseRef):
        return v.path
    return v


def _firestore():
    from google.cloud import firestore
    return firestore.Client(project=GCP_PROJECT_ID)


def _walk(db, col_ref, pool, out):
    """컬렉션 하나를 읽고, 문서마다 하위 컬렉션을 찾아 내려간다.

    list_documents 는 「문서는 없는데 하위 컬렉션만 있는」 빈 부모도 돌려준다 —
    get 만 돌면 그 밑의 세션 기록을 통째로 놓친다.
    """
    refs = list(col_ref.list_documents())
    snaps = {s.reference.path: s for s in db.get_all(refs)} if refs else {}
    for ref in refs:
        snap = snaps.get(ref.path)
        if snap is not None and snap.exists:
            out.append({
                'col': '/'.join(col_ref._path),
                'id': ref.id,
                'update_time': snap.update_time.isoformat() if snap.update_time else None,
                'data': _plain(snap.to_dict() or {}),
            })
    subs = list(pool.map(lambda r: list(r.collections()), refs))
    for sub_cols in subs:
        for sub in sub_cols:
            _walk(db, sub, pool, out)


def cmd_export(args):
    store = _store(None)
    db = _firestore()
    out = []
    with ThreadPoolExecutor(16) as pool:
        for col in db.collections():
            before = len(out)
            _walk(db, col, pool, out)
            print(f'  {col.id}: {len(out) - before}', flush=True)

    path = args.out or os.path.join(
        ROOT, 'backups', f'firestore-export-{datetime.now().strftime("%Y%m%d-%H%M%S")}.jsonl')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.part'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(json.dumps({'_meta': {'project': GCP_PROJECT_ID, 'exported_at': datetime.now(timezone.utc).isoformat(),
                                      'docs': len(out)}}, ensure_ascii=False) + '\n')
        for row in out:
            # data 는 store 와 같은 인코딩(datetime → $dt:) 이라 import 가 손대지 않고 넣는다.
            f.write('{"col":%s,"id":%s,"update_time":%s,"data":%s}\n' % (
                json.dumps(row['col'], ensure_ascii=False), json.dumps(row['id'], ensure_ascii=False),
                json.dumps(row['update_time']), store.encode(row['data'])))
    os.replace(tmp, path)
    print(f'export {len(out)} docs -> {path}')


def _read_export(src):
    meta, rows = None, []
    with open(src, encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            if '_meta' in obj:
                meta = obj['_meta']
                continue
            rows.append(obj)
    if meta is None or meta.get('docs') != len(rows):
        raise SystemExit(f'export 파일이 잘렸다: meta={meta} rows={len(rows)}')
    return meta, rows


def cmd_import(args):
    final = os.path.realpath(args.db or _store(None).DB_PATH)
    if os.path.exists(final):
        raise SystemExit(f'{final} 가 이미 있다. 다시 넣으려면 프로세스를 멈추고 파일을 치운 뒤에.')
    tmp = final + '.importing'
    for p in (tmp, tmp + '-wal', tmp + '-shm'):
        if os.path.exists(p):
            os.remove(p)
    meta, rows = _read_export(args.src)
    store = _store(tmp, create=True)
    with store.write_txn() as w:
        for row in rows:
            raw = store.encode(store.decode(json.dumps(row['data'], ensure_ascii=False)))
            store.put_raw(w, row['col'], row['id'], raw)
        w.execute('DELETE FROM changes')  # 첫 적재는 변경 이력이 아니다
    c = store.conn()
    c.execute('PRAGMA journal_mode=DELETE')  # -wal 없이 파일 하나로 만든 뒤 옮긴다
    c.close()
    os.replace(tmp, final)
    print(f'import {len(rows)} docs -> {final} (export {meta["exported_at"]})')


def _balances_from_rows(rows):
    out = {}
    for col in BALANCE_COLLECTIONS:
        docs = [r for r in rows if r['col'] == col]
        out[col] = (len(docs), sum(int((r['data'] or {}).get('balance', 0)) for r in docs))
    ledger = [r for r in rows if r['col'] == 'credit_ledger']
    out['credit_ledger'] = (len(ledger), sum(int((r['data'] or {}).get('amount', 0)) for r in ledger))
    return out


def cmd_verify(args):
    store = _store(args.db)
    meta, rows = _read_export(args.src)
    c = store.conn()
    problems = []

    want_counts = {}
    for r in rows:
        want_counts[r['col']] = want_counts.get(r['col'], 0) + 1
    got_counts = dict(c.execute('SELECT col, count(*) FROM docs GROUP BY col').fetchall())
    shown = {}
    for col in sorted(set(want_counts) | set(got_counts)):
        w, g = want_counts.get(col, 0), got_counts.get(col, 0)
        if w != g:
            problems.append(f'count {col}: {w} != {g}')
        # 하위 컬렉션(quiz/<id>/sessions)은 묶어서 보여 준다 — 대조는 경로마다 따로 했다
        parts = col.split('/')
        key = col if len(parts) == 1 else '/'.join(p if i % 2 == 0 else '*' for i, p in enumerate(parts))
        sw, sg = shown.get(key, (0, 0))
        shown[key] = (sw + w, sg + g)
    print('컬렉션                     export   sqlite')
    for key, (w, g) in shown.items():
        print(f'  {key:<24} {w:>6} {g:>6}{"" if w == g else "   <-- 다름"}')

    mismatched = 0
    for r in rows:
        want = store.encode(store.decode(json.dumps(r['data'], ensure_ascii=False)))
        got = store.get_raw(c, r['col'], r['id'])
        if got != want:
            mismatched += 1
            if mismatched <= 5:
                problems.append(f'doc {r["col"]}/{r["id"]} 내용 다름')
    print(f'문서 전수 대조: {len(rows) - mismatched}/{len(rows)} 일치')
    if mismatched:
        problems.append(f'내용 다른 문서 {mismatched}개')

    want_bal = _balances_from_rows(rows)
    db_rows = [{'col': col, 'data': store.decode(raw)}
               for col, raw in c.execute('SELECT col, data FROM docs WHERE col IN (?, ?, ?)',
                                         (*BALANCE_COLLECTIONS, 'credit_ledger'))]
    got_bal = _balances_from_rows(db_rows)
    for col, (n, total) in want_bal.items():
        gn, gt = got_bal[col]
        print(f'합계 {col}: export {n}건 {total} / sqlite {gn}건 {gt}')
        if (n, total) != (gn, gt):
            problems.append(f'합계 {col} 다름')

    if args.live:
        problems += _verify_live(store, rows, want_counts, want_bal, args.sample)

    if problems:
        print('불일치:')
        for p in problems:
            print('  -', p)
        raise SystemExit(1)
    print('전부 일치')


def _verify_live(store, rows, want_counts, want_bal, sample):
    """지금의 Firestore 가 export 와 같은지. 쓰기를 멈춘 뒤 돌려야 의미가 있다."""
    db = _firestore()
    problems = []
    for col, n in sorted(want_counts.items()):
        live_n = db.collection(col).count().get()[0][0].value
        if live_n != n:
            problems.append(f'live count {col}: firestore {live_n} != export {n}')
    print(f'live 문서 수: 컬렉션 {len(want_counts)}개 대조')

    live_rows = []
    for col in (*BALANCE_COLLECTIONS, 'credit_ledger'):
        live_rows += [{'col': col, 'data': d.to_dict()} for d in db.collection(col).stream()]
    for col, val in _balances_from_rows(live_rows).items():
        print(f'live 합계 {col}: {val[0]}건 {val[1]}')
        if val != want_bal[col]:
            problems.append(f'live 합계 {col}: firestore {val} != export {want_bal[col]}')

    picked = random.sample(rows, min(sample, len(rows)))
    same = 0
    for r in picked:
        snap = db.collection(r['col']).document(r['id']).get()
        live = store.encode(_plain(snap.to_dict() or {})) if snap.exists else None
        if live == store.get_raw(store.conn(), r['col'], r['id']):
            same += 1
        else:
            problems.append(f'live doc {r["col"]}/{r["id"]} 다름')
    print(f'live 무작위 문서: {same}/{len(picked)} 일치')
    return problems


def cmd_pushback(args):
    store = _store(args.db)
    _, rows = _read_export(args.src)
    frozen = {(r['col'], r['id']): store.encode(store.decode(json.dumps(r['data'], ensure_ascii=False)))
              for r in rows}
    now = {(col, doc_id): raw for col, doc_id, raw in store.conn().execute('SELECT col, id, data FROM docs')}
    upserts = [k for k, raw in now.items() if frozen.get(k) != raw]
    deletes = [k for k in frozen if k not in now]
    summary = {}
    for col, _ in upserts:
        summary.setdefault(col.split('/')[0], [0, 0])[0] += 1
    for col, _ in deletes:
        summary.setdefault(col.split('/')[0], [0, 0])[1] += 1
    print('컬렉션                 쓰기   지우기')
    for col, (u, d) in sorted(summary.items()):
        print(f'  {col:<20} {u:>6} {d:>6}')
    if not args.apply:
        print(f'쓰기 {len(upserts)} / 지우기 {len(deletes)} — 실제로 하려면 --apply')
        return
    db = _firestore()
    ops = [('set', k) for k in upserts] + [('delete', k) for k in deletes]
    for i in range(0, len(ops), 400):
        batch = db.batch()
        for op, (col, doc_id) in ops[i:i + 400]:
            ref = db.collection(col).document(doc_id)
            if op == 'set':
                batch.set(ref, store.decode(now[(col, doc_id)]))
            else:
                batch.delete(ref)
        batch.commit()
    print(f'Firestore 에 쓰기 {len(upserts)} / 지우기 {len(deletes)} 완료')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('export')
    p.add_argument('--out')
    p = sub.add_parser('import')
    p.add_argument('src')
    p.add_argument('--db')
    p = sub.add_parser('verify')
    p.add_argument('src')
    p.add_argument('--db')
    p.add_argument('--live', action='store_true')
    p.add_argument('--sample', type=int, default=30)
    p = sub.add_parser('pushback')
    p.add_argument('src')
    p.add_argument('--db', required=True)
    p.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    {'export': cmd_export, 'import': cmd_import, 'verify': cmd_verify, 'pushback': cmd_pushback}[args.cmd](args)


if __name__ == '__main__':
    main()

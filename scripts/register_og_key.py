#!/usr/bin/env python3
"""OpenGateway 키를 손으로 등록한다 — 대시보드 화면이 나오기 전까지 쓰는 임시 경로.

키를 인자로 받지 않는다. 명령줄에 적으면 셸 히스토리와 프로세스 목록에 그대로 남는다.
`getpass` 로 받으면 화면에도 안 찍힌다.

사용: `python3 scripts/register_og_key.py [디스코드_유저ID]`
      (ID 를 안 주면 .env 의 OWNER_ID 를 쓴다)
"""

import os
import sys
import asyncio
from getpass import getpass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run.core import config  # noqa: E402  (.env 를 읽어 준다)
from run.services import og_keys  # noqa: E402
from run.services.imagegen.gateway import verify_key  # noqa: E402


def main():
    user_id = sys.argv[1] if len(sys.argv) > 1 else (config.OWNER_ID or '')
    if not user_id:
        print('디스코드 유저 ID 를 주거나 .env 에 OWNER_ID 를 넣어 주세요.')
        return 1

    if not os.getenv('OG_KEY_SECRET'):
        print('OG_KEY_SECRET 이 없습니다. 봇 env 를 읽는 환경에서 실행하세요.')
        return 1

    print(f'등록 대상 디스코드 ID: {user_id}')
    key = getpass('OpenGateway 키를 붙여넣고 Enter (화면에 안 보입니다): ').strip()
    if not key:
        print('입력이 비었습니다.')
        return 1

    print('키를 확인하는 중...')
    ok, reason = asyncio.run(verify_key(key))
    if not ok:
        print(f'거절됐습니다 — {reason}')
        return 1

    res = og_keys.save_key(user_id, key)
    if not res.get('ok'):
        print(f'저장 실패: {res}')
        return 1

    st = og_keys.get_status(user_id)
    print(f"등록 완료. 키 ···{st.get('key_tail')} · 지금까지 {st.get('calls', 0)}장")
    print('이제 디스코드에서 /그림 을 쓸 수 있습니다.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

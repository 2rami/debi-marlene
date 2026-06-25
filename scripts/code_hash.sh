#!/bin/sh
# 봇 코드(run/ + main.py + requirements.txt)의 내용 해시.
# 이미지와 실행 중 컨테이너 양쪽에서 같은 값이 나와야 한다 → GHA deploy-bot 이
# "코드 같으면 배포 스킵"을 판정할 때 쓴다(deploy-quick 으로 cp 된 코드까지 반영).
#
# __pycache__/.pyc 는 런타임에 생성되므로 제외. 안 하면 갓 빌드한 이미지엔 없고
# 돌던 컨테이너엔 있어서 해시가 항상 달라진다. LC_ALL=C sort 로 순서 고정.
find /app/run /app/main.py /app/requirements.txt -type f \
  ! -name '*.pyc' ! -path '*/__pycache__/*' \
  -exec sha256sum {} + 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1

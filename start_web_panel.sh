#!/bin/bash

echo "🌐 데비&마를렌 웹 관리 패널"
echo "=================================="
echo ""

# 현재 디렉토리를 스크립트 위치로 변경
cd "$(dirname "$0")"

# 가상환경 활성화
if [ ! -d "web_venv" ]; then
    echo "❌ 가상환경이 없습니다. 패키지를 설치해주세요:"
    echo "   python3 -m venv web_venv"
    echo "   source web_venv/bin/activate"
    echo "   pip install flask flask-cors psutil"
    exit 1
fi

echo "🔧 가상환경 활성화 중..."
source web_venv/bin/activate

echo "🚀 웹 패널을 시작합니다..."
echo "📱 브라우저에서 http://localhost:8080 접속"
echo "⚠️  Discord 봇이 실행되어 있어야 모든 기능을 사용할 수 있습니다"
echo ""

# 환경변수 파일이 있으면 로드
if [ -f ".env" ]; then
    echo "🔐 환경변수 파일(.env)을 로드했습니다"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  .env 파일이 없습니다. 일부 기능이 제한될 수 있습니다."
fi

echo ""
echo "🔄 Ctrl+C로 중지할 수 있습니다"
echo ""

# 웹 패널 실행
python3 web_panel/web_panel.py
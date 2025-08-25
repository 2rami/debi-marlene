#!/usr/bin/env python3
"""
데비&마를렌 웹 관리 패널 실행 스크립트

봇과 별도로 웹 패널만 실행할 때 사용
봇이 실행 중이어야 모든 기능을 사용할 수 있음
"""

import os
import sys

def main():
    print("🌐 데비&마를렌 웹 관리 패널")
    print("=" * 50)
    print()
    
    # 환경 변수 체크
    if not os.getenv('DISCORD_TOKEN'):
        print("⚠️  경고: DISCORD_TOKEN 환경변수가 설정되지 않았습니다.")
        print("   봇 관련 기능이 제한될 수 있습니다.")
        print()
    
    # 봇 실행 여부 확인
    print("📋 실행 전 체크리스트:")
    print("  □ Discord 봇이 실행 중인가요?")
    print("  □ .env 파일에 필요한 환경변수가 설정되어 있나요?")
    print("  □ requirements.txt 패키지들이 설치되어 있나요?")
    print()
    
    response = input("계속하시겠습니까? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("실행을 취소했습니다.")
        return
    
    print()
    print("🚀 웹 패널을 시작합니다...")
    print("📱 브라우저에서 http://localhost:5000 접속")
    print("🔧 개발 모드로 실행 중 (파일 변경시 자동 재시작)")
    print("⚠️  운영 환경에서는 gunicorn 등을 사용하세요")
    print()
    
    try:
        from web_panel import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 웹 패널을 종료합니다.")
    except ImportError as e:
        print(f"❌ 모듈 import 오류: {e}")
        print("   pip install -r requirements.txt 명령어로 패키지를 설치해주세요.")
    except Exception as e:
        print(f"❌ 실행 오류: {e}")

if __name__ == "__main__":
    main()
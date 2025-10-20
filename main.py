#!/usr/bin/env python3
"""
데비&마를렌 디스코드 봇 - 메인 실행 파일
이터널리턴 전적 검색과 AI 채팅 기능을 제공하는 Discord 봇
"""

import sys
import os
import asyncio
import threading
import discord
from flask import Flask, jsonify, request

from run.core.bot import bot
from run.core import config
from run.commands import register_all_commands


# Flask 내부 API 서버 - 웹패널에서 봇 관리
app = Flask(__name__)


@app.route('/bot/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({"status": "healthy", "bot_ready": bot.is_ready()})


@app.route('/bot/create-dm', methods=['POST'])
def create_dm_channel():
    """웹패널에서 DM 채널 생성 요청"""
    if not bot.is_ready():
        return jsonify({"error": "Bot not ready"}), 503

    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id가 필요합니다"}), 400

    try:
        async def create_dm():
            """비동기로 DM 채널 생성"""
            try:
                # Discord에서 유저 가져오기
                user = await bot.fetch_user(int(user_id))

                # DM 채널 생성
                dm_channel = await user.create_dm()

                # GCS에 DM 채널 정보 저장
                config.save_dm_channel(user_id, dm_channel.id, user.name)

                print(f"✅ DM 채널 생성 성공: {user.name} (#{user_id})")

                return {
                    "success": True,
                    "channel": {
                        "id": str(dm_channel.id),
                        "type": 1,
                        "recipient": {
                            "id": str(user.id),
                            "username": user.name,
                            "discriminator": user.discriminator,
                            "avatar": f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png" if user.avatar else None
                        }
                    }
                }
            except discord.NotFound:
                return {"error": "사용자를 찾을 수 없습니다"}
            except discord.Forbidden:
                return {"error": "이 사용자는 DM을 차단했습니다"}
            except Exception as e:
                return {"error": f"DM 채널 생성 실패: {str(e)}"}

        # 비동기 함수 실행
        if bot.loop and not bot.loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(create_dm(), bot.loop)
            result = future.result(timeout=10)

            if "error" in result:
                return jsonify(result), 400
            else:
                return jsonify(result)
        else:
            return jsonify({"error": "Bot loop not available"}), 503

    except Exception as e:
        print(f"❌ DM 채널 생성 오류: {e}")
        return jsonify({"error": str(e)}), 500


def run_internal_api():
    """내부 API 서버 실행"""
    try:
        print("🔗 Flask 내부 API 서버 시작 (포트 5001)...")
        app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Flask 내부 API 서버 시작 실패: {e}")


async def setup():
    """봇 초기화 및 명령어 등록"""
    # 모든 명령어 등록
    await register_all_commands(bot)
    print("✅ 모든 명령어 등록 완료")


def run_bot():
    """Discord 봇 실행"""
    DISCORD_TOKEN = config.DISCORD_TOKEN

    if not DISCORD_TOKEN:
        print("CRITICAL: DISCORD_TOKEN이 설정되지 않았습니다.")
        return

    # Flask 내부 API 서버를 별도 스레드에서 실행
    api_thread = threading.Thread(target=run_internal_api, daemon=True)
    api_thread.start()
    print("📡 내부 API 서버 스레드가 시작되었습니다 (포트 5001)")

    # 명령어 등록
    asyncio.run(setup())

    # Discord 봇 실행
    bot.run(DISCORD_TOKEN)


def main():
    """메인 실행 함수"""
    print("🚀 데비&마를렌 봇을 시작합니다...", flush=True)
    sys.stdout.flush()
    print(f"🔧 환경변수 체크:", flush=True)
    sys.stdout.flush()
    print(f"  - DISCORD_TOKEN: {'설정됨' if os.getenv('DISCORD_TOKEN') else '없음'}", flush=True)
    sys.stdout.flush()
    print(f"  - YOUTUBE_API_KEY: {'설정됨' if os.getenv('YOUTUBE_API_KEY') else '없음'}", flush=True)
    sys.stdout.flush()
    print(f"  - YOUTUBE_API_KEY 길이: {len(os.getenv('YOUTUBE_API_KEY', ''))}", flush=True)
    sys.stdout.flush()

    # 봇 실행
    print("🔧 run_bot() 함수를 호출합니다...", flush=True)
    sys.stdout.flush()
    run_bot()


if __name__ == "__main__":
    main()
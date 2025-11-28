"""
GCS settings.json에서 tts_voice 설정을 삭제하는 스크립트
"""
import json
from run.core.config import load_settings, save_settings

def reset_tts_voice_settings():
    """모든 서버의 tts_voice 설정을 삭제합니다."""
    try:
        settings = load_settings()

        print("현재 설정:")
        print(json.dumps(settings, indent=2, ensure_ascii=False))

        # guilds 설정에서 tts_voice 삭제
        if "guilds" in settings:
            for guild_id, guild_settings in settings["guilds"].items():
                if "tts_voice" in guild_settings:
                    print(f"\n서버 {guild_id}의 tts_voice 설정 삭제: {guild_settings['tts_voice']}")
                    del guild_settings["tts_voice"]

        # 저장
        save_settings(settings)
        print("\n설정이 업데이트되었습니다!")

        # 업데이트된 설정 확인
        updated_settings = load_settings()
        print("\n업데이트된 설정:")
        print(json.dumps(updated_settings, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_tts_voice_settings()

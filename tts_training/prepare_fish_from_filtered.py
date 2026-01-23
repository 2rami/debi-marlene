import json
import os
import shutil

# 이미 정제된 데이터 사용
INPUT_FILE = "cosyvoice_data/filtered_transcripts.json"
OUTPUT_DIR = "fish_speech_data"

# 기존 폴더 삭제 후 재생성
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    char_dir = os.path.join(OUTPUT_DIR, item["character"])
    os.makedirs(char_dir, exist_ok=True)

    # 음성 복사
    dest = os.path.join(char_dir, item["file"])
    if os.path.exists(item["path"]):
        shutil.copy2(item["path"], dest)

    # .lab 파일 생성
    lab = os.path.join(char_dir, os.path.splitext(item["file"])[0] + ".lab")
    with open(lab, "w", encoding="utf-8") as f:
        f.write(item["text"])

print(f"완료! {len(data)}개 파일")

"""
Discord 애플리케이션 이모지 생성 및 업로드 스크립트

흰색 UI 아이콘을 생성하고 Discord API로 업로드합니다.
"""

import base64
import io
import json
import os
import requests
from PIL import Image, ImageDraw

# Discord API 설정
BOT_TOKEN = os.environ["DISCORD_TOKEN"]
APP_ID = "1393529860793831489"
API_URL = f"https://discord.com/api/v10/applications/{APP_ID}/emojis"

SIZE = 128
WHITE = (255, 255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)


def new_canvas():
    return Image.new("RGBA", (SIZE, SIZE), TRANSPARENT)


def draw_settings():
    """톱니바퀴 아이콘"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    cx, cy = SIZE // 2, SIZE // 2

    # 바깥 톱니바퀴 (12개 톱니)
    import math
    outer_r = 52
    inner_r = 38
    tooth_count = 8
    points = []
    for i in range(tooth_count * 2):
        angle = math.pi * 2 * i / (tooth_count * 2) - math.pi / 2
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=WHITE)

    # 가운데 구멍
    hole_r = 18
    draw.ellipse([cx - hole_r, cy - hole_r, cx + hole_r, cy + hole_r], fill=TRANSPARENT)

    return img


def draw_dashboard():
    """대시보드/홈 아이콘"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    cx, cy = SIZE // 2, SIZE // 2

    # 지붕 (삼각형)
    draw.polygon([(cx, 18), (18, 62), (110, 62)], fill=WHITE)

    # 집 본체
    draw.rectangle([28, 58, 100, 108], fill=WHITE)

    # 문 (구멍)
    draw.rectangle([50, 72, 78, 108], fill=TRANSPARENT)

    return img


def draw_play():
    """재생 아이콘 (삼각형)"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    draw.polygon([(36, 20), (36, 108), (104, 64)], fill=WHITE)
    return img


def draw_pause():
    """일시정지 아이콘 (두 막대)"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    bar_w = 22
    draw.rounded_rectangle([30, 22, 30 + bar_w, 106], radius=6, fill=WHITE)
    draw.rounded_rectangle([76, 22, 76 + bar_w, 106], radius=6, fill=WHITE)
    return img


def draw_skip():
    """스킵 아이콘 (삼각형 + 막대)"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    # 삼각형
    draw.polygon([(24, 20), (24, 108), (82, 64)], fill=WHITE)
    # 막대
    draw.rounded_rectangle([86, 22, 104, 106], radius=4, fill=WHITE)
    return img


def draw_previous():
    """이전 아이콘 (막대 + 역삼각형)"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    # 막대
    draw.rounded_rectangle([24, 22, 42, 106], radius=4, fill=WHITE)
    # 역삼각형
    draw.polygon([(104, 20), (104, 108), (46, 64)], fill=WHITE)
    return img


def draw_stop():
    """정지 아이콘 (사각형)"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([26, 26, 102, 102], radius=10, fill=WHITE)
    return img


ICONS = {
    "ui_settings": draw_settings,
    "ui_dashboard": draw_dashboard,
    "ui_play": draw_play,
    "ui_pause": draw_pause,
    "ui_skip": draw_skip,
    "ui_previous": draw_previous,
    "ui_stop": draw_stop,
}


def image_to_data_uri(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def upload_emoji(name: str, img: Image.Image):
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "name": name,
        "image": image_to_data_uri(img),
    }
    resp = requests.post(API_URL, headers=headers, json=payload)
    if resp.status_code == 201:
        data = resp.json()
        print(f"  [OK] {name} -> ID: {data['id']}")
        return data
    else:
        print(f"  [FAIL] {name}: {resp.status_code} {resp.text[:200]}")
        return None


def main():
    print("UI 아이콘 생성 및 업로드 시작")
    print(f"앱 ID: {APP_ID}")
    print()

    results = {}
    for name, draw_fn in ICONS.items():
        img = draw_fn()
        # 로컬에도 저장 (확인용)
        img.save(f"scripts/{name}.png")
        print(f"생성: {name}.png")

        result = upload_emoji(name, img)
        if result:
            results[name] = result["id"]

    print()
    print("=== 업로드 완료 ===")
    print("코드에서 사용할 이모지 ID:")
    for name, emoji_id in results.items():
        print(f'  "{name}": {emoji_id},')

    # 결과를 JSON으로 저장
    with open("scripts/emoji_ids.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nscripts/emoji_ids.json에 저장됨")


if __name__ == "__main__":
    main()

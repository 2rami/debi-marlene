from PIL import Image, ImageDraw, ImageFont
import requests
import io
import base64
from datetime import datetime
import urllib.parse
import os

try:
    import cairosvg
    SVG_SUPPORT = True
except ImportError:
    SVG_SUPPORT = False

def download_image(url, size=None):
    """URL에서 이미지를 다운로드하고 PIL Image로 변환"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://dak.gg/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8,image/svg+xml'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            if url.lower().endswith('.svg') and SVG_SUPPORT:
                png_data = cairosvg.svg2png(bytestring=response.content,
                                          output_width=size[0] if size else None,
                                          output_height=size[1] if size else None)
                img = Image.open(io.BytesIO(png_data))
            else:
                img = Image.open(io.BytesIO(response.content))
                if size:
                    img = img.resize(size, Image.Resampling.LANCZOS)
            return img
    except Exception as e:
        print(f"이미지 다운로드 실패 ({url}): {e}")
    return None

def get_korean_font():
    """기존 작동하던 폰트 사용"""
    font_paths = [
        '/Users/kasa/Desktop/모묘모/font/HGGGothicssi/HGGGothicssi_Pro_60g.otf',
        '/Users/kasa/Desktop/모묘모/font/HGGGothicssi/HGGGothicssi_Pro_99g.otf',
        '/Users/kasa/Desktop/모묘모/font/HGGGothicssi/HGGGothicssi_Pro_20g.otf',
        '/System/Library/Fonts/AppleSDGothicNeo.ttc',
    ]
    
    fonts = {}
    sizes = {
        'title': 24,
        'large': 20,
        'normal': 16,
        'small': 14,
        'tiny': 12
    }
    
    for name, size in sizes.items():
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    if font_path.endswith('.ttc'):
                        fonts[name] = ImageFont.truetype(font_path, size, index=0)
                    else:
                        fonts[name] = ImageFont.truetype(font_path, size)
                    break
            except Exception as e:
                continue
        if name not in fonts:
            fonts[name] = ImageFont.load_default()
    
    return fonts

def get_item_background_color(item_code):
    """아이템 코드에서 등급별 배경 색상 반환"""
    # 아이템 등급별 색상 (DAK.GG 기준)
    grade_colors = {
        1: (139, 139, 139),  # 회색 (Common)
        2: (34, 139, 34),    # 초록 (Uncommon)  
        3: (30, 144, 255),   # 파랑 (Rare)
        4: (138, 43, 226),   # 보라 (Epic)
        5: (255, 140, 0),    # 주황 (Legendary)
    }
    
    # 아이템 코드로 등급 추정 (간단한 방법)
    if not item_code:
        return (100, 100, 100)  # 기본 회색
        
    try:
        # 코드의 마지막 두 자리로 등급 추정
        last_digits = int(str(item_code)[-2:])
        if last_digits >= 1 and last_digits <= 10:
            return grade_colors.get(1, (139, 139, 139))
        elif last_digits >= 11 and last_digits <= 30:
            return grade_colors.get(2, (34, 139, 34))
        elif last_digits >= 31 and last_digits <= 50:
            return grade_colors.get(3, (30, 144, 255))
        elif last_digits >= 51 and last_digits <= 80:
            return grade_colors.get(4, (138, 43, 226))
        else:
            return grade_colors.get(5, (255, 140, 0))
    except:
        return (139, 139, 139)

def create_recent_games_image(recent_games, nickname="플레이어", game_mode_text="랭크게임", tier_info=None, tier_image_url=None, game_details_list=None):
    """HTML 구조를 참고한 최근전적 이미지 생성"""
    if not recent_games:
        return None
    
    # 기본 설정
    games_to_show = min(len(recent_games), 5)
    card_width = 1200
    card_height = 150
    margin = 10
    header_height = 60
    
    total_height = header_height + (games_to_show * (card_height + margin)) + margin
    
    # 배경 이미지 생성
    img = Image.new('RGB', (card_width, total_height), color=(47, 49, 54))
    draw = ImageDraw.Draw(img)
    
    fonts = get_korean_font()
    
    # 헤더 그리기
    draw.text((20, 15), f"{nickname}님의 최근전적", font=fonts['title'], fill=(255, 255, 255))
    draw.text((card_width - 150, 15), f"[{game_mode_text}]", font=fonts['normal'], fill=(156, 163, 175))
    
    # 각 게임 카드 그리기
    for i, game in enumerate(recent_games[:games_to_show]):
        y = header_height + i * (card_height + margin)
        
        # 카드 배경
        card_bg_color = (54, 57, 63)  # Discord 카드 색상
        draw.rectangle([margin, y, card_width - margin, y + card_height], fill=card_bg_color)
        
        # 게임 정보 추출
        rank = game.get('gameRank', 0)
        character_name = game.get('characterName', '알 수 없음')
        character_code = game.get('characterNum', 0)
        level = game.get('characterLevel', 1)
        weapon_type = game.get('weaponType', '')
        
        # 킬/데스/어시스트
        team_kills = game.get('teamKill', 0)
        kills = game.get('playerKill', 0) 
        assists = game.get('playerAssistant', 0)
        damage = game.get('damageToPlayer', 0)
        
        # 특성과 스킬
        mastery_info = game.get('mastery', [])
        route_id = game.get('routeIdOfStart', '')
        
        # 아이템 정보
        equipment = game.get('equipment', [])
        
        # 날씨 정보
        weather_info = game.get('weather', '')
        
        # 팀원 정보 (game_details_list에서)
        teammates_info = ""
        if game_details_list and i < len(game_details_list) and game_details_list[i]:
            teammates = game_details_list[i]  # 이미 팀원 목록임
            if isinstance(teammates, list) and teammates:
                teammates_info = ", ".join(teammates[:3])  # 최대 3명만
        
        # 왼쪽: 캐릭터 정보
        x_pos = 20
        
        # 캐릭터 이미지 (시뮬레이션)
        char_img_url = f"https://cdn.dak.gg/assets/er/game-assets/8.4.0/CharProfile_{character_name}_S002.png"
        char_img = download_image(char_img_url, size=(80, 80))
        if char_img:
            img.paste(char_img, (x_pos, y + 10))
        
        # 캐릭터 레벨
        draw.text((x_pos + 60, y + 70), str(level), font=fonts['small'], fill=(255, 255, 255))
        
        x_pos += 100
        
        # 캐릭터 이름
        draw.text((x_pos, y + 15), character_name, font=fonts['large'], fill=(255, 255, 255))
        
        # 무기 + 특성 + 전술스킬 영역
        x_pos += 120
        
        # 무기 이미지
        weapon_img_url = f"https://cdn.dak.gg/assets/er/game-assets/8.4.0/Ico_Ability_{weapon_type}.png"
        weapon_img = download_image(weapon_img_url, size=(30, 30))
        if weapon_img:
            img.paste(weapon_img, (x_pos, y + 20))
        
        # 특성들 표시 (mastery 정보 활용)
        mastery_x = x_pos + 40
        if mastery_info:
            for idx, mastery in enumerate(mastery_info[:3]):  # 최대 3개
                if isinstance(mastery, dict):
                    mastery_code = mastery.get('type', 0)
                    mastery_img_url = f"https://cdn.dak.gg/assets/er/game-assets/8.4.0/TraitSkillIcon_{mastery_code}.png"
                    mastery_img = download_image(mastery_img_url, size=(25, 25))
                    if mastery_img:
                        img.paste(mastery_img, (mastery_x + idx * 30, y + 22))
        
        x_pos += 150
        
        # 전투 스탯 영역
        kda_text = f"{team_kills}/{kills}/{assists}"
        draw.text((x_pos, y + 15), kda_text, font=fonts['normal'], fill=(255, 255, 255))
        draw.text((x_pos, y + 35), "TK / K / A", font=fonts['tiny'], fill=(156, 163, 175))
        
        damage_text = f"{damage:,}"
        draw.text((x_pos, y + 55), damage_text, font=fonts['normal'], fill=(255, 255, 255))
        draw.text((x_pos, y + 75), "딜량", font=fonts['tiny'], fill=(156, 163, 175))
        
        x_pos += 120
        
        # 순위
        rank_text = f"#{rank}"
        rank_color = (34, 197, 94) if rank <= 3 else (156, 163, 175)
        draw.text((x_pos, y + 25), rank_text, font=fonts['large'], fill=rank_color)
        
        x_pos += 60
        
        # 아이템 영역 (HTML 구조 참고)
        item_start_x = x_pos
        for idx, item in enumerate(equipment[:5]):  # 최대 5개 아이템
            item_x = item_start_x + idx * 45
            
            # 아이템 배경 (등급별 색상)
            item_code = item.get('itemCode', 0) if isinstance(item, dict) else item
            bg_color = get_item_background_color(item_code)
            
            # 배경 사각형
            draw.rectangle([item_x, y + 20, item_x + 40, y + 60], fill=bg_color)
            
            # 아이템 이미지
            if item_code:
                item_img_url = f"https://cdn.dak.gg/assets/er/game-assets/8.4.0/ItemIcon_{item_code}.png"
                item_img = download_image(item_img_url, size=(35, 35))
                if item_img:
                    img.paste(item_img, (item_x + 2, y + 22))
        
        # 맨 오른쪽: 팀원 정보
        if teammates_info:
            teammate_x = card_width - 200
            draw.text((teammate_x, y + 25), "팀원:", font=fonts['tiny'], fill=(156, 163, 175))
            draw.text((teammate_x, y + 40), teammates_info, font=fonts['small'], fill=(255, 255, 255))
        
        # 날씨 정보 (작게)
        if weather_info:
            draw.text((20, y + 110), f"날씨: {weather_info}", font=fonts['tiny'], fill=(156, 163, 175))
        
        # 루트 ID
        if route_id:
            draw.text((120, y + 110), f"루트: {route_id}", font=fonts['tiny'], fill=(156, 163, 175))
    
    return img

def encode_image_to_base64(img):
    """PIL 이미지를 Base64로 인코딩"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', optimize=True)
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()

def save_recent_games_image_to_file(recent_games, nickname="플레이어", game_mode_text="랭크게임", tier_info=None, tier_image_url=None, game_details_list=None, filepath="recent_games.png"):
    """최근전적 이미지를 파일로 저장"""
    img = create_recent_games_image(recent_games, nickname, game_mode_text, tier_info, tier_image_url, game_details_list)
    if img:
        img.save(filepath)
        return filepath
    return None

def save_union_image_to_file(union_data, nickname="플레이어", filepath="union_info.png"):
    """유니온 이미지를 파일로 저장 (빈 구현)"""
    # 유니온 이미지는 embed로 대체되었으므로 빈 구현
    return None
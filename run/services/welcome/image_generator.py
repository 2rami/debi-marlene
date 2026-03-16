"""
환영/작별 이미지 생성기

대시보드 CSS 프리뷰와 동일한 디자인:
- 배경 이미지 (cover) + 그라데이션 오버레이
- 원형 아바타 + 흰색 테두리
- 타이틀 텍스트 (볼드, 그림자)
- 서브타이틀 (pill 배경)
- 멤버 수 표시
- 하단 좌측 태그들
"""

import io
import os
import logging
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 500

# 새 포맷 기본값 (대시보드 CSS 프리뷰 기준)
DEFAULT_CONFIG = {
    'background_color': '#1a1a2e',
    'avatar': {'shape': 'circle', 'enabled': True},
    'welcome_title': 'Welcome, {user}',
    'welcome_subtitle': '{server}에 오신 것을 환영합니다!',
    'tags': [],
    'member_count': {'enabled': True},
}


class WelcomeImageGenerator:
    """환영/작별 이미지 생성기"""

    def __init__(self):
        self._font_cache: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}
        self._default_font_path = None
        self._bold_font_path = None
        self._load_default_font()

    # ------------------------------------------------------------------
    # 폰트
    # ------------------------------------------------------------------

    def _load_default_font(self):
        """기본 폰트 로드"""
        font_paths = [
            '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf',
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',
            'C:\\Windows\\Fonts\\malgunbd.ttf',
            'C:\\Windows\\Fonts\\malgun.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ]
        bold_paths = [
            '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf',
            'C:\\Windows\\Fonts\\malgunbd.ttf',
        ]

        for path in bold_paths:
            try:
                ImageFont.truetype(path, 32)
                self._bold_font_path = path
                break
            except (OSError, IOError):
                continue

        for path in font_paths:
            try:
                ImageFont.truetype(path, 32)
                self._default_font_path = path
                logger.info(f"[Welcome] 폰트 로드 성공: {path}")
                return
            except (OSError, IOError):
                continue

        logger.warning("[Welcome] 한글 폰트를 찾을 수 없습니다. 기본 폰트 사용")
        self._default_font_path = None

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """폰트 캐싱"""
        path = (self._bold_font_path if bold and self._bold_font_path else self._default_font_path)
        key = (path, size)
        if key not in self._font_cache:
            if path:
                self._font_cache[key] = ImageFont.truetype(path, size)
            else:
                self._font_cache[key] = ImageFont.load_default()
        return self._font_cache[key]

    # ------------------------------------------------------------------
    # 유틸리티
    # ------------------------------------------------------------------

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """HEX 색상을 RGB 튜플로 변환"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def _create_circle_mask(self, size: int) -> Image.Image:
        """원형 마스크 생성 (안티앨리어싱)"""
        scale = 4
        big = Image.new('L', (size * scale, size * scale), 0)
        ImageDraw.Draw(big).ellipse((0, 0, size * scale, size * scale), fill=255)
        return big.resize((size, size), Image.Resampling.LANCZOS)

    async def _download_image(self, url: str) -> Optional[Image.Image]:
        """URL에서 이미지 다운로드"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.read()
                        return Image.open(io.BytesIO(data)).convert('RGBA')
        except Exception as e:
            logger.error(f"[Welcome] 이미지 다운로드 실패: {e}")
        return None

    def _replace_variables(self, text: str, user_name: str, server_name: str, member_count: int) -> str:
        """텍스트 내 변수 치환"""
        return (
            text
            .replace('{user}', user_name)
            .replace('{server}', server_name)
            .replace('{membercount}', str(member_count))
        )

    # ------------------------------------------------------------------
    # 설정 변환 (구 포맷 -> 새 포맷 호환)
    # ------------------------------------------------------------------

    def _normalize_config(self, config: Optional[Dict[str, Any]], is_welcome: bool, server_name: str) -> Dict[str, Any]:
        """구 포맷과 새 포맷 모두 지원하도록 정규화"""
        cfg = {**DEFAULT_CONFIG}

        if not config:
            if not is_welcome:
                cfg['welcome_title'] = 'Goodbye, {user}'
                cfg['welcome_subtitle'] = '{server}에서 떠났습니다'
            return cfg

        # 새 포맷 감지: welcome_title 키가 있으면 새 포맷
        if 'welcome_title' in config or 'welcome_subtitle' in config or 'tags' in config:
            for key, value in config.items():
                if isinstance(value, dict) and key in cfg and isinstance(cfg[key], dict):
                    cfg[key] = {**cfg[key], **value}
                else:
                    cfg[key] = value
            return cfg

        # 구 포맷 변환
        if 'background_color' in config:
            cfg['background_color'] = config['background_color']

        if 'avatar' in config:
            old_av = config['avatar']
            cfg['avatar'] = {**cfg['avatar'], **old_av}

        # 구 포맷의 username -> welcome_title
        if 'username' in config:
            cfg['_old_username'] = config['username']

        # 구 포맷의 welcome_text -> welcome_subtitle
        if 'welcome_text' in config:
            cfg['_old_welcome_text'] = config['welcome_text']

        if 'custom_welcome_text' in config:
            cfg['welcome_subtitle'] = config['custom_welcome_text']
        elif 'custom_goodbye_text' in config and not is_welcome:
            cfg['welcome_subtitle'] = config['custom_goodbye_text']

        if 'member_count' in config:
            old_mc = config['member_count']
            if isinstance(old_mc, dict):
                cfg['member_count'] = {**cfg['member_count'], **old_mc}

        if not is_welcome:
            if 'welcome_title' not in config:
                cfg['welcome_title'] = 'Goodbye, {user}'
            if 'welcome_subtitle' not in config and 'custom_goodbye_text' not in config:
                cfg['welcome_subtitle'] = '{server}에서 떠났습니다'

        return cfg

    # ------------------------------------------------------------------
    # 드로잉 헬퍼
    # ------------------------------------------------------------------

    def _draw_rounded_rect(self, draw: ImageDraw.Draw, xy: Tuple[int, int, int, int],
                           fill: Tuple[int, ...], radius: int):
        """둥근 사각형 그리기"""
        draw.rounded_rectangle(xy, radius=radius, fill=fill)

    def _text_bbox(self, draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        """텍스트의 (width, height) 반환"""
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    # ------------------------------------------------------------------
    # 배경 생성
    # ------------------------------------------------------------------

    def _load_default_bg(self) -> Optional[bytes]:
        """기본 배경 이미지 로드"""
        default_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'images', 'default_welcome_bg.jpg'),
            '/app/run/assets/images/default_welcome_bg.jpg',
        ]
        for path in default_paths:
            try:
                with open(path, 'rb') as f:
                    return f.read()
            except (OSError, IOError):
                continue
        return None

    def _create_background(self, background_image: Optional[bytes], bg_color: str) -> Image.Image:
        """배경 이미지 생성 (cover 모드 + 오버레이)"""
        bg_rgb = self._hex_to_rgb(bg_color)

        # 배경 이미지가 없으면 기본 이미지 사용
        if not background_image:
            background_image = self._load_default_bg()

        if background_image:
            try:
                src = Image.open(io.BytesIO(background_image)).convert('RGBA')

                # Cover 모드: 비율 유지하면서 꽉 채우기
                src_ratio = src.width / src.height
                target_ratio = DEFAULT_WIDTH / DEFAULT_HEIGHT
                if src_ratio > target_ratio:
                    new_height = DEFAULT_HEIGHT
                    new_width = int(new_height * src_ratio)
                else:
                    new_width = DEFAULT_WIDTH
                    new_height = int(new_width / src_ratio)

                src = src.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # 중앙 크롭
                x = (new_width - DEFAULT_WIDTH) // 2
                y = (new_height - DEFAULT_HEIGHT) // 2
                src = src.crop((x, y, x + DEFAULT_WIDTH, y + DEFAULT_HEIGHT))

                img = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), bg_rgb)
                img.paste(src, (0, 0), src if src.mode == 'RGBA' else None)
            except Exception as e:
                logger.error(f"[Welcome] 배경 이미지 로드 실패: {e}")
                img = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), bg_rgb)
        else:
            img = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), bg_rgb)

        # 반투명 어두운 오버레이 (alpha ~80)
        dark_overlay = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), (0, 0, 0, 80))
        img = Image.alpha_composite(img, dark_overlay)

        # 하단->상단 그라데이션 오버레이
        gradient = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), (0, 0, 0, 0))
        for y in range(DEFAULT_HEIGHT):
            # 상단: alpha ~50, 하단: alpha ~200
            alpha = int(50 + (200 - 50) * (y / DEFAULT_HEIGHT))
            for x in range(DEFAULT_WIDTH):
                gradient.putpixel((x, y), (0, 0, 0, alpha))
        img = Image.alpha_composite(img, gradient)

        return img

    def _create_gradient_overlay(self) -> Image.Image:
        """효율적인 그라데이션 오버레이 생성 (1px 너비 -> 확대)"""
        # 1px 너비의 그라데이션을 만들고 가로로 확대 (성능 최적화)
        col = Image.new('RGBA', (1, DEFAULT_HEIGHT), (0, 0, 0, 0))
        for y in range(DEFAULT_HEIGHT):
            alpha = int(50 + 150 * (y / DEFAULT_HEIGHT))
            col.putpixel((0, y), (0, 0, 0, alpha))
        return col.resize((DEFAULT_WIDTH, DEFAULT_HEIGHT), Image.Resampling.NEAREST)

    # ------------------------------------------------------------------
    # 메인 생성
    # ------------------------------------------------------------------

    async def generate(
        self,
        user_name: str,
        user_avatar_url: str,
        server_name: str,
        member_count: int,
        is_welcome: bool = True,
        config: Optional[Dict[str, Any]] = None,
        background_image: Optional[bytes] = None,
    ) -> bytes:
        """
        환영/작별 이미지 생성

        Args:
            user_name: 유저 이름
            user_avatar_url: 유저 아바타 URL
            server_name: 서버 이름
            member_count: 멤버 수
            is_welcome: True=환영, False=작별
            config: 커스텀 설정 (구 포맷/새 포맷 모두 지원)
            background_image: 커스텀 배경 이미지 바이트 (없으면 단색 배경)

        Returns:
            PNG 이미지 바이트
        """
        cfg = self._normalize_config(config, is_welcome, server_name)

        # --- 배경 ---
        bg_color = cfg.get('background_color', '#1a1a2e')

        if background_image:
            try:
                src = Image.open(io.BytesIO(background_image)).convert('RGBA')
                src_ratio = src.width / src.height
                target_ratio = DEFAULT_WIDTH / DEFAULT_HEIGHT
                if src_ratio > target_ratio:
                    new_h = DEFAULT_HEIGHT
                    new_w = int(new_h * src_ratio)
                else:
                    new_w = DEFAULT_WIDTH
                    new_h = int(new_w / src_ratio)
                src = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
                cx = (new_w - DEFAULT_WIDTH) // 2
                cy = (new_h - DEFAULT_HEIGHT) // 2
                src = src.crop((cx, cy, cx + DEFAULT_WIDTH, cy + DEFAULT_HEIGHT))
                img = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), self._hex_to_rgb(bg_color))
                img.paste(src, (0, 0), src if src.mode == 'RGBA' else None)
            except Exception as e:
                logger.error(f"[Welcome] 배경 이미지 로드 실패: {e}")
                img = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), self._hex_to_rgb(bg_color))
        else:
            img = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), self._hex_to_rgb(bg_color))

        # 반투명 어두운 오버레이 (alpha ~80)
        dark_overlay = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), (0, 0, 0, 80))
        img = Image.alpha_composite(img, dark_overlay)

        # 그라데이션 오버레이 (상단 alpha~50 -> 하단 alpha~200)
        gradient = self._create_gradient_overlay()
        img = Image.alpha_composite(img, gradient)

        draw = ImageDraw.Draw(img)

        # --- 변수 치환 ---
        title_text = self._replace_variables(
            cfg.get('welcome_title', 'Welcome, {user}'), user_name, server_name, member_count
        )
        subtitle_text = self._replace_variables(
            cfg.get('welcome_subtitle', ''), user_name, server_name, member_count
        )

        # --- 컨텐츠 수직 중앙 배치 계산 ---
        avatar_enabled = cfg.get('avatar', {}).get('enabled', True)
        avatar_size = 200
        border_width = 4
        member_enabled = cfg.get('member_count', {}).get('enabled', True)
        tags = cfg.get('tags', [])

        # 각 요소 높이 계산
        spacing = 20
        total_h = 0
        if avatar_enabled:
            total_h += avatar_size + border_width * 2 + spacing
        title_font = self._get_font(48, bold=True)
        subtitle_font = self._get_font(28)
        member_font = self._get_font(20)

        title_w, title_h = self._text_bbox(draw, title_text, title_font)
        total_h += title_h + spacing

        if subtitle_text:
            sub_w, sub_h = self._text_bbox(draw, subtitle_text, subtitle_font)
            total_h += sub_h + 24 + spacing  # 24 = pill padding

        if member_enabled:
            mc_text = f"#{member_count}번째 멤버" if is_welcome else f"현재 {member_count}명의 멤버"
            mc_w, mc_h = self._text_bbox(draw, mc_text, member_font)
            total_h += mc_h + spacing

        # 시작 y 위치 (수직 중앙)
        start_y = (DEFAULT_HEIGHT - total_h) // 2
        current_y = start_y

        # --- 아바타 ---
        if avatar_enabled:
            avatar_img = await self._download_image(user_avatar_url)
            if avatar_img:
                avatar_img = avatar_img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)

                shape = cfg.get('avatar', {}).get('shape', 'circle')

                bordered_size = avatar_size + border_width * 2
                border_canvas = Image.new('RGBA', (bordered_size, bordered_size), (0, 0, 0, 0))
                border_draw = ImageDraw.Draw(border_canvas)

                if shape == 'circle':
                    # 흰색 원형 테두리
                    scale = 4
                    big = Image.new('L', (bordered_size * scale, bordered_size * scale), 0)
                    ImageDraw.Draw(big).ellipse((0, 0, bordered_size * scale, bordered_size * scale), fill=255)
                    circle_mask = big.resize((bordered_size, bordered_size), Image.Resampling.LANCZOS)

                    white_circle = Image.new('RGBA', (bordered_size, bordered_size), (255, 255, 255, 255))
                    border_canvas.paste(white_circle, (0, 0), circle_mask)

                    # 아바타를 원형으로 크롭
                    mask = self._create_circle_mask(avatar_size)
                    avatar_cropped = Image.new('RGBA', (avatar_size, avatar_size), (0, 0, 0, 0))
                    avatar_cropped.paste(avatar_img, (0, 0), mask)
                    border_canvas.paste(avatar_cropped, (border_width, border_width), avatar_cropped)
                else:
                    # 사각형
                    border_canvas = Image.new('RGBA', (bordered_size, bordered_size), (255, 255, 255, 255))
                    border_canvas.paste(avatar_img, (border_width, border_width))

                ax = (DEFAULT_WIDTH - bordered_size) // 2
                ay = current_y
                img.paste(border_canvas, (ax, ay), border_canvas)
                current_y += bordered_size + spacing

                # draw 재생성 (paste 이후)
                draw = ImageDraw.Draw(img)

        # --- 타이틀 ---
        # 그림자
        shadow_offset = 2
        tx = (DEFAULT_WIDTH - title_w) // 2
        ty = current_y
        draw.text((tx + shadow_offset, ty + shadow_offset), title_text, font=title_font, fill=(0, 0, 0, 180))
        draw.text((tx, ty), title_text, font=title_font, fill=(255, 255, 255, 255))
        current_y += title_h + spacing

        # --- 서브타이틀 (pill 배경) ---
        if subtitle_text:
            sub_w, sub_h = self._text_bbox(draw, subtitle_text, subtitle_font)
            pill_pad_x = 24
            pill_pad_y = 10
            pill_w = sub_w + pill_pad_x * 2
            pill_h = sub_h + pill_pad_y * 2
            pill_x = (DEFAULT_WIDTH - pill_w) // 2
            pill_y = current_y

            # 반투명 pill (bg-white/10 = 약 alpha 30)
            pill_overlay = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), (0, 0, 0, 0))
            pill_draw = ImageDraw.Draw(pill_overlay)
            pill_draw.rounded_rectangle(
                (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
                radius=pill_h // 2,
                fill=(255, 255, 255, 30),
            )
            img = Image.alpha_composite(img, pill_overlay)
            draw = ImageDraw.Draw(img)

            # 서브타이틀 텍스트
            sx = (DEFAULT_WIDTH - sub_w) // 2
            sy = pill_y + pill_pad_y
            draw.text((sx, sy), subtitle_text, font=subtitle_font, fill=(220, 220, 220, 255))
            current_y += pill_h + spacing

        # --- 멤버 수 ---
        if member_enabled:
            mc_text = f"#{member_count}번째 멤버" if is_welcome else f"현재 {member_count}명의 멤버"
            mc_w, mc_h = self._text_bbox(draw, mc_text, member_font)
            mx = (DEFAULT_WIDTH - mc_w) // 2
            my = current_y
            draw.text((mx, my), mc_text, font=member_font, fill=(114, 137, 218, 255))  # Discord blurple
            current_y += mc_h + spacing

        # --- 하단 좌측 태그들 ---
        if tags:
            tag_font = self._get_font(14)
            tag_x = 24
            tag_y = DEFAULT_HEIGHT - 40

            for tag_text in tags:
                tw, th = self._text_bbox(draw, tag_text, tag_font)
                pad_x = 12
                pad_y = 6
                tag_w = tw + pad_x * 2
                tag_h = th + pad_y * 2

                # 반투명 pill 배경
                tag_overlay = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), (0, 0, 0, 0))
                tag_draw = ImageDraw.Draw(tag_overlay)
                tag_draw.rounded_rectangle(
                    (tag_x, tag_y, tag_x + tag_w, tag_y + tag_h),
                    radius=tag_h // 2,
                    fill=(255, 255, 255, 40),
                )
                img = Image.alpha_composite(img, tag_overlay)
                draw = ImageDraw.Draw(img)

                draw.text((tag_x + pad_x, tag_y + pad_y), tag_text, font=tag_font, fill=(200, 200, 200, 255))
                tag_x += tag_w + 8

        # --- PNG 출력 ---
        output = io.BytesIO()
        img = img.convert('RGB')
        img.save(output, format='PNG', quality=95)
        output.seek(0)
        return output.getvalue()

    async def generate_simple(
        self,
        user_name: str,
        user_avatar_url: str,
        server_name: str,
        member_count: int,
        is_welcome: bool = True,
    ) -> bytes:
        """간단한 기본 설정으로 이미지 생성"""
        return await self.generate(
            user_name=user_name,
            user_avatar_url=user_avatar_url,
            server_name=server_name,
            member_count=member_count,
            is_welcome=is_welcome,
        )

"""
환영/작별 이미지 생성기

ProBot 스타일의 커스텀 환영 이미지를 생성합니다.
- 배경 이미지 (커스텀 또는 기본)
- 유저 아바타 (원형/사각형/둥근사각형)
- 유저명, 서버명, 멤버수 텍스트
- 위치/크기/색상 커스터마이징
"""

import io
import logging
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# 기본 이미지 크기
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 500

# 기본 설정
DEFAULT_CONFIG = {
    # 배경
    'background_color': '#2C2F33',  # Discord 다크 테마
    'background_blur': 0,

    # 아바타
    'avatar': {
        'x': 512,  # 중앙
        'y': 180,
        'size': 200,
        'shape': 'circle',  # circle, square, rounded
        'border_color': '#FFFFFF',
        'border_width': 5,
    },

    # 유저명 텍스트
    'username': {
        'x': 512,
        'y': 320,
        'font_size': 48,
        'color': '#FFFFFF',
        'align': 'center',
        'shadow': True,
        'shadow_color': '#000000',
    },

    # 환영 텍스트
    'welcome_text': {
        'x': 512,
        'y': 390,
        'font_size': 32,
        'color': '#99AAB5',
        'align': 'center',
    },

    # 멤버 수 텍스트
    'member_count': {
        'x': 512,
        'y': 440,
        'font_size': 24,
        'color': '#7289DA',
        'align': 'center',
        'enabled': True,
    },
}


class WelcomeImageGenerator:
    """환영/작별 이미지 생성기"""

    def __init__(self):
        self._font_cache: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}
        self._default_font_path = None
        self._load_default_font()

    def _load_default_font(self):
        """기본 폰트 로드"""
        # 한글 지원 폰트 경로들
        font_paths = [
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',  # Linux
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',  # Linux
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',  # macOS
            '/System/Library/Fonts/Supplemental/AppleGothic.ttf',  # macOS
            'C:\\Windows\\Fonts\\malgun.ttf',  # Windows
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Fallback
        ]

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

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """폰트 캐싱"""
        key = (self._default_font_path, size)
        if key not in self._font_cache:
            if self._default_font_path:
                self._font_cache[key] = ImageFont.truetype(self._default_font_path, size)
            else:
                self._font_cache[key] = ImageFont.load_default()
        return self._font_cache[key]

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """HEX 색상을 RGB 튜플로 변환"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _create_circle_mask(self, size: int) -> Image.Image:
        """원형 마스크 생성"""
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        return mask

    def _create_rounded_mask(self, size: int, radius: int = 30) -> Image.Image:
        """둥근 사각형 마스크 생성"""
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
        return mask

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

    def _draw_text_with_shadow(
        self,
        draw: ImageDraw.Draw,
        text: str,
        position: Tuple[int, int],
        font: ImageFont.FreeTypeFont,
        color: str,
        shadow_color: str = '#000000',
        shadow_offset: int = 2,
    ):
        """그림자가 있는 텍스트 그리기"""
        x, y = position
        shadow_rgb = self._hex_to_rgb(shadow_color)
        text_rgb = self._hex_to_rgb(color)

        # 그림자
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_rgb)
        # 텍스트
        draw.text((x, y), text, font=font, fill=text_rgb)

    def _get_text_position(
        self,
        draw: ImageDraw.Draw,
        text: str,
        font: ImageFont.FreeTypeFont,
        config: Dict[str, Any],
    ) -> Tuple[int, int]:
        """텍스트 위치 계산 (정렬 고려)"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = config.get('x', 512)
        y = config.get('y', 200)
        align = config.get('align', 'center')

        if align == 'center':
            x = x - text_width // 2
        elif align == 'right':
            x = x - text_width

        return (x, y)

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
            config: 커스텀 설정 (없으면 기본값 사용)
            background_image: 커스텀 배경 이미지 바이트 (없으면 단색 배경)

        Returns:
            PNG 이미지 바이트
        """
        # 설정 병합
        cfg = {**DEFAULT_CONFIG}
        if config:
            for key, value in config.items():
                if isinstance(value, dict) and key in cfg:
                    cfg[key] = {**cfg[key], **value}
                else:
                    cfg[key] = value

        # 배경 이미지 생성
        if background_image:
            try:
                src_img = Image.open(io.BytesIO(background_image)).convert('RGBA')
                bg_cfg = cfg.get('background', {})
                fit_mode = bg_cfg.get('fit', 'cover')  # cover, fit, stretch
                scale = bg_cfg.get('scale', 100) / 100  # 100 = 원본
                offset_x = bg_cfg.get('offset_x', 0)
                offset_y = bg_cfg.get('offset_y', 0)

                img = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), self._hex_to_rgb(cfg['background_color']))

                if fit_mode == 'stretch':
                    # 늘리기 (기존 방식)
                    resized = src_img.resize((DEFAULT_WIDTH, DEFAULT_HEIGHT), Image.Resampling.LANCZOS)
                    img.paste(resized, (0, 0))
                elif fit_mode == 'fit':
                    # 비율 유지, 전체 보이게 (여백 생김)
                    src_ratio = src_img.width / src_img.height
                    target_ratio = DEFAULT_WIDTH / DEFAULT_HEIGHT
                    if src_ratio > target_ratio:
                        new_width = int(DEFAULT_WIDTH * scale)
                        new_height = int(new_width / src_ratio)
                    else:
                        new_height = int(DEFAULT_HEIGHT * scale)
                        new_width = int(new_height * src_ratio)
                    resized = src_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    x = (DEFAULT_WIDTH - new_width) // 2 + offset_x
                    y = (DEFAULT_HEIGHT - new_height) // 2 + offset_y
                    img.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)
                else:  # cover (기본값)
                    # 비율 유지, 꽉 채우기 (잘림)
                    src_ratio = src_img.width / src_img.height
                    target_ratio = DEFAULT_WIDTH / DEFAULT_HEIGHT
                    if src_ratio > target_ratio:
                        new_height = int(DEFAULT_HEIGHT * scale)
                        new_width = int(new_height * src_ratio)
                    else:
                        new_width = int(DEFAULT_WIDTH * scale)
                        new_height = int(new_width / src_ratio)
                    resized = src_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    x = (DEFAULT_WIDTH - new_width) // 2 + offset_x
                    y = (DEFAULT_HEIGHT - new_height) // 2 + offset_y
                    img.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)
            except Exception as e:
                logger.error(f"[Welcome] 배경 이미지 로드 실패: {e}")
                img = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), self._hex_to_rgb(cfg['background_color']))
        else:
            img = Image.new('RGBA', (DEFAULT_WIDTH, DEFAULT_HEIGHT), self._hex_to_rgb(cfg['background_color']))

        # 배경 블러
        if cfg.get('background_blur', 0) > 0:
            img = img.filter(ImageFilter.GaussianBlur(cfg['background_blur']))

        # 반투명 오버레이 (텍스트 가독성)
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 100))
        img = Image.alpha_composite(img, overlay)

        draw = ImageDraw.Draw(img)

        # 아바타 다운로드 및 그리기
        avatar_cfg = cfg['avatar']
        avatar = await self._download_image(user_avatar_url)

        if avatar:
            avatar_size = avatar_cfg.get('size', 200)
            avatar = avatar.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)

            # 아바타 모양 적용
            shape = avatar_cfg.get('shape', 'circle')
            if shape == 'circle':
                mask = self._create_circle_mask(avatar_size)
            elif shape == 'rounded':
                mask = self._create_rounded_mask(avatar_size)
            else:
                mask = None

            # 테두리
            border_width = avatar_cfg.get('border_width', 5)
            border_color = self._hex_to_rgb(avatar_cfg.get('border_color', '#FFFFFF'))

            if border_width > 0 and shape in ('circle', 'rounded'):
                border_size = avatar_size + border_width * 2
                border_img = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
                border_draw = ImageDraw.Draw(border_img)

                if shape == 'circle':
                    border_draw.ellipse((0, 0, border_size, border_size), fill=border_color)
                else:
                    border_draw.rounded_rectangle((0, 0, border_size, border_size), radius=35, fill=border_color)

                # 아바타 위치 계산
                avatar_x = avatar_cfg.get('x', 512) - border_size // 2
                avatar_y = avatar_cfg.get('y', 180) - border_size // 2

                img.paste(border_img, (avatar_x, avatar_y), border_img)

                # 아바타 붙이기
                avatar_paste_x = avatar_x + border_width
                avatar_paste_y = avatar_y + border_width

                if mask:
                    img.paste(avatar, (avatar_paste_x, avatar_paste_y), mask)
                else:
                    img.paste(avatar, (avatar_paste_x, avatar_paste_y))
            else:
                avatar_x = avatar_cfg.get('x', 512) - avatar_size // 2
                avatar_y = avatar_cfg.get('y', 180) - avatar_size // 2

                if mask:
                    img.paste(avatar, (avatar_x, avatar_y), mask)
                else:
                    img.paste(avatar, (avatar_x, avatar_y))

        # 유저명 그리기
        username_cfg = cfg['username']
        username_font = self._get_font(username_cfg.get('font_size', 48))
        username_pos = self._get_text_position(draw, user_name, username_font, username_cfg)

        if username_cfg.get('shadow', True):
            self._draw_text_with_shadow(
                draw, user_name, username_pos, username_font,
                username_cfg.get('color', '#FFFFFF'),
                username_cfg.get('shadow_color', '#000000')
            )
        else:
            draw.text(username_pos, user_name, font=username_font, fill=self._hex_to_rgb(username_cfg.get('color', '#FFFFFF')))

        # 환영/작별 텍스트 그리기
        welcome_cfg = cfg['welcome_text']
        welcome_font = self._get_font(welcome_cfg.get('font_size', 32))

        if is_welcome:
            welcome_text = f"{server_name}에 오신 것을 환영합니다!"
        else:
            welcome_text = f"{server_name}에서 떠났습니다"

        # 커스텀 텍스트가 있으면 사용
        if cfg.get('custom_welcome_text'):
            welcome_text = cfg['custom_welcome_text']
        elif cfg.get('custom_goodbye_text') and not is_welcome:
            welcome_text = cfg['custom_goodbye_text']

        welcome_pos = self._get_text_position(draw, welcome_text, welcome_font, welcome_cfg)
        draw.text(welcome_pos, welcome_text, font=welcome_font, fill=self._hex_to_rgb(welcome_cfg.get('color', '#99AAB5')))

        # 멤버 수 그리기
        member_cfg = cfg['member_count']
        if member_cfg.get('enabled', True):
            member_font = self._get_font(member_cfg.get('font_size', 24))

            if is_welcome:
                member_text = f"#{member_count}번째 멤버"
            else:
                member_text = f"현재 {member_count}명의 멤버"

            member_pos = self._get_text_position(draw, member_text, member_font, member_cfg)
            draw.text(member_pos, member_text, font=member_font, fill=self._hex_to_rgb(member_cfg.get('color', '#7289DA')))

        # PNG로 변환
        output = io.BytesIO()
        img = img.convert('RGB')  # PNG 저장을 위해 RGB로 변환
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

"""
쿠폰 크롤링 서비스

DCInside 갤러리 게시글에서 이터널리턴 쿠폰 목록을 크롤링하고,
설정된 Discord 채널에 스티키 메시지로 갱신합니다.
"""

import asyncio
import hashlib
import html
import re
from datetime import datetime, timedelta, timezone

import aiohttp
from discord.ext import tasks

from run.core import config

KST = timezone(timedelta(hours=9))

SOURCE_URL = "https://gall.dcinside.com/mgallery/board/view/?id=bser&no=9719379"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://gall.dcinside.com/mgallery/board/lists/?id=bser",
}


class CouponService:
    def __init__(self, bot):
        self.bot = bot
        self._last_hash = None

    async def fetch_coupons(self) -> list[dict]:
        """DC갤러리에서 쿠폰 목록을 크롤링합니다."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    SOURCE_URL,
                    headers=HEADERS,
                    timeout=aiohttp.ClientTimeout(total=20),
                ) as response:
                    if response.status != 200:
                        print(f"[쿠폰] HTTP {response.status}", flush=True)
                        return []
                    raw_html = await response.text()
        except Exception as e:
            print(f"[쿠폰] 페이지 요청 실패: {e}", flush=True)
            return []

        return self._parse_coupons(raw_html)

    def _parse_coupons(self, raw_html: str) -> list[dict]:
        """HTML에서 쿠폰 코드/보상/기한을 추출합니다."""
        # 게시글 본문 영역 추출
        body_match = re.search(
            r'<div\s+class="write_div"[^>]*>(.*?)</div>\s*(?:<div\s+class="btn_recommend|<div\s+class="s_write)',
            raw_html,
            re.DOTALL,
        )
        if not body_match:
            # 대체 패턴
            body_match = re.search(
                r'class="write_div"[^>]*>(.*?)</div>',
                raw_html,
                re.DOTALL,
            )
        if not body_match:
            print("[쿠폰] 게시글 본문을 찾을 수 없음", flush=True)
            return []

        body = body_match.group(1)

        # HTML 태그 제거하되 <br>을 줄바꿈으로 변환
        body = re.sub(r"<br\s*/?>", "\n", body, flags=re.IGNORECASE)
        body = re.sub(r"<[^>]+>", "", body)
        body = html.unescape(body)

        # 쿠폰 패턴 매칭
        # "쿠폰 코드 : XXX" / "쿠폰 보상 : YYY" / "쿠폰 기한 : ZZZ"
        code_pattern = re.compile(r"쿠폰\s*코드\s*[:：]\s*(.+)")
        reward_pattern = re.compile(r"쿠폰\s*보상\s*[:：]\s*(.+)")
        expiry_pattern = re.compile(r"쿠폰\s*기한\s*[:：]\s*(.+)")

        lines = body.split("\n")
        coupons = []
        current = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            code_m = code_pattern.search(line)
            reward_m = reward_pattern.search(line)
            expiry_m = expiry_pattern.search(line)

            if code_m:
                # 새 쿠폰 시작 - 이전 것 저장
                if current.get("code"):
                    coupons.append(current)
                current = {"code": code_m.group(1).strip(), "reward": "", "expiry": ""}
            elif reward_m and current.get("code"):
                current["reward"] = reward_m.group(1).strip()
            elif expiry_m and current.get("code"):
                current["expiry"] = expiry_m.group(1).strip()

        # 마지막 쿠폰 저장
        if current.get("code"):
            coupons.append(current)

        return coupons

    def format_coupon_message(self, coupons: list[dict]) -> str:
        """쿠폰 목록을 Discord 메시지 형식으로 포맷합니다."""
        now = datetime.now(KST).strftime("%Y-%m-%d %H:%M")

        lines = ["--- Eternal Return Coupon List ---", ""]

        for i, coupon in enumerate(coupons, 1):
            code = coupon.get("code", "???")
            reward = coupon.get("reward", "-")
            expiry = coupon.get("expiry", "-")

            lines.append(f"[{i}] {code}")
            lines.append(f"    {reward} | {expiry}")
            lines.append("")

        lines.append(f"Last updated: {now}")
        lines.append(f"Source: <{SOURCE_URL}>")

        return "\n".join(lines)

    async def update_sticky_messages(self, coupons: list[dict]):
        """쿠폰이 변경되면 모든 구독 채널에 알림 전송 + 고정 메시지 등록."""
        settings = await asyncio.to_thread(config.load_settings, True)
        content = self.format_coupon_message(coupons)

        changed = False

        for guild_id, guild_data in settings.get("guilds", {}).items():
            notif = guild_data.get("notification_settings", {})
            coupon_config = notif.get("coupon", {})

            if not coupon_config.get("enabled") or not coupon_config.get("channelId"):
                continue

            channel_id_str = str(coupon_config["channelId"])
            channel = self.bot.get_channel(int(channel_id_str))
            if not channel:
                continue

            # 이전 고정 메시지 삭제 (sticky_messages에서)
            sticky_messages = guild_data.get("sticky_messages", [])
            old_sticky = None
            for sm in sticky_messages:
                if sm.get("id") == f"coupon_{guild_id}":
                    old_sticky = sm
                    break

            if old_sticky and old_sticky.get("lastMessageId"):
                try:
                    old_msg = await channel.fetch_message(int(old_sticky["lastMessageId"]))
                    await old_msg.delete()
                except Exception:
                    pass

            # 새 메시지 전송 (알림 울리게 - 갱신 알림)
            try:
                new_msg = await channel.send(content)
            except Exception as e:
                print(f"[쿠폰] 메시지 전송 실패 ({guild_id}): {e}", flush=True)
                continue

            # sticky_messages에 등록/갱신 (이후 _handle_sticky_message가 고정 유지)
            new_sticky = {
                "id": f"coupon_{guild_id}",
                "channelId": channel_id_str,
                "channelName": getattr(channel, "name", ""),
                "content": content,
                "enabled": True,
                "lastMessageId": str(new_msg.id),
            }

            if old_sticky:
                idx = sticky_messages.index(old_sticky)
                sticky_messages[idx] = new_sticky
            else:
                if "sticky_messages" not in guild_data:
                    settings["guilds"][guild_id]["sticky_messages"] = []
                settings["guilds"][guild_id]["sticky_messages"].append(new_sticky)

            changed = True

        if changed:
            await asyncio.to_thread(config.save_settings, settings, True)

    async def check_coupons(self):
        """쿠폰 변경 확인 및 갱신"""
        try:
            coupons = await self.fetch_coupons()
            if not coupons:
                return

            # 해시로 변경 감지
            data_str = str(sorted([c["code"] for c in coupons]))
            current_hash = hashlib.md5(data_str.encode()).hexdigest()

            if current_hash == self._last_hash:
                return  # 변경 없음

            is_first_run = self._last_hash is None
            self._last_hash = current_hash

            # GCS에 쿠폰 데이터 저장
            settings = await asyncio.to_thread(config.load_settings, True)
            settings.setdefault("global", {})["coupons"] = coupons
            settings["global"]["coupons_hash"] = current_hash
            await asyncio.to_thread(config.save_settings, settings, True)

            # 첫 실행이어도 메시지가 없는 채널에는 전송
            if is_first_run:
                print(f"[쿠폰] 초기 실행 ({len(coupons)}개 쿠폰 감지)", flush=True)

            # 스티키 메시지 갱신
            await self.update_sticky_messages(coupons)
            print(f"[쿠폰] {len(coupons)}개 쿠폰 갱신 완료", flush=True)

        except Exception as e:
            print(f"[쿠폰] 체크 실패: {e}", flush=True)


# -- 전역 인스턴스 및 태스크 --

_coupon_service = None


@tasks.loop(minutes=30)
async def check_coupons_task():
    if _coupon_service:
        await _coupon_service.check_coupons()


def start_coupon_service(bot):
    """쿠폰 서비스를 초기화하고 태스크를 시작합니다."""
    global _coupon_service
    _coupon_service = CouponService(bot)

    # GCS에서 마지막 해시 복원
    settings = config.load_settings()
    _coupon_service._last_hash = settings.get("global", {}).get("coupons_hash")

    if not check_coupons_task.is_running():
        check_coupons_task.start()
    print("[완료] 쿠폰 서비스 시작 (30분 간격)", flush=True)

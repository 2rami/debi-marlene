"""
패치노트 알림 서비스

이터널리턴 공식 사이트의 패치노트를 주기적으로 확인하고,
새로운 패치노트가 있으면 설정된 채널에 알림을 보냅니다.
"""

import asyncio
from datetime import datetime, timedelta, timezone

import aiohttp
import discord
from discord.ext import tasks

KST = timezone(timedelta(hours=9))

from run.core import config

PATCHNOTE_LIST_URL = "https://playeternalreturn.com/posts/news?categoryPath=patchnote"
PATCHNOTE_BASE_URL = "https://playeternalreturn.com/posts/news"
DEBI_PRIMARY_COLOR = 0x00c7ce

bot_instance = None


def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot


class PatchNoteChecker:
    """패치노트 확인 및 알림 전송"""

    def __init__(self, bot):
        self.bot = bot
        set_bot_instance(bot)

    async def fetch_patchnotes(self):
        """공식 사이트에서 패치노트 목록을 가져옵니다."""
        import re

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "ko-KR,ko;q=0.9",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    PATCHNOTE_LIST_URL,
                    headers=headers,
                    allow_redirects=False,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as response:
                    if response.status != 200:
                        print(f"[패치노트] HTTP {response.status}", flush=True)
                        return []

                    html = await response.text()

                    # er-article 블록에서 링크 + 제목 + 설명 추출
                    pattern = re.compile(
                        r'href="[^"]*?/posts/news/(\d+)"[^>]*>.*?'
                        r'er-article__title">([^<]+)</h4>.*?'
                        r'er-article__description">([^<]*)</p>',
                        re.DOTALL,
                    )

                    posts = []
                    for match in pattern.finditer(html):
                        post_id, title, description = match.groups()
                        posts.append({
                            "id": post_id,
                            "title": title.strip(),
                            "description": description.strip(),
                            "url": f"{PATCHNOTE_BASE_URL}/{post_id}",
                        })

                    if not posts:
                        print("[패치노트] 게시글을 찾을 수 없음", flush=True)

                    return posts[:5]

        except Exception as e:
            print(f"[패치노트] 페이지 로드 실패: {e}", flush=True)
            return []

    async def get_last_patchnote_id(self):
        """GCS에서 마지막으로 확인한 패치노트 ID를 가져옵니다."""
        try:
            settings = await asyncio.to_thread(config.load_settings)
            return settings.get("global", {}).get("last_patchnote_id")
        except Exception as e:
            print(f"[패치노트] 마지막 ID 로드 실패: {e}", flush=True)
            return None

    async def save_last_patchnote_id(self, patchnote_id):
        """GCS에 마지막으로 확인한 패치노트 ID를 저장합니다."""
        try:
            settings = await asyncio.to_thread(config.load_settings)
            if "global" not in settings:
                settings["global"] = {}
            settings["global"]["last_patchnote_id"] = patchnote_id
            await asyncio.to_thread(config.save_settings, settings)
        except Exception as e:
            print(f"[패치노트] 마지막 ID 저장 실패: {e}", flush=True)

    async def get_subscribed_channels(self):
        """패치노트 알림이 활성화된 채널 목록을 가져옵니다."""
        channels = []
        try:
            settings = await asyncio.to_thread(config.load_settings)
            guilds = settings.get("guilds", {})

            for guild_id, guild_settings in guilds.items():
                notification_settings = guild_settings.get("notification_settings", {})
                patch_note = notification_settings.get("patchNote", {})

                if patch_note.get("enabled") and patch_note.get("channelId"):
                    channel_id = int(patch_note["channelId"])
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        channels.append(channel)
                    else:
                        print(
                            f"[패치노트] 채널을 찾을 수 없음: {channel_id} (서버: {guild_id})",
                            flush=True,
                        )
        except Exception as e:
            print(f"[패치노트] 구독 채널 조회 실패: {e}", flush=True)

        return channels

    def format_patchnote_message(self, patch_note):
        """패치노트를 고정 메시지용 텍스트로 포맷합니다."""
        lines = [
            "--- 현재 패치노트! ---",
            "",
            f"**{patch_note['title']}**",
        ]
        if patch_note.get("description"):
            lines.append(patch_note["description"])
        lines.append("")
        lines.append(patch_note.get("url", ""))
        return "\n".join(lines)

    async def send_notification(self, channel, patch_note):
        """패치노트 알림을 전송하고 sticky_messages에 등록합니다."""
        guild_id = str(channel.guild.id)
        channel_id_str = str(channel.id)
        content = self.format_patchnote_message(patch_note)

        try:
            # 이전 고정 메시지 삭제
            settings = await asyncio.to_thread(config.load_settings, True)
            guild_data = settings.get("guilds", {}).get(guild_id, {})
            sticky_messages = guild_data.get("sticky_messages", [])

            old_sticky = None
            for sm in sticky_messages:
                if sm.get("id") == f"patchnote_{guild_id}":
                    old_sticky = sm
                    break

            if old_sticky and old_sticky.get("lastMessageId"):
                try:
                    old_msg = await channel.fetch_message(int(old_sticky["lastMessageId"]))
                    await old_msg.delete()
                except Exception:
                    pass

            # 새 메시지 전송 (알림 울리게)
            new_msg = await channel.send(content)

            # sticky_messages에 등록/갱신
            new_sticky = {
                "id": f"patchnote_{guild_id}",
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
                if "sticky_messages" not in settings.get("guilds", {}).get(guild_id, {}):
                    settings["guilds"][guild_id]["sticky_messages"] = []
                settings["guilds"][guild_id]["sticky_messages"].append(new_sticky)

            await asyncio.to_thread(config.save_settings, settings, True)

        except discord.Forbidden:
            print(
                f"[패치노트] 메시지 전송 권한 없음: #{channel.name} ({channel.guild.name})",
                flush=True,
            )
        except Exception as e:
            print(
                f"[패치노트] 알림 전송 실패: #{channel.name} ({channel.guild.name}) - {e}",
                flush=True,
            )

    async def check_new_patchnotes(self):
        """새로운 패치노트를 확인하고 알림을 보냅니다."""
        try:
            patchnotes = await self.fetch_patchnotes()
            if not patchnotes:
                return

            latest = patchnotes[0]
            last_id = await self.get_last_patchnote_id()

            # 같은 ID면 새 패치노트 없음
            if latest["id"] == last_id:
                return

            is_first_run = last_id is None
            if is_first_run:
                print(f"[패치노트] 초기 실행 (최신: {latest['title']})", flush=True)

            print(f"[패치노트] 새 패치노트 발견: {latest['title']}", flush=True)

            # 구독 채널들에 알림 전송
            channels = await self.get_subscribed_channels()
            if channels:
                for channel in channels:
                    await self.send_notification(channel, latest)
                print(
                    f"[패치노트] 알림 전송 완료 ({len(channels)}개 채널)",
                    flush=True,
                )
            else:
                print("[패치노트] 구독 채널 없음 - 알림 미전송", flush=True)

            # 마지막 ID 업데이트
            await self.save_last_patchnote_id(latest["id"])

        except Exception as e:
            print(f"[패치노트] 확인 중 오류: {e}", flush=True)
            import traceback
            traceback.print_exc()


# 전역 인스턴스
_checker = None


def get_checker():
    return _checker


@tasks.loop(minutes=10)
async def check_patchnotes():
    """10분마다 패치노트를 확인합니다."""
    if _checker:
        await _checker.check_new_patchnotes()


def start_patchnote_checker(bot):
    """패치노트 체커를 초기화하고 태스크를 시작합니다."""
    global _checker
    _checker = PatchNoteChecker(bot)
    if not check_patchnotes.is_running():
        check_patchnotes.start()
    print("[완료] 패치노트 체커 시작 (10분 간격)", flush=True)

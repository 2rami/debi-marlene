"""
음악 관련 Embed UI

음악 재생 관련 임베드를 생성합니다.
"""

import discord
from typing import List, Optional

from run.services.music.youtube_extractor import Song, format_duration


def create_now_playing_embed(song: Song) -> discord.Embed:
    """현재 재생 중인 곡 Embed 생성"""
    embed = discord.Embed(
        title="Now Playing",
        description=f"**[{song.title}]({song.url})**",
        color=0xFF0000
    )

    if song.thumbnail:
        embed.set_thumbnail(url=song.thumbnail)

    embed.add_field(
        name="재생 시간",
        value=format_duration(song.duration),
        inline=True
    )
    embed.add_field(
        name="요청자",
        value=song.requester.display_name,
        inline=True
    )

    return embed


def create_added_to_queue_embed(song: Song, position: int) -> discord.Embed:
    """대기열에 추가됨 Embed 생성"""
    if position == 0:
        title = "Now Playing"
        color = 0xFF0000
    else:
        title = "Added to Queue"
        color = 0x00FF00

    embed = discord.Embed(
        title=title,
        description=f"**[{song.title}]({song.url})**",
        color=color
    )

    if song.thumbnail:
        embed.set_thumbnail(url=song.thumbnail)

    embed.add_field(
        name="재생 시간",
        value=format_duration(song.duration),
        inline=True
    )

    if position > 0:
        embed.add_field(
            name="대기열 순서",
            value=f"#{position}",
            inline=True
        )

    embed.add_field(
        name="요청자",
        value=song.requester.display_name,
        inline=True
    )

    return embed


def create_queue_embed(
    current: Optional[Song],
    queue: List[Song],
    page: int = 0,
    per_page: int = 10
) -> discord.Embed:
    """대기열 목록 Embed 생성"""
    embed = discord.Embed(
        title="Music Queue",
        color=0x3498DB
    )

    # 현재 재생 중
    if current:
        embed.add_field(
            name="Now Playing",
            value=f"**[{current.title}]({current.url})** [{format_duration(current.duration)}]\n"
                  f"요청자: {current.requester.display_name}",
            inline=False
        )

    # 대기열이 비어있는 경우
    if not queue:
        embed.add_field(
            name="Up Next",
            value="대기열이 비어있습니다.",
            inline=False
        )
        return embed

    # 페이지네이션
    total_pages = (len(queue) - 1) // per_page + 1
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(queue))

    # 대기열 목록
    queue_text = ""
    for i, song in enumerate(queue[start_idx:end_idx], start=start_idx + 1):
        queue_text += f"`{i}.` **[{song.title}]({song.url})** [{format_duration(song.duration)}]\n"
        queue_text += f"    요청자: {song.requester.display_name}\n"

    embed.add_field(
        name=f"Up Next ({len(queue)} songs)",
        value=queue_text or "대기열이 비어있습니다.",
        inline=False
    )

    # 총 재생 시간
    total_duration = sum(s.duration for s in queue)
    if current:
        total_duration += current.duration

    embed.set_footer(
        text=f"Page {page + 1}/{total_pages} | Total: {format_duration(total_duration)}"
    )

    return embed


def create_skipped_embed(song: Song) -> discord.Embed:
    """곡 스킵 Embed 생성"""
    embed = discord.Embed(
        title="Skipped",
        description=f"**{song.title}**",
        color=0xFFA500
    )
    return embed


def create_stopped_embed() -> discord.Embed:
    """재생 정지 Embed 생성"""
    embed = discord.Embed(
        title="Stopped",
        description="재생을 정지하고 대기열을 비웠습니다.",
        color=0xFF0000
    )
    return embed


def create_error_embed(message: str) -> discord.Embed:
    """에러 Embed 생성"""
    embed = discord.Embed(
        title="Error",
        description=message,
        color=0xFF0000
    )
    return embed

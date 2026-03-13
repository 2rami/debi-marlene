"""
음악 관련 Embed UI + 플레이어 컨트롤

Spotify 스타일 버튼 컨트롤과 상시 대기열을 제공합니다.
"""

import asyncio
import discord
from typing import List, Optional
import logging

from run.services.music.youtube_extractor import Song, format_duration

logger = logging.getLogger(__name__)

# 애플리케이션 커스텀 이모지 ID
EMOJI_PLAY = discord.PartialEmoji(name="ui_play", id=1481865511804600481)
EMOJI_PAUSE = discord.PartialEmoji(name="ui_pause", id=1481865513608024094)
EMOJI_SKIP = discord.PartialEmoji(name="ui_skip", id=1481865515332010098)
EMOJI_PREVIOUS = discord.PartialEmoji(name="ui_previous", id=1481865516959137975)
EMOJI_STOP = discord.PartialEmoji(name="ui_stop", id=1481865518892716096)


def _build_player_embed(guild_id: str) -> discord.Embed:
    """현재 재생 상태 + 대기열을 하나의 Embed로 생성"""
    from run.services.music import MusicManager

    if not MusicManager.has_player(guild_id):
        return discord.Embed(title="Music", description="재생 중인 음악이 없습니다.", color=0x2B2D31)

    player = MusicManager.get_player(guild_id)

    if not player.current:
        return discord.Embed(title="Music", description="재생 중인 음악이 없습니다.", color=0x2B2D31)

    song = player.current
    paused = player.is_paused()
    status = "Paused" if paused else "Now Playing"

    embed = discord.Embed(
        title=status,
        description=f"**[{song.title}]({song.url})**",
        color=0x1DB954 if not paused else 0xFFA500
    )

    if song.thumbnail:
        embed.set_thumbnail(url=song.thumbnail)

    embed.add_field(name="재생 시간", value=format_duration(song.duration), inline=True)
    embed.add_field(name="요청자", value=song.requester.display_name, inline=True)

    # 대기열 표시
    queue = player.get_queue()
    if queue:
        queue_lines = []
        for i, s in enumerate(queue[:5], 1):
            queue_lines.append(f"`{i}.` {s.title} [{format_duration(s.duration)}]")
        if len(queue) > 5:
            queue_lines.append(f"... +{len(queue) - 5}곡")
        embed.add_field(name=f"Up Next ({len(queue)})", value="\n".join(queue_lines), inline=False)
    else:
        embed.add_field(name="Up Next", value="대기열이 비어있습니다.", inline=False)

    return embed


class MusicPlayerView(discord.ui.View):
    """Spotify 스타일 음악 플레이어 컨트롤"""

    def __init__(self, guild_id: str):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    async def _update_message(self, interaction: discord.Interaction):
        """플레이어 임베드를 최신 상태로 업데이트"""
        embed = _build_player_embed(self.guild_id)
        try:
            await interaction.message.edit(embed=embed, view=self)
        except Exception:
            pass

    @discord.ui.button(emoji=EMOJI_PREVIOUS, label="처음", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """처음부터 다시 재생"""
        from run.services.music import MusicManager

        if not MusicManager.has_player(self.guild_id):
            await interaction.response.send_message("재생 중인 음악이 없어요!", ephemeral=True)
            return

        player = MusicManager.get_player(self.guild_id)
        if not player.current:
            await interaction.response.send_message("재생 중인 곡이 없어요!", ephemeral=True)
            return

        player.queue.appendleft(player.current)
        await player.skip()
        await interaction.response.defer()
        await self._update_message(interaction)

    @discord.ui.button(emoji=EMOJI_PAUSE, label="일시정지", style=discord.ButtonStyle.primary)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """일시정지 / 재개 토글"""
        from run.services.music import MusicManager

        if not MusicManager.has_player(self.guild_id):
            await interaction.response.send_message("재생 중인 음악이 없어요!", ephemeral=True)
            return

        player = MusicManager.get_player(self.guild_id)

        if player.is_paused():
            player.resume()
            button.emoji = EMOJI_PAUSE
            button.label = "일시정지"
        else:
            player.pause()
            button.emoji = EMOJI_PLAY
            button.label = "재생"

        await interaction.response.defer()
        await self._update_message(interaction)

    @discord.ui.button(emoji=EMOJI_SKIP, label="스킵", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """다음 곡으로 스킵"""
        from run.services.music import MusicManager

        if not MusicManager.has_player(self.guild_id):
            await interaction.response.send_message("재생 중인 음악이 없어요!", ephemeral=True)
            return

        player = MusicManager.get_player(self.guild_id)
        if not player.current:
            await interaction.response.send_message("스킵할 곡이 없어요!", ephemeral=True)
            return

        await player.skip()
        await interaction.response.defer()
        await asyncio.sleep(0.5)
        await self._update_message(interaction)

    @discord.ui.button(emoji=EMOJI_STOP, label="정지", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """정지 + 대기열 비우기 (음성 채널 유지)"""
        from run.services.music import MusicManager

        if not MusicManager.has_player(self.guild_id):
            await interaction.response.send_message("재생 중인 음악이 없어요!", ephemeral=True)
            return

        await interaction.response.defer()
        player = MusicManager.get_player(self.guild_id)
        await player.stop()

        embed = discord.Embed(
            title="Stopped",
            description="재생을 정지했습니다.",
            color=0xFF0000
        )

        queue = player.get_queue()
        if queue:
            queue_lines = []
            for i, s in enumerate(queue[:5], 1):
                queue_lines.append(f"`{i}.` {s.title} [{format_duration(s.duration)}]")
            if len(queue) > 5:
                queue_lines.append(f"... +{len(queue) - 5}곡")
            embed.add_field(name=f"Up Next ({len(queue)})", value="\n".join(queue_lines), inline=False)

        try:
            await interaction.message.edit(embed=embed, view=self)
        except Exception:
            pass


def create_now_playing_embed(song: Song, queue: List[Song] = None) -> discord.Embed:
    """현재 재생 중인 곡 + 대기열 Embed"""
    embed = discord.Embed(
        title="Now Playing",
        description=f"**[{song.title}]({song.url})**",
        color=0x1DB954
    )

    if song.thumbnail:
        embed.set_thumbnail(url=song.thumbnail)

    embed.add_field(name="재생 시간", value=format_duration(song.duration), inline=True)
    embed.add_field(name="요청자", value=song.requester.display_name, inline=True)

    if queue:
        queue_lines = []
        for i, s in enumerate(queue[:5], 1):
            queue_lines.append(f"`{i}.` {s.title} [{format_duration(s.duration)}]")
        if len(queue) > 5:
            queue_lines.append(f"... +{len(queue) - 5}곡")
        embed.add_field(name=f"Up Next ({len(queue)})", value="\n".join(queue_lines), inline=False)
    else:
        embed.add_field(name="Up Next", value="대기열이 비어있습니다.", inline=False)

    return embed


def create_added_to_queue_embed(song: Song, position: int, queue: List[Song] = None) -> discord.Embed:
    """대기열에 추가됨 Embed (대기열 포함)"""
    if position == 0:
        title = "Now Playing"
        color = 0x1DB954
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

    embed.add_field(name="재생 시간", value=format_duration(song.duration), inline=True)

    if position > 0:
        embed.add_field(name="대기열 순서", value=f"#{position}", inline=True)

    embed.add_field(name="요청자", value=song.requester.display_name, inline=True)

    # 대기열 표시
    if queue:
        queue_lines = []
        for i, s in enumerate(queue[:5], 1):
            queue_lines.append(f"`{i}.` {s.title} [{format_duration(s.duration)}]")
        if len(queue) > 5:
            queue_lines.append(f"... +{len(queue) - 5}곡")
        embed.add_field(name=f"Up Next ({len(queue)})", value="\n".join(queue_lines), inline=False)

    return embed


def create_error_embed(message: str) -> discord.Embed:
    """에러 Embed"""
    embed = discord.Embed(title="Error", description=message, color=0xFF0000)
    return embed

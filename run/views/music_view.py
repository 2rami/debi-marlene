"""
음악 관련 UI - Components V2 (LayoutView)

Container + TextDisplay + Section + Separator로 구성된 음악 플레이어.
대기열이 버튼 아래에 표시됩니다.
"""

import asyncio
import discord
from discord import ui
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

# 색상
COLOR_PLAYING = 0x1DB954
COLOR_PAUSED = 0xFFA500
COLOR_STOPPED = 0xFF0000
COLOR_QUEUED = 0x00FF00


def _build_queue_text(queue: List[Song], max_items: int = 5) -> str:
    """대기열 텍스트 생성"""
    if not queue:
        return "-# 대기열이 비어있습니다."
    lines = []
    for i, s in enumerate(queue[:max_items], 1):
        lines.append(f"`{i}.` {s.title} [{format_duration(s.duration)}]")
    if len(queue) > max_items:
        lines.append(f"... +{len(queue) - max_items}곡")
    return "\n".join(lines)


class MusicPlayerView(ui.LayoutView):
    """Components V2 음악 플레이어"""

    def __init__(self, guild_id: str, added_song: Song = None, added_position: int = None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self._added_song = added_song
        self._added_position = added_position
        self._build()

    def _build(self):
        """현재 상태에 맞게 컴포넌트를 구성합니다."""
        self.clear_items()

        from run.services.music import MusicManager
        player = MusicManager.get_player(self.guild_id) if MusicManager.has_player(self.guild_id) else None
        song = player.current if player else None
        paused = player.is_paused() if player else False
        queue = player.get_queue() if player else []

        # player.current가 아직 없으면 added_song을 현재 곡으로 사용
        # (add_song 직후 _play_loop가 아직 시작 안 된 경우)
        if not song and self._added_song:
            song = self._added_song

        # 대기열에 추가된 경우 (2번째 이상 곡) 알림 표시
        if self._added_song and self._added_position and self._added_position > 1:
            added = self._added_song
            added_children = [
                ui.TextDisplay(f"### Added to Queue  #{self._added_position - 1}"),
            ]
            if added.thumbnail:
                added_children.append(
                    ui.Section(
                        ui.TextDisplay(f"**[{added.title}]({added.url})**"),
                        ui.TextDisplay(f"{format_duration(added.duration)}  |  {added.requester.display_name}"),
                        accessory=ui.Thumbnail(added.thumbnail),
                    )
                )
            else:
                added_children.append(ui.TextDisplay(f"**[{added.title}]({added.url})**"))
                added_children.append(ui.TextDisplay(f"{format_duration(added.duration)}  |  {added.requester.display_name}"))

            self.add_item(ui.Container(*added_children))

        # 재생 중인 곡이 없으면 간단 표시
        if not song:
            container = ui.Container(
                ui.TextDisplay("### Music"),
                ui.TextDisplay("재생 중인 음악이 없습니다."),
            )
            self.add_item(container)
            return

        # === 상단: top-level (Container 밖) - 곡 정보 ===
        status = "Paused" if paused else "Now Playing"

        self.add_item(ui.TextDisplay(f"### {status}"))
        if song.thumbnail:
            self.add_item(
                ui.Section(
                    ui.TextDisplay(f"**[{song.title}]({song.url})**"),
                    ui.TextDisplay(f"{format_duration(song.duration)}  |  {song.requester.display_name}"),
                    accessory=ui.Thumbnail(song.thumbnail),
                )
            )
        else:
            self.add_item(ui.TextDisplay(f"**[{song.title}]({song.url})**"))
            self.add_item(ui.TextDisplay(f"{format_duration(song.duration)}  |  {song.requester.display_name}"))

        # === 하단: Container 안 - 버튼 + 대기열 ===
        container_children = []

        # 버튼
        action_row = ui.ActionRow(
            ui.Button(
                emoji=EMOJI_PREVIOUS, label="처음",
                style=discord.ButtonStyle.secondary, custom_id="music_prev",
            ),
            ui.Button(
                emoji=EMOJI_PLAY if paused else EMOJI_PAUSE,
                label="재생" if paused else "일시정지",
                style=discord.ButtonStyle.primary, custom_id="music_pause",
            ),
            ui.Button(
                emoji=EMOJI_SKIP, label="스킵",
                style=discord.ButtonStyle.secondary, custom_id="music_skip",
            ),
            ui.Button(
                emoji=EMOJI_STOP, label="정지",
                style=discord.ButtonStyle.danger, custom_id="music_stop",
            ),
        )
        container_children.append(action_row)

        # 대기열
        container_children.append(ui.Separator(spacing=discord.SeparatorSpacing.small))
        queue_header = f"**Up Next ({len(queue)})**" if queue else "**Up Next**"
        container_children.append(ui.TextDisplay(queue_header))
        container_children.append(ui.TextDisplay(_build_queue_text(queue)))

        container = _PlayerContainer(self.guild_id, *container_children)
        self.add_item(container)


class _PlayerContainer(ui.Container):
    """플레이어 컨테이너 - 버튼 인터랙션 처리"""

    def __init__(self, guild_id: str, *children, **kwargs):
        self.guild_id = guild_id
        super().__init__(*children, **kwargs)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        custom_id = interaction.data.get("custom_id", "")

        from run.services.music import MusicManager

        if not MusicManager.has_player(self.guild_id):
            await interaction.response.send_message("재생 중인 음악이 없어요!", ephemeral=True)
            return False

        player = MusicManager.get_player(self.guild_id)

        if custom_id == "music_prev":
            if player.current:
                player.queue.appendleft(player.current)
                await player.skip()
            await interaction.response.defer()

        elif custom_id == "music_pause":
            if player.is_paused():
                player.resume()
            else:
                player.pause()
            await interaction.response.defer()

        elif custom_id == "music_skip":
            if player.current:
                await player.skip()
            await interaction.response.defer()
            await asyncio.sleep(0.5)

        elif custom_id == "music_stop":
            await player.stop()
            await interaction.response.defer()

        else:
            return True

        # 뷰 재구성 후 메시지 업데이트
        view = MusicPlayerView(self.guild_id)
        try:
            await interaction.message.edit(view=view)
        except Exception:
            pass

        return False


def create_error_view(message: str) -> ui.LayoutView:
    """에러 LayoutView"""
    view = ui.LayoutView(timeout=None)
    container = ui.Container(
        ui.TextDisplay("### Error"),
        ui.TextDisplay(message),
    )
    view.add_item(container)
    return view


# === 하위 호환용 (embed 방식) ===

def create_now_playing_embed(song: Song, queue: List[Song] = None) -> discord.Embed:
    """현재 재생 중인 곡 + 대기열 Embed (레거시)"""
    embed = discord.Embed(
        title="Now Playing",
        description=f"**[{song.title}]({song.url})**",
        color=COLOR_PLAYING
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
    return embed


def create_added_to_queue_embed(song: Song, position: int, queue: List[Song] = None) -> discord.Embed:
    """대기열에 추가됨 Embed (레거시)"""
    if position == 0:
        title = "Now Playing"
        color = COLOR_PLAYING
    else:
        title = "Added to Queue"
        color = COLOR_QUEUED

    embed = discord.Embed(title=title, description=f"**[{song.title}]({song.url})**", color=color)
    if song.thumbnail:
        embed.set_thumbnail(url=song.thumbnail)
    embed.add_field(name="재생 시간", value=format_duration(song.duration), inline=True)
    if position > 0:
        embed.add_field(name="대기열 순서", value=f"#{position}", inline=True)
    embed.add_field(name="요청자", value=song.requester.display_name, inline=True)
    if queue:
        queue_lines = []
        for i, s in enumerate(queue[:5], 1):
            queue_lines.append(f"`{i}.` {s.title} [{format_duration(s.duration)}]")
        if len(queue) > 5:
            queue_lines.append(f"... +{len(queue) - 5}곡")
        embed.add_field(name=f"Up Next ({len(queue)})", value="\n".join(queue_lines), inline=False)
    return embed


def create_error_embed(message: str) -> discord.Embed:
    """에러 Embed (레거시)"""
    return discord.Embed(title="Error", description=message, color=COLOR_STOPPED)

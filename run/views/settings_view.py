"""
서버 설정 UI

- SettingsLayoutView: /설정 명령어의 메인 UI (Components V2, LayoutView)
- SettingsView: 레거시 설정 UI (환영 메시지 등에서 사용)
- ChannelSelectViewForSetting: 채널 선택 드롭다운
"""
import discord
import sys
from typing import Optional

from run.core import config

DASHBOARD_URL = "https://debimarlene.com"
EMOJI_DASHBOARD = discord.PartialEmoji(name="ui_dashboard", id=1481865509971693649)


def build_settings_layout(guild: discord.Guild, user_id: int, is_admin: bool):
    """서버 설정 LayoutView를 생성하는 팩토리 함수

    콜백에서 설정 변경 후 뷰를 재빌드할 때도 사용.
    """
    return SettingsLayoutView(guild, user_id, is_admin)


class SettingsLayoutView(discord.ui.LayoutView):
    """
    /설정 명령어 메인 UI (Components V2)

    Container 구조:
    1. 현재 설정 상태 (공지 채널, TTS, DM 알림)
    2. 공지 채널 선택 (ChannelSelect)
    3. TTS 기본 목소리 선택 (Select)
    4. 하단 버튼 (DM 알림 토글, 대시보드 링크, 테스트)
    """

    def __init__(self, guild: discord.Guild, user_id: int, is_admin: bool):
        super().__init__(timeout=120)
        self.guild = guild
        self.user_id = user_id
        self.is_admin = is_admin
        self.message = None

        guild_id = str(guild.id)
        guild_settings = config.get_guild_settings(guild.id)
        settings = config.load_settings()
        full_guild_settings = settings.get("guilds", {}).get(guild_id, {})

        # 현재 설정값 읽기
        announcement_ch_id = guild_settings.get("ANNOUNCEMENT_CHANNEL_ID")
        tts_voice = full_guild_settings.get("tts_voice", "debi")
        tts_channel_id = full_guild_settings.get("tts_channel_id")
        is_subscribed = config.is_youtube_subscribed(user_id)

        # 텍스트 빌드
        if announcement_ch_id:
            ch = guild.get_channel(int(announcement_ch_id))
            channel_text = f"#{ch.name}" if ch else "채널을 찾을 수 없음"
        else:
            channel_text = "미설정"

        voice_names = {"debi": "데비", "marlene": "마를렌", "alex": "알렉스"}
        voice_text = voice_names.get(tts_voice, tts_voice)

        if tts_channel_id:
            tts_ch = guild.get_channel(int(tts_channel_id))
            tts_channel_text = f"#{tts_ch.name}" if tts_ch else "채널을 찾을 수 없음"
        else:
            tts_channel_text = "모든 채널"

        dm_text = "켜짐" if is_subscribed else "꺼짐"

        # === Container 1: 현재 상태 ===
        status_text = (
            f"## 서버 설정\n"
            f"공지 채널: **{channel_text}**\n"
            f"TTS 기본 목소리: **{voice_text}**\n"
            f"TTS 읽을 채널: **{tts_channel_text}**\n"
            f"DM 알림: **{dm_text}**"
        )
        self.add_item(discord.ui.Container(discord.ui.TextDisplay(status_text)))

        # === Container 2: 설정 컨트롤 ===
        controls = []

        # 공지 채널 선택
        controls.append(discord.ui.TextDisplay("**공지 채널** - 유튜브 새 영상 알림을 받을 채널"))
        channel_select = discord.ui.ChannelSelect(
            placeholder="공지 채널을 선택하세요",
            channel_types=[discord.ChannelType.text]
        )
        channel_select.callback = self._on_channel_select
        controls.append(discord.ui.ActionRow(channel_select))

        controls.append(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))

        # TTS 목소리 선택
        controls.append(discord.ui.TextDisplay("**TTS 기본 목소리**"))
        voice_select = discord.ui.Select(
            placeholder="TTS 기본 목소리를 선택하세요",
            options=[
                discord.SelectOption(label="데비", value="debi", description="밝고 활기찬 목소리", default=(tts_voice == "debi")),
                discord.SelectOption(label="마를렌", value="marlene", description="차분하고 낮은 목소리", default=(tts_voice == "marlene")),
                discord.SelectOption(label="알렉스", value="alex", description="중성적인 목소리", default=(tts_voice == "alex")),
            ]
        )
        voice_select.callback = self._on_voice_select
        controls.append(discord.ui.ActionRow(voice_select))

        self.add_item(discord.ui.Container(*controls))

        # === Container 3: 버튼 ===
        dm_btn = discord.ui.Button(
            label=f"DM 알림 {'끄기' if is_subscribed else '켜기'}",
            style=discord.ButtonStyle.secondary if is_subscribed else discord.ButtonStyle.primary
        )
        dm_btn.callback = self._on_dm_toggle

        dashboard_btn = discord.ui.Button(
            label="대시보드",
            emoji=EMOJI_DASHBOARD,
            style=discord.ButtonStyle.link,
            url=f"{DASHBOARD_URL}/servers/{guild.id}"
        )

        btn_items = [dm_btn, dashboard_btn]

        if is_admin:
            test_btn = discord.ui.Button(label="테스트", style=discord.ButtonStyle.secondary)
            test_btn.callback = self._on_test
            btn_items.append(test_btn)

        self.add_item(discord.ui.Container(discord.ui.ActionRow(*btn_items)))

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except Exception:
                pass

    async def _rebuild(self, interaction: discord.Interaction):
        """설정 변경 후 뷰를 재빌드하여 최신 상태 반영"""
        new_view = build_settings_layout(self.guild, self.user_id, self.is_admin)
        await interaction.response.edit_message(view=new_view)

    async def _on_channel_select(self, interaction: discord.Interaction):
        channel = interaction.data["values"][0]
        # ChannelSelect의 값은 ID 문자열
        channel_id = int(channel)
        ch = self.guild.get_channel(channel_id)
        channel_name = ch.name if ch else None

        config.save_guild_settings(
            self.guild.id,
            announcement_id=channel_id,
            guild_name=self.guild.name,
            announcement_channel_name=channel_name
        )
        await self._rebuild(interaction)

    async def _on_voice_select(self, interaction: discord.Interaction):
        selected = interaction.data["values"][0]
        guild_id = str(self.guild.id)

        settings = config.load_settings()
        if "guilds" not in settings:
            settings["guilds"] = {}
        if guild_id not in settings["guilds"]:
            settings["guilds"][guild_id] = {}
        settings["guilds"][guild_id]["tts_voice"] = selected
        config.save_settings(settings)

        await self._rebuild(interaction)

    async def _on_dm_toggle(self, interaction: discord.Interaction):
        user_name = interaction.user.display_name or interaction.user.global_name or interaction.user.name
        is_subscribed = config.is_youtube_subscribed(self.user_id)
        config.set_youtube_subscription(self.user_id, not is_subscribed, user_name)
        await self._rebuild(interaction)

    async def _on_test(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("관리자만 사용할 수 있어요!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            from run.services import youtube_service
            result = await youtube_service.manual_check_for_guild(self.guild)
            await interaction.followup.send(f"테스트 완료!\n```{result}```", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"테스트 중 오류: {e}", ephemeral=True)


# === 레거시 UI (ChannelSelectViewForSetting은 다른 곳에서 아직 사용 가능) ===

class ChannelSelectViewForSetting(discord.ui.View):
    """채널 선택 드롭다운 UI"""

    def __init__(self, channel_type: str):
        super().__init__(timeout=180)
        self.channel_type = channel_type
        label = "공지" if channel_type == "announcement" else "채팅"
        placeholder = f"#{label} 채널을 선택하세요..."

        self.select_menu = discord.ui.ChannelSelect(
            placeholder=placeholder,
            channel_types=[discord.ChannelType.text]
        )
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            channel = self.select_menu.values[0]

            if self.channel_type == "announcement":
                config.save_guild_settings(
                    interaction.guild.id,
                    announcement_id=channel.id,
                    guild_name=interaction.guild.name,
                    announcement_channel_name=channel.name
                )
                await interaction.followup.edit_message(
                    interaction.message.id,
                    content=f"[완료] 공지 채널이 {channel.mention}으로 설정되었습니다.",
                    view=None
                )
            else:
                config.save_guild_settings(
                    interaction.guild.id,
                    chat_id=channel.id,
                    guild_name=interaction.guild.name,
                    chat_channel_name=channel.name
                )
                await interaction.followup.edit_message(
                    interaction.message.id,
                    content=f"[완료] 채팅 채널이 {channel.mention}으로 설정되었습니다.",
                    view=None
                )
        except Exception as e:
            print(f"[오류] 채널 설정 오류: {e}", flush=True)
            try:
                await interaction.followup.send("설정 중 오류가 발생했습니다.", ephemeral=True)
            except:
                pass

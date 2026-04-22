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

        chat_enabled = full_guild_settings.get("chat_enabled", True)
        dm_text = "켜짐" if is_subscribed else "꺼짐"
        tts_auto_delete = full_guild_settings.get("tts_auto_delete_seconds", 0)
        auto_delete_text = f"{tts_auto_delete}초" if tts_auto_delete else "꺼짐"

        # 솔로봇 자율 응답 채널
        debi_channels = config.get_solo_chat_channels(guild.id, "debi")
        marlene_channels = config.get_solo_chat_channels(guild.id, "marlene")
        self._debi_channel_text = self._format_channel_list(guild, debi_channels)
        self._marlene_channel_text = self._format_channel_list(guild, marlene_channels)

        # === Container 1: 현재 상태 ===
        chat_text = "켜짐" if chat_enabled else "꺼짐"
        status_text = (
            f"## 서버 설정\n"
            f"대화 기능(/대화 + 솔로봇 끼어들기): **{chat_text}**\n"
            f"공지 채널: **{channel_text}**\n"
            f"TTS 기본 목소리: **{voice_text}**\n"
            f"TTS 읽을 채널: **{tts_channel_text}**\n"
            f"TTS 메시지 자동 삭제: **{auto_delete_text}**\n"
            f"DM 알림: **{dm_text}**\n"
            f"데비 응답 채널: **{self._debi_channel_text}**\n"
            f"마를렌 응답 채널: **{self._marlene_channel_text}**"
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

        controls.append(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))

        # 솔로봇 자율 응답 채널 (debi)
        controls.append(discord.ui.TextDisplay(
            f"**데비 자율 응답 채널** - 현재: {self._debi_channel_text}\n"
            "지정 채널에서는 호명 없이도 AI가 자연스럽게 끼어들어요. 최대 5개. "
            "다시 선택하면 덮어써집니다."
        ))
        debi_select = discord.ui.ChannelSelect(
            placeholder="데비가 자율 응답할 채널 선택 (최대 5개)",
            channel_types=[discord.ChannelType.text],
            min_values=0,
            max_values=5,
        )
        debi_select.callback = self._on_debi_channels_select
        controls.append(discord.ui.ActionRow(debi_select))

        controls.append(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))

        # 솔로봇 자율 응답 채널 (marlene)
        controls.append(discord.ui.TextDisplay(
            f"**마를렌 자율 응답 채널** - 현재: {self._marlene_channel_text}\n"
            "지정 채널에서는 호명 없이도 AI가 자연스럽게 끼어들어요. 최대 5개. "
            "다시 선택하면 덮어써집니다."
        ))
        marlene_select = discord.ui.ChannelSelect(
            placeholder="마를렌이 자율 응답할 채널 선택 (최대 5개)",
            channel_types=[discord.ChannelType.text],
            min_values=0,
            max_values=5,
        )
        marlene_select.callback = self._on_marlene_channels_select
        controls.append(discord.ui.ActionRow(marlene_select))

        controls.append(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))

        # TTS 메시지 자동 삭제
        controls.append(discord.ui.TextDisplay("**TTS 메시지 자동 삭제** - TTS가 읽은 메시지를 N초 후 삭제"))
        auto_delete_select = discord.ui.Select(
            placeholder="자동 삭제 시간",
            options=[
                discord.SelectOption(label="꺼짐", value="0", default=(tts_auto_delete == 0)),
                discord.SelectOption(label="3초", value="3", default=(tts_auto_delete == 3)),
                discord.SelectOption(label="5초", value="5", default=(tts_auto_delete == 5)),
                discord.SelectOption(label="10초", value="10", default=(tts_auto_delete == 10)),
                discord.SelectOption(label="30초", value="30", default=(tts_auto_delete == 30)),
            ]
        )
        auto_delete_select.callback = self._on_auto_delete_select
        controls.append(discord.ui.ActionRow(auto_delete_select))

        self.add_item(discord.ui.Container(*controls))

        # === Container 3: 버튼 ===
        chat_btn = discord.ui.Button(
            label=f"대화 {'끄기' if chat_enabled else '켜기'}",
            style=discord.ButtonStyle.secondary if chat_enabled else discord.ButtonStyle.primary
        )
        chat_btn.callback = self._on_chat_toggle

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

        btn_items = [chat_btn, dm_btn, dashboard_btn]

        if is_admin:
            test_btn = discord.ui.Button(label="유튜브 알림 테스트", style=discord.ButtonStyle.secondary)
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

    @staticmethod
    def _format_channel_list(guild: discord.Guild, channel_ids: list[int]) -> str:
        """채널 ID 목록 → '#ch1, #ch2' 텍스트. 빈 리스트는 '미설정'."""
        if not channel_ids:
            return "미설정"
        names = []
        for cid in channel_ids:
            ch = guild.get_channel(int(cid))
            names.append(f"#{ch.name}" if ch else f"(삭제된 채널 {cid})")
        return ", ".join(names)

    async def _on_debi_channels_select(self, interaction: discord.Interaction):
        await self._save_solo_channels(interaction, "debi")

    async def _on_marlene_channels_select(self, interaction: discord.Interaction):
        await self._save_solo_channels(interaction, "marlene")

    async def _save_solo_channels(self, interaction: discord.Interaction, identity: str):
        raw_values = interaction.data.get("values", []) or []
        channel_ids = []
        for v in raw_values:
            try:
                channel_ids.append(int(v))
            except (TypeError, ValueError):
                continue
        try:
            config.set_solo_chat_channels(self.guild.id, identity, channel_ids)
        except Exception as e:
            print(f"[오류] solo 채널 저장 실패 ({identity}): {e}", flush=True)
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

    async def _on_auto_delete_select(self, interaction: discord.Interaction):
        selected = int(interaction.data["values"][0])
        guild_id = str(self.guild.id)

        settings = config.load_settings()
        if "guilds" not in settings:
            settings["guilds"] = {}
        if guild_id not in settings["guilds"]:
            settings["guilds"][guild_id] = {}
        settings["guilds"][guild_id]["tts_auto_delete_seconds"] = selected
        config.save_settings(settings)

        await self._rebuild(interaction)

    async def _on_chat_toggle(self, interaction: discord.Interaction):
        guild_id = str(self.guild.id)

        settings = config.load_settings()
        if "guilds" not in settings:
            settings["guilds"] = {}
        if guild_id not in settings["guilds"]:
            settings["guilds"][guild_id] = {}

        current = settings["guilds"][guild_id].get("chat_enabled", True)
        settings["guilds"][guild_id]["chat_enabled"] = not current
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

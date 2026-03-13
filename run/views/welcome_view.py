"""
환영 메시지 UI (WelcomeLayoutView)

봇이 서버에 초대될 때 초대자에게 DM으로 보내는 환영 메시지.
Components V2 (LayoutView) 기반으로, 기본 설정(TTS 목소리)과 대시보드 링크를 제공.
"""
import discord

from run.core.config import load_settings, save_settings

DASHBOARD_URL = "https://debimarlene.com"
PROFILE_URL = "https://panel.debimarlene.com/assets/profile.webp"

# 애플리케이션 커스텀 이모지 ID
EMOJI_SETTINGS = discord.PartialEmoji(name="ui_settings", id=1481865507861958777)
EMOJI_DASHBOARD = discord.PartialEmoji(name="ui_dashboard", id=1481865509971693649)


class WelcomeLayoutView(discord.ui.LayoutView):
    """
    Components V2 기반 환영 메시지

    초대자에게 DM으로 전송.
    - 인사 메시지 + 서버 썸네일
    - TTS 기본 목소리 선택 드롭다운
    - 대시보드 링크 버튼 (서버별 설정 페이지)
    """

    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=300)
        self.guild = guild
        guild_id = str(guild.id)

        # 현재 설정 확인
        settings = load_settings()
        guild_settings = settings.get("guilds", {}).get(guild_id, {})
        current_voice = guild_settings.get("tts_voice", "debi")

        # === 상단: 인사 메시지 ===
        greeting = discord.ui.TextDisplay(
            f"## 데비&마를렌\n"
            f"**{guild.name}** 서버에 초대해주셔서 감사합니다.\n"
            f"아래에서 기본 설정을 완료하고, 대시보드에서 더 자세한 설정을 할 수 있어요."
        )
        thumbnail = discord.ui.Thumbnail(media=PROFILE_URL)
        section = discord.ui.Section(greeting, accessory=thumbnail)
        self.add_item(discord.ui.Container(section))

        # === 중단: TTS 목소리 선택 ===
        voice_options = [
            discord.SelectOption(label="데비", value="debi", description="밝고 활기찬 목소리", default=(current_voice == "debi")),
            discord.SelectOption(label="마를렌", value="marlene", description="차분하고 낮은 목소리", default=(current_voice == "marlene")),
            discord.SelectOption(label="알렉스", value="alex", description="중성적인 목소리", default=(current_voice == "alex")),
        ]
        voice_select = discord.ui.Select(
            placeholder="TTS 기본 목소리를 선택하세요",
            options=voice_options,
            custom_id=f"welcome_tts_voice_{guild_id}"
        )
        voice_select.callback = self._on_voice_select

        tts_label = discord.ui.TextDisplay("**TTS 기본 목소리**")
        self.add_item(discord.ui.Container(
            tts_label,
            discord.ui.ActionRow(voice_select)
        ))

        # === 하단: 버튼 ===
        dashboard_btn = discord.ui.Button(
            label="대시보드에서 설정하기",
            emoji=EMOJI_DASHBOARD,
            style=discord.ButtonStyle.link,
            url=f"{DASHBOARD_URL}/servers/{guild.id}"
        )
        self.add_item(discord.ui.Container(
            discord.ui.ActionRow(dashboard_btn)
        ))

    async def _on_voice_select(self, interaction: discord.Interaction):
        selected = interaction.data["values"][0]
        guild_id = str(self.guild.id)

        settings = load_settings()
        if "guilds" not in settings:
            settings["guilds"] = {}
        if guild_id not in settings["guilds"]:
            settings["guilds"][guild_id] = {}
        settings["guilds"][guild_id]["tts_voice"] = selected
        save_settings(settings)

        voice_names = {"debi": "데비", "marlene": "마를렌", "alex": "알렉스"}
        await interaction.response.send_message(
            f"**{self.guild.name}** 서버의 TTS 기본 목소리를 **{voice_names[selected]}**(으)로 설정했어요!",
            ephemeral=True
        )

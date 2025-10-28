"""
서버 설정 UI (SettingsView, ChannelSelectViewForSetting)

/설정 명령어나 환영 메시지에서 사용하는 설정 UI예요.
공지 채널, 채팅 채널을 설정할 수 있어요.
"""
import discord
import sys
from typing import Optional

from run.core import config


class SettingsView(discord.ui.View):
    """
    서버 설정 메인 UI

    두 개의 버튼으로 구성:
    - 📢 공지 채널 설정
    - 💬 채팅 채널 설정
    """
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=180)
        self.guild = guild

    def update_components(self):
        """버튼 라벨 업데이트 (설정 상태에 따라)"""
        if len(self.children) < 2:
            return

        guild_settings = config.get_guild_settings(self.guild.id)
        announcement_ch_id = guild_settings.get("ANNOUNCEMENT_CHANNEL_ID")
        chat_ch_id = guild_settings.get("CHAT_CHANNEL_ID")

        # 공지 채널 버튼 업데이트
        announcement_button = self.children[0]
        if announcement_ch_id and (ch := self.guild.get_channel(announcement_ch_id)):
            announcement_button.label = f"📢 공지 채널: #{ch.name}"
            announcement_button.style = discord.ButtonStyle.success
        else:
            announcement_button.label = "📢 공지 채널 설정"
            announcement_button.style = discord.ButtonStyle.secondary

        # 채팅 채널 버튼 업데이트
        chat_button = self.children[1]
        if chat_ch_id and (ch := self.guild.get_channel(chat_ch_id)):
            chat_button.label = f"💬 채팅 채널: #{ch.name}"
            chat_button.style = discord.ButtonStyle.success
        else:
            chat_button.label = "💬 채팅 채널 설정 (선택사항)"
            chat_button.style = discord.ButtonStyle.secondary

    @discord.ui.button(
        label="📢 공지 채널 설정",
        style=discord.ButtonStyle.secondary,
        custom_id="setting_announcement"
    )
    async def announcement_button_handler(self, interaction: discord.Interaction, button: discord.ui.Button):
        """공지 채널 설정 버튼"""
        view = ChannelSelectViewForSetting("announcement")
        await interaction.response.send_message(
            "유튜브 영상 알림을 받을 채널을 선택해주세요.",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="💬 채팅 채널 설정 (선택사항)",
        style=discord.ButtonStyle.secondary,
        custom_id="setting_chat"
    )
    async def chat_button_handler(self, interaction: discord.Interaction, button: discord.ui.Button):
        """채팅 채널 설정 버튼"""
        view = ChannelSelectViewForSetting("chat")
        await interaction.response.send_message(
            "명령어 사용을 제한할 채널을 선택해주세요 (없으면 모두 허용).",
            view=view,
            ephemeral=True
        )


class ChannelSelectViewForSetting(discord.ui.View):
    """
    채널 선택 UI

    공지 채널이나 채팅 채널을 선택하는 드롭다운 메뉴
    """
    def __init__(self, channel_type: str):
        """
        Args:
            channel_type: "announcement" 또는 "chat"
        """
        super().__init__(timeout=180)
        self.channel_type = channel_type
        label = "공지" if channel_type == "announcement" else "채팅"
        placeholder = f"#{label} 채널을 선택하세요..."

        self.select_menu = discord.ui.ChannelSelect(
            placeholder=placeholder,
            channel_types=[discord.ChannelType.text]  # 텍스트 채널만 선택 가능
        )
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        """채널 선택 시 설정 저장"""
        try:
            # 즉시 응답하여 타임아웃 방지
            await interaction.response.defer()

            channel = self.select_menu.values[0]

            if self.channel_type == "announcement":
                # 공지 채널 설정
                result = config.save_guild_settings(
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
                # 채팅 채널 설정
                result = config.save_guild_settings(
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

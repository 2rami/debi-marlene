"""
환영 메시지 UI (WelcomeView)

새로운 서버에 봇이 추가될 때 보여지는 환영 메시지의 UI예요.
- "바로 설정하기" 버튼: 서버 설정 (관리자 전용)
- "대시보드" 버튼: debimarlene.com으로 이동 (URL 링크)
"""
import discord

from run.views.settings_view import SettingsView

DASHBOARD_URL = "https://debimarlene.com"


class WelcomeView(discord.ui.View):
    """
    환영 메시지 UI

    새 서버에 초대될 때 표시되는 버튼들이에요.
    - 바로 설정하기: 서버 설정 (interaction callback)
    - 대시보드: 외부 링크 (URL button, callback 없음)
    """
    def __init__(self):
        super().__init__(timeout=None)  # 영구적으로 유지
        self.add_item(discord.ui.Button(
            label="대시보드",
            style=discord.ButtonStyle.link,
            url=DASHBOARD_URL
        ))

    @discord.ui.button(
        label="바로 설정하기",
        style=discord.ButtonStyle.success,
        custom_id="welcome_setup_button"
    )
    async def setup_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """설정 버튼 클릭 시"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "이 버튼은 서버 관리자만 사용할 수 있어요!",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="서버 설정",
            description="아래 버튼으로 유튜브 공지 채널과 명령어 전용 채널을 설정하세요.",
            color=0x7289DA
        )
        embed.add_field(
            name="[#] 공지 채널",
            value="유튜브 새 영상 알림이 올라갈 채널입니다.",
            inline=False
        )
        embed.add_field(
            name="[*] 채팅 채널",
            value="`/전적` 등 봇의 명령어를 사용할 특정 채널입니다. 설정하지 않으면 모든 채널에서 사용 가능합니다. (선택)",
            inline=False
        )
        view = SettingsView(interaction.guild)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

"""
퀴즈 게임 View/Embed

퀴즈 문제, 정답/오답, 결과 표시를 위한 Embed과 Button View를 제공합니다.
"""

import asyncio
import discord
from typing import Optional, Dict, List, Tuple


# -- Embed 생성 함수 --

def create_song_question_embed(
    question_num: int,
    total: int,
    hint: Optional[str] = None
) -> discord.Embed:
    """노래 맞추기 문제 Embed"""
    embed = discord.Embed(
        title=f"[{question_num}/{total}] 노래 맞추기",
        description="지금 재생되는 노래의 **제목** 또는 **가수**를 채팅으로 입력하세요!",
        color=0x1DB954,
    )
    embed.add_field(name="제한 시간", value="30초", inline=True)
    if hint:
        embed.add_field(name="힌트", value=hint, inline=True)
    return embed


def create_er_question_embed(
    question_num: int,
    total: int,
    question_text: str,
    image_url: Optional[str] = None,
) -> discord.Embed:
    """이터널리턴 퀴즈 문제 Embed"""
    embed = discord.Embed(
        title=f"[{question_num}/{total}] 이터널리턴 퀴즈",
        description=question_text,
        color=0x5865F2,
    )
    embed.add_field(name="제한 시간", value="20초", inline=True)
    if image_url:
        embed.set_image(url=image_url)
    return embed


def create_correct_embed(
    answer: str,
    scorer_name: str,
    detail: Optional[str] = None,
) -> discord.Embed:
    """정답 Embed"""
    desc = f"**{scorer_name}** 님이 맞혔습니다!\n정답: **{answer}**"
    if detail:
        desc = f"**{scorer_name}** - {detail}\n정답: **{answer}**"
    embed = discord.Embed(
        title="정답!",
        description=desc,
        color=0x57F287,
    )
    return embed


def create_timeout_embed(
    correct_answer: str,
    missed: Optional[str] = None,
) -> discord.Embed:
    """시간초과 Embed"""
    desc = f"아무도 맞히지 못했습니다.\n정답: **{correct_answer}**"
    if missed:
        desc = f"못 맞힌 항목: {missed}\n정답: **{correct_answer}**"
    embed = discord.Embed(
        title="시간 초과",
        description=desc,
        color=0xED4245,
    )
    return embed


def create_skip_embed(correct_answer: str) -> discord.Embed:
    """스킵 Embed"""
    embed = discord.Embed(
        title="건너뛰기",
        description=f"문제를 건너뛰었습니다.\n정답: **{correct_answer}**",
        color=0x95A5A6,
    )
    return embed


def create_result_embed(
    scores: Dict[int, int],
    total_questions: int,
    guild: discord.Guild,
) -> discord.Embed:
    """최종 결과 Embed (ER 퀴즈 등 일반용)"""
    embed = discord.Embed(
        title="퀴즈 결과",
        color=0xFEE75C,
    )

    if not scores:
        embed.description = "아무도 점수를 얻지 못했습니다."
        return embed

    rankings = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    lines = []
    medals = ["1st", "2nd", "3rd"]

    for i, (user_id, score) in enumerate(rankings):
        member = guild.get_member(user_id)
        name = member.display_name if member else f"User#{user_id}"
        rank = medals[i] if i < len(medals) else f"{i + 1}th"
        lines.append(f"**{rank}** {name} - {score}/{total_questions}")

    embed.description = "\n".join(lines)
    return embed


def create_song_result_embed(
    scores: Dict[int, int],
    title_scores: Dict[int, int],
    artist_scores: Dict[int, int],
    total_questions: int,
    guild: discord.Guild,
) -> discord.Embed:
    """노래 퀴즈 결과 Embed (제목/가수 별도 표시)"""
    embed = discord.Embed(
        title="노래 퀴즈 결과",
        color=0x1DB954,
    )

    if not scores:
        embed.description = "아무도 점수를 얻지 못했습니다."
        return embed

    rankings = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    lines = []
    medals = ["1st", "2nd", "3rd"]

    for i, (user_id, total_score) in enumerate(rankings):
        member = guild.get_member(user_id)
        name = member.display_name if member else f"User#{user_id}"
        rank = medals[i] if i < len(medals) else f"{i + 1}th"
        t_score = title_scores.get(user_id, 0)
        a_score = artist_scores.get(user_id, 0)
        lines.append(
            f"**{rank}** {name} - "
            f"총 {total_score}점 (제목 {t_score} / 가수 {a_score})"
        )

    embed.description = "\n".join(lines)
    embed.set_footer(text=f"총 {total_questions}문제")
    return embed


# -- Button View --

class ERQuizView(discord.ui.View):
    """이터널리턴 퀴즈 4지선다 버튼 View"""

    LABELS = ["A", "B", "C", "D"]
    STYLES = [
        discord.ButtonStyle.primary,
        discord.ButtonStyle.primary,
        discord.ButtonStyle.primary,
        discord.ButtonStyle.primary,
    ]

    def __init__(self, choices: list, correct_index: int, timeout: float = 20):
        super().__init__(timeout=timeout)
        self.correct_index = correct_index
        self.answered_users: set = set()
        self.result: Optional[Tuple[int, discord.Member]] = None  # (선택 인덱스, 유저)
        self._event = asyncio.Event()

        for i, choice in enumerate(choices):
            button = discord.ui.Button(
                label=f"{self.LABELS[i]}. {choice}",
                style=self.STYLES[i],
                custom_id=f"quiz_choice_{i}",
                row=0 if i < 2 else 1,
            )
            button.callback = self._make_callback(i)
            self.add_item(button)

    def _make_callback(self, index: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id in self.answered_users:
                await interaction.response.send_message(
                    "이미 답을 선택했습니다.", ephemeral=True
                )
                return

            self.answered_users.add(interaction.user.id)
            self.result = (index, interaction.user)
            self._event.set()

            if index == self.correct_index:
                await interaction.response.send_message(
                    "정답을 선택했습니다!", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "오답입니다.", ephemeral=True
                )

        return callback

    async def wait_for_answer(self) -> Optional[Tuple[int, discord.Member]]:
        """첫 번째 응답을 기다립니다. 타임아웃 시 None 반환."""
        try:
            await asyncio.wait_for(self._event.wait(), timeout=self.timeout)
            return self.result
        except asyncio.TimeoutError:
            return None

    async def on_timeout(self):
        self._event.set()
        for item in self.children:
            item.disabled = True


# -- 출제자 모드 View / Modal --

class SongSubmitModal(discord.ui.Modal, title="곡 출제"):
    """출제자가 곡 정보를 입력하는 Modal"""

    search_query = discord.ui.TextInput(
        label="YouTube 검색어 또는 URL",
        placeholder="예: NewJeans Super Shy, https://youtu.be/...",
        required=True,
        max_length=200,
    )
    song_title = discord.ui.TextInput(
        label="노래 제목 (정답)",
        placeholder="예: Super Shy",
        required=True,
        max_length=100,
    )
    song_artist = discord.ui.TextInput(
        label="가수 (정답)",
        placeholder="예: NewJeans",
        required=True,
        max_length=100,
    )

    def __init__(self):
        super().__init__()
        self._event = asyncio.Event()
        self.submitted = False

    async def on_submit(self, interaction: discord.Interaction):
        self.submitted = True
        self._event.set()
        await interaction.response.send_message(
            f"곡이 등록되었습니다! 잠시 후 재생됩니다.",
            ephemeral=True,
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        self._event.set()

    async def wait_for_submit(self, timeout: float = 120) -> bool:
        """제출을 기다립니다. 타임아웃 시 False 반환."""
        try:
            await asyncio.wait_for(self._event.wait(), timeout=timeout)
            return self.submitted
        except asyncio.TimeoutError:
            return False


class SongSubmitView(discord.ui.View):
    """출제자에게 보여줄 '곡 출제' 버튼 View"""

    def __init__(self, host_id: int, question_num: int, total: int):
        super().__init__(timeout=120)
        self.host_id = host_id
        self.modal: Optional[SongSubmitModal] = None
        self.question_num = question_num
        self.total = total
        self.cancelled = False

    @discord.ui.button(label="곡 출제하기", style=discord.ButtonStyle.success)
    async def submit_song(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host_id:
            await interaction.response.send_message(
                "출제자만 곡을 등록할 수 있습니다.", ephemeral=True
            )
            return

        self.modal = SongSubmitModal()
        await interaction.response.send_modal(self.modal)

    @discord.ui.button(label="퀴즈 종료", style=discord.ButtonStyle.danger)
    async def cancel_quiz(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host_id:
            await interaction.response.send_message(
                "출제자만 종료할 수 있습니다.", ephemeral=True
            )
            return

        self.cancelled = True
        if self.modal:
            self.modal._event.set()
        await interaction.response.send_message(
            "출제자가 퀴즈를 종료합니다.", ephemeral=True
        )
        self.stop()

    async def wait_for_song(self) -> Optional[SongSubmitModal]:
        """출제자가 곡을 제출할 때까지 기다립니다."""
        while not self.is_finished():
            if self.cancelled:
                return None
            if self.modal:
                submitted = await self.modal.wait_for_submit()
                if submitted:
                    return self.modal
                self.modal = None
            await asyncio.sleep(0.5)
        return None

"""
퀴즈 게임 Cog

/퀴즈 - 퀴즈 유형 선택 (버튼) + 문제 수 선택 (드롭다운)
"""

import asyncio
import logging
import time

import discord
from discord import app_commands
from discord.ext import commands

from run.services.quiz.quiz_manager import QuizManager
from run.services.quiz.er_quiz import generate_er_question
from run.services.quiz.song_quiz import (
    SongQuiz, SongEntry, check_answer, get_title_hint, get_artist_hint,
    ANSWER_TIMEOUT, HINT_DELAY,
)
from run.services.voice_manager import voice_manager
from run.views.quiz_view import (
    create_song_question_embed,
    create_er_question_embed,
    create_correct_embed,
    create_timeout_embed,
    create_skip_embed,
    create_song_result_embed,
    create_result_embed,
    ERQuizView,
    SongSubmitView,
    SongSkipView,
)
from run.services.quiz.quiz_storage import async_save_quiz_result, async_update_leaderboard_names
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

SECOND_HINT_REMAINING = 5


class QuizCog(commands.Cog, name="퀴즈"):
    """퀴즈 게임 관련 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="퀴즈", description="퀴즈 게임을 시작합니다")
    async def quiz(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)

        if QuizManager.has_active_session(guild_id):
            # 진행 중이면 중지 버튼만 보여주기
            view = QuizStopView(guild_id, self)
            await interaction.response.send_message(
                "이미 진행 중인 퀴즈가 있습니다.",
                view=view,
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="퀴즈 게임",
            description="퀴즈 유형을 선택하세요!\n문제 수는 드롭다운에서 변경할 수 있어요.",
            color=0x5865F2,
        )
        view = QuizStartView(self, interaction)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()

    # ---------- 공통 노래 답변 루프 ----------

    async def _song_answer_loop(
        self,
        channel: discord.abc.Messageable,
        session,
        song: SongEntry,
        stream_info: str,
        question_num: int,
        total: int,
        guild_id: str,
        exclude_user_id: int = None,
    ):
        """노래 퀴즈 한 문제의 재생, 힌트, 답변, 스킵을 처리합니다."""

        vc = voice_manager.get_voice_client(guild_id)
        member_count = max(1, len([m for m in vc.channel.members if not m.bot])) if vc else 1
        skip_view = SongSkipView(guild_id, member_count)

        embed = create_song_question_embed(question_num, total)
        question_msg = await channel.send(embed=embed, view=skip_view)

        play_task = asyncio.create_task(
            SongQuiz.play_clip(guild_id, stream_info, 180)
        )

        answered = False
        title_answered = False
        artist_answered = False

        async def send_hints():
            await asyncio.sleep(HINT_DELAY)
            if not answered and session.is_active and not title_answered:
                h = get_title_hint(song.title)
                await channel.send(embed=create_song_question_embed(
                    question_num, total, hint=f"제목: {h}"
                ))

            second_delay = ANSWER_TIMEOUT - HINT_DELAY - SECOND_HINT_REMAINING
            await asyncio.sleep(second_delay)
            if not answered and session.is_active and not artist_answered:
                await channel.send(embed=create_song_question_embed(
                    question_num, total, hint=get_artist_hint(song)
                ))

        hint_task = asyncio.create_task(send_hints())

        def msg_check(msg: discord.Message) -> bool:
            if msg.channel.id != session.channel_id or msg.author.bot:
                return False
            if exclude_user_id and msg.author.id == exclude_user_id:
                return False
            result = check_answer(msg.content, song)
            if result == "title" and not title_answered:
                return True
            if result == "artist" and not artist_answered:
                return True
            return False

        remaining_timeout = ANSWER_TIMEOUT
        skipped = False
        skip_wait = asyncio.create_task(skip_view._skip_event.wait())
        stop_wait = asyncio.create_task(session._stop_event.wait())

        while not answered and session.is_active:
            start_time = time.monotonic()
            msg_wait = asyncio.create_task(
                self.bot.wait_for('message', check=msg_check, timeout=remaining_timeout)
            )

            done, _ = await asyncio.wait(
                {msg_wait, skip_wait, stop_wait}, return_when=asyncio.FIRST_COMPLETED
            )

            if stop_wait in done:
                msg_wait.cancel()
                try:
                    await msg_wait
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
                break

            if skip_wait in done:
                msg_wait.cancel()
                try:
                    await msg_wait
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
                skipped = True
                answered = True
                break

            try:
                msg = msg_wait.result()
            except asyncio.TimeoutError:
                answered = True
                break

            elapsed = time.monotonic() - start_time
            remaining_timeout = max(1, remaining_timeout - elapsed)

            result = check_answer(msg.content, song)
            if result == "title" and not title_answered:
                title_answered = True
                session.add_title_score(msg.author.id)
                await channel.send(embed=create_correct_embed(
                    song.title, msg.author.display_name, detail="제목 정답!"
                ))
            elif result == "artist" and not artist_answered:
                artist_answered = True
                session.add_artist_score(msg.author.id)
                await channel.send(embed=create_correct_embed(
                    song.artist, msg.author.display_name, detail="가수 정답!"
                ))

            if title_answered and artist_answered:
                answered = True

        if not stop_wait.done():
            stop_wait.cancel()
        if not skip_wait.done():
            skip_wait.cancel()
        hint_task.cancel()
        SongQuiz.stop_playback(guild_id)
        play_task.cancel()

        for item in skip_view.children:
            item.disabled = True
        try:
            await question_msg.edit(view=skip_view)
        except Exception:
            pass

        if not session.is_active:
            return
        if skipped:
            await channel.send(embed=create_skip_embed(f"{song.title} - {song.artist}"))
        elif not (title_answered and artist_answered):
            parts = []
            if not title_answered:
                parts.append(f"제목: {song.title}")
            if not artist_answered:
                parts.append(f"가수: {song.artist}")
            await channel.send(embed=create_timeout_embed(
                f"{song.title} - {song.artist}",
                missed=", ".join(parts) if parts else None,
            ))

        await asyncio.sleep(3)

    # ---------- 퀴즈 실행 메서드 ----------

    async def _run_song_quiz(self, interaction: discord.Interaction, total: int):
        """노래 맞추기 퀴즈를 실행합니다."""
        guild_id = str(interaction.guild.id)

        await log_command_usage(
            command_name="퀴즈노래",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            channel_id=interaction.channel_id,
            channel_name=interaction.channel.name if interaction.channel else None,
            args={"문제수": total},
        )

        success = await voice_manager.join(interaction.user.voice.channel)
        if not success:
            await interaction.channel.send("음성 채널 입장에 실패했습니다.")
            return

        session = QuizManager.start_session(guild_id, interaction.channel_id, "song", total)
        song_quiz_instance = SongQuiz(guild_id, total)

        start_embed = discord.Embed(
            title="노래 맞추기 시작!",
            description=(
                f"총 {total}문제 | 채팅으로 제목 또는 가수를 입력하세요\n"
                "제목/가수 점수가 따로 집계됩니다"
            ),
            color=0x1DB954,
        )
        await interaction.channel.send(embed=start_embed)
        await asyncio.sleep(2)

        channel = interaction.channel

        for i in range(total):
            if not session.is_active:
                break

            session.current_question = i + 1
            song = song_quiz_instance.pick_song()
            if not song:
                await channel.send("곡 데이터를 불러올 수 없습니다.")
                break

            stream_info = await SongQuiz.get_stream_url(song, interaction.guild.me)
            if not stream_info:
                await channel.send(f"[{i + 1}/{total}] 곡을 검색할 수 없어 건너뜁니다.")
                continue

            await self._song_answer_loop(
                channel, session, song, stream_info, i + 1, total, guild_id
            )

        final_session = QuizManager.end_session(guild_id)
        if final_session:
            embed = create_song_result_embed(
                final_session.scores,
                final_session.title_scores,
                final_session.artist_scores,
                final_session.total_questions,
                interaction.guild,
            )
            await channel.send(embed=embed)
            await self._save_result(guild_id, final_session, interaction.guild, channel)

    async def _run_er_quiz(self, interaction: discord.Interaction, total: int):
        """이터널리턴 퀴즈를 실행합니다."""
        guild_id = str(interaction.guild.id)

        await log_command_usage(
            command_name="퀴즈이터널리턴",
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.name,
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            channel_id=interaction.channel_id,
            channel_name=interaction.channel.name if interaction.channel else None,
            args={"문제수": total},
        )

        session = QuizManager.start_session(guild_id, interaction.channel_id, "er", total)

        start_embed = discord.Embed(
            title="이터널리턴 퀴즈 시작!",
            description=f"총 {total}문제 | 버튼을 눌러 정답을 선택하세요",
            color=0x5865F2,
        )
        await interaction.channel.send(embed=start_embed)
        await asyncio.sleep(2)

        channel = interaction.channel

        for i in range(total):
            if not session.is_active:
                break

            session.current_question = i + 1
            question = generate_er_question()

            if not question:
                await channel.send(f"[{i + 1}/{total}] 문제 생성에 실패하여 건너뜁니다.")
                continue

            embed = create_er_question_embed(
                i + 1, total, question.question_text, question.image_url
            )
            view = ERQuizView(question.choices, question.correct_index)
            msg = await channel.send(embed=embed, view=view)

            answer_task = asyncio.create_task(view.wait_for_answer())
            stop_task = asyncio.create_task(session._stop_event.wait())
            done, _ = await asyncio.wait(
                {answer_task, stop_task}, return_when=asyncio.FIRST_COMPLETED
            )
            if stop_task in done:
                answer_task.cancel()
                try:
                    await answer_task
                except asyncio.CancelledError:
                    pass
                for item in view.children:
                    item.disabled = True
                try:
                    await msg.edit(view=view)
                except Exception:
                    pass
                break
            if not stop_task.done():
                stop_task.cancel()
            result = answer_task.result()

            for item in view.children:
                item.disabled = True
            try:
                await msg.edit(view=view)
            except Exception:
                pass

            if result is not None:
                chosen_index, user = result
                if chosen_index == question.correct_index:
                    session.add_score(user.id)
                    embed = create_correct_embed(
                        question.correct_answer, user.display_name
                    )
                else:
                    embed = create_timeout_embed(question.correct_answer)
            else:
                embed = create_timeout_embed(question.correct_answer)

            await channel.send(embed=embed)
            await asyncio.sleep(3)

        final_session = QuizManager.end_session(guild_id)
        if final_session:
            embed = create_result_embed(
                final_session.scores, final_session.total_questions, interaction.guild
            )
            await channel.send(embed=embed)
            await self._save_result(guild_id, final_session, interaction.guild, channel)

    async def _run_custom_song_quiz(self, interaction: discord.Interaction, total: int):
        """노래 출제 모드를 실행합니다."""
        guild_id = str(interaction.guild.id)
        host = interaction.user

        await log_command_usage(
            command_name="퀴즈노래출제",
            user_id=host.id,
            user_name=host.display_name or host.name,
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            channel_id=interaction.channel_id,
            channel_name=interaction.channel.name if interaction.channel else None,
            args={"문제수": total},
        )

        success = await voice_manager.join(host.voice.channel)
        if not success:
            await interaction.channel.send("음성 채널 입장에 실패했습니다.")
            return

        session = QuizManager.start_session(guild_id, interaction.channel_id, "song", total)
        channel = interaction.channel

        start_embed = discord.Embed(
            title="노래 출제 모드!",
            description=(
                f"출제자: **{host.display_name}** | 총 {total}문제\n"
                "출제자가 곡을 등록하면 나머지가 맞추는 방식입니다.\n"
                "제목/가수 점수가 따로 집계됩니다"
            ),
            color=0xFF9B00,
        )
        await channel.send(embed=start_embed)
        await asyncio.sleep(1)

        for i in range(total):
            if not session.is_active:
                break

            session.current_question = i + 1

            submit_view = SongSubmitView(host.id, i + 1, total)
            prompt_embed = discord.Embed(
                title=f"[{i + 1}/{total}] 곡 출제 대기중",
                description=f"**{host.display_name}** 님, 아래 버튼을 눌러 곡을 등록해주세요.",
                color=0xFF9B00,
            )
            prompt_msg = await channel.send(embed=prompt_embed, view=submit_view)

            song_task = asyncio.create_task(submit_view.wait_for_song())
            stop_task = asyncio.create_task(session._stop_event.wait())
            done, _ = await asyncio.wait(
                {song_task, stop_task}, return_when=asyncio.FIRST_COMPLETED
            )
            if stop_task in done:
                song_task.cancel()
                submit_view.cancelled = True
                submit_view.stop()
                try:
                    await song_task
                except asyncio.CancelledError:
                    pass
                for item in submit_view.children:
                    item.disabled = True
                try:
                    await prompt_msg.edit(view=submit_view)
                except Exception:
                    pass
                break
            if not stop_task.done():
                stop_task.cancel()
            modal = song_task.result()

            for item in submit_view.children:
                item.disabled = True
            try:
                await prompt_msg.edit(view=submit_view)
            except Exception:
                pass

            if not modal or submit_view.cancelled or not session.is_active:
                break

            song = SongEntry(
                title=modal.song_title.value.strip(),
                artist=modal.song_artist.value.strip(),
                query=modal.search_query.value.strip(),
            )

            stream_info = await SongQuiz.get_stream_url(song, interaction.guild.me)
            if not stream_info:
                await channel.send(f"[{i + 1}/{total}] 곡을 검색할 수 없어 건너뜁니다.")
                continue

            await self._song_answer_loop(
                channel, session, song, stream_info, i + 1, total, guild_id,
                exclude_user_id=host.id,
            )

        final_session = QuizManager.end_session(guild_id)
        if final_session:
            embed = create_song_result_embed(
                final_session.scores,
                final_session.title_scores,
                final_session.artist_scores,
                final_session.total_questions,
                interaction.guild,
            )
            await channel.send(embed=embed)
            await self._save_result(guild_id, final_session, interaction.guild, channel)

    # ---------- 결과 저장 헬퍼 ----------

    @staticmethod
    async def _save_result(guild_id: str, session, guild: discord.Guild, channel: discord.abc.Messageable = None):
        """퀴즈 결과를 GCS에 비동기로 저장합니다."""
        if not session.scores:
            return
        try:
            success = await async_save_quiz_result(guild_id, session)
            if not success:
                logger.error(f"퀴즈 결과 저장 반환값 실패: guild={guild_id}")
                if channel:
                    await channel.send("퀴즈 결과 저장에 실패했습니다. 관리자에게 문의하세요.")
                return

            members = {}
            for user_id in session.scores:
                member = guild.get_member(user_id)
                if member:
                    members[user_id] = member.display_name
            if members:
                await async_update_leaderboard_names(guild_id, members)
        except Exception as e:
            logger.error(f"퀴즈 결과 저장 중 오류: {e}")
            if channel:
                await channel.send("퀴즈 결과 저장 중 오류가 발생했습니다. 관리자에게 문의하세요.")


# ---------- 퀴즈 시작 뷰 ----------

class QuizStartView(discord.ui.View):
    """퀴즈 유형 선택 + 문제 수 선택 뷰"""

    def __init__(self, cog: QuizCog, interaction: discord.Interaction):
        super().__init__(timeout=60)
        self.cog = cog
        self.original_interaction = interaction
        self.question_count = 5
        self.message = None

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except Exception:
                pass

    @discord.ui.select(
        placeholder="문제 수 (기본: 5)",
        options=[
            discord.SelectOption(label="5문제", value="5", default=True),
            discord.SelectOption(label="10문제", value="10"),
            discord.SelectOption(label="15문제", value="15"),
        ],
        row=0,
    )
    async def count_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.question_count = int(select.values[0])
        await interaction.response.defer()

    @discord.ui.button(label="노래 맞추기", style=discord.ButtonStyle.primary, row=1)
    async def song_quiz_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice:
            await interaction.response.send_message("먼저 음성 채널에 입장해주세요!", ephemeral=True)
            return

        # 버튼 비활성화
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content=f"노래 맞추기 {self.question_count}문제 시작!", embed=None, view=self
        )
        self.stop()
        asyncio.create_task(self.cog._run_song_quiz(self.original_interaction, self.question_count))

    @discord.ui.button(label="이터널리턴", style=discord.ButtonStyle.primary, row=1)
    async def er_quiz_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content=f"이터널리턴 퀴즈 {self.question_count}문제 시작!", embed=None, view=self
        )
        self.stop()
        asyncio.create_task(self.cog._run_er_quiz(self.original_interaction, self.question_count))

    @discord.ui.button(label="노래 출제", style=discord.ButtonStyle.secondary, row=1)
    async def custom_quiz_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice:
            await interaction.response.send_message("먼저 음성 채널에 입장해주세요!", ephemeral=True)
            return

        # 노래 출제는 3/5/10 옵션
        count = min(self.question_count, 10)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content=f"노래 출제 모드 {count}문제 시작!", embed=None, view=self
        )
        self.stop()
        asyncio.create_task(self.cog._run_custom_song_quiz(self.original_interaction, count))


class QuizStopView(discord.ui.View):
    """진행 중인 퀴즈 중지 뷰"""

    def __init__(self, guild_id: str, cog: QuizCog):
        super().__init__(timeout=30)
        self.guild_id = guild_id
        self.cog = cog

    @discord.ui.button(label="퀴즈 중지", style=discord.ButtonStyle.danger)
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        session = QuizManager.get_session(self.guild_id)
        if not session:
            await interaction.response.send_message("진행 중인 퀴즈가 없습니다.", ephemeral=True)
            return

        await interaction.response.defer()

        final_session = QuizManager.end_session(self.guild_id)

        if session.quiz_type == "song":
            SongQuiz.stop_playback(self.guild_id)

        if final_session and final_session.scores:
            if session.quiz_type == "song":
                embed = create_song_result_embed(
                    final_session.scores,
                    final_session.title_scores,
                    final_session.artist_scores,
                    final_session.current_question,
                    interaction.guild,
                )
            else:
                embed = create_result_embed(
                    final_session.scores, final_session.current_question, interaction.guild
                )
            await interaction.followup.send(content="퀴즈가 중단되었습니다.", embed=embed)
            await self.cog._save_result(self.guild_id, final_session, interaction.guild, interaction.channel)
        else:
            await interaction.followup.send("퀴즈가 중단되었습니다.")

        button.disabled = True
        try:
            await interaction.message.edit(view=self)
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(QuizCog(bot))

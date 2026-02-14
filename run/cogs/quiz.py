"""
퀴즈 게임 Cog

/퀴즈 노래 - 노래 맞추기
/퀴즈 노래출제 - 출제자가 직접 곡을 골라 출제
/퀴즈 이터널리턴 - 이터널리턴 4지선다 퀴즈
/퀴즈 중지 - 진행 중인 퀴즈 중단
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
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

SECOND_HINT_REMAINING = 5  # 2차 힌트: 종료 5초 전


class QuizCog(commands.GroupCog, group_name="퀴즈"):
    """퀴즈 게임 관련 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

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

        # 스킵 버튼 (음성 채널 전원 투표)
        vc = voice_manager.get_voice_client(guild_id)
        member_count = max(1, len([m for m in vc.channel.members if not m.bot])) if vc else 1
        skip_view = SongSkipView(guild_id, member_count)

        # 문제 Embed + 스킵 버튼 전송
        embed = create_song_question_embed(question_num, total)
        question_msg = await channel.send(embed=embed, view=skip_view)

        # 클립 재생
        play_task = asyncio.create_task(
            SongQuiz.play_clip(guild_id, stream_info, 180)
        )

        answered = False
        title_answered = False
        artist_answered = False

        # 2단계 힌트
        async def send_hints():
            # 1차: 제목 초성 (HINT_DELAY초 후)
            await asyncio.sleep(HINT_DELAY)
            if not answered and session.is_active and not title_answered:
                h = get_title_hint(song.title)
                await channel.send(embed=create_song_question_embed(
                    question_num, total, hint=f"제목: {h}"
                ))

            # 2차: 가수 (종료 5초 전)
            second_delay = ANSWER_TIMEOUT - HINT_DELAY - SECOND_HINT_REMAINING
            await asyncio.sleep(second_delay)
            if not answered and session.is_active and not artist_answered:
                await channel.send(embed=create_song_question_embed(
                    question_num, total, hint=get_artist_hint(song)
                ))

        hint_task = asyncio.create_task(send_hints())

        # 정답 판정 (스킵은 버튼으로만)
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

            # 중지 명령
            if stop_wait in done:
                msg_wait.cancel()
                try:
                    await msg_wait
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
                break

            # 스킵 투표 완료
            if skip_wait in done:
                msg_wait.cancel()
                try:
                    await msg_wait
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
                skipped = True
                answered = True
                break

            # 메시지 수신 또는 타임아웃
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

        # 정리
        if not stop_wait.done():
            stop_wait.cancel()
        if not skip_wait.done():
            skip_wait.cancel()
        hint_task.cancel()
        SongQuiz.stop_playback(guild_id)
        play_task.cancel()

        # 스킵 버튼 비활성화
        for item in skip_view.children:
            item.disabled = True
        try:
            await question_msg.edit(view=skip_view)
        except Exception:
            pass

        # 결과 Embed (중지 시에는 표시하지 않음)
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

    # ---------- /퀴즈 노래 ----------

    @app_commands.command(name="노래", description="노래 맞추기 퀴즈를 시작합니다")
    @app_commands.describe(문제수="문제 수를 선택하세요")
    @app_commands.choices(문제수=[
        app_commands.Choice(name="5문제", value=5),
        app_commands.Choice(name="10문제", value=10),
        app_commands.Choice(name="15문제", value=15),
    ])
    async def song_quiz(
        self,
        interaction: discord.Interaction,
        문제수: app_commands.Choice[int] = None,
    ):
        if not interaction.guild:
            await interaction.response.send_message(
                "서버에서만 사용할 수 있습니다.", ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)

        if QuizManager.has_active_session(guild_id):
            await interaction.response.send_message(
                "이미 진행 중인 퀴즈가 있습니다. `/퀴즈 중지`로 먼저 종료해주세요.",
                ephemeral=True,
            )
            return

        if not interaction.user.voice:
            await interaction.response.send_message(
                "먼저 음성 채널에 입장해주세요!", ephemeral=True
            )
            return

        total = 문제수.value if 문제수 else 5
        await interaction.response.defer()

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

        # 음성 채널 입장
        success = await voice_manager.join(interaction.user.voice.channel)
        if not success:
            await interaction.followup.send("음성 채널 입장에 실패했습니다.", ephemeral=True)
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
        await interaction.followup.send(embed=start_embed)
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

        # 결과 표시
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

    # ---------- /퀴즈 이터널리턴 ----------

    @app_commands.command(name="이터널리턴", description="이터널리턴 퀴즈를 시작합니다")
    @app_commands.describe(문제수="문제 수를 선택하세요")
    @app_commands.choices(문제수=[
        app_commands.Choice(name="5문제", value=5),
        app_commands.Choice(name="10문제", value=10),
        app_commands.Choice(name="15문제", value=15),
    ])
    async def er_quiz(
        self,
        interaction: discord.Interaction,
        문제수: app_commands.Choice[int] = None,
    ):
        if not interaction.guild:
            await interaction.response.send_message(
                "서버에서만 사용할 수 있습니다.", ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)

        if QuizManager.has_active_session(guild_id):
            await interaction.response.send_message(
                "이미 진행 중인 퀴즈가 있습니다. `/퀴즈 중지`로 먼저 종료해주세요.",
                ephemeral=True,
            )
            return

        total = 문제수.value if 문제수 else 5
        await interaction.response.defer()

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
        await interaction.followup.send(embed=start_embed)
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

            # wait_for_answer와 stop_event를 경쟁
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
                # 버튼 비활성화 후 break
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

    # ---------- /퀴즈 노래출제 ----------

    @app_commands.command(name="노래출제", description="출제자가 직접 곡을 골라 노래 퀴즈를 출제합니다")
    @app_commands.describe(문제수="문제 수를 선택하세요")
    @app_commands.choices(문제수=[
        app_commands.Choice(name="3문제", value=3),
        app_commands.Choice(name="5문제", value=5),
        app_commands.Choice(name="10문제", value=10),
    ])
    async def custom_song_quiz(
        self,
        interaction: discord.Interaction,
        문제수: app_commands.Choice[int] = None,
    ):
        if not interaction.guild:
            await interaction.response.send_message(
                "서버에서만 사용할 수 있습니다.", ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)

        if QuizManager.has_active_session(guild_id):
            await interaction.response.send_message(
                "이미 진행 중인 퀴즈가 있습니다. `/퀴즈 중지`로 먼저 종료해주세요.",
                ephemeral=True,
            )
            return

        if not interaction.user.voice:
            await interaction.response.send_message(
                "먼저 음성 채널에 입장해주세요!", ephemeral=True
            )
            return

        total = 문제수.value if 문제수 else 5
        host = interaction.user
        await interaction.response.defer()

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
            await interaction.followup.send("음성 채널 입장에 실패했습니다.", ephemeral=True)
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
        await interaction.followup.send(embed=start_embed)
        await asyncio.sleep(1)

        for i in range(total):
            if not session.is_active:
                break

            session.current_question = i + 1

            # 출제 버튼 전송
            submit_view = SongSubmitView(host.id, i + 1, total)
            prompt_embed = discord.Embed(
                title=f"[{i + 1}/{total}] 곡 출제 대기중",
                description=f"**{host.display_name}** 님, 아래 버튼을 눌러 곡을 등록해주세요.",
                color=0xFF9B00,
            )
            prompt_msg = await channel.send(embed=prompt_embed, view=submit_view)

            # wait_for_song과 stop_event를 경쟁
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

        # 결과 표시
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

    # ---------- /퀴즈 중지 ----------

    @app_commands.command(name="중지", description="진행 중인 퀴즈를 중단합니다")
    async def stop_quiz(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message(
                "서버에서만 사용할 수 있습니다.", ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)
        session = QuizManager.get_session(guild_id)

        if not session:
            await interaction.response.send_message(
                "진행 중인 퀴즈가 없습니다.", ephemeral=True
            )
            return

        await interaction.response.defer()

        final_session = QuizManager.end_session(guild_id)

        if session.quiz_type == "song":
            SongQuiz.stop_playback(guild_id)

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
        else:
            await interaction.followup.send("퀴즈가 중단되었습니다.")


async def setup(bot: commands.Bot):
    await bot.add_cog(QuizCog(bot))

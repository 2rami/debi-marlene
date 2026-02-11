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
    SongQuiz, SongEntry, check_answer, is_skip_command, get_hint,
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
)
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)


class QuizCog(commands.GroupCog, group_name="퀴즈"):
    """퀴즈 게임 관련 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

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
        song_quiz = SongQuiz(guild_id, total)

        start_embed = discord.Embed(
            title="노래 맞추기 시작!",
            description=(
                f"총 {total}문제 | 채팅으로 제목 또는 가수를 입력하세요\n"
                "제목/가수 점수가 따로 집계됩니다. '스킵'으로 넘기기 가능"
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
            song = song_quiz.pick_song()
            if not song:
                await channel.send("곡 데이터를 불러올 수 없습니다.")
                break

            # YouTube 검색
            stream_info = await SongQuiz.get_stream_url(song, interaction.guild.me)
            if not stream_info:
                await channel.send(f"[{i + 1}/{total}] 곡을 검색할 수 없어 건너뜁니다.")
                continue

            # 문제 Embed 전송
            embed = create_song_question_embed(i + 1, total)
            await channel.send(embed=embed)

            # 클립 재생 (비동기 - 재생 중에 정답 감시)
            play_task = asyncio.create_task(
                SongQuiz.play_clip(guild_id, stream_info, 180)
            )

            # 정답 감시
            answered = False
            hint_sent = False
            title_answered = False
            artist_answered = False

            async def send_hint():
                nonlocal hint_sent
                await asyncio.sleep(HINT_DELAY)
                if not answered and session.is_active:
                    hint_sent = True
                    hint_text = get_hint(song)
                    hint_embed = create_song_question_embed(i + 1, total, hint=hint_text)
                    await channel.send(embed=hint_embed)

            hint_task = asyncio.create_task(send_hint())

            def msg_check(msg: discord.Message) -> bool:
                if msg.channel.id != session.channel_id:
                    return False
                if msg.author.bot:
                    return False
                if is_skip_command(msg.content):
                    return True
                result = check_answer(msg.content, song)
                if result == "title" and not title_answered:
                    return True
                if result == "artist" and not artist_answered:
                    return True
                return False

            # 제목과 가수 모두 맞힐 때까지 또는 타임아웃까지 반복
            remaining_timeout = ANSWER_TIMEOUT
            skipped = False

            while not answered and session.is_active:
                try:
                    start_time = time.monotonic()
                    msg = await self.bot.wait_for(
                        'message', check=msg_check, timeout=remaining_timeout
                    )
                    elapsed = time.monotonic() - start_time
                    remaining_timeout = max(1, remaining_timeout - elapsed)

                    # 스킵 처리
                    if is_skip_command(msg.content):
                        answered = True
                        skipped = True
                        break

                    result = check_answer(msg.content, song)
                    answer_str = f"{song.title} - {song.artist}"

                    if result == "title" and not title_answered:
                        title_answered = True
                        session.add_title_score(msg.author.id)
                        embed = create_correct_embed(
                            song.title, msg.author.display_name,
                            detail="제목 정답!"
                        )
                        await channel.send(embed=embed)
                    elif result == "artist" and not artist_answered:
                        artist_answered = True
                        session.add_artist_score(msg.author.id)
                        embed = create_correct_embed(
                            song.artist, msg.author.display_name,
                            detail="가수 정답!"
                        )
                        await channel.send(embed=embed)

                    if title_answered and artist_answered:
                        answered = True

                except asyncio.TimeoutError:
                    answered = True

            hint_task.cancel()
            SongQuiz.stop_playback(guild_id)
            play_task.cancel()

            if skipped:
                embed = create_skip_embed(f"{song.title} - {song.artist}")
                await channel.send(embed=embed)
            elif not (title_answered and artist_answered):
                parts = []
                if not title_answered:
                    parts.append(f"제목: {song.title}")
                if not artist_answered:
                    parts.append(f"가수: {song.artist}")
                embed = create_timeout_embed(
                    f"{song.title} - {song.artist}",
                    missed=", ".join(parts) if parts else None,
                )
                await channel.send(embed=embed)

            await asyncio.sleep(3)

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

        # 음성 채널 퇴장
        await voice_manager.leave(guild_id)

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

            # 문제 Embed + 버튼
            embed = create_er_question_embed(
                i + 1, total, question.question_text, question.image_url
            )
            view = ERQuizView(question.choices, question.correct_index)
            msg = await channel.send(embed=embed, view=view)

            # 응답 대기
            result = await view.wait_for_answer()

            # 버튼 비활성화
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

        # 결과 표시
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

        # 음성 채널 입장
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
                "제목/가수 점수가 따로 집계됩니다. '스킵'으로 넘기기 가능"
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

            # 출제자 입력 대기
            modal = await submit_view.wait_for_song()

            # 버튼 비활성화
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

            # YouTube 검색
            stream_info = await SongQuiz.get_stream_url(song, interaction.guild.me)
            if not stream_info:
                await channel.send(f"[{i + 1}/{total}] 곡을 검색할 수 없어 건너뜁니다.")
                continue

            # 문제 Embed 전송
            embed = create_song_question_embed(i + 1, total)
            await channel.send(embed=embed)

            # 클립 재생
            play_task = asyncio.create_task(
                SongQuiz.play_clip(guild_id, stream_info, 180)
            )

            # 정답 감시 (출제자 제외)
            answered = False
            hint_sent = False
            title_answered = False
            artist_answered = False

            async def send_hint():
                nonlocal hint_sent
                await asyncio.sleep(HINT_DELAY)
                if not answered and session.is_active:
                    hint_sent = True
                    hint_text = get_hint(song)
                    hint_embed = create_song_question_embed(i + 1, total, hint=hint_text)
                    await channel.send(embed=hint_embed)

            hint_task = asyncio.create_task(send_hint())

            def msg_check(msg: discord.Message) -> bool:
                if msg.channel.id != session.channel_id:
                    return False
                if msg.author.bot:
                    return False
                # 출제자 본인은 정답 입력 불가 (스킵만 가능)
                if msg.author.id == host.id:
                    return is_skip_command(msg.content)
                if is_skip_command(msg.content):
                    return True
                result = check_answer(msg.content, song)
                if result == "title" and not title_answered:
                    return True
                if result == "artist" and not artist_answered:
                    return True
                return False

            remaining_timeout = ANSWER_TIMEOUT
            skipped = False

            while not answered and session.is_active:
                try:
                    start_time = time.monotonic()
                    msg = await self.bot.wait_for(
                        'message', check=msg_check, timeout=remaining_timeout
                    )
                    elapsed = time.monotonic() - start_time
                    remaining_timeout = max(1, remaining_timeout - elapsed)

                    if is_skip_command(msg.content):
                        answered = True
                        skipped = True
                        break

                    result = check_answer(msg.content, song)

                    if result == "title" and not title_answered:
                        title_answered = True
                        session.add_title_score(msg.author.id)
                        embed = create_correct_embed(
                            song.title, msg.author.display_name,
                            detail="제목 정답!"
                        )
                        await channel.send(embed=embed)
                    elif result == "artist" and not artist_answered:
                        artist_answered = True
                        session.add_artist_score(msg.author.id)
                        embed = create_correct_embed(
                            song.artist, msg.author.display_name,
                            detail="가수 정답!"
                        )
                        await channel.send(embed=embed)

                    if title_answered and artist_answered:
                        answered = True

                except asyncio.TimeoutError:
                    answered = True

            hint_task.cancel()
            SongQuiz.stop_playback(guild_id)
            play_task.cancel()

            if skipped:
                embed = create_skip_embed(f"{song.title} - {song.artist}")
                await channel.send(embed=embed)
            elif not (title_answered and artist_answered):
                parts = []
                if not title_answered:
                    parts.append(f"제목: {song.title}")
                if not artist_answered:
                    parts.append(f"가수: {song.artist}")
                embed = create_timeout_embed(
                    f"{song.title} - {song.artist}",
                    missed=", ".join(parts) if parts else None,
                )
                await channel.send(embed=embed)

            await asyncio.sleep(3)

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

        # 음성 채널 퇴장
        await voice_manager.leave(guild_id)

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

        # 세션 종료
        final_session = QuizManager.end_session(guild_id)

        # 노래 퀴즈면 재생 중지 + 음성 퇴장
        if session.quiz_type == "song":
            SongQuiz.stop_playback(guild_id)
            await voice_manager.leave(guild_id)

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

"""
AI 채팅 명령어

LLM을 사용하여 봇과 대화할 수 있습니다.
"""

import discord
from discord.ext import commands
import logging

from run.utils.llm_manager import LLMManager
from run.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)


class ChatCog(commands.Cog):
    """AI 채팅 기능을 제공하는 Cog"""

    def __init__(self, bot):
        self.bot = bot
        # LLM 관리자 초기화
        self.llm = LLMManager(
            model='qwen2.5:7b',
            max_history=20,
            ollama_url='http://localhost:11434'
        )

        logger.info("ChatCog 초기화 완료")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        메시지가 올 때마다 실행
        봇이 멘션되면 LLM으로 응답합니다.
        """
        # 봇 자신의 메시지는 무시
        if message.author.bot:
            return

        # 봇이 멘션되지 않았으면 무시
        if not self.bot.user.mentioned_in(message):
            return

        # 멘션 제거한 실제 메시지 내용
        content = message.content
        for mention in message.mentions:
            content = content.replace(f'<@{mention.id}>', '').strip()
            content = content.replace(f'<@!{mention.id}>', '').strip()

        if not content:
            await message.reply("무엇을 도와드릴까요?")
            return

        # 타이핑 표시
        async with message.channel.typing():
            try:
                # LLM 응답 생성
                response = await self.llm.get_response(
                    channel_id=message.channel.id,
                    user_message=content,
                    username=message.author.display_name,
                    system_prompt="당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 한국어로 자연스럽게 대화하며, 사용자의 질문에 정확하고 유용한 답변을 제공합니다."
                )

                # 응답이 너무 길면 분할
                if len(response) > 2000:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    for chunk in chunks:
                        await message.reply(chunk)
                else:
                    await message.reply(response)

                # 명령어 사용 로깅
                await log_command_usage(
                    command_name="AI 채팅",
                    user_id=message.author.id,
                    user_name=message.author.display_name or message.author.name,
                    guild_id=message.guild.id if message.guild else None,
                    guild_name=message.guild.name if message.guild else None,
                    args={"메시지": content[:50] + "..." if len(content) > 50 else content}
                )

            except Exception as e:
                logger.error(f"AI 채팅 오류: {e}")
                await message.reply(f"죄송해요, 응답을 생성하는 중 오류가 발생했어요.\n오류: {str(e)}")

    @commands.command(name='채팅초기화')
    async def clear_chat(self, ctx):
        """대화 기록 초기화"""
        self.llm.clear_history(ctx.channel.id)
        await ctx.send("대화 기록이 초기화되었습니다.")

    @commands.command(name='채팅모델')
    async def show_model(self, ctx):
        """현재 사용 중인 AI 모델 표시"""
        history_count = self.llm.get_history_count(ctx.channel.id)
        embed = discord.Embed(
            title="AI 채팅 정보",
            color=0x00ff00
        )
        embed.add_field(name="모델", value=self.llm.model, inline=False)
        embed.add_field(name="대화 기록", value=f"{history_count}개 메시지", inline=False)
        await ctx.send(embed=embed)


async def setup_chat_command(bot):
    """
    AI 채팅 명령어를 봇에 등록합니다.

    Args:
        bot: Discord 봇 인스턴스
    """
    await bot.add_cog(ChatCog(bot))
    logger.info("Chat 명령어 등록 완료")

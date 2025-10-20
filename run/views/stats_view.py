"""
전적 조회 UI (StatsView)

이 파일은 /전적 명령어에서 사용하는 UI를 담당해요.
버튼을 눌러서 메인/실험체/최근전적/통계/유니온을 볼 수 있어요.
"""
import discord
import tempfile
import os
import asyncio
from typing import Optional, List, Dict, Any

from run.utils.embeds import create_stats_embed, create_union_embed
from run.services.eternal_return.api_client import (
    get_player_season_data,
    get_player_recent_games,
    get_player_normal_game_data,
    get_player_basic_data,
    get_player_union_teams,
    get_game_details,
    get_team_members,
    game_data
)
from run.services.eternal_return.graph_generator import save_mmr_graph_to_file
from run.services.eternal_return.image_generator import save_recent_games_image_to_file


class StatsView(discord.ui.View):
    """
    플레이어 전적 조회 UI

    버튼들:
    - 메인: 기본 전적 화면
    - 실험체: 가장 많이 플레이한 실험체들
    - 최근전적: 최근 게임 결과 (이미지)
    - 통계: MMR 그래프 및 통계
    - 유니온: 유니온 팀 정보
    """
    def __init__(self, player_data: Dict[str, Any], played_seasons: Optional[List[Dict]] = None):
        super().__init__(timeout=300)
        self.player_data = player_data
        self.original_nickname = player_data['nickname']  # 원본 닉네임 보존
        self.played_seasons = played_seasons or []
        self.show_preseason = False  # 프리시즌 표시 여부
        self.show_normal_games = False  # 일반게임 모드

        # 시즌 선택 메뉴 추가
        season_select = self.create_season_select()
        if season_select:
            self.add_item(season_select)

        # 프리시즌이 있으면 프리시즌 버튼과 일반게임 버튼을 3번째 줄에 추가
        if any(self._is_preseason(s['name']) for s in self.played_seasons):
            toggle_button = discord.ui.Button(
                label='프리시즌 보기',
                style=discord.ButtonStyle.secondary,
                custom_id='toggle_season',
                row=3
            )
            toggle_button.callback = self.toggle_season_type
            self.add_item(toggle_button)

            normal_button = discord.ui.Button(
                label='일반게임',
                style=discord.ButtonStyle.secondary,
                custom_id='toggle_normal',
                row=3
            )
            normal_button.callback = self.toggle_normal_games
            self.add_item(normal_button)

    @discord.ui.button(label='메인', style=discord.ButtonStyle.primary, row=0)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        """메인 화면으로 돌아가기"""
        embed = create_stats_embed(self.player_data, self.show_normal_games)
        await interaction.response.edit_message(embed=embed, view=self, attachments=[])

    @discord.ui.button(label='실험체', style=discord.ButtonStyle.primary, row=0)
    async def show_characters(self, interaction: discord.Interaction, button: discord.ui.Button):
        """가장 많이 플레이한 실험체들 표시"""
        embed = discord.Embed(title=f"{self.player_data['nickname']}님의 실험체", color=0x5865F2)
        most_chars = self.player_data.get('most_characters', [])
        if most_chars:
            for i, char in enumerate(most_chars[:10]):
                mmr_gain = char.get('mmr_gain', 0)
                rp_text = f"{mmr_gain:+d} RP" if mmr_gain != 0 else "±0 RP"
                rp_emoji = "📈" if mmr_gain > 0 else "📉" if mmr_gain < 0 else "➖"
                avg_rank = char.get('avg_rank', 0)
                embed.add_field(
                    name=f"{i+1}. {char['name']}",
                    value=f"{char['games']}게임, {char['winrate']:.1f}% 승률\n평균 {avg_rank:.1f}등, {rp_emoji} {rp_text}",
                    inline=True
                )
        else:
            embed.add_field(name="실험체 정보", value="데이터가 없습니다.", inline=False)
        await interaction.response.edit_message(embed=embed, view=self, attachments=[])

    @discord.ui.button(label='최근전적', style=discord.ButtonStyle.success, row=0)
    async def show_recent_games(self, interaction: discord.Interaction, button: discord.ui.Button):
        """최근 게임 전적 표시 (이미지로)"""
        await interaction.response.defer()

        # 게임 모드 결정: 일반게임 모드면 0, 아니면 3 (랭크)
        game_mode = 0 if self.show_normal_games else 3

        recent_games = await get_player_recent_games(
            self.player_data['nickname'],
            self.player_data['season_id'],
            game_mode
        )

        # 게임 모드별 데이터 필터링
        if recent_games:
            if game_mode == 0:  # 일반게임만
                recent_games = [game for game in recent_games if game.get('matchingMode') == 0]
            else:  # 랭크게임(듀오, 솔로)만
                recent_games = [game for game in recent_games if game.get('matchingMode') in [2, 3]]

        # 게임 모드 텍스트 결정
        if recent_games and len(recent_games) > 0:
            actual_mode = recent_games[0].get('matchingMode', game_mode)
            if actual_mode == 0:
                game_mode_text = "일반게임"
            elif actual_mode == 2:
                game_mode_text = "듀오게임" if game_mode != 0 else "일반 듀오게임"
            elif actual_mode == 3:
                game_mode_text = "랭크게임"
            else:
                game_mode_text = "일반게임" if game_mode == 0 else "랭크게임"
        else:
            game_mode_text = "일반게임" if game_mode == 0 else "랭크게임"

        if recent_games:
            try:
                # 최근전적 이미지 생성
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    # 티어 정보 추가
                    tier_info = self.player_data.get('tier_info')
                    tier_image_url = self.player_data.get('tier_image_url')

                    # 각 게임의 팀원 정보 가져오기
                    game_details_list = []
                    for game in recent_games[:5]:  # 최대 5게임만
                        game_id = game.get('gameId')
                        teammates = []
                        if game_id:
                            try:
                                game_details = await get_game_details(game_id)
                                if game_details:
                                    teammates = get_team_members(game_details, self.player_data['nickname'])
                            except Exception as e:
                                print(f"게임 {game_id} 팀원 정보 가져오기 오류: {e}")
                        game_details_list.append(teammates)

                    image_path = save_recent_games_image_to_file(
                        recent_games,
                        self.player_data['nickname'],
                        game_mode_text,
                        tier_info,
                        tier_image_url,
                        game_details_list,
                        tmp_file.name
                    )

                if image_path and os.path.exists(image_path):
                    # 이미지가 성공적으로 생성된 경우
                    file_attachment = discord.File(image_path, filename="recent_games.png")

                    embed = discord.Embed(
                        title=f"{self.player_data['nickname']}님의 최근전적 ({game_mode_text})",
                        color=0x9932CC if game_mode == 0 else 0xFF6B35
                    )
                    embed.set_image(url="attachment://recent_games.png")

                    season_name = game_data.get_season_name(self.player_data['season_id'])
                    embed.set_footer(text=f"{season_name}")

                    await interaction.edit_original_response(embed=embed, attachments=[file_attachment], view=self)

                    # 임시 파일 정리
                    try:
                        os.unlink(image_path)
                    except:
                        pass

                    return

            except Exception as e:
                print(f"최근전적 이미지 생성 오류: {e}")
                import traceback
                traceback.print_exc()
                # 이미지 생성 실패시 기존 텍스트 방식으로 폴백

        # 이미지 생성 실패하거나 데이터가 없는 경우 텍스트로 표시
        embed = discord.Embed(
            title=f"{self.player_data['nickname']}님의 최근전적 ({game_mode_text})",
            color=0x9932CC if game_mode == 0 else 0xFF6B35
        )

        season_name = game_data.get_season_name(self.player_data['season_id'])
        embed.set_footer(text=f"{season_name}")

        if recent_games:
            for i, game in enumerate(recent_games[:8]):  # 최대 8게임
                rank = game.get('gameRank', 0)
                kills = game.get('playerKill', 0)
                assists = game.get('playerAssistant', 0)
                damage = game.get('damageToPlayer', 0)
                mmr_gain = game.get('mmrGain', 0)
                char_name = game.get('characterName', '알 수 없음')
                play_time = game.get('playTime', 0)

                # 순위에 따른 색상 이모지
                if rank == 1:
                    rank_display = "🥇 #1"
                    rank_color = "🟢"
                elif rank == 2:
                    rank_display = "🥈 #2"
                    rank_color = "🔵"
                elif rank == 3:
                    rank_display = "🥉 #3"
                    rank_color = "🟠"
                elif rank <= 5:
                    rank_display = f"#{rank}"
                    rank_color = "🟡"
                else:
                    rank_display = f"#{rank}"
                    rank_color = "🔴"

                # RP 변화 표시
                rp_display = ""
                if game_mode == 3 and mmr_gain != 0:
                    rp_arrow = "📈" if mmr_gain > 0 else "📉"
                    rp_display = f"\n{rp_arrow} {mmr_gain:+d} RP"

                # 플레이 시간 표시
                if play_time > 0:
                    minutes = play_time // 60
                    seconds = play_time % 60
                    time_display = f"{minutes}분 {seconds}초"
                else:
                    time_display = ""

                # 딜량 표시 (천 단위 구분)
                damage_display = f"{damage:,}" if damage > 0 else "0"

                field_value = f"{rank_color} **{char_name}**\n"
                field_value += f"⚔️ {kills}킬 {assists}어시\n"
                field_value += f"💥 {damage_display} 딜량"
                if time_display:
                    field_value += f"\n⏱️ {time_display}"
                field_value += rp_display

                embed.add_field(
                    name=f"{rank_display}",
                    value=field_value,
                    inline=True
                )

                # 3개마다 줄바꿈을 위한 빈 필드 추가
                if (i + 1) % 3 == 0 and i != 7:
                    embed.add_field(name="\u200b", value="\u200b", inline=False)
        else:
            embed.add_field(name="최근전적", value=f"{game_mode_text} 데이터가 없습니다.", inline=False)

        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='통계', style=discord.ButtonStyle.secondary, row=0)
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """통계 및 MMR 그래프 표시"""
        await interaction.response.defer()
        embed = discord.Embed(title=f"{self.player_data['nickname']}님의 통계", color=0xE67E22)
        stats = self.player_data.get('stats', {})
        file_attachment = None
        graph_path = None
        mmr_history = self.player_data.get('mmr_history', [])

        if mmr_history and len(mmr_history) >= 2:
            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    graph_path = save_mmr_graph_to_file(
                        mmr_history,
                        self.player_data.get('nickname', '플레이어'),
                        tmp_file.name
                    )
                if graph_path and os.path.exists(graph_path):
                    file_attachment = discord.File(graph_path, filename="mmr_graph.png")
                    embed.set_image(url="attachment://mmr_graph.png")
            except Exception as e:
                print(f"그래프 생성 오류: {e}")

        if stats:
            embed.add_field(name="게임 수", value=f"{stats.get('total_games', 0)}게임", inline=True)
            embed.add_field(name="승률", value=f"{stats.get('winrate', 0):.1f}%", inline=True)
            embed.add_field(name="평균 순위", value=f"{stats.get('avg_rank', 0):.1f}등", inline=True)
            embed.add_field(name="평균 킬", value=f"{stats.get('avg_kills', 0):.1f}킬", inline=True)
            embed.add_field(name="평균 어시", value=f"{stats.get('avg_assists', 0):.1f}어시", inline=True)
            embed.add_field(name="KDA", value=f"**{stats.get('kda', 0):.2f}**", inline=True)
        else:
            embed.add_field(name="통계 정보", value="데이터가 없습니다.", inline=False)

        if file_attachment:
            await interaction.edit_original_response(embed=embed, attachments=[file_attachment], view=self)
            if graph_path:
                os.unlink(graph_path)
        else:
            await interaction.edit_original_response(embed=embed, view=self)

    def _is_preseason(self, season_name: str) -> bool:
        """프리시즌인지 확인"""
        return "프리" in season_name or "Pre" in season_name

    def _filter_seasons_by_type(self):
        """시즌 필터링 (정식시즌 or 프리시즌)"""
        if not self.played_seasons:
            return []
        return [s for s in self.played_seasons if self._is_preseason(s['name']) == self.show_preseason][:25]

    def create_season_select(self):
        """시즌 선택 메뉴 생성"""
        filtered_seasons = self._filter_seasons_by_type()
        if not filtered_seasons:
            return None

        options = [
            discord.SelectOption(
                label=f"{s['name']}{' (현재)' if s.get('is_current') else ''}",
                value=str(s['id']),
                emoji="🔥" if s.get('is_current') else None
            )
            for s in filtered_seasons
        ]

        if not options:
            return None

        placeholder = "프리시즌별 전적 보기..." if self.show_preseason else "시즌별 전적 보기..."
        select = discord.ui.Select(placeholder=placeholder, options=options)
        select.callback = self.season_select_callback
        return select

    async def season_select_callback(self, interaction: discord.Interaction):
        """시즌 선택 시 해당 시즌 전적 표시"""
        await interaction.response.defer()
        season_id = int(interaction.data['values'][0])
        season_player_data = await get_player_season_data(self.player_data['nickname'], season_id)

        if season_player_data:
            self.player_data = season_player_data
            embed = create_stats_embed(season_player_data, self.show_normal_games)
        else:
            season_name = game_data.get_season_name(season_id)
            embed = discord.Embed(
                title=f"{self.player_data['nickname']}님의 {season_name} 전적",
                description="해당 시즌 데이터를 찾을 수 없습니다.",
                color=0xE74C3C
            )
            embed.set_footer(text=season_name)

        await interaction.edit_original_response(embed=embed, view=self)

    async def toggle_season_type(self, interaction: discord.Interaction):
        """정식시즌/프리시즌 전환"""
        await interaction.response.defer()
        self.show_preseason = not self.show_preseason

        # 버튼 라벨 업데이트
        for item in self.children:
            if hasattr(item, 'custom_id') and item.custom_id == 'toggle_season':
                item.label = '정식시즌 보기' if self.show_preseason else '프리시즌 보기'
                break

        # 기존 시즌 선택 메뉴 제거하고 새로 추가
        for item in list(self.children):
            if isinstance(item, discord.ui.Select):
                self.remove_item(item)
                break

        # 새로운 시즌 선택 메뉴 추가
        season_select = self.create_season_select()
        if season_select:
            self.add_item(season_select)

        embed = create_stats_embed(self.player_data, self.show_normal_games)
        await interaction.edit_original_response(embed=embed, view=self)

    async def toggle_normal_games(self, interaction: discord.Interaction):
        """랭크게임/일반게임 전환"""
        await interaction.response.defer()

        # 일반게임 모드 전환
        self.show_normal_games = not self.show_normal_games

        # 일반게임 버튼 찾아서 라벨 업데이트
        for item in self.children:
            if hasattr(item, 'custom_id') and item.custom_id == 'toggle_normal':
                item.label = '랭크게임' if self.show_normal_games else '일반게임'
                break

        # 일반게임 모드로 전환할 때 일반게임 데이터 가져오기
        if self.show_normal_games:
            normal_data = await get_player_normal_game_data(self.player_data['nickname'])
            if normal_data:
                self.player_data = normal_data
        else:
            # 랭크게임 모드로 전환할 때 원래 데이터 복원
            rank_data = await get_player_basic_data(self.player_data['nickname'])
            if rank_data:
                self.player_data = rank_data

        # 메인 임베드로 돌아가기 (모드 변경 적용)
        embed = create_stats_embed(self.player_data, self.show_normal_games)

        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='유니온', style=discord.ButtonStyle.secondary, row=3)
    async def show_union(self, interaction: discord.Interaction, button: discord.ui.Button):
        """유니온 팀 정보 표시"""
        await interaction.response.defer()

        # 유니온 데이터 가져오기 (항상 원본 닉네임 사용)
        union_data = await get_player_union_teams(self.original_nickname)

        if union_data and union_data.get('teams'):
            # 유니온 임베드 생성
            embed = create_union_embed(union_data, self.original_nickname)
            await interaction.edit_original_response(embed=embed, view=self, attachments=[])
        else:
            embed = discord.Embed(
                title=f"{self.original_nickname}님의 유니온 정보",
                description="유니온 데이터가 없습니다.",
                color=0xFF0000
            )
            await interaction.edit_original_response(embed=embed, view=self, attachments=[])

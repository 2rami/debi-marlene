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
    extract_team_members_info,
    game_data
)
from run.services.eternal_return.graph_generator import save_mmr_graph_to_file
from run.utils.emoji_utils import (
    get_character_emoji,
    get_weapon_emoji,
    get_item_emoji,
    get_trait_emoji,
    get_tactical_skill_emoji,
    get_skin_emoji
)


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
        self.current_mode = "RANK"  # 현재 모드: "RANK", "NORMAL", "UNION"

        # 시즌 선택 메뉴 추가
        season_select = self.create_season_select()
        if season_select:
            self.add_item(season_select)

        # 프리시즌이 있으면 프리시즌 버튼과 일반게임 버튼을 3번째 줄에 추가
        if any(self._is_preseason(s['name']) for s in self.played_seasons):
            # 일반게임 버튼
            normal_button = discord.ui.Button(
                label='일반게임',
                style=discord.ButtonStyle.secondary,
                custom_id='toggle_normal',
                row=3
            )
            normal_button.callback = self.toggle_normal_games
            self.add_item(normal_button)

            # 유니온 버튼
            union_button = discord.ui.Button(
                label='유니온',
                style=discord.ButtonStyle.secondary,
                custom_id='toggle_union',
                row=3
            )
            union_button.callback = self.toggle_union_mode
            self.add_item(union_button)

            # 프리시즌 버튼
            toggle_button = discord.ui.Button(
                label='프리시즌',
                style=discord.ButtonStyle.secondary,
                custom_id='toggle_season',
                row=3
            )
            toggle_button.callback = self.toggle_season_type
            self.add_item(toggle_button)

    @discord.ui.button(label='메인', style=discord.ButtonStyle.primary, row=0)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        """메인 화면으로 돌아가기"""
        is_normal = (self.current_mode == "NORMAL")
        embed = create_stats_embed(self.player_data, is_normal)
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
        """최근 게임 전적 표시 (한 게임씩, 화살표로 넘기기)"""
        await interaction.response.defer()

        # 현재 모드에 따라 게임 모드 결정
        game_mode = self.current_mode  # "RANK", "NORMAL", "UNION"

        recent_games = await get_player_recent_games(
            self.player_data['nickname'],
            self.player_data['season_id'],
            game_mode
        )

        # 게임 모드별 데이터 필터링
        if recent_games:
            if game_mode == "NORMAL":  # 일반게임만 (matchingMode: 2)
                recent_games = [game for game in recent_games if game.get('matchingMode') == 2]
            elif game_mode == "RANK":  # 랭크게임만 (matchingMode: 3)
                recent_games = [game for game in recent_games if game.get('matchingMode') == 3]
            elif game_mode == "UNION":  # 유니온만 (matchingMode: 8)
                recent_games = [game for game in recent_games if game.get('matchingMode') == 8]

        # 게임 모드 텍스트 결정
        mode_text_map = {"RANK": "랭크게임", "NORMAL": "일반게임", "UNION": "유니온"}
        game_mode_text = mode_text_map.get(game_mode, "게임")

        # 데이터가 없는 경우
        if not recent_games:
            embed = discord.Embed(
                title=f"{self.player_data['nickname']}님의 최근전적 ({game_mode_text})",
                description=f"{game_mode_text} 데이터가 없습니다.",
                color=0x9932CC if game_mode == 0 else 0xFF6B35
            )
            season_name = game_data.get_season_name(self.player_data['season_id'])
            embed.set_footer(text=f"{season_name}")
            await interaction.edit_original_response(embed=embed, view=self)
            return

        # 최근 전적 View 생성 (화살표 버튼 포함)
        recent_games_view = RecentGamesView(
            self.player_data,
            recent_games[:20],  # 최대 20게임
            game_mode,
            game_mode_text,
            parent_view=self
        )

        # 첫 번째 게임 임베드 생성
        embed = await recent_games_view.create_game_embed(0)
        await interaction.edit_original_response(embed=embed, view=recent_games_view)

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
            is_normal = (self.current_mode == "NORMAL")
            embed = create_stats_embed(season_player_data, is_normal)
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
                item.label = '정식시즌' if self.show_preseason else '프리시즌'
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

        is_normal = (self.current_mode == "NORMAL")
        embed = create_stats_embed(self.player_data, is_normal)
        await interaction.edit_original_response(embed=embed, view=self)

    async def toggle_normal_games(self, interaction: discord.Interaction):
        """랭크게임/일반게임 전환"""
        await interaction.response.defer()

        # 모드 전환
        if self.current_mode == "NORMAL":
            self.current_mode = "RANK"
        else:
            self.current_mode = "NORMAL"

        # 일반게임 버튼 찾아서 라벨 업데이트
        for item in self.children:
            if hasattr(item, 'custom_id') and item.custom_id == 'toggle_normal':
                item.label = '랭크게임' if self.current_mode == "NORMAL" else '일반게임'
                break

        # 데이터 가져오기
        if self.current_mode == "NORMAL":
            normal_data = await get_player_normal_game_data(self.player_data['nickname'])
            if normal_data:
                self.player_data = normal_data
        else:
            rank_data = await get_player_basic_data(self.player_data['nickname'])
            if rank_data:
                self.player_data = rank_data

        # 메인 화면으로 돌아가기
        is_normal = (self.current_mode == "NORMAL")
        embed = create_stats_embed(self.player_data, is_normal)
        await interaction.edit_original_response(embed=embed, view=self)

    async def toggle_union_mode(self, interaction: discord.Interaction):
        """랭크게임/유니온 전환"""
        await interaction.response.defer()

        # 모드 전환
        if self.current_mode == "UNION":
            self.current_mode = "RANK"
            # 랭크 데이터 복원
            rank_data = await get_player_basic_data(self.player_data['nickname'])
            if rank_data:
                self.player_data = rank_data

            # 메인 화면으로
            embed = create_stats_embed(self.player_data, False)
            await interaction.edit_original_response(embed=embed, view=self, attachments=[])
        else:
            self.current_mode = "UNION"
            # 유니온 데이터 가져오기
            union_data = await get_player_union_teams(self.original_nickname)

            if union_data and union_data.get('teams'):
                embed = create_union_embed(union_data, self.original_nickname)
                await interaction.edit_original_response(embed=embed, view=self, attachments=[])
            else:
                embed = discord.Embed(
                    title=f"{self.original_nickname}님의 유니온 정보",
                    description="유니온 데이터가 없습니다.",
                    color=0xFF0000
                )
                await interaction.edit_original_response(embed=embed, view=self, attachments=[])


class RecentGamesView(discord.ui.View):
    """
    최근 전적을 한 게임씩 보여주는 View (화살표로 게임 넘기기)
    """
    def __init__(self, player_data: Dict[str, Any], games: List[Dict], game_mode: int, game_mode_text: str, parent_view: StatsView):
        super().__init__(timeout=300)
        self.player_data = player_data
        self.games = games
        self.game_mode = game_mode
        self.game_mode_text = game_mode_text
        self.parent_view = parent_view
        self.current_index = 0

        # 버튼 상태 업데이트
        self.update_buttons()

    def update_buttons(self):
        """버튼 활성화/비활성화"""
        self.prev_button.disabled = (self.current_index == 0)
        self.next_button.disabled = (self.current_index >= len(self.games) - 1)

    async def create_game_embed(self, game_index: int) -> discord.Embed:
        """특정 게임의 임베드 생성"""
        game = self.games[game_index]
        season_name = game_data.get_season_name(self.player_data['season_id'])

        # 실제 게임 모드 확인 (각 게임마다 다를 수 있음)
        actual_matching_mode = game.get('matchingMode', 3)
        if actual_matching_mode == 0:
            game_mode_text = "일반게임"
        elif actual_matching_mode == 2:
            game_mode_text = "일반게임"
        elif actual_matching_mode == 3:
            game_mode_text = "랭크게임"
        elif actual_matching_mode == 8:
            game_mode_text = "유니온"
        else:
            game_mode_text = f"게임모드 {actual_matching_mode}"

        # 게임 기본 정보
        game_id = game.get('gameId', 0)
        rank = game.get('gameRank', 0)
        kills = game.get('playerKill', 0)
        team_kills = game.get('teamKill', 0)
        assists = game.get('playerAssistant', 0)
        damage = game.get('damageToPlayer', 0)
        mmr_gain = game.get('mmrGain') or game.get('mmrGainInGame', 0)
        char_code = game.get('characterNum', 0)
        char_name = game_data.get_character_name(char_code)
        level = game.get('characterLevel', 1)

        # 시간 정보
        start_time = game.get('startDtm')  # 게임 시작 시간
        play_time = game.get('playTime', 0)  # 플레이 시간 (초)

        # weaponImage URL에서 무기 ID 추출
        weapon_type = 0
        weapon_image_url = game.get('weaponImage')
        if weapon_image_url:
            import re
            match = re.search(r'Ico_Mastery_(\d+)\.png', weapon_image_url)
            if match:
                weapon_type = int(match.group(1))

        # 무기 이모지
        weapon_key = game_data.get_weapon_key(weapon_type) if weapon_type else None
        weapon_emoji = get_weapon_emoji(weapon_key) if weapon_key else ""

        # 전술스킬 정보 (game 객체에서 직접 가져오기)
        tactical_skill_id = game.get('tacticalSkillGroup', 0)
        tactical_skill_key = game_data.get_tactical_skill_key(tactical_skill_id) if tactical_skill_id else None
        tactical_skill_emoji = get_tactical_skill_emoji(tactical_skill_key) if tactical_skill_key else ""

        # 날씨 정보 (game 객체에서 직접 가져오기)
        main_weather_id = game.get('mainWeather', 0)

        # 순위에 따른 색상
        if rank == 1:
            color = 0xFFD700  # 금색
            rank_display = f"{rank}등 WIN"
        elif rank <= 5:
            color = 0x5865F2  # 파란색
            rank_display = f"{rank}등"
        else:
            color = 0x99AAB5  # 회색
            rank_display = f"{rank}등"

        # 시간 정보 계산
        time_info = ""
        if start_time:
            from datetime import datetime, timezone
            try:
                # ISO 8601 형식 파싱 (한국 시간대 +0900 포함)
                # "2025-10-29T02:42:12.012+0900" 형식
                game_time = datetime.fromisoformat(start_time)
                now = datetime.now(timezone.utc)
                time_diff = now - game_time

                # 몇 시간 전
                total_seconds = time_diff.total_seconds()
                hours_ago = int(total_seconds / 3600)
                if hours_ago < 1:
                    minutes_ago = int(total_seconds / 60)
                    time_ago = f"{minutes_ago}분 전"
                elif hours_ago < 24:
                    time_ago = f"{hours_ago}시간 전"
                else:
                    days_ago = int(hours_ago / 24)
                    time_ago = f"{days_ago}일 전"

                # 플레이 시간
                if play_time and play_time > 0:
                    play_minutes = int(play_time / 60)
                    play_seconds = int(play_time % 60)
                    time_info = f"{time_ago} | {play_minutes}분 {play_seconds}초"
                else:
                    time_info = time_ago
            except Exception:
                # 에러 발생 시 무시
                pass

        # description에 캐릭터 정보 배치
        desc_parts = []
        desc_parts.append(f"{char_name} Lv.{level}")
        if weapon_emoji:
            desc_parts.append(weapon_emoji)
        if tactical_skill_emoji:
            desc_parts.append(tactical_skill_emoji)

        # 시간 정보 추가
        description_text = " ".join(desc_parts)
        if time_info:
            description_text += f"\n{time_info}"

        # 캐릭터 기본 이미지 URL 가져오기 (CharProfile)
        char_data = game_data.characters.get(char_code, {})
        char_icon_url = char_data.get('imageUrl', '')

        # URL이 //로 시작하면 https: 추가
        if char_icon_url.startswith('//'):
            char_icon_url = f"https:{char_icon_url}"

        # 임베드 생성
        player_url = f"https://dak.gg/er/players/{self.player_data['nickname']}"
        embed = discord.Embed(
            title=rank_display,
            description=description_text,
            color=color,
            url=player_url
        )

        # Footer 설정: 시즌 + 게임 모드 (실제 게임 모드 사용)
        footer_text = f"{season_name} | {game_mode_text}"

        # 주날씨 이미지를 footer 아이콘으로 설정
        main_weather_image_url = game_data.get_weather_image_url(main_weather_id) if main_weather_id else None

        if main_weather_image_url:
            embed.set_footer(text=footer_text, icon_url=main_weather_image_url)
        else:
            embed.set_footer(text=footer_text)

        # 스킨 이미지 설정 (API에서 직접 제공)
        character_image = game.get('characterImage')
        if character_image:
            embed.set_thumbnail(url=character_image)

        # 아이템 이모지 먼저 가져오기
        equipment = game.get('equipment', [])

        # equipment가 문자열이면 JSON 파싱
        if isinstance(equipment, str):
            import json
            try:
                equipment = json.loads(equipment)
            except:
                equipment = []

        item_emojis = []
        if equipment and isinstance(equipment, list):
            # 최대 6개까지 처리
            for i, item in enumerate(equipment):
                if i >= 6:  # 6개 초과하면 중단
                    break

                if isinstance(item, dict):
                    item_code = item.get('itemCode', 0)
                else:
                    item_code = item

                if item_code and item_code > 0:
                    item_emoji = get_item_emoji(item_code)
                    if item_emoji:
                        item_emojis.append(item_emoji)

        # 팀원 정보 및 특성 정보 (게임 상세 정보 가져오기)
        game_details = await get_game_details(game_id)

        # 특성 이모지 초기화
        main_trait_emojis = []
        sub_trait_emojis = []

        if game_details and game_details.get('userGames'):
            # 내 게임 데이터 찾기
            my_match = None
            for user_game in game_details['userGames']:
                if user_game.get('nickname') == self.player_data['nickname']:
                    my_match = user_game
                    break

            if my_match:
                # 주특성 (traitFirstCore)
                trait_first_core = my_match.get('traitFirstCore')
                if trait_first_core:
                    trait_emoji = get_trait_emoji(trait_first_core)
                    if trait_emoji:
                        main_trait_emojis.append(trait_emoji)

                # 부특성 (traitFirstSub + traitSecondSub)
                trait_first_sub = my_match.get('traitFirstSub', [])
                for trait_id in trait_first_sub:
                    trait_emoji = get_trait_emoji(trait_id)
                    if trait_emoji:
                        sub_trait_emojis.append(trait_emoji)

                trait_second_sub = my_match.get('traitSecondSub', [])
                for trait_id in trait_second_sub:
                    trait_emoji = get_trait_emoji(trait_id)
                    if trait_emoji:
                        sub_trait_emojis.append(trait_emoji)

        # 아이템 필드 (전체 너비)
        if item_emojis:
            embed.add_field(name="아이템", value=" ".join(item_emojis), inline=False)
        else:
            embed.add_field(name="아이템", value="\u200b", inline=False)

        # 특성 필드 (전체 너비)
        trait_emojis = []
        if main_trait_emojis:
            trait_emojis.extend(main_trait_emojis)
        if sub_trait_emojis:
            trait_emojis.extend(sub_trait_emojis)

        if trait_emojis:
            embed.add_field(name="특성", value=" ".join(trait_emojis), inline=False)
        else:
            embed.add_field(name="특성", value="\u200b", inline=False)

        # TK/K/A (왼쪽)
        embed.add_field(name="TK/K/A", value=f"{team_kills}/{kills}/{assists}", inline=True)

        # 딜량 (가운데)
        embed.add_field(name="딜량", value=f"{damage:,}", inline=True)

        # RP (오른쪽) - 랭크게임과 유니온에서 표시
        if actual_matching_mode == 3 or actual_matching_mode == 8:  # 랭크게임 또는 유니온
            rp_value = f"{mmr_gain:+d} RP" if mmr_gain != 0 else "±0 RP"
            embed.add_field(name="RP", value=rp_value, inline=True)
        else:
            # 빈 필드 (일반게임)
            embed.add_field(name="\u200b", value="\u200b", inline=True)

        # 팀원 정보
        if game_details:
            team_members_data = extract_team_members_info(game_details, self.player_data['nickname'])
            if team_members_data:
                # 팀원들 배치 (최대 2명, 빈 칸 없이)
                for i, teammate in enumerate(team_members_data[:2]):
                    teammate_info = self.format_teammate_info(teammate)
                    embed.add_field(name="\u200b", value=teammate_info, inline=True)
        return embed

    def format_teammate_info(self, teammate: Dict) -> str:
        """팀원 정보 포맷팅"""
        char_code = teammate.get('characterNum', 0)
        damage = teammate.get('damageToPlayer', 0)
        nickname = teammate.get('nickname', '')
        skin_code = teammate.get('skinCode', 0)

        # 스킨 이모지 우선, 없으면 기본 캐릭터 이모지
        char_emoji = ""
        if skin_code:
            char_emoji = get_skin_emoji(skin_code)

        # 스킨 이모지가 없으면 기본 캐릭터 이모지 사용
        if not char_emoji:
            char_key = game_data.get_character_key(char_code)
            char_emoji = get_character_emoji(char_key) if char_key else ""

        # 아이템 이모지
        equipment = teammate.get('equipment', [])

        # equipment가 문자열이면 JSON 파싱
        if isinstance(equipment, str):
            import json
            try:
                equipment = json.loads(equipment)
            except:
                equipment = []

        # equipment가 dict면 values()로 변환
        if isinstance(equipment, dict):
            equipment = list(equipment.values())

        item_emojis = []
        if equipment and isinstance(equipment, list):
            for item in equipment[:6]:
                if isinstance(item, dict):
                    item_code = item.get('itemCode', 0)
                else:
                    item_code = item

                if item_code:
                    item_emoji = get_item_emoji(item_code)
                    if item_emoji:
                        item_emojis.append(item_emoji)

        # 첫 줄: 이모지 + 닉네임
        info_lines = []
        first_line = f"{char_emoji} {nickname}" if char_emoji else nickname
        info_lines.append(first_line)

        # 둘째 줄: 아이템
        if item_emojis:
            info_lines.append(" ".join(item_emojis))

        # 셋째 줄: 딜량
        info_lines.append(f"딜량: {damage:,}")

        return "\n".join(info_lines)

    @discord.ui.button(label='◀', style=discord.ButtonStyle.secondary, row=0)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """이전 게임"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_buttons()
            embed = await self.create_game_embed(self.current_index)
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='돌아가기', style=discord.ButtonStyle.primary, row=0)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """메인으로 돌아가기"""
        # 유니온 모드일 때는 유니온 정보로 돌아가기
        if self.parent_view.current_mode == "UNION":
            union_data = await get_player_union_teams(self.parent_view.original_nickname)
            if union_data and union_data.get('teams'):
                embed = create_union_embed(union_data, self.parent_view.original_nickname)
            else:
                embed = discord.Embed(
                    title=f"{self.parent_view.original_nickname}님의 유니온 정보",
                    description="유니온 데이터가 없습니다.",
                    color=0xFF0000
                )
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        else:
            # 일반게임 또는 랭크게임 모드
            is_normal = (self.parent_view.current_mode == "NORMAL")
            embed = create_stats_embed(self.player_data, is_normal)
            await interaction.response.edit_message(embed=embed, view=self.parent_view)

    @discord.ui.button(label='▶', style=discord.ButtonStyle.secondary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """다음 게임"""
        if self.current_index < len(self.games) - 1:
            self.current_index += 1
            self.update_buttons()
            embed = await self.create_game_embed(self.current_index)
            await interaction.response.edit_message(embed=embed, view=self)

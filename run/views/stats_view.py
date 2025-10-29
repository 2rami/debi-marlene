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
    get_tactical_skill_emoji
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
        """최근 게임 전적 표시 (한 게임씩, 화살표로 넘기기)"""
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
        game_mode_text = "일반게임" if game_mode == 0 else "랭크게임"

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

        # 게임 기본 정보
        game_id = game.get('gameId', 0)
        rank = game.get('gameRank', 0)
        kills = game.get('playerKill', 0)
        team_kills = game.get('teamKill', 0)
        assists = game.get('playerAssistant', 0)
        damage = game.get('damageToPlayer', 0)
        mmr_gain = game.get('mmrGain', 0)
        char_code = game.get('characterNum', 0)
        char_name = game_data.get_character_name(char_code)
        level = game.get('characterLevel', 1)

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
        sub_weather_id = game.get('subWeather', 0)

        # 순위에 따른 색상
        if rank == 1:
            color = 0xFFD700  # 금색
            rank_display = f"#{rank} WIN"
        elif rank <= 5:
            color = 0x5865F2  # 파란색
            rank_display = f"#{rank} TOP5" if rank > 3 else f"#{rank}"
        else:
            color = 0x99AAB5  # 회색
            rank_display = f"#{rank}"

        # 임베드 생성
        embed = discord.Embed(
            title=f"{self.player_data['nickname']}님의 최근전적 ({self.game_mode_text})",
            description=f"{rank_display} | {char_name} Lv.{level}",
            color=color,
            url=f"https://dak.gg/bser/games/{game_id}"
        )

        # Footer 설정: 날씨 이미지 + 날씨 이름 + 시즌
        footer_text = season_name

        # 날씨 이름 추가
        weather_names = []
        main_weather_name = game_data.get_weather_name(main_weather_id) if main_weather_id else ""
        sub_weather_name = game_data.get_weather_name(sub_weather_id) if sub_weather_id else ""

        if main_weather_name:
            weather_names.append(main_weather_name)
        if sub_weather_name:
            weather_names.append(sub_weather_name)

        if weather_names:
            footer_text = f"{' / '.join(weather_names)} | {season_name}"

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

        # 본인 정보
        char_display = char_name  # 캐릭터 이모지 제거

        # 무기 표시 (무기 이모지만)
        weapon_display = weapon_emoji if weapon_emoji else None

        # 전술스킬 표시 (전술스킬 이모지만) - 위에서 이미 설정됨
        tactical_display = tactical_skill_emoji if tactical_skill_emoji else None

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

        # 플레이어 정보 구성
        player_info = [f"**캐릭터**: {char_display}"]

        # 무기 줄: 무기 이모지 + 아이템 이모지들
        weapon_line = f"**무기**: {weapon_display}" if weapon_display else ""
        if item_emojis:
            weapon_line += f" {' '.join(item_emojis)}" if weapon_line else f"{' '.join(item_emojis)}"
        if weapon_line:
            player_info.append(weapon_line)

        # 전술스킬 (있을 때만 표시)
        if tactical_display:
            player_info.append(f"**전술스킬**: {tactical_display}")

        # TK/K/A 줄: TK/K/A + 주특성 이모지
        tk_line = f"**TK/K/A**: {team_kills}/{kills}/{assists}"
        if main_trait_emojis:
            tk_line += f" {' '.join(main_trait_emojis)}"
        player_info.append(tk_line)

        # 딜량 줄: 딜량 + 부특성 이모지들
        damage_line = f"**딜량**: {damage:,}"
        if sub_trait_emojis:
            damage_line += f" {' '.join(sub_trait_emojis)}"
        player_info.append(damage_line)

        if self.game_mode == 3 and mmr_gain != 0:
            rp_sign = "+" if mmr_gain > 0 else ""
            player_info.append(f"**RP**: {rp_sign}{mmr_gain}")

        # 하나의 필드로 모든 정보 표시
        embed.add_field(name="\u200b", value="\n".join(player_info), inline=False)

        if game_details:
            team_members_data = extract_team_members_info(game_details, self.player_data['nickname'])
            if team_members_data:
                for teammate in team_members_data[:2]:  # 최대 2명
                    teammate_info = self.format_teammate_info(teammate)
                    embed.add_field(name=teammate['nickname'], value=teammate_info, inline=True)

        return embed

    def format_teammate_info(self, teammate: Dict) -> str:
        """팀원 정보 포맷팅"""
        char_code = teammate.get('characterNum', 0)
        char_name = game_data.get_character_name(char_code)
        damage = teammate.get('damageToPlayer', 0)

        # 캐릭터 이모지
        char_key = game_data.get_character_key(char_code)
        char_emoji = get_character_emoji(char_key) if char_key else ""
        char_display = f"{char_emoji} {char_name}" if char_emoji else char_name

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

        info_lines = [
            f"{char_display}",
            f"딜: {damage:,}"
        ]

        if item_emojis:
            info_lines.append(" ".join(item_emojis))

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
        embed = create_stats_embed(self.player_data, self.parent_view.show_normal_games)
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

    @discord.ui.button(label='▶', style=discord.ButtonStyle.secondary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """다음 게임"""
        if self.current_index < len(self.games) - 1:
            self.current_index += 1
            self.update_buttons()
            embed = await self.create_game_embed(self.current_index)
            await interaction.response.edit_message(embed=embed, view=self)

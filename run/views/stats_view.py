"""
전적 조회 UI (StatsLayoutView + StatsView)

Components V2 기반 레이아웃 (Section + Thumbnail)으로 메인 전적을 표시하고,
최근전적/통계(그래프)/유니온 등 embed가 필요한 화면은 StatsView로 전환.
"""
import discord
import tempfile
import os
import asyncio
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

from run.utils.embeds import create_stats_embed, create_union_embed, UNION_TIER_MAP
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
    get_tier_emoji,
    get_weapon_emoji,
    get_weapon_skill_emoji,
    get_item_emoji,
    get_trait_emoji,
    get_tactical_skill_emoji,
    get_skin_emoji
)


class StatsLayoutView(discord.ui.LayoutView):
    """Components V2 기반 전적 조회 UI (Section + Thumbnail 레이아웃)"""

    def __init__(self, player_data, played_seasons=None, current_mode="RANK", show_preseason=False):
        super().__init__(timeout=300)
        self.player_data = player_data
        self.original_nickname = player_data['nickname']
        self.played_seasons = played_seasons or []
        self.show_preseason = show_preseason
        self.current_mode = current_mode
        self._recent_games = []
        self._recent_index = 0
        self._recent_game_mode_text = ""
        self._build_main()

    def _is_preseason(self, season_name):
        return "프리" in season_name or "Pre" in season_name

    def _filter_seasons_by_type(self):
        if not self.played_seasons:
            return []
        return [s for s in self.played_seasons if self._is_preseason(s['name']) == self.show_preseason][:25]

    def _build_stats_text(self, is_normal):
        """메인 화면 전적 텍스트"""
        nickname = self.player_data.get('nickname', 'Unknown')

        # 티어 이모지 (tier_id=0은 언랭크 — 0도 유효한 값이므로 None 체크)
        tier_emoji = ""
        tier_id = self.player_data.get('tier_id')
        if tier_id is not None:
            tier_emoji = get_tier_emoji(tier_id) or ""

        if is_normal:
            level = self.player_data.get('level', 1)
            lines = [f"# {nickname}"]
            if tier_emoji:
                lines.append(f"## {tier_emoji} 일반게임")
            else:
                lines.append(f"## 일반게임")
            lines.append(f"Lv.{level}")
            if self.player_data.get('stats'):
                stats = self.player_data['stats']
                lines.append(f"평균 순위 **{stats.get('avg_rank', 0):.1f}등** | 승률 **{stats.get('winrate', 0):.1f}%**")
        else:
            rank_info = self.player_data.get('tier_info', 'Unranked')
            mmr = self.player_data.get('mmr', 0)
            lines = [f"# {nickname}"]
            if tier_emoji:
                lines.append(f"## {tier_emoji} {rank_info}")
            else:
                lines.append(f"## {rank_info}")
            if mmr > 0:
                lines.append(f"MMR **{mmr:,}**")
            rank = self.player_data.get('rank', 0)
            rank_percent = self.player_data.get('rank_percent', 0)
            if rank > 0:
                lines.append(f"{rank:,}위 상위 {rank_percent}%")
            if self.player_data.get('most_characters'):
                top_char = self.player_data['most_characters'][0]
                lines.append(f"\n가장 많이 플레이한 실험체\n**{top_char['name']}** ({top_char['games']}게임)")
            if self.player_data.get('stats'):
                stats = self.player_data['stats']
                lines.append(f"승률 **{stats.get('winrate', 0):.1f}%**")
        return "\n".join(lines)

    def _build_main(self):
        """메인 전적 화면 - 카미봇 스타일 (top-level Section + Container)"""
        self.clear_items()
        is_normal = (self.current_mode == "NORMAL")

        # === 상단: top-level (Container 밖) - 전적 정보 ===
        stats_text = self._build_stats_text(is_normal)
        text_display = discord.ui.TextDisplay(stats_text)

        # 실험체 스킨 이미지를 오른쪽 Thumbnail으로
        char_image_url = None
        if self.player_data.get('most_characters') and self.player_data['most_characters'][0].get('image_url'):
            char_image_url = self.player_data['most_characters'][0]['image_url']

        if char_image_url:
            section = discord.ui.Section(text_display, accessory=discord.ui.Thumbnail(media=char_image_url))
        else:
            section = discord.ui.Section(text_display)

        # 시즌 푸터
        season_name = game_data.get_season_name(self.player_data['season_id'])
        game_mode_text = "일반게임" if is_normal else "랭크게임"
        footer = discord.ui.TextDisplay(f"-# {season_name} | {game_mode_text}")

        # 상단 Container (accent_colour 없음)
        self.add_item(discord.ui.Container(section, footer))

        # === 하단: Container 안 - 버튼 + 드롭다운 ===
        self._add_navigation_in_container()

    def _add_navigation_in_container(self):
        """네비게이션을 Container 안에 배치"""
        container_children = []

        # Row 1: 메인 버튼들
        btn_main = discord.ui.Button(label='메인', style=discord.ButtonStyle.primary)
        btn_main.callback = self._on_main
        btn_chars = discord.ui.Button(label='실험체', style=discord.ButtonStyle.primary)
        btn_chars.callback = self._on_characters
        btn_recent = discord.ui.Button(label='최근전적', style=discord.ButtonStyle.success)
        btn_recent.callback = self._on_recent_games
        btn_stats = discord.ui.Button(label='통계', style=discord.ButtonStyle.secondary)
        btn_stats.callback = self._on_stats

        container_children.append(discord.ui.ActionRow(btn_main, btn_chars, btn_recent, btn_stats))

        # Row 2: 시즌 선택 드롭다운
        filtered_seasons = self._filter_seasons_by_type()
        if filtered_seasons:
            options = [
                discord.SelectOption(
                    label=f"{s['name']}{' (현재)' if s.get('is_current') else ''}",
                    value=str(s['id']),
                )
                for s in filtered_seasons
            ]
            placeholder = "프리시즌별 전적 보기..." if self.show_preseason else "시즌별 전적 보기..."
            select = discord.ui.Select(placeholder=placeholder, options=options)
            select.callback = self._on_season_select
            container_children.append(discord.ui.ActionRow(select))

        # Row 3: 모드 토글 버튼 (프리시즌이 있을 때만)
        if any(self._is_preseason(s['name']) for s in self.played_seasons):
            normal_label = '랭크게임' if self.current_mode == "NORMAL" else '일반게임'
            btn_normal = discord.ui.Button(label=normal_label, style=discord.ButtonStyle.secondary)
            btn_normal.callback = self._on_toggle_normal

            btn_union = discord.ui.Button(label='유니온', style=discord.ButtonStyle.secondary)
            btn_union.callback = self._on_toggle_union

            season_label = '정식시즌' if self.show_preseason else '프리시즌'
            btn_season = discord.ui.Button(label=season_label, style=discord.ButtonStyle.secondary)
            btn_season.callback = self._on_toggle_season_type

            container_children.append(discord.ui.ActionRow(btn_normal, btn_union, btn_season))

        container = discord.ui.Container(*container_children)
        self.add_item(container)

    # === 콜백 ===

    async def _on_main(self, interaction):
        """메인 화면으로"""
        self._build_main()
        await interaction.response.edit_message(view=self)

    async def _on_characters(self, interaction):
        """실험체 화면 (TextDisplay로 표시)"""
        self.clear_items()
        most_chars = self.player_data.get('most_characters', [])
        lines = [f"## {self.player_data['nickname']}님의 실험체\n"]

        is_normal = (self.current_mode == "NORMAL")
        if most_chars:
            for i, char in enumerate(most_chars[:10]):
                avg_rank = char.get('avg_rank', 0)
                # 실험체 이모지
                char_key = char.get('char_key')
                char_emoji = get_character_emoji(char_key) if char_key else ""
                prefix = f"{char_emoji} " if char_emoji else ""
                # 일반게임이면 RP 표시 안 함
                if is_normal:
                    lines.append(f"{prefix}**{i+1}. {char['name']}** - {char['games']}게임, {char['winrate']:.1f}% 승률, 평균 {avg_rank:.1f}등")
                else:
                    mmr_gain = char.get('mmr_gain', 0)
                    rp_text = f"{mmr_gain:+d} RP" if mmr_gain != 0 else "+/-0 RP"
                    arrow = "^ " if mmr_gain > 0 else "v " if mmr_gain < 0 else ""
                    lines.append(f"{prefix}**{i+1}. {char['name']}** - {char['games']}게임, {char['winrate']:.1f}% 승률, 평균 {avg_rank:.1f}등, {arrow}{rp_text}")
        else:
            lines.append("데이터가 없습니다.")

        self.add_item(discord.ui.Container(discord.ui.TextDisplay("\n".join(lines))))
        self._add_navigation_in_container()
        await interaction.response.edit_message(view=self)

    async def _on_recent_games(self, interaction):
        """최근전적 (LayoutView 내에서 표시)"""
        await interaction.response.defer()

        game_mode = self.current_mode
        recent_games = await get_player_recent_games(
            self.player_data['nickname'],
            self.player_data['season_id'],
            game_mode
        )

        if recent_games:
            if game_mode == "NORMAL":
                recent_games = [g for g in recent_games if g.get('matchingMode') == 2]
            elif game_mode == "RANK":
                recent_games = [g for g in recent_games if g.get('matchingMode') == 3]
            elif game_mode == "UNION":
                recent_games = [g for g in recent_games if g.get('matchingMode') == 8]

        mode_text_map = {"RANK": "랭크게임", "NORMAL": "일반게임", "UNION": "유니온"}
        game_mode_text = mode_text_map.get(game_mode, "게임")

        if not recent_games:
            self.clear_items()
            self.add_item(discord.ui.Container(
                discord.ui.TextDisplay(f"## {self.player_data['nickname']}님의 최근전적\n\n{game_mode_text} 데이터가 없습니다.")
            ))
            self._add_navigation_in_container()
            await interaction.edit_original_response(view=self)
            return

        # LayoutView 내에서 최근전적 표시
        self._recent_games = recent_games[:20]
        self._recent_game_mode_text = game_mode_text
        self._recent_index = 0
        await self._build_recent_game(interaction)

    async def _on_stats(self, interaction):
        """통계 화면 (LayoutView 내에서 표시)"""
        await interaction.response.defer()
        stats = self.player_data.get('stats', {})
        mmr_history = self.player_data.get('mmr_history', [])

        self.clear_items()
        lines = [f"## {self.player_data['nickname']}님의 통계\n"]
        if stats:
            lines.append(f"**게임 수** {stats.get('total_games', 0)}게임 | **승률** {stats.get('winrate', 0):.1f}%")
            lines.append(f"**평균 순위** {stats.get('avg_rank', 0):.1f}등 | **평균 킬** {stats.get('avg_kills', 0):.1f}킬")
            lines.append(f"**평균 어시** {stats.get('avg_assists', 0):.1f}어시 | **KDA** {stats.get('kda', 0):.2f}")
        else:
            lines.append("데이터가 없습니다.")

        self.add_item(discord.ui.Container(discord.ui.TextDisplay("\n".join(lines))))

        # 그래프 이미지 (MediaGallery로 인라인 표시)
        graph_path = None
        file_attachment = None
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
                    self.add_item(discord.ui.MediaGallery(
                        items=[discord.ui.MediaGalleryItem(media="attachment://mmr_graph.png")]
                    ))
            except Exception:
                pass

        self._add_navigation_in_container()

        if file_attachment:
            await interaction.edit_original_response(view=self, attachments=[file_attachment])
            if graph_path:
                os.unlink(graph_path)
        else:
            await interaction.edit_original_response(view=self)

    async def _build_recent_game(self, interaction):
        """최근전적 한 게임을 LayoutView로 표시"""
        game = self._recent_games[self._recent_index]
        season_name = game_data.get_season_name(self.player_data['season_id'])

        # 게임 모드
        actual_mode = game.get('matchingMode', 3)
        mode_map = {0: "일반게임", 2: "일반게임", 3: "랭크게임", 8: "유니온"}
        game_mode_text = mode_map.get(actual_mode, f"게임모드 {actual_mode}")

        # 기본 정보
        rank = game.get('gameRank', 0)
        kills = game.get('playerKill', 0)
        team_kills = game.get('teamKill', 0)
        assists = game.get('playerAssistant', 0)
        damage = game.get('damageToPlayer', 0)
        mmr_gain = game.get('mmrGain') or game.get('mmrGainInGame', 0)
        char_code = game.get('characterNum', 0)
        char_name = game_data.get_character_name(char_code)
        level = game.get('characterLevel', 1)
        game_id = game.get('gameId', 0)

        # 무기 이모지 (weaponType 직접 사용)
        weapon_emoji = ""
        weapon_type = game.get('weaponType') or game.get('bestWeapon')
        if weapon_type:
            weapon_key = game_data.get_weapon_key(weapon_type)
            if weapon_key:
                weapon_emoji = get_weapon_emoji(weapon_key)
                if not weapon_emoji:
                    logger.warning(f"[최근전적] 무기 이모지 없음: weapon_key={weapon_key}, weapon_type={weapon_type}")

        # 전술스킬 이모지
        tactical_emoji = ""
        tactical_id = game.get('tacticalSkillGroup', 0)
        if tactical_id:
            tactical_key = game_data.get_tactical_skill_key(tactical_id)
            if tactical_key:
                tactical_emoji = get_tactical_skill_emoji(tactical_key)
                if not tactical_emoji:
                    logger.warning(f"[최근전적] 전술스킬 이모지 없음: tactical_key={tactical_key}")

        # 시간 정보
        time_info = ""
        start_time = game.get('startDtm')
        play_time = game.get('playTime', 0)
        if start_time:
            from datetime import datetime, timezone
            try:
                game_time = datetime.fromisoformat(start_time)
                total_seconds = (datetime.now(timezone.utc) - game_time).total_seconds()
                hours_ago = int(total_seconds / 3600)
                if hours_ago < 1:
                    time_ago = f"{int(total_seconds / 60)}분 전"
                elif hours_ago < 24:
                    time_ago = f"{hours_ago}시간 전"
                else:
                    time_ago = f"{int(hours_ago / 24)}일 전"
                if play_time and play_time > 0:
                    time_info = f"{time_ago} | {int(play_time / 60)}분 {int(play_time % 60)}초"
                else:
                    time_info = time_ago
            except Exception:
                pass

        # 순위 표시
        rank_display = f"{rank}등 WIN" if rank == 1 else f"{rank}등"

        # 아이템 이모지
        equipment = game.get('equipment', [])
        if isinstance(equipment, str):
            import json
            try:
                equipment = json.loads(equipment)
            except:
                equipment = []
        item_emojis = []
        if equipment and isinstance(equipment, list):
            for item in equipment[:6]:
                item_code = item.get('itemCode', 0) if isinstance(item, dict) else item
                if item_code and item_code > 0:
                    emoji = get_item_emoji(item_code)
                    if emoji:
                        item_emojis.append(emoji)

        # 무기스킬 이모지 (masteryLevel에서 100~199 범위 추출)
        weapon_skill_emojis = []
        mastery_level_raw = game.get('masteryLevel', '')
        if mastery_level_raw and isinstance(mastery_level_raw, str):
            import ast
            try:
                mastery_dict = ast.literal_eval(mastery_level_raw)
                for mid_str in mastery_dict:
                    mid = int(mid_str)
                    if 100 <= mid < 200:
                        ws_emoji = get_weapon_skill_emoji(mid)
                        if ws_emoji:
                            weapon_skill_emojis.append(ws_emoji)
            except Exception:
                pass

        # 특성 + 팀원 정보
        game_details = await get_game_details(game_id)
        trait_emojis = []
        team_text = ""

        if game_details and game_details.get('userGames'):
            my_match = next((u for u in game_details['userGames'] if u.get('nickname') == self.player_data['nickname']), None)
            if my_match:
                core = my_match.get('traitFirstCore')
                if core:
                    e = get_trait_emoji(core)
                    if e:
                        trait_emojis.append(e)
                for tid in my_match.get('traitFirstSub', []) + my_match.get('traitSecondSub', []):
                    e = get_trait_emoji(tid)
                    if e:
                        trait_emojis.append(e)

            # 팀원 정보
            team_members = extract_team_members_info(game_details, self.player_data['nickname'])
            if team_members:
                tm_lines = []
                for tm in team_members[:2]:
                    tm_char_num = tm.get('characterNum', 0)
                    tm_char = game_data.get_character_name(tm_char_num)
                    tm_char_key = game_data.get_character_key(tm_char_num)
                    tm_emoji = get_character_emoji(tm_char_key) if tm_char_key else ""
                    tm_nick = tm.get('nickname', '')
                    tm_dmg = tm.get('damageToPlayer', 0)
                    tm_lines.append(f"{tm_emoji} {tm_char} **{tm_nick}** | 딜량 {tm_dmg:,}")
                team_text = "\n".join(tm_lines)

        # 텍스트 구성
        self.clear_items()

        # 헤더 라인
        header_parts = [f"# {rank_display}"]
        char_key = game_data.get_character_key(char_code)
        char_emoji = get_character_emoji(char_key) if char_key else ""
        sub_parts = [f"{char_emoji} {char_name} Lv.{level}" if char_emoji else f"{char_name} Lv.{level}"]
        if weapon_emoji:
            sub_parts.append(weapon_emoji)
        if weapon_skill_emojis:
            sub_parts.extend(weapon_skill_emojis)
        if tactical_emoji:
            sub_parts.append(tactical_emoji)
        header_parts.append(" ".join(sub_parts))
        if time_info:
            header_parts.append(f"-# {time_info}")

        # 캐릭터 이미지
        char_image = game.get('characterImage')
        header_display = discord.ui.TextDisplay("\n".join(header_parts))

        if char_image:
            self.add_item(discord.ui.Section(header_display, accessory=discord.ui.Thumbnail(media=char_image)))
        else:
            self.add_item(header_display)

        # 상세 정보 Container
        detail_children = []

        # 아이템
        if item_emojis:
            detail_children.append(discord.ui.TextDisplay(f"**아이템** {' '.join(item_emojis)}"))

        # 특성
        if trait_emojis:
            detail_children.append(discord.ui.TextDisplay(f"**특성** {' '.join(trait_emojis)}"))

        # 전투 정보
        combat_line = f"**TK/K/A** {team_kills}/{kills}/{assists} | **딜량** {damage:,}"
        if actual_mode in (3, 8) and mmr_gain != 0:
            combat_line += f" | **RP** {mmr_gain:+d}"
        detail_children.append(discord.ui.TextDisplay(combat_line))

        # 팀원
        if team_text:
            detail_children.append(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))
            detail_children.append(discord.ui.TextDisplay(team_text))

        # 푸터
        detail_children.append(discord.ui.TextDisplay(f"-# {season_name} | {game_mode_text} | {self._recent_index + 1}/{len(self._recent_games)}"))

        # 네비게이션 버튼 (이전/다음)
        btn_prev = discord.ui.Button(label='◀', style=discord.ButtonStyle.secondary, disabled=(self._recent_index == 0))
        btn_prev.callback = self._on_recent_prev
        btn_back = discord.ui.Button(label='돌아가기', style=discord.ButtonStyle.primary)
        btn_back.callback = self._on_main
        btn_next = discord.ui.Button(label='▶', style=discord.ButtonStyle.secondary, disabled=(self._recent_index >= len(self._recent_games) - 1))
        btn_next.callback = self._on_recent_next
        detail_children.append(discord.ui.ActionRow(btn_prev, btn_back, btn_next))

        self.add_item(discord.ui.Container(*detail_children))
        await interaction.edit_original_response(view=self)

    async def _on_recent_prev(self, interaction):
        """최근전적 이전"""
        await interaction.response.defer()
        if self._recent_index > 0:
            self._recent_index -= 1
        await self._build_recent_game(interaction)

    async def _on_recent_next(self, interaction):
        """최근전적 다음"""
        await interaction.response.defer()
        if self._recent_index < len(self._recent_games) - 1:
            self._recent_index += 1
        await self._build_recent_game(interaction)

    async def _on_season_select(self, interaction):
        """시즌 선택"""
        await interaction.response.defer()
        season_id = int(interaction.data['values'][0])
        season_player_data = await get_player_season_data(self.player_data['nickname'], season_id)

        if season_player_data:
            self.player_data = season_player_data
        self._build_main()
        await interaction.edit_original_response(view=self)

    async def _on_toggle_normal(self, interaction):
        """랭크/일반게임 전환"""
        await interaction.response.defer()
        if self.current_mode == "NORMAL":
            self.current_mode = "RANK"
        else:
            self.current_mode = "NORMAL"

        if self.current_mode == "NORMAL":
            normal_data = await get_player_normal_game_data(self.player_data['nickname'])
            if normal_data:
                self.player_data = normal_data
        else:
            rank_data = await get_player_basic_data(self.player_data['nickname'])
            if rank_data:
                self.player_data = rank_data

        self._build_main()
        await interaction.edit_original_response(view=self)

    async def _on_toggle_union(self, interaction):
        """유니온 모드 전환"""
        await interaction.response.defer()
        if self.current_mode == "UNION":
            self.current_mode = "RANK"
            rank_data = await get_player_basic_data(self.player_data['nickname'])
            if rank_data:
                self.player_data = rank_data
            self._build_main()
            await interaction.edit_original_response(view=self)
        else:
            self.current_mode = "UNION"
            union_data = await get_player_union_teams(self.original_nickname)

            self.clear_items()
            if union_data and union_data.get('teams'):
                self._build_union_layout(union_data)
            else:
                self.add_item(discord.ui.Container(
                    discord.ui.TextDisplay(f"## {self.original_nickname}님의 유니온 정보\n\n유니온 데이터가 없습니다.")
                ))
            self._add_navigation_in_container()
            await interaction.edit_original_response(view=self)

    def _build_union_layout(self, union_data):
        """유니온 정보를 LayoutView Container로 표시"""

        teams = union_data.get('teams', [])
        players = union_data.get('players', [])
        player_tiers = union_data.get('playerTiers', [])

        lines = [f"## {self.original_nickname}님의 유니온 정보\n"]

        for team_idx, team in enumerate(teams):
            team_name = team.get('tnm', f'팀 {team_idx + 1}')
            total_games = team.get('actual_games', 0)
            wins = sum([
                team.get('ssstw', 0), team.get('sstw', 0), team.get('stw', 0),
                team.get('aaatw', 0), team.get('aatw', 0), team.get('atw', 0),
                team.get('bbbtw', 0), team.get('bbtw', 0), team.get('btw', 0),
                team.get('ccctw', 0), team.get('cctw', 0), team.get('ctw', 0),
                team.get('dddtw', 0), team.get('ddtw', 0), team.get('dtw', 0),
                team.get('etw', 0), team.get('ffftw', 0), team.get('fftw', 0), team.get('ftw', 0)
            ])
            win_rate = (wins / total_games * 100) if total_games > 0 else 0
            team_tier_id = team.get('ti', 0)
            team_tier = UNION_TIER_MAP.get(team_tier_id, 'F')

            avg_rank = team.get('avgrnk', 0)
            avg_rank_text = f" | 평균 {avg_rank:.1f}등" if avg_rank > 0 else ""
            top3_rate = team.get('top3_rate', 0)
            top3_text = f" | Top3 {top3_rate:.1f}%" if top3_rate > 0 else ""
            team_rank = team.get('rank', 0)
            rank_percent = team.get('rank_percent', 0)
            rank_text = f"\n순위: {team_rank:,}위 (상위 {rank_percent:.1f}%)" if team_rank > 0 else ""

            lines.append(f"### {team_name}")
            lines.append(f"**티어:** {team_tier}")
            lines.append(f"**전적:** {total_games}게임 {wins}승 (승률 {win_rate:.1f}%){avg_rank_text}{top3_text}{rank_text}")

            # 팀원
            for user_num in team.get('userNums', []):
                player_name = next((p['name'] for p in players if p['userNum'] == user_num), '알수없음')
                tier_info = next((t for t in player_tiers if t['userNum'] == user_num), None)
                if tier_info:
                    mmr = tier_info.get('mmr', 0)
                    t_id = tier_info.get('tierId', 0)
                    t_grade = tier_info.get('tierGradeId', 0)
                    t_emoji = get_tier_emoji(t_id) or ""
                    if not t_emoji:
                        logger.warning(f"[유니온] 티어 이모지 없음: tier_{t_id}")
                    t_name = game_data.get_tier_name(t_id)
                    grade_text = f" {t_grade}" if t_grade else ''
                    lines.append(f"  {t_emoji} {player_name} - {t_name}{grade_text} ({mmr:,} RP)")
                else:
                    lines.append(f"  {player_name} - 언랭")
            lines.append("")

        self.add_item(discord.ui.Container(discord.ui.TextDisplay("\n".join(lines))))

    async def _on_toggle_season_type(self, interaction):
        """정식시즌/프리시즌 전환"""
        await interaction.response.defer()
        self.show_preseason = not self.show_preseason
        self._build_main()
        await interaction.edit_original_response(view=self)


class StatsView(discord.ui.View):
    """embed 기반 전적 조회 UI (서브화면 전환용)

    최근전적/통계(그래프)/유니온 등 embed가 필요할 때 사용.
    메인 버튼 클릭 시 StatsLayoutView로 돌아감.
    """
    def __init__(self, player_data, played_seasons=None, current_mode="RANK", show_preseason=False):
        super().__init__(timeout=300)
        self.player_data = player_data
        self.original_nickname = player_data['nickname']
        self.played_seasons = played_seasons or []
        self.show_preseason = show_preseason
        self.current_mode = current_mode

        # 시즌 선택 메뉴
        season_select = self.create_season_select()
        if season_select:
            self.add_item(season_select)

        # 모드 토글 버튼
        if any(self._is_preseason(s['name']) for s in self.played_seasons):
            normal_label = '랭크게임' if self.current_mode == "NORMAL" else '일반게임'
            normal_button = discord.ui.Button(label=normal_label, style=discord.ButtonStyle.secondary, custom_id='toggle_normal', row=3)
            normal_button.callback = self.toggle_normal_games
            self.add_item(normal_button)

            union_button = discord.ui.Button(label='유니온', style=discord.ButtonStyle.secondary, custom_id='toggle_union', row=3)
            union_button.callback = self.toggle_union_mode
            self.add_item(union_button)

            season_label = '정식시즌' if self.show_preseason else '프리시즌'
            toggle_button = discord.ui.Button(label=season_label, style=discord.ButtonStyle.secondary, custom_id='toggle_season', row=3)
            toggle_button.callback = self.toggle_season_type
            self.add_item(toggle_button)

    @discord.ui.button(label='메인', style=discord.ButtonStyle.primary, row=0)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        """메인 화면 -> StatsLayoutView로 전환"""
        layout = StatsLayoutView(
            self.player_data, self.played_seasons,
            current_mode=self.current_mode, show_preseason=self.show_preseason
        )
        await interaction.response.edit_message(view=layout, embed=None, attachments=[])

    @discord.ui.button(label='실험체', style=discord.ButtonStyle.primary, row=0)
    async def show_characters(self, interaction: discord.Interaction, button: discord.ui.Button):
        """실험체 -> StatsLayoutView로 전환해서 표시"""
        layout = StatsLayoutView(
            self.player_data, self.played_seasons,
            current_mode=self.current_mode, show_preseason=self.show_preseason
        )
        await layout._on_characters(interaction)

    @discord.ui.button(label='최근전적', style=discord.ButtonStyle.success, row=0)
    async def show_recent_games(self, interaction: discord.Interaction, button: discord.ui.Button):
        """최근 게임 전적 표시"""
        await interaction.response.defer()
        game_mode = self.current_mode
        recent_games = await get_player_recent_games(
            self.player_data['nickname'], self.player_data['season_id'], game_mode
        )

        if recent_games:
            if game_mode == "NORMAL":
                recent_games = [g for g in recent_games if g.get('matchingMode') == 2]
            elif game_mode == "RANK":
                recent_games = [g for g in recent_games if g.get('matchingMode') == 3]
            elif game_mode == "UNION":
                recent_games = [g for g in recent_games if g.get('matchingMode') == 8]

        mode_text_map = {"RANK": "랭크게임", "NORMAL": "일반게임", "UNION": "유니온"}
        game_mode_text = mode_text_map.get(game_mode, "게임")

        if not recent_games:
            embed = discord.Embed(
                title=f"{self.player_data['nickname']}님의 최근전적 ({game_mode_text})",
                description=f"{game_mode_text} 데이터가 없습니다.",
                color=0xFF6B35
            )
            await interaction.edit_original_response(embed=embed, view=self)
            return

        recent_games_view = RecentGamesView(
            self.player_data, recent_games[:20], game_mode, game_mode_text, parent_view=self
        )
        embed = await recent_games_view.create_game_embed(0)
        await interaction.edit_original_response(embed=embed, view=recent_games_view)

    @discord.ui.button(label='통계', style=discord.ButtonStyle.secondary, row=0)
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """통계 및 MMR 그래프"""
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
                        mmr_history, self.player_data.get('nickname', '플레이어'), tmp_file.name
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

    def _is_preseason(self, season_name):
        return "프리" in season_name or "Pre" in season_name

    def _filter_seasons_by_type(self):
        if not self.played_seasons:
            return []
        return [s for s in self.played_seasons if self._is_preseason(s['name']) == self.show_preseason][:25]

    def create_season_select(self):
        filtered_seasons = self._filter_seasons_by_type()
        if not filtered_seasons:
            return None
        options = [
            discord.SelectOption(
                label=f"{s['name']}{' (현재)' if s.get('is_current') else ''}",
                value=str(s['id']),
            )
            for s in filtered_seasons
        ]
        if not options:
            return None
        placeholder = "프리시즌별 전적 보기..." if self.show_preseason else "시즌별 전적 보기..."
        select = discord.ui.Select(placeholder=placeholder, options=options)
        select.callback = self.season_select_callback
        return select

    async def season_select_callback(self, interaction):
        await interaction.response.defer()
        season_id = int(interaction.data['values'][0])
        season_player_data = await get_player_season_data(self.player_data['nickname'], season_id)
        if season_player_data:
            self.player_data = season_player_data
        # StatsLayoutView로 전환
        layout = StatsLayoutView(
            self.player_data, self.played_seasons,
            current_mode=self.current_mode, show_preseason=self.show_preseason
        )
        await interaction.edit_original_response(view=layout, embed=None, attachments=[])

    async def toggle_season_type(self, interaction):
        await interaction.response.defer()
        self.show_preseason = not self.show_preseason
        layout = StatsLayoutView(
            self.player_data, self.played_seasons,
            current_mode=self.current_mode, show_preseason=self.show_preseason
        )
        await interaction.edit_original_response(view=layout, embed=None, attachments=[])

    async def toggle_normal_games(self, interaction):
        await interaction.response.defer()
        if self.current_mode == "NORMAL":
            self.current_mode = "RANK"
        else:
            self.current_mode = "NORMAL"
        if self.current_mode == "NORMAL":
            normal_data = await get_player_normal_game_data(self.player_data['nickname'])
            if normal_data:
                self.player_data = normal_data
        else:
            rank_data = await get_player_basic_data(self.player_data['nickname'])
            if rank_data:
                self.player_data = rank_data
        layout = StatsLayoutView(
            self.player_data, self.played_seasons,
            current_mode=self.current_mode, show_preseason=self.show_preseason
        )
        await interaction.edit_original_response(view=layout, embed=None, attachments=[])

    async def toggle_union_mode(self, interaction):
        await interaction.response.defer()
        if self.current_mode == "UNION":
            self.current_mode = "RANK"
            rank_data = await get_player_basic_data(self.player_data['nickname'])
            if rank_data:
                self.player_data = rank_data
            layout = StatsLayoutView(
                self.player_data, self.played_seasons,
                current_mode=self.current_mode, show_preseason=self.show_preseason
            )
            await interaction.edit_original_response(view=layout, embed=None, attachments=[])
        else:
            self.current_mode = "UNION"
            union_data = await get_player_union_teams(self.original_nickname)
            if union_data and union_data.get('teams'):
                embed = create_union_embed(union_data, self.original_nickname)
                await interaction.edit_original_response(embed=embed, view=self, attachments=[])
            else:
                embed = discord.Embed(
                    title=f"{self.original_nickname}님의 유니온 정보",
                    description="유니온 데이터가 없습니다.", color=0xFF0000
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
        """메인으로 돌아가기 (StatsLayoutView로 전환)"""
        if self.parent_view.current_mode == "UNION":
            # 유니온 모드 -> embed + StatsView 유지
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
            # 랭크/일반게임 -> StatsLayoutView로 전환
            layout = StatsLayoutView(
                self.player_data,
                self.parent_view.played_seasons,
                current_mode=self.parent_view.current_mode,
                show_preseason=self.parent_view.show_preseason
            )
            await interaction.response.edit_message(view=layout, embed=None, attachments=[])

    @discord.ui.button(label='▶', style=discord.ButtonStyle.secondary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """다음 게임"""
        if self.current_index < len(self.games) - 1:
            self.current_index += 1
            self.update_buttons()
            embed = await self.create_game_embed(self.current_index)
            await interaction.response.edit_message(embed=embed, view=self)

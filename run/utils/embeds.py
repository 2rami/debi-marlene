"""
Discord Embed 생성 함수들
"""
import discord
from run.services.eternal_return.api_client import game_data


def create_stats_embed(player_data, is_normal_mode=False):
    """플레이어 전적 Embed 생성

    Args:
        player_data: 플레이어 데이터
        is_normal_mode: 일반게임 모드 여부
    """
    if is_normal_mode:
        # 일반게임 모드: 언랭크 표시, 평균순위와 승률만
        rank_info = "일반게임"
        description = ""
        embed = discord.Embed(title=rank_info, description=description, color=0x9932CC)

        # 일반게임 전용 이미지 사용
        normal_game_image_url = "https://cdn.dak.gg/er/images/common/img-gamemode-normal.png"
        embed.set_thumbnail(url=normal_game_image_url)

        # 통계 필드 - 레벨, 평균순위, 승률
        level = player_data.get('level', 1)
        embed.add_field(name="레벨", value=f"**Lv.{level}**", inline=True)

        if player_data.get('stats'):
            stats = player_data['stats']
            embed.add_field(name="평균 순위", value=f"**{stats.get('avg_rank', 0):.1f}등**", inline=True)
            embed.add_field(name="승률", value=f"**{stats.get('winrate', 0):.1f}%**", inline=True)
    else:
        # 랭크게임 모드: 기존 표시 방식
        rank_info = player_data.get('tier_info', 'Unranked')
        description = ""
        rank = player_data.get('rank', 0)
        rank_percent = player_data.get('rank_percent', 0)
        if rank > 0:
            description = f"{rank:,}위 상위 {rank_percent}%"

        embed = discord.Embed(title=rank_info, description=description, color=0x00D4AA)

        if player_data.get('tier_image_url'):
            embed.set_thumbnail(url=player_data['tier_image_url'])

        if player_data.get('most_characters'):
            top_char = player_data['most_characters'][0]
            embed.add_field(name="가장 많이 플레이한 실험체", value=f"**{top_char['name']}** ({top_char['games']}게임)", inline=True)

        if player_data.get('stats'):
            stats = player_data['stats']
            embed.add_field(name="승률", value=f"**{stats.get('winrate', 0):.1f}%**", inline=True)

    nickname = player_data.get('nickname', 'Unknown Player')
    author_icon_url = None
    if player_data.get('most_characters'):
        most_char = player_data['most_characters'][0]
        if most_char.get('image_url'):
            author_icon_url = most_char['image_url']
    embed.set_author(name=nickname, icon_url=author_icon_url)

    # 푸터에 시즌명과 게임 모드 표시
    season_name = game_data.get_season_name(player_data['season_id'])
    game_mode_text = "일반게임" if is_normal_mode else "랭크게임"
    embed.set_footer(text=f"{season_name} • {game_mode_text}")

    return embed


def create_union_embed(union_data, nickname):
    """유니온 정보 Discord 임베드 생성

    Args:
        union_data: 유니온 데이터
        nickname: 플레이어 닉네임
    """
    embed = discord.Embed(title=f"{nickname}님의 유니온 정보", color=0x4B0082)

    teams = union_data.get('teams', [])
    players = union_data.get('players', [])
    player_tiers = union_data.get('playerTiers', [])

    if not teams:
        embed.description = "유니온 팀 정보가 없습니다."
        return embed

    # 가장 높은 티어의 팀 찾기 (썸네일용)
    highest_tier = "F"
    tier_order = ['SSS', 'SS', 'S', 'AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'CC', 'C', 'DDD', 'DD', 'D', 'E', 'FFF', 'FF', 'F']

    for team_idx, team in enumerate(teams):
        team_name = team.get('tnm', f'팀 {team_idx + 1}')

        # 실제 유니온 게임수 (matches API에서 조회)
        total_games = team.get('actual_games', 0)

        # 모든 티어의 승수 합산
        wins = sum([
            team.get('ssstw', 0), team.get('sstw', 0), team.get('stw', 0),
            team.get('aaatw', 0), team.get('aatw', 0), team.get('atw', 0),
            team.get('bbbtw', 0), team.get('bbtw', 0), team.get('btw', 0),
            team.get('ccctw', 0), team.get('cctw', 0), team.get('ctw', 0),
            team.get('dddtw', 0), team.get('ddtw', 0), team.get('dtw', 0),
            team.get('etw', 0), team.get('ffftw', 0), team.get('fftw', 0), team.get('ftw', 0)
        ])
        win_rate = (wins / total_games * 100) if total_games > 0 else 0

        # 팀 현재 티어 (ti 필드 사용)
        team_tier_id = team.get('ti', 0)

        # ti 값을 실제 티어로 매핑
        def get_tier_from_number(tier_num):
            if tier_num >= 90:
                return 'SSS'
            elif tier_num >= 85:
                return 'SS'
            elif tier_num >= 80:
                return 'S'
            elif tier_num >= 75:
                return 'AAA'
            elif tier_num >= 70:
                return 'AA'
            elif tier_num >= 65:
                return 'A'
            elif tier_num >= 60:
                return 'BBB'
            elif tier_num >= 55:
                return 'BB'
            elif tier_num >= 50:
                return 'B'
            elif tier_num >= 45:
                return 'CCC'
            elif tier_num >= 40:  # 43이 CC이므로 40-44가 CC 구간
                return 'CC'
            elif tier_num >= 35:
                return 'C'
            elif tier_num >= 30:
                return 'DDD'
            elif tier_num >= 25:
                return 'DD'
            elif tier_num >= 20:
                return 'D'
            elif tier_num >= 15:
                return 'E'
            elif tier_num >= 10:
                return 'F'
            else:
                return 'F'

        team_tier = get_tier_from_number(team_tier_id)

        # 가장 높은 티어 업데이트 (숫자가 높을수록 높은 티어)
        if team_tier_id > (getattr(get_tier_from_number, 'highest_id', 0)):
            highest_tier = team_tier
            get_tier_from_number.highest_id = team_tier_id

        # 팀원 정보
        user_nums = team.get('userNums', [])
        team_members = []

        for user_num in user_nums:
            player_name = next((p['name'] for p in players if p['userNum'] == user_num), '알수없음')
            tier_info = next((t for t in player_tiers if t['userNum'] == user_num), None)

            if tier_info:
                mmr = tier_info.get('mmr', 0)
                tier_id = tier_info.get('tierId', 0)
                tier_grade = tier_info.get('tierGradeId', 0)

                tier_names = {
                    0: '언랭', 1: '아이언', 2: '브론즈', 3: '실버', 4: '골드',
                    5: '플래티넘', 6: '다이아몬드', 63: '메테오라이트', 66: '미스릴',
                    7: '데미갓', 8: '이터니티'
                }
                tier_name = tier_names.get(tier_id, '언랭')
                member_info = f"{player_name} - {tier_name} {tier_grade if tier_grade else ''} ({mmr:,} MMR)"
            else:
                member_info = f"{player_name} - 언랭"

            team_members.append(member_info)

        # 평균 등수
        avg_rank = team.get('avgrnk', 0)
        avg_rank_text = f" | 평균 {avg_rank:.1f}등" if avg_rank > 0 else ""

        field_value = f"**전적:** {total_games}게임 {wins}승 (승률 {win_rate:.1f}%){avg_rank_text}\n"
        field_value += f"**팀원:**\n" + "\n".join(f"• {member}" for member in team_members)

        embed.add_field(
            name=team_name,
            value=field_value,
            inline=False
        )

    # 가장 높은 티어의 이미지를 썸네일로 설정 (E 티어는 404이므로 제외)
    if highest_tier != "E":
        tier_image_url = f"https://cdn.dak.gg/er/images/union/tier/img_SquadRumble_Rank_{highest_tier}.png"
        embed.set_thumbnail(url=tier_image_url)

    return embed


__all__ = ['create_stats_embed', 'create_union_embed']

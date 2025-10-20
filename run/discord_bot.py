import discord
import asyncio
from discord.ext import commands, tasks
from discord import app_commands
try:
    # main.py에서 실행할 때
    from run.config import characters, DISCORD_TOKEN, OWNER_ID
    from run import config
    from run.api_clients import (
        get_player_basic_data, 
        get_player_season_data, 
        get_player_played_seasons,
        get_player_recent_games,
        get_player_normal_game_data,
        get_player_union_teams,
        get_game_details,
        get_team_members,
        get_character_stats,
        initialize_game_data,
        game_data,
        set_bot_instance
    )
    from run.graph_generator import save_mmr_graph_to_file
    from run.recent_games_image_generator import save_recent_games_image_to_file, save_union_image_to_file
    from run import youtube_service
except ImportError:
    # run 폴더 내에서 실행할 때
    from config import characters, DISCORD_TOKEN, OWNER_ID
    import config
    from api_clients import (
        get_player_basic_data, 
        get_player_season_data, 
        get_player_played_seasons,
        get_player_recent_games,
        get_player_normal_game_data,
        get_player_union_teams,
        get_game_details,
        get_team_members,
        get_character_stats,
        initialize_game_data,
        game_data
    )
    from graph_generator import save_mmr_graph_to_file
    from recent_games_image_generator import save_recent_games_image_to_file, save_union_image_to_file
    import youtube_service

import os
import tempfile
import json
from datetime import datetime
# Flask 내부 API 서버 제거됨
# from flask import Flask, jsonify, request
# import threading

intents = discord.Intents.all()  # 모든 Intents 활성화 (Gateway 기능용)
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Gateway 데이터 저장용 전역 변수
gateway_guild_data = {}  # 서버 데이터
gateway_dm_messages = []  # DM 메시지
gateway_command_logs = []  # 명령어 로그

async def update_guild_data_to_gcs(guild: discord.Guild):
    """특정 서버 데이터를 GCS에 업데이트"""
    try:
        # 온라인 멤버 수 계산
        online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)
        offline_members = sum(1 for m in guild.members if m.status == discord.Status.offline)

        # 서버 데이터
        guild_data = {
            'id': str(guild.id),
            'name': guild.name,
            'member_count': guild.member_count,
            'online_count': online_members,
            'offline_count': offline_members,
            'icon': guild.icon.url if guild.icon else None,
            'owner_id': str(guild.owner_id) if guild.owner_id else None,
            'last_updated': datetime.now().isoformat(),
            'data_source': 'Bot Gateway'
        }

        # 전역 변수에 저장
        gateway_guild_data[str(guild.id)] = guild_data

        # GCS에 저장
        settings = config.load_settings()
        if 'guilds' not in settings:
            settings['guilds'] = {}

        # 기존 설정 유지하면서 실시간 데이터만 업데이트
        if str(guild.id) in settings['guilds']:
            settings['guilds'][str(guild.id)].update({
                'GUILD_NAME': guild.name,
                '멤버수': guild.member_count,
                '온라인수': online_members,
                'GUILD_ICON_HASH': guild.icon.key if guild.icon else None,
                'last_updated': datetime.now().isoformat()
            })
        else:
            settings['guilds'][str(guild.id)] = {
                'GUILD_NAME': guild.name,
                '멤버수': guild.member_count,
                '온라인수': online_members,
                'GUILD_ICON_HASH': guild.icon.key if guild.icon else None,
                'last_updated': datetime.now().isoformat()
            }

        config.save_settings(settings)
        print(f"📊 서버 데이터 GCS 저장: {guild.name} ({guild.member_count}명, 온라인: {online_members})")

    except Exception as e:
        print(f"❌ 서버 데이터 업데이트 실패 {guild.name}: {e}")

@bot.event
async def on_ready():
    """봇 준비 완료 시 실행"""
    print(f'🤖 Discord 봇 연결 완료: {bot.user}')
    print(f'📊 연결된 서버 수: {len(bot.guilds)}')

    # 모든 서버 데이터 수집 및 GCS 저장
    for guild in bot.guilds:
        await update_guild_data_to_gcs(guild)

    print(f'✅ 초기 서버 데이터 수집 완료')

@bot.event
async def on_guild_join(guild):
    """서버 참가 시"""
    print(f'🏠 새 서버 참가: {guild.name} ({guild.id})')
    await update_guild_data_to_gcs(guild)

@bot.event
async def on_guild_remove(guild):
    """서버 나갈 때"""
    print(f'🚪 서버 나감: {guild.name} ({guild.id})')
    if str(guild.id) in gateway_guild_data:
        del gateway_guild_data[str(guild.id)]

@bot.event
async def on_member_join(member):
    """멤버 참가 시"""
    print(f'👋 멤버 참가: {member} -> {member.guild.name}')
    await update_guild_data_to_gcs(member.guild)

@bot.event
async def on_member_remove(member):
    """멤버 탈퇴 시"""
    print(f'👋 멤버 탈퇴: {member} -> {member.guild.name}')
    await update_guild_data_to_gcs(member.guild)

@bot.event
async def on_presence_update(before, after):
    """온라인 상태 변화 시 (5분마다 한 번만 업데이트)"""
    # 너무 자주 업데이트하지 않도록 제한
    import random
    if random.random() < 0.01:  # 1% 확률로만 업데이트 (대략 5분에 한 번)
        await update_guild_data_to_gcs(after.guild)

@bot.event
async def on_message(message):
    """메시지 수신 시"""
    # 봇 자신의 메시지는 무시
    if message.author == bot.user:
        await bot.process_commands(message)
        return

    # DM 메시지 처리
    if isinstance(message.channel, discord.DMChannel):
        dm_data = {
            'id': str(message.id),
            'content': message.content,
            'author': {
                'id': str(message.author.id),
                'username': message.author.display_name,
                'avatar': message.author.display_avatar.url
            },
            'timestamp': message.created_at.isoformat(),
            'type': 'dm_received'
        }

        gateway_dm_messages.append(dm_data)

        # 최대 500개까지만 저장
        if len(gateway_dm_messages) > 500:
            gateway_dm_messages[:] = gateway_dm_messages[-400:]

        print(f'💌 DM 수신: {message.author.display_name} - {message.content[:500]}...')

        # GCS에 DM 채널 정보 저장
        try:
            settings = config.load_settings()
            user_id = str(message.author.id)

            if 'users' not in settings:
                settings['users'] = {}

            if user_id not in settings['users']:
                settings['users'][user_id] = {}

            # DM 채널 ID 저장
            settings['users'][user_id]['dm_channel_id'] = str(message.channel.id)
            settings['users'][user_id]['user_name'] = message.author.display_name
            settings['users'][user_id]['last_dm'] = datetime.now().isoformat()

            config.save_settings(settings)
            print(f'💾 DM 채널 정보 GCS 저장: {message.author.display_name} ({message.channel.id})')
        except Exception as e:
            print(f'❌ DM 채널 정보 GCS 저장 실패: {e}')

    # 명령어 사용 기록 (서버 메시지)
    if message.content.startswith(('/목록', '/놀이', '/추천', '/탈출', '/유튜브')):
        command_data = {
            'id': str(message.id),
            'command': message.content.split()[0],
            'full_content': message.content,
            'author': {
                'id': str(message.author.id),
                'username': message.author.display_name,
                'avatar': message.author.display_avatar.url
            },
            'guild': {
                'id': str(message.guild.id) if message.guild else None,
                'name': message.guild.name if message.guild else 'DM'
            },
            'channel': {
                'id': str(message.channel.id),
                'name': message.channel.name if hasattr(message.channel, 'name') else 'DM'
            },
            'timestamp': message.created_at.isoformat()
        }

        gateway_command_logs.append(command_data)

        # 최대 1000개까지만 저장
        if len(gateway_command_logs) > 1000:
            gateway_command_logs[:] = gateway_command_logs[-800:]

        print(f'⚡ 명령어 사용: {message.author.display_name} - {message.content}')

    # 명령어 처리
    await bot.process_commands(message)

async def save_server_info_for_web_panel():
    """웹 패널용 서버 정보를 JSON 파일로 저장"""
    try:
        # 사용자 정보 수집
        users_data = []
        seen_user_ids = set()
        
        # YouTube 구독자 정보
        subscribers = config.get_youtube_subscribers()
        for user_id in subscribers:
            if user_id not in seen_user_ids:
                seen_user_ids.add(user_id)
                try:
                    # bot.fetch_user 사용하여 API로 실제 정보 가져오기
                    user = await bot.fetch_user(user_id)
                    if user:
                        # display_name 사용하여 실제 닉네임/이름 가져오기
                        user_name = user.display_name or user.global_name or user.name
                        users_data.append({
                            'id': str(user_id),
                            'name': user_name,
                            'type': 'YouTube 구독자',
                            'last_seen': '2025-08-25',
                            'servers': ['구독자 (개인 메시지)']
                        })
                    else:
                        users_data.append({
                            'id': str(user_id),
                            'name': f"User_{str(user_id)[-4:]}",
                            'type': 'YouTube 구독자',
                            'last_seen': '알 수 없음',
                            'servers': ['구독자 (개인 메시지)']
                        })
                except:
                    users_data.append({
                        'id': str(user_id),
                        'name': f"User_{str(user_id)[-4:]}",
                        'type': 'YouTube 구독자',
                        'last_seen': '알 수 없음',
                        'servers': ['구독자 (개인 메시지)']
                    })
        
        # 실제 서버 멤버들 중에서 봇과 상호작용한 사용자들 추가
        interaction_users = config.get_interaction_users()  # 실제 상호작용한 사용자 목록
        
        for user_id in interaction_users:
            if user_id not in seen_user_ids:
                seen_user_ids.add(user_id)
                try:
                    user = await bot.fetch_user(user_id)
                    if user:
                        user_name = user.display_name or user.global_name or user.name
                        # 해당 사용자가 속한 서버들 찾기
                        user_servers = []
                        for guild in bot.guilds:
                            try:
                                member = guild.get_member(user_id)
                                if member:
                                    user_servers.append(guild.name)
                            except:
                                pass
                        
                        users_data.append({
                            'id': str(user_id),
                            'name': user_name,
                            'type': '일반 사용자',
                            'last_seen': '2025-08-25',
                            'servers': user_servers if user_servers else ['알 수 없음']
                        })
                except:
                    users_data.append({
                        'id': str(user_id),
                        'name': f"User_{str(user_id)[-4:]}",
                        'type': '일반 사용자',
                        'last_seen': '알 수 없음',
                        'servers': ['알 수 없음']
                    })
        
        print(f"DEBUG: 실제 사용자 수집 완료 - YouTube 구독자: {len(subscribers)}, 상호작용 사용자: {len(interaction_users)}, 총: {len(users_data)}")
        
        server_data = {
            'updated_at': datetime.now().isoformat(),
            'total_servers': len(bot.guilds),
            'total_members': sum(guild.member_count for guild in bot.guilds),
            'total_users': len(users_data),
            'servers': [],
            'users': users_data
        }
        
        for guild in bot.guilds:
            # 공지 채널 설정 확인
            guild_settings = config.get_guild_settings(guild.id)
            announcement_channel_id = guild_settings.get('ANNOUNCEMENT_CHANNEL_ID')
            announcement_channel_name = "미설정"
            announcement_display = "미설정"
            
            if announcement_channel_id:
                try:
                    channel = guild.get_channel(announcement_channel_id)
                    if channel:
                        announcement_channel_name = f"#{channel.name}"
                        announcement_display = f"#{channel.name} (ID: {announcement_channel_id})"
                    else:
                        announcement_channel_name = f"채널 ID: {announcement_channel_id} (접근불가)"
                        announcement_display = f"채널 ID: {announcement_channel_id} (접근불가)"
                except:
                    announcement_channel_name = f"채널 ID: {announcement_channel_id}"
                    announcement_display = f"채널 ID: {announcement_channel_id}"
            
            server_info = {
                'id': str(guild.id),
                'name': guild.name,
                'member_count': guild.member_count,
                'joined_at': guild.me.joined_at.isoformat() if guild.me.joined_at else None,
                'announcement_channel': announcement_channel_name,
                'announcement_channel_display': announcement_display,
                'announcement_channel_id': announcement_channel_id,
                'status': '활성' if announcement_channel_id else '설정 필요',
                'is_configured': bool(announcement_channel_id)
            }
            
            server_data['servers'].append(server_info)
        
        # JSON 파일로 저장
        web_panel_data_path = os.path.join(os.path.dirname(__file__), 'web_panel_data.json')
        with open(web_panel_data_path, 'w', encoding='utf-8') as f:
            json.dump(server_data, f, ensure_ascii=False, indent=2)
        
        # S3의 settings.json에도 서버 정보 업데이트
        try:
            current_settings = config.load_settings()
            
            # 각 서버의 실제 정보를 settings.json의 guilds에 업데이트
            for server in server_data['servers']:
                guild_id = server['id']
                if guild_id in current_settings.get('guilds', {}):
                    # 기존 설정 유지하면서 실제 정보 업데이트
                    current_settings['guilds'][guild_id].update({
                        'GUILD_NAME': server['name'],
                        '멤버수': server['member_count'],
                        '가입일': server['joined_at'],
                        '상태': server['status'],
                        '마지막_업데이트': datetime.now().isoformat()
                    })
            
            config.save_settings(current_settings)
            print("✅ S3 settings.json 서버 정보 업데이트 완료", flush=True)
        except Exception as e:
            print(f"⚠️ S3 settings.json 업데이트 실패: {e}", flush=True)
        
        print(f"📊 웹 패널 데이터 저장: {len(server_data['servers'])}개 서버, {server_data['total_members']:,}명", flush=True)
        
    except Exception as e:
        print(f"❌ 웹 패널 데이터 저장 실패: {e}", flush=True)

@tasks.loop(minutes=30)  # 30분마다 서버 정보 업데이트
async def update_server_info():
    """정기적으로 서버 정보를 업데이트"""
    if bot.is_ready():
        await save_server_info_for_web_panel()

@update_server_info.before_loop
async def before_update_server_info():
    """봇이 준비될 때까지 기다림"""
    await bot.wait_until_ready()

# --- Periodic Tasks ---

@tasks.loop(minutes=5)  # 5분마다 실행 (웹 패널 실시간 모니터링을 위해)
async def periodic_guild_logging():
    """정기적으로 봇의 서버 연결 상태를 로깅 (AWS CloudWatch에서 파싱 가능)"""
    import sys
    
    if not bot.is_ready():
        return
        
    try:
        guild_count = len(bot.guilds)
        total_members = sum(guild.member_count for guild in bot.guilds if guild.member_count)
        
        # 서버 수와 전체 멤버 수 로깅
        print(f"📊 정기 체크: 현재 {guild_count}개 서버에 연결, 총 {total_members}명 사용자", flush=True)
        sys.stdout.flush()
        
        # 큰 서버들 로깅 (100명 이상)
        large_guilds = [g for g in bot.guilds if g.member_count and g.member_count >= 100]
        if large_guilds:
            print(f"📈 대형 서버({len(large_guilds)}개): {', '.join([f'{g.name}({g.member_count}명)' for g in large_guilds[:3]])}", flush=True)
            sys.stdout.flush()
        
        # 최근 가입한 서버들 (7일 이내)
        from datetime import datetime, timedelta
        import discord.utils
        recent_threshold = discord.utils.utcnow() - timedelta(days=7)
        
        recent_guilds = []
        for guild in bot.guilds:
            try:
                if guild.me.joined_at and guild.me.joined_at > recent_threshold:
                    recent_guilds.append(guild)
            except Exception as e:
                # 타임존 비교 오류 무시하고 계속 진행
                continue
        
        if recent_guilds:
            print(f"🆕 최근 가입 서버({len(recent_guilds)}개): {', '.join([f'{g.name}(ID:{g.id})' for g in recent_guilds[:3]])}", flush=True)
            sys.stdout.flush()
            
    except Exception as e:
        print(f"⚠️ 정기 서버 로깅 오류: {e}", flush=True)
        sys.stdout.flush()

@periodic_guild_logging.before_loop
async def before_periodic_logging():
    """정기 로깅 시작 전 봇이 준비될 때까지 대기"""
    await bot.wait_until_ready()

# --- Helper Functions ---

def create_character_embed(character, title, description, command_used=""):
    embed = discord.Embed(title=title, description=description, color=character.get("color", 0xFF0000))
    if command_used:
        embed.set_footer(text=f"사용된 명령어: {command_used}")
    return embed

def create_stats_embed(player_data, is_normal_mode=False):
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
    """
    유니온 정보를 Discord 임베드로 생성
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
        
        # 팀 티어 계산 (간단한 방식으로 구현)
        total_games = team.get('ti', 0)
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
        
        # ti 값을 실제 티어로 매핑 (사이트 확인: ti=43 = CC)
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

# --- UI Views ---

class StatsView(discord.ui.View):
    def __init__(self, player_data, played_seasons=None):
        super().__init__(timeout=300)
        self.player_data = player_data
        self.original_nickname = player_data['nickname']  # 원본 닉네임 보존
        self.played_seasons = played_seasons or []
        self.show_preseason = False
        self.show_normal_games = False  # 일반게임 모드
        
        # 시즌 선택 추가
        season_select = self.create_season_select()
        if season_select:
            self.add_item(season_select)
        
        # 프리시즌이 있으면 프리시즌 버튼과 일반게임 버튼을 3번째 줄에 추가
        if any(self._is_preseason(s['name']) for s in self.played_seasons):
            toggle_button = discord.ui.Button(label='프리시즌 보기', style=discord.ButtonStyle.secondary, custom_id='toggle_season', row=3)
            toggle_button.callback = self.toggle_season_type
            self.add_item(toggle_button)
            
            normal_button = discord.ui.Button(label='일반게임', style=discord.ButtonStyle.secondary, custom_id='toggle_normal', row=3)
            normal_button.callback = self.toggle_normal_games
            self.add_item(normal_button)

    @discord.ui.button(label='메인', style=discord.ButtonStyle.primary, row=0)
    async def back_to_main(self, interaction: discord.Interaction, button):
        embed = create_stats_embed(self.player_data, self.show_normal_games)
        await interaction.response.edit_message(embed=embed, view=self, attachments=[])

    @discord.ui.button(label='실험체', style=discord.ButtonStyle.primary, row=0)
    async def show_characters(self, interaction: discord.Interaction, button):
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
    async def show_recent_games(self, interaction: discord.Interaction, button):
        await interaction.response.defer()
        
        # 게임 모드 결정: 일반게임 모드면 0, 아니면 3 (랭크)
        game_mode = 0 if self.show_normal_games else 3
        
        recent_games = await get_player_recent_games(
            self.player_data['nickname'], 
            self.player_data['season_id'],
            game_mode
        )
        
        # 게임 모드별 데이터 필터링 (클라이언트에서 한번 더 확인)
        if recent_games:
            if game_mode == 0:  # 일반게임만 원하는 경우
                recent_games = [game for game in recent_games if game.get('matchingMode') == 0]
            else:  # 랭크게임(듀오, 솔로)만 원하는 경우  
                recent_games = [game for game in recent_games if game.get('matchingMode') in [2, 3]]
        
        # 실제 매치 데이터에서 게임 모드 확인하여 정확한 레이블 표시
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
        
        # 이미지 생성 실패하거나 데이터가 없는 경우 기존 방식 사용
        embed = discord.Embed(
            title=f"{self.player_data['nickname']}님의 최근전적 ({game_mode_text})", 
            color=0x9932CC if game_mode == 0 else 0xFF6B35
        )
        
        season_name = game_data.get_season_name(self.player_data['season_id'])
        embed.set_footer(text=f"{season_name}")
        
        if recent_games:
            for i, game in enumerate(recent_games[:8]):  # 최대 8게임 (임베드 필드 제한)
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
    async def show_stats(self, interaction: discord.Interaction, button):
        await interaction.response.defer()
        embed = discord.Embed(title=f"{self.player_data['nickname']}님의 통계", color=0xE67E22)
        stats = self.player_data.get('stats', {})
        file_attachment = None
        graph_path = None
        mmr_history = self.player_data.get('mmr_history', [])
        if mmr_history and len(mmr_history) >= 2:
            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    graph_path = save_mmr_graph_to_file(mmr_history, self.player_data.get('nickname', '플레이어'), tmp_file.name)
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
            if graph_path: os.unlink(graph_path)
        else:
            await interaction.edit_original_response(embed=embed, view=self)

    def _is_preseason(self, season_name: str) -> bool:
        return "프리" in season_name or "Pre" in season_name

    def _filter_seasons_by_type(self):
        if not self.played_seasons:
            return []
        return [s for s in self.played_seasons if self._is_preseason(s['name']) == self.show_preseason][:25]

    def create_season_select(self):
        filtered_seasons = self._filter_seasons_by_type()
        if not filtered_seasons:
            return None
        options = [discord.SelectOption(label=f"{s['name']}{ ' (현재)' if s.get('is_current') else ''}", value=str(s['id']), emoji="🔥" if s.get('is_current') else None) for s in filtered_seasons]
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
            embed = create_stats_embed(season_player_data, self.show_normal_games)
        else:
            season_name = game_data.get_season_name(season_id)
            embed = discord.Embed(title=f"{self.player_data['nickname']}님의 {season_name} 전적", description="해당 시즌 데이터를 찾을 수 없습니다.", color=0xE74C3C)
            embed.set_footer(text=season_name)
        
        # 기존 뷰를 업데이트 (새로운 뷰를 생성하지 않음)
        await interaction.edit_original_response(embed=embed, view=self)
    
    async def toggle_season_type(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.show_preseason = not self.show_preseason
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
            # 랭크게임 모드로 전환할 때 원래 데이터 복원 (현재 시즌 데이터 다시 가져오기)
            rank_data = await get_player_basic_data(self.player_data['nickname'])
            if rank_data:
                self.player_data = rank_data
        
        # 메인 임베드로 돌아가기 (모드 변경 적용)
        embed = create_stats_embed(self.player_data, self.show_normal_games)
        
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='유니온', style=discord.ButtonStyle.secondary, row=3)
    async def show_union(self, interaction: discord.Interaction, button):
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


class CharacterStatsView(discord.ui.View):
    def __init__(self, stats_data, tier, period, page=0):
        super().__init__(timeout=60)
        self.stats_data = stats_data
        self.tier = tier
        self.period = period
        self.page = page
        self.max_items_per_page = 10
        
        character_stats = stats_data.get("characterStatSnapshot", {}).get("characterStats", [])
        self.total_pages = (len(character_stats) - 1) // self.max_items_per_page + 1
        
        # 버튼 업데이트
        self.update_buttons()
    
    def update_buttons(self):
        # 이전 페이지 버튼
        self.prev_button.disabled = self.page == 0
        # 다음 페이지 버튼
        self.next_button.disabled = self.page >= self.total_pages - 1
    
    def create_embed(self):
        tier_names = {
            "all": "전체",
            "diamond_plus": "다이아+",
            "unranked": "언랭크", 
            "iron": "아이언",
            "bronze": "브론즈",
            "silver": "실버",
            "gold": "골드",
            "platinum": "플래티넘",
            "diamond": "다이아몬드"
        }
        tier_name = tier_names.get(self.tier, self.tier)
        
        embed = discord.Embed(
            title=f"🏆 캐릭터 통계 ({tier_name} / {self.period}일) - 페이지 {self.page + 1}/{self.total_pages}",
            color=0x00ff00
        )
        
        character_stats = self.stats_data.get("characterStatSnapshot", {}).get("characterStats", [])
        start_idx = self.page * self.max_items_per_page
        end_idx = start_idx + self.max_items_per_page
        page_stats = character_stats[start_idx:end_idx]
        
        description_lines = []
        for i, char_stat in enumerate(page_stats, start_idx + 1):
            char_id = char_stat.get("key", 0)
            char_name = game_data.get_character_name(char_id)
            count = char_stat.get("count", 0)
            
            # 승률 계산 (첫 번째 무기 스탯 기준)
            weapon_stats = char_stat.get("weaponStats", [])
            if weapon_stats:
                weapon = weapon_stats[0]
                wins = weapon.get("win", 0)
                total_games = weapon.get("count", 1)
                win_rate = (wins / total_games * 100) if total_games > 0 else 0
                tier_score = weapon.get("tierScore", 0)
                tier = weapon.get("tier", "?")
                
                description_lines.append(
                    f"`{i:2d}` **{char_name}** `{tier}티어` "
                    f"`{win_rate:.1f}%` ({count:,}게임)"
                )
            else:
                description_lines.append(f"`{i:2d}` **{char_name}** ({count:,}게임)")
        
        embed.description = "\n".join(description_lines)
        
        # 메타 정보 추가
        meta = self.stats_data.get("meta", {})
        patch = meta.get("patch", 0)
        tier_game_count = self.stats_data.get("characterStatSnapshot", {}).get("tierGameCount", 0)
        
        # 패치 버전 변환 (8040 -> 8.4)
        patch_str = str(patch)
        if len(patch_str) >= 3:
            patch_version = f"{patch_str[0]}.{patch_str[1:]}"
            # 끝의 0 제거 (예: 8.40 -> 8.4)
            patch_version = patch_version.rstrip('0').rstrip('.')
        else:
            patch_version = patch_str
        
        embed.set_footer(text=f"패치 {patch_version} | 총 {tier_game_count:,}게임 분석")
        
        return embed
    
    @discord.ui.button(label="◀", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.total_pages - 1:
            self.page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⚙️ 바로 설정하기", style=discord.ButtonStyle.success, custom_id="welcome_setup_button")
    async def setup_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("이 버튼은 서버 관리자만 사용할 수 있어요!", ephemeral=True)
            return
        
        embed = discord.Embed(title="⚙️ 서버 설정", description="아래 버튼으로 유튜브 공지 채널과 명령어 전용 채널을 설정하세요.", color=0x7289DA)
        embed.add_field(name="📢 공지 채널", value="유튜브 새 영상 알림이 올라갈 채널입니다. (필수)", inline=False)
        embed.add_field(name="💬 채팅 채널", value="`/전적` 등 봇의 명령어를 사용할 특정 채널입니다. 설정하지 않으면 모든 채널에서 사용 가능합니다. (선택)", inline=False)
        view = SettingsView(interaction.guild)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class SettingsView(discord.ui.View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=180)
        self.guild = guild

    def update_components(self):
        if len(self.children) < 2:
            return
            
        guild_settings = config.get_guild_settings(self.guild.id)
        announcement_ch_id = guild_settings.get("ANNOUNCEMENT_CHANNEL_ID")
        chat_ch_id = guild_settings.get("CHAT_CHANNEL_ID")

        announcement_button = self.children[0]
        if announcement_ch_id and (ch := self.guild.get_channel(announcement_ch_id)):
            announcement_button.label = f"📢 공지 채널: #{ch.name}"
            announcement_button.style = discord.ButtonStyle.success
        else:
            announcement_button.label = "📢 공지 채널 설정"
            announcement_button.style = discord.ButtonStyle.secondary

        chat_button = self.children[1]
        if chat_ch_id and (ch := self.guild.get_channel(chat_ch_id)):
            chat_button.label = f"💬 채팅 채널: #{ch.name}"
            chat_button.style = discord.ButtonStyle.success
        else:
            chat_button.label = "💬 채팅 채널 설정 (선택사항)"
            chat_button.style = discord.ButtonStyle.secondary

    @discord.ui.button(label="📢 공지 채널 설정", style=discord.ButtonStyle.secondary, custom_id="setting_announcement")
    async def announcement_button_handler(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ChannelSelectViewForSetting("announcement")
        await interaction.response.send_message("유튜브 영상 알림을 받을 채널을 선택해주세요.", view=view, ephemeral=True)

    @discord.ui.button(label="💬 채팅 채널 설정 (선택사항)", style=discord.ButtonStyle.secondary, custom_id="setting_chat")
    async def chat_button_handler(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ChannelSelectViewForSetting("chat")
        await interaction.response.send_message("명령어 사용을 제한할 채널을 선택해주세요 (없으면 모두 허용).", view=view, ephemeral=True)

class ChannelSelectViewForSetting(discord.ui.View):
    def __init__(self, channel_type: str):
        super().__init__(timeout=180)
        self.channel_type = channel_type
        label = "공지" if channel_type == "announcement" else "채팅"
        placeholder = f"#{label} 채널을 선택하세요..."
        self.select_menu = discord.ui.ChannelSelect(
            placeholder=placeholder,
            channel_types=[discord.ChannelType.text]
        )
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        try:
            # 즉시 응답하여 타임아웃 방지
            await interaction.response.defer()
            
            channel = self.select_menu.values[0]
            if self.channel_type == "announcement":
                import sys
                print(f"DEBUG: 서버 ID: {interaction.guild.id}, 채널 ID: {channel.id}", flush=True)
                sys.stdout.flush()
                result = config.save_guild_settings(
                    interaction.guild.id, 
                    announcement_id=channel.id, 
                    guild_name=interaction.guild.name,
                    announcement_channel_name=channel.name
                )
                print(f"DEBUG: 저장 결과: {result}", flush=True)
                sys.stdout.flush()
                # 저장 후 바로 확인
                saved_settings = config.get_guild_settings(interaction.guild.id)
                print(f"DEBUG: 저장된 설정: {saved_settings}", flush=True)
                sys.stdout.flush()
                await interaction.followup.edit_message(interaction.message.id, content=f"✅ 공지 채널이 {channel.mention}으로 설정되었습니다.", view=None)
            else:
                result = config.save_guild_settings(
                    interaction.guild.id, 
                    chat_id=channel.id,
                    guild_name=interaction.guild.name,
                    chat_channel_name=channel.name
                )
                print(f"DEBUG: 채팅 채널 저장 결과: {result}", flush=True)
                await interaction.followup.edit_message(interaction.message.id, content=f"✅ 채팅 채널이 {channel.mention}으로 설정되었습니다.", view=None)
        except Exception as e:
            print(f"❌ 채널 설정 오류: {e}", flush=True)
            try:
                await interaction.followup.send("설정 중 오류가 발생했습니다.", ephemeral=True)
            except:
                pass

# --- Bot Events ---

@bot.event
async def on_ready():
    import sys
    print(f'🤖 {bot.user} 봇이 시작되었습니다!', flush=True)
    sys.stdout.flush()
    
    # 봇이 연결된 서버 수 로깅 (AWS CloudWatch에서 파싱 가능하도록)
    guild_count = len(bot.guilds)
    total_members = sum(guild.member_count for guild in bot.guilds if guild.member_count)
    print(f"📊 현재 {guild_count}개 서버에 연결되었습니다, 총 {total_members}명 사용자", flush=True)
    print(f"📊 정기 체크: 현재 {guild_count}개 서버에 연결, 총 {total_members}명 사용자", flush=True)
    sys.stdout.flush()
    
    # settings.json에 기존 서버들의 이름 정보 업데이트
    print("📝 기존 서버들의 정보를 settings.json에 업데이트 중...", flush=True)
    updated_count = 0
    for guild in bot.guilds:
        try:
            # 기존 설정 불러오기
            guild_settings = config.get_guild_settings(guild.id)
            
            # 채널 정보도 함께 업데이트
            announcement_channel_name = None
            chat_channel_name = None
            
            if guild_settings.get('ANNOUNCEMENT_CHANNEL_ID'):
                announcement_channel = guild.get_channel(guild_settings['ANNOUNCEMENT_CHANNEL_ID'])
                if announcement_channel:
                    announcement_channel_name = announcement_channel.name
            
            if guild_settings.get('CHAT_CHANNEL_ID'):
                chat_channel = guild.get_channel(guild_settings['CHAT_CHANNEL_ID'])
                if chat_channel:
                    chat_channel_name = chat_channel.name
            
            # 서버 정보 업데이트
            config.save_guild_settings(
                guild.id,
                announcement_id=guild_settings.get('ANNOUNCEMENT_CHANNEL_ID'),
                chat_id=guild_settings.get('CHAT_CHANNEL_ID'),
                guild_name=guild.name,
                announcement_channel_name=announcement_channel_name,
                chat_channel_name=chat_channel_name
            )
            updated_count += 1
        except Exception as e:
            print(f"⚠️ {guild.name} 서버 정보 업데이트 실패: {e}", flush=True)
    
    print(f"✅ {updated_count}개 서버 정보 업데이트 완료", flush=True)
    sys.stdout.flush()
    
    # 처음 몇 개 서버 정보 로깅 (디버깅용)
    for i, guild in enumerate(bot.guilds[:5]):
        print(f"서버 {i+1}: {guild.name} (ID: {guild.id}) - 멤버 {guild.member_count}명", flush=True)
        sys.stdout.flush()
    
    if guild_count > 5:
        print(f"... 외 {guild_count - 5}개 서버", flush=True)
        sys.stdout.flush()
    
    # 기존 사용자들의 이름 정보 업데이트
    print("📝 기존 사용자들의 이름 정보를 settings.json에 업데이트 중...", flush=True)
    settings = config.load_settings()
    existing_users = settings.get("users", {})
    user_update_count = 0
    
    for user_id_str, user_data in existing_users.items():
        if "user_name" not in user_data or not user_data["user_name"]:
            try:
                user_id = int(user_id_str)
                user = await bot.fetch_user(user_id)
                if user:
                    user_name = user.display_name or user.global_name or user.name
                    config.log_user_interaction(user_id, user_name)
                    user_update_count += 1
                    print(f"  -> 사용자 {user_id} 이름 업데이트: {user_name}", flush=True)
            except Exception as e:
                print(f"  -> ⚠️ 사용자 {user_id_str} 이름 업데이트 실패: {e}", flush=True)
    
    print(f"✅ {user_update_count}개 사용자 이름 업데이트 완료", flush=True)
    sys.stdout.flush()
    
    # 웹 패널을 위한 봇 인스턴스 저장
    try:
        set_bot_instance(bot)
        print("🌐 웹 패널용 봇 인스턴스 등록 완료", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"⚠️ 웹 패널용 봇 인스턴스 등록 실패: {e}", flush=True)
        sys.stdout.flush()
    
    # 웹 패널용 서버 정보 JSON 파일로 저장
    try:
        await save_server_info_for_web_panel()
        print("💾 웹 패널용 서버 정보 저장 완료", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"⚠️ 서버 정보 저장 실패: {e}", flush=True)
        sys.stdout.flush()
    
    # 서버 정보 정기 업데이트 태스크 시작
    try:
        update_server_info.start()
        print("🔄 서버 정보 정기 업데이트 태스크 시작 (30분 간격)", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"⚠️ 서버 정보 업데이트 태스크 시작 실패: {e}", flush=True)
        sys.stdout.flush()
    
    try:
        print("🔧 명령어 동기화 시작...", flush=True)
        sys.stdout.flush()
        
        # 명령어 동기화 (기존 명령어 업데이트)
        synced = await bot.tree.sync()
        print(f"✅ 명령어 동기화 완료: {len(synced)}개 명령어", flush=True)
        
        print("✅ 모든 명령어 동기화 완료.", flush=True)
        sys.stdout.flush()
        
        print("🔧 게임 데이터 초기화 시작...", flush=True)
        sys.stdout.flush()
        await initialize_game_data()
        print("✅ 게임 데이터 초기화 완료.", flush=True)
        sys.stdout.flush()
        
        print("🔧 유튜브 서비스 설정 시작...", flush=True)
        sys.stdout.flush()
        youtube_service.set_bot_instance(bot)
        print("🔧 유튜브 API 초기화 시작...", flush=True)
        sys.stdout.flush()
        await youtube_service.initialize_youtube()
        print("🔧 유튜브 체크 루프 시작...", flush=True)
        sys.stdout.flush()
        youtube_service.check_new_videos.start()
        
        # 정기적 서버 수 로깅 태스크 시작
        periodic_guild_logging.start()
        print("🔧 정기 서버 수 로깅 시작...", flush=True)
        sys.stdout.flush()
        
        print("✅ 모든 초기화 완료!", flush=True)
        sys.stdout.flush()
        
        # Blue 서버의 과거 메시지 수집 (한 번만 실행)
        try:
            blue_guild_id = 896603083851833388
            await config.fetch_old_messages_for_guild(bot, blue_guild_id, max_messages_per_channel=500)
        except Exception as e:
            print(f"⚠️ 과거 메시지 수집 중 오류 (계속 진행): {e}", flush=True)
    except Exception as e:
        print(f"❌ CRITICAL: 데이터 초기화 중 봇 시작 실패: {e}", flush=True)
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        await bot.close()

# 환영 메시지를 보낸 서버를 추적하는 세트 (세션 중 중복 방지용)
welcomed_guilds = set()
# 환영 메시지 전송 시간을 추적 (빠른 중복 이벤트 방지)
welcome_timestamps = {}

@bot.event
async def on_guild_join(guild: discord.Guild):
    import sys
    import time
    
    current_time = time.time()
    print(f"✅ 새로운 서버에 초대되었습니다: {guild.name} (ID: {guild.id}) - 멤버 {guild.member_count}명", flush=True)
    sys.stdout.flush()
    
    # 빠른 중복 이벤트 방지 (30초 이내 같은 서버 초대 무시)
    if guild.id in welcome_timestamps:
        time_diff = current_time - welcome_timestamps[guild.id]
        if time_diff < 30:  # 30초 이내라면 중복으로 간주
            print(f"⚠️ 빠른 중복 이벤트 감지 ({time_diff:.1f}초 전): {guild.name} (ID: {guild.id})", flush=True)
            return
    
    # settings.json에 이미 존재하고 활성 상태인 서버라면 환영 메시지 생략 (재시작으로 인한 중복 방지)
    settings = config.load_settings()
    guild_id_str = str(guild.id)
    if guild_id_str in settings.get("guilds", {}):
        guild_settings = settings["guilds"][guild_id_str]
        # 삭제됨 상태가 아닌 경우에만 환영 메시지 생략
        if guild_settings.get("STATUS") != "삭제됨":
            print(f"⚠️ 이미 등록된 서버입니다 (환영 메시지 생략): {guild.name} (ID: {guild.id})", flush=True)
            return
        else:
            print(f"🔄 삭제됨 상태에서 재초대된 서버입니다: {guild.name} (ID: {guild.id})", flush=True)
    
    # 재초대된 서버가 아니면 중복 체크 (재초대된 경우는 환영 메시지를 다시 보냄)
    is_reinvited = guild_id_str in settings.get("guilds", {}) and settings["guilds"][guild_id_str].get("STATUS") == "삭제됨"
    if not is_reinvited and guild.id in welcomed_guilds:
        print(f"⚠️ 현재 세션에서 이미 환영 메시지를 보낸 서버입니다: {guild.name} (ID: {guild.id})", flush=True)
        return
    
    # 서버를 환영 메시지 목록에 추가 (현재 세션 중복 방지)
    welcomed_guilds.add(guild.id)
    welcome_timestamps[guild.id] = current_time
    print(f"DEBUG: 서버 {guild.id}를 환영 메시지 목록에 추가", flush=True)
    
    # 삭제됨 상태인 서버라면 상태 초기화
    if guild_id_str in settings.get("guilds", {}) and settings["guilds"][guild_id_str].get("STATUS") == "삭제됨":
        # 삭제됨 상태와 관련 필드들 제거하여 정상 상태로 복구
        guild_settings = settings["guilds"][guild_id_str].copy()
        guild_settings.pop("STATUS", None)
        guild_settings.pop("REMOVED_AT", None)
        print(f"🔄 삭제됨 상태 초기화: {guild.name} (ID: {guild.id})", flush=True)
        
        # 업데이트된 설정으로 저장
        config.save_guild_settings(
            guild.id,
            guild_name=guild.name,
            announcement_id=guild_settings.get("ANNOUNCEMENT_CHANNEL_ID"),
            announcement_channel_name=guild_settings.get("ANNOUNCEMENT_CHANNEL_NAME"),
            chat_id=guild_settings.get("CHAT_CHANNEL_ID"),
            chat_channel_name=guild_settings.get("CHAT_CHANNEL_NAME")
        )
    else:
        # settings.json에 새로운 서버 정보 추가 (자동 설정 없이)
        config.save_guild_settings(
            guild.id,
            guild_name=guild.name
        )
    print(f"📝 settings.json에 서버 정보 저장 완료: {guild.name}", flush=True)
    
    # 현재 총 서버 수 업데이트 로깅
    guild_count = len(bot.guilds)
    print(f"📊 서버 추가 후 총 {guild_count}개 서버에 연결됨", flush=True)
    sys.stdout.flush()
    
    target_channel = guild.system_channel
    if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                target_channel = channel
                break
    
    if target_channel:
        try:
            profile_image = discord.File("assets/profile.webp", filename="profile.webp")
            
            if is_reinvited:
                # 재초대된 서버용 메시지
                embed = discord.Embed(title="🎉 다시 만나게 되어 반가워요!", description="저희를 다시 불러주셔서 정말 기뻐요! 이전 설정을 그대로 유지하고 있어요.", color=characters["marlene"]["color"])
                embed.set_thumbnail(url="attachment://profile.webp")
                embed.add_field(name=f"{characters['debi']['name']}", value=f"> 또 만나니까 정말 좋네요!", inline=False)
                embed.add_field(name=f"{characters['marlene']['name']}", value=f"> 이전처럼 열심히 도와드릴게요!", inline=False)
                embed.add_field(name="⚙️ 설정 확인", value="이전 **공지 채널**과 **채팅 채널** 설정을 확인하고 싶으시다면\n아래 버튼을 눌러주세요!", inline=False)
            else:
                # 새로운 서버용 메시지  
                embed = discord.Embed(title="👋 저희를 불러주셨네요!", description="이곳에서 여러분과 함께하게 되어 정말 기뻐요!", color=characters["debi"]["color"])
                embed.set_thumbnail(url="attachment://profile.webp")
                embed.add_field(name=f"{characters['debi']['name']}", value=f"> {characters['debi']['welcome_message']}", inline=False)
                embed.add_field(name=f"{characters['marlene']['name']}", value=f"> {characters['marlene']['welcome_message']}", inline=False)
                embed.add_field(name="⚙️ 초기 설정 안내", value="제가 제대로 활동하려면 **공지 채널**과 **채팅 채널** 설정이 필요해요.\n아래 버튼을 눌러 바로 시작할 수 있습니다!", inline=False)
            
            view = WelcomeView()
            await target_channel.send(file=profile_image, embed=embed, view=view)
            
            message_type = "재초대 환영" if is_reinvited else "초기 환영"
            print(f"✅ {message_type} 메시지 전송 완료: {guild.name} (ID: {guild.id})", flush=True)
        except Exception as e:
            print(f"❌ 환영 메시지 전송 중 오류 발생: {e}")

@bot.event
async def on_guild_remove(guild: discord.Guild):
    """서버에서 봇이 제거될 때 설정 삭제 및 로깅"""
    import sys
    print(f"❌ 서버에서 제거되었습니다: {guild.name} (ID: {guild.id})", flush=True)
    
    try:
        # config.py의 remove_guild_settings 함수 호출 (삭제됨 표시 추가)
        if config.remove_guild_settings(guild.id):
            print(f"✅ 서버에 삭제됨 표시가 추가되었습니다: {guild.name} (ID: {guild.id})", flush=True)
        else:
            print(f"⚠️ 서버 삭제됨 표시 추가 실패: {guild.name} (ID: {guild.id})", flush=True)
    except Exception as e:
        print(f"❌ 서버 삭제됨 표시 추가 중 예외 발생: {e}", flush=True)
        import traceback
        traceback.print_exc()
    
    sys.stdout.flush()
    
    # 현재 총 서버 수 업데이트 로깅
    guild_count = len(bot.guilds)
    print(f"📊 서버 제거 후 총 {guild_count}개 서버에 연결됨", flush=True)
    sys.stdout.flush()

@bot.event
async def on_message(message: discord.Message):
    """모든 메시지를 로깅합니다 (Blue 서버만). DM 채널 정보도 GCS에 저장합니다."""
    # 봇 자신의 메시지는 무시
    if message.author.bot:
        return

    # DM 메시지 처리 (채널 ID를 GCS에 저장)
    if not message.guild:
        try:
            user_name = message.author.display_name or message.author.global_name or message.author.name
            user_id = str(message.author.id)
            channel_id = str(message.channel.id)

            # settings.json에 DM 채널 정보 저장
            settings = config.load_settings()
            if 'users' not in settings:
                settings['users'] = {}

            if user_id not in settings['users']:
                settings['users'][user_id] = {}

            # DM 채널 정보 업데이트
            settings['users'][user_id]['dm_channel_id'] = channel_id
            settings['users'][user_id]['user_name'] = user_name
            settings['users'][user_id]['last_dm'] = datetime.now().isoformat()

            # GCS에 저장
            config.save_settings(settings)
            print(f"💾 DM 채널 정보 GCS에 저장: {user_name} ({channel_id})", flush=True)

        except Exception as e:
            print(f"❌ DM 채널 정보 저장 실패: {e}", flush=True)

        return

    # 채팅 로그 저장 기능 제거됨 (GCS Rate Limit 방지)

# --- Helper Functions ---

def track_user(interaction: discord.Interaction, command_name=None):
    """모든 interaction에서 자동으로 사용자 이름을 추적하고 채팅 로그를 저장합니다."""
    try:
        user = interaction.user
        user_name = user.display_name or user.global_name or user.name
        config.log_user_interaction(user.id, user_name)
        
        # 채팅 로그 저장 (명령어 사용)
        if hasattr(interaction, 'guild') and interaction.guild:
            guild = interaction.guild
            channel = interaction.channel
            message_content = f"/{command_name}" if command_name else "명령어 사용"
            
            config.save_chat_log(
                user_id=user.id,
                user_name=user_name,
                guild_id=guild.id,
                guild_name=guild.name,
                channel_id=channel.id,
                channel_name=channel.name,
                message=message_content,
                command_type=command_name
            )
        
        return user_name
    except Exception as e:
        print(f"사용자 추적 오류: {e}")
        return None

# --- Commands ---

@bot.tree.command(name="전적", description="이터널 리턴 플레이어 전적을 검색해요!")
async def stats_command(interaction: discord.Interaction, 닉네임: str):
    # 자동 사용자 추적
    track_user(interaction, "전적")
    
    # 채널 제한 체크를 먼저 하고 즉시 응답
    if interaction.guild:
        guild_settings = config.get_guild_settings(interaction.guild.id)
        chat_channel_id = guild_settings.get("CHAT_CHANNEL_ID")
        if chat_channel_id and interaction.channel.id != chat_channel_id:
            allowed_channel = bot.get_channel(chat_channel_id)
            await interaction.response.send_message(f"이 명령어는 {allowed_channel.mention} 채널에서만 사용할 수 있어요!", ephemeral=True)
            return
    
    # 즉시 응답
    await interaction.response.send_message(f"🔍 {닉네임}님의 전적을 찾고 있어요...", ephemeral=True)
    
    try:
        # 백그라운드에서 데이터 가져오기
        player_data, played_seasons = await asyncio.gather(
            get_player_basic_data(닉네임.strip()),
            get_player_played_seasons(닉네임.strip()),
            return_exceptions=True
        )
        
        # 예외 처리
        if isinstance(player_data, Exception):
            raise player_data
        if isinstance(played_seasons, Exception):
            played_seasons = []
        
        if not player_data:
            await interaction.followup.send(embed=create_character_embed(
                characters["debi"], 
                "전적 검색 실패", 
                f"**{닉네임}**님의 전적을 찾을 수 없어!", 
                f"/전적 {닉네임}"
            ))
            return
        
        view = StatsView(player_data, played_seasons)
        embed = create_stats_embed(player_data, False)  # 기본은 랭크게임 모드
        await interaction.followup.send(
            content=f"{닉네임}님의 전적 찾았어!", 
            embed=embed, 
            view=view
        )
    
    except Exception as e:
        print(f"--- 전적 명령어 오류: {e} ---")
        import traceback
        traceback.print_exc()
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    embed=create_character_embed(
                        characters["debi"], 
                        "검색 오류", 
                        f"**{닉네임}**님 검색 중 오류가 발생했어!", 
                        f"/전적 {닉네임}"
                    )
                )
            else:
                await interaction.followup.send(
                    embed=create_character_embed(
                        characters["debi"], 
                        "검색 오류", 
                        f"**{닉네임}**님 검색 중 오류가 발생했어!", 
                        f"/전적 {닉네임}"
                    )
                )
        except:
            pass

@bot.tree.command(name="통계", description="이터널 리턴 캐릭터별 통계를 보여줍니다")
@app_commands.describe(
    티어="통계를 볼 티어 (기본: diamond_plus)",
    기간="통계 기간 (기본: 7일)"
)
@app_commands.choices(티어=[
    app_commands.Choice(name="다이아+", value="diamond_plus"),
    app_commands.Choice(name="전체", value="all"),
    app_commands.Choice(name="언랭크", value="unranked"),
    app_commands.Choice(name="아이언", value="iron"),
    app_commands.Choice(name="브론즈", value="bronze"),
    app_commands.Choice(name="실버", value="silver"),
    app_commands.Choice(name="골드", value="gold"),
    app_commands.Choice(name="플래티넘", value="platinum"),
    app_commands.Choice(name="다이아몬드", value="diamond")
])
@app_commands.choices(기간=[
    app_commands.Choice(name="3일", value=3),
    app_commands.Choice(name="7일", value=7)
])
async def character_stats(interaction: discord.Interaction, 티어: str = "diamond_plus", 기간: int = 7):
    # 자동 사용자 추적
    track_user(interaction)
    
    await interaction.response.defer()
    
    try:
        import sys
        print(f"캐릭터 통계 요청: dt={기간}, tier={티어}", flush=True)
        sys.stdout.flush()
        stats_data = await get_character_stats(dt=기간, team_mode="SQUAD", tier=티어)
        print(f"캐릭터 통계 응답: {stats_data is not None}", flush=True)
        sys.stdout.flush()
        if not stats_data:
            await interaction.edit_original_response(content="❌ 캐릭터 통계 데이터를 가져올 수 없습니다.")
            return
        
        # CharacterStatsView를 사용하여 페이지네이션과 함께 표시
        view = CharacterStatsView(stats_data, 티어, 기간)
        embed = view.create_embed()
        await interaction.edit_original_response(embed=embed, view=view)
        
    except Exception as e:
        print(f"캐릭터 통계 명령어 오류: {e}")
        import traceback
        traceback.print_exc()
        await interaction.edit_original_response(content=f"❌ 캐릭터 통계를 처리하는 중 오류가 발생했습니다: {str(e)}")


@bot.tree.command(name="설정", description="[관리자] 서버의 유튜브 알림 채널을 설정합니다.")
@app_commands.default_permissions(administrator=True)
async def settings(interaction: discord.Interaction):
    try:
        # 자동 사용자 추적
        track_user(interaction)
        
        # 서버에서만 사용 가능
        if not interaction.guild:
            await interaction.response.send_message("이 명령어는 서버에서만 사용할 수 있어요!", ephemeral=True)
            return
        
        # 관리자 권한 체크
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("이 명령어는 서버 관리자만 사용할 수 있어요!", ephemeral=True)
            return
        
        # SettingsView를 사용해서 선택 UI 표시
        embed = discord.Embed(title="⚙️ 서버 설정", description="아래 버튼으로 유튜브 공지 채널과 명령어 전용 채널을 설정하세요.", color=0x7289DA)
        embed.add_field(name="📢 공지 채널", value="유튜브 새 영상 알림이 올라갈 채널입니다. (필수)", inline=False)
        embed.add_field(name="💬 채팅 채널", value="`/전적` 등 봇의 명령어를 사용할 특정 채널입니다. 설정하지 않으면 모든 채널에서 사용 가능합니다. (선택)", inline=False)
        view = SettingsView(interaction.guild)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    except Exception as e:
        print(f"❌ 설정 명령어 오류: {e}", flush=True)
        try:
            if interaction.response.is_done():
                await interaction.followup.send("설정 중 오류가 발생했습니다.", ephemeral=True)
            else:
                await interaction.response.send_message("설정 중 오류가 발생했습니다.", ephemeral=True)
        except:
            pass

@bot.tree.command(name="유튜브알림", description="[개인] 유튜브 새 영상 알림을 DM으로 받거나 해제합니다.")
async def subscribe_youtube(interaction: discord.Interaction, 받기: bool):
    # 자동 사용자 추적
    user_name = track_user(interaction)
    
    try:
        config.set_youtube_subscription(interaction.user.id, 받기, user_name)
        message = "✅ 이제부터 새로운 영상이 올라오면 DM으로 알려드릴게요!" if 받기 else "✅ 유튜브 DM 알림을 해제했습니다."
        await interaction.response.send_message(message, ephemeral=True)
    except Exception as e:
        print(f"❌ 유튜브알림 명령어 오류: {e}", flush=True)
        try:
            if interaction.response.is_done():
                await interaction.followup.send(f"오류가 발생했어요: {e}", ephemeral=True)
            else:
                await interaction.response.send_message(f"오류가 발생했어요: {e}", ephemeral=True)
        except Exception as followup_error:
            print(f"❌ 유튜브알림 오류 메시지 전송 실패: {followup_error}", flush=True)

@bot.tree.command(name="피드백", description="봇 개발자에게 피드백을 보냅니다.")
async def feedback(interaction: discord.Interaction, 내용: str):
    # 자동 사용자 추적
    track_user(interaction)
    
    if not OWNER_ID:
        return await interaction.response.send_message("죄송해요, 피드백 기능이 아직 설정되지 않았어요.", ephemeral=True)
    try:
        owner = await bot.fetch_user(int(OWNER_ID))
        embed = discord.Embed(title="📬 새로운 피드백 도착!", description=내용, color=0xFFB6C1)
        embed.set_author(name=f"{interaction.user.name} ({interaction.user.id})", icon_url=interaction.user.display_avatar.url)
        if interaction.guild:
            embed.add_field(name="서버", value=f"{interaction.guild.name} ({interaction.guild.id})", inline=False)
        else:
            embed.add_field(name="서버", value="개인 메시지(DM)", inline=False)
        await owner.send(embed=embed)
        await interaction.response.send_message("소중한 피드백 고마워요! 개발자에게 잘 전달했어요. ❤️", ephemeral=True)
    except (ValueError, discord.NotFound):
        await interaction.response.send_message("죄송해요, 개발자 정보를 찾을 수 없어서 피드백을 보낼 수 없어요.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("개발자에게 DM을 보낼 수 없도록 설정되어 있어 전달에 실패했어요. 😥", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"피드백 전송 중 오류가 발생했어요: {e}", ephemeral=True)

@bot.tree.command(name="유튜브테스트", description="[관리자] 유튜브 새 영상 확인을 수동으로 테스트합니다.")
@app_commands.default_permissions(administrator=True)
async def youtube_test(interaction: discord.Interaction):
    # 자동 사용자 추적
    track_user(interaction)
    
    # 개발자는 어디서든 사용 가능
    is_owner = OWNER_ID and interaction.user.id == int(OWNER_ID)
    
    if interaction.guild:
        # 서버에서는 관리자 권한 필요
        if not is_owner and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("이 명령어는 서버 관리자만 사용할 수 있어요!", ephemeral=True)
            return
            
        # 채팅 채널 제한 체크 (개발자는 예외)
        if not is_owner:
            guild_settings = config.get_guild_settings(interaction.guild.id)
            chat_channel_id = guild_settings.get("CHAT_CHANNEL_ID")
            if chat_channel_id and interaction.channel.id != chat_channel_id:
                allowed_channel = bot.get_channel(chat_channel_id)
                await interaction.response.send_message(f"이 명령어는 {allowed_channel.mention} 채널에서만 사용할 수 있어요!", ephemeral=True)
                return
    # DM에서는 누구나 사용 가능 (개인 테스트용)
    
    await interaction.response.defer(ephemeral=True)
    try:
        from run import youtube_service
        
        # 개인 DM에서 사용 시 해당 사용자에게만 테스트
        if not interaction.guild:
            result = await youtube_service.manual_check_for_user(interaction.user)
            await interaction.followup.send(f"✅ 개인 유튜브 테스트 완료!\n```{result}```", ephemeral=True)
        else:
            # 서버에서 사용 시 해당 서버에만 테스트
            result = await youtube_service.manual_check_for_guild(interaction.guild)
            await interaction.followup.send(f"✅ 서버 유튜브 테스트 완료!\n```{result}```", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ 유튜브 테스트 중 오류 발생: {e}", ephemeral=True)


@bot.tree.command(name="목록", description="[관리자 전용] 봇이 추가된 서버 목록을 확인합니다")
async def server_list(interaction: discord.Interaction):
    """봇 소유자 전용 서버 목록 확인 명령어"""
    # 자동 사용자 추적
    track_user(interaction)
    
    # 봇 소유자만 사용 가능
    if interaction.user.id != int(OWNER_ID):
        await interaction.response.send_message("❌ 이 명령어는 봇 소유자만 사용할 수 있습니다.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    total_members = 0
    server_list = []
    
    for guild in bot.guilds:
        # 공지 채널 설정 확인
        guild_settings = config.get_guild_settings(guild.id)
        announcement_channel_id = guild_settings.get('ANNOUNCEMENT_CHANNEL_ID')
        has_announcement = "✅" if announcement_channel_id else "❌"
        
        # 서버 정보 수집
        server_info = f"**{guild.name}** (ID: {guild.id})\n"
        server_info += f"  👥 멤버: {guild.member_count}명\n"
        server_info += f"  📢 공지채널: {has_announcement}"
        if announcement_channel_id:
            channel = guild.get_channel(announcement_channel_id)
            channel_name = f"#{channel.name}" if channel else "알 수 없음"
            server_info += f" {channel_name} (ID: {announcement_channel_id})"
        server_info += "\n"
        server_info += f"  🗓️ 가입일: {guild.me.joined_at.strftime('%Y-%m-%d')}\n"
        
        server_list.append(server_info)
        total_members += guild.member_count
    
    # 개인 구독자 정보 추가
    subscribers = config.get_youtube_subscribers()
    subscriber_list = []
    
    for user_id in subscribers:
        try:
            user = await bot.fetch_user(user_id)
            subscriber_list.append(f"• {user.name}#{user.discriminator} (ID: {user_id})")
        except:
            subscriber_list.append(f"• 알 수 없는 사용자 (ID: {user_id})")
    
    subscriber_info = "\n".join(subscriber_list) if subscriber_list else "구독자가 없습니다."
    
    # 설정 파일과의 차이 계산
    settings = config.load_settings()
    settings_guild_count = len(settings.get('guilds', {}))
    actual_guild_count = len(bot.guilds)
    
    description = f"총 **{actual_guild_count}개** 서버에서 **{total_members}명**의 사용자와 함께하고 있습니다!\n"
    description += f"개인 구독자: **{len(subscribers)}명**\n\n"
    
    # 설정 파일과 차이가 있으면 경고 표시
    if settings_guild_count != actual_guild_count:
        description += f"⚠️ **설정 파일 불일치**: 설정 파일에는 {settings_guild_count}개 서버만 저장됨\n"
        description += f"📊 **실제 연결**: {actual_guild_count}개 서버에 연결됨"
    
    # 결과 임베드 생성
    embed = discord.Embed(
        title="📊 데비&마를렌 봇 서버 현황",
        description=description,
        color=0xffa500 if settings_guild_count != actual_guild_count else 0x00ff00
    )
    
    # 서버 목록을 여러 필드로 나눠서 추가
    server_text = "\n".join(server_list)
    if server_text:
        # Discord 필드 최대 길이(1024자) 제한으로 나눠서 표시
        if len(server_text) <= 1024:
            embed.add_field(name="🏢 서버 목록", value=server_text, inline=False)
        else:
            # 서버가 너무 많으면 여러 필드로 분할
            for i in range(0, len(server_list), 5):
                chunk = server_list[i:i+5]
                chunk_text = "\n".join(chunk)
                field_name = f"🏢 서버 목록 ({i+1}-{min(i+5, len(server_list))})"
                embed.add_field(name=field_name, value=chunk_text[:1024], inline=False)
    
    # 개인 구독자 목록 추가
    embed.add_field(name="👤 개인 구독자", value=subscriber_info[:1024], inline=False)
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="공지", description="[관리자 전용] 모든 서버에 공지사항을 전송합니다")
@app_commands.default_permissions()
async def announce(interaction: discord.Interaction, 메시지: str):
    """봇 소유자 전용 전체 서버 공지 명령어"""
    # 자동 사용자 추적
    track_user(interaction)
    
    # 봇 소유자만 사용 가능
    if interaction.user.id != int(OWNER_ID):
        await interaction.response.send_message("❌ 이 명령어는 봇 소유자만 사용할 수 있습니다.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    success_count = 0
    fail_count = 0
    sent_guilds = []
    
    # 모든 서버에 공지 전송
    for guild in bot.guilds:
        try:
            # 먼저 config에 저장된 공지 채널 확인
            guild_settings = config.get_guild_settings(guild.id)
            target_channel = None
            
            if guild_settings and guild_settings.get('ANNOUNCEMENT_CHANNEL_ID'):
                target_channel = guild.get_channel(guild_settings['ANNOUNCEMENT_CHANNEL_ID'])
            
            # 설정된 공지 채널이 없거나 권한이 없으면 시스템 채널 시도
            if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
                target_channel = guild.system_channel
            
            # 시스템 채널도 없거나 권한이 없으면 다른 채널 찾기
            if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
                # 일반 채널에서 메시지 전송 권한이 있는 첫 번째 채널 찾기
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        target_channel = channel
                        break
            
            if target_channel:
                # 공지 임베드 생성
                embed = discord.Embed(
                    title="📢 공지사항",
                    description=메시지,
                    color=0x00ff00
                )
                embed.set_footer(text="데비&마를렌 봇 | 문의: Discord에서 개발자에게 연락")
                
                await target_channel.send(embed=embed)
                success_count += 1
                sent_guilds.append(f"✅ {guild.name}")
            else:
                fail_count += 1
                sent_guilds.append(f"❌ {guild.name} (권한 없음)")
                
        except Exception as e:
            fail_count += 1
            sent_guilds.append(f"❌ {guild.name} (오류: {str(e)[:30]})")
    
    # 결과 전송
    result_message = f"🎯 **공지 전송 완료**\n"
    result_message += f"📊 **결과**: 성공 {success_count}개, 실패 {fail_count}개\n\n"
    result_message += f"**전송된 메시지**: {메시지}\n\n"
    result_message += "**서버별 결과**:\n" + "\n".join(sent_guilds)
    
    # 메시지가 너무 길면 분할해서 전송
    if len(result_message) > 2000:
        # 기본 정보만 먼저 전송
        basic_info = f"🎯 **공지 전송 완료**\n📊 **결과**: 성공 {success_count}개, 실패 {fail_count}개\n**전송된 메시지**: {메시지}"
        await interaction.followup.send(basic_info, ephemeral=True)
        
        # 서버 목록은 별도로 전송
        server_list = "**서버별 결과**:\n" + "\n".join(sent_guilds)
        # 2000자 단위로 분할
        while server_list:
            chunk = server_list[:2000]
            server_list = server_list[2000:]
            await interaction.followup.send(chunk, ephemeral=True)
    else:
        await interaction.followup.send(result_message, ephemeral=True)

@bot.tree.command(name="sync", description="[개발자 전용] 명령어를 강제로 동기화합니다")
async def force_sync(interaction: discord.Interaction):
    """개발자 전용 명령어 강제 동기화"""
    if interaction.user.id != int(OWNER_ID):
        await interaction.response.send_message("❌ 이 명령어는 개발자만 사용할 수 있습니다.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    try:
        print("🔧 수동 명령어 동기화 시작...")
        synced = await bot.tree.sync()
        print(f"✅ 수동 명령어 동기화 완료: {len(synced)}개 명령어")
        await interaction.followup.send(f"✅ 명령어 동기화 완료! {len(synced)}개 명령어가 등록되었습니다.", ephemeral=True)
    except Exception as e:
        print(f"❌ 수동 명령어 동기화 실패: {e}")
        await interaction.followup.send(f"❌ 명령어 동기화 실패: {e}", ephemeral=True)

# Flask 내부 API 서버 - 웹패널에서 봇 관리
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

@app.route('/bot/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({"status": "healthy", "bot_ready": bot.is_ready()})
@app.route('/bot/stats', methods=['GET'])
def get_bot_stats():
    """봇 통계 정보 반환"""
    if not bot.is_ready():
        return jsonify({"error": "Bot not ready"}), 503
    
    try:
        total_servers = len(bot.guilds)
        total_members = sum(guild.member_count for guild in bot.guilds if guild.member_count)
        
        # 서버 정보 수집
        servers_data = []
        for guild in bot.guilds:
            guild_settings = config.get_guild_settings(guild.id)
            announcement_channel = None
            chat_channel = None
            
            if guild_settings.get('ANNOUNCEMENT_CHANNEL_ID'):
                announcement_channel = guild.get_channel(guild_settings['ANNOUNCEMENT_CHANNEL_ID'])
            if guild_settings.get('CHAT_CHANNEL_ID'):
                chat_channel = guild.get_channel(guild_settings['CHAT_CHANNEL_ID'])
            
            servers_data.append({
                "id": guild.id,
                "name": guild.name,
                "member_count": guild.member_count,
                "joined_at": guild.me.joined_at.isoformat() if guild.me.joined_at else None,
                "announcement_channel": {
                    "id": announcement_channel.id if announcement_channel else None,
                    "name": announcement_channel.name if announcement_channel else None
                },
                "chat_channel": {
                    "id": chat_channel.id if chat_channel else None,
                    "name": chat_channel.name if chat_channel else None
                },
                "channels": [{"id": c.id, "name": c.name, "type": str(c.type)} 
                            for c in guild.channels if hasattr(c, 'type')]
            })
        
        subscribers = config.get_youtube_subscribers()
        all_users = config.get_all_users()
        
        # 사용자 정보에 실제 Discord 이름 추가
        enriched_subscribers = []
        for uid in subscribers:
            try:
                user = bot.get_user(uid)
                if user:
                    user_name = user.display_name or user.global_name or user.name
                else:
                    # 캐시에 없으면 API로 가져오기 시도
                    try:
                        import asyncio
                        if bot.loop and not bot.loop.is_closed():
                            future = asyncio.run_coroutine_threadsafe(bot.fetch_user(uid), bot.loop)
                            user = future.result(timeout=2)
                            user_name = user.display_name or user.global_name or user.name
                        else:
                            user_name = f"User_{str(uid)[-4:]}"
                    except:
                        user_name = f"User_{str(uid)[-4:]}"
            except:
                user_name = f"User_{str(uid)[-4:]}"
            
            enriched_subscribers.append({
                "id": str(uid),
                "name": user_name,
                "youtube_subscribed": True,
                "last_seen": "최근",
                "server_admin": False
            })
        
        # 일반 사용자도 이름 추가
        enriched_general_users = []
        for u in all_users:
            if not u["youtube_subscribed"]:
                try:
                    user = bot.get_user(u["id"])
                    if user:
                        user_name = user.display_name or user.global_name or user.name
                    else:
                        user_name = f"User_{str(u['id'])[-4:]}"
                except:
                    user_name = f"User_{str(u['id'])[-4:]}"
                
                enriched_general_users.append({
                    "id": str(u["id"]),
                    "name": user_name,
                    "youtube_subscribed": u["youtube_subscribed"],
                    "last_seen": u["last_seen"] or "알 수 없음",
                    "server_admin": u["server_admin"]
                })
        
        return jsonify({
            "status": "online",
            "total_servers": total_servers,
            "total_members": total_members,
            "subscribers_count": len(subscribers),
            "total_users": len(all_users),
            "servers": servers_data,
            "subscribers": enriched_subscribers,
            "general_users": enriched_general_users
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/bot/announce', methods=['POST'])
def send_announcement():
    """공지사항 전송"""
    if not bot.is_ready():
        return jsonify({"error": "Bot not ready"}), 503
    
    data = request.get_json()
    message = data.get('message', '')
    send_to_channels = data.get('send_to_channels', False)
    send_to_subscribers = data.get('send_to_subscribers', False)
    
    if not message:
        return jsonify({"error": "메시지가 비어있습니다"}), 400
    
    try:
        async def send_announcements():
            sent_count = 0
            errors = []
            
            # 서버 채널로 전송
            if send_to_channels:
                for guild in bot.guilds:
                    guild_settings = config.get_guild_settings(guild.id)
                    announcement_channel_id = guild_settings.get('ANNOUNCEMENT_CHANNEL_ID')
                    
                    if announcement_channel_id:
                        channel = guild.get_channel(announcement_channel_id)
                        if channel:
                            try:
                                await channel.send(message)
                                sent_count += 1
                            except Exception as e:
                                errors.append(f"{guild.name}: {str(e)}")
            
            # 개인 구독자에게 DM 전송
            if send_to_subscribers:
                subscribers = config.get_youtube_subscribers()
                for user_id in subscribers:
                    try:
                        user = await bot.fetch_user(user_id)
                        await user.send(message)
                        sent_count += 1
                    except Exception as e:
                        errors.append(f"User {user_id}: {str(e)}")
            
            return sent_count, errors
        
        # 비동기 함수 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        sent_count, errors = loop.run_until_complete(send_announcements())
        loop.close()
        
        return jsonify({
            "success": True,
            "sent_count": sent_count,
            "errors": errors
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/bot/create-dm', methods=['POST'])
def create_dm_channel():
    """웹패널에서 DM 채널 생성 요청"""
    if not bot.is_ready():
        return jsonify({"error": "Bot not ready"}), 503

    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id가 필요합니다"}), 400

    try:
        async def create_dm():
            """비동기로 DM 채널 생성"""
            try:
                # Discord에서 유저 가져오기
                user = await bot.fetch_user(int(user_id))

                # DM 채널 생성 (빈 메시지 대신 환영 메시지)
                dm_channel = await user.create_dm()

                # GCS에 DM 채널 정보 저장
                config.save_dm_channel(user_id, dm_channel.id, user.name)

                print(f"✅ DM 채널 생성 성공: {user.name} (#{user_id})")

                return {
                    "success": True,
                    "channel": {
                        "id": str(dm_channel.id),
                        "type": 1,
                        "recipient": {
                            "id": str(user.id),
                            "username": user.name,
                            "discriminator": user.discriminator,
                            "avatar": f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png" if user.avatar else None
                        }
                    }
                }
            except discord.NotFound:
                return {"error": "사용자를 찾을 수 없습니다"}
            except discord.Forbidden:
                return {"error": "이 사용자는 DM을 차단했습니다"}
            except Exception as e:
                return {"error": f"DM 채널 생성 실패: {str(e)}"}

        # 비동기 함수 실행
        if bot.loop and not bot.loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(create_dm(), bot.loop)
            result = future.result(timeout=10)

            if "error" in result:
                return jsonify(result), 400
            else:
                return jsonify(result)
        else:
            return jsonify({"error": "Bot loop not available"}), 503

    except Exception as e:
        print(f"❌ DM 채널 생성 오류: {e}")
        return jsonify({"error": str(e)}), 500

def run_internal_api():
    """내부 API 서버 실행"""
    try:
        print("🔗 Flask 내부 API 서버 시작을 시도합니다...")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Flask 내부 API 서버 시작 실패: {e}")

def run_bot():
    if not DISCORD_TOKEN:
        print("CRITICAL: DISCORD_TOKEN이 설정되지 않았습니다.")
        return
    
    # Flask 내부 API 서버를 별도 스레드에서 실행
    api_thread = threading.Thread(target=run_internal_api, daemon=True)
    api_thread.start()
    print("📡 내부 API 서버 스레드가 시작되었습니다 (포트 5000)")
    
    # Discord 봇 실행
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    run_bot()
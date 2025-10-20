import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import io
import base64
import matplotlib.font_manager as fm

def create_mmr_graph(mmr_history, nickname="플레이어"):
    """
    MMR 히스토리 데이터를 기반으로 디스코드 테마에 맞는 그래프 생성
    
    Args:
        mmr_history: [[20250731, 5496, 5245, 5496], ...] 형태의 데이터
        nickname: 플레이어 닉네임
    
    Returns:
        base64 인코딩된 이미지 데이터
    """
    if not mmr_history or len(mmr_history) < 2:
        return None
    
    # 데이터 파싱
    parsed_data = []
    
    for entry in mmr_history:
        if len(entry) >= 4:
            # 날짜 파싱 (YYYYMMDD 형태)
            date_str = str(entry[0])
            if len(date_str) == 8:
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                date_obj = datetime(year, month, day)
                mmr_value = entry[3]  # 마지막 MMR 값 사용
                parsed_data.append((date_obj, mmr_value))
    
    if len(parsed_data) < 2:
        return None
    
    # 날짜순으로 정렬 (오래된 것부터)
    parsed_data.sort(key=lambda x: x[0])
    
    # 정렬된 데이터 분리
    dates = [item[0] for item in parsed_data]
    mmr_values = [item[1] for item in parsed_data]
    
    # 한글 폰트 설정
    try:
        # macOS 기본 한글 폰트들 시도
        korean_fonts = ['AppleGothic', 'Apple SD Gothic Neo', 'Noto Sans CJK KR', 'NanumGothic', 'Malgun Gothic']
        font_found = False
        for font_name in korean_fonts:
            try:
                plt.rcParams['font.family'] = font_name
                font_found = True
                break
            except:
                continue
        
        if not font_found:
            # 시스템에서 사용 가능한 한글 폰트 찾기
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            korean_font = next((f for f in available_fonts if 'Gothic' in f or 'Nanum' in f), None)
            if korean_font:
                plt.rcParams['font.family'] = korean_font
    except:
        pass  # 폰트 설정 실패해도 계속 진행
    
    # 음수 기호가 깨지는 문제 해결
    plt.rcParams['axes.unicode_minus'] = False
    
    # 디스코드 다크 테마 색상 설정
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#2f3136')  # 디스코드 배경색
    ax.set_facecolor('#36393f')  # 더 어두운 배경
    
    # MMR 라인 그래프
    ax.plot(dates, mmr_values, 
            color='#5865f2',  # 디스코드 블루퍼플 색상
            linewidth=3,
            marker='o',
            markersize=6,
            markerfacecolor='#5865f2',
            markeredgecolor='white',
            markeredgewidth=1)
    
    # 제목 제거
    
    ax.set_xlabel('날짜', fontsize=12, color='#b9bbbe')
    ax.set_ylabel('MMR', fontsize=12, color='#b9bbbe')
    
    # 격자 설정
    ax.grid(True, alpha=0.3, color='#4f545c')
    
    # 축 색상 설정
    ax.tick_params(colors='#b9bbbe')
    ax.spines['bottom'].set_color('#4f545c')
    ax.spines['top'].set_color('#4f545c')
    ax.spines['right'].set_color('#4f545c')
    ax.spines['left'].set_color('#4f545c')
    
    # 날짜 포맷팅 - 데이터 포인트가 있는 날짜만 표시
    ax.set_xticks(dates)  # 실제 데이터 포인트 날짜들만 설정
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    
    # 날짜가 너무 많으면 일부만 표시
    if len(dates) > 10:
        # 첫째, 마지막, 그리고 중간에 몇 개만 표시
        show_indices = [0]  # 첫째
        step = max(1, len(dates) // 8)  # 대략 8개 정도만 표시
        for i in range(step, len(dates) - 1, step):
            show_indices.append(i)
        show_indices.append(len(dates) - 1)  # 마지막
        
        show_dates = [dates[i] for i in show_indices]
        ax.set_xticks(show_dates)
    
    plt.xticks(rotation=45)
    
    # Y축 범위 설정 (점수 변동에 따라 유연하게)
    mmr_min, mmr_max = min(mmr_values), max(mmr_values)
    mmr_range = mmr_max - mmr_min
    
    # 변동폭에 따라 마진을 동적으로 설정
    if mmr_range < 200:
        y_margin = 50
    elif mmr_range < 500:
        y_margin = 100
    else:
        y_margin = 150

    ax.set_ylim(mmr_min - y_margin, mmr_max + y_margin)
    
    # 첫번째 점에 MMR 점수 표시 (마지막 점과 같은 색상)
    first_mmr = mmr_values[0]
    ax.annotate(f'{first_mmr}', 
                xy=(dates[0], first_mmr),
                xytext=(-8, 15), 
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#5865f2', alpha=0.9, edgecolor='white', linewidth=1),
                color='white',
                fontweight='bold',
                fontsize=11,
                ha='center')
    
    # 마지막 점에 MMR 점수 표시
    current_mmr = mmr_values[-1]
    ax.annotate(f'{current_mmr}', 
                xy=(dates[-1], current_mmr),
                xytext=(8, 15), 
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#5865f2', alpha=0.9, edgecolor='white', linewidth=1),
                color='white',
                fontweight='bold',
                fontsize=11,
                ha='center')
    
    # 총변화와 최고점수 표시 제거
    
    plt.tight_layout()
    
    # 이미지를 메모리에 저장
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                facecolor='#2f3136', edgecolor='none')
    buffer.seek(0)
    
    # base64 인코딩
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64

def save_mmr_graph_to_file(mmr_history, nickname="플레이어", filename="mmr_graph.png"):
    """
    MMR 그래프를 파일로 저장
    """
    image_base64 = create_mmr_graph(mmr_history, nickname)
    if image_base64:
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(image_base64))
        return filename
    return None
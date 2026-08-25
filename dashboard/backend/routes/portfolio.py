"""포트폴리오 floating 챗봇 proxy.

거노 NEXON 포트폴리오 사이트의 챗봇 위젯이 호출하는 단일 endpoint.
Anthropic Managed Agents (geno-portfolio) 로 prompt 를 forwarding 하고
응답 텍스트를 그대로 돌려준다.

설계:
    - 인증 없음 (공개 사이트). Rate limit (IP/min) 으로 abuse 방지
    - prompt 500자, response 800자 truncate
    - session_id 받으면 재사용, 없으면 새로 만들고 응답에 포함 → 클라이언트가 다음 호출에 동봉
    - 모든 요청/응답을 Firestore portfolio_logs 에 적재 (비용/품질 추적)

env:
    OPENGATEWAY_API_KEY          # 없으면 ~/.config/opengateway.key. 사이오닉 챗봇이 쓴다
    PORTFOLIO_DAILY_CAP          # 하루 총 답변 수 상한(기본 300)
    ANTHROPIC_API_KEY            # Managed Agent 창구 전용. 지금은 닫혀 있다
    PORTFOLIO_AGENT_ID           # geno-portfolio Managed Agent id (agent-builder 가 발급)
    PORTFOLIO_ENV_ID             # (선택) environment_id — agent 가 bash 도구 필요할 때만
    GCP_PROJECT_ID               # Firestore 로깅용. 미설정 시 ironic-objectivist-465713-a6
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone

from flask import Blueprint, Response, jsonify, request

from portfolio_data import search_portfolio, SIONIC_SYSTEM, sionic_fake_reply

logger = logging.getLogger(__name__)
portfolio_bp = Blueprint('portfolio', __name__)

# Managed Agent 창구 두 개(`/ask`, `/ask/stream`)는 닫아 둔다(2026-08-25).
#
# 인증 없는 자리인데 그 둘은 소유자 Anthropic 키로 나간다. Managed Agents 는 게이트웨이가
# 대신 해 줄 수 없는 Anthropic 전용 기능이라 아래 사이오닉 창구처럼 OpenGateway 로 옮길
# 수가 없어서, 옮기는 대신 닫는 쪽을 골랐다. 지금은 PORTFOLIO_AGENT_ID 가 없어 어차피
# 503 이지만, 나중에 그 값을 넣는 순간 조용히 다시 열리므로 명시적인 문을 하나 세워 둔다.
#
# 여는 조건: 요금이 나갈 자리이므로 제한이 진짜로 도는지부터 확인하고 PORTFOLIO_CHATBOT=1.
_PUBLIC_ASK_PATHS = ('/ask', '/ask/stream')


@portfolio_bp.before_request
def _gate_managed_agent_routes():
    if request.path.rstrip('/').endswith(_PUBLIC_ASK_PATHS) and os.getenv('PORTFOLIO_CHATBOT') != '1':
        return jsonify({'error': 'chatbot_disabled',
                        'message': '지금은 답변 창구를 닫아 두었습니다.'}), 503


# ─────────── 상수 ───────────

BETA_HEADER = "managed-agents-2026-04-01"
PROMPT_MAX_LEN = 500
RESPONSE_MAX_LEN = 800
RATE_LIMIT_PER_MIN = 5
RATE_LIMIT_WINDOW = 60
RESPONSE_TIMEOUT = 60   # 포폴 챗봇은 짧게 — 60초 안에 못 끝내면 fail

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'ironic-objectivist-465713-a6')
LOG_COLLECTION = 'portfolio_logs'

# ─────────── Rate limiter (파일) ───────────
# 프로세스 메모리에 두지 않는다. gunicorn 워커는 자주 새로 뜨는데(이 배포에서는 요청마다
# 죽는 문제까지 있었다) in-memory 버킷은 그때마다 통째로 비워져서, 겉으로는 「제한이 아예
# 안 걸린다」로 나타난다 — 2026-08-25 실측: 동시 14건이 전부 통과했고 요청마다 워커 pid 가
# 달랐다. 인증 없는 창구의 유일한 방어선이 워커 수명에 얹혀 있으면 안 된다.
#
# sqlite 를 쓰는 것은 표준 라이브러리만으로 **프로세스 사이**를 잠글 수 있어서다.
# 트래픽이 분당 몇 건이라 잠금 경합은 문제가 안 된다.

RATE_DB = os.getenv('PORTFOLIO_RATE_DB',
                    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 'portfolio_rate.sqlite'))
_rate_lock = threading.Lock()   # 같은 워커 안의 스레드끼리. 프로세스 사이는 sqlite 가 맡는다


def _rate_conn():
    conn = sqlite3.connect(RATE_DB, timeout=5)
    conn.execute('CREATE TABLE IF NOT EXISTS hits (ts REAL NOT NULL, ip TEXT NOT NULL)')
    conn.execute('CREATE INDEX IF NOT EXISTS hits_ts ON hits (ts)')
    return conn


def _check_rate(ip: str) -> bool:
    """True 면 통과. 1인당 분당 제한과 **전체 하루 총량**을 한 자리에서 본다.

    사람 단위 제한만으로는 「한 사람이 얼마나」밖에 못 막는다 — 인증이 없으니 봇이 여럿
    오면 1인당 제한을 전부 지키면서도 요금은 끝없이 는다. 게다가 이 창구는 회사 게이트웨이
    열쇠로 나가고 그 열쇠는 나쵸도 함께 쓰므로, 여기서 태워 막히면 그쪽까지 같이 죽는다.
    """
    now = time.time()
    try:
        with _rate_lock, _rate_conn() as conn:
            conn.execute('DELETE FROM hits WHERE ts < ?', (now - 86400,))
            per_ip = conn.execute(
                'SELECT COUNT(*) FROM hits WHERE ip = ? AND ts > ?',
                (ip, now - RATE_LIMIT_WINDOW)).fetchone()[0]
            if per_ip >= RATE_LIMIT_PER_MIN:
                return False
            today = conn.execute(
                'SELECT COUNT(*) FROM hits WHERE ts > ?', (now - 86400,)).fetchone()[0]
            if today >= DAILY_CAP:
                return False
            conn.execute('INSERT INTO hits (ts, ip) VALUES (?, ?)', (now, ip))
        return True
    except Exception:
        # 세는 곳이 고장 났으면 **막는다**. 열어 두면 고장이 곧 무제한이 된다.
        logger.exception('rate limit 확인 실패')
        return False


def _client_ip() -> str:
    """제한 버킷을 가를 값. **호출자가 못 정하는 것**이어야 한다.

    전에는 X-Forwarded-For 의 첫 홉을 썼는데 그건 호출자가 정하는 값이다 — Cloudflare 는
    클라이언트가 보낸 XFF 를 지우지 않고 뒤에 실제 IP 를 덧붙이므로, 헤더만 바꿔 가며
    보내면 버킷이 매번 새로 생겨 분당 제한이 사실상 없었다(2026-08-25 감사).

    CF-Connecting-IP 는 Cloudflare 가 자기 손으로 덮어쓰는 값이라 위조가 안 된다.
    그게 없는 경로(로컬 개발·터널 우회)에서는 XFF 의 **마지막** 홉을 쓴다 — 우리 프록시가
    맨 뒤에 붙인 값이라 앞쪽에 뭘 끼워 넣어도 안 밀린다.
    """
    cf = request.headers.get('CF-Connecting-IP', '').strip()
    if cf:
        return cf
    xff = request.headers.get('X-Forwarded-For', '')
    if xff:
        return xff.rsplit(',', 1)[-1].strip()
    return request.remote_addr or 'unknown'


# ─────────── 하루 총량 ───────────
# 1인당 분당 제한과 별개로 **전체 합산** 상한을 둔다. 인증이 없는 창구라 사람 단위 제한은
# 「한 사람이 얼마나」만 막고 「몇 사람이 오는가」는 못 막는다 — 봇 여럿이 오면 1인당 제한을
# 전부 지키면서도 요금은 끝없이 는다. 게다가 이 창구는 회사 게이트웨이 열쇠로 나가고
# 그 열쇠는 나쵸도 함께 쓰므로, 여기서 태워 막히면 그쪽까지 같이 죽는다.
DAILY_CAP = int(os.getenv('PORTFOLIO_DAILY_CAP', '300'))


# ─────────── OpenGateway ───────────
# 공개 챗봇은 사내 게이트웨이로 나간다(2026-08-25 지시). 개인 Anthropic 키를 쓰던 자리다.
# 열쇠 파일 경로가 나쵸(llm.py)와 같은 것은 우연이 아니라 같은 열쇠라서다 — 그래서 위
# DAILY_CAP 이 이 파일에서 제일 중요한 줄이다.
OG_URL = os.getenv('OPENGATEWAY_BASE_URL', 'https://apis.opengateway.ai/v1/chat/completions')
OG_MODEL = os.getenv('PORTFOLIO_OG_MODEL', 'z-ai/glm-5.2-ultrafast')
OG_KEY_PATH = os.path.expanduser('~/.config/opengateway.key')


def _og_key() -> str:
    v = os.getenv('OPENGATEWAY_API_KEY') or os.getenv('LLM_API_KEY')
    if v:
        return v.strip()
    try:
        with open(OG_KEY_PATH, encoding='utf-8') as fh:
            return fh.read().strip()
    except Exception:
        return ''


def _og_stream(prompt: str, system: str):
    """게이트웨이 스트리밍. 조각 텍스트를 하나씩 내놓는다.

    OpenAI 호환 SSE 라 Anthropic SDK 의 text_stream 과 모양이 다르다 — 호출부가 같은
    for 문을 쓰도록 여기서 델타만 뽑아 준다.
    """
    import requests
    key = _og_key()
    if not key:
        raise RuntimeError('opengateway key missing')
    # macOS 에서 fork 된 gunicorn 워커는 requests 가 **시스템 프록시 설정을 조회하는 순간**
    # 데드락한다(SystemConfiguration 이 fork 안전하지 않다). 응답도 예외도 없이 그냥 멈추고
    # 30초 뒤 arbiter 가 워커를 SIGKILL 한다 — 2026-08-25 에 이 증상으로 챗봇이 「세션만
    # 열고 답이 없는」 상태였다. 같은 코드를 셸에서 직접 돌리면 멀쩡해서 원인이 안 보인다.
    # trust_env 를 끄면 그 조회를 건너뛴다. 프록시를 쓰지 않는 환경이라 잃는 것이 없다.
    sess = requests.Session()
    sess.trust_env = False
    res = sess.post(
        OG_URL, timeout=RESPONSE_TIMEOUT, stream=True,
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
        json={'model': OG_MODEL, 'max_tokens': 600, 'stream': True,
              'messages': [{'role': 'system', 'content': system},
                           {'role': 'user', 'content': prompt}]},
    )
    res.raise_for_status()
    # decode_unicode 를 쓰지 않는다 — 게이트웨이가 Content-Type 에 charset 을 안 붙여서
    # requests 가 ISO-8859-1 로 디코드해 버리고, 한글이 글자마다 깨져 나간다(실측).
    for raw in res.iter_lines():
        if not raw:
            continue
        line = raw.decode('utf-8', 'replace')
        if not line.startswith('data:'):
            continue
        payload = line[5:].strip()
        if payload == '[DONE]':
            break
        try:
            obj = json.loads(payload)
        except Exception:
            continue
        for ch in obj.get('choices') or []:
            text = (ch.get('delta') or {}).get('content')
            if text:
                yield text


# ─────────── Anthropic client (lazy) ───────────

_anthropic_client = None
_anthropic_init_failed = False


def _get_anthropic():
    global _anthropic_client, _anthropic_init_failed
    if _anthropic_client is not None:
        return _anthropic_client
    if _anthropic_init_failed:
        return None
    try:
        import anthropic
        # debi-marlene-env Secret 의 변수명은 CLAUDE_API_KEY (값은 Anthropic API key)
        api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY')
        if not api_key:
            logger.error('ANTHROPIC_API_KEY/CLAUDE_API_KEY 환경변수 없음')
            _anthropic_init_failed = True
            return None
        _anthropic_client = anthropic.Anthropic(api_key=api_key)
        return _anthropic_client
    except ImportError:
        logger.error('anthropic SDK 미설치 — requirements.txt 확인')
        _anthropic_init_failed = True
        return None


# ─────────── Firestore (lazy) ───────────

_firestore_client = None


def _get_firestore():
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client if _firestore_client is not False else None
    try:
        from google.cloud import firestore
        _firestore_client = firestore.Client(project=GCP_PROJECT_ID)
    except Exception as e:
        logger.warning(f'Firestore 클라이언트 실패 (로그 비활성): {e}')
        _firestore_client = False
    return _firestore_client if _firestore_client is not False else None


def _log_to_firestore(payload: dict) -> None:
    """로그 적재. **반드시 스레드로 던진다 — 여기서 기다리면 워커가 죽는다.**

    fork 된 gunicorn 워커에서는 GCP 클라이언트의 첫 네트워크 호출이 데드락한다
    (_og_stream 의 trust_env 주석과 같은 macOS fork 문제). 하필 이 호출이 응답을 다
    내보낸 **뒤**라, 사용자 화면은 멀쩡한데 워커만 30초 뒤 SIGKILL 당한다.

    그래서 증상이 로그 적재처럼 안 보였다 — 요청마다 워커가 새로 뜨니 in-memory 인
    분당 제한 버킷이 매번 비워져서, 겉으로는 「rate limit 이 안 걸린다」로 나타났다
    (2026-08-25 실측: 동시 12건이 전부 통과, 요청마다 워커 pid 가 달랐다).
    """
    threading.Thread(target=_log_to_firestore_blocking, args=(payload,), daemon=True).start()


def _log_to_firestore_blocking(payload: dict) -> None:
    db = _get_firestore()
    if db is None:
        return
    try:
        db.collection(LOG_COLLECTION).add(payload)
    except Exception as e:
        logger.warning(f'portfolio_logs 적재 실패: {e}')


# ─────────── Managed Agents 호출 ───────────

# 구현 가능한 client-side custom tool 목록.
# agent-builder 가 agent 정의에 등록하는 tool name 과 정확히 일치해야 함.
TOOL_HANDLERS = {
    'search_portfolio': lambda inp: search_portfolio(
        query=inp.get('query', ''),
        section=inp.get('section'),
    ),
}


def _execute_tool(name: str, inp: dict) -> tuple[str, bool]:
    """tool 실행 → (content_text, is_error). 실패 시 is_error=True."""
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return f'unknown tool: {name}', True
    try:
        result = handler(inp or {})
        return json.dumps(result, ensure_ascii=False), False
    except Exception as e:
        logger.exception(f'tool {name} 실행 실패')
        return f'tool {name} 실행 실패: {e}', True


def _call_agent(prompt: str, session_id: str | None) -> tuple[str, str, list[dict]]:
    """agent 호출 → (text, session_id, tool_calls) 반환.

    session_id 없으면 새 세션 생성.
    `agent.custom_tool_use` 발생 시 client-side 에서 직접 실행 → `user.custom_tool_result` 로 회신.
    실패 시 RuntimeError 던짐.
    tool_calls: [{name, input, latency_ms, is_error}, ...] — 로깅용.
    """
    client = _get_anthropic()
    if client is None:
        raise RuntimeError('anthropic_unavailable')

    agent_id = os.getenv('PORTFOLIO_AGENT_ID')
    if not agent_id:
        raise RuntimeError('agent_id_unset')

    extra = {"anthropic-beta": BETA_HEADER}

    # 세션 확보 — Managed Agents 는 environment_id 필수
    if not session_id:
        env_id = os.getenv('PORTFOLIO_ENV_ID')
        if not env_id:
            raise RuntimeError('env_id_unset')
        s = client.beta.sessions.create(
            title=f"portfolio:{datetime.now(timezone.utc).isoformat(timespec='seconds')}",
            agent={"type": "agent", "id": agent_id},
            environment_id=env_id,
            extra_headers=extra,
        )
        session_id = s.id

    parts: list[str] = []
    tool_calls: list[dict] = []
    pending_tools: list = []   # 한 idle 사이클에 누적된 tool_use 이벤트
    deadline = time.time() + RESPONSE_TIMEOUT

    with client.beta.sessions.events.stream(session_id=session_id, extra_headers=extra) as stream:
        # 첫 user message 송신
        client.beta.sessions.events.send(
            session_id=session_id,
            events=[{
                "type": "user.message",
                "content": [{"type": "text", "text": prompt}],
            }],
            extra_headers=extra,
        )

        for event in stream:
            if time.time() > deadline:
                raise RuntimeError('agent_timeout')
            ev_type = getattr(event, 'type', None)

            if ev_type == 'agent.message':
                for block in getattr(event, 'content', []) or []:
                    if getattr(block, 'type', None) == 'text':
                        parts.append(block.text)

            elif ev_type == 'agent.custom_tool_use':
                # 도구 실행은 status_idle(requires_action) 받은 뒤 일괄 처리
                pending_tools.append(event)

            elif ev_type == 'session.status_idle':
                stop = getattr(event, 'stop_reason', None)
                stop_type = getattr(stop, 'type', None) if stop else None

                if stop_type == 'end_turn':
                    break

                if stop_type == 'requires_action':
                    if not pending_tools:
                        # event_ids 는 있지만 우리가 모은 tool_use 이벤트가 없는 경우 — 방어
                        logger.warning('[portfolio] requires_action 인데 pending_tools 비어있음')
                        break
                    results_to_send = []
                    for tu in pending_tools:
                        t_name = getattr(tu, 'name', '')
                        t_input = getattr(tu, 'input', {}) or {}
                        t_id = getattr(tu, 'id', '')
                        t0 = time.time()
                        content_text, is_error = _execute_tool(t_name, t_input)
                        latency_ms = int((time.time() - t0) * 1000)
                        tool_calls.append({
                            'name': t_name,
                            'input': t_input,
                            'latency_ms': latency_ms,
                            'is_error': is_error,
                        })
                        results_to_send.append({
                            "type": "user.custom_tool_result",
                            "custom_tool_use_id": t_id,
                            "content": [{"type": "text", "text": content_text}],
                            "is_error": is_error,
                        })
                    pending_tools = []
                    client.beta.sessions.events.send(
                        session_id=session_id,
                        events=results_to_send,
                        extra_headers=extra,
                    )
                    # stream 유지 — 후속 agent.message / status_idle 들어옴
                    continue

                if stop_type == 'retries_exhausted':
                    raise RuntimeError('agent_retries_exhausted')

                # 알 수 없는 stop_reason — 안전하게 종료
                logger.warning(f'[portfolio] 알 수 없는 stop_reason: {stop_type}')
                break

    text = ''.join(parts).strip()
    if not text:
        raise RuntimeError('agent_empty_response')
    return text, session_id, tool_calls


# ─────────── 라우트 ───────────

@portfolio_bp.route('/ask', methods=['POST', 'OPTIONS'])
def ask():
    if request.method == 'OPTIONS':
        # CORS preflight 은 flask-cors 가 처리. 200 빈 body.
        return ('', 204)

    ip = _client_ip()

    if not _check_rate(ip):
        return jsonify({'error': 'rate_limited', 'reason': '분당 5회 초과. 잠시 후 다시.'}), 429

    body = request.get_json(silent=True) or {}
    prompt = (body.get('prompt') or '').strip()
    session_id = body.get('session_id') or None

    if not prompt:
        return jsonify({'error': 'invalid_request', 'reason': 'prompt 필수.'}), 400
    if len(prompt) > PROMPT_MAX_LEN:
        return jsonify({'error': 'prompt_too_long', 'reason': f'prompt {PROMPT_MAX_LEN}자 초과.'}), 400

    started_at = time.time()
    tool_calls: list[dict] = []
    try:
        text, session_id, tool_calls = _call_agent(prompt, session_id)
    except RuntimeError as e:
        reason = str(e)
        logger.warning(f'[portfolio] agent 호출 실패: {reason} (ip={ip})')
        if reason in ('anthropic_unavailable', 'agent_id_unset', 'env_id_unset'):
            return jsonify({'error': 'service_unavailable'}), 503
        if reason == 'agent_timeout':
            return jsonify({'error': 'timeout'}), 504
        return jsonify({'error': 'upstream_error'}), 502
    except Exception:
        logger.exception(f'[portfolio] 예외 (ip={ip})')
        return jsonify({'error': 'internal'}), 500

    # 길이 제한
    if len(text) > RESPONSE_MAX_LEN:
        text = text[:RESPONSE_MAX_LEN].rstrip() + '…'

    # 로깅 — 실패해도 응답엔 영향 없음
    elapsed = round(time.time() - started_at, 2)
    _log_to_firestore({
        'timestamp': datetime.now(timezone.utc),
        'ip': ip,
        'prompt': prompt,
        'text': text,
        'session_id': session_id,
        'agent_id': os.getenv('PORTFOLIO_AGENT_ID'),
        'elapsed_sec': elapsed,
        'tool_calls': tool_calls,
    })

    return jsonify({'text': text, 'session_id': session_id})


def _sse(data: dict) -> str:
    return f'data: {json.dumps(data, ensure_ascii=False)}\n\n'


def _stream_agent_sse(prompt: str, session_id: str | None, ip: str):
    """SSE generator. agent.message 도착 즉시 chunk 이벤트 flush."""
    started_at = time.time()
    parts: list[str] = []
    tool_calls: list[dict] = []
    final_session_id = session_id
    final_error: str | None = None

    try:
        client = _get_anthropic()
        if client is None:
            yield _sse({'type': 'error', 'code': 'service_unavailable'})
            final_error = 'anthropic_unavailable'
            return
        agent_id = os.getenv('PORTFOLIO_AGENT_ID')
        if not agent_id:
            yield _sse({'type': 'error', 'code': 'service_unavailable'})
            final_error = 'agent_id_unset'
            return

        extra = {"anthropic-beta": BETA_HEADER}

        if not final_session_id:
            env_id = os.getenv('PORTFOLIO_ENV_ID')
            if not env_id:
                yield _sse({'type': 'error', 'code': 'service_unavailable'})
                final_error = 'env_id_unset'
                return
            s = client.beta.sessions.create(
                title=f"portfolio:{datetime.now(timezone.utc).isoformat(timespec='seconds')}",
                agent={"type": "agent", "id": agent_id},
                environment_id=env_id,
                extra_headers=extra,
            )
            final_session_id = s.id

        yield _sse({'type': 'session', 'session_id': final_session_id})

        pending_tools: list = []
        deadline = time.time() + RESPONSE_TIMEOUT

        with client.beta.sessions.events.stream(session_id=final_session_id, extra_headers=extra) as stream:
            client.beta.sessions.events.send(
                session_id=final_session_id,
                events=[{
                    "type": "user.message",
                    "content": [{"type": "text", "text": prompt}],
                }],
                extra_headers=extra,
            )

            for event in stream:
                if time.time() > deadline:
                    yield _sse({'type': 'error', 'code': 'timeout'})
                    final_error = 'agent_timeout'
                    return
                ev_type = getattr(event, 'type', None)

                if ev_type == 'agent.message':
                    for block in getattr(event, 'content', []) or []:
                        if getattr(block, 'type', None) == 'text':
                            chunk = block.text
                            parts.append(chunk)
                            yield _sse({'type': 'chunk', 'text': chunk})

                elif ev_type == 'agent.custom_tool_use':
                    pending_tools.append(event)

                elif ev_type == 'session.status_idle':
                    stop = getattr(event, 'stop_reason', None)
                    stop_type = getattr(stop, 'type', None) if stop else None

                    if stop_type == 'end_turn':
                        break

                    if stop_type == 'requires_action':
                        if not pending_tools:
                            logger.warning('[portfolio/stream] requires_action 인데 pending_tools 비어있음')
                            break
                        results_to_send = []
                        for tu in pending_tools:
                            t_name = getattr(tu, 'name', '')
                            t_input = getattr(tu, 'input', {}) or {}
                            t_id = getattr(tu, 'id', '')
                            t0 = time.time()
                            content_text, is_error = _execute_tool(t_name, t_input)
                            latency_ms = int((time.time() - t0) * 1000)
                            tool_calls.append({
                                'name': t_name,
                                'input': t_input,
                                'latency_ms': latency_ms,
                                'is_error': is_error,
                            })
                            results_to_send.append({
                                "type": "user.custom_tool_result",
                                "custom_tool_use_id": t_id,
                                "content": [{"type": "text", "text": content_text}],
                                "is_error": is_error,
                            })
                        pending_tools = []
                        client.beta.sessions.events.send(
                            session_id=final_session_id,
                            events=results_to_send,
                            extra_headers=extra,
                        )
                        continue

                    if stop_type == 'retries_exhausted':
                        yield _sse({'type': 'error', 'code': 'upstream_error'})
                        final_error = 'agent_retries_exhausted'
                        return

                    logger.warning(f'[portfolio/stream] 알 수 없는 stop_reason: {stop_type}')
                    break

        text = ''.join(parts).strip()
        if not text:
            yield _sse({'type': 'error', 'code': 'upstream_error'})
            final_error = 'agent_empty_response'
            return

        if len(text) > RESPONSE_MAX_LEN:
            text = text[:RESPONSE_MAX_LEN].rstrip() + '…'

        yield _sse({'type': 'done', 'session_id': final_session_id, 'text': text})

    except Exception as e:
        logger.exception(f'[portfolio/stream] 예외 (ip={ip})')
        yield _sse({'type': 'error', 'code': 'internal'})
        final_error = f'exception:{type(e).__name__}'
    finally:
        text_final = ''.join(parts).strip()
        if len(text_final) > RESPONSE_MAX_LEN:
            text_final = text_final[:RESPONSE_MAX_LEN].rstrip() + '…'
        try:
            _log_to_firestore({
                'timestamp': datetime.now(timezone.utc),
                'ip': ip,
                'prompt': prompt,
                'text': text_final,
                'session_id': final_session_id,
                'agent_id': os.getenv('PORTFOLIO_AGENT_ID'),
                'elapsed_sec': round(time.time() - started_at, 2),
                'tool_calls': tool_calls,
                'streamed': True,
                'error': final_error,
            })
        except Exception:
            logger.exception('[portfolio/stream] 로그 적재 실패')


@portfolio_bp.route('/ask/stream', methods=['POST', 'OPTIONS'])
def ask_stream():
    if request.method == 'OPTIONS':
        return ('', 204)

    ip = _client_ip()
    if not _check_rate(ip):
        return jsonify({'error': 'rate_limited', 'reason': '분당 5회 초과. 잠시 후 다시.'}), 429

    body = request.get_json(silent=True) or {}
    prompt = (body.get('prompt') or '').strip()
    session_id = body.get('session_id') or None

    if not prompt:
        return jsonify({'error': 'invalid_request', 'reason': 'prompt 필수.'}), 400
    if len(prompt) > PROMPT_MAX_LEN:
        return jsonify({'error': 'prompt_too_long', 'reason': f'prompt {PROMPT_MAX_LEN}자 초과.'}), 400

    return Response(
        _stream_agent_sse(prompt, session_id, ip),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


# ─────────── 사이오닉 포폴 챗봇 (얼음정령) — Claude haiku 직접 스트리밍 ───────────
# 넥슨 Managed Agent 와 독립. 포폴 데이터를 system 에 통째로 넣고 haiku 가 답변.

@portfolio_bp.route('/ask/sionic/stream', methods=['POST', 'OPTIONS'])
def ask_sionic_stream():
    if request.method == 'OPTIONS':
        return ('', 204)
    ip = _client_ip()
    if not _check_rate(ip):
        return jsonify({'error': 'rate_limited', 'reason': '잠시 후 다시 시도해 주세요.'}), 429
    data = request.get_json(silent=True) or {}
    prompt = (data.get('prompt') or '').strip()[:PROMPT_MAX_LEN]
    if not prompt:
        return jsonify({'error': 'invalid_request', 'reason': 'prompt 필수.'}), 400

    def gen():
        yield f"data: {json.dumps({'type': 'session', 'session_id': 'sionic'}, ensure_ascii=False)}\n\n"
        full = ''
        try:
            for text in _og_stream(prompt, SIONIC_SYSTEM):
                full += text
                yield f"data: {json.dumps({'type': 'chunk', 'text': text}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'text': full[:RESPONSE_MAX_LEN]}, ensure_ascii=False)}\n\n"
            try:
                _log_to_firestore({'kind': 'sionic', 'ip': ip, 'prompt': prompt, 'response': full[:RESPONSE_MAX_LEN]})
            except Exception:
                pass
        except Exception:
            logger.exception('sionic chat error')
            yield f"data: {json.dumps({'type': 'chunk', 'text': sionic_fake_reply(prompt)}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

    return Response(
        gen(),
        mimetype='text/event-stream',
        # Connection: keep-alive 는 보내지 않는다. gunicorn sync 워커가 keep-alive 를
        # 지원하지 않아 지킬 수 없는 약속이다.
        #
        # ⚠️ 이걸 뺐다고 「요청마다 워커가 SIGKILL 당하는」 증상이 낫지는 않았다
        # (2026-08-25 실측). 그 원인은 아직 못 찾았다 — Firestore 적재를 스레드로
        # 옮기고 이 헤더를 빼도 요청 뒤 워커 하나가 계속 교체된다. 응답 자체는 done
        # 까지 정상이라 사용자에겐 안 보이고, 분당 제한은 sqlite 로 옮겨서 워커가
        # 죽어도 유지된다 — 그래서 급한 불은 껐지만 원인은 남아 있다.
        headers={'Cache-Control': 'no-cache, no-transform', 'X-Accel-Buffering': 'no'},
    )


# ─────────── 메이플 캐릭터 조회 (닉네임 → look hash) ───────────
# 캐릭터 이미지 자체(static/character/look)는 키 없이 열리지만, 닉네임을 그 hash 로
# 바꾸는 경로만 NEXON Open API 키를 요구한다. 키를 프론트에 두면 번들에 노출되므로
# 여기서 프록시한다. 키가 없으면 503 — 프론트는 기본 캐릭터로 폴백한다.

NEXON_API_BASE = 'https://open.api.nexon.com'
NEXON_LOOK_PREFIX = f'{NEXON_API_BASE}/static/maplestory/character/look/'
MAPLE_CACHE_TTL = 3600          # 넥슨 원본이 하루 1회 갱신이라 1시간이면 충분
MAPLE_RATE_PER_MIN = 20         # 챗봇(5회)보다 관대 — 오타 재입력이 잦다

_maple_cache: dict[str, tuple[float, dict]] = {}
_maple_cache_lock = threading.Lock()
_maple_rate_buckets: dict[str, deque[float]] = defaultdict(deque)


def _check_maple_rate(ip: str) -> bool:
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW
    with _rate_lock:
        bucket = _maple_rate_buckets[ip]
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= MAPLE_RATE_PER_MIN:
            return False
        bucket.append(now)
        return True


def _nexon_get(path: str, params: dict, api_key: str) -> tuple[int, dict]:
    import requests
    res = requests.get(
        f'{NEXON_API_BASE}{path}',
        params=params,
        headers={'x-nxopen-api-key': api_key},
        timeout=8,
    )
    try:
        return res.status_code, res.json()
    except ValueError:
        return res.status_code, {}


def _extract_look_hash(image_url: str) -> str | None:
    """character_image URL 에서 look hash 만 뽑는다.

    넥슨이 붙여 보내는 쿼리(?x=&y=)는 정면 정지 포즈용이라 버린다 —
    프론트가 wmotion/emotion/action 을 직접 조립해 걷기 모션을 만든다.
    """
    if not image_url or not image_url.startswith(NEXON_LOOK_PREFIX):
        return None
    tail = image_url[len(NEXON_LOOK_PREFIX):]
    return tail.split('?', 1)[0].strip() or None


@portfolio_bp.route('/maple/character', methods=['GET', 'OPTIONS'])
def maple_character():
    if request.method == 'OPTIONS':
        return ('', 204)

    ip = _client_ip()
    if not _check_maple_rate(ip):
        return jsonify({'error': 'rate_limited', 'reason': '잠시 후 다시 시도해 주세요.'}), 429

    name = (request.args.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'invalid_request', 'reason': '닉네임을 입력해 주세요.'}), 400
    if len(name) > 12:
        return jsonify({'error': 'invalid_request', 'reason': '메이플 닉네임은 12자를 넘지 않습니다.'}), 400

    cache_key = name.lower()
    with _maple_cache_lock:
        hit = _maple_cache.get(cache_key)
        if hit and time.time() - hit[0] < MAPLE_CACHE_TTL:
            return jsonify(hit[1])

    api_key = os.getenv('NEXON_API_KEY')
    if not api_key:
        return jsonify({
            'error': 'no_api_key',
            'reason': '캐릭터 검색이 아직 준비되지 않았습니다.',
        }), 503

    try:
        status, body = _nexon_get('/maplestory/v1/id', {'character_name': name}, api_key)
    except Exception:
        logger.exception('[maple] ocid 조회 실패')
        return jsonify({'error': 'upstream_error', 'reason': '넥슨 서버 응답이 없습니다.'}), 502

    ocid = body.get('ocid')
    if status != 200 or not ocid:
        # 여기서 400 이 나는 건 형식이 잘못된 입력일 때다. 존재하지 않는 닉네임은
        # 이 단계를 200 으로 통과한다(아래 basic 에서 갈린다).
        if status in (400, 404):
            return jsonify({'error': 'not_found', 'reason': f'"{name}" 캐릭터를 찾지 못했습니다.'}), 404
        logger.warning('[maple] ocid status=%s body=%s', status, body)
        return jsonify({'error': 'upstream_error', 'reason': '넥슨 서버 응답이 없습니다.'}), 502

    try:
        status, basic = _nexon_get('/maplestory/v1/character/basic', {'ocid': ocid}, api_key)
    except Exception:
        logger.exception('[maple] basic 조회 실패')
        return jsonify({'error': 'upstream_error', 'reason': '넥슨 서버 응답이 없습니다.'}), 502

    # 넥슨은 없는 닉네임에도 ocid 를 200 으로 발급한다(실측). 실제 존재 여부는
    # 여기서 400 OPENAPI00003 으로 갈리므로, ocid 를 받았다고 캐릭터가 있는 게 아니다.
    if status in (400, 404):
        return jsonify({'error': 'not_found', 'reason': f'"{name}" 캐릭터를 찾지 못했습니다.'}), 404
    if status != 200:
        logger.warning('[maple] basic status=%s body=%s', status, basic)
        return jsonify({'error': 'upstream_error', 'reason': '캐릭터 정보를 가져오지 못했습니다.'}), 502

    look_hash = _extract_look_hash(basic.get('character_image') or '')
    if not look_hash:
        # 캐릭터는 있는데 외형 URL 형식이 바뀐 경우 — 폴백 없이 원인을 남긴다
        logger.warning('[maple] look hash 추출 실패 image=%s', basic.get('character_image'))
        return jsonify({'error': 'no_look', 'reason': '이 캐릭터의 외형을 불러오지 못했습니다.'}), 502

    payload = {
        'name': basic.get('character_name') or name,
        'hash': look_hash,
        'world': basic.get('world_name'),
        'job': basic.get('character_class'),
        'level': basic.get('character_level'),
    }
    with _maple_cache_lock:
        _maple_cache[cache_key] = (time.time(), payload)
    return jsonify(payload)

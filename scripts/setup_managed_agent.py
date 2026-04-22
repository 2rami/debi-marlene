"""Anthropic Managed Agent에 메모리/게임 도구 추가 + 페르소나 미세 조정.

기본 dry-run. 실제 적용은 --apply 플래그.

사용법:
    python3 scripts/setup_managed_agent.py                 # unified 1개만 dry-run
    python3 scripts/setup_managed_agent.py --apply         # unified 1개만 update
    python3 scripts/setup_managed_agent.py --all           # unified+debi+marlene 3개 dry-run
    python3 scripts/setup_managed_agent.py --all --apply   # 3개 모두 update
    python3 scripts/setup_managed_agent.py --agent agent_XXX --apply  # 특정 agent만

이 스크립트는 idempotent — 같은 도구 이미 있으면 schema만 갱신, 중복 안 만듦.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env(ROOT / ".env")

API_KEY = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
AGENT_ID = os.getenv("MANAGED_AGENT_ID")
AGENT_ID_DEBI = os.getenv("MANAGED_AGENT_ID_DEBI")
AGENT_ID_MARLENE = os.getenv("MANAGED_AGENT_ID_MARLENE")

MEMORY_TOOLS = [
    {
        "type": "custom",
        "name": "remember_about_user",
        "description": (
            "유저가 명시적으로 알려준 사실(닉네임/메인 캐릭/호칭/봇 캐릭터 정정 등)을 영구 저장. "
            "농담, 감정 표현(사랑해 등), 모호한 추측은 저장 금지. "
            "유저가 '기억해', '알아둬', '나는 X야' 등 명확히 알려줄 때만 사용."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "fact": {
                    "type": "string",
                    "description": "한 줄로 요약된 사실. 예: '유저 닉네임은 거노', '메인 캐릭은 알렉스'",
                }
            },
            "required": ["fact"],
        },
    },
    {
        "type": "custom",
        "name": "recall_about_user",
        "description": (
            "이 유저에 대해 저장된 모든 사실 조회. "
            "유저가 '내 정보 뭐 있어', '나에 대해 뭐 알아' 같은 질문 할 때 사용."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "type": "custom",
        "name": "forget_about_user",
        "description": (
            "특정 사실 삭제. 유저가 '그거 잊어줘', 'X는 빼' 같은 명시적 요청 시만 사용."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "fact": {
                    "type": "string",
                    "description": "삭제할 사실. recall_about_user로 먼저 정확한 텍스트 확인 권장.",
                }
            },
            "required": ["fact"],
        },
    },
    {
        "type": "custom",
        "name": "get_conversation_stats",
        "description": (
            "이 유저와의 대화 통계 조회 (턴 수, 마지막 활동 시간). "
            "유저가 '우리 얼마나 얘기했어?', '대화 얼마나 됐어?' 같은 질문 할 때 사용."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "type": "custom",
        "name": "reset_my_memory",
        "description": (
            "세션 컨텍스트 초기화 (corrections는 안 건드림). "
            "유저가 명시적으로 '처음부터 다시', '대화 리셋' 요청 시만 사용. 함부로 호출 금지."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

GAME_TOOLS = [
    {
        "type": "custom",
        "name": "get_character_stats",
        "description": (
            "이터널 리턴 캐릭터별 통계(티어/승률/픽률) 조회. 다이아+ 기준. "
            "유저가 '통계', '요즘 캐릭터 뭐 쎄', 'OP 캐릭', '티어 어때', '픽률' 같이 캐릭터 메타 물어볼 때 사용. "
            "결과는 Discord 채널에 CharacterStatsView(페이지네이션 UI)로 자동 송출되고, "
            "Claude에는 상위 3~5 캐릭터 텍스트 요약이 반환돼서 톤 살려 답하면 됨."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "description": "조회 기간(일). 기본 7. 1/3/7 중 하나 권장.",
                }
            },
            "required": [],
        },
    },
    {
        "type": "custom",
        "name": "get_season_info",
        "description": (
            "이터널 리턴 현재 시즌 이름·경과일·시작일 조회. "
            "유저가 '시즌 언제 끝나', '지금 몇 시즌이야', '시즌 정보' 같이 시즌 물어볼 때 사용. "
            "결과는 Discord 채널에 Embed로 자동 송출. Claude에는 시즌명+일차 요약 반환."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "type": "custom",
        "name": "get_online_players",
        "description": (
            "이터널 리턴 Steam 동접자 수 조회. "
            "유저가 '동접 몇 명', '요즘 얼마나 해', '유저 많아' 같은 플레이어 수 물어볼 때 사용. "
            "결과는 Discord 채널에 Embed로 자동 송출. Claude에는 숫자 반환."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

ALL_NEW_TOOLS = MEMORY_TOOLS + GAME_TOOLS

PROMPT_APPENDIX = """

---

[메모리 도구 사용 규칙 — 2026-04-20 추가]

이전엔 "이름/메모장 역할 안 함"으로 거절했지만, 이제 도구로 영구 저장 가능. 다음 도구를 자율 판단으로 사용:

저장 OK인 정보:
- 유저 닉네임/호칭 (예: "거노라고 불러줘")
- 메인 캐릭터 (예: "내 메인은 알렉스")
- 게임 내 선호 (예: "솔로 플레이어야")
- 봇 캐릭터 정정 (예: "데비는 여캐야")

저장 금지:
- 감정 표현 (사랑해, 싫어, 좋아)
- 부적절 요청 (개인정보 무관)
- 봇이 추측한 것 (유저가 명시 안 한 것)

호출 시점:
- "기억해/알아둬/나는 X야" → remember_about_user
- "내 정보 뭐 있어" → recall_about_user
- "그거 잊어줘" → forget_about_user(fact)
- "우리 얼마나 얘기했어" → get_conversation_stats
- "리셋", "처음부터" → reset_my_memory

저장 후엔 데비/마를렌 캐릭터 톤으로 자연스럽게 답:
- "OK, 거노네! 기억할게."
- "응, 알렉스 메인 잘 챙길게."
- 절대 "기억해주는 거 아니야" 류 거절 X

단 *부적절/모호*한 요청은 여전히 캐릭터 톤으로 거절 (예: "사랑해 기억해줘" → 농담으로 받아치고 저장 X).
"""


def _update_one_agent(client, agent_id: str, apply: bool) -> bool:
    """단일 agent에 ALL_NEW_TOOLS 적용. solo/unified 자동 감지 → PROMPT_APPENDIX는 unified만."""
    print(f"\n=== agent {agent_id} ===")
    agent = client.beta.agents.retrieve(agent_id=agent_id)
    current_prompt = getattr(agent, "system", "") or ""
    current_tools = list(getattr(agent, "tools", []) or [])
    current_tool_names = []
    for t in current_tools:
        n = getattr(t, "name", None) or (t.get("name") if isinstance(t, dict) else None)
        if n:
            current_tool_names.append(n)

    print(f"  system 길이: {len(current_prompt)}")
    print(f"  현재 tools ({len(current_tool_names)}개): {current_tool_names}")

    new_tool_names = {t["name"] for t in ALL_NEW_TOOLS}
    added = [t["name"] for t in ALL_NEW_TOOLS if t["name"] not in current_tool_names]
    renewed = [t["name"] for t in ALL_NEW_TOOLS if t["name"] in current_tool_names]
    if added:
        print(f"  [신규] {added}")
    if renewed:
        print(f"  [갱신] {renewed}")

    has_memory_rules = "[메모리 도구 사용 규칙" in current_prompt
    if has_memory_rules:
        print(f"  system: 메모리 규칙 이미 포함, 건너뜀")
        new_prompt = current_prompt
    else:
        print(f"  system: 메모리 규칙 +{len(PROMPT_APPENDIX)} chars 추가")
        new_prompt = current_prompt + PROMPT_APPENDIX

    # 기존 tools 유지 (search_*) + ALL_NEW_TOOLS 추가/갱신
    merged_tools = []
    for t in current_tools:
        n = getattr(t, "name", None) or (t.get("name") if isinstance(t, dict) else None)
        if n in new_tool_names:
            continue
        merged_tools.append(_tool_to_dict(t))
    merged_tools.extend(ALL_NEW_TOOLS)

    final_names = [t["name"] for t in merged_tools]
    print(f"  최종 tools ({len(merged_tools)}개): {final_names}")

    if not apply:
        return False

    current_version = getattr(agent, "version", None)
    updated = client.beta.agents.update(
        agent_id=agent_id,
        version=current_version,
        system=new_prompt,
        tools=merged_tools,
    )
    print(f"  OK → version={getattr(updated, 'version', '?')}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Managed Agent에 메모리+게임 도구 추가")
    parser.add_argument("--apply", action="store_true", help="실제 update 실행 (없으면 dry-run)")
    parser.add_argument("--all", action="store_true",
                        help="unified+debi+marlene 3개 모두 처리 (env에 ID 필요)")
    parser.add_argument("--agent", metavar="AGENT_ID",
                        help="특정 agent_id만 처리 (env 무시)")
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: CLAUDE_API_KEY 또는 ANTHROPIC_API_KEY .env에 필요")
        sys.exit(1)

    # 처리할 agent 리스트 결정
    targets: list[tuple[str, str]] = []  # (label, agent_id)
    if args.agent:
        targets.append(("custom", args.agent))
    elif args.all:
        if AGENT_ID:
            targets.append(("unified", AGENT_ID))
        if AGENT_ID_DEBI:
            targets.append(("debi-solo", AGENT_ID_DEBI))
        if AGENT_ID_MARLENE:
            targets.append(("marlene-solo", AGENT_ID_MARLENE))
        if not targets:
            print("ERROR: --all 사용 시 MANAGED_AGENT_ID / _DEBI / _MARLENE 중 하나 이상 필요")
            sys.exit(1)
    else:
        if not AGENT_ID:
            print("ERROR: MANAGED_AGENT_ID .env에 필요 (또는 --all / --agent 사용)")
            sys.exit(1)
        targets.append(("unified", AGENT_ID))

    print(f"=== 대상 agent {len(targets)}개 ===")
    for label, aid in targets:
        print(f"  - {label}: {aid}")

    client = anthropic.Anthropic(api_key=API_KEY)

    for label, aid in targets:
        print(f"\n[{label}]")
        _update_one_agent(client, aid, args.apply)

    print()
    if args.apply:
        print(f"OK 업데이트 완료 ({len(targets)}개 agent)")
    else:
        print(f"[DRY RUN] --apply 안 줌. 실제 update 안 함. ({len(targets)}개 agent 대상)")


def _tool_to_dict(t):
    """anthropic SDK 객체 또는 dict → dict 정규화. type='custom' 보장."""
    if isinstance(t, dict):
        d = dict(t)
    else:
        d = {
            "name": getattr(t, "name", ""),
            "description": getattr(t, "description", ""),
            "input_schema": getattr(t, "input_schema", {"type": "object", "properties": {}}),
        }
    d.setdefault("type", "custom")
    return d


if __name__ == "__main__":
    main()

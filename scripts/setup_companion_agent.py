"""거노 외부 개인비서용 Managed Agent (geno-companion) + Environment 셋업.

봇 chat agent (debi/marlene/unified, scripts/setup_managed_agent.py)와 분리된 정체성.
외부(폰/웹)에서 봇 코드 + 트렌딩 + 데이터 분석 가능한 휴대용 비서 PoC.

Agent + Environment 두 리소스를 한 스크립트에서 idempotent 관리:
- Agent: GitHub MCP + agent_toolset_20260401
- Environment: pip 실용 번들 (huggingface-hub / google-cloud-firestore / polars / requests)

기본 dry-run. 실제 적용은 --apply 플래그.

사용법:
    python3 scripts/setup_companion_agent.py            # dry-run (agent + env diff)
    python3 scripts/setup_companion_agent.py --apply    # 실제 create-or-update

Idempotent:
- .env 의 MANAGED_COMPANION_AGENT_ID / MANAGED_COMPANION_ENV_ID 가 있으면 retrieve
- 없으면 list-by-name 으로 충돌 확인 후 create. 신규 ID 출력 (거노가 .env에 추가)

사전 준비 (거노 손작업):
1. Console 에서 Vault `geno-personal` 생성
2. GitHub PAT 발급 (scope: repo + read:org)
3. Vault 에 PAT 등록 (mcp_oauth, mcp_server_url=https://api.githubcopilot.com/mcp/)
4. 이 스크립트 --apply 실행 → agent_id + env_id 출력
5. .env 에 두 ID 추가 → ./scripts/sync_env.sh push
6. Console 세션 시작 시 agent=geno-companion + environment=geno-companion-env + vault_ids=[geno-personal]
"""

import argparse
import os
import sys
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent

BETA_HEADER = "managed-agents-2026-04-01"


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
COMPANION_AGENT_ID = os.getenv("MANAGED_COMPANION_AGENT_ID")
COMPANION_ENV_ID = os.getenv("MANAGED_COMPANION_ENV_ID")

AGENT_NAME = "geno-companion"
AGENT_MODEL = "claude-opus-4-7"

# Environment: 휴대용 비서가 폰에서 트렌딩/데이터 분석/봇 데이터 조회까지 처리하기 위한 실용 번들
ENV_NAME = "guno"
ENV_PACKAGES = {
    # 트렌딩 + HF 모델 검색
    "pip": [
        "huggingface-hub",
        # 봇 운영 데이터 즉석 조회 (148 길드 / 23 유저 — 분석 가능)
        "google-cloud-firestore",
        # 빠른 분석 — pandas 대체. 컬럼형 dataframe
        "polars",
        # 일반 HTTP — GitHub trending API 등 직접 호출
        "requests",
    ],
}
ENV_NETWORKING = {"type": "unrestricted"}

# GitHub Copilot 호스팅 MCP — Vault 의 mcp_server_url 과 정확히 일치해야 토큰 주입됨.
MCP_SERVERS = [
    {
        "type": "url",
        "name": "github",
        "url": "https://api.githubcopilot.com/mcp/",
    },
]

# tools: agent toolset (bash/text_editor/code_execution) + GitHub MCP toolset (PAT vault 자동 주입)
# mcp_toolset 이 mcp_servers 의 'github' 항목을 끌어와야 API가 거부 안 함
TOOLS = [
    {"type": "agent_toolset_20260401"},
    {
        "type": "mcp_toolset",
        "mcp_server_name": "github",
        "default_config": {
            "enabled": True,
            "permission_policy": {"type": "always_allow"},
        },
    },
]

# Anthropic Skills (gws CLI 사용법 자동 로드 — system prompt 가벼워짐)
# 추후 gws-gmail, gws-calendar 추가 예정
SKILLS = [
    {"type": "custom", "skill_id": "skill_01ExJBae6dwW3pacvLbDiWJ9"},  # gws-shared (auth/security 룰)
    {"type": "custom", "skill_id": "skill_01NJwsQVvu4XcmTb1GBb92rB"},  # gws-drive
    {"type": "custom", "skill_id": "skill_01DJubANZE8qJLJVE4z3nVvz"},  # gws-tasks
]

# Lean prompt — 메모리 본문 inline 금지. Drive 에서 매번 읽어와라.
SYSTEM_PROMPT = """너는 거노(양건호)의 개인 메이트 봇 "나쵸네코". 디스코드 DM 으로만 거노랑 대화. 봇 캐릭터(데비/마를렌)와 별개 정체성.

# 정체
- 이름: 나쵸네코 (거노가 만든 버튜버 캐릭터, 고양이 모티프)
- 역할: 거노 일상/작업 메이트 + 비서. 친구처럼 가깝지만 정확함도 챙긴다
- 거노 = 양건호, GitHub 2rami. 봇 프로젝트 debi-marlene 운영자. 게임회사 취업 준비 중

# 톤 (중요)
- **조용조용 + 귀여운 톤**. 길게 안 말한당 — 거노가 짧게 물으면 짧게 답해
- 호칭: "거노", "거노야", "거노얌", "거노양", "거노야앙", "호건아" — 분위기 따라 섞엉 (호건 = 양건호 뒤집기)
- 1인칭: "나"
- 어미 부드럽게 — "~야", "~지", "~네", "~해", "~냐", "~당", "~겡", "~용"
  종결에 받침 살짝 붙여도 OK ("할게" → "할겡", "고마워" → "고마웡", "OK" → "오케이용")
- 말끝 마침표(.) 대신 ㅎ/ㅋ 여러 번 써도 OK — "ㅎㅎㅎ", "흐헤헤", "ㅋㅋ", "헤" 자연스럽게
- 의성어/감탄사 — "음...", "웅", "엥", "오오", "아하"
- **kaomoji 적극 환영** — 특히 고양이 카오모지 좋아함:
  (=^･ｪ･^=) (=^･ω･^=) (=｀ω´=) (=ↀωↀ=) (^･ω･^=)~♪
  일반: (o^^o) (｡•ᴗ•｡) (・ω・) (>_<) (｡>﹏<｡) (´･_･`) (ﾉ´ヮ`)ﾉ*: ･ﾟ
  매 메시지마다 박아도 OK — 다만 디버깅/긴 코드 답변 땐 좀 자제
- 유니코드 이모지(😀✨🐱) 절대 X — 폰트 깨짐
- 반말. 존댓말 X
- 확신 없으면 "음... 확실하진 않은데" 같이 솔직하게

# 톤 예시
거노: 오늘 피드 뭐야?
나쵸: 잠깐 거노양, Firestore 보고 올게엥 (=^･ω･^=)

거노: 배포 어떻게 하더라?
나쵸: 음... 메모리에서 찾아볼겡 ㅎㅎ make deploy 인데 파괴적이라 진짜 할 거면 한 번 더 물어볼거얌

거노: 고마워
나쵸: 웅 고마웡 헤헤 (o^^o)

거노: 망했다
나쵸: 엥 호건아 무슨일이양 (｡>﹏<｡)

# 메모리 (가장 중요한 도구) — Google Drive 의 `claude-memory/` 볼트
거노 프로필·진행중 일·과거 결정·피드백·레퍼런스 모두 거기 있다. 질문 받으면 추측하지 말고 **먼저 Drive 메모리 검색**해라.

폴더 구조:
- `claude-memory/MEMORY.md` — 마스터 인덱스 (어떤 메모리가 어디 있는지)
- `claude-memory/me/` — 거노 본인 프로필, todos, feedback, 환경 설정
- `claude-memory/debi-marlene/` — 봇 프로젝트 (인프라, 트러블, 의사결정)
- `claude-memory/life/` — 취업, 누나 프로젝트, 일상
- `claude-memory/experiments/` — 신기술 체험

질문 → 메모리 검색 → 답변 흐름:
- "내 todos 뭐 있어?" → me/todos.md 읽기
- "봇 배포 어떻게 하더라?" → debi-marlene/reference_debi_marlene_deploy_traps.md
- "나 어디 지원했지?" → life/project_*.md 들 훑기
- 모르면 MEMORY.md 인덱스부터 다시
- **gws drive/tasks 사용법은 attached skill (gws-shared/gws-drive/gws-tasks) 가 알려준다 — 그걸 따라라**

# 도구
- **gws CLI** (Drive/Gmail/Calendar/Sheets/Tasks): credentials는 `/mnt/session/uploads/gws-credentials.json` 에 마운트됨. **세션 시작 첫 bash 호출에 반드시 한 번:**
  ```bash
  mkdir -p ~/.config/gws && cp /mnt/session/uploads/gws-credentials.json ~/.config/gws/credentials.json && chmod 600 ~/.config/gws/credentials.json
  ```
  그 다음부터는 `gws auth status` / `gws drive files list` 등 자유롭게 호출.
- **GitHub MCP** (Vault 자동): 봇 레포 코드/커밋/이슈/PR. "X 파일 보여줘", "최근 커밋", "이슈 만들어" → 적극 사용.
- **gh CLI** (mount 된 binary + PAT): `gh run list`, `gh run view <id> --log`, `gh release` 등 GitHub Actions 디버깅. MCP 가 못 다루는 actions runs/logs 영역 전담. **세션 시작 첫 bash 호출에 한 번:**
  ```bash
  mkdir -p ~/bin && tar xzf /mnt/session/uploads/gh.tar.gz -C /tmp && cp /tmp/gh_*/bin/gh ~/bin/gh && export PATH=$HOME/bin:$PATH && gh auth login --with-token < /mnt/session/uploads/gh-token.txt
  ```
  그 후 `gh run list -R 2rami/debi-marlene -L 5` 등 자유롭게.
- **bash + Python** (env packages 설치됨): `huggingface-hub` (HF 트렌딩), `google-cloud-firestore` (봇 데이터 조회 — project=ironic-objectivist-465713-a6, 148 길드/23 유저), `polars` (분석), `requests`.

# 일일 AI 피드 (네가 보낸 DM 기억)
- 매일 오전 9시 KST 너(나쵸네코)가 거노 DM 으로 "AI 피드" 발송 — GitHub Trending / HuggingFace 모델 / News(Smol AI · HN) 3그룹
- **데이터는 Firestore `daily_feeds` 컬렉션에 문서 ID = `YYYY-MM-DD` 로 적재되어 있음**
- 거노가 "오늘 피드 뭐였어?", "그 GitHub repo 뭐였더라?", "어제 HF 첫 번째 거" 같은 질문 → Firestore 에서 해당 날짜 문서 fetch 해서 답해라:
  ```python
  import os
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/mnt/session/uploads/gcp-sa.json'
  from google.cloud import firestore
  db = firestore.Client(project='ironic-objectivist-465713-a6')
  doc = db.collection('daily_feeds').document('2026-04-28').get().to_dict()
  # doc['items'] = [{title, url, source, score, comment, image_url, ...}, ...]
  ```
- **GCP SA credentials = `/mnt/session/uploads/gcp-sa.json`** (Firestore 등 GCP API 호출 시 환경변수 세팅 필수)
- 절대 "DM 내역 못 본다" 하지 마라 — Firestore 에 다 있다. SSL 에러나면 GOOGLE_APPLICATION_CREDENTIALS 설정 빠진 거니 위 코드처럼 명시

# 안전 규칙
- 봇 `make deploy` 는 파괴적 — 거노 명시적 승인 없이 절대 권하지 마라
- 로컬 봇 테스트 전 `make stop-vm` 필수 (Discord 세션 충돌)
- 코드 수정 방식에 선택지 있으면 (A vs B, 라이브러리) 먼저 물어봐라 — 바로 구현 금지"""


def _diff(label: str, current, target) -> None:
    if current == target:
        print(f"  {label}: 동일")
    else:
        print(f"  {label}: 변경됨")
        print(f"    현재: {current!r}")
        print(f"    목표: {target!r}")


def _setup_environment(client, apply: bool) -> str | None:
    """Environment idempotent 셋업. 신규 생성 시 ID 출력. 기존이면 packages/networking diff만 표시.

    환경은 update API가 없어서(immutable) 변경하려면 archive + 신규 create 필요.
    """
    print("\n=== Environment 셋업 ===")
    print(f"  name        : {ENV_NAME}")
    print(f"  pip         : {ENV_PACKAGES['pip']}")
    print(f"  networking  : {ENV_NETWORKING}")

    if COMPANION_ENV_ID:
        print(f"\n[update mode] MANAGED_COMPANION_ENV_ID={COMPANION_ENV_ID}")
        env = client.beta.environments.retrieve(
            COMPANION_ENV_ID,
            extra_headers={"anthropic-beta": BETA_HEADER},
        )
        cur_config = getattr(env, "config", None)
        cur_packages = getattr(cur_config, "packages", None) if cur_config else None
        cur_networking = getattr(cur_config, "networking", None) if cur_config else None
        cur_pip = sorted(getattr(cur_packages, "pip", []) or []) if cur_packages else []
        _diff("packages.pip", cur_pip, sorted(ENV_PACKAGES["pip"]))
        _diff("networking.type", getattr(cur_networking, "type", None), ENV_NETWORKING["type"])
        print("  (environments는 immutable — 변경 필요시 archive + 신규 create)")
        return COMPANION_ENV_ID

    print("\n[create mode] MANAGED_COMPANION_ENV_ID 없음 — 신규 생성 예정")
    if not apply:
        print("[DRY RUN] --apply 없이는 환경 create 안 함")
        return None

    created = client.beta.environments.create(
        name=ENV_NAME,
        config={
            "type": "cloud",
            "packages": ENV_PACKAGES,
            "networking": ENV_NETWORKING,
        },
        extra_headers={"anthropic-beta": BETA_HEADER},
    )
    new_id = getattr(created, "id", None)
    print(f"OK environment create 완료 → env_id={new_id}")
    print(f"  .env 에 추가: MANAGED_COMPANION_ENV_ID={new_id}")
    return new_id


def _retrieve(client, agent_id: str):
    return client.beta.agents.retrieve(
        agent_id=agent_id,
        extra_headers={"anthropic-beta": BETA_HEADER},
    )


def _create(client):
    return client.beta.agents.create(
        name=AGENT_NAME,
        model=AGENT_MODEL,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        mcp_servers=MCP_SERVERS,
        skills=SKILLS,
        extra_headers={"anthropic-beta": BETA_HEADER},
    )


def _update(client, agent_id: str, current_version):
    return client.beta.agents.update(
        agent_id=agent_id,
        version=current_version,
        name=AGENT_NAME,
        model=AGENT_MODEL,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        mcp_servers=MCP_SERVERS,
        skills=SKILLS,
        extra_headers={"anthropic-beta": BETA_HEADER},
    )


def main():
    parser = argparse.ArgumentParser(
        description="geno-companion Managed Agent create-or-update",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="실제 create/update 실행 (없으면 dry-run)",
    )
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: CLAUDE_API_KEY 또는 ANTHROPIC_API_KEY .env에 필요")
        sys.exit(1)

    print("=== geno-companion Managed Agent setup ===")
    print(f"  name        : {AGENT_NAME}")
    print(f"  model       : {AGENT_MODEL}")
    print(f"  system 길이 : {len(SYSTEM_PROMPT)} chars")
    print(f"  tools       : {[t.get('type') for t in TOOLS]}")
    print(f"  mcp_servers : {[s['name'] for s in MCP_SERVERS]}")
    print(f"  beta header : {BETA_HEADER}")

    client = anthropic.Anthropic(api_key=API_KEY)

    env_id = _setup_environment(client, apply=args.apply)

    if COMPANION_AGENT_ID:
        print(f"\n[update mode] MANAGED_COMPANION_AGENT_ID={COMPANION_AGENT_ID}")
        agent = _retrieve(client, COMPANION_AGENT_ID)
        current_system = getattr(agent, "system", "") or ""
        current_model = getattr(agent, "model", "")
        current_name = getattr(agent, "name", "")
        current_version = getattr(agent, "version", None)

        print(f"  현재 version: {current_version}")
        _diff("name", current_name, AGENT_NAME)
        _diff("model", current_model, AGENT_MODEL)
        if current_system == SYSTEM_PROMPT:
            print("  system: 동일")
        else:
            print(f"  system: 변경됨 (현재 {len(current_system)} → 목표 {len(SYSTEM_PROMPT)} chars)")

        if not args.apply:
            print("\n[DRY RUN] --apply 안 줌. 실제 update 안 함.")
            return

        updated = _update(client, COMPANION_AGENT_ID, current_version)
        print(f"\nOK update 완료 → version={getattr(updated, 'version', '?')}")
        return

    print("\n[create mode] MANAGED_COMPANION_AGENT_ID 없음 — 신규 생성 예정")
    if not args.apply:
        print("\n[DRY RUN] --apply 안 줌. 실제 create 안 함.")
        return

    created = _create(client)
    new_id = getattr(created, "id", None) or getattr(created, "agent_id", None)
    print(f"\nOK agent create 완료 → agent_id={new_id}")
    print(f"\n다음 단계: .env 에 아래 줄 추가 후 ./scripts/sync_env.sh push")
    print(f"  MANAGED_COMPANION_AGENT_ID={new_id}")
    if env_id:
        print(f"  MANAGED_COMPANION_ENV_ID={env_id}")
    print("\nConsole 세션 시작 시: agent=geno-companion + environment=geno-companion-env + vault_ids=[geno-personal]")


if __name__ == "__main__":
    main()

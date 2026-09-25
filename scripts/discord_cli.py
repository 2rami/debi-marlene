#!/usr/bin/env python3
"""디스코드 CLI(dsc) - Components V2 를 읽을 수 있는 텍스트로 풀어준다.

공개된 디스코드 도구들은 메시지의 `content` 만 읽는다. 그런데 우리 봇 화면은 전부
Components V2 라 `content` 가 비어 있고 내용이 `components` 안에 들어간다. 그래서 남의
도구로 우리 봇 화면을 보면 빈 메시지로 보인다.

여기서는 webpanel/src/components/chat/MessageArea.tsx 의 렌더러를 텍스트로 옮겨서,
Container/Section/Thumbnail/Separator 까지 구조 그대로 보여준다.

MCP 로 물려 두면 도구 설명이 모든 세션의 매 요청에 실리는데, 쓰는 날은 드물다. 그래서
부를 때만 비용이 드는 CLI 로 둔다.

봇 토큰으로만 동작한다. 유저 토큰(셀프봇)은 디스코드 ToS 위반이라 쓰지 않는다 - 봇이
초대된 서버만 보이는 게 이 방식의 한계이자 안전장치다.
"""

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://discord.com/api/v10"
UA = "debi-marlene-cli (local, 1.0)"

# 메시지가 Components V2 인지 알려주는 플래그. MessageArea.tsx 와 같은 값이다.
IS_COMPONENTS_V2 = 1 << 15

BUTTON_STYLE = {1: "Primary", 2: "Secondary", 3: "Success", 4: "Danger", 5: "Link"}


def _token() -> str:
    """토큰은 설정 파일이 아니라 레포의 .env 에서 읽는다.

    래퍼나 설정 파일에 토큰을 적어 두면 그 파일이 실수로 커밋될 수 있다.
    """
    if env := os.environ.get("DISCORD_TOKEN"):
        return env
    path = pathlib.Path(__file__).resolve().parent.parent / ".env"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DISCORD_TOKEN="):
            return line.split("=", 1)[1].strip().strip("'\"")
    raise RuntimeError(".env 에서 DISCORD_TOKEN 을 찾지 못했어요")


def _api(path: str, *, method: str = "GET", body: dict | None = None):
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(body).encode() if body else None,
        headers={
            "Authorization": "Bot " + _token(),
            "User-Agent": UA,
            **({"Content-Type": "application/json"} if body else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return json.loads(res.read() or "null")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        if exc.code == 403:
            raise RuntimeError(f"권한이 없어요(403). 봇이 그 채널을 볼 수 있는지 확인해주세요. {detail}")
        if exc.code == 404:
            raise RuntimeError(f"찾을 수 없어요(404). ID 를 다시 확인해주세요. {detail}")
        raise RuntimeError(f"디스코드 API 오류 {exc.code}: {detail}")


# === Components V2 렌더러 (MessageArea.tsx 이식) ===

def _accent(value: int | None) -> str:
    return f" accent=#{value:06x}" if value is not None else ""


def _render(component: dict, depth: int = 0) -> list[str]:
    pad = "  " * depth
    kind = component.get("type")

    if kind == 10:  # TextDisplay
        return [pad + line for line in (component.get("content") or "").split("\n")]

    if kind == 9:  # Section - 텍스트 + 오른쪽 accessory
        out: list[str] = []
        for child in component.get("components") or []:
            out += _render(child, depth)
        acc = component.get("accessory") or {}
        if acc.get("type") == 11:
            url = (acc.get("media") or {}).get("url", "")
            out.append(f"{pad}└ [썸네일] {url}")
        return out

    if kind == 12:  # MediaGallery
        out = []
        for item in component.get("items") or []:
            url = (item.get("media") or {}).get("url", "")
            desc = item.get("description") or ""
            out.append(f"{pad}[이미지] {url}" + (f" ({desc})" if desc else ""))
        return out

    if kind == 14:  # Separator
        wide = component.get("spacing") == 2
        if component.get("divider") is False:
            return [pad + "  (여백)"]
        return [pad + ("=" * 40 if wide else "-" * 40)]

    if kind == 1:  # ActionRow
        out = []
        for child in component.get("components") or []:
            out += _render(child, depth)
        return out

    if kind == 2:  # Button
        style = BUTTON_STYLE.get(component.get("style", 2), "?")
        label = component.get("label") or ""
        url = f" -> {component['url']}" if component.get("url") else ""
        return [f"{pad}[버튼:{style}] {label}{url}"]

    if kind == 13:  # File
        url = (component.get("file") or {}).get("url", "")
        return [f"{pad}[파일] {url.split('/')[-1]}"]

    if kind == 17:  # Container - 최상위 상자
        out = [f"{pad}┌─ Container{_accent(component.get('accent_color'))}"]
        for child in component.get("components") or []:
            out += _render(child, depth + 1)
        out.append(f"{pad}└─")
        return out

    if kind in (3, 5, 6, 7, 8):  # Select 메뉴
        return [f"{pad}[선택메뉴] {component.get('placeholder') or ''}"]

    return [f"{pad}[알 수 없는 컴포넌트 type={kind}]"]


def _render_message(msg: dict) -> str:
    author = msg.get("author") or {}
    name = author.get("username", "?")
    tag = " (봇)" if author.get("bot") else ""
    stamp = (msg.get("timestamp") or "")[:16].replace("T", " ")
    head = f"[{stamp}] {name}{tag}  (id={msg.get('id')})"

    lines = [head]
    if content := (msg.get("content") or "").strip():
        lines += ["  " + line for line in content.split("\n")]

    components = msg.get("components") or []
    is_v2 = bool(msg.get("flags", 0) & IS_COMPONENTS_V2) or any(
        c.get("type") == 17 for c in components
    )
    if components and is_v2:
        lines.append("  --- Components V2 ---")
        for comp in components:
            lines += _render(comp, 1)
    elif embeds := msg.get("embeds"):
        for emb in embeds:
            title = emb.get("title") or ""
            desc = (emb.get("description") or "").split("\n")[0][:120]
            lines.append(f"  [임베드] {title} {desc}".rstrip())

    for att in msg.get("attachments") or []:
        lines.append(f"  [첨부] {att.get('filename')} {att.get('url','')}")

    if reactions := msg.get("reactions"):
        marks = " ".join(f"{(r.get('emoji') or {}).get('name')}x{r.get('count')}" for r in reactions)
        lines.append(f"  [반응] {marks}")

    return "\n".join(lines)


# === 도구 ===

def discord_list_guilds(query: str = "", limit: int = 30) -> str:
    """봇이 들어가 있는 서버 목록. query 를 주면 이름으로 걸러낸다.

    봇이 서버 수백 개에 있을 수 있어서 기본은 30개만 보여준다.
    """
    guilds = _api("/users/@me/guilds") or []
    if query:
        guilds = [g for g in guilds if query.lower() in (g.get("name") or "").lower()]
    total = len(guilds)
    rows = [f"{g['id']}  {g.get('name')}" for g in guilds[:limit]]
    head = f"서버 {total}개" + (f" (검색: {query})" if query else "") + f" - {len(rows)}개 표시"
    return head + "\n" + "\n".join(rows) if rows else head + "\n(없음)"


def discord_list_channels(guild_id: str) -> str:
    """서버의 텍스트 채널 목록. 카테고리별로 묶어서 보여준다."""
    channels = _api(f"/guilds/{guild_id}/channels") or []
    cats = {c["id"]: c.get("name", "?") for c in channels if c.get("type") == 4}
    text = [c for c in channels if c.get("type") in (0, 5, 15)]
    text.sort(key=lambda c: (c.get("position") or 0))

    grouped: dict[str, list[str]] = {}
    for ch in text:
        label = cats.get(ch.get("parent_id"), "(분류 없음)")
        grouped.setdefault(label, []).append(f"  {ch['id']}  #{ch.get('name')}")

    out = [f"텍스트 채널 {len(text)}개"]
    for label, rows in grouped.items():
        out.append(f"[{label}]")
        out += rows
    return "\n".join(out)


def discord_read_messages(channel_id: str, limit: int = 25, before: str = "", bots_only: bool = False) -> str:
    """채널 메시지를 읽는다. Components V2 화면은 구조를 풀어서 보여준다.

    before 에 메시지 ID 를 주면 그보다 이전 것을 가져온다(과거로 넘기기).
    --bots 를 주면 봇이 보낸 것만 남긴다 - 내 봇 화면을 확인할 때 쓴다.
    """
    limit = max(1, min(limit, 100))
    path = f"/channels/{channel_id}/messages?limit={limit}"
    if before:
        path += f"&before={before}"
    msgs = _api(path) or []
    if bots_only:
        msgs = [m for m in msgs if (m.get("author") or {}).get("bot")]
    if not msgs:
        return "메시지가 없어요." + (" (봇 메시지만 걸렀어요)" if bots_only else "")

    # 디스코드는 최신순으로 주는데, 읽을 때는 위에서 아래로 흐르는 게 편하다.
    msgs.reverse()
    return "\n\n".join(_render_message(m) for m in msgs)


def discord_send_message(channel_id: str, content: str) -> str:
    """봇 이름으로 메시지를 보낸다. 실제로 전송되니 사람 확인을 받고 쓴다."""
    if not content.strip():
        raise RuntimeError("빈 내용은 보낼 수 없어요.")
    msg = _api(f"/channels/{channel_id}/messages", method="POST", body={"content": content})
    return f"보냈어요. id={msg.get('id')} channel={channel_id}"


def discord_send_dm(user_id: str, content: str) -> str:
    """봇이 그 사람에게 DM 을 보낸다. 실제로 전송되니 사람 확인을 받고 쓴다.

    DM 은 채널 ID 가 따로 없어서 먼저 상대와의 DM 채널을 연 다음 보낸다. 이미 열려
    있으면 디스코드가 같은 채널을 돌려주므로 채널이 새로 늘지는 않는다.
    """
    if not content.strip():
        raise RuntimeError("빈 내용은 보낼 수 없어요.")
    channel = _api("/users/@me/channels", method="POST", body={"recipient_id": user_id})
    channel_id = channel.get("id")
    msg = _api(f"/channels/{channel_id}/messages", method="POST", body={"content": content})
    return f"DM 보냈어요. id={msg.get('id')} dm_channel={channel_id}"


def _content(value: str) -> str:
    # 여러 줄 본문은 셸 따옴표를 거치며 깨지기 쉬워서 `-` 면 표준입력으로 받는다.
    return sys.stdin.read() if value == "-" else value


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dsc",
        description="봇 토큰으로 디스코드를 읽고 보낸다. send·dm 은 실제로 전송된다.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="<명령>")

    def add(name, fn, summary):
        return sub.add_parser(name, help=summary, description=fn.__doc__,
                              formatter_class=argparse.RawDescriptionHelpFormatter)

    p = add("guilds", discord_list_guilds, "봇이 들어간 서버 목록")
    p.add_argument("query", nargs="?", default="", help="이름 검색어")
    p.add_argument("--limit", type=int, default=30)
    p.set_defaults(run=lambda a: discord_list_guilds(a.query, a.limit))

    p = add("channels", discord_list_channels, "서버의 텍스트 채널 목록")
    p.add_argument("guild_id")
    p.set_defaults(run=lambda a: discord_list_channels(a.guild_id))

    p = add("read", discord_read_messages, "채널 메시지 읽기(Components V2 풀어서)")
    p.add_argument("channel_id")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--before", default="", help="이 메시지 ID 보다 이전 것")
    p.add_argument("--bots", action="store_true", help="봇 메시지만")
    p.set_defaults(run=lambda a: discord_read_messages(a.channel_id, a.limit, a.before, a.bots))

    p = add("send", discord_send_message, "채널에 메시지 보내기(실제 전송)")
    p.add_argument("channel_id")
    p.add_argument("content", help="본문. - 면 표준입력")
    p.set_defaults(run=lambda a: discord_send_message(a.channel_id, _content(a.content)))

    p = add("dm", discord_send_dm, "DM 보내기(실제 전송)")
    p.add_argument("user_id")
    p.add_argument("content", help="본문. - 면 표준입력")
    p.set_defaults(run=lambda a: discord_send_dm(a.user_id, _content(a.content)))

    args = parser.parse_args()
    try:
        print(args.run(args))
    except RuntimeError as exc:
        sys.exit(str(exc))


if __name__ == "__main__":
    main()

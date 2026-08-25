"""@tasks.loop 이 예외로 멈추는 것을 잡는다.

discord.ext.tasks 의 루프는 처리되지 않은 예외를 만나면 콘솔에 한 번 찍고
**영영 멈춘다.** 알림도 재기동도 없어서 패치노트·쿠폰·동접 갱신 같은 기능이
죽어 있어도 봇은 겉으로 멀쩡해 보인다 — 명령어는 계속 되니까.

여기 붙이면 죽는 순간 훅으로 알리고 정해진 횟수까지 되살린다.
"""

from __future__ import annotations

# 같은 루프가 계속 죽으면 폭주한다. 세 번까지만 되살리고 그 뒤엔 알리고 포기한다.
_MAX_RESTARTS = 3

_restarts: dict[str, int] = {}


def attach(loop, name: str, *, restart: bool = True) -> None:
    """`@tasks.loop` 객체에 오류 핸들러를 건다.

    cog 안의 루프는 핸들러가 (self, exc) 로, 모듈 레벨은 (exc) 로 불리므로
    인자를 열어 두고 마지막 것을 예외로 본다 — discord.py 가 그렇게 넘긴다.
    """

    async def _handler(*args):
        exc = args[-1] if args else RuntimeError("알 수 없는 오류")

        count = _restarts.get(name, 0) + 1
        _restarts[name] = count
        give_up = (not restart) or count > _MAX_RESTARTS

        if give_up:
            note = f"{count}번째 실패 — 되살리기를 멈춘다. 봇을 다시 켜야 복구된다."
        else:
            note = f"{count}번째 실패 — 다시 시작한다. ({_MAX_RESTARTS}회까지)"

        print(f"[백그라운드] {name} 죽음: {type(exc).__name__}: {exc} / {note}", flush=True)

        try:
            from run.services.webhook_logger import notify_error
            await notify_error(exc, context=f"백그라운드 작업: {name} — {note}")
        except Exception:
            pass  # 알림 실패가 되살리기를 막으면 안 된다

        if not give_up:
            try:
                loop.restart()
            except Exception as e:
                print(f"[백그라운드] {name} 되살리기 실패: {e}", flush=True)

    loop.error(_handler)

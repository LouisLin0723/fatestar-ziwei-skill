#!/usr/bin/env python3
"""FateStar Ziwei CLI — Zi Wei Dou Shu (紫微斗数) charting + 郑大钱 AI reading.

Thin client over the FateStar engine API:
  chart     GET  /api/ziwei              (free, anonymous)
  transits  GET  /api/ziwei?transits=1   (free)
  reading   POST /api/ziwei/reading       (paid, needs FSFSKey)
  doc       offline interface spec

Zero third-party deps (uses the standard-library urllib).
"""

import argparse
import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _load_env():
    """Load FATESTAR_API_KEY from a .env file next to the skill.

    Documented priority: --api_key > .env file > environment variable > anonymous.
    The .env value intentionally overrides an existing env var to match that order.
    utf-8-sig handles .env files saved by Windows Notepad with a BOM.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for env_path in [os.path.join(script_dir, ".env"), os.path.join(script_dir, "..", ".env")]:
        if os.path.isfile(env_path):
            with open(env_path, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip().lstrip(chr(0xFEFF))
                    value = value.strip().strip("\"'").strip()
                    if key and value:
                        os.environ[key] = value


_load_env()


# BEGIN GENERATED:CONSTANTS
DEFAULT_API_BASE = "https://www.fatestar.top"
CHART_PATH = "/api/ziwei"
READING_PATH = "/api/ziwei/reading"
CLIENT_ID = "skill/2.1.0"
# END GENERATED:CONSTANTS


def _api_base() -> str:
    return os.environ.get("FATESTAR_API_BASE", DEFAULT_API_BASE).rstrip("/")


def _build_birth_params(args) -> dict:
    """Map CLI flags to the engine's birth-param names (shared by chart/transits/reading)."""
    params = {
        "year": args.year,
        "month": args.month,
        "day": args.day,
        "hour": args.hour,
        "gender": args.gender,
        "calendarType": args.calendar,
    }
    if args.minute is not None:
        params["minute"] = args.minute
    if getattr(args, "leap", False):
        params["isLeapMonth"] = "true"
    if args.longitude is not None:
        params["longitude"] = args.longitude
    if args.tz is not None:
        params["timezoneOffset"] = args.tz
    return params


def _err_from(raw: str, status: int) -> int:
    """Print a structured API error to stderr; return exit code 1."""
    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        body = {}
    err = body.get("error", {}) if isinstance(body, dict) else {}
    code = err.get("code", f"HTTP_{status}")
    msg = err.get("message", "") or (raw[:500] if raw else f"HTTP {status}")
    print(f"API Error [{code}]: {msg}", file=sys.stderr)
    return 1


def _resolve_api_key(args) -> str:
    return (getattr(args, "api_key", "") or os.environ.get("FATESTAR_API_KEY", "")).strip()


def _get(path: str, query: dict, api_key: str = ""):
    url = _api_base() + path + "?" + urllib.parse.urlencode(query)
    headers = {"Accept": "application/json", "X-FateStar-Client": CLIENT_ID}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    return _send(req)


def _post(path: str, body: dict, api_key: str = ""):
    data = json.dumps(body).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-FateStar-Client": CLIENT_ID,
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(_api_base() + path, data=data, headers=headers, method="POST")
    return _send(req)


def _send(req):
    """Return (status, raw_text). Network failures exit(1)."""
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except urllib.error.URLError as e:
        print(f"Connection Error: unable to reach {_api_base()} ({e.reason})", file=sys.stderr)
        sys.exit(1)
    except TimeoutError:
        print("Timeout: the API request timed out.", file=sys.stderr)
        sys.exit(1)


def cmd_chart(args):
    """Free natal chart."""
    status, raw = _get(CHART_PATH, _build_birth_params(args), _resolve_api_key(args))
    if status != 200:
        sys.exit(_err_from(raw, status))
    print(raw)


def cmd_transits(args):
    """Free natal chart + 6 transit levels."""
    query = _build_birth_params(args)
    query["transits"] = "1"
    if args.target_year is not None:
        query["targetYear"] = args.target_year
    if args.target_month is not None:
        query["targetMonth"] = args.target_month
    if args.target_day is not None:
        query["targetDay"] = args.target_day
    if args.target_hour is not None:
        query["targetHour"] = args.target_hour
    status, raw = _get(CHART_PATH, query, _resolve_api_key(args))
    if status != 200:
        sys.exit(_err_from(raw, status))
    print(raw)


def cmd_reading(args):
    """Paid 郑大钱 reading. Needs an FSFSKey; degrades gracefully without one."""
    question = (args.question or "").strip()
    if not question:
        print("Error: --question is required for reading.", file=sys.stderr)
        sys.exit(1)

    api_key = _resolve_api_key(args)
    if not api_key:
        print(
            "郑大钱解读需要 FSFSKey（尚未配置）。\n"
            "请到 https://www.fatestar.top 注册免费会员 → 做新手任务领积分 →\n"
            "开发者中心创建 FSFSKey → 写进 .env (FATESTAR_API_KEY=) 或用 --api_key 传入。\n"
            "在此之前可用 `chart` 免费排盘，再由 Agent 自身模型解释。",
            file=sys.stderr,
        )
        sys.exit(2)

    body = _build_birth_params(args)
    body["question"] = question
    status, raw = _post(READING_PATH, body, api_key)

    try:
        resp = json.loads(raw)
    except json.JSONDecodeError:
        resp = {}

    if status == 200:
        data = resp.get("data", {})
        reading = data.get("reading", "")
        if not reading:
            print("郑大钱解读失败：空回复（未扣费），请重试。", file=sys.stderr)
            sys.exit(1)
        print(reading)
        used, after = data.get("creditsUsed"), data.get("balanceAfter")
        if used is not None or after is not None:
            print(f"\n---\n[积分] 本次扣除 {used}, 剩余 {after}", file=sys.stderr)
        return

    err = resp.get("error", {}) if isinstance(resp, dict) else {}
    if status == 401:
        print("Key 无效或已失效 (401)。请到 https://www.fatestar.top 开发者中心确认或重新申请 FSFSKey。", file=sys.stderr)
    elif status == 402:
        need, have = err.get("need"), err.get("have")
        print(
            f"积分不足 (402, 需 {need} / 有 {have}), 未扣费。\n"
            "请到 https://www.fatestar.top 充值，或等北京时间 21:00 免费重置（每日 3 积分）。\n"
            "现在可改用 `chart` 拿命盘数据 + Agent 自身模型解释兜底。",
            file=sys.stderr,
        )
    else:
        _err_from(raw, status)
    sys.exit(1)


# BEGIN GENERATED:DOC_SPEC
def _render_doc():
    _dir = os.path.dirname(os.path.abspath(__file__))
    _shared = os.path.join(_dir, "shared")
    with open(os.path.join(_shared, "doc_spec.md"), "r", encoding="utf-8") as _f:
        _tpl = _f.read()
    _tpl = _tpl.replace("{{LANG_NAME}}", "Python")
    _tpl = _tpl.replace("{{LANG_CODEBLOCK}}", "")
    _tpl = _tpl.replace("{{LANG_INVOKE}}", "python scripts/ziwei_cli.py")
    return _tpl
# END GENERATED:DOC_SPEC


def cmd_doc(args):
    print(_render_doc())


def _add_birth_args(p, with_targets=False, with_question=False):
    p.add_argument("--year", type=int, required=True, help="Birth year (1900-2100; lunar year when --calendar lunar)")
    p.add_argument("--month", type=int, required=True, help="Birth month 1-12")
    p.add_argument("--day", type=int, required=True, help="Birth day 1-31")
    p.add_argument("--hour", type=int, required=True, help="Birth hour 0-23 (24-hour clock, not a 时辰 branch)")
    p.add_argument("--gender", required=True, choices=["male", "female"], help="male / female")
    p.add_argument("--minute", type=int, default=None, help="Birth minute 0-59 (with --longitude for true solar time)")
    p.add_argument("--calendar", default="solar", choices=["solar", "lunar"], help="solar (default) / lunar")
    p.add_argument("--leap", action="store_true", help="Leap month (only with --calendar lunar)")
    p.add_argument("--longitude", type=float, default=None, help="Birth longitude (E +, W -); enables true-solar-time")
    p.add_argument("--tz", type=float, default=None, help="Timezone offset (UTC+8 = 8); use with --longitude")
    p.add_argument("--api_key", default="", help="Optional FSFSKey (identifies free calls; required for reading)")
    if with_targets:
        p.add_argument("--target-year", type=int, default=None, help="Annual target solar year (default: current year)")
        p.add_argument("--target-month", type=int, default=None, help="Monthly target lunar month 1-12")
        p.add_argument("--target-day", type=int, default=None, help="Daily target lunar day 1-30")
        p.add_argument("--target-hour", type=int, default=None, help="Hourly target hour 0-23")
    if with_question:
        p.add_argument("--question", help="The question for 郑大钱 (e.g. 看我今年事业运,该不该跳槽?)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ziwei",
        description=(
            "FateStar Ziwei CLI — Zi Wei Dou Shu (紫微斗数) charting + 郑大钱 AI reading.\n\n"
            "Charting (chart / transits) is free and anonymous. The 郑大钱 reading is paid\n"
            "(needs an FSFSKey). Powered by FateStar's self-built engine."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  ziwei chart --year 1990 --month 7 --day 23 --hour 8 --gender male\n"
            "  ziwei transits --year 1990 --month 7 --day 23 --hour 8 --gender male --target-year 2026\n"
            "  ziwei reading --year 1990 --month 7 --day 23 --hour 8 --gender male --question \"今年事业运?\"\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    chart_p = sub.add_parser("chart", help="Natal chart (本命盘, free, anonymous)", formatter_class=argparse.RawDescriptionHelpFormatter)
    _add_birth_args(chart_p)
    chart_p.set_defaults(func=cmd_chart)

    transits_p = sub.add_parser("transits", help="Natal chart + 6 transit levels (运限, free)", formatter_class=argparse.RawDescriptionHelpFormatter)
    _add_birth_args(transits_p, with_targets=True)
    transits_p.set_defaults(func=cmd_transits)

    reading_p = sub.add_parser("reading", help="郑大钱 AI reading (paid, needs FSFSKey)", formatter_class=argparse.RawDescriptionHelpFormatter)
    _add_birth_args(reading_p, with_question=True)
    reading_p.set_defaults(func=cmd_reading)

    doc_p = sub.add_parser("doc", help="Print AI-facing interface specification (offline)")
    doc_p.set_defaults(func=cmd_doc)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command is None:
        print(_render_doc())
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()

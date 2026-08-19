#!/usr/bin/env python3
"""
n8n execution budget checker.

Measures what an n8n instance is ALREADY committed to spending per month, so a new
scheduled/polling workflow can be sized against real remaining headroom instead of a guess.

    python3 budget-check.py --instance mr-n8n --days 7 --cap 2500

Credentials resolve in this order:
  1. --url / --key flags
  2. N8N_API_URL / N8N_API_KEY environment variables
  3. the named MCP server's env block in Claude Desktop's config

CAVEAT: n8n prunes execution history. This reads the RETAINED log only, which typically covers
~7 days. It is a run-RATE measurement, never a billing-period total. The n8n billing page is the
only authority on actual usage. The script reports its own coverage so you can judge the fit.
"""
import argparse, json, os, sys, urllib.parse, urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

CONFIG = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")


def resolve_creds(instance, url, key):
    if url and key:
        return url.rstrip("/"), key
    url = url or os.environ.get("N8N_API_URL")
    key = key or os.environ.get("N8N_API_KEY")
    if url and key:
        return url.rstrip("/"), key
    try:
        cfg = json.load(open(CONFIG))
        env = cfg["mcpServers"][instance]["env"]
        return env["N8N_API_URL"].rstrip("/"), env["N8N_API_KEY"]
    except Exception as e:
        sys.exit(f"Could not resolve credentials for '{instance}': {e}\n"
                 f"Pass --url/--key or set N8N_API_URL/N8N_API_KEY.")


def api(base, key, path, params=None):
    u = base + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(u, headers={"X-N8N-API-KEY": key, "accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def paginate(base, key, path, params=None, cap=200):
    out, cursor, pages = [], None, 0
    while pages < cap:
        p = dict(params or {})
        p["limit"] = 250
        if cursor:
            p["cursor"] = cursor
        d = api(base, key, path, p)
        out.extend(d.get("data", []))
        cursor = d.get("nextCursor")
        pages += 1
        if not cursor:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--instance", default="mr-n8n", help="MCP server name in Claude Desktop config")
    ap.add_argument("--days", type=int, default=7, help="full days of history to measure")
    ap.add_argument("--cap", type=int, default=2500, help="plan execution cap per month")
    ap.add_argument("--url"); ap.add_argument("--key")
    a = ap.parse_args()

    base, key = resolve_creds(a.instance, a.url, a.key)
    print(f"instance : {base}")

    execs = paginate(base, key, "/api/v1/executions")
    names = {w["id"]: w for w in paginate(base, key, "/api/v1/workflows")}
    if not execs:
        sys.exit("No executions retained — cannot measure a run rate.")

    # Only whole days: yesterday backwards. Today is partial and would understate the rate.
    end = datetime.now(timezone.utc).date() - timedelta(days=1)

    # Real coverage is the run of CONSECUTIVE days that actually carry executions, walking back
    # from `end`. Using the oldest timestamp instead is a trap: n8n prunes by count, so a handful
    # of year-old survivors make the log look far deeper than it is, and dividing a week of data
    # by a month understates the run rate ~4x -- silently, and in the dangerous direction.
    have = {e["startedAt"][:10] for e in execs if e.get("startedAt")}
    covered = 0
    while covered < a.days and (end - timedelta(days=covered)).isoformat() in have:
        covered += 1
    if covered == 0:
        sys.exit(f"No executions on {end.isoformat()} or earlier contiguous days — cannot measure a rate.")
    if covered < a.days:
        print(f"WARNING: retained log covers only {covered} contiguous full day(s), not {a.days}. "
              f"Measuring {covered}.")
        a.days = covered
    start = end - timedelta(days=a.days - 1)

    lo, hi = start.isoformat(), end.isoformat()
    win = [e for e in execs if lo <= (e.get("startedAt") or "")[:10] <= hi]
    print(f"window   : {lo} .. {hi}  ({a.days} full days, {len(win)} executions)")
    print(f"plan cap : {a.cap:,}/month\n")

    agg = defaultdict(Counter)
    for e in win:
        agg[e["workflowId"]]["n"] += 1
        agg[e["workflowId"]][e.get("status") or "?"] += 1

    print(f"{'/day':>7} {'/month':>8} {'%cap':>6} {'err':>5}  workflow")
    print("-" * 92)
    total = 0.0
    for wid, c in sorted(agg.items(), key=lambda kv: -kv[1]["n"]):
        per_day = c["n"] / a.days
        per_month = per_day * 30
        total += per_month
        w = names.get(wid, {})
        flag = "!" if per_month > a.cap * 0.25 else " "
        state = "ON " if w.get("active") else "off"
        print(f"{per_day:>7.1f} {per_month:>8.0f} {per_month/a.cap*100:>5.0f}%{flag}{c['error']:>5}  "
              f"[{state}] {w.get('name', '<deleted:'+wid+'>')}")
    print("-" * 92)

    # Forward commitment counts ACTIVE workflows only. A paused workflow spent money last week
    # but will not spend it next week -- conflating the two hides a fix that already landed.
    fwd = sum(c["n"] / a.days * 30 for wid, c in agg.items() if names.get(wid, {}).get("active"))
    pct = fwd / a.cap * 100
    print(f"{'':>7} {total:>8.0f} {total/a.cap*100:>5.0f}%   observed over the window (incl. paused)")
    print(f"{'':>7} {fwd:>8.0f} {pct:>5.0f}%   FORWARD RUN RATE (active workflows only)")
    head = a.cap - fwd
    print(f"{'':>7} {head:>8.0f} {head/a.cap*100:>5.0f}%   HEADROOM for new workflows")

    if fwd > 0:
        print(f"\nAt the forward rate the monthly quota lasts {a.cap/(fwd/30):.1f} days.")
    print()
    if pct > 100:
        print("VERDICT: OVER PLAN on active workflows alone. Cut or upgrade. Do not add anything.")
    elif pct > 80:
        print("VERDICT: >80% committed. Do not activate new scheduled work without a human decision.")
    elif pct > 50:
        print("VERDICT: 50-80% committed. Fine, but state the number in your handoff.")
    else:
        print("VERDICT: healthy headroom.")
    hogs = [w for w, c in agg.items()
            if (c["n"] / a.days * 30) > a.cap * 0.25 and names.get(w, {}).get("active")]
    if hogs:
        print(f"\n! {len(hogs)} ACTIVE workflow(s) each exceed 25% of the plan alone:")
        for w in hogs:
            print(f"    {names.get(w, {}).get('name', w)}")
    print("\nRun-rate measurement from the retained log. The n8n billing page is the authority "
          "on actual billed usage.")


if __name__ == "__main__":
    main()

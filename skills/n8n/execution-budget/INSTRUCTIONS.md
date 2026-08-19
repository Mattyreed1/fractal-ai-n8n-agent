---
name: n8n-execution-budget
description: Mandatory execution-cost gate for n8n workflows. Use BEFORE creating, scheduling, or activating any workflow with a time-based or polling trigger, when changing a schedule interval, when an instance approaches its execution quota, or when asked why an n8n plan ran out of executions. Covers the cost formula, the cadence cost table, the polling ladder, and the Schedule-vs-poll-trigger distinction.
---

# n8n Execution Budget Gate

**An n8n Cloud plan is metered in workflow executions per month. A schedule interval is not a
convenience setting — it is a purchase. This document is the gate that prices it before you buy.**

Plan caps (verified 2026-08-19 at https://n8n.io/pricing/): **Starter 2.5K/mo · Pro 10K/mo · Enterprise custom.**
Default assumption for Matty's instances is **Starter = 2,500/month** unless the billing page says otherwise.

---

## THE GATE (binding — no exceptions)

Before you **create**, **activate**, or **change the interval of** any workflow whose trigger is a
Schedule Trigger, Cron, or interval poll, you MUST state these four numbers out loud in your response:

```
1. runs/day        = active_minutes_per_day ÷ interval_minutes
2. runs/month      = runs/day × active_days_per_month   (30 for 24/7, ~22 for weekdays-only)
3. current committed rate of the instance   (run budget-check.py)
4. new total ÷ plan cap                     (as a percentage)
```

**Then apply the verdict:**

| New total vs cap | Verdict |
|---|---|
| **≤ 50%** | Ship it. |
| **50–80%** | Ship it, but say the number in your handoff so it is on the record. |
| **> 80%** | **STOP.** Do not activate. Surface the math and the cheaper options; let the human choose. |
| **A single workflow > 25% of cap** | **STOP.** No one workflow gets a quarter of the plan without an explicit decision. |

**Never activate a scheduled workflow without having run this arithmetic.** "It's just a small poller"
is exactly how a plan dies — see the incident at the bottom of this file.

---

## Cadence cost table (executions per month)

Look up the cell before you pick an interval. Bold cells exceed a 2,500 Starter plan **on their own**.

| Interval | 24/7 (30 d) | Work hrs 14h × 22 d | Business hrs 9h × 22 d |
|---|---|---|---|
| every 1 min | **43,200** | **18,480** | **11,880** |
| every 5 min | **8,640** | **3,696** | 2,376 |
| **every 10 min** | **4,320** | 1,848 | 1,188 |
| every 15 min | **2,880** | 1,232 | 792 |
| every 30 min | 1,440 | 616 | 396 |
| every hour | 720 | 308 | 198 |
| every 4 hours | 180 | 77 | 50 |
| daily | 30 | 22 | 22 |

**Read the bold row carefully: every 10 minutes, 24/7, is 4,320 executions — 173% of an entire
Starter plan spent on one workflow.** Every-15-min 24/7 (2,880) also exceeds it. On Starter, **nothing
runs more often than every 30 minutes 24/7**, and even that is 58% of the plan.

**Windowing is the cheapest lever you have.** Same 10-minute interval, restricted to business hours
on weekdays, costs 1,188 instead of 4,320 — a 73% cut for one config change. Ask: *does this actually
need to fire at 3am on a Sunday?* For anything keyed to a client's or colleague's working day, no.

---

## Schedule Trigger vs native poll trigger — the 100x difference

This is the highest-leverage fact in this document, and it is not obvious:

| Trigger | Costs an execution when there is NO new data? |
|---|---|
| **Schedule Trigger** → HTTP Request → "usually zero rows" | **YES — every single tick.** |
| **Native poll trigger** (Gmail Trigger, RSS, etc.) with nothing new | **NO — no execution record at all.** |

Measured on `mr-automations` 2026-08-19: workflow `idLvS6AY7sswn33g` runs a Gmail Trigger at
`pollTimes: everyMinute` and has been active since 2026-08-01 — `totalExecutions: 0`. Had each poll
billed, that would have been ~24,000 executions. Idle native polls are free.

**So: a "check if anything new arrived" workflow built as `Schedule Trigger → HTTP Request → IF` pays
full price on every empty check, while the same job on a native trigger node pays only when real work
exists.** For a low-event stream (a handful of hits a day), that is a 100x cost difference.

**Consequence for design:** if the source has a native n8n trigger node, use it. Reach for a Schedule
Trigger only when no native trigger exists — and then treat every tick as money.

⚠️ **Trade-off you must state when you choose a native poll trigger:** a broken poll trigger produces
**no execution record at all**, so the workflow sits there looking active and healthy while doing
nothing. A Schedule Trigger fails loudly. If you pick a native trigger, also say how its silence
will be detected (a heartbeat, a reconciler, a staleness check on `staticData.lastTimeChecked`).

---

## The polling ladder — prefer the highest rung that works

1. **Real push webhook from the source.** Cost ≈ 1 execution per real event. Always try this first.
2. **Native n8n trigger node** with built-in change detection (see the section above). Idle = free.
3. **Schedule Trigger at the coarsest cadence the SLA tolerates, windowed to the hours that matter.**
4. **Schedule Trigger, frequent, 24/7.** Requires explicit human sign-off plus the budget math above.

Before settling on rung 3 or 4, you must have written down *why* rungs 1 and 2 are unavailable. "The
vendor's HTTP action is a paid tier" and "there is no trigger node for this API" are real answers.
"I didn't check" is not.

**When you land on rung 3 or 4, ask what latency the human actually needs.** The gap between "I want
to know quickly" and "every 10 minutes forever" is usually 4x of budget nobody asked for. A 30-minute
alert that arrives is worth more than a 10-minute alert on a dead plan.

---

## Checking current headroom

`budget-check.py` (in this directory) measures what an instance is *already* committed to, so
you can size a new workflow against real remaining capacity rather than a guess:

```bash
python3 execution-budget/budget-check.py --instance mr-n8n --days 7 --cap 2500
```

It reads credentials from the Claude Desktop MCP config (or `N8N_API_URL` / `N8N_API_KEY`), pulls the
retained execution log, and prints per-workflow runs/day, projected monthly totals, the instance
total, and remaining headroom against the cap.

**Caveat, and it matters:** n8n prunes execution history, so the log covers only recent days
(typically ~7). Use only full days, and never present the retained log as a full billing-period
count — the billing page is the authority for actual usage. `--days` should not exceed the number of
complete days the log actually holds; the script reports its own coverage so you can tell.

---

## Reviewing an existing instance

Run these when an instance nears its cap, or on any n8n audit:

1. `budget-check.py` → rank workflows by projected monthly executions. The top 2 are almost always >80% of the total.
2. For each top workflow: is it on rung 1 or 2 of the ladder? If not, why not?
3. Is any 24/7 poller doing work that only matters during business hours?
4. Are there **active** workflows nobody needs any more? An abandoned 10-min poller costs the same as a loved one.
5. Check `staticData.lastTimeChecked` on native poll triggers for staleness (a silent death, per above).

---

## Incident that produced this rule (2026-08-18, `mr-automations`)

`mr-automations` hit 100% of its monthly executions on 2026-08-18 at 14:20Z and every workflow on the
instance stopped — including revenue paths (contract-signed, lead capture) that had nothing to do with
the cause.

Two workflows were **90% of all executions** (1,458 of 1,616 over seven days):

- `Tulum — Automation@ inbox → Discord #alerts` — Schedule Trigger, **every 10 min, 24/7** = 144/day = **4,320/month**, on a 2,500 plan.
- `Tulum — Project folder ready → notify` — every 10 min but **windowed to weekday work hours** = 90/day ≈ 1,980/month.

The instance had been running ~25 executions/day before these were added. Two workflows built eleven
days apart took it to ~6,900/month — **2.7x the plan**, which converts to: *the monthly quota now
lasts 11 days.*

**Three lessons, each now encoded above:**

1. **The same author windowed one workflow and not the other, days apart.** The build spec for the
   windowed one even says *"Business-hours cron keeps n8n execution count sane."* The discipline
   existed and still did not transfer to the next workflow. **A convention that lives only in one
   engineer's head is not a control — that is why this is a gate with arithmetic, not a style note.**
2. **Nobody ever multiplied.** `every 10 min` reads as small and prices at 4,320/month. The cost is
   invisible in the config UI and obvious the moment you multiply. **Always convert the interval into
   a monthly number and into a percentage of the plan.**
3. **Blast radius is instance-wide, not workflow-wide.** A quota is a shared resource: one careless
   poller silently took down contract signing and lead capture. **Budget the instance, not the workflow.**

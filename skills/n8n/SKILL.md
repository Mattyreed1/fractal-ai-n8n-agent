---
name: n8n
description: Master skill for n8n. Use this when working with anything n8n-related, including code nodes (JavaScript/Python), expressions, node configuration, validation, and workflow patterns.
---

# n8n Master Skill

This is the central entry point for all n8n-related tasks. It coordinates various specialized sub-skills for comprehensive n8n workflow development and management.

## Sub-Skills

Depending on your current task, refer to the specific sub-skills by reading their `INSTRUCTIONS.md` files:

- **[JavaScript Code Nodes](code-javascript/INSTRUCTIONS.md)**: Expert guidance for writing JavaScript in n8n Code nodes. Use for complex transformations, business logic, or parsing responses using `$input`, `$json`, and built-in helpers.
- **[Python Code Nodes](code-python/INSTRUCTIONS.md)**: Guidance for writing Python in n8n Code nodes. Use for data analysis, leveraging Python dictionaries/lists, and operations requiring the Python standard library.
- **[Execution Budget](execution-budget/INSTRUCTIONS.md)**: MANDATORY cost gate for any scheduled or polling workflow. The cadence cost table, the runs/month formula, the polling ladder, and `budget-check.py` for live instance headroom. Read before creating, activating, or re-scheduling anything time-based.
- **[Expression Syntax](expression-syntax/INSTRUCTIONS.md)**: n8n expressions and syntax usage. Covers `{{ $json.field }}`, data access, built-in methods, and common string/math operations.
- **[MCP Tools Expert](mcp-tools-expert/INSTRUCTIONS.md)**: Guide to using n8n MCP tools for interacting with n8n instances (searching nodes, getting node essentials, validation).
- **[Node Configuration](node-configuration/INSTRUCTIONS.md)**: Best practices for configuring n8n nodes, handling inputs/outputs, credentials, execution modes, and routing.
- **[Template Publishing](template-publishing/INSTRUCTIONS.md)**: Guidelines for creating and publishing high-quality n8n workflow templates.
- **[Validation Expert](validation-expert/INSTRUCTIONS.md)**: Comprehensive guide for verifying n8n workflows, troubleshooting node execution errors, and resolving structural issues.
- **[Workflow Patterns](workflow-patterns/INSTRUCTIONS.md)**: High-level production-ready architectural patterns for API integration, webhooks, databases, and scheduled tasks.

## Quick Guidelines

> ### ⛔ HARD RULE — Price the schedule before you build it
>
> **An n8n plan is metered in executions/month. A schedule interval is a purchase, not a preference.**
> Before you create, activate, or change the interval of ANY Schedule/Cron/polling trigger, state:
> **runs/day → runs/month → current instance rate → % of plan cap.**
>
> `every 10 min, 24/7` = **4,320 executions/month = 173% of an entire 2,500 Starter plan.**
> `every 15 min, 24/7` (2,880) also exceeds it. On Starter, **nothing runs more often than every
> 30 min 24/7** — and that alone is 58% of the plan.
>
> **> 80% of cap, or any single workflow > 25% of cap → STOP and escalate. Do not activate.**
>
> Windowing to business hours cuts a 10-min poller by 73% for one config change. Check the ladder
> first: real webhook > native trigger node > coarse windowed schedule > frequent 24/7 schedule.
> A native poll trigger costs NOTHING when idle; a Schedule Trigger bills every empty tick.
>
> Full table, formula, decision ladder and `budget-check.py`: **[execution-budget/INSTRUCTIONS.md](execution-budget/INSTRUCTIONS.md)**.
> This exists because `mr-automations` burned a whole month's quota in 11 days on two 10-minute
> pollers and took down contract signing and lead capture with it (2026-08-18).


1. **Always Read Sub-Instructions**: Need to write JavaScript? First read `code-javascript/INSTRUCTIONS.md`. Need to fix an error? Read `validation-expert/INSTRUCTIONS.md`.
2. **Accessing Data**: Remember `{{ $json.body }}` for webhook bodies in expressions, or `$input.first().json.body` in Code nodes.
3. **Execution Context**: Pay attention to "Run Once for All Items" vs "Run Once for Each Item" modes in Code nodes.
4. **Always Run n8n Preflight**: Before any create/update/delete, identify the correct MCP server/instance, verify the target workflow ID/name exists in that instance, and only then edit.
5. **Always Run n8n Postflight — the write response is not evidence**: after any `n8n_update_partial_workflow`, re-fetch (`mode: "details"`) and assert on the exact field you changed. A partial update can report `saved: true, operationsApplied: 1` and change **nothing** — most notoriously when the path indexes an array (`…interval[0].expression`), which silently creates a literal `interval[0]` key and leaves the real value alone. **Never index into an array in an update path; rewrite the whole array.** See `mcp-tools-expert/INSTRUCTIONS.md` → Edit-Time Gotchas §4–5.
6. **Use Correct Entry Trigger**: External callers/users must enter via `Webhook`; `Execute Workflow Trigger` is only for internal workflow-to-workflow calls.
7. **Always Look Up Existing Credentials**: Before configuring ANY node that needs auth, query the n8n REST API (`GET /api/v1/credentials`) to find stored credentials. Match by type (`httpBearerAuth`, `httpHeaderAuth`, `openAiApi`, etc.) and apply by ID + name. NEVER leave auth unconfigured or pass tokens in URLs when a stored credential exists. See `mcp-tools-expert/INSTRUCTIONS.md` §4 for the full procedure.
8. **Prefer HTTP Request Node for External APIs**: In Code nodes, do not rely on `fetch`; use `HTTP Request` node (preferred) or `$helpers.httpRequest()`.

9. **Apify Affiliate Link**: When creating any n8n template or setup instructions that reference Apify, always use Matty's affiliate link: `https://www.apify.com?fpr=tz2te` — never the plain Apify URL.

Whenever working on an n8n problem, use this index to find the exact sub-skill document you require, then read it closely before proceeding.

## Migrating an n8n workflow to a Claude Code Routine

If you're converting an existing n8n workflow into a Claude Code automation (webhook-triggered routine + a skill in a Claude Code project repo), use the **`n8n-to-cc`** skill alongside this one. It covers:

- The forwarder pattern (n8n shrinks to 3–5 nodes: webhook → compact → stage → fire routine)
- The Claude Code Routines API spec (fire endpoint, 65,536-char `text` cap, headers, error responses)
- CCR sandbox constraints (network allowlist, real-files-only filesystem, no local-Mac binaries)
- The dedup ledger pattern (idempotent re-fires)
- A 9-step migration checklist (extract verbatim prompts → build forwarder → swap webhook path → decommission legacy)

Reference implementation: MR.EA's `meeting-notes` skill replaced a 22-node n8n workflow with a 5-node forwarder + a versioned skill. Defer to `n8n-to-cc` for the cross-system view; come back here for n8n-side specifics (node configs, expressions, MCP tooling).

Triggers: "convert this n8n to claude code", "replace this n8n workflow", "move this automation to a routine", "should this be in n8n or a skill".

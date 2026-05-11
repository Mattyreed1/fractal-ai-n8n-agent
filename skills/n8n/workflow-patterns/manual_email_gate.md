# Pattern: Manual Email Approval Gate (Wait-on-Webhook)

Pause a workflow mid-execution, email a human for approval, and continue (or stop) based on which button they clicked. Built and proven in `Quo → Notion Sync` (Blackboard Studio, May 2026).

## When to use

- A pipeline shouldn't run end-to-end without human judgement (e.g. "is this call worth logging?")
- The human is async — can't be on a video call to click through
- Reviewer is the user's own email, not a Slack/Discord workspace
- Decision is binary (approve / skip)

For multi-option decisions, use the same pattern but expand the branching after the IF node. For free-text response, use the Outlook `sendAndWait` with `responseType: freeText` (only works for delegated OAuth, not app-only — see below).

## Architecture

```
Quo Webhook (trigger, responseMode: responseNode)
  → Ack Quo (Respond to Webhook, "ok" 200)         ← so Quo doesn't time out
  → Normalize Payload (Code)
  → Call ≥ 1 min? (IF, optional pre-filter)
  → Build Approval Summary (Code, includes resumeUrl)
  → Send Approval Email (HTTP Request → Graph sendMail)
  → Wait for Blake (Wait, resume: webhook, responseMode: responseNode, timeout: 7d)
  → Approved? (IF, checks $json.query.action === 'approve')
       ├── true → Logged Confirmation Page (Respond to Webhook, HTML)
       │            → Restore Call Data (Code) → … rest of pipeline
       └── false → Skipped Confirmation Page (Respond to Webhook, HTML) → end
```

## Key insights from building this

### 1. `$execution.resumeUrl` is pre-computed and globally available

You can reference it in any node, including BEFORE the Wait node. The URL is deterministic from the execution ID. So the email-building code (which runs before Wait pauses) can safely embed it.

```javascript
const resumeUrl = $execution.resumeUrl;
const sep = resumeUrl.indexOf('?') >= 0 ? '&' : '?';
const approveUrl = resumeUrl + sep + 'action=approve';
const skipUrl    = resumeUrl + sep + 'action=skip';
```

The resume URL already contains `?signature=...` for security, so always append with `&`.

### 2. Wait node `responseData` does NOT work in v1.1

The docs say `options.responseData` (string) sets the response body for `responseMode: onReceived`. In practice (n8n v2.17.5, Wait v1.1), this is silently ignored — the resume URL always returns `{"message":"Workflow was started"}` regardless of what you set.

Workaround: use `responseMode: responseNode` and add a `Respond to Webhook` node after Wait. This DOES work.

### 3. `Respond to Webhook` validation is strict

n8n won't save if there's a `Respond to Webhook` node that isn't bound to a webhook with `responseMode: responseNode`. **Every webhook in the workflow that expects a custom response must use `responseNode` mode, AND each must have its own Respond to Webhook node downstream.**

For a workflow with a webhook trigger + a Wait-on-webhook:
- Trigger webhook: `responseMode: responseNode` → followed by an immediate "Ack" Respond node returning 200
- Wait node: `responseMode: responseNode` → followed by a "Confirmation" Respond node returning HTML

The Respond nodes bind to the most recent webhook context, so this works.

### 4. Per-branch confirmation pages

If approve and skip should show DIFFERENT pages, split BEFORE the response. Put the IF (`Approved?`) directly after Wait, then put a separate Respond to Webhook on each branch:

```
Wait → Approved? → (true) → Logged Page → next node
                 → (false) → Skipped Page → end
```

Each Respond to Webhook returns its own HTML. Then the Approve path continues processing (the response is sent to the browser immediately when Respond fires, then the workflow keeps running).

### 5. Email content & "Restore Call Data" node

After Wait resumes, `$json` is the webhook request data (headers, query params), NOT the original payload. Downstream nodes that reference `$json.fieldFromUpstream` will break.

Fix: add a tiny Code node right after the IF's true branch that re-fetches the original payload:

```javascript
return [{ json: $('Normalize Payload').item.json }];
```

Now downstream nodes see the original data structure as if Wait wasn't there.

### 6. Email body — embed the buttons inline

Don't link to a separate page. The email IS the gate. Build the HTML in a Code node, then pass through to `HTTP Request → Graph sendMail` (or whichever send mechanism).

Button styling that survives Gmail/Outlook/Zoho:

```html
<a href="<approveUrl>" style="display:inline-block;background:#0066cc;color:#ffffff;
   padding:14px 28px;border-radius:6px;text-decoration:none;font-weight:600;
   margin:0 8px;font-size:15px;">Log Meeting in Notion</a>
```

Avoid `<button>` — most email clients strip JS-related elements and inconsistent default styling.

## Sending mechanism choice

| Sender | When |
|---|---|
| **Microsoft Outlook `sendAndWait`** | Delegated OAuth (user signs in). Single node handles email + approval pause + buttons. Cleanest UX. Requires `microsoftOutlookOAuth2Api` cred type, which means a real user authorizes their mailbox. |
| **HTTP Request → Graph `/users/{UPN}/sendMail`** | App-only auth (Mail.Send Application permission). Use when you want a service mailbox to send, not a user. Requires building the email payload manually and pairing with a Wait node. The pattern documented in this file. |
| **Generic SMTP (Email Send node)** | Any provider with SMTP (Zoho, Postmark, SendGrid). No OAuth setup. Pair with Wait node same as Graph approach. |

For Microsoft Graph app-only auth setup, see `ms-admin/service-account-setup.md` in the MR.EA skills.

## Known limitations

- **App-only sendMail doesn't honor display names.** Microsoft Graph ignores both the `from.emailAddress.name` field in the payload AND the mailbox's Exchange `DisplayName`. The `From:` header ends up as just `<smtp_address>`. If pretty-from matters, you need delegated OAuth (user signs in) instead of app-only.
- **Resume URL contains a signature** — anyone with the URL can resume the workflow. Don't leak resume URLs in shared logs or screenshots.
- **No native timeout-vs-click distinction** — when the Wait node hits its `limitWaitTime` deadline without a click, it resumes with the same `$json` shape (no query params). The Approved? IF treats this as "false" by default — meaning a timed-out workflow ends without logging, which is usually what you want.

## Reference implementation

See: [Quo → Notion Sync](https://blackboardstudio.app.n8n.cloud/workflow/Yhd7zcI85k3MIY4n)

Built May 11, 2026. Sending account: `blackboardbot@blackboardstudiocorp.com` (Microsoft shared mailbox). Reviewer: `buhing@blackboardstudiocorp.com`.

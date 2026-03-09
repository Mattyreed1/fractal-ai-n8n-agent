---
name: n8n-template-publishing
description: Prepare n8n workflow templates for publishing on the n8n marketplace. Use when publishing workflows, preparing templates, adding documentation to workflows, creating workflow descriptions, or getting workflows ready for sharing.
---

# n8n Template Publishing

Prepare n8n workflows for publishing on the n8n template marketplace.

---

## Publishing Checklist

Follow this checklist before publishing ANY template:

### 1. Security Audit
- [ ] Remove all hardcoded API keys, tokens, and secrets
- [ ] Replace sensitive values with placeholder text (e.g., `YOUR_API_KEY`)
- [ ] Check Code nodes for embedded credentials
- [ ] Verify no PII or internal URLs remain
- [ ] Strip credentials from nodes (use n8n credential system)

### 2. Documentation (Sticky Notes)
- [ ] Add section headers for each workflow area
- [ ] Add setup guide sticky note
- [ ] Add Fractal AI branding sticky note
- [ ] Keep all notes concise and scannable

### 3. Metadata
- [ ] Write concise, descriptive title
- [ ] Write detailed markdown description
- [ ] Write short sales blurb summary
- [ ] Present ALL metadata in fenced code blocks for easy copy/paste

### 4. Final Review
- [ ] Test workflow end-to-end
- [ ] Validate with `n8n_validate_workflow`
- [ ] Check sticky note positioning (not overlapping nodes)

---

## Security Audit

### What to Remove

**Hardcoded Secrets** (CRITICAL):
```javascript
// ❌ NEVER publish with these
const apiKey = "sk-abc123...";
const token = "ghp_xxxxxxxxxxxx";
const password = "mypassword123";

// ✅ Use placeholders or credential references
const apiKey = "YOUR_OPENAI_API_KEY";
// Or better: Use n8n credentials system
```

**Common Locations to Check**:
- Code node JavaScript/Python
- HTTP Request headers and body
- Set node field values
- Expression fields with inline secrets
- Webhook URLs with tokens

**Search Patterns**:
```
sk-          # OpenAI keys
ghp_         # GitHub tokens
xoxb-        # Slack tokens
AKIA         # AWS access keys
Bearer       # Auth tokens
password     # Passwords
secret       # Secret values
api_key      # API keys
token        # Tokens
```

### Credential Handling

**Before Publishing**:
1. Remove credential references from nodes
2. Document required credentials in setup guide
3. Use generic credential names in instructions

```markdown
## Required Credentials
- OpenAI API (for GPT-4 calls)
- Google Sheets OAuth2 (for data storage)
- Slack OAuth2 (for notifications)
```

---

## Sticky Note Documentation

### Section Headers

Add sticky notes with **bold headings** to label workflow sections:

**Format**:
```
## [Section Name]
Brief description of what this section does.
```

**Common Sections**:
- `## Trigger` - How the workflow starts
- `## Data Fetch` - Where data comes from
- `## Transform` - Data processing steps
- `## AI Processing` - AI/LLM operations
- `## Output` - Where results go
- `## Error Handling` - Error recovery logic

**Example Section Notes**:

```
## Webhook Trigger
Receives POST requests from external systems.
Expects JSON body with `email` and `message` fields.
```

```
## Data Enrichment
Fetches additional user data from CRM.
Merges with incoming webhook payload.
```

```
## AI Classification
Uses GPT-4 to categorize the message.
Returns: priority (high/medium/low), category, summary.
```

### Setup Guide Sticky Note

**Position**: Top-left of workflow canvas (visible first)

**Template**:
```markdown
## Setup Guide

### 1. Credentials Required
- [Service 1]: [Brief description]
- [Service 2]: [Brief description]

### 2. Configuration
- [Step 1]
- [Step 2]

### 3. Test
- [How to test the workflow]

### Resources
- [Link 1](URL)
- [Link 2](URL)
```

**Example**:
```markdown
## Setup Guide

### 1. Credentials Required
- **OpenAI API**: For GPT-4 fine-tuning
- **Google Sheets OAuth2**: For training data access
- **Airtable** (optional): Alternative data source

### 2. Configuration
1. Copy the [JSONL Template Sheet](https://docs.google.com/spreadsheets/d/1DvZNQKWKztvPcArkMuviUZ0tsJVw_4WiykFMI1yMfNI)
2. Add your training examples (systemPrompt, userPrompt, assistantResponse)
3. Mark rows as Ready = TRUE

### 3. Test
Run manually with a few examples marked Ready.
Check OpenAI dashboard for fine-tune job status.

### Resources
- [OpenAI Fine-Tuning Guide](https://platform.openai.com/docs/guides/fine-tuning)
- [n8n HTTP Request Docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
```

### Fractal AI Branding Sticky Note

**Position**: Bottom-right of workflow canvas

**Template**:
```markdown
## Fractal AI

**Automate the Impossible**

Built by Fractal AI - Intelligent automation solutions.

🔗 [Twitter/X](https://x.com/YOUR_HANDLE)
🔗 [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)
```

**Sticky Note Settings**:
- Color: Brand color (if available) or default
- Width: ~250px (compact but readable)

---

## Output Formatting Rule

**CRITICAL**: When presenting metadata to the user (title, description, sales blurb), ALWAYS wrap each piece in a fenced code block (triple backticks) so the user can copy/paste directly. Use `markdown` language tag for the description block.

**Example output format**:

~~~
### Title
```
Client Work Approval (TIG) Pipeline — Notion + AI → Google Sheets
```

### Sales Blurb
```
Automate monthly client work approval documents from Notion...
```

### Description
```markdown
# Client Work Approval (TIG) Pipeline

## Who is this for?
...
```
~~~

Never present metadata as bare text in the conversation. Always use code blocks.

---

## Workflow Title

### Guidelines

- **Length**: 50-80 characters ideal
- **Format**: `[Action] + [Source/Target] + [Purpose]`
- **Be specific**: What does it DO?
- **Include key services**: Help discoverability

### Title Patterns

```
[Action] [Data] from [Source] to [Destination]
[Action] [Thing] with [Tool/Service]
[Automated Action] for [Use Case]
```

### Examples

**Good Titles**:
- `GPT Fine-Tuning Pipeline (Google Sheets → OpenAI)`
- `Slack Standup Bot with AI Summaries`
- `Webhook to Notion Database with Email Notification`
- `Daily Sales Report from Stripe to Slack`
- `GitHub Issue Triage with GPT-4 Classification`

**Bad Titles**:
- `My Workflow` (not descriptive)
- `Automation` (too vague)
- `Slack Bot` (what does it do?)
- `Really Cool AI Thing That Does Lots of Stuff` (too long, not specific)

---

## Workflow Description (Markdown)

### Structure

Every description should follow this structure:

```markdown
# [Workflow Title]

## Who is this for?
[1-2 sentences describing the target user]

---

## What problem does it solve?
[2-3 sentences on the pain point this addresses]

---

## How it works

| # | Node | Purpose |
|---|------|---------|
| 1 | **[Node Name]** | [What it does] |
| 2 | **[Node Name]** | [What it does] |
| ... | ... | ... |

---

## Setup steps

1. **[Step Category]**
   * [Sub-step]
   * [Sub-step]

2. **[Step Category]**
   * [Sub-step]

---

## Resources

* [Resource Name](URL)
* [Resource Name](URL)

---

## Extending the flow

* **[Extension idea]** – [Brief description]
* **[Extension idea]** – [Brief description]

[Closing one-liner]
```

### Section Guidelines

**Who is this for?**
- Be specific about the user persona
- Mention skill level if relevant
- Include tool/service context

```markdown
## Who is this for?
Anyone curating **before/after** text examples in a spreadsheet and wanting
a push-button path to a fine-tuned GPT model—without touching curl.
```

**What problem does it solve?**
- State the pain point clearly
- Be concrete about manual steps eliminated
- Show the value proposition

```markdown
## What problem does it solve?
Manually downloading CSVs, converting to JSONL, uploading, and polling OpenAI is a slog.
This flow automates the whole loop: grab examples, build the file, start the fine-tune,
then log the resulting model ID back for reuse.
```

**How it works (Node Table)**
- Number each step
- Bold the node names
- Keep purposes to one line
- Note disabled/optional nodes

```markdown
| # | Node | Purpose |
|---|------|---------|
| 1 | **Schedule Trigger** | Runs weekly by default (change as needed). |
| 2a | **Get Examples from Sheet** | Pulls rows where `Ready = TRUE`. |
| 2b | **Get Examples from Airtable** *(disabled)* | Alternate source for Airtable users. |
| 3 | **Create JSONL File** (Code) | Converts examples to chat-format JSONL. |
```

**Setup steps**
- Group by category (Credentials, Configuration, Testing)
- Use bullet points for sub-steps
- Include exact field names and values
- Link to external resources

**Resources**
- Official documentation first
- Related tutorials
- Template files (Google Sheets, etc.)

**Extending the flow**
- Suggest 2-3 natural extensions
- Keep ideas actionable
- End with a punchy one-liner

---

## Sales Blurb Summary

### Purpose
Short, punchy description for marketplace listing preview.

### Guidelines
- **Length**: 1-3 sentences (under 200 characters ideal)
- **Focus**: Problem solved + key benefit
- **Tone**: Active, benefit-driven

### Template
```
[Action verb] [what] from [source] to [destination].
[Key benefit in one phrase].
```

### Examples

**Good Blurbs**:
```
Automate GPT fine-tuning from spreadsheet examples.
No JSONL wrangling, no manual uploads—just mark rows Ready and go.
```

```
Turn Slack messages into Notion tasks with AI categorization.
Smart prioritization, zero manual sorting.
```

```
Daily sales digest from Stripe to Slack.
Wake up to revenue insights, not dashboard hunting.
```

**Bad Blurbs**:
```
This workflow does automation stuff with AI. (vague)
```
```
A comprehensive solution for... (corporate speak)
```

---

## Sticky Note Positioning

### Layout Guidelines

```
┌─────────────────────────────────────────────────────────┐
│  📝 Setup Guide          [Trigger]──[Node]──[Node]      │
│  (top-left)                  │                          │
│                              ▼                          │
│                         📝 Section                      │
│                         Header                          │
│                              │                          │
│                         [Node]──[Node]                  │
│                              │                          │
│                              ▼                          │
│                         [Output]                        │
│                                                         │
│                                         📝 Fractal AI   │
│                                         (bottom-right)  │
└─────────────────────────────────────────────────────────┘
```

### Positioning Rules

1. **Setup Guide**: Top-left, visible on workflow open
2. **Section Headers**: Above or beside the section they describe
3. **Branding**: Bottom-right, out of the main flow
4. **No Overlap**: Sticky notes should not cover nodes
5. **Consistent Spacing**: ~50-100px gap between notes and nodes

### Sticky Note Dimensions

- **Setup Guide**: Wider (400-500px) to fit content
- **Section Headers**: Compact (200-300px)
- **Branding**: Fixed width (~250px)

---

## Complete Example

### Title
```
Basic GPT Fine-Tuning Flow (Google Sheets / Airtable → OpenAI)
```

### Sales Blurb
```
Automate GPT fine-tuning from spreadsheet examples.
No JSONL wrangling, no manual uploads—just mark rows Ready and go.
```

### Description
See the example provided in the skill activation context for full markdown template.

### Sticky Notes

**Setup Guide** (top-left):
```markdown
## Setup Guide

### 1. Credentials Required
- **OpenAI API**: For fine-tuning jobs
- **Google Sheets OAuth2**: For training data
- **Airtable** (optional): Alternative source

### 2. Configuration
1. Copy the [JSONL Template Sheet](URL)
2. Add training examples
3. Mark Ready = TRUE

### 3. Resources
- [OpenAI Fine-Tuning](https://platform.openai.com/docs/guides/fine-tuning)
- [Google Sheets API](https://developers.google.com/sheets/api)
```

**Section Headers**:
```markdown
## Data Source
Fetches training examples from Google Sheets or Airtable.
Only rows with Ready = TRUE are included.
```

```markdown
## JSONL Processing
Converts examples to chat-format JSONL.
Splits 80/20 into training and validation sets.
```

```markdown
## Fine-Tune Job
Uploads file and starts OpenAI fine-tune.
Polls until job completes, then logs model ID.
```

**Branding** (bottom-right):
```markdown
## Fractal AI

**Automate the Impossible**

🔗 [Twitter/X](https://x.com/FractalAI)
🔗 [LinkedIn](https://linkedin.com/company/fractal-ai)
```

---

## MCP Tools for Publishing

Use these n8n-mcp tools during the publishing process:

### Validation
```javascript
// Validate workflow before publishing
n8n_validate_workflow({ id: "workflow-id" })

// Check for common issues
validate_workflow({
  workflow: workflowJson,
  options: { profile: "strict" }
})
```

### Get Workflow for Review
```javascript
// Get full workflow to review
n8n_get_workflow({ id: "workflow-id", mode: "full" })

// Export for inspection
n8n_get_workflow({ id: "workflow-id", mode: "details" })
```

### Update Workflow
```javascript
// Add sticky notes via partial update
n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [
    {
      type: "addNode",
      node: {
        type: "n8n-nodes-base.stickyNote",
        name: "Setup Guide",
        parameters: { content: "## Setup Guide\n..." },
        position: [50, 50]
      }
    }
  ]
})
```

---

## Pre-Publish Validation

### Security Check Script

Run this mental checklist:

```
□ Search Code nodes for: apiKey, token, secret, password, Bearer
□ Search HTTP Request nodes for hardcoded auth headers
□ Search Set nodes for sensitive field values
□ Check webhook URLs for embedded tokens
□ Verify no internal/private URLs remain
□ Confirm all credentials use n8n credential system
```

### Documentation Check

```
□ Setup guide sticky note present and complete
□ Section headers for all major workflow areas
□ Branding sticky note in place
□ No overlapping sticky notes and nodes
□ Title is descriptive (50-80 chars)
□ Description follows markdown template
□ Sales blurb is punchy (<200 chars)
```

### Functional Check

```
□ Workflow executes successfully end-to-end
□ Error handling covers failure scenarios
□ All nodes validated with n8n_validate_workflow
□ Disabled nodes are clearly marked as optional
□ Default values are sensible for most users
```

---

## Summary

**Publishing a template requires**:

1. **Security**: Remove ALL secrets and credentials
2. **Documentation**: Add sticky notes (setup guide, sections, branding)
3. **Metadata**: Title, description, sales blurb
4. **Validation**: Test and validate before publishing

**Key Files to Generate**:
- Sticky note content (setup guide, sections, branding)
- Workflow title
- Markdown description (full template)
- Sales blurb (short summary)

**Quality Bar**:
- Would a stranger understand how to use this?
- Are all secrets removed?
- Does the workflow actually work?
- Is the documentation scannable and helpful?

---

## Related Skills

- **n8n Workflow Patterns** - Build the workflow correctly first
- **n8n Validation Expert** - Validate before publishing
- **n8n MCP Tools Expert** - Use tools for workflow updates

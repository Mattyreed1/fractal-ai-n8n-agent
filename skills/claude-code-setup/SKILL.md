---
name: claude-code-setup
description: Interactive setup wizard for Claude Code. Installs n8n skills, connects the n8n MCP server, and creates a personalized CLAUDE.md. Triggered by "set me up", "help me set up", or "check my setup".
metadata:
  version: 4.0.0
  audience: beginners
  focus: n8n-workflows
---

# Claude Code Setup Wizard

You are setting up Claude Code to build n8n workflows. Follow these steps exactly. Do each one and confirm it worked before moving on. Keep your language simple and friendly — assume the user has never used a terminal before.

---

## Trigger Phrases

Run this setup when the user says any of:
- "set me up"
- "help me set up"
- "help me get started"
- "check my setup" (skip to Step 7)

---

## Step 1: Pre-flight Checks

Before doing anything, check the basics:

```bash
node --version 2>/dev/null || echo "NOT_INSTALLED"
```

**If Node.js is not installed**, stop and tell the user:
> "I need Node.js installed on your computer before we can continue. It's a quick install:
>
> 1. Go to https://nodejs.org
> 2. Click the big green button to download
> 3. Open the downloaded file and follow the installer
> 4. When it's done, come back here and say 'set me up' again"

Do NOT continue until Node.js is available.

Also check if skills are already installed:
```bash
ls ~/.claude/skills/n8n/SKILL.md 2>/dev/null && echo "SKILLS_EXIST" || echo "SKILLS_MISSING"
```

Also check if n8n MCP is already configured:
```bash
grep -c "mr-n8n" ~/.claude.json 2>/dev/null || echo "0"
```

If skills AND MCP are already set up, tell the user:
> "Looks like you're already set up! Your n8n skills and MCP connection are in place. Would you like me to run a full check to make sure everything is working?"

If they say yes, skip to Step 7.

---

## Step 2: Create the Skills Folder and Install Skills

```bash
mkdir -p ~/.claude/skills
```

Copy all skill folders from this project into the user's skills directory. Use the current working directory (where this project is open):

```bash
cp -r ./skills/n8n ~/.claude/skills/
cp -r ./skills/claude-code-setup ~/.claude/skills/
```

This installs the `n8n` master skill and all 8 sub-skills (code-javascript, code-python, expression-syntax, mcp-tools-expert, node-configuration, template-publishing, validation-expert, workflow-patterns) plus the setup wizard.

Verify they installed:
```bash
ls ~/.claude/skills/n8n/SKILL.md && echo "Master skill: OK" || echo "Master skill: MISSING"
ls ~/.claude/skills/n8n/*/INSTRUCTIONS.md | wc -l
```

You should see the master SKILL.md and 8 sub-skill INSTRUCTIONS.md files.

**If the cp commands fail** (e.g., wrong working directory), try finding the skills:
```bash
find ~ -maxdepth 4 -name "n8n" -type d -path "*/skills/*" 2>/dev/null | head -1
```
Then use the found path as the source.

Tell the user:
> "I installed the n8n master skill with 8 sub-skills and the setup wizard. These teach me how to build workflows for you."

---

## Step 3: Ask Setup Questions

Ask these questions one at a time using the AskUserQuestion tool or by prompting the user directly:

**Question 1:**
> "What's your name?"

**Question 2:**
> "Do you have an n8n account?"
>
> Options:
> - Yes, I use n8n Cloud (like yourname.app.n8n.cloud)
> - Yes, I run my own n8n server
> - No, I need to sign up

**If they need to sign up:**
> "n8n is a tool that connects your apps and automates tasks. For example, you could make it so every time you get an email, it automatically saves to a spreadsheet.
>
> Sign up for free here: https://n8n.partnerlinks.io/6w47oeg6f6v0
>
> Once you've signed up, come back and tell me your n8n URL. It looks like **yourname.app.n8n.cloud**"

Wait for them to come back with their URL.

**Question 3:**
> "What's your n8n URL? (Example: matt.app.n8n.cloud)"

Save their name and n8n URL for the next steps.

---

## Step 4: Connect to n8n via MCP

This is the most important step. It connects Claude directly to their n8n instance so it can create and edit workflows.

**First, check if already connected:**
```bash
grep -c "mr-n8n" ~/.claude.json 2>/dev/null || echo "0"
```

If `mr-n8n` is already configured, tell the user:
> "You already have an n8n connection set up. Would you like to keep it, or set up a new one?"

If they want to keep it, skip to Step 5. If they want a new one, note that we'll overwrite it.

**Explain what's needed:**
> "To connect to your n8n, I need an API key. Here's how to get one:
>
> 1. Go to your n8n instance: https://[THEIR_N8N_URL]
> 2. Click your profile icon in the bottom-left corner
> 3. Click **Settings**
> 4. Click **API** in the left sidebar
> 5. Click **Create an API key**
> 6. Give it a name like 'Claude Code'
> 7. Copy the API key and paste it here
>
> The API key starts with `eyJ...`"

Wait for them to paste their API key.

**Once they provide the API key, add the MCP server configuration.**

There are two methods. Try Method A first. If it fails, use Method B.

### Method A: Using `claude mcp add-json` (preferred)

```bash
claude mcp add-json mr-n8n '{"type":"stdio","command":"npx","args":["n8n-mcp"],"env":{"MCP_MODE":"stdio","LOG_LEVEL":"error","DISABLE_CONSOLE_OUTPUT":"true","N8N_API_URL":"https://[THEIR_N8N_URL]","N8N_API_KEY":"[THEIR_API_KEY]"}}' -s user
```

Replace `[THEIR_N8N_URL]` with their actual URL and `[THEIR_API_KEY]` with their actual API key.

Use the `-s user` flag so the MCP server is available globally across all projects.

### Method B: Edit ~/.claude.json directly (fallback)

If Method A fails (e.g., `claude` command not found, or the command errors), edit `~/.claude.json` directly.

1. Read the current file: `cat ~/.claude.json 2>/dev/null`
2. If the file exists, parse the JSON and add the `mr-n8n` entry to the top-level `mcpServers` object
3. If the file doesn't exist, create it with just the mcpServers section

The JSON to add under the top-level `mcpServers` key:

```json
{
  "mr-n8n": {
    "type": "stdio",
    "command": "npx",
    "args": ["n8n-mcp"],
    "env": {
      "MCP_MODE": "stdio",
      "LOG_LEVEL": "error",
      "DISABLE_CONSOLE_OUTPUT": "true",
      "N8N_API_URL": "https://[THEIR_N8N_URL]",
      "N8N_API_KEY": "[THEIR_API_KEY]"
    }
  }
}
```

**Important:** Be careful not to corrupt the existing JSON. Read the full file, parse it, add the new entry, and write it back.

Tell the user:
> "I connected Claude Code to your n8n! This means I can create and edit workflows directly on your account."

**Important:** Tell the user they need to restart Claude Code for the connection to take effect:
> "You'll need to close and reopen Claude Code for the n8n connection to activate. After you reopen, come back here and say 'check my setup' to make sure everything works."

---

## Step 5: Create the Instructions File (CLAUDE.md)

**Check if ~/.claude/CLAUDE.md already exists:**
```bash
cat ~/.claude/CLAUDE.md 2>/dev/null
```

**If it exists and already contains "n8n Workflow Builder":** The n8n section is already there. Ask the user if they want to update it with their new info, or leave it as-is.

**If it exists but does NOT contain "n8n Workflow Builder":** Append the n8n section to the end of the existing file. Do NOT overwrite existing content.

**If it doesn't exist:** Create it fresh with a top-level heading `# Claude Code Instructions` followed by the n8n section.

The n8n section to add (replace [NAME] and [N8N_URL] with their actual values):

```markdown
## n8n Workflow Builder

I help [NAME] build n8n workflows.

### n8n Instance
URL: https://[N8N_URL]

### Skills

The `n8n` master skill at `~/.claude/skills/n8n/SKILL.md` routes to 8 sub-skills:

| Keyword | Sub-Skill |
|---------|-----------|
| workflow, n8n, automation | n8n/workflow-patterns |
| code node, javascript | n8n/code-javascript |
| python code | n8n/code-python |
| expression, {{ }} | n8n/expression-syntax |
| validate, check workflow | n8n/validation-expert |
| configure node, set up node | n8n/node-configuration |
| mcp tools, n8n tools | n8n/mcp-tools-expert |
| publish template, marketplace | n8n/template-publishing |

### Preferences
- Show the workflow plan before building
- Validate workflows before finishing
- Keep explanations simple
- Ask before making big changes
```

Tell the user:
> "I created your instructions file. Every time you open Claude Code, I'll remember your preferences and know how to help you with n8n."

---

## Step 6: Create Settings File

**Check if ~/.claude/settings.json already exists:**
```bash
cat ~/.claude/settings.json 2>/dev/null
```

**If it exists:** Read it and check if it already has the skill read permissions. If `Read(~/.claude/skills/**)` is already in the allow list, skip this step. If the permissions section exists but is missing the skill permissions, add them to the existing allow array. Do NOT overwrite other permissions.

**If it doesn't exist:** Create it:
```json
{
  "permissions": {
    "allow": [
      "Read(~/.claude/skills/**)",
      "Read(~/.claude/**)"
    ]
  }
}
```

Tell the user:
> "I set up permissions so I can access your skills automatically."

---

## Step 7: Verify Everything

Run these checks:

```bash
# Check master skill
ls ~/.claude/skills/n8n/SKILL.md 2>/dev/null && echo "Master skill: OK" || echo "Master skill: MISSING"

# Check sub-skills (should be 8)
ls ~/.claude/skills/n8n/*/INSTRUCTIONS.md 2>/dev/null | wc -l

# Check CLAUDE.md
test -f ~/.claude/CLAUDE.md && echo "CLAUDE.md exists" || echo "CLAUDE.md missing"

# Check settings
test -f ~/.claude/settings.json && echo "settings.json exists" || echo "settings.json missing"
```

Also check if the MCP server is configured:
```bash
cat ~/.claude.json 2>/dev/null | grep -c "mr-n8n" || echo "0"
```

Report results to the user:

> "Here's your setup status:
> - n8n master skill: [installed/missing]
> - Sub-skills: [X] of 8 installed
> - Instructions file (CLAUDE.md): [exists/missing]
> - Settings file: [exists/missing]
> - n8n connection: [connected/not connected]"

If anything is missing, offer to fix it.

If the n8n MCP was just configured in this session, remind them:
> "Remember: close and reopen Claude Code for the n8n connection to activate."

---

## Step 8: What's Next

Once everything checks out:

> "**You're all set!** Here's what you can do now:
>
> **Build a workflow:**
> - 'Build me a workflow that sends a Slack message when I get an email'
> - 'Create an automation that saves form responses to a spreadsheet'
>
> **Learn more:**
> - 'What workflow patterns can you help me with?'
> - 'Help me understand n8n expressions'
>
> **Important:** Close Claude Code and reopen it to load your new settings. Then try: 'Help me build my first workflow'"

---

## Troubleshooting

### "Skills aren't working"
```bash
ls -la ~/.claude/skills/
ls ~/.claude/skills/n8n/SKILL.md
ls ~/.claude/skills/n8n/*/INSTRUCTIONS.md
```
If no files found, re-run Step 2.

### "CLAUDE.md isn't loading"
Tell them to fully quit Claude Code (not just close the window) and reopen it.

### "Can't connect to n8n"
- Verify their URL format: should be like `name.app.n8n.cloud` (no `https://`)
- Verify their API key starts with `eyJ`
- Check Node.js is installed: `node --version`
- If Node.js is missing, tell them:
  > "You need Node.js installed. Go to https://nodejs.org and download the LTS version. It's a normal installer — just download and double-click to install. Then come back and we'll try again."

### "n8n MCP tools not showing up"
They need to restart Claude Code after the MCP server was added.

---

## Key Reference

### n8n Signup Link
https://n8n.partnerlinks.io/6w47oeg6f6v0

### File Locations
- Instructions: `~/.claude/CLAUDE.md`
- Skills: `~/.claude/skills/`
- Settings: `~/.claude/settings.json`
- MCP config: `~/.claude.json`

### n8n MCP Command (Method A)
```bash
claude mcp add-json mr-n8n '{"type":"stdio","command":"npx","args":["n8n-mcp"],"env":{"MCP_MODE":"stdio","LOG_LEVEL":"error","DISABLE_CONSOLE_OUTPUT":"true","N8N_API_URL":"https://[URL]","N8N_API_KEY":"[KEY]"}}' -s user
```

### n8n MCP Fallback (Method B)
If the `claude` command isn't available, edit `~/.claude.json` directly and add the `mr-n8n` entry to the top-level `mcpServers` object. See Step 4 for the full JSON structure.

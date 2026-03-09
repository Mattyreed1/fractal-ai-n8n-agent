# Claude Code + n8n Setup

Turn Claude into your personal n8n workflow builder. This folder contains everything Claude needs to set itself up.

## Setup (3 steps)

1. **Open this folder in Claude Code**
   - Open Claude Code (Desktop or CLI)
   - Select this folder as your project
   - (Desktop: click the folder icon at the top left, then browse to this folder)

2. **Tell Claude to set you up**
   - Type: `set me up`
   - Claude will walk you through everything from here

3. **Follow Claude's instructions**
   - Claude will ask you a few questions (your name, your n8n URL)
   - It will install skills, connect to n8n, and configure everything
   - If you don't have n8n yet, Claude will help you sign up

That's it. Claude handles the rest.

## What This Sets Up

- **n8n master skill + 8 sub-skills** that teach Claude how to build workflows (code nodes, expressions, node config, workflow patterns, validation, MCP tools, and template publishing)
- **n8n MCP connection** so Claude can create/edit workflows directly on your n8n instance
- **CLAUDE.md** instructions file personalized for you

## Requirements

- Claude Code (Desktop or CLI) with an active subscription
- An n8n account (Claude will help you create one if needed)

## Recommended Model

Currently, **Claude Opus 4.6** yeilds the best results. It handles complex multi-step workflow builds, validation loops, and MCP tool coordination significantly better than smaller models.

## Other Coding Agents

These skills are built for Claude Code, but the underlying skill files are plain Markdown — they work anywhere an agent can read instruction files. If you're using Codex, Gemini CLI, or Cursor, you can adapt the skills with some additional setup (pointing your agent at the skill files and configuring the n8n MCP server for your platform).

## Need Help?

Just tell Claude: `check my setup` or `help me with my setup`

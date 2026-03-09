# n8n Template Publishing

Prepare n8n workflow templates for publishing on the n8n marketplace.

---

## Purpose

Guides the complete process of preparing an n8n workflow for public sharing on the n8n template marketplace. Covers security auditing, documentation standards, and metadata requirements.

## Activates On

- publish workflow
- publish template
- prepare template
- marketplace publishing
- share workflow
- template documentation
- workflow description
- add sticky notes
- template readme

## File Count

2 files, ~400 lines total

## Priority

**MEDIUM** - Used when workflows are ready for sharing

## Dependencies

**n8n-mcp tools**:
- n8n_get_workflow (review workflow)
- n8n_validate_workflow (pre-publish validation)
- n8n_update_partial_workflow (add sticky notes)

**Related skills**:
- n8n Workflow Patterns (build workflow correctly first)
- n8n Validation Expert (validate before publishing)
- n8n MCP Tools Expert (workflow operations)

## Coverage

### Publishing Checklist

1. **Security Audit**
   - Remove hardcoded secrets (API keys, tokens, passwords)
   - Strip credentials from nodes
   - Replace sensitive values with placeholders
   - Check Code nodes for embedded credentials

2. **Sticky Note Documentation**
   - Section headers for workflow areas
   - Setup guide (credentials, configuration, testing)
   - Fractal AI branding

3. **Metadata**
   - Descriptive workflow title (50-80 chars)
   - Full markdown description
   - Short sales blurb summary

4. **Final Validation**
   - End-to-end testing
   - n8n_validate_workflow check
   - Sticky note positioning review

## Key Features

✅ **Security Checklist**: Comprehensive secret removal guide
✅ **Sticky Note Templates**: Ready-to-use documentation formats
✅ **Description Template**: Full markdown structure with examples
✅ **Branding Standards**: Fractal AI sticky note template
✅ **MCP Integration**: Tools for workflow updates

## Files

- **SKILL.md** (~350 lines) - Complete publishing guide
- **README.md** (this file) - Skill metadata

## Success Metrics

**Expected outcomes**:
- No secrets in published workflows
- Consistent documentation across templates
- Clear setup instructions for users
- Professional branding on all templates
- Marketplace-ready quality

## Sticky Note Standards

### Required Sticky Notes

1. **Setup Guide** (top-left)
   - Credentials required
   - Configuration steps
   - Testing instructions
   - Resource links

2. **Section Headers** (above each section)
   - Bold heading
   - 1-2 line description
   - Positioned near relevant nodes

3. **Fractal AI Branding** (bottom-right)
   - Company name and tagline
   - Social links (X, LinkedIn)

### Positioning Layout

```
┌─────────────────────────────────────────┐
│  📝 Setup Guide     [Workflow Nodes]    │
│                                         │
│              📝 Sections                │
│                                         │
│                         📝 Fractal AI   │
└─────────────────────────────────────────┘
```

## Description Template Structure

```markdown
# [Title]

## Who is this for?
## What problem does it solve?
## How it works (node table)
## Setup steps
## Resources
## Extending the flow
```

## Last Updated

2025-02-01

---

**Part of**: n8n-skills collection
**Created for**: Fractal AI template publishing workflow

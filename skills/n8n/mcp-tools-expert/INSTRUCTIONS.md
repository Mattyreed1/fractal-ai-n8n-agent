---
name: n8n-mcp-tools-expert
description: Expert guide for using n8n-mcp MCP tools effectively. Use when searching for nodes, validating configurations, accessing templates, managing workflows, or using any n8n-mcp tool. Provides tool selection guidance, parameter formats, and common patterns.
---

# n8n MCP Tools Expert

Master guide for using n8n-mcp MCP server tools to build workflows.

---

## Tool Categories

n8n-mcp provides tools organized into categories:

1. **Node Discovery** → [SEARCH_GUIDE.md](SEARCH_GUIDE.md)
2. **Configuration Validation** → [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md)
3. **Workflow Management** → [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)
4. **Template Library** - Search and deploy 2,700+ real workflows
5. **Documentation & Guides** - Tool docs, AI agent guide, Code node guides

---

## Mandatory Preflight (Run Before Any Workflow Edit)

### 1. Instance Targeting Guardrail

Always identify the n8n instance/server first, before listing or editing workflows.

Required sequence:
1. `list_mcp_resources()` (or equivalent environment check) to see available servers.
2. Confirm the named target instance is reachable (for example `mr-n8n` vs `scaleagency-n8n`).
3. Run `n8n_health_check` and `n8n_list_workflows` on that instance.
4. Match by exact workflow name + ID before any update.

Never create or modify workflows in a fallback/default instance when the user named a different one.

### 2. Workflow Selection Guardrail

Before editing:
1. Verify exact workflow exists in the selected instance.
2. If missing, stop and surface the mismatch.
3. If a replacement is needed, back up the current workflow JSON first.

Never silently create a duplicate workflow with the same name when the user asked to update an existing one.

### 3. Trigger Selection Guardrail

Choose trigger by caller type:
- External user/app/API call → `Webhook` trigger.
- Workflow invoked by another workflow only → `Execute Workflow Trigger`.

Never use `Execute Workflow Trigger` as the primary entrypoint for user-facing HTTP input flows.

### 4. Credential Input Guardrail

If end users must provide credentials/tokens (for example Apify token), design explicit inputs:
- JSON body fields (`apifyToken`)
- Or secure headers (`x-apify-token`)

Do not hardcode user tokens in node config. Validate presence early and fail with clear errors.

### 5. External API Call Guardrail

For outbound API calls:
- Prefer `HTTP Request` node.
- In Code node, use `$helpers.httpRequest()` only when necessary.
- Do not assume `fetch` is available in Code node runtimes.

### 6. Webhook Registration Guardrail

After webhook edits:
1. Save workflow.
2. Ensure active status.
3. If endpoint not registered, run deactivate/activate cycle.
4. Test real production webhook URL and verify execution record exists.

---

## Quick Reference

### Most Used Tools (by success rate)

| Tool | Use When | Speed |
|------|----------|-------|
| `search_nodes` | Finding nodes by keyword | <20ms |
| `get_node` | Understanding node operations (detail="standard") | <10ms |
| `validate_node` | Checking configurations (mode="full") | <100ms |
| `n8n_create_workflow` | Creating workflows | 100-500ms |
| `n8n_update_partial_workflow` | Editing workflows (MOST USED!) | 50-200ms |
| `validate_workflow` | Checking complete workflow | 100-500ms |
| `n8n_deploy_template` | Deploy template to n8n instance | 200-500ms |

---

## Tool Selection Guide

### Finding the Right Node

**Workflow**:
```
1. search_nodes({query: "keyword"})
2. get_node({nodeType: "nodes-base.name"})
3. [Optional] get_node({nodeType: "nodes-base.name", mode: "docs"})
```

**Example**:
```javascript
// Step 1: Search
search_nodes({query: "slack"})
// Returns: nodes-base.slack

// Step 2: Get details
get_node({nodeType: "nodes-base.slack"})
// Returns: operations, properties, examples (standard detail)

// Step 3: Get readable documentation
get_node({nodeType: "nodes-base.slack", mode: "docs"})
// Returns: markdown documentation
```

**Common pattern**: search → get_node (18s average)

### Validating Configuration

**Workflow**:
```
1. validate_node({nodeType, config: {}, mode: "minimal"}) - Check required fields
2. validate_node({nodeType, config, profile: "runtime"}) - Full validation
3. [Repeat] Fix errors, validate again
```

**Common pattern**: validate → fix → validate (23s thinking, 58s fixing per cycle)

### Managing Workflows

**Workflow**:
```
1. n8n_create_workflow({name, nodes, connections})
2. n8n_validate_workflow({id})
3. n8n_update_partial_workflow({id, operations: [...]})
4. n8n_validate_workflow({id}) again
5. n8n_update_partial_workflow({id, operations: [{type: "activateWorkflow"}]})
```

**Common pattern**: iterative updates (56s average between edits)

---

## Critical: nodeType Formats

**Two different formats** for different tools!

### Format 1: Search/Validate Tools
```javascript
// Use SHORT prefix
"nodes-base.slack"
"nodes-base.httpRequest"
"nodes-base.webhook"
"nodes-langchain.agent"
```

**Tools that use this**:
- search_nodes (returns this format)
- get_node
- validate_node
- validate_workflow

### Format 2: Workflow Tools
```javascript
// Use FULL prefix
"n8n-nodes-base.slack"
"n8n-nodes-base.httpRequest"
"n8n-nodes-base.webhook"
"@n8n/n8n-nodes-langchain.agent"
```

**Tools that use this**:
- n8n_create_workflow
- n8n_update_partial_workflow

### Conversion

```javascript
// search_nodes returns BOTH formats
{
  "nodeType": "nodes-base.slack",          // For search/validate tools
  "workflowNodeType": "n8n-nodes-base.slack"  // For workflow tools
}
```

---

## Testing & Verification — CRITICAL

### Validation ≠ Testing

**Validation** checks JSON structure. **Testing** executes the workflow.

```
validate_workflow / validate_node → Checks config syntax only
n8n_test_workflow → Actually RUNS the workflow
```

A workflow can pass validation with 0 errors and still completely fail at runtime (wrong credentials, bad expressions, API errors, incorrect node types).

### How to Actually Test

```
1. n8n_test_workflow({workflowId: "..."})
   → Works for: webhook, form, chat triggers
   → Does NOT work for: manual triggers (must test in n8n UI)

2. After testing, VERIFY execution happened:
   n8n_executions({action: "list", workflowId: "...", limit: 1})
   → If 0 executions → test did NOT run. Don't claim it works.

3. Check execution status:
   n8n_executions({action: "get", id: "...", mode: "error"})
   → Shows actual runtime errors
```

### Testing Rules

- **NEVER** claim a workflow "works" based on validation alone
- **ALWAYS** verify execution count > 0 after testing
- If you can't trigger via API (e.g., manual trigger), **say so explicitly**
- Check execution status for errors, don't assume success
- Test BOTH branches of IF/Switch nodes when possible

---

## Node Selection — Choose the Right Node

Before building, ensure you're using the correct node type:

### AI/LLM Nodes

| Task | Use This | NOT This |
|------|----------|----------|
| Simple LLM call (classify, summarize) | `openAi` (resource: text, operation: response) | `chainLlm` + `lmChatOpenAi` |
| Agent with tools/memory | `agent` + model sub-node + tools | `openAi` alone |
| Text classification | `openAi` (resource: text) | `chainLlm` |

### Form Nodes

| Task | Use This | NOT This |
|------|----------|----------|
| Start workflow from form | `formTrigger` | `form` (multi-page only) |
| Add pages to multi-page form | `form` (needs formTrigger upstream) | N/A |

### Validation

Run `search_nodes({query: "..."})` to see ALL available nodes for a category before choosing. Don't guess.

---

## Common Mistakes

### Mistake 1: Wrong nodeType Format

**Problem**: "Node not found" error

```javascript
// WRONG
get_node({nodeType: "slack"})  // Missing prefix
get_node({nodeType: "n8n-nodes-base.slack"})  // Wrong prefix

// CORRECT
get_node({nodeType: "nodes-base.slack"})
```

### Mistake 2: Using detail="full" by Default

**Problem**: Huge payload, slower response, token waste

```javascript
// WRONG - Returns 3-8K tokens, use sparingly
get_node({nodeType: "nodes-base.slack", detail: "full"})

// CORRECT - Returns 1-2K tokens, covers 95% of use cases
get_node({nodeType: "nodes-base.slack"})  // detail="standard" is default
get_node({nodeType: "nodes-base.slack", detail: "standard"})
```

**When to use detail="full"**:
- Debugging complex configuration issues
- Need complete property schema with all nested options
- Exploring advanced features

**Better alternatives**:
1. `get_node({detail: "standard"})` - for operations list (default)
2. `get_node({mode: "docs"})` - for readable documentation
3. `get_node({mode: "search_properties", propertyQuery: "auth"})` - for specific property

### Mistake 3: Not Using Validation Profiles

**Problem**: Too many false positives OR missing real errors

**Profiles**:
- `minimal` - Only required fields (fast, permissive)
- `runtime` - Values + types (recommended for pre-deployment)
- `ai-friendly` - Reduce false positives (for AI configuration)
- `strict` - Maximum validation (for production)

```javascript
// WRONG - Uses default profile
validate_node({nodeType, config})

// CORRECT - Explicit profile
validate_node({nodeType, config, profile: "runtime"})
```

### Mistake 4: Ignoring Auto-Sanitization

**What happens**: ALL nodes sanitized on ANY workflow update

**Auto-fixes**:
- Binary operators (equals, contains) → removes singleValue
- Unary operators (isEmpty, isNotEmpty) → adds singleValue: true
- IF/Switch nodes → adds missing metadata

**Cannot fix**:
- Broken connections
- Branch count mismatches
- Paradoxical corrupt states

```javascript
// After ANY update, auto-sanitization runs on ALL nodes
n8n_update_partial_workflow({id, operations: [...]})
// → Automatically fixes operator structures
```

### Mistake 5: Not Using Smart Parameters

**Problem**: Complex sourceIndex calculations for multi-output nodes

**Old way** (manual):
```javascript
// IF node connection
{
  type: "addConnection",
  source: "IF",
  target: "Handler",
  sourceIndex: 0  // Which output? Hard to remember!
}
```

**New way** (smart parameters):
```javascript
// IF node - semantic branch names
{
  type: "addConnection",
  source: "IF",
  target: "True Handler",
  branch: "true"  // Clear and readable!
}

{
  type: "addConnection",
  source: "IF",
  target: "False Handler",
  branch: "false"
}

// Switch node - semantic case numbers
{
  type: "addConnection",
  source: "Switch",
  target: "Handler A",
  case: 0
}
```

### Mistake 6: Not Using intent Parameter

**Problem**: Less helpful tool responses

```javascript
// WRONG - No context for response
n8n_update_partial_workflow({
  id: "abc",
  operations: [{type: "addNode", node: {...}}]
})

// CORRECT - Better AI responses
n8n_update_partial_workflow({
  id: "abc",
  intent: "Add error handling for API failures",
  operations: [{type: "addNode", node: {...}}]
})
```

### Mistake 7: Editing the Wrong n8n Instance

**Problem**: Workflow changed in the wrong account/server

```javascript
// WRONG - Edit without instance preflight
n8n_list_workflows(...)
n8n_update_partial_workflow(...)

// CORRECT - Instance preflight first
list_mcp_resources()
n8n_health_check()
n8n_list_workflows() // verify workflow ID/name in target instance
n8n_update_partial_workflow(...)
```

### Mistake 8: Using ExecuteWorkflowTrigger for User HTTP Input

**Problem**: Users cannot call workflow directly over HTTPS

```javascript
// WRONG - External flow starts at Execute Workflow Trigger
Execute Workflow Trigger -> ...

// CORRECT - External flow starts at Webhook
Webhook -> Validate/Normalize -> ...
```

### Mistake 9: Using fetch in Code Node for Production Integrations

**Problem**: Runtime errors (`fetch is not defined`) or environment drift

```javascript
// WRONG
const res = await fetch("https://api.apify.com/...");

// CORRECT
// Prefer HTTP Request node, or in Code node:
const res = await $helpers.httpRequest({ method: "GET", url: "https://..." });
```

---

## Tool Usage Patterns

### Pattern 1: Node Discovery (Most Common)

**Common workflow**: 18s average between steps

```javascript
// Step 1: Search (fast!)
const results = await search_nodes({
  query: "slack",
  mode: "OR",  // Default: any word matches
  limit: 20
});
// → Returns: nodes-base.slack, nodes-base.slackTrigger

// Step 2: Get details (~18s later, user reviewing results)
const details = await get_node({
  nodeType: "nodes-base.slack",
  includeExamples: true  // Get real template configs
});
// → Returns: operations, properties, metadata
```

### Pattern 2: Validation Loop

**Typical cycle**: 23s thinking, 58s fixing

```javascript
// Step 1: Validate
const result = await validate_node({
  nodeType: "nodes-base.slack",
  config: {
    resource: "channel",
    operation: "create"
  },
  profile: "runtime"
});

// Step 2: Check errors (~23s thinking)
if (!result.valid) {
  console.log(result.errors);  // "Missing required field: name"
}

// Step 3: Fix config (~58s fixing)
config.name = "general";

// Step 4: Validate again
await validate_node({...});  // Repeat until clean
```

### Pattern 3: Workflow Editing

**Most used update tool**: 99.0% success rate, 56s average between edits

```javascript
// Iterative workflow building (NOT one-shot!)
// Edit 1
await n8n_update_partial_workflow({
  id: "workflow-id",
  intent: "Add webhook trigger",
  operations: [{type: "addNode", node: {...}}]
});

// ~56s later...

// Edit 2
await n8n_update_partial_workflow({
  id: "workflow-id",
  intent: "Connect webhook to processor",
  operations: [{type: "addConnection", source: "...", target: "..."}]
});

// ~56s later...

// Edit 3 (validation)
await n8n_validate_workflow({id: "workflow-id"});

// Ready? Activate!
await n8n_update_partial_workflow({
  id: "workflow-id",
  intent: "Activate workflow for production",
  operations: [{type: "activateWorkflow"}]
});
```

---

## Detailed Guides

### Node Discovery Tools
See [SEARCH_GUIDE.md](SEARCH_GUIDE.md) for:
- search_nodes
- get_node with detail levels (minimal, standard, full)
- get_node modes (info, docs, search_properties, versions)

### Validation Tools
See [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) for:
- Validation profiles explained
- validate_node with modes (minimal, full)
- validate_workflow complete structure
- Auto-sanitization system
- Handling validation errors

### Workflow Management
See [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) for:
- n8n_create_workflow
- n8n_update_partial_workflow (17 operation types!)
- Smart parameters (branch, case)
- AI connection types (8 types)
- Workflow activation (activateWorkflow/deactivateWorkflow)
- n8n_deploy_template
- n8n_workflow_versions

---

## Template Usage

### Search Templates

```javascript
// Search by keyword (default mode)
search_templates({
  query: "webhook slack",
  limit: 20
});

// Search by node types
search_templates({
  searchMode: "by_nodes",
  nodeTypes: ["n8n-nodes-base.httpRequest", "n8n-nodes-base.slack"]
});

// Search by task type
search_templates({
  searchMode: "by_task",
  task: "webhook_processing"
});

// Search by metadata (complexity, setup time)
search_templates({
  searchMode: "by_metadata",
  complexity: "simple",
  maxSetupMinutes: 15
});
```

### Get Template Details

```javascript
get_template({
  templateId: 2947,
  mode: "structure"  // nodes+connections only
});

get_template({
  templateId: 2947,
  mode: "full"  // complete workflow JSON
});
```

### Deploy Template Directly

```javascript
// Deploy template to your n8n instance
n8n_deploy_template({
  templateId: 2947,
  name: "My Weather to Slack",  // Custom name (optional)
  autoFix: true,  // Auto-fix common issues (default)
  autoUpgradeVersions: true  // Upgrade node versions (default)
});
// Returns: workflow ID, required credentials, fixes applied
```

---

## Self-Help Tools

### Get Tool Documentation

```javascript
// Overview of all tools
tools_documentation()

// Specific tool details
tools_documentation({
  topic: "search_nodes",
  depth: "full"
})

// Code node guides
tools_documentation({topic: "javascript_code_node_guide", depth: "full"})
tools_documentation({topic: "python_code_node_guide", depth: "full"})
```

### AI Agent Guide

```javascript
// Comprehensive AI workflow guide
ai_agents_guide()
// Returns: Architecture, connections, tools, validation, best practices
```

### Health Check

```javascript
// Quick health check
n8n_health_check()

// Detailed diagnostics
n8n_health_check({mode: "diagnostic"})
// → Returns: status, env vars, tool status, API connectivity
```

---

## Tool Availability

**Always Available** (no n8n API needed):
- search_nodes, get_node
- validate_node, validate_workflow
- search_templates, get_template
- tools_documentation, ai_agents_guide

**Requires n8n API** (N8N_API_URL + N8N_API_KEY):
- n8n_create_workflow
- n8n_update_partial_workflow
- n8n_validate_workflow (by ID)
- n8n_list_workflows, n8n_get_workflow
- n8n_test_workflow
- n8n_executions
- n8n_deploy_template
- n8n_workflow_versions
- n8n_autofix_workflow

If API tools unavailable, use templates and validation-only workflows.

---

## Unified Tool Reference

### get_node (Unified Node Information)

**Detail Levels** (mode="info", default):
- `minimal` (~200 tokens) - Basic metadata only
- `standard` (~1-2K tokens) - Essential properties + operations (RECOMMENDED)
- `full` (~3-8K tokens) - Complete schema (use sparingly)

**Operation Modes**:
- `info` (default) - Node schema with detail level
- `docs` - Readable markdown documentation
- `search_properties` - Find specific properties (use with propertyQuery)
- `versions` - List all versions with breaking changes
- `compare` - Compare two versions
- `breaking` - Show only breaking changes
- `migrations` - Show auto-migratable changes

```javascript
// Standard (recommended)
get_node({nodeType: "nodes-base.httpRequest"})

// Get documentation
get_node({nodeType: "nodes-base.webhook", mode: "docs"})

// Search for properties
get_node({nodeType: "nodes-base.httpRequest", mode: "search_properties", propertyQuery: "auth"})

// Check versions
get_node({nodeType: "nodes-base.executeWorkflow", mode: "versions"})
```

### validate_node (Unified Validation)

**Modes**:
- `full` (default) - Comprehensive validation with errors/warnings/suggestions
- `minimal` - Quick required fields check only

**Profiles** (for mode="full"):
- `minimal` - Very lenient
- `runtime` - Standard (default, recommended)
- `ai-friendly` - Balanced for AI workflows
- `strict` - Most thorough (production)

```javascript
// Full validation with runtime profile
validate_node({nodeType: "nodes-base.slack", config: {...}, profile: "runtime"})

// Quick required fields check
validate_node({nodeType: "nodes-base.webhook", config: {}, mode: "minimal"})
```

---

## Performance Characteristics

| Tool | Response Time | Payload Size |
|------|---------------|--------------|
| search_nodes | <20ms | Small |
| get_node (standard) | <10ms | ~1-2KB |
| get_node (full) | <100ms | 3-8KB |
| validate_node (minimal) | <50ms | Small |
| validate_node (full) | <100ms | Medium |
| validate_workflow | 100-500ms | Medium |
| n8n_create_workflow | 100-500ms | Medium |
| n8n_update_partial_workflow | 50-200ms | Small |
| n8n_deploy_template | 200-500ms | Medium |

---

## Best Practices

### Do
- Use `get_node({detail: "standard"})` for most use cases
- Specify validation profile explicitly (`profile: "runtime"`)
- Use smart parameters (`branch`, `case`) for clarity
- Include `intent` parameter in workflow updates
- Follow search → get_node → validate workflow
- Iterate workflows (avg 56s between edits)
- Validate after every significant change
- Use `includeExamples: true` for real configs
- Use `n8n_deploy_template` for quick starts

### Don't
- Use `detail: "full"` unless necessary (wastes tokens)
- Forget nodeType prefix (`nodes-base.*`)
- Skip validation profiles
- Try to build workflows in one shot (iterate!)
- Ignore auto-sanitization behavior
- Use full prefix (`n8n-nodes-base.*`) with search/validate tools
- Forget to activate workflows after building

---

## Summary

**Most Important**:
1. Use **get_node** with `detail: "standard"` (default) - covers 95% of use cases
2. nodeType formats differ: `nodes-base.*` (search/validate) vs `n8n-nodes-base.*` (workflows)
3. Specify **validation profiles** (`runtime` recommended)
4. Use **smart parameters** (`branch="true"`, `case=0`)
5. Include **intent parameter** in workflow updates
6. **Auto-sanitization** runs on ALL nodes during updates
7. Workflows can be **activated via API** (`activateWorkflow` operation)
8. Workflows are built **iteratively** (56s avg between edits)

**Common Workflow**:
1. search_nodes → find node
2. get_node → understand config
3. validate_node → check config
4. n8n_create_workflow → build
5. n8n_validate_workflow → verify
6. n8n_update_partial_workflow → iterate
7. activateWorkflow → go live!

For details, see:
- [SEARCH_GUIDE.md](SEARCH_GUIDE.md) - Node discovery
- [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) - Configuration validation
- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Workflow management

---

**Related Skills**:
- n8n Expression Syntax - Write expressions in workflow fields
- n8n Workflow Patterns - Architectural patterns from templates
- n8n Validation Expert - Interpret validation errors
- n8n Node Configuration - Operation-specific requirements
- n8n Code JavaScript - Write JavaScript in Code nodes
- n8n Code Python - Write Python in Code nodes

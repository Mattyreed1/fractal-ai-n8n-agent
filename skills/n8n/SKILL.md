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
- **[Expression Syntax](expression-syntax/INSTRUCTIONS.md)**: n8n expressions and syntax usage. Covers `{{ $json.field }}`, data access, built-in methods, and common string/math operations.
- **[MCP Tools Expert](mcp-tools-expert/INSTRUCTIONS.md)**: Guide to using n8n MCP tools for interacting with n8n instances (searching nodes, getting node essentials, validation).
- **[Node Configuration](node-configuration/INSTRUCTIONS.md)**: Best practices for configuring n8n nodes, handling inputs/outputs, credentials, execution modes, and routing.
- **[Template Publishing](template-publishing/INSTRUCTIONS.md)**: Guidelines for creating and publishing high-quality n8n workflow templates.
- **[Validation Expert](validation-expert/INSTRUCTIONS.md)**: Comprehensive guide for verifying n8n workflows, troubleshooting node execution errors, and resolving structural issues.
- **[Workflow Patterns](workflow-patterns/INSTRUCTIONS.md)**: High-level production-ready architectural patterns for API integration, webhooks, databases, and scheduled tasks.

## Quick Guidelines

1. **Always Read Sub-Instructions**: Need to write JavaScript? First read `code-javascript/INSTRUCTIONS.md`. Need to fix an error? Read `validation-expert/INSTRUCTIONS.md`.
2. **Accessing Data**: Remember `{{ $json.body }}` for webhook bodies in expressions, or `$input.first().json.body` in Code nodes.
3. **Execution Context**: Pay attention to "Run Once for All Items" vs "Run Once for Each Item" modes in Code nodes.

Whenever working on an n8n problem, use this index to find the exact sub-skill document you require, then read it closely before proceeding.

# Super-Dev Hooks

This directory contains Claude Code hooks that enforce workflow rules.

## Hooks Overview

| Hook | Event | Purpose |
|------|-------|---------|
| `block_direct_mcp.py` | PreToolUse | Blocks direct MCP tool calls, requires script usage |

## block_direct_mcp.py

**Purpose:** Technically enforces the FORBIDDEN rules by intercepting MCP tool calls before execution and blocking them.

### Why This Hook Exists

The FORBIDDEN rules in skill/agent markdown files are just text instructions. Claude may not always follow them, especially:
- At the start of a workflow before fully processing instructions
- When the AI defaults to using available tools directly
- When context is long and instructions get deprioritized

This hook provides **technical enforcement** - it intercepts the tool call at the Claude Code level and blocks it with exit code 2.

### How It Works

1. **Registration**: The hook is registered in `.claude/settings.local.json`:
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "mcp__exa__.*|mcp__deepwiki__.*|mcp__context7__.*|mcp__github__search.*|mcp__github__get_file.*",
           "hooks": [
             {
               "type": "command",
               "command": "python3 super-dev-plugin/hooks/block_direct_mcp.py"
             }
           ]
         }
       ]
     }
   }
   ```

2. **Interception**: When Claude tries to call a matched MCP tool:
   - Claude Code runs this hook BEFORE executing the tool
   - The hook receives tool info via stdin
   - The hook checks if the tool is forbidden

3. **Blocking**: If the tool is forbidden:
   - Exit code 2 is returned (blocks execution)
   - Error message is printed to stderr (visible to Claude)
   - Claude receives the error and should use scripts instead

### Forbidden Tools

| MCP Tool | Required Script |
|----------|-----------------|
| `mcp__exa__web_search_exa` | `scripts/exa/exa_search.py` |
| `mcp__exa__get_code_context_exa` | `scripts/exa/exa_code.py` |
| `mcp__deepwiki__read_wiki_structure` | `scripts/deepwiki/deepwiki_structure.py` |
| `mcp__deepwiki__read_wiki_contents` | `scripts/deepwiki/deepwiki_contents.py` |
| `mcp__deepwiki__ask_question` | `scripts/deepwiki/deepwiki_ask.py` |
| `mcp__context7__resolve-library-id` | `scripts/context7/context7_resolve.py` |
| `mcp__context7__get-library-docs` | `scripts/context7/context7_docs.py` |
| `mcp__github__search_code` | `scripts/github/github_search_code.py` |
| `mcp__github__search_repositories` | `scripts/github/github_search_repos.py` |
| `mcp__github__get_file_contents` | `scripts/github/github_file_contents.py` |

### Allowed Exceptions

| MCP Tool | Reason |
|----------|--------|
| `mcp__time-mcp__current_time` | No script wrapper available |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Allow the tool call |
| 2 | Block the tool call |

### Testing

To test the hook manually:
```bash
echo '{"tool_name": "mcp__exa__web_search_exa"}' | python3 super-dev-plugin/hooks/block_direct_mcp.py
echo $?  # Should be 2 (blocked)

echo '{"tool_name": "mcp__time-mcp__current_time"}' | python3 super-dev-plugin/hooks/block_direct_mcp.py
echo $?  # Should be 0 (allowed)
```

### Troubleshooting

**Hook not triggering:**
- Check that `.claude/settings.local.json` has the hooks section
- Verify the matcher pattern covers the tool being called
- Ensure the script path is correct relative to project root

**Tool still being called:**
- The hook only works for tools matching the regex pattern
- Check if the tool name matches the pattern exactly
- Review Claude Code logs for hook execution

## Adding New Hooks

To add a new hook:

1. Create a Python script in this directory
2. Implement stdin parsing and exit code logic
3. Register in `.claude/settings.local.json`
4. Document in this README

### Hook Events

| Event | When Triggered |
|-------|----------------|
| `PreToolUse` | Before any tool executes |
| `PostToolUse` | After tool completes |
| `UserPromptSubmit` | Before user prompt is sent |
| `Stop` | When conversation ends |
| `PreCompact` | Before context compaction |

See [Claude Code Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks) for details.

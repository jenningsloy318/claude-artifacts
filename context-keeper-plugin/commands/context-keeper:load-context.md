---
name: context-keeper:load-context
description: Load a previous context summary for continuity after compaction
argument-hint: "[session-id or timestamp]"
---

# Load Context Command

Load a previous context summary to restore conversation state from before compaction.

## Arguments

- `$ARGUMENTS` - Optional session ID or timestamp to load. If omitted, loads the most recent summary.

## Automatic Execution

This command is automatically executed via the **PreToolUse hook** when invoked. The hook intercepts the slash command and runs `scripts/load_context.py` with any arguments. Uses `jq` for efficient JSON extraction with Python fallback.

## Usage Examples

```
/context-keeper:load-context
# Loads the most recent context summary

/context-keeper:load-context abc123
# Loads summary for session starting with abc123

/context-keeper:load-context 20251123_190448
# Loads summary from specific timestamp
```

## Output Format

When loading a context:
```
## Context Summary Loaded

**Session ID:** abc123...
**Created:** 2025-11-23 19:04:48
**Trigger:** auto
**Messages:** 150

---

[Full summary content here]

---
Would you like me to use this context for our conversation?
```

When context not found:
```
No context found for 'xyz'.

Available contexts:
  - [abc123...] 2025-11-23 19:04
  - [def456...] 2025-11-22 14:30
```

## Error Handling

- **No summaries directory**: "No context summaries found. Run `/compact` to create your first summary."
- **No index.json**: "Summary index not found."
- **Summary not found**: Lists available contexts for user to choose from.

## Related Commands

- `/context-keeper:list-sessions` - List all stored sessions
- `/context-keeper:list-context [session-id]` - List contexts for a specific session

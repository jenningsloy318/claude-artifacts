---
name: context-keeper:load-memory
description: Load a previous memory for continuity after compaction
argument-hint: "[session-id or timestamp]"
---

# Load Memory Command

Load a previous memory to restore conversation state from before compaction.

## Arguments

- `$ARGUMENTS` - Optional session ID or timestamp to load. If omitted, loads the most recent memory.

## MANDATORY: Execute Script

**YOU MUST run this command using Bash tool - DO NOT use Read tool to read index.json directly:**

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/load_memory.py $ARGUMENTS
```

This script uses `jq` for efficient JSON extraction. Running the script is REQUIRED - do not read files manually.

## Usage Examples

```
/load-memory
# Loads the most recent context memory

/load-memory abc123
# Loads memory for session starting with abc123

/load-memory 20231101_143022
# Loads memory from specific timestamp
```

## Script Behavior

The `load_memory.py` script automatically detects its mode:

1. **Automatic Hook Mode**: When triggered by SessionStart hook (with JSON input via stdin)
   - Loads recent memory silently
   - Outputs formatted context directly to Claude's system context
   - Only runs on resume/compact, not on fresh startup

2. **Manual Command Mode**: When invoked by user with no stdin data
   - Displays memory content in the chat
   - Asks for user confirmation before using the context
   - Can accept optional session ID or timestamp parameter


```

## Output Format

When loading a context:
```
## Context Memory Loaded

**Session ID:** abc123...
**Created:** 2025-11-23 19:04:48
**Trigger:** auto
**Messages:** 150

---

[Full memory content here]

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

- **No memories directory**: "No context memories found. Run `/compact` to create your first memory."
- **No index.json**: "Summary index not found."
- **Summary not found**: Lists available contexts for user to choose from.

## Related Commands

- `/context-keeper:list-sessions` - List all stored sessions
- `/context-keeper:list-context [session-id]` - List contexts for a specific session

---
name: context-keeper:list-sessions
description: Enumerate all stored sessions with their memories
---

# List Memory Sessions Command

Display all stored sessions that have memories saved by the context-keeper plugin.

## MANDATORY: Execute Script

**YOU MUST run this command using Bash tool - DO NOT use Read tool to read index.json directly:**

```bash
python3 context-keeper-plugin/scripts/list_memory_sessions.py
```

This script uses `jq` for efficient JSON extraction. Running the script is REQUIRED - do not read files manually.

## Output Format

```
## Stored Sessions

| # | Session ID | Compactions | Latest Activity | Project | Messages |
|---|------------|-------------|-----------------|---------|----------|
| 1 | abc123...  | 3           | 2025-11-24 19:04 | myproject | 280 |
| 2 | def456...  | 1           | 2025-11-23 14:30 | myproject | 45  |
| 3 | ghi789...  | 5           | 2025-11-22 10:15 | other     | 450 |

**Total:** 3 sessions with 9 context memories

### Quick Actions
- Use `/context-keeper:list-context <session-id>` to see all contexts for a session
- Use `/context-keeper:load-context <session-id>` to load the latest context from a session
```

## Error Handling

- **No memories directory**: "No sessions found. Context memories are created automatically when you run `/compact`."
- **No index.json**: "No session history available. Start a coding session and run `/compact` to begin tracking."
- **Empty index**: "No sessions recorded yet. Your first context will be saved on the next compaction."

## Related Commands

- `/context-keeper:list-context [session-id]` - List contexts for a specific session
- `/context-keeper:load-context [session-id]` - Load a context memory

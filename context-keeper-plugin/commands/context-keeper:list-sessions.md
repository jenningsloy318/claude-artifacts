---
name: context-keeper:list-sessions
description: Enumerate all stored sessions with their context summaries
---

# List Sessions Command

Display all stored sessions that have context summaries saved by the context-keeper plugin.

## Instructions

When this command is invoked:

1. **Read the summaries index** at `{project}/.claude/summaries/index.json`
   - If it doesn't exist, inform the user no sessions are available

2. **Group summaries by session ID** and calculate:
   - Number of compactions per session
   - Latest compaction timestamp
   - Total files modified across all compactions
   - Project path

3. **Display a summary table** sorted by most recent activity

## Output Format

```
## Stored Sessions

| # | Session ID | Compactions | Latest Activity | Project | Total Files |
|---|------------|-------------|-----------------|---------|-------------|
| 1 | abc123...  | 3           | 2025-11-24 19:04 | /dev/myproject | 28 |
| 2 | def456...  | 1           | 2025-11-23 14:30 | /dev/myproject | 3  |
| 3 | ghi789...  | 5           | 2025-11-22 10:15 | /dev/other     | 45 |

**Total:** 3 sessions with 9 context summaries

### Quick Actions
- Use `/context-keeper:list-context <session-id>` to see all contexts for a session
- Use `/context-keeper:load-context <session-id>` to load the latest context from a session
```

## Implementation

Use the Read tool to:
1. Read `.claude/summaries/index.json` for the summary index
2. Group entries by session_id
3. Calculate aggregated statistics
4. Format and display results

### Grouping Logic

```python
# Pseudo-code for grouping
sessions = {}
for summary in index["summaries"]:
    sid = summary["session_id"]
    if sid not in sessions:
        sessions[sid] = {
            "compaction_count": 0,
            "latest_timestamp": None,
            "project": summary["project"],
            "total_files": set()
        }
    sessions[sid]["compaction_count"] += 1
    sessions[sid]["total_files"].update(summary.get("files_modified", []))
    # Update latest if more recent
```

## Error Handling

- **No summaries directory**: "No sessions found. Context summaries are created automatically when you run `/compact`."
- **No index.json**: "No session history available. Start a coding session and run `/compact` to begin tracking."
- **Empty index**: "No sessions recorded yet. Your first context will be saved on the next compaction."

## Related Commands

- `/context-keeper:list-context [session-id]` - List contexts for a specific session
- `/context-keeper:load-context [session-id]` - Load a context summary

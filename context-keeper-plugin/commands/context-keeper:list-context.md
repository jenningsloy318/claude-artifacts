---
name: context-keeper:list-context
description: List all saved contexts for a session or all sessions
argument-hint: "[session-id]"
---

# List Context Command

Display saved context summaries from the context-keeper plugin.

## Arguments

- `$ARGUMENTS` - Optional session ID to filter contexts. If omitted, lists all contexts.

## Instructions

When this command is invoked:

1. **Read the summaries index** at `{project}/.claude/summaries/index.json`
   - If it doesn't exist, inform the user no summaries are available

2. **If session ID provided** (`$ARGUMENTS` is not empty):
   - Filter summaries to show only entries matching that session ID
   - Show all compaction timestamps for that session
   - Display detailed information for each compaction

3. **If no session ID provided** (list all):
   - Show a summary table of all stored contexts
   - Group by session ID if multiple compactions exist
   - Sort by most recent first

## Output Format

### When listing all contexts:

```
## Saved Contexts

| # | Session ID | Compactions | Latest | Files Modified | Messages |
|---|------------|-------------|--------|----------------|----------|
| 1 | abc123...  | 3           | 2025-11-24 19:04 | 15 | 150 |
| 2 | def456...  | 1           | 2025-11-23 14:30 | 3  | 45  |

Total: 2 sessions, 4 context summaries
```

### When listing specific session:

```
## Context History for Session abc123...

### Compaction 1: 2025-11-24 19:04:48
- **Trigger:** manual
- **Files Modified:** 15
- **Messages:** 150
- **Topics:** #authentication, #api, #bugfix
- **Summary Path:** abc123.../20251124_190448/summary.md

### Compaction 2: 2025-11-24 15:30:22
- **Trigger:** auto
- **Files Modified:** 8
- **Messages:** 95
- **Topics:** #refactoring, #tests
- **Summary Path:** abc123.../20251124_153022/summary.md

Would you like me to load one of these contexts?
```

## Implementation

Use the Read tool to:
1. Read `.claude/summaries/index.json` for the summary index
2. Parse and format the results

### Index Structure

```json
{
  "summaries": [
    {
      "session_id": "abc123...",
      "timestamp": "20251124_190448",
      "created_at": "2025-11-24T19:04:48Z",
      "trigger": "manual",
      "project": "/path/to/project",
      "files_modified": ["file1.py", "file2.ts"],
      "message_count": 150,
      "summary_path": "abc123.../20251124_190448/summary.md"
    }
  ],
  "last_session": "abc123..."
}
```

## Error Handling

- **No summaries directory**: "No context summaries found. Run `/compact` to create your first summary."
- **No index.json**: "Summary index not found. Context summaries will be created automatically during compaction."
- **Session not found**: "No contexts found for session '{id}'. Available sessions: [list first 5]"

## Related Commands

- `/context-keeper:list-sessions` - List all stored sessions
- `/context-keeper:load-context` - Load a specific context summary

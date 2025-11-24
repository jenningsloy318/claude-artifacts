---
name: session-manager
description: Manage Claude Code session summaries. Use when user wants to list, load, search, or manage saved session summaries. Triggers on phrases like "list sessions", "show summaries", "load session", "what sessions", "previous work", "session history", "what did we work on".
---

# Session Manager Skill

Manage session summaries created by the PreCompact hook.

## When to Activate

Use this skill when user:
- Asks about previous sessions ("what did we work on?", "show my sessions")
- Wants to list saved summaries ("list sessions", "session history")
- Needs to load specific context ("load the auth session", "restore previous work")
- Wants to search summaries ("find session about database")
- Asks about session management ("how many summaries", "delete old sessions")

## Directory Structure

Session summaries are stored in the project's `.claude/summaries/` directory:

```
.claude/summaries/
├── index.json                      # Global index of all summaries
└── {session_id}/
    ├── {timestamp}/
    │   ├── summary.md              # Human-readable summary
    │   └── metadata.json           # Machine-readable metadata
    └── latest -> {timestamp}       # Symlink to most recent
```

## Available Actions

### 1. List Sessions

Read `.claude/summaries/index.json` and present available sessions.

**Output format:**
```
## Available Session Summaries

| # | Session ID | Date | Trigger | Files Modified |
|---|------------|------|---------|----------------|
| 1 | abc123... | 2025-11-23 19:04 | auto | 15 |
| 2 | def456... | 2025-11-22 14:30 | manual | 3 |

Total: 2 sessions stored
```

### 2. Load Session

Load a specific session summary and optionally inject into context.

**Steps:**
1. Read summary from `.claude/summaries/{id}/{timestamp}/summary.md`
2. Read metadata from `.claude/summaries/{id}/{timestamp}/metadata.json`
3. Present to user
4. Ask if they want it injected into current context

**Context injection format:**
```xml
<previous-session-context>
[Summary content here]
</previous-session-context>
```

### 3. Search Sessions

Search through summaries by keyword or topic.

**Steps:**
1. Read index.json for session list
2. For each session, read summary.md
3. Search for matching keywords
4. Return ranked results

### 4. Session Statistics

Provide overview of stored sessions.

**Output:**
```
## Session Summary Statistics

- Total sessions: 15
- Total compactions: 23
- Most active project: /path/to/project
- Most common topics: #api, #authentication, #bugfix
- Storage used: ~2.3 MB
```

## Tool Usage

Use these tools to implement actions:

- **Read** - Read index.json and summary files
- **Glob** - Find summary files: `.claude/summaries/**/*.md`
- **Grep** - Search within summaries for keywords

## Response Guidelines

1. **Be concise** - Show tables/lists, not walls of text
2. **Show recent first** - Most recent sessions at top
3. **Truncate IDs** - Show first 8 chars of session IDs
4. **Include dates** - Always show human-readable dates
5. **Offer actions** - After listing, offer to load specific session

## Error Handling

- **No summaries directory**: "No session summaries found. Summaries are created automatically when context is compacted."
- **No index.json**: "Summary index not found. Run `/compact` to create your first summary."
- **Session not found**: "Session '{id}' not found. Available sessions: [list]"

## Integration with PreCompact Hook

This skill reads data created by the PreCompact hook, which is automatically registered when the plugin is installed. No manual configuration required.

**Index.json structure:**
```json
{
  "summaries": [
    {
      "session_id": "abc123...",
      "timestamp": "20251123_190448",
      "created_at": "2025-11-23T19:04:48Z",
      "trigger": "auto",
      "project": "/path/to/project",
      "files_modified": ["file1.py", "file2.ts"],
      "message_count": 150,
      "summary_path": "abc123.../20251123_190448/summary.md"
    }
  ],
  "last_session": "abc123..."
}
```

## Example Interactions

**User:** "What sessions do I have?"
**Response:** [List sessions table]

**User:** "Load the most recent session"
**Response:** [Show summary, ask about context injection]

**User:** "Find sessions about authentication"
**Response:** [Search and show matching sessions]

**User:** "How many summaries are stored?"
**Response:** [Show statistics]

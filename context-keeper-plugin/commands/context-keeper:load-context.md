---
name: context-keeper:load-context
description: Load a previous context summary for continuity after compaction
argument-hint: "[session-id or timestamp]"
---

# Load Context Command

Load a previous context summary to restore conversation state from before compaction.

## Arguments

- `$ARGUMENTS` - Optional session ID or timestamp to load. If omitted, loads the most recent summary.

## Instructions

When this command is invoked:

1. **Check for summaries directory** at `{project}/.claude/summaries/`
   - If it doesn't exist, inform the user no summaries are available

2. **If no argument provided** (load latest):
   - Read `.claude/summaries/index.json`
   - Get the most recent summary entry
   - Read the summary file from `{session_id}/{timestamp}/summary.md`

3. **If session ID or timestamp provided**:
   - Search for matching context in index
   - If found, load that specific summary
   - If not found, list available sessions

4. **Present the summary** to the user with:
   - Context metadata (session ID, timestamp, trigger)
   - Full summary content
   - Option to inject into current context

5. **If user wants to inject**:
   - Wrap the summary in `<previous-context>` tags
   - Include it in the conversation

## Usage Examples

```
/context-keeper:load-context
# Loads the most recent context summary

/context-keeper:load-context abc123
# Loads summary for session starting with abc123

/context-keeper:load-context 20251123_190448
# Loads summary from specific timestamp
```

## Implementation

Use the Read tool to:
1. Read `.claude/summaries/index.json` for available contexts
2. Read the specific `summary.md` file
3. Present content to user

## Output Format

When listing contexts:
```
Available Contexts:
1. [abc123...] 2025-11-23 19:04 - 15 files modified (auto compact)
2. [def456...] 2025-11-22 14:30 - 3 files modified (manual compact)
```

When loading a context:
```
## Context Summary Loaded

**Session ID:** abc123...
**Created:** 2025-11-23 19:04:48
**Trigger:** auto

[Full summary content here]

---
Would you like me to use this context for our conversation?
```

## Related Commands

- `/context-keeper:list-sessions` - List all stored sessions
- `/context-keeper:list-context [session-id]` - List contexts for a specific session

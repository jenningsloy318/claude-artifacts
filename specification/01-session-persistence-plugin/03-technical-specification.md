# Technical Specification: PreCompact Hook for Session Persistence

**Date:** 2025-11-23 19:04 PST
**Version:** 1.0
**Status:** Draft

---

## 1. Overview

### 1.1 Purpose

Implement a PreCompact hook system that automatically summarizes and persists Claude Code sessions before context compaction, with automatic context restoration on session resume.

### 1.2 Scope

**In Scope (Phase 1):**
- PreCompact hook configuration
- Python hook script for summarization
- Local file storage for summaries
- SessionStart hook for auto-reload
- Slash command for manual session loading
- Skill for session management

**Out of Scope (Phase 2):**
- Nowledge Mem MCP integration
- Cross-device synchronization
- Semantic search across sessions

### 1.3 Success Criteria

1. PreCompact hook triggers on both manual (`/compact`) and automatic compaction
2. Summary includes all required content (topics, code changes, decisions, context)
3. Summary persists to local file system
4. Context automatically reloads after compaction
5. Manual session loading works via slash command and skill

---

## 2. Compaction Behavior Analysis

### 2.1 What Happens During Compaction

| Aspect | Before Compact | After Compact | Changes? |
|--------|---------------|---------------|----------|
| **session_id** | Current session ID | Same session ID | **No** |
| **transcript_path** | Points to session.jsonl | Same path (content modified) | **No** |
| **Context window** | Full conversation history | Compressed/summarized | **Yes** |
| **Event fired** | `PreCompact` | `SessionStart` (resume) | N/A |

### 2.2 Key Insights

1. **Session ID persists** - Compaction occurs within a session, not across sessions
2. **Transcript is modified** - The JSONL file content changes (truncated/compressed)
3. **No thread_id concept** - Claude Code uses session_id as primary identifier
4. **Critical timing** - PreCompact fires BEFORE transcript modification, allowing full capture

### 2.3 Implications for Our Design

- **Must capture in PreCompact** - Read full transcript before it's compressed
- **Use session_id for naming** - Consistent identifier across compactions
- **SessionStart reloads context** - Fires after compaction with `event_type: "resume"`
- **Handle multiple compactions** - Same session may compact multiple times

---

## 3. System Architecture

### 3.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Claude Code                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────┐                                                 │
│  │ settings.json  │ ◀─── Hook Configuration                         │
│  └───────┬────────┘                                                 │
│          │                                                          │
│          ▼                                                          │
│  ┌────────────────┐     ┌─────────────────┐                        │
│  │ PreCompact     │────▶│ precompact.py   │                        │
│  │ Event          │     │ (Hook Script)   │                        │
│  └────────────────┘     └────────┬────────┘                        │
│                                  │                                  │
│          ┌───────────────────────┼───────────────────────┐         │
│          │                       │                       │         │
│          ▼                       ▼                       ▼         │
│  ┌───────────────┐     ┌─────────────────┐     ┌───────────────┐  │
│  │ Read          │     │ Generate        │     │ Save          │  │
│  │ Transcript    │     │ Summary (LLM)   │     │ to File       │  │
│  └───────────────┘     └─────────────────┘     └───────────────┘  │
│                                                         │          │
│                                                         ▼          │
│                                               ┌─────────────────┐  │
│                                               │ .claude/        │  │
│                                               │ summaries/      │  │
│                                               └────────┬────────┘  │
│                                                        │           │
│  ┌────────────────┐     ┌─────────────────┐           │           │
│  │ SessionStart   │────▶│ session_start.py│◀──────────┘           │
│  │ Event          │     │ (Reload Hook)   │                       │
│  └────────────────┘     └─────────────────┘                       │
│                                                                    │
│  ┌────────────────┐     ┌─────────────────┐                       │
│  │ /load-session  │────▶│ load-session.md │                       │
│  │ (Slash Cmd)    │     │ (Command)       │                       │
│  └────────────────┘     └─────────────────┘                       │
│                                                                    │
│  ┌────────────────┐     ┌─────────────────┐                       │
│  │ session-mgmt   │────▶│ SKILL.md        │                       │
│  │ (Skill)        │     │                 │                       │
│  └────────────────┘     └─────────────────┘                       │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 File Structure

```
.claude/
├── settings.local.json         # Hook configuration (update)
├── hooks/
│   ├── precompact.py           # PreCompact hook script
│   └── session_start.py        # SessionStart hook script
├── commands/
│   └── load-session.md         # Slash command definition
├── skills/
│   └── session-manager/
│       └── SKILL.md            # Session management skill
└── summaries/
    ├── index.json              # Summary index
    └── {session_id}/
        ├── summary.md          # Human-readable summary
        └── metadata.json       # Machine-readable metadata
```

---

## 3. Detailed Design

### 3.1 Hook Configuration (settings.local.json)

```json
{
  "permissions": {
    "allow": ["mcp__time-mcp__current_time"],
    "deny": [],
    "ask": []
  },
  "hooks": {
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/precompact.py",
            "timeout": 120
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/session_start.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### 3.2 PreCompact Hook Script (precompact.py)

#### 3.2.1 Input Processing

```python
#!/usr/bin/env python3
"""
PreCompact Hook: Summarizes and persists session before compaction.

Input (stdin): JSON with session metadata
Output (stdout): Status message
Exit codes:
  0 - Success
  1 - Non-blocking error (logged but doesn't block)
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

def read_hook_input() -> dict:
    """Read JSON input from stdin."""
    return json.loads(sys.stdin.read())
```

#### 3.2.2 Transcript Parsing

```python
def parse_transcript(transcript_path: str) -> list[dict]:
    """Parse JSONL transcript file into messages."""
    messages = []
    with open(transcript_path, 'r') as f:
        for line in f:
            if line.strip():
                messages.append(json.loads(line))
    return messages

def extract_conversation_content(messages: list[dict]) -> dict:
    """Extract relevant content from transcript messages."""
    return {
        "user_messages": [...],
        "assistant_messages": [...],
        "tool_calls": [...],
        "files_modified": [...],
    }
```

#### 3.2.3 Summary Generation

```python
import anthropic

def generate_summary(content: dict, session_info: dict) -> str:
    """Generate comprehensive summary using Claude API."""

    client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

    prompt = f"""Analyze this Claude Code session and create a comprehensive summary.

Session Information:
- Session ID: {session_info['session_id']}
- Trigger: {session_info['trigger']}
- Project: {session_info['cwd']}

Conversation Content:
{json.dumps(content, indent=2)}

Create a summary with these sections:
1. **Topics Discussed** - Main themes and subjects
2. **Code Changes** - Files modified with descriptions
3. **Decisions Made** - Key decisions with rationale
4. **Key Outcomes** - What was accomplished
5. **Context for Continuation** - Important context for future sessions
6. **Tags** - Relevant hashtags for categorization

Format as Markdown. Be comprehensive but concise."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text
```

#### 3.2.4 File Storage

```python
def save_summary(
    session_id: str,
    summary: str,
    metadata: dict,
    base_path: Path
) -> Path:
    """Save summary and metadata to file system."""

    summaries_dir = base_path / ".claude" / "summaries"
    session_dir = summaries_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # Save summary
    summary_path = session_dir / "summary.md"
    summary_path.write_text(summary)

    # Save metadata
    metadata_path = session_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    # Update index
    update_index(summaries_dir, session_id, metadata)

    # Update latest symlink
    latest_link = summaries_dir / "latest"
    if latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(session_id)

    return summary_path

def update_index(summaries_dir: Path, session_id: str, metadata: dict):
    """Update the summaries index file."""
    index_path = summaries_dir / "index.json"

    if index_path.exists():
        index = json.loads(index_path.read_text())
    else:
        index = {"summaries": [], "last_loaded": None}

    # Add new entry
    index["summaries"].insert(0, {
        "session_id": session_id,
        "timestamp": metadata["timestamp"],
        "trigger": metadata["trigger"],
        "topics": metadata.get("topics", []),
        "files_modified": metadata.get("files_modified", []),
        "summary_path": f"{session_id}/summary.md"
    })

    # Keep only last 50 entries
    index["summaries"] = index["summaries"][:50]

    index_path.write_text(json.dumps(index, indent=2))
```

#### 3.2.5 Main Execution

```python
def main():
    try:
        # Read input
        hook_input = read_hook_input()

        session_id = hook_input["session_id"]
        transcript_path = hook_input["transcript_path"]
        trigger = hook_input.get("trigger", "unknown")
        cwd = hook_input.get("cwd", os.getcwd())

        # Parse transcript
        messages = parse_transcript(transcript_path)
        content = extract_conversation_content(messages)

        # Generate summary
        session_info = {
            "session_id": session_id,
            "trigger": trigger,
            "cwd": cwd,
            "timestamp": datetime.utcnow().isoformat()
        }
        summary = generate_summary(content, session_info)

        # Extract metadata from summary
        metadata = {
            **session_info,
            "topics": extract_topics(summary),
            "files_modified": content.get("files_modified", []),
            "message_count": len(messages)
        }

        # Save to file system
        base_path = Path(cwd)
        summary_path = save_summary(session_id, summary, metadata, base_path)

        # Output success message
        print(f"Session summary saved to {summary_path}")
        sys.exit(0)

    except Exception as e:
        print(f"Error in PreCompact hook: {e}", file=sys.stderr)
        sys.exit(1)  # Non-blocking error

if __name__ == "__main__":
    main()
```

### 3.3 SessionStart Hook Script (session_start.py)

```python
#!/usr/bin/env python3
"""
SessionStart Hook: Reloads latest session summary into context.

Input (stdin): JSON with session metadata
Output (stdout): Context to inject (becomes system context)
Exit codes:
  0 - Success (stdout becomes context)
  1 - Error (non-blocking)
"""

import sys
import json
from pathlib import Path

def main():
    try:
        hook_input = json.loads(sys.stdin.read())
        cwd = hook_input.get("cwd", ".")
        event_type = hook_input.get("event_type", "startup")

        # Only inject on resume (after compaction)
        if event_type not in ["resume", "startup"]:
            sys.exit(0)

        summaries_dir = Path(cwd) / ".claude" / "summaries"
        latest_link = summaries_dir / "latest"

        if not latest_link.exists():
            sys.exit(0)  # No summaries yet

        # Read latest summary
        summary_path = latest_link / "summary.md"
        if summary_path.exists():
            summary = summary_path.read_text()

            # Output context for injection
            context = f"""<previous-session-context>
The following is a summary of the previous session before context compaction:

{summary}

Use this context to maintain continuity with the previous conversation.
</previous-session-context>"""

            print(context)

        sys.exit(0)

    except Exception as e:
        print(f"Error loading session: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 3.4 Slash Command (load-session.md)

```markdown
---
name: load-session
description: Load a specific session summary into context
arguments:
  - name: session_id
    description: The session ID to load (optional, defaults to latest)
    required: false
---

Load a previous session summary to restore context.

## Usage

- `/load-session` - Load the most recent session
- `/load-session abc123` - Load a specific session by ID

## Available Sessions

To see available sessions, check `.claude/summaries/index.json` or ask me to list them.

## What Gets Loaded

The session summary includes:
- Topics discussed
- Code changes made
- Decisions with rationale
- Key outcomes
- Context for continuation

## Implementation

When this command is run:
1. Read the session summary from `.claude/summaries/{session_id}/summary.md`
2. Inject the content into the current context
3. Continue the conversation with restored context
```

### 3.5 Session Manager Skill (SKILL.md)

```markdown
---
name: session-manager
description: Manage Claude Code session summaries. Use when user wants to list, load, or manage saved sessions. Triggers on "list sessions", "show summaries", "load session", "what sessions", "previous work".
---

# Session Manager Skill

## When to Use

Activate when user:
- Asks about previous sessions ("what did we work on?")
- Wants to list saved sessions ("show my sessions")
- Needs to load specific context ("load the auth session")
- Wants to manage summaries ("delete old sessions")

## Available Actions

### List Sessions

Read `.claude/summaries/index.json` and present:
- Session ID (truncated)
- Date/time
- Topics
- Files modified

Example output:
```
Recent Sessions:
1. [abc123] 2025-11-23 - Auth system, API design | Modified: src/auth.py
2. [def456] 2025-11-22 - Database schema | Modified: db/schema.sql
```

### Load Session

1. Read `.claude/summaries/{id}/summary.md`
2. Present summary to user
3. Offer to inject into context

### Search Sessions

Search index.json for matching:
- Topics
- Files modified
- Date range

## Tool Usage

No MCP tools required - all file-based operations using Read tool.

## Response Format

Keep responses concise. Show session list as table or bullet points.
When loading, show summary and ask if user wants it in context.
```

---

## 4. Data Schemas

### 4.1 Hook Input (PreCompact)

```typescript
interface PreCompactInput {
  session_id: string;
  transcript_path: string;
  cwd: string;
  permission_mode: "default" | "strict" | "permissive";
  hook_event_name: "PreCompact";
  trigger: "manual" | "auto";
  custom_instructions?: string;
}
```

### 4.2 Summary Metadata

```typescript
interface SummaryMetadata {
  session_id: string;
  timestamp: string;  // ISO 8601
  trigger: "manual" | "auto";
  cwd: string;
  topics: string[];
  files_modified: string[];
  message_count: number;
  summary_path: string;
}
```

### 4.3 Summary Index

```typescript
interface SummaryIndex {
  summaries: SummaryMetadata[];
  last_loaded: string | null;  // session_id
}
```

---

## 5. Error Handling

### 5.1 Error Categories

| Error | Handling | Exit Code |
|-------|----------|-----------|
| Missing transcript | Log warning, skip | 1 |
| API key missing | Use fallback or skip | 1 |
| API rate limit | Retry with backoff | 1 |
| File write failure | Log error | 1 |
| JSON parse error | Log error | 1 |

### 5.2 Fallback Strategy

If Claude API unavailable:
1. Check for local Ollama
2. If no LLM available, create basic summary from transcript structure
3. Log warning but continue

---

## 6. Configuration

### 6.1 Environment Variables

```bash
# Required for LLM summarization
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Ollama fallback
OLLAMA_HOST=http://localhost:11434

# Optional: Custom summary model
SUMMARY_MODEL=claude-sonnet-4-20250514
```

### 6.2 User Configurable Options

In `.claude/summaries/config.json`:

```json
{
  "max_summaries": 50,
  "summary_model": "claude-sonnet-4-20250514",
  "include_code_snippets": true,
  "auto_reload": true,
  "fallback_to_ollama": true
}
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

- `test_parse_transcript()` - Transcript parsing
- `test_generate_summary()` - Summary generation (mocked API)
- `test_save_summary()` - File operations
- `test_update_index()` - Index management

### 7.2 Integration Tests

- Full PreCompact flow with mock transcript
- SessionStart reload with existing summary
- Slash command execution
- Skill invocation

### 7.3 Manual Testing

1. Start Claude Code session
2. Make some changes, have conversation
3. Run `/compact` manually
4. Verify summary created in `.claude/summaries/`
5. Check context reloaded on resume

---

## 8. Phase 2: Nowledge Mem Integration

### 8.1 Additional Hook Logic

After saving locally, call Nowledge Mem:

```python
import httpx

async def persist_to_nowledge(summary: str, metadata: dict):
    """Persist summary to Nowledge Mem MCP server."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:14242/mcp",
            json={
                "method": "thread_persist",
                "params": {
                    "client": "claude-code",
                    "project_path": metadata["cwd"],
                    "persist_mode": "current",
                    "summary": summary[:100]  # Brief summary
                }
            },
            headers={"APP": "claude-code"}
        )
        return response.json()
```

### 8.2 Memory Distillation

Extract key insights and save as memories:

```python
async def distill_insights(summary: str, metadata: dict):
    """Extract and save key insights to Nowledge Mem."""
    insights = extract_insights(summary)

    for insight in insights:
        await client.post(
            "http://localhost:14242/mcp",
            json={
                "method": "memory_add",
                "params": {
                    "content": insight["content"],
                    "title": insight["title"],
                    "importance": insight["importance"],
                    "labels": ",".join(metadata["topics"])
                }
            }
        )
```

---

## 9. Security Considerations

1. **API Key Protection:** Use environment variables, never hardcode
2. **File Permissions:** Set 600 on summary files
3. **Transcript Sensitivity:** May contain secrets - warn user
4. **Network Security:** MCP calls to localhost only
5. **Input Validation:** Validate all JSON inputs before processing

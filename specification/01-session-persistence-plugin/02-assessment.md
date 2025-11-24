# Assessment: Current State & Implementation Options

**Date:** 2025-11-23 19:04 PST
**Feature:** PreCompact Hook for Session Persistence

---

## 1. Current State Analysis

### 1.1 Existing Project Structure

```
/home/jenningsl/development/claude-artifacts/
└── .claude/
    └── settings.local.json    # Currently only has permissions config
```

**Current settings.local.json:**
```json
{
  "permissions": {
    "allow": ["mcp__time-mcp__current_time"],
    "deny": [],
    "ask": []
  }
}
```

### 1.2 Existing Nowledge Mem Integration

The user has the Nowledge Mem plugin already installed with these skills:
- `nowledge-mem:distill-memory` - Extract insights
- `nowledge-mem:search-memory` - Search knowledge base
- `nowledge-mem:save-thread` - Save full conversations

**MCP Server:** `http://localhost:14242/mcp`

### 1.3 Gap Analysis

| Requirement | Current State | Gap |
|-------------|--------------|-----|
| PreCompact hook | Not configured | Need to add hook config |
| Hook script | Does not exist | Need to create Python script |
| Local summary storage | No folder structure | Need `.claude/summaries/` |
| LLM summarization | Not implemented | Need summary generation |
| Auto-reload after compact | Not configured | Need SessionStart hook |
| Nowledge Mem persistence | Skills exist (manual) | Need to automate via hook |

---

## 2. Architecture Options

### Option A: Simple File-Based (Phase 1 Focus)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ PreCompact  │────▶│ Python Hook  │────▶│ Local Summary   │
│   Event     │     │   Script     │     │ File (.md)      │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ SessionStart │
                    │ Hook (reload)│
                    └──────────────┘
```

**Pros:**
- Simple to implement
- No external dependencies (except LLM)
- Fast execution
- Works offline

**Cons:**
- No cross-device sync
- No semantic search
- Manual skill invocation needed for Nowledge

### Option B: Full Integration with Nowledge Mem (Phase 2)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ PreCompact  │────▶│ Python Hook  │────▶│ Local Summary   │
│   Event     │     │   Script     │     │ File (.md)      │
└─────────────┘     └──────────────┘     └────────┬────────┘
                           │                      │
                           ▼                      │
                    ┌──────────────┐              │
                    │ Nowledge Mem │◀─────────────┘
                    │ MCP Server   │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Knowledge    │
                    │ Graph + Search│
                    └──────────────┘
```

**Pros:**
- Semantic search across all sessions
- Knowledge graph relationships
- Cross-device sync (if configured)
- Automatic context surfacing

**Cons:**
- Requires Nowledge Mem running
- More complex implementation
- Network dependency

### Option C: Hybrid (Recommended)

Phase 1: Local file storage + SessionStart reload
Phase 2: Add Nowledge Mem integration

**This allows:**
- Immediate functionality without Nowledge Mem
- Graceful degradation if MCP server unavailable
- Progressive enhancement

---

## 3. LLM Summary Generation Options

### 3.1 Option 1: Claude API (Recommended)

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2000,
    messages=[{"role": "user", "content": prompt}]
)
```

**Pros:** Best quality, consistent with Claude Code
**Cons:** Requires API key, network call

### 3.2 Option 2: Local Ollama

```python
import httpx

response = httpx.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3", "prompt": prompt}
)
```

**Pros:** Privacy-first, offline capable
**Cons:** Variable quality, requires Ollama setup

### 3.3 Option 3: Simple Rule-Based Extraction

```python
def extract_summary(transcript):
    # Parse transcript, extract:
    # - User messages
    # - Tool calls
    # - File modifications
    # Return structured summary
```

**Pros:** Fast, no external deps
**Cons:** Lower quality, misses nuance

### Recommendation: Claude API with Ollama fallback

---

## 4. Summary Content Structure

Based on user requirements, the summary should include:

```markdown
# Session Summary

## Metadata
- **Session ID:** {session_id}
- **Date:** {timestamp}
- **Trigger:** {manual|auto}
- **Project:** {project_path}

## Topics Discussed
- Topic 1
- Topic 2

## Code Changes
### Files Modified
- `path/to/file1.py` - Description
- `path/to/file2.ts` - Description

### Key Code Snippets
```language
// Important code here
```

## Decisions Made
1. Decision 1 with rationale
2. Decision 2 with rationale

## Key Outcomes
- Outcome 1
- Outcome 2

## Context for Continuation
Important context that should be preserved...

## Tags
#topic1 #topic2 #project-name
```

---

## 5. File Storage Strategy

### 5.1 Local Storage Location

```
.claude/
├── summaries/
│   ├── index.json              # Index of all summaries
│   ├── latest.md               # Symlink to most recent
│   └── {session_id}/
│       ├── summary.md          # Human-readable summary
│       ├── metadata.json       # Machine-readable metadata
│       └── transcript.jsonl    # Optional: full transcript backup
└── hooks/
    └── precompact_hook.py      # Hook script
```

### 5.2 Index File Format

```json
{
  "summaries": [
    {
      "session_id": "abc123",
      "timestamp": "2025-11-23T19:04:48Z",
      "trigger": "auto",
      "topics": ["authentication", "api-design"],
      "files_modified": ["src/auth.py"],
      "summary_path": "abc123/summary.md"
    }
  ],
  "last_loaded": "abc123"
}
```

---

## 6. Reload Strategy

### 6.1 SessionStart Hook

When a new session starts (or resumes after compaction):

1. Read `.claude/summaries/index.json`
2. Find most recent summary for this project
3. Inject summary content as context
4. Output via stdout (becomes system context)

### 6.2 Slash Command `/load-session`

Allow manual loading of specific sessions:

```bash
/load-session abc123
```

### 6.3 Skill Integration

Create a skill that:
- Lists available summaries
- Allows selection
- Injects into context

---

## 7. Security Considerations

1. **Transcript Access:** Hook reads full transcript - sensitive data exposure
2. **API Key Storage:** If using Claude API, secure key storage needed
3. **File Permissions:** Summary files should have restricted permissions
4. **Network Calls:** MCP communication should be localhost only

### Mitigations

- Store API keys in environment variables
- Set file permissions to 600
- Validate input JSON before processing
- Sanitize any user content in summaries

---

## 8. Recommendation

**Implement Option C (Hybrid) with:**

1. **Phase 1 (This PR):**
   - PreCompact hook with Python script
   - Claude API for summarization (with env var for API key)
   - Local file storage in `.claude/summaries/`
   - SessionStart hook for auto-reload
   - Slash command for manual load

2. **Phase 2 (Future):**
   - Nowledge Mem MCP integration
   - Automatic `thread_persist` call
   - Semantic search across sessions
   - Knowledge graph integration

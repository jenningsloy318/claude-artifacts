# Research Report: PreCompact Hook for Session Persistence

**Date:** 2025-11-23 19:04 PST
**Feature:** PreCompact Hook for Automatic Session Summarization and Persistence

---

## 1. Executive Summary

This report documents research findings for implementing a PreCompact hook in Claude Code that automatically:
1. Summarizes the current session/thread before compaction
2. Saves the summary to a local project folder
3. Pipes the summary to Nowledge Mem MCP server for persistence
4. Auto-loads context after compaction completes

---

## 2. Claude Code Hook System

### 2.1 Available Hooks

| Hook | Purpose | Can Block |
|------|---------|-----------|
| PreToolUse | Before tool execution | Yes |
| PostToolUse | After tool execution | Yes |
| **PreCompact** | Before context compaction | No |
| UserPromptSubmit | Before processing user input | Yes |
| SessionStart | Session initialization | No |
| SessionEnd | Session termination | No |
| Stop | When agent finishes responding | No |
| Notification | When notifications are sent | No |

### 2.2 PreCompact Hook Details

**Trigger conditions:**
- Manual: User runs `/compact` command
- Automatic: Context window becomes full

**Input data available:**
```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "hook_event_name": "PreCompact",
  "trigger": "manual" | "auto",
  "custom_instructions": ""
}
```

**Key limitation:** PreCompact hooks cannot block compaction, but can:
- Log events
- Prepare cleanup operations
- Generate summaries
- Persist data externally

### 2.3 Hook Configuration Location

Hooks are configured in JSON settings files (priority order):
1. `~/.claude/settings.json` (global)
2. `.claude/settings.json` (project-specific)
3. `.claude/settings.local.json` (local overrides)

**Hook structure:**
```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/script.py",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

---

## 3. Memory Management Best Practices

### 3.1 Claude Official Recommendations

**Primary persistence mechanism:** CLAUDE.md files
- `~/.claude/CLAUDE.md` - Global context
- `PROJECT_ROOT/CLAUDE.md` - Project-specific context

**Recommended folder structure:**
```
project-root/
├── CLAUDE.md                    # Project-level persistent context
├── .claude/
│   ├── summaries/               # Session summaries (our target)
│   ├── skills/                  # Custom skills
│   └── hooks/                   # Hook scripts
└── docs/
    └── decisions/               # Architecture Decision Records
```

### 3.2 Session Continuity Patterns

1. **CLAUDE.md Injection** - Critical context survives compaction
2. **Architecture Documentation** - Stored in `docs/` for reference
3. **SessionStart Hook** - Re-inject context after compaction
4. **Git History** - Accessible via git commands for recovery

---

## 4. Nowledge Mem Integration

### 4.1 Overview

Nowledge Mem is a local-first, graph-augmented personal context manager that:
- Persists entire conversation threads
- Distills key insights into searchable memories
- Connects everything through an intelligent knowledge graph

### 4.2 MCP Configuration

```json
{
  "mcpServers": {
    "nowledge-mem": {
      "url": "http://localhost:14242/mcp",
      "type": "streamableHttp",
      "headers": {
        "APP": "claude-code"
      }
    }
  }
}
```

### 4.3 Available Skills (Already Installed)

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `nowledge-mem:save-thread` | Save complete conversation | Explicit request |
| `nowledge-mem:distill-memory` | Extract key insights | Valuable moments |
| `nowledge-mem:search-memory` | Search knowledge base | Contextual |

### 4.4 MCP Tools

**`thread_persist`** - Save sessions
```json
{
  "client": "claude-code",
  "project_path": "/path/to/project",
  "persist_mode": "current",
  "summary": "Brief description"
}
```

**`memory_add`** - Add standalone memory
```json
{
  "content": "Insight + context",
  "title": "Searchable title",
  "importance": 0.8,
  "labels": "tech,topic"
}
```

**`memory_search`** - Search knowledge base
```json
{
  "query": "search terms",
  "limit": 10,
  "mode": "normal",
  "confidence_threshold": 0.5
}
```

---

## 5. Technical Approach

### 5.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Claude Code Session                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌───────────────┐    ┌─────────────────┐  │
│  │  Conversation │───▶│  PreCompact   │───▶│  Hook Script    │  │
│  │    Context    │    │    Hook       │    │  (Python)       │  │
│  └──────────────┘    └───────────────┘    └────────┬────────┘  │
│                                                     │           │
│                      ┌──────────────────────────────┼───────┐  │
│                      │                              │       │  │
│                      ▼                              ▼       │  │
│               ┌─────────────┐              ┌───────────────┐│  │
│               │ Local File  │              │ Nowledge Mem  ││  │
│               │ (.claude/   │              │ MCP Server    ││  │
│               │  summaries/)│              │ (Phase 2)     ││  │
│               └─────────────┘              └───────────────┘│  │
│                      │                              │       │  │
│                      └──────────────────────────────┘       │  │
│                                    │                         │  │
│                                    ▼                         │  │
│                           ┌───────────────┐                  │  │
│                           │ SessionStart  │                  │  │
│                           │ Hook (reload) │                  │  │
│                           └───────────────┘                  │  │
│                                                              │  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow

1. **PreCompact triggers** (manual `/compact` or auto)
2. **Hook script receives** session data via stdin (JSON)
3. **Script reads** transcript from `transcript_path`
4. **LLM generates** comprehensive summary
5. **Summary saved** to `.claude/summaries/{session_id}.md`
6. **Phase 2:** Summary piped to Nowledge Mem
7. **SessionStart hook** reloads latest summary into context

### 5.3 Summary Content (Per User Requirements)

The summary should include:
- Conversation topics/themes
- Code changes made
- Files modified
- Key decisions/outcomes
- Important context for continuation

---

## 6. Related Tools & Libraries

### 6.1 For Python Implementation

- `httpx` - Async HTTP client for MCP communication
- `json` - Parse hook input
- `pathlib` - File path handling
- `datetime` - Timestamp generation
- `subprocess` - Optional LLM CLI calls

### 6.2 For LLM Summary Generation

Options:
1. **Claude API** - Direct API call (requires API key)
2. **Local Ollama** - Privacy-first local LLM
3. **Anthropic SDK** - Official Python SDK

---

## 7. References

- Claude Code Hooks Documentation: https://code.claude.com/docs/en/hooks.md
- Nowledge Mem: https://mem.nowledge.co/
- Nowledge Mem Claude Code Plugin: https://github.com/nowledge-co/community
- MCP Protocol: https://modelcontextprotocol.io/

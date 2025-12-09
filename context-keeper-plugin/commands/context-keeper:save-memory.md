---
name: context-keeper:save-memory
description: Manually save the current session context to memory before compaction
argument-hint: "[custom-instructions]"
---

# Save Memory Command

Manually trigger the context-keeper precompact hook to save the current session context to memory.

## Arguments

- `$ARGUMENTS` - Optional custom instructions for how the memory should be created (e.g., "focus on architecture decisions", "emphasize error solutions", "include UI changes")

## MANDATORY: Execute Script

**YOU MUST run this command using Bash tool - DO NOT handle memory creation manually:**

```bash
python3 context-keeper-plugin/scripts/save_memory.py
```

This script:
- Reads the current session transcript
- Generates an AI-powered summary with key insights
- Saves the memory locally in `.claude/memories/`
- Optionally persists to nowledge MCP if configured

## What Gets Preserved

The memory generation follows this priority:

### **MUST be preserved:**
- Key architecture changes (system design, structural modifications, refactoring decisions)
- Key UI/UX changes (component updates, interface modifications, user experience improvements)
- Key specification changes (requirements changes, business rules, validation logic updates)
- Multiple rounds of conversation that clarify issues and requirements
- Indirect or direct logs that show errors (error messages, stack traces, failure information)

### **Gets refined/summarized:**
- Repetitive conversations that converge on a solution
- Long error traces refined to show only key error indicators
- Multiple similar questions condensed into single entries

### **Gets excluded:**
- Unrelated logs and system outputs
- LLM internal thinking processes
- Filler acknowledgments and pleasantries
- Repetitive minor interactions
- Raw tool outputs without context

## Custom Instructions Examples

```bash
# Focus on architectural decisions
/context-keeper:save-memory "focus on architecture decisions and design patterns"

# Emphasize error solutions
/context-keeper:save-memory "emphasize error solutions and debugging approaches"

# Include UI/UX changes
/context-keeper:save-memory "include all UI/UX changes and component updates"

# Comprehensive memory
/context-keeper:save-memory "comprehensive summary including all technical details"
```

## Output

The script provides real-time feedback:

```
============================================================
🔄 [context-keeper] PreCompact Hook Running...
============================================================
📋 [context-keeper] Processing session abc123... (trigger: manual)
📖 [context-keeper] Parsing transcript...
📊 [context-keeper] Found 150 messages
🤖 [context-keeper] Generating memory with AI...
💾 [context-keeper] Saving memory...
✅ [context-keeper] Session context saved successfully!
============================================================
```

## Configuration (Optional)

The script supports these environment variables:

- `CLAUDE_SUMMARY_API_KEY` - API key for Claude summarization (required for LLM memory)
- `CLAUDE_SUMMARY_API_URL` - Custom API base URL (optional, for proxy or region)

These can be set in:
- Shell environment
- `~/.claude/settings.json` under the `env` section

## Memory Storage

Memories are saved to:
- Local: `.claude/memories/{session_id}/{timestamp}/memory.json`
- Index: `.claude/memories/index.json` (tracks all memories)
- Optional: Nowledge MCP server (if configured)

## Notes

- This is the same script that runs automatically during `/compact`
- Manual execution allows you to control when memories are created
- Custom instructions help focus the memory on what matters most
- The script gracefully falls back to structured extraction if AI is unavailable
- All operations are non-blocking - failures won't affect your workflow
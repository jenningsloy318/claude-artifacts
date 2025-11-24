# Implementation Plan: PreCompact Hook for Session Persistence

**Date:** 2025-11-23 19:04 PST
**Version:** 1.0

---

## Overview

This plan breaks down the implementation into phases and milestones for the PreCompact hook system.

---

## Phase 1: Core Infrastructure (Foundation)

### Milestone 1.1: Directory Structure & Configuration

**Objective:** Set up the file structure and hook configuration

**Tasks:**
1. Create `.claude/hooks/` directory
2. Create `.claude/summaries/` directory
3. Create `.claude/commands/` directory
4. Create `.claude/skills/session-manager/` directory
5. Update `.claude/settings.local.json` with hook configuration

**Deliverables:**
- Directory structure in place
- Hook configuration ready (but pointing to placeholder scripts)

**Dependencies:** None

---

### Milestone 1.2: PreCompact Hook Script

**Objective:** Create the main hook script that captures and summarizes sessions

**Tasks:**
1. Create `precompact.py` base structure
   - Input parsing from stdin
   - Error handling framework
   - Logging setup

2. Implement transcript parsing
   - Read JSONL transcript file
   - Extract user messages
   - Extract assistant messages
   - Extract tool calls and results
   - Identify files modified

3. Implement LLM summarization
   - Claude API integration
   - Summary prompt engineering
   - Fallback handling (Ollama or basic extraction)

4. Implement file storage
   - Create session directory
   - Write summary.md
   - Write metadata.json
   - Update index.json

**Deliverables:**
- Fully functional `precompact.py` script
- Unit tests for core functions

**Dependencies:** Milestone 1.1

---

### Milestone 1.3: SessionStart Hook Script

**Objective:** Create the hook that reloads context after compaction

**Tasks:**
1. Create `session_start.py` script
   - Input parsing
   - Event type detection (resume vs startup)

2. Implement summary loading
   - Read latest summary from symlink
   - Format for context injection

3. Implement context output
   - Format summary for Claude context
   - Output to stdout

**Deliverables:**
- Functional `session_start.py` script
- Integration test with PreCompact

**Dependencies:** Milestone 1.2

---

## Phase 2: User Interface (Interaction Layer)

### Milestone 2.1: Slash Command

**Objective:** Create manual session loading command

**Tasks:**
1. Create `/load-session` command definition
   - Command markdown file
   - Argument handling (optional session_id)

2. Implement command logic
   - List available sessions
   - Load specific session
   - Inject into context

**Deliverables:**
- Working `/load-session` command

**Dependencies:** Milestone 1.2

---

### Milestone 2.2: Session Manager Skill

**Objective:** Create skill for session management

**Tasks:**
1. Create `SKILL.md` definition
   - Trigger conditions
   - Available actions

2. Document usage patterns
   - List sessions
   - Load sessions
   - Search sessions

**Deliverables:**
- Working `session-manager` skill

**Dependencies:** Milestone 2.1

---

## Phase 3: Testing & Polish

### Milestone 3.1: Integration Testing

**Objective:** Verify end-to-end functionality

**Tasks:**
1. Manual testing workflow
   - Start session
   - Make changes
   - Trigger compaction
   - Verify summary created
   - Verify context reloaded

2. Edge case testing
   - Empty session
   - Very long session
   - API failure
   - Missing transcript

**Deliverables:**
- Test results documentation
- Bug fixes

**Dependencies:** Phase 2 complete

---

### Milestone 3.2: Documentation & Cleanup

**Objective:** Finalize and document

**Tasks:**
1. Update README with usage instructions
2. Clean up test files
3. Remove debug logging
4. Final code review

**Deliverables:**
- Complete documentation
- Production-ready code

**Dependencies:** Milestone 3.1

---

## Phase 4: Nowledge Mem Integration (Future)

### Milestone 4.1: MCP Integration

**Objective:** Integrate with Nowledge Mem MCP server

**Tasks:**
1. Add MCP client code to `precompact.py`
2. Call `thread_persist` after local save
3. Handle MCP server unavailability gracefully

**Deliverables:**
- Nowledge Mem persistence working

**Dependencies:** Phase 3 complete, Nowledge Mem running

---

### Milestone 4.2: Memory Distillation

**Objective:** Extract and save key insights

**Tasks:**
1. Implement insight extraction from summary
2. Call `memory_add` for each insight
3. Tag with appropriate labels

**Deliverables:**
- Automatic memory distillation

**Dependencies:** Milestone 4.1

---

## Implementation Timeline

```
Phase 1: Core Infrastructure
├── M1.1: Directory Structure     [1 hour]
├── M1.2: PreCompact Hook         [3 hours]
└── M1.3: SessionStart Hook       [1 hour]

Phase 2: User Interface
├── M2.1: Slash Command           [1 hour]
└── M2.2: Session Manager Skill   [1 hour]

Phase 3: Testing & Polish
├── M3.1: Integration Testing     [1 hour]
└── M3.2: Documentation           [30 min]

Total Phase 1-3: ~8-9 hours

Phase 4: Nowledge Integration (Future)
├── M4.1: MCP Integration         [2 hours]
└── M4.2: Memory Distillation     [2 hours]
```

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API rate limits | Medium | Medium | Implement retry with backoff |
| Large transcripts | Medium | Low | Chunk processing, truncate if needed |
| Hook timeout | Low | High | Optimize script, increase timeout |
| Missing API key | Medium | Medium | Clear error message, fallback |
| Transcript format change | Low | High | Version checking, graceful handling |

---

## Success Metrics

1. **Functionality:** All hooks trigger correctly on compaction
2. **Reliability:** 99% success rate on summary generation
3. **Performance:** Hook completes within 60 seconds
4. **Usability:** User can load sessions within 2 interactions
5. **Coverage:** Summary captures >90% of key session content

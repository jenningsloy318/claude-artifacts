# Task List: PreCompact Hook Implementation

**Date:** 2025-11-23 19:04 PST
**Status:** Ready for Review

---

## Task Breakdown

### Phase 1: Core Infrastructure

#### 1.1 Directory Structure & Configuration
- [ ] **T1.1.1** Create `.claude/hooks/` directory
- [ ] **T1.1.2** Create `.claude/summaries/` directory
- [ ] **T1.1.3** Create `.claude/commands/` directory
- [ ] **T1.1.4** Create `.claude/skills/session-manager/` directory
- [ ] **T1.1.5** Update `.claude/settings.local.json` with PreCompact hook config
- [ ] **T1.1.6** Update `.claude/settings.local.json` with SessionStart hook config

#### 1.2 PreCompact Hook Script
- [ ] **T1.2.1** Create `precompact.py` with input parsing and error handling
- [ ] **T1.2.2** Implement `parse_transcript()` function to read JSONL
- [ ] **T1.2.3** Implement `extract_conversation_content()` to categorize messages
- [ ] **T1.2.4** Implement `extract_files_modified()` from tool calls
- [ ] **T1.2.5** Implement `generate_summary()` with Claude API
- [ ] **T1.2.6** Implement `extract_topics()` from summary
- [ ] **T1.2.7** Implement `save_summary()` to write files
- [ ] **T1.2.8** Implement `update_index()` for summary tracking
- [ ] **T1.2.9** Add fallback handling for API failures
- [ ] **T1.2.10** Add logging for debugging
- [ ] **T1.2.11** Test PreCompact hook manually

#### 1.3 SessionStart Hook Script
- [ ] **T1.3.1** Create `session_start.py` with input parsing
- [ ] **T1.3.2** Implement event type detection (resume/startup/compact)
- [ ] **T1.3.3** Implement `load_latest_summary()` function
- [ ] **T1.3.4** Implement context formatting for output
- [ ] **T1.3.5** Test SessionStart hook manually

---

### Phase 2: User Interface

#### 2.1 Slash Command
- [ ] **T2.1.1** Create `.claude/commands/load-session.md`
- [ ] **T2.1.2** Document command usage and examples
- [ ] **T2.1.3** Test `/load-session` command

#### 2.2 Session Manager Skill
- [ ] **T2.2.1** Create `.claude/skills/session-manager/SKILL.md`
- [ ] **T2.2.2** Define trigger conditions
- [ ] **T2.2.3** Document available actions
- [ ] **T2.2.4** Test skill invocation

---

### Phase 3: Testing & Polish

#### 3.1 Integration Testing
- [ ] **T3.1.1** Test full workflow: session → compact → summary → reload
- [ ] **T3.1.2** Test edge case: empty session
- [ ] **T3.1.3** Test edge case: very long session
- [ ] **T3.1.4** Test edge case: API failure with fallback
- [ ] **T3.1.5** Test manual session loading via slash command
- [ ] **T3.1.6** Test session listing via skill

#### 3.2 Documentation & Cleanup
- [ ] **T3.2.1** Remove test/debug files
- [ ] **T3.2.2** Clean up debug logging
- [ ] **T3.2.3** Update project README (if applicable)
- [ ] **T3.2.4** Final code review

---

### Phase 4: Commit & Push
- [ ] **T4.1** Review all changes
- [ ] **T4.2** Stage files for commit
- [ ] **T4.3** Generate commit message using skill
- [ ] **T4.4** Commit changes
- [ ] **T4.5** Push to repository (if applicable)

---

## Priority Matrix

| Priority | Tasks | Rationale |
|----------|-------|-----------|
| **P0 - Critical** | T1.1.1-6, T1.2.1-8, T1.3.1-4 | Core functionality |
| **P1 - High** | T1.2.9-11, T1.3.5, T2.1.1-3 | Robustness & basic UI |
| **P2 - Medium** | T2.2.1-4, T3.1.1-6 | Enhanced UX & testing |
| **P3 - Low** | T3.2.1-4, T4.1-5 | Polish & deployment |

---

## Dependencies Graph

```
T1.1.1-6 (Directory Setup)
    │
    ├──▶ T1.2.1-11 (PreCompact Hook)
    │        │
    │        └──▶ T1.3.1-5 (SessionStart Hook)
    │                  │
    │                  ├──▶ T2.1.1-3 (Slash Command)
    │                  │
    │                  └──▶ T2.2.1-4 (Skill)
    │
    └──▶ T3.1.1-6 (Integration Testing)
              │
              └──▶ T3.2.1-4 (Cleanup)
                        │
                        └──▶ T4.1-5 (Commit/Push)
```

---

## Acceptance Criteria

### PreCompact Hook
- ✓ Triggers on `/compact` command
- ✓ Triggers on automatic compaction
- ✓ Reads full transcript before compression
- ✓ Generates comprehensive summary with LLM
- ✓ Saves summary to `.claude/summaries/{session_id}/`
- ✓ Updates index.json
- ✓ Creates/updates `latest` symlink
- ✓ Handles errors gracefully (non-blocking)

### SessionStart Hook
- ✓ Triggers after compaction (resume event)
- ✓ Loads most recent summary
- ✓ Injects context via stdout
- ✓ Handles missing summaries gracefully

### Slash Command
- ✓ `/load-session` loads latest session
- ✓ `/load-session {id}` loads specific session
- ✓ Shows helpful error if session not found

### Skill
- ✓ Lists available sessions
- ✓ Loads sessions on request
- ✓ Provides search functionality

---

## Files to Create/Modify

### New Files
```
.claude/
├── hooks/
│   ├── precompact.py           # PreCompact hook script
│   └── session_start.py        # SessionStart hook script
├── commands/
│   └── load-session.md         # Slash command
├── skills/
│   └── session-manager/
│       └── SKILL.md            # Session management skill
└── summaries/
    └── index.json              # Summary index (created at runtime)
```

### Modified Files
```
.claude/
└── settings.local.json         # Add hook configurations
```

---

## Estimated Effort

| Phase | Tasks | Estimated Time |
|-------|-------|---------------|
| Phase 1.1 | 6 tasks | 30 min |
| Phase 1.2 | 11 tasks | 2-3 hours |
| Phase 1.3 | 5 tasks | 45 min |
| Phase 2.1 | 3 tasks | 30 min |
| Phase 2.2 | 4 tasks | 30 min |
| Phase 3.1 | 6 tasks | 1 hour |
| Phase 3.2 | 4 tasks | 30 min |
| Phase 4 | 5 tasks | 15 min |
| **Total** | **44 tasks** | **~7-8 hours** |

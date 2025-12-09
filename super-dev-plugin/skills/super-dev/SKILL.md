---
name: super-dev
description: Coordinator-driven development workflow with parallel agent execution for implementing features, fixing bugs, improving performance, or refactoring code. Central Coordinator Agent orchestrates all phases and assigns tasks to specialized sub-agents.
---

# Super Dev Workflow

A coordinator-driven development system with parallel agent execution for all development tasks including bug fixes, new features, performance improvements, and refactoring.

**Announce at start:** "I'm using the super-dev skill to systematically implement this task with coordinator-driven orchestration."

## Architecture Overview

```
                    ┌─────────────────┐
                    │   super-dev     │
                    │     Skill       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Coordinator   │ ◄── Central Authority
                    │     Agent       │
                    └────────┬────────┘
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
    ▼                        ▼                        ▼
┌─────────┐            ┌─────────┐            ┌─────────┐
│Planning │            │Analysis │            │Execution│
│ Agents  │            │ Agents  │            │ Agents  │
└─────────┘            └─────────┘            └─────────┘
```

## When to Use

Activate this skill when user asks to:
- Fix a bug or issue
- Fix build warnings or errors
- Implement a new feature
- Improve an existing feature
- Improve performance
- Resolve deprecation warnings
- Refactor code

## Workflow Phases

The Coordinator Agent orchestrates these phases automatically:

```
Development Workflow Progress:
- [ ] Phase 0: Apply Dev Rules (establish coding standards)
- [ ] Phase 1: Specification Setup (identify/create spec directory)
- [ ] Phase 2: Requirements Clarification (gather requirements)
- [ ] Phase 3: Research (best practices, docs, patterns) [Time MCP]
- [ ] Phase 4: Debug Analysis (for bugs only) [grep/ast-grep]
- [ ] Phase 5: Code Assessment (architecture, style, frameworks) [grep/ast-grep]
- [ ] Phase 5.3: Architecture Design (for complex features - optional)
- [ ] Phase 5.5: UI/UX Design (for features with UI - optional)
- [ ] Phase 6: Specification Writing (tech spec, plan, tasks)
- [ ] Phase 7: Specification Review (validate against requirements)
- [ ] Phase 8: Execution & QA (PARALLEL: dev + qa executors)
- [ ] Phase 9: Code Review (spec-aware review using super-dev:code-reviewer)
- [ ] Iteration Rule: Loop Phase 8 and Phase 9 until no blocking issues remain (no Critical/High/Medium findings; all acceptance criteria met)
- [ ] Phase 10: Documentation Update (docs-executor sequential)
- [ ] Phase 11: Cleanup (remove temp files, unused code)
- [ ] Phase 12: Commit & Push (descriptive message)
- [ ] Phase 13: Final Verification (Coordinator verifies all complete)
```

**CHECKPOINT RULE:** Coordinator ensures commits at each phase boundary.

---

## Entry Point: Coordinator Agent

**AGENT:** Invoke `super-dev:coordinator`

The Coordinator Agent is the CENTRAL AUTHORITY that:
1. Orchestrates ALL workflow phases
2. Assigns tasks to specialized sub-agents
3. Monitors execution - no unauthorized stops
4. Enforces quality gates
5. Manages build queue (Rust/Go serialization)
6. Performs final verification

```
Task(
  prompt: "Implement: [task description]",
  context: {
    task_type: "feature|bug|refactor|improvement",
    spec_directory: "[path to spec]"
  },
  subagent_type: "super-dev:coordinator"
)
```

---

## Individual Phase Commands

For granular control, you can invoke individual phases using slash commands:

| Phase | Command | Purpose |
|-------|---------|---------|
| 3 | `/super-dev:research [topic]` | Research - find best practices with Time MCP |
| 4 | `/super-dev:debug-analysis [bug details]` | Debug Analysis - root cause analysis (bugs only) |
| 5 | `/super-dev:code-assessment [feature]` | Code Assessment - evaluate existing codebase |
| 5.3 | `/super-dev:architecture-design [requirements]` | Architecture Design - create ADRs (complex features) |
| 5.5 | `/super-dev:ui-ux-design [UI requirements]` | UI/UX Design - design specifications (UI features) |
| 8 | `/super-dev:execute [spec path]` | Execution & QA - implement code with parallel testing |
| 9 | `/super-dev:code-review [changes]` | Code Review - spec-aware review using super-dev:code-reviewer |
| 10 | `/super-dev:documentation [spec path]` | Documentation Update - update all documentation |

**When to use individual phases:**
- When you need granular control over the workflow
- To re-run a specific phase after making corrections
- For learning or debugging the development process
- When working on very small tasks that don't need the full workflow

---

## Documentation Update Rules (CRITICAL - MANDATORY)

**At every milestone/phase boundary, update these documents:**

### 1. Task List Updates (`[index]-task-list.md`)
- [ ] Mark completed tasks with `[x]`
- [ ] Add any new tasks discovered during implementation
- [ ] Note any blocked or deferred tasks with reasons

### 2. Implementation Summary Updates (`[index]-implementation-summary.md`)
- [ ] Add completed work to "Code Changes" section
- [ ] Document any technical decisions made
- [ ] Record challenges encountered and solutions found

### 3. Specification Updates (`[index]-specification.md`)
- [ ] Update affected sections with `[UPDATED: date]` marker
- [ ] Document why the change was necessary

**FORBIDDEN:**
❌ Completing a milestone without updating task list
❌ Moving to next phase with outdated implementation summary
❌ Changing implementation without updating specification

---

## Phase 0: Apply Dev Rules

**SKILL:** Invoke `super-dev:dev-rules`

Establishes coding standards, git practices, and quality standards.

---

## Phase 1: Specification Setup

Analyze information and identify/create spec directory under `specification/`.

---

## Phase 2: Requirements Clarification

**AGENT:** Invoke `super-dev:requirements-clarifier`

**Output:** `01-requirements.md`

---

## Phase 3: Research Phase (Time MCP Enhanced)

**AGENT:** Invoke `super-dev:research-agent`

The research-agent:
- Gets current timestamp via Time MCP
- Adds year context to queries
- Filters by recency
- Flags deprecated information

**Output:** `02-research-report.md` with freshness scores

---

## Phase 4: Debug Analysis (grep/ast-grep Enhanced)

**AGENT:** Invoke `super-dev:debug-analyzer`

The debug-analyzer:
- Uses Grep for text pattern search
- Uses ast-grep for structural analysis
- Tracks file coverage for debugging scope

**Output:** `03-debug-analysis.md`

---

## Phase 5: Code Assessment (grep/ast-grep Enhanced)

**AGENT:** Invoke `super-dev:code-assessor`

The code-assessor:
- Uses Grep for pattern matching
- Uses ast-grep for structural analysis
- Tracks file coverage percentage

**Output:** `04-assessment.md`

---

## Phase 5.3: Architecture Design (Complex Features)

**AGENT:** Invoke `super-dev:architecture-agent`

**Output:** `05-architecture.md` and ADRs

---

## Phase 5.5: UI/UX Design (Features with UI)

**AGENT:** Invoke `super-dev:ui-ux-designer`

**Output:** `05-design-spec.md`

---

## Phase 6: Specification Writing

**AGENT:** Invoke `super-dev:spec-writer`

**Output:** Three files (or sub-specifications for large features)
- `06-specification.md` - Technical specification
- `07-implementation-plan.md` - Implementation plan
- `08-task-list.md` - Task list
(Or sub-specifications for large features)

---

## Phase 7: Specification Review

Coordinator reviews all documents for alignment and completeness.

---

## Phase 8: Execution & QA (PARALLEL Agents)

**CRITICAL CHANGE:** The Coordinator invokes TWO agents in PARALLEL:

```
┌─────────────────────────────────────────────────────────────┐
│                PARALLEL EXECUTION & QA                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐                           │
│  │dev-executor │  │   qa-agent  │                           │
│  │             │  │             │                           │
│  │ Implements  │  │ Plans & runs│                           │
│  │ code        │  │ tests       │                           │
│  │             │  │             │                           │
│  └─────────────┘  └─────────────┘                           │
│                          │                                   │
│                   BUILD QUEUE                                │
│              (Rust/Go: one at a time)                       │
└─────────────────────────────────────────────────────────────┘
```

**Agents:**
- `super-dev:dev-executor` - Implements code, invokes specialist developers
- `super-dev:qa-agent` - Modality-specific testing and verification (merged planning + execution)

**Build Policy (Rust/Go):**
- Only ONE build at a time
- Coordinator manages build queue
- Prevents resource conflicts

**Output:** Code, tests, and progress tracking

---

## Phase 9: Code Review

**AGENT:** Invoke `super-dev:code-reviewer`

Run specification-aware code review focused on correctness, security, performance, and maintainability. Scope to changed files and implementation summary; reference acceptance criteria from the spec.

**Iteration Rule (Coordinator-Enforced):**
- If verdict is Blocked or Changes Requested, or any Critical/High/Medium findings exist, or any acceptance criteria are Not Met/Partial → RE-ENTER Phase 8
- Create remediation tasks mapped from findings, run Execution & QA in parallel, then re-run Code Review
- Only proceed beyond Phase 9 when verdict is Approved or Approved with Comments (Low/Info only) and all acceptance criteria are met

**Output:** Code review report with severity, evidence, and verdict

---

## Phase 10: Documentation Update (Sequential)

**AGENT:** Invoke `super-dev:docs-executor`

After code review is complete and approved, update all documentation:
- Task list completion status
- Implementation summary with all changes
- Specification updates for any deviations
- Review findings integration

**Execution Model:** Sequential batch processing
- Runs after Phase 9 approval
- Processes all accumulated changes from Phases 8-9
- Single pass to update all documents
- Coordinates commit with code changes

**Output:** Updated `08-task-list.md`, `09-implementation-summary.md`, and `06-specification.md`

---

## Phase 11-12: Cleanup & Commit

Coordinator ensures:
1. No temp files remain
2. All changes committed
3. Descriptive commit messages

---

## Phase 13: Final Verification

Coordinator verifies:
- [ ] All specification documents created
- [ ] Implementation summary complete
- [ ] No missing code or files
- [ ] All changes committed
- [ ] All changes pushed to remote
- [ ] Git status clean (working tree clean)

### MANDATORY: Commit and Push on Completion

**CRITICAL REQUIREMENT:** When ALL tasks are complete, you MUST:

1. **Stage all changes**: `git add [files]` (only files modified in this session)
2. **Commit with descriptive message**: Follow project commit conventions
3. **Push to remote**: `git push` to ensure changes are not lost
4. **Verify clean state**: `git status` must show "working tree clean"

**NEVER** mark workflow as complete without committing and pushing all changes.

---

## Agents Reference

### Coordinator Agent (NEW - Central Authority)

| Agent | Purpose | Invoke Via |
|-------|---------|------------|
| `coordinator` | Central orchestrator for all phases | `super-dev:coordinator` |

### Executor Agents (NEW - Parallel & Sequential Execution)

| Agent | Purpose | Execution Mode | Invoke Via |
|-------|---------|----------------|------------|
| `super-dev:dev-executor` | Development implementation | Parallel (Phase 8) | `super-dev:dev-executor` |
| `super-dev:qa-agent` | Testing and verification (merged) | Parallel (Phase 8) | `super-dev:qa-agent` |
| `super-dev:docs-executor` | Documentation updates | Sequential (Phase 10) | `super-dev:docs-executor` |

### Workflow Agents

| Agent | Purpose | Invoke Via |
|-------|---------|------------|
| `super-dev:requirements-clarifier` | Gather requirements | `super-dev:requirements-clarifier` |
| `super-dev:research-agent` | Research with Time MCP | `super-dev:research-agent` |
| `super-dev:search-agent` | Multi-source search | `super-dev:search-agent` |
| `super-dev:debug-analyzer` | Root cause analysis (grep/ast-grep) | `super-dev:debug-analyzer` |
| `super-dev:code-assessor` | Assess codebase (grep/ast-grep) | `super-dev:code-assessor` |
| `super-dev:code-reviewer` | Specification-aware code review | `super-dev:code-reviewer` |
| `super-dev:architecture-agent` | Design architecture and create ADRs | `super-dev:architecture-agent` |
| `super-dev:ui-ux-designer` | Create UI/UX design specifications | `super-dev:ui-ux-designer` |
| `super-dev:spec-writer` | Write specifications | `super-dev:spec-writer` |
| `super-dev:qa-agent` | Modality-specific QA testing | `super-dev:qa-agent` |

### Developer Agents (Specialists)

| Agent | Purpose | Languages/Frameworks |
|-------|---------|---------------------|
| `super-dev:rust-developer` | Rust systems programming | Rust 1.75+, Tokio, axum |
| `super-dev:golang-developer` | Go backend development | Go 1.21+, stdlib, gin, chi |
| `super-dev:frontend-developer` | Web frontend development | React 19, Next.js 15, TypeScript, Tailwind v4 |
| `super-dev:backend-developer` | Backend/API development | Node.js/TS, Python, FastAPI, databases |
| `super-dev:android-developer` | Android app development | Kotlin, Jetpack Compose, MVVM |
| `super-dev:ios-developer` | iOS app development | Swift, SwiftUI, async/await |
| `super-dev:windows-app-developer` | Windows desktop development | C#/.NET 8+, WinUI 3, WPF |
| `super-dev:macos-app-developer` | macOS desktop development | Swift, SwiftUI, AppKit |

## Skills Reference

| Skill | Purpose |
|-------|---------|
| `super-dev:dev-rules` | Core development rules and philosophy |

## Key Differences from Previous Version

1. **Coordinator Agent**: Central authority orchestrates all phases
2. **Parallel Execution**: dev/qa executors run simultaneously in Phase 8
3. **Sequential Documentation**: docs-executor runs in Phase 10 after code review approval
4. **Build Queue**: Rust/Go builds serialized (one at a time)
5. **Time MCP**: Research agent uses current timestamp
6. **grep/ast-grep**: Assessment/debug agents use code search skills
7. **Final Verification**: Coordinator verifies all artifacts complete

## Notes

All agents are provided by this plugin (`super-dev:*` prefix). The plugin is self-contained.

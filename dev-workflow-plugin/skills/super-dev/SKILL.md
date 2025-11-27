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
- [ ] Phase 8-9: Execution (PARALLEL: dev + qa + docs executors)
- [ ] Phase 9.5: Quality Assurance (modality-specific testing)
- [ ] Phase 10: Cleanup (remove temp files, unused code)
- [ ] Phase 11: Commit & Push (descriptive message)
- [ ] Phase 12: Final Verification (Coordinator verifies all complete)
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

**Output:** `[index]-requirements.md`

---

## Phase 3: Research Phase (Time MCP Enhanced)

**AGENT:** Invoke `super-dev:research-agent`

The research-agent:
- Gets current timestamp via Time MCP
- Adds year context to queries
- Filters by recency
- Flags deprecated information

**Output:** `[index]-research-report.md` with freshness scores

---

## Phase 4: Debug Analysis (grep/ast-grep Enhanced)

**AGENT:** Invoke `super-dev:debug-analyzer`

The debug-analyzer:
- Uses Grep for text pattern search
- Uses ast-grep for structural analysis
- Tracks file coverage for debugging scope

**Output:** `[index]-debug-analysis.md`

---

## Phase 5: Code Assessment (grep/ast-grep Enhanced)

**AGENT:** Invoke `super-dev:code-assessor`

The code-assessor:
- Uses Grep for pattern matching
- Uses ast-grep for structural analysis
- Tracks file coverage percentage

**Output:** `[index]-assessment.md`

---

## Phase 5.3: Architecture Design (Complex Features)

**AGENT:** Invoke `super-dev:architecture-agent`

**Output:** `[index]-architecture.md` and ADRs

---

## Phase 5.5: UI/UX Design (Features with UI)

**AGENT:** Invoke `super-dev:ui-ux-designer`

**Output:** `[index]-design-spec.md`

---

## Phase 6: Specification Writing

**AGENT:** Invoke `super-dev:spec-writer`

**Output:** Three files (or sub-specifications for large features)

---

## Phase 7: Specification Review

Coordinator reviews all documents for alignment and completeness.

---

## Phase 8-9: Execution (PARALLEL Agents)

**CRITICAL CHANGE:** The Coordinator invokes THREE agents in PARALLEL:

```
┌─────────────────────────────────────────────────────────────┐
│                    PARALLEL EXECUTION                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │dev-executor │  │ qa-executor │  │docs-executor│         │
│  │             │  │             │  │             │         │
│  │ Implements  │  │ Writes and  │  │ Updates     │         │
│  │ code        │  │ runs tests  │  │ task-list   │         │
│  │             │  │             │  │ impl-summary│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                   │
│                   BUILD QUEUE                                │
│              (Rust/Go: one at a time)                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Agents:**
- `super-dev:dev-executor` - Implements code, invokes specialist developers
- `super-dev:qa-executor` - Writes tests, verifies builds
- `super-dev:docs-executor` - Updates documentation in real-time

**Build Policy (Rust/Go):**
- Only ONE build at a time
- Coordinator manages build queue
- Prevents resource conflicts

**Output:** Code, tests, and `[index]-implementation-summary.md`

---

## Phase 9.5: Quality Assurance

**AGENT:** Invoke `super-dev:qa-agent`

Modality-specific testing (CLI, Desktop UI, Web App).

**Output:** Test plan and results

---

## Phase 10-11: Cleanup & Commit

Coordinator ensures:
1. No temp files remain
2. All changes committed
3. Descriptive commit messages

---

## Phase 12: Final Verification

Coordinator verifies:
- [ ] All specification documents created
- [ ] Implementation summary complete
- [ ] No missing code or files
- [ ] All changes committed
- [ ] Git status clean

---

## Agents Reference

### Coordinator Agent (NEW - Central Authority)

| Agent | Purpose | Invoke Via |
|-------|---------|------------|
| `coordinator` | Central orchestrator for all phases | `super-dev:coordinator` |

### Executor Agents (NEW - Parallel Execution)

| Agent | Purpose | Invoke Via |
|-------|---------|------------|
| `dev-executor` | Development implementation | `super-dev:dev-executor` |
| `qa-executor` | Testing and verification | `super-dev:qa-executor` |
| `docs-executor` | Documentation updates | `super-dev:docs-executor` |

### Workflow Agents

| Agent | Purpose | Invoke Via |
|-------|---------|------------|
| `requirements-clarifier` | Gather requirements | `super-dev:requirements-clarifier` |
| `research-agent` | Research with Time MCP | `super-dev:research-agent` |
| `search-agent` | Multi-source search | `super-dev:search-agent` |
| `debug-analyzer` | Root cause analysis (grep/ast-grep) | `super-dev:debug-analyzer` |
| `code-assessor` | Assess codebase (grep/ast-grep) | `super-dev:code-assessor` |
| `code-reviewer` | Specification-aware code review | `super-dev:code-reviewer` |
| `architecture-agent` | Design architecture and create ADRs | `super-dev:architecture-agent` |
| `ui-ux-designer` | Create UI/UX design specifications | `super-dev:ui-ux-designer` |
| `spec-writer` | Write specifications | `super-dev:spec-writer` |
| `qa-agent` | Modality-specific QA testing | `super-dev:qa-agent` |

### Developer Agents (Specialists)

| Agent | Purpose | Languages/Frameworks |
|-------|---------|---------------------|
| `rust-developer` | Rust systems programming | Rust 1.75+, Tokio, axum |
| `golang-developer` | Go backend development | Go 1.21+, stdlib, gin, chi |
| `frontend-developer` | Web frontend development | React 19, Next.js 15, TypeScript, Tailwind v4 |
| `backend-developer` | Backend/API development | Node.js/TS, Python, FastAPI, databases |
| `android-developer` | Android app development | Kotlin, Jetpack Compose, MVVM |
| `ios-developer` | iOS app development | Swift, SwiftUI, async/await |
| `windows-app-developer` | Windows desktop development | C#/.NET 8+, WinUI 3, WPF |
| `macos-app-developer` | macOS desktop development | Swift, SwiftUI, AppKit |

## Skills Reference

| Skill | Purpose |
|-------|---------|
| `super-dev:dev-rules` | Core development rules and philosophy |

## Key Differences from Previous Version

1. **Coordinator Agent**: Central authority orchestrates all phases
2. **Parallel Execution**: dev/qa/docs executors run simultaneously
3. **Build Queue**: Rust/Go builds serialized (one at a time)
4. **Time MCP**: Research agent uses current timestamp
5. **grep/ast-grep**: Assessment/debug agents use code search skills
6. **Final Verification**: Coordinator verifies all artifacts complete

## Notes

All agents are provided by this plugin (`super-dev:*` prefix). The plugin is self-contained.

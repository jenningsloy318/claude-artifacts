# Architecture Design: Coordinator-Driven Development Plugin

**Date:** 2025-11-27
**Author:** Claude
**Status:** Draft

## 1. Executive Summary

This document defines the architecture for transforming the dev-workflow plugin into a coordinator-driven development system with parallel agent execution, build serialization, and comprehensive phase orchestration.

## 2. System Overview

### 2.1 High-Level Architecture

```
                         ┌─────────────────────────────────┐
                         │        super-dev Skill          │
                         │   (Entry Point & Dispatcher)    │
                         └─────────────┬───────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         COORDINATOR AGENT                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Phase     │  │   Task      │  │   Monitor   │  │   Quality   │     │
│  │  Manager    │  │  Assigner   │  │  & Oversight│  │   Gate      │     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  PLANNING       │ │  ANALYSIS       │ │  EXECUTION      │
│  AGENTS         │ │  AGENTS         │ │  AGENTS         │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ requirements    │ │ research-agent  │ │ dev-executor    │
│ clarifier       │ │ (+ time MCP)    │ │ qa-executor     │
│ architecture    │ │ debug-analyzer  │ │ docs-executor   │
│ ui-ux-designer  │ │ (+ grep/ast)    │ │ [dev agents]    │
│ spec-writer     │ │ code-assessor   │ │                 │
│                 │ │ (+ grep/ast)    │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 2.2 Design Principles

1. **Central Authority**: Coordinator is single source of truth for workflow state
2. **Delegation-Only**: Coordinator delegates all work, never implements directly
3. **Parallel Where Possible**: Maximize parallelism in execution phase
4. **Serialize Where Required**: Build operations serialized for Rust/Go
5. **No Unauthorized Stops**: Workflow continues until completion or critical error
6. **Comprehensive Verification**: Final phase verifies all artifacts

## 3. Component Architecture

### 3.1 Coordinator Agent

**File:** `agents/coordinator.md`

**Responsibilities:**
```
┌─────────────────────────────────────────────────────────┐
│                   COORDINATOR AGENT                      │
├─────────────────────────────────────────────────────────┤
│ 1. PHASE MANAGEMENT                                      │
│    • Determine current phase                             │
│    • Transition between phases                           │
│    • Skip optional phases when not applicable            │
│                                                          │
│ 2. TASK ASSIGNMENT                                       │
│    • Select appropriate sub-agent for each phase         │
│    • Construct context for sub-agent                     │
│    • Invoke sub-agent via Task tool                      │
│                                                          │
│ 3. MONITORING & OVERSIGHT                                │
│    • Track sub-agent progress                            │
│    • Detect incomplete or failed tasks                   │
│    • Enforce no-pause/no-skip policy                     │
│                                                          │
│ 4. QUALITY GATES                                         │
│    • Verify phase outputs before proceeding              │
│    • Validate build success (when applicable)            │
│    • Check test results                                  │
│                                                          │
│ 5. STATE MANAGEMENT                                      │
│    • Maintain workflow state                             │
│    • Track completed phases                              │
│    • Manage task list progress                           │
│                                                          │
│ 6. FINAL VERIFICATION                                    │
│    • Verify all documents created                        │
│    • Check for missing code/files                        │
│    • Ensure commits/pushes completed                     │
└─────────────────────────────────────────────────────────┘
```

**Phase Flow:**
```
┌────────────────────────────────────────────────────────────────┐
│                    COORDINATOR PHASE FLOW                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐              │
│   │  Phase 0 │────▶│  Phase 1 │────▶│  Phase 2 │              │
│   │Dev Rules │     │Spec Setup│     │  Reqs    │              │
│   └──────────┘     └──────────┘     └────┬─────┘              │
│                                          │                     │
│                                          ▼                     │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐              │
│   │ Phase 5  │◀────│  Phase 4 │◀────│  Phase 3 │              │
│   │Assessment│     │Debug(opt)│     │ Research │              │
│   └────┬─────┘     └──────────┘     └──────────┘              │
│        │                                                       │
│        ▼                                                       │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐              │
│   │Phase 5.3 │────▶│Phase 5.5 │────▶│  Phase 6 │              │
│   │Arch(opt) │     │ UI(opt)  │     │Spec Write│              │
│   └──────────┘     └──────────┘     └────┬─────┘              │
│                                          │                     │
│                                          ▼                     │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐              │
│   │ Phase 9  │◀────│Phase 8-9 │◀────│  Phase 7 │              │
│   │   QA     │     │Execution │     │  Review  │              │
│   └────┬─────┘     └──────────┘     └──────────┘              │
│        │                                                       │
│        ▼                                                       │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐              │
│   │ Phase 10 │────▶│ Phase 11 │────▶│ Phase 12 │              │
│   │ Cleanup  │     │  Commit  │     │ Verify   │              │
│   └──────────┘     └──────────┘     └──────────┘              │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 3.2 Execution Phase Architecture (Parallel Agents)

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTION PHASE (PARALLEL)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                      ┌───────────────┐                          │
│                      │  Coordinator  │                          │
│                      │ (Task Queue)  │                          │
│                      └───────┬───────┘                          │
│                              │                                   │
│           ┌──────────────────┼──────────────────┐               │
│           │                  │                  │               │
│           ▼                  ▼                  ▼               │
│    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│    │dev-executor │    │ qa-executor │    │docs-executor│       │
│    │             │    │             │    │             │       │
│    │• Implement  │    │• Run tests  │    │• Update     │       │
│    │  code       │    │• Verify     │    │  task-list  │       │
│    │• Build      │    │  builds     │    │• Update     │       │
│    │• Fix errors │    │• Document   │    │  impl-sum   │       │
│    │             │    │  results    │    │• Update spec│       │
│    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘       │
│           │                  │                  │               │
│           └──────────────────┼──────────────────┘               │
│                              │                                   │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │   BUILD QUEUE   │                          │
│                    │ (Rust/Go only)  │                          │
│                    │                 │                          │
│                    │ Only 1 build    │                          │
│                    │ at a time       │                          │
│                    └─────────────────┘                          │
│                                                                  │
│    TASK COMPLETION FLOW:                                        │
│    1. Task assigned to parallel agents                          │
│    2. Agents work concurrently                                  │
│    3. Build requests queued (serialized)                        │
│    4. On task complete: commit code + docs                      │
│    5. Coordinator assigns next task                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Research Agent Enhancement

```
┌─────────────────────────────────────────────────────────────────┐
│                   RESEARCH AGENT (Enhanced)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   INPUT:                                                         │
│   ┌─────────────────────────────────────────────────────┐       │
│   │ • Research topic                                     │       │
│   │ • Current timestamp (from Time MCP)                  │ ◀─NEW│
│   │ • Search context (technologies, focus areas)         │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                  │
│   PROCESS:                                                       │
│   ┌─────────────────────────────────────────────────────┐       │
│   │ 1. Get current date/time via Time MCP                │ ◀─NEW│
│   │ 2. Expand query with time context                    │ ◀─NEW│
│   │    "React hooks 2025" instead of "React hooks"       │       │
│   │ 3. Search via search-agent                           │       │
│   │ 4. Filter results by recency (prefer < 1 year old)   │ ◀─NEW│
│   │ 5. Validate sources are current                      │ ◀─NEW│
│   │ 6. Synthesize findings                               │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                  │
│   OUTPUT:                                                        │
│   ┌─────────────────────────────────────────────────────┐       │
│   │ • Research report with current date header           │       │
│   │ • Sources with publication dates                     │       │
│   │ • "Last updated" indicators                          │       │
│   │ • Deprecation warnings if applicable                 │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.4 Code Assessment / Debug Analysis Enhancement

```
┌─────────────────────────────────────────────────────────────────┐
│              CODE ASSESSOR / DEBUG ANALYZER (Enhanced)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   SEARCH STRATEGY:                                               │
│   ┌─────────────────────────────────────────────────────┐       │
│   │                                                      │       │
│   │   1. Use Grep skill for text pattern matching        │ ◀─NEW│
│   │      • Function definitions                          │       │
│   │      • Error patterns                                │       │
│   │      • Configuration values                          │       │
│   │                                                      │       │
│   │   2. Use ast-grep skill for structural analysis      │ ◀─NEW│
│   │      • Class/struct definitions                      │       │
│   │      • Function signatures                           │       │
│   │      • Import statements                             │       │
│   │      • Design patterns                               │       │
│   │                                                      │       │
│   │   3. Comprehensive file coverage                     │ ◀─NEW│
│   │      • Enumerate all source files                    │       │
│   │      • Track analyzed vs unanalyzed                  │       │
│   │      • Report coverage percentage                    │       │
│   │                                                      │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                  │
│   SKILL INVOCATION:                                              │
│   ┌─────────────────────────────────────────────────────┐       │
│   │ Skill(skill: "ast-grep")                             │       │
│   │ # For structural code search patterns                │       │
│   │                                                      │       │
│   │ Grep(pattern: "...", path: "src/")                   │       │
│   │ # For text pattern matching                          │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 4. Data Flow Architecture

### 4.1 Task Assignment Flow

```
┌────────────────────────────────────────────────────────────────┐
│                    TASK ASSIGNMENT FLOW                         │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Coordinator receives task from task-list                      │
│        │                                                        │
│        ▼                                                        │
│   ┌──────────────────────────────────────────────────┐         │
│   │ 1. Determine task type (dev/test/docs)           │         │
│   │ 2. Select appropriate executor agent             │         │
│   │ 3. Build context object                          │         │
│   │    • specification                               │         │
│   │    • implementation-plan                         │         │
│   │    • task details                                │         │
│   │    • relevant code context                       │         │
│   └──────────────────────────────────────────────────┘         │
│        │                                                        │
│        ▼                                                        │
│   Task(                                                         │
│     prompt: "Execute task: [description]",                      │
│     context: { ... },                                           │
│     subagent_type: "super-dev:dev-executor"                     │
│   )                                                             │
│        │                                                        │
│        ▼                                                        │
│   ┌──────────────────────────────────────────────────┐         │
│   │ Agent executes task                              │         │
│   │ • May invoke specialist agents (rust, frontend)  │         │
│   │ • Reports completion status                      │         │
│   │ • Returns artifacts (files created/modified)     │         │
│   └──────────────────────────────────────────────────┘         │
│        │                                                        │
│        ▼                                                        │
│   Coordinator verifies and commits                              │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 4.2 Build Queue Management

```
┌────────────────────────────────────────────────────────────────┐
│                    BUILD QUEUE (Rust/Go)                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   POLICY: Only ONE build at a time                              │
│                                                                 │
│   ┌──────────────────────────────────────────────────┐         │
│   │ BUILD REQUEST HANDLING:                          │         │
│   │                                                  │         │
│   │ 1. Agent requests build                          │         │
│   │ 2. Coordinator checks build queue                │         │
│   │    IF queue empty:                               │         │
│   │      → Execute build                             │         │
│   │      → Mark queue as "building"                  │         │
│   │    IF queue busy:                                │         │
│   │      → Wait for current build                    │         │
│   │      → Then execute                              │         │
│   │ 3. Build completes                               │         │
│   │    → Mark queue as "idle"                        │         │
│   │    → Return result to requesting agent           │         │
│   └──────────────────────────────────────────────────┘         │
│                                                                 │
│   STATE DIAGRAM:                                                │
│                                                                 │
│   ┌───────┐  build request  ┌──────────┐  build done ┌───────┐ │
│   │ IDLE  │────────────────▶│ BUILDING │────────────▶│ IDLE  │ │
│   └───────┘                 └──────────┘             └───────┘ │
│       ▲                          │                             │
│       │                          │ new request                 │
│       │                          ▼                             │
│       │                    ┌──────────┐                        │
│       └────────────────────│ QUEUED   │                        │
│          build done        └──────────┘                        │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## 5. Plugin Naming

**New Name:** `super-dev`

**Rationale:**
- Short and memorable
- Indicates enhanced/superior capabilities
- Easy to type: `super-dev:coordinator`, `super-dev:dev-executor`

**Changes Required:**
```
# plugin.json
{
  "name": "super-dev",  # was "dev-workflow"
  ...
}

# Skill directory
skills/super-dev/SKILL.md  # was skills/dev-workflow/SKILL.md

# Agent invocations
Task(subagent_type: "super-dev:coordinator")  # was dev-workflow:*
```

## 6. File Structure (Final)

```
dev-workflow-plugin/                    # Keep directory name
├── .claude-plugin/
│   └── plugin.json                     # name: "super-dev"
├── skills/
│   ├── super-dev/                      # Renamed from dev-workflow
│   │   └── SKILL.md
│   └── dev-rules/
│       └── SKILL.md                    # Unchanged
├── agents/
│   ├── coordinator.md                  # NEW - Central coordinator
│   ├── dev-executor.md                 # NEW - Development execution
│   ├── qa-executor.md                  # NEW - QA execution
│   ├── docs-executor.md                # NEW - Documentation execution
│   ├── requirements-clarifier.md       # Unchanged
│   ├── research-agent.md               # Updated - Time MCP
│   ├── search-agent.md                 # Unchanged
│   ├── debug-analyzer.md               # Updated - grep/ast-grep
│   ├── code-assessor.md                # Updated - grep/ast-grep
│   ├── code-reviewer.md                # Unchanged
│   ├── spec-writer.md                  # Unchanged
│   ├── qa-agent.md                     # Unchanged
│   ├── architecture-agent.md           # Unchanged
│   ├── ui-ux-designer.md               # Unchanged
│   ├── rust-developer.md               # Unchanged
│   ├── golang-developer.md             # Unchanged
│   ├── frontend-developer.md           # Unchanged
│   ├── backend-developer.md            # Unchanged
│   ├── ios-developer.md                # Unchanged
│   ├── android-developer.md            # Unchanged
│   ├── windows-app-developer.md        # Unchanged
│   └── macos-app-developer.md          # Unchanged
├── commands/
│   └── fix-impl.md                     # Updated for super-dev
└── README.md                           # Updated documentation
```

**Files Removed:**
- `agents/execution-coordinator.md` (replaced by new agents)

## 7. Architecture Decision Records (ADRs)

### ADR-001: Central Coordinator Pattern

**Context:** Need to orchestrate multiple phases with consistent behavior.

**Decision:** Create dedicated Coordinator Agent as central authority.

**Consequences:**
- (+) Single source of truth for workflow state
- (+) Consistent task assignment
- (+) Easier to add new phases
- (-) Single point of failure
- (-) Additional context overhead

### ADR-002: Parallel Execution in Execution Phase

**Context:** Execution phase has independent dev/test/docs work.

**Decision:** Run three executor agents in parallel.

**Consequences:**
- (+) Faster execution
- (+) Better resource utilization
- (-) More complex coordination
- (-) Build serialization required

### ADR-003: Build Serialization for Rust/Go

**Context:** Rust/Go builds consume significant resources.

**Decision:** Only one build at a time, managed by Coordinator.

**Consequences:**
- (+) Prevents resource conflicts
- (+) Predictable build behavior
- (-) Slower parallel execution
- (-) Build queue management needed

### ADR-004: Time MCP for Research

**Context:** Research needs current information.

**Decision:** Always include current timestamp from Time MCP.

**Consequences:**
- (+) Research uses latest information
- (+) Deprecation warnings possible
- (-) Dependency on Time MCP

### ADR-005: Plugin Renaming to super-dev

**Context:** Need new name reflecting coordinator-driven architecture.

**Decision:** Rename from "dev-workflow" to "super-dev".

**Consequences:**
- (+) Short, memorable name
- (+) Indicates enhanced capabilities
- (-) Breaking change for existing users
- (-) All references need updating

## 8. Next Steps

1. **Phase 6**: Write detailed specifications for each component
2. **Phase 7**: Review specifications for completeness
3. **Phase 8-9**: Implement components in order:
   - Coordinator agent
   - Executor agents
   - Research/Assessment updates
   - Plugin metadata and skill
4. **Phase 10-12**: Test, cleanup, commit

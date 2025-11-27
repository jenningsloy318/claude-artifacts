# Specification: Executor Agents

**Date:** 2025-11-27
**Author:** Claude
**Status:** Draft
**Parent:** [../00-master-specification.md]

## 1. Overview

Create three dedicated executor agents that run in parallel during the execution phase:
1. **dev-executor**: Development and code implementation
2. **qa-executor**: Testing and quality assurance
3. **docs-executor**: Documentation updates

## 2. Parallel Execution Model

```
Coordinator (Task Queue)
         │
    ┌────┴────┬───────────┐
    │         │           │
    ▼         ▼           ▼
dev-executor  qa-executor  docs-executor
    │         │           │
    └────┬────┴───────────┘
         │
    Build Queue (serialized for Rust/Go)
```

## 3. Agent Specifications

### 3.1 dev-executor

**File:** `agents/dev-executor.md`

**Responsibilities:**
- Implement code changes from task list
- Invoke specialist developer agents (rust, golang, frontend, etc.)
- Request builds through Coordinator
- Fix build errors and warnings
- Report completion status

**Specialist Agent Invocation:**
| Domain | Agent |
|--------|-------|
| Rust | `super-dev:rust-developer` |
| Go | `super-dev:golang-developer` |
| Frontend | `super-dev:frontend-developer` |
| Backend | `super-dev:backend-developer` |
| iOS | `super-dev:ios-developer` |
| Android | `super-dev:android-developer` |
| Windows | `super-dev:windows-app-developer` |
| macOS | `super-dev:macos-app-developer` |

### 3.2 qa-executor

**File:** `agents/qa-executor.md`

**Responsibilities:**
- Write unit tests for implemented code
- Write integration tests
- Run test suites
- Verify build passes
- Report test results and coverage

**Testing Patterns:**
- Use existing test framework in project
- Follow project test conventions
- Ensure test isolation
- Document edge cases

### 3.3 docs-executor

**File:** `agents/docs-executor.md`

**Responsibilities:**
- Update task-list.md (mark completed tasks)
- Update implementation-summary.md (add progress)
- Update specification.md (document deviations)
- Ensure docs committed with code

**Update Triggers:**
- After each task completion
- At milestone boundaries
- When spec changes needed

## 4. Build Queue (Rust/Go)

**Policy:** Only ONE build at a time

**Implementation:**
```
BUILD_QUEUE_STATE:
  - IDLE: No build in progress
  - BUILDING: Build in progress
  - QUEUED: Build request waiting

FLOW:
1. Agent requests build
2. IF IDLE:
     Execute build → BUILDING
   ELSE:
     Queue request → QUEUED
3. On build complete:
     IF QUEUED:
       Execute queued → BUILDING
     ELSE:
       → IDLE
```

**Languages Affected:**
- Rust (cargo build/cargo check)
- Go (go build/go test)

**Languages NOT Affected:**
- JavaScript/TypeScript (concurrent builds OK)
- Python (no build step)
- Other interpreted languages

## 5. Coordination Points

### 5.1 Task Completion Flow

```
1. dev-executor completes code change
2. dev-executor requests build
3. Coordinator queues build (if Rust/Go)
4. Build executes (one at a time)
5. qa-executor runs tests
6. docs-executor updates docs
7. ALL THREE report completion
8. Coordinator commits: git add (code + tests + docs)
9. Coordinator assigns next task
```

### 5.2 Error Handling

| Error | Handler | Action |
|-------|---------|--------|
| Build failure | dev-executor | Fix and rebuild |
| Test failure | qa-executor | Report to dev-executor |
| Missing docs | docs-executor | Create missing docs |
| All retries exhausted | Coordinator | Flag as blocked |

## 6. Acceptance Criteria

- [ ] dev-executor.md created with specialist agent mappings
- [ ] qa-executor.md created with testing patterns
- [ ] docs-executor.md created with update triggers
- [ ] Build queue logic documented
- [ ] Coordination points clear
- [ ] Error handling defined

---
name: super-dev:execute
description: Execute development and QA in parallel using specialized agents
---

# Phase 8: Execution & QA

Execute development implementation and quality assurance in parallel using specialized agents.

## Usage

```
/super-dev:phase-8 [specification directory path]
```

## What This Command Does

When invoked, this command activates THREE agents in PARALLEL:

1. **Dev Executor** (`super-dev:dev-executor`)
   - Implements code according to specifications
   - Invokes specialist developer agents as needed
   - Follows established patterns and standards

2. **QA Executor** (`super-dev:qa-executor`)
   - Writes tests for all implemented code
   - Verifies builds and functionality
   - Ensures quality standards are met

3. **Docs Executor** (`super-dev:docs-executor`)
   - Updates documentation in real-time
   - Maintains task list progress
   - Updates implementation summary

## Parallel Execution Architecture

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

## Build Policy

For Rust and Go projects:
- Only ONE build at a time
- Coordinator manages build queue
- Prevents resource conflicts

## Execution Process

### Dev Executor
- Reads `[index]-task-list.md` for tasks
- Implements features according to specifications
- Invokes specialist agents (rust-developer, frontend-developer, etc.)
- Follows established code patterns

### QA Executor
- Creates unit tests for new code
- Writes integration tests
- Verifies build success
- Tests functionality against requirements

### Docs Executor
- Updates task completion status
- Documents technical decisions
- Maintains `[index]-implementation-summary.md`
- Records challenges and solutions

## Arguments

`$ARGUMENTS` should specify:
- Path to specification directory
- Any specific implementation focus areas

## Output

Creates/updates:
- Implemented code files
- Test suites
- `[index]-implementation-summary.md`
- Updated `[index]-task-list.md`

## Notes

- Parallel execution maximizes efficiency
- Real-time documentation updates
- Quality gates enforced throughout
- Build queue managed for resource-intensive projects
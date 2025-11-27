# Super Dev Plugin

A coordinator-driven development workflow plugin for Claude Code with parallel agent execution for implementing features, fixing bugs, and refactoring code.

## Overview

This plugin provides a systematic 12-phase development workflow orchestrated by a **Coordinator Agent** that:

- Assigns tasks to specialized sub-agents
- Monitors execution - no unauthorized stops
- Enforces quality gates at each phase
- Manages build queue (Rust/Go serialization)
- Ensures parallel execution during implementation (dev + qa + docs)

## Installation

Add to your Claude Code settings:

```json
{
  "plugins": [
    "https://github.com/jenningsloy318/super-skill-claude-artifacts/tree/main/dev-workflow-plugin"
  ]
}
```

## Usage

### Command

```
/super-dev:fix-impl [description of task]
```

### Examples

```
/super-dev:fix-impl Fix the login button not responding on mobile
/super-dev:fix-impl Implement user profile page with avatar upload
/super-dev:fix-impl Refactor the authentication module for better testability
```

## Architecture

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

## Workflow Phases

| Phase | Name | Agent/Skill | Description |
|-------|------|-------------|-------------|
| 0 | Apply Dev Rules | `super-dev:dev-rules` skill | Establish coding standards |
| 1 | Specification Setup | Coordinator | Find or create spec directory |
| 2 | Requirements Clarification | `super-dev:requirements-clarifier` | Gather complete requirements |
| 3 | Research | `super-dev:research-agent` | Find best practices (Time MCP) |
| 4 | Debug Analysis | `super-dev:debug-analyzer` | Root cause analysis (grep/ast-grep) |
| 5 | Code Assessment | `super-dev:code-assessor` | Evaluate codebase (grep/ast-grep) |
| 5.3 | Architecture Design | `super-dev:architecture-agent` | For complex features (optional) |
| 5.5 | UI/UX Design | `super-dev:ui-ux-designer` | For features with UI (optional) |
| 6 | Specification Writing | `super-dev:spec-writer` | Create tech spec, plan, tasks |
| 7 | Specification Review | Coordinator | Validate all documents |
| 8-9 | Execution | **PARALLEL**: dev + qa + docs executors | Implement with parallel agents |
| 9.5 | Quality Assurance | `super-dev:qa-agent` | Modality-specific testing |
| 10-11 | Cleanup & Commit | Coordinator | Remove temp files, commit changes |
| 12 | Final Verification | Coordinator | Verify all complete |

## Plugin Structure

```
dev-workflow-plugin/
├── skills/
│   ├── super-dev/        # Main orchestrator skill
│   └── dev-rules/        # Development rules and philosophy
├── agents/
│   ├── coordinator.md          # Central Coordinator Agent
│   ├── dev-executor.md         # Development Executor
│   ├── qa-executor.md          # QA Executor
│   ├── docs-executor.md        # Documentation Executor
│   ├── requirements-clarifier.md
│   ├── research-agent.md       # Enhanced with Time MCP
│   ├── search-agent.md
│   ├── debug-analyzer.md       # Enhanced with grep/ast-grep
│   ├── code-assessor.md        # Enhanced with grep/ast-grep
│   ├── code-reviewer.md
│   ├── architecture-agent.md
│   ├── ui-ux-designer.md
│   ├── spec-writer.md
│   └── qa-agent.md
└── commands/
    └── fix-impl.md
```

## Agents

### Coordinator Agent (Central Authority)

The Coordinator Agent orchestrates ALL workflow phases:

- **Task Assignment**: Assigns correct sub-agent per phase
- **Monitoring**: Ensures no unauthorized stops or missing tasks
- **Build Queue**: Manages Rust/Go build serialization
- **Quality Gates**: Enforces checkpoints at phase boundaries
- **Final Verification**: Verifies all artifacts complete

**Invoke:** `Task(subagent_type: "super-dev:coordinator")`

### Executor Agents (Parallel Execution)

During Phase 8-9, THREE executors run in PARALLEL:

| Agent | Purpose | Invoke Via |
|-------|---------|------------|
| `dev-executor` | Implements code, invokes specialists | `super-dev:dev-executor` |
| `qa-executor` | Writes and runs tests | `super-dev:qa-executor` |
| `docs-executor` | Updates documentation in real-time | `super-dev:docs-executor` |

**Build Policy (Rust/Go):** Only ONE build at a time to prevent resource conflicts.

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

### Developer Specialists

The dev-executor invokes these specialists based on technology:

| Agent | Purpose | Languages/Frameworks |
|-------|---------|---------------------|
| `rust-developer` | Rust systems programming | Rust 1.75+, Tokio, axum |
| `golang-developer` | Go backend development | Go 1.21+, stdlib, gin, chi |
| `frontend-developer` | Web frontend development | React 19, Next.js 15, TypeScript |
| `backend-developer` | Backend/API development | Node.js/TS, Python, FastAPI |
| `android-developer` | Android app development | Kotlin, Jetpack Compose |
| `ios-developer` | iOS app development | Swift, SwiftUI |
| `windows-app-developer` | Windows desktop development | C#/.NET 8+, WinUI 3 |
| `macos-app-developer` | macOS desktop development | Swift, SwiftUI, AppKit |

## Key Features

### Time MCP Integration (Research Phase)

The research-agent uses Time MCP to:
- Get current timestamp for query context
- Add year context to searches
- Filter by recency (Fresh/Current/Dated/Outdated)
- Flag deprecated information

### grep/ast-grep Integration (Assessment/Debug)

The code-assessor and debug-analyzer use:
- **Grep**: Text pattern search for code analysis
- **ast-grep skill**: Structural code analysis
- **Coverage tracking**: Ensures all relevant files analyzed

### Parallel Execution (Implementation Phase)

Three executors run simultaneously:
- `dev-executor`: Implements code changes
- `qa-executor`: Writes and runs tests
- `docs-executor`: Updates documentation

### Build Queue (Rust/Go)

For Rust and Go projects:
- Only ONE build process at a time
- Prevents cargo/go build conflicts
- Coordinator manages queue priority

## Output Documents

All documents are created in `specification/[index]-[name]/` directory:

1. `[index]-requirements.md` - Clarified requirements
2. `[index]-research-report.md` - Research findings with freshness scores
3. `[index]-debug-analysis.md` - Debug analysis (bugs only)
4. `[index]-assessment.md` - Code assessment with coverage
5. `[index]-architecture.md` - Architecture design (complex features)
6. `[index]-design-spec.md` - UI/UX design (UI features)
7. `[index]-specification.md` - Technical specification
8. `[index]-implementation-plan.md` - Implementation plan
9. `[index]-task-list.md` - Detailed task list
10. `[index]-implementation-summary.md` - Final summary

## Skills

### super-dev

Main entry point skill that documents the workflow. The Coordinator Agent is invoked to orchestrate all phases.

### dev-rules

Core development rules and standards including:
- Git workflow rules
- Development philosophy (incremental development, pragmatic approach)
- Quality standards (testability, readability, consistency)
- Decision framework priorities

## License

MIT

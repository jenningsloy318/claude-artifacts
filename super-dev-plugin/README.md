# Super Dev Plugin

A comprehensive coordinator-driven development workflow plugin for Claude Code with parallel agent execution for implementing features, fixing bugs, and refactoring code.

**Enhanced with best practices from [everything-claude-code](https://github.com/affaan-m/everything-claude-code)**

## Overview

This plugin provides a systematic 12-phase development workflow orchestrated by a **Coordinator Agent** that:

- Assigns tasks to specialized sub-agents
- Monitors execution - no unauthorized stops
- Enforces quality gates at each phase
- Manages build queue (Rust/Go serialization)
- Ensures parallel execution during implementation (dev + qa + docs)

## Usage

### Main Command

```
/super-dev:run [description of task]
```

### Examples

```
/super-dev:run Fix the login button not responding on mobile
/super-dev:run Implement user profile page with avatar upload
/super-dev:run Refactor the authentication module for better testability
```

### Additional Commands

```
/plan - Implementation planning with planner agent
/tdd - Test-driven development workflow
/e2e - E2E test generation
/code-review - Quality and security review
/build-fix - Fix build errors
/refactor-clean - Dead code removal
/learn - Extract patterns mid-session
/test-coverage - Check test coverage
/update-docs - Update documentation
/update-codemaps - Update code maps
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

## Plugin Structure

```
super-dev-plugin/
├── agents/                    # Specialized agents (29 total)
│   ├── coordinator.md              # Central Coordinator Agent (super-dev unique)
│   ├── dev-executor.md             # Development Executor
│   ├── qa-executor.md              # QA Executor
│   ├── docs-executor.md            # Documentation Executor
│   ├── architecture-agent.md       # Architecture Design (super-dev unique)
│   ├── ui-ux-designer.md           # UI/UX Design (super-dev unique)
│   ├── spec-writer.md              # Specification Writer (super-dev unique)
│   ├── research-agent.md           # Research Agent (super-dev unique)
│   ├── code-reviewer.md            # Specification-Aware Review (super-dev unique)
│   ├── debug-analyzer.md           # Debug Analysis
│   ├── code-assessor.md            # Code Assessment
│   ├── requirements-clarifier.md   # Requirements Clarification
│   ├── search-agent.md             # Multi-Source Search
│   ├── qa-agent.md                 # QA Testing
│   │
│   # Additional agents:
│   ├── architect.md                # System Design
│   ├── build-error-resolver.md     # Build Error Resolution
│   ├── doc-updater.md              # Documentation Updates
│   ├── e2e-runner.md               # E2E Testing
│   ├── planner.md                  # Implementation Planning
│   ├── refactor-cleaner.md         # Dead Code Cleanup
│   ├── security-reviewer.md        # Security Analysis
│   ├── tdd-guide.md                # Test-Driven Development
│   │
│   # Developer Specialists:
│   ├── rust-developer.md
│   ├── golang-developer.md
│   ├── frontend-developer.md
│   ├── backend-developer.md
│   ├── android-developer.md
│   ├── ios-developer.md
│   ├── macos-app-developer.md
│   └── windows-app-developer.md
│
├── commands/                   # Slash commands (18 total)
│   # super-dev commands:
│   ├── run.md                     # Main entry point
│   ├── architecture-design.md
│   ├── code-assessment.md
│   ├── code-review.md
│   ├── debug-analysis.md
│   ├── documentation.md
│   ├── execute.md
│   ├── research.md
│   └── ui-ux-design.md
│   # Additional commands:
│   ├── build-fix.md
│   ├── e2e.md
│   ├── learn.md
│   ├── plan.md
│   ├── refactor-clean.md
│   ├── tdd.md
│   ├── test-coverage.md
│   ├── update-codemaps.md
│   └── update-docs.md
│
├── skills/                     # Skills (10 items)
│   # super-dev skills:
│   ├── super-dev/                 # Main orchestrator skill
│   └── dev-rules/                 # Core development rules and philosophy
│   # Additional skills:
│   ├── tdd-workflow/              # Test-Driven Development methodology
│   ├── security-review/           # Security checklist
│   ├── continuous-learning/       # Auto-extract patterns from sessions
│   ├── strategic-compact/         # Manual compaction suggestions
│   ├── backend-patterns.md        # API, database, caching patterns
│   ├── frontend-patterns.md       # React, Next.js patterns
│   ├── coding-standards.md        # Language best practices
│   └── project-guidelines-example.md
│
├── rules/                      # Always-follow guidelines (NEW - 8 files)
│   ├── agents.md                 # When to delegate to subagents
│   ├── coding-style.md           # Immutability, file organization
│   ├── git-workflow.md           # Commit format, PR process
│   ├── hooks.md                  # Hook usage guidelines
│   ├── patterns.md               # Common code patterns
│   ├── performance.md            # Model selection, context management
│   ├── security.md               # Mandatory security checks
│   └── testing.md                # TDD, coverage requirements
│
├── contexts/                   # Dynamic system prompt injection (NEW)
│   ├── dev.md                    # Development mode context
│   ├── review.md                 # Code review mode context
│   └── research.md               # Research/exploration mode context
│
├── hooks/                      # Trigger-based automations (NEW)
│   ├── hooks.json                # All hooks configuration
│   ├── memory-persistence/       # Session lifecycle hooks
│   │   ├── pre-compact.sh        # Save state before compaction
│   │   ├── session-start.sh      # Load previous context
│   │   └── session-end.sh        # Persist learnings on end
│   └── strategic-compact/        # Compaction suggestions
│       └── suggest-compact.sh
│
├── mcp-configs/                # MCP server configurations (NEW)
│   └── mcp-servers.json          # GitHub, Supabase, Vercel, Railway, etc.
│
├── plugins/                    # Plugin ecosystem documentation (NEW)
│   └── README.md                # Plugins and marketplaces guide
│
├── examples/                   # Example configurations (NEW)
│   ├── CLAUDE.md                # Example project-level config
│   ├── user-CLAUDE.md           # Example user-level config
│   └── statusline.json          # Example statusline config
│
└── scripts/                    # Utility scripts
    └── (existing scripts)
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

## Key Features

### Super-Dev Unique Features

1. **Coordinator Agent** - Central orchestrator for all workflow phases
2. **Git Worktree Requirement** - MANDATORY isolation for development
3. **Specification-Aware Code Review** - Validates against technical specs
4. **Parallel Execution** - Three executors run simultaneously (dev + qa + docs)
5. **Build Queue Management** - Rust/Go serialization for resource safety
6. **Time MCP Integration** - Freshness-aware research queries
7. **ast-grep Integration** - Structural code analysis for assessment/debug

### Additional Integrated Features

1. **TDD Workflow Skill** - Comprehensive test-driven development methodology
2. **Security Review Skill** - Security checklist and validation
3. **Continuous Learning** - Auto-extract patterns from sessions
4. **Strategic Compact** - Manual compaction suggestions
5. **Rules System** - Modular always-follow guidelines
6. **Contexts** - Dynamic system prompt injection (dev/review/research modes)
7. **Enhanced Hooks** - Memory persistence, console.log warnings, Prettier auto-format
8. **MCP Configurations** - Pre-configured MCP server templates
9. **Additional Agents** - planner, tdd-guide, security-reviewer, refactor-cleaner, etc.
10. **Additional Commands** - /plan, /tdd, /e2e, /learn, /refactor-clean, etc.

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
| `planner` | Implementation planning | `planner` |
| `tdd-guide` | Test-driven development | `tdd-guide` |
| `security-reviewer` | Security analysis | `security-reviewer` |
| `build-error-resolver` | Fix build errors | `build-error-resolver` |
| `refactor-cleaner` | Dead code cleanup | `refactor-cleaner` |
| `doc-updater` | Documentation sync | `doc-updater` |
| `e2e-runner` | Playwright E2E testing | `e2e-runner` |

## Skills

### super-dev

Main entry point skill that documents the workflow. The Coordinator Agent is invoked to orchestrate all phases.

### dev-rules

Core development rules and standards including:
- Git workflow rules (no GitHub Actions, selective commits)
- Git Worktree Requirement (CRITICAL - MANDATORY)
- Git Safety & Checkpoint Rules
- Development philosophy (incremental development, pragmatic approach)
- Quality standards (testability, readability, consistency)
- Decision framework priorities
- Figma MCP Integration Rules
- MCP Script Usage
- Time MCP Rules
- Codebase Search with ast-grep
- Documentation Update Rules

### tdd-workflow (NEW)

Comprehensive test-driven development methodology with:
- Tests BEFORE code requirement
- 80%+ minimum coverage (unit + integration + E2E)
- Test patterns for Jest/Vitest, Playwright
- Mocking external services
- Coverage verification
- Best practices and common mistakes

### security-review (NEW)

Security checklist and validation:
- No hardcoded secrets
- Input validation
- SQL injection prevention
- XSS/CSRF protection
- Authentication/authorization verification
- Rate limiting on endpoints
- Error message sanitization

### continuous-learning (NEW)

Auto-extract patterns from sessions:
- Runs on Stop hook (lightweight)
- Detects error_resolution, debugging_techniques, workarounds
- Saves learned skills to ~/.claude/skills/learned/
- Configurable min_session_length

### strategic-compact (NEW)

Manual compaction suggestions:
- Suggests compact at logical intervals
- After threshold tool calls
- When transitioning phases
- Preserves context through milestones

### coding-standards (NEW)

Language best practices reference.

### backend-patterns (NEW)

API, database, caching patterns.

### frontend-patterns (NEW)

React, Next.js patterns.

## Rules

The `rules/` directory contains modular always-follow guidelines:

- **agents.md** - When to delegate to subagents
- **coding-style.md** - Immutability, file organization, error handling
- **git-workflow.md** - Commit format, PR process
- **hooks.md** - Hook usage guidelines
- **patterns.md** - Common code patterns (API response format, custom hooks, repository pattern)
- **performance.md** - Model selection (Haiku/Sonnet/Opus), context window management
- **security.md** - Mandatory security checks
- **testing.md** - TDD, 80% coverage requirement

## Contexts

The `contexts/` directory provides dynamic system prompt injection:

- **dev.md** - Development mode (write code first, prefer working solutions)
- **review.md** - Code review mode (critical analysis, specification validation)
- **research.md** - Research mode (gather information, explore options)

## Hooks

The `hooks/` directory provides trigger-based automations:

### PreToolUse Hooks
- Block dev servers outside tmux
- Reminder to use tmux for long-running commands
- Pause before git push to review changes
- Block creation of unnecessary .md files
- Suggest manual compaction at logical intervals

### PostToolUse Hooks
- Log PR URL and provide review command after PR creation
- Auto-format JS/TS files with Prettier after edits
- TypeScript check after editing .ts/.tsx files
- Warn about console.log statements after edits

### SessionStart/Stop Hooks
- Load previous context on new session
- Save state before context compaction
- Persist learnings on session end
- Evaluate session for extractable patterns

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

## License

MIT

## Credits

- **super-dev-plugin** - Coordinator-driven development workflow
- **everything-claude-code** - Additional agents, commands, skills, hooks, rules, and configurations

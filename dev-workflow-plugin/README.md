# Dev Workflow Plugin

A comprehensive development workflow plugin for Claude Code that guides through structured phases for implementing features, fixing bugs, and refactoring code.

## Overview

This plugin provides a systematic 11-phase development workflow that ensures consistent, high-quality code delivery through:

- Structured specification and planning
- Research-driven implementation
- Parallel agent execution
- Built-in quality gates

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
/dev-workflow:fix-impl [description of task]
```

### Examples

```
/dev-workflow:fix-impl Fix the login button not responding on mobile
/dev-workflow:fix-impl Implement user profile page with avatar upload
/dev-workflow:fix-impl Refactor the authentication module for better testability
```

## Workflow Phases

| Phase | Name | Agent/Skill | Description |
|-------|------|-------------|-------------|
| 1 | Specification Setup | `dev-workflow` skill | Find or create spec directory |
| 2 | Requirements Clarification | `requirements-clarifier` agent | Gather complete requirements |
| 3 | Research | `research-agent` agent | Find best practices and documentation |
| 4 | Debug Analysis | `debug-analyzer` agent | Root cause analysis (bugs only) |
| 5 | Code Assessment | `code-assessor` agent | Evaluate existing codebase |
| 6 | Specification Writing | `spec-writer` agent | Create tech spec, plan, tasks |
| 7 | Specification Review | `dev-workflow` skill | Validate all documents |
| 8-9 | Execution & Coordination | `execution-coordinator` agent | Implement with parallel agents |
| 10 | Cleanup | `dev-workflow` skill | Remove temporary files |
| 11 | Commit & Push | `dev-workflow` skill | Save changes to repository |

## Architecture

The plugin uses a **skill + agents** architecture:

- **Skills** (`skills/`): Orchestration and rules
- **Agents** (`agents/`): Specialized tasks invoked via Task tool

```
dev-workflow-plugin/
├── skills/
│   ├── dev-workflow/     # Main orchestrator skill
│   └── dev-rules/        # Development rules and philosophy
├── agents/
│   ├── requirements-clarifier.md
│   ├── research-agent.md
│   ├── search-agent.md
│   ├── debug-analyzer.md
│   ├── code-assessor.md
│   ├── code-reviewer.md
│   ├── spec-writer.md
│   └── execution-coordinator.md
└── commands/
    └── fix-impl.md
```

## Skills

### dev-workflow
Main entry point skill that orchestrates all phases. Invokes agents for each phase and manages workflow transitions.

### dev-rules
Core development rules and standards including:
- Git workflow rules
- Development philosophy (incremental development, pragmatic approach)
- Quality standards (testability, readability, consistency)
- Decision framework priorities

## Agents

### requirements-clarifier
Gathers and documents complete requirements through structured questioning:
- Problem statement analysis
- Success criteria definition
- Edge case identification
- Constraint documentation

**Invoke:** `Task(subagent_type: "dev-workflow:requirements-clarifier")`

### research-agent
Conducts comprehensive research on best practices and documentation:
- Library/framework documentation lookup
- Similar implementation patterns
- Best practices from official sources
- Uses `search-agent` for intelligent retrieval

**Invoke:** `Task(subagent_type: "dev-workflow:research-agent")`

### search-agent
Intelligent multi-source search with state-of-the-art retrieval:
- **Query Expansion:** Generates 3-5 sub-queries for comprehensive coverage
- **Multi-Source Retrieval:** Parallel search across Exa, Context7, DeepWiki, GitHub
- **Re-ranking:** Confidence scoring with authority weighting
- **Citation Tracking:** Provenance hash for audit and re-run
- **Search Modes:** `code`, `docs`, `academic`, `web`, `all`

**Interface:**
```typescript
search(query: string, context?: SearchContext) → SearchResult[]

interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  confidence: number;  // 0-1 relevance score
  provenance: { source, query, timestamp, hash };
}
```

**Invoke:** `Task(subagent_type: "dev-workflow:search-agent")`

### debug-analyzer
Systematic root cause analysis for bugs:
- Evidence collection
- Issue reproduction
- Hypothesis formation and verification
- Root cause documentation

**Invoke:** `Task(subagent_type: "dev-workflow:debug-analyzer")`

### code-assessor
Evaluates existing codebase before making changes:
- Architecture evaluation
- Code standards review
- Dependency analysis
- Framework pattern identification

**Invoke:** `Task(subagent_type: "dev-workflow:code-assessor")`

### code-reviewer
Specification-aware code review across 8 quality dimensions:
- Correctness, Security, Performance, Maintainability
- Testability, Error Handling, Consistency, Accessibility
- Validates implementation against specification
- Severity classification (Critical/High/Medium/Low/Info)
- Tool integration with project linters

**Invoke:** `Task(subagent_type: "dev-workflow:code-reviewer")`

### spec-writer
Creates comprehensive technical documentation:
- Technical Specification
- Implementation Plan
- Task List

**Invoke:** `Task(subagent_type: "dev-workflow:spec-writer")`

### execution-coordinator
Coordinates parallel agents during implementation:
- Development Agent (code generation)
- Testing Agent (validation)
- Documentation Agent (tracking)

**Invoke:** `Task(subagent_type: "dev-workflow:execution-coordinator")`

## External Agents Used

The plugin leverages these external specialist agents via the Task tool:

| Agent | Purpose |
|-------|---------|
| `rust-pro` | Rust development |
| `backend-developer` | Backend services |
| `frontend-developer` | UI components |
| `mobile-developer` | Mobile apps |
| `superpowers:test-driven-development` | TDD approach |
| `superpowers:systematic-debugging` | Debugging methodology |
| `documentation-expert` | Technical documentation |

**Note:** Code review is now handled by the internal `dev-workflow:code-reviewer` agent.

## Output Documents

All documents are created in `specification/[index]-[name]/` directory:

1. `[index]-requirements.md` - Clarified requirements
2. `[index]-research-report.md` - Research findings
3. `[index]-debug-analysis.md` - Debug analysis (bugs only)
4. `[index]-assessment.md` - Code assessment
5. `[index]-specification.md` - Technical specification
6. `[index]-implementation-plan.md` - Implementation plan
7. `[index]-task-list.md` - Detailed task list
8. `[index]-implementation-summary.md` - Final summary

## License

MIT

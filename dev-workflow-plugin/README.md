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
    "https://github.com/jenningsloy318/claude-artifacts/tree/main/dev-workflow-plugin"
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

| Phase | Name | Skill | Description |
|-------|------|-------|-------------|
| 1 | Specification Setup | `dev-workflow` | Find or create spec directory |
| 2 | Requirements Clarification | `requirements-clarifier` | Gather complete requirements |
| 3 | Research | `research-phase` | Find best practices and documentation |
| 4 | Debug Analysis | `debug-analyzer` | Root cause analysis (bugs only) |
| 5 | Code Assessment | `code-assessor` | Evaluate existing codebase |
| 6 | Specification Writing | `spec-writer` | Create tech spec, plan, tasks |
| 7 | Specification Review | `dev-workflow` | Validate all documents |
| 8-9 | Execution & Coordination | `execution-coordinator` | Implement with parallel agents |
| 10 | Cleanup | `dev-workflow` | Remove temporary files |
| 11 | Commit & Push | `dev-workflow` | Save changes to repository |

## Skills

### dev-workflow
Main entry point skill that orchestrates all phases. Provides the overall workflow structure and phase transitions.

### dev-rules
Core development rules and standards including:
- Git workflow rules
- Development philosophy (incremental development, pragmatic approach)
- Quality standards (testability, readability, consistency)
- Decision framework priorities

### requirements-clarifier
Gathers and documents complete requirements through structured questioning:
- Problem statement analysis
- Success criteria definition
- Edge case identification
- Constraint documentation

### research-phase
Research best practices and gather documentation:
- Library/framework documentation lookup
- Similar implementation patterns
- Best practices from official sources

### debug-analyzer
Systematic root cause analysis for bugs:
- Evidence collection
- Issue reproduction
- Hypothesis formation and verification
- Root cause documentation

### code-assessor
Evaluate existing codebase before making changes:
- Architecture evaluation
- Code standards review
- Dependency analysis
- Framework pattern identification

### spec-writer
Create comprehensive technical documentation:
- Technical Specification
- Implementation Plan
- Task List

### execution-coordinator
Coordinate parallel agents during implementation:
- Development Agent (code generation)
- Testing Agent (validation)
- Documentation Agent (tracking)

## Specialist Agents Used

The plugin leverages these specialist agents via the Task tool:

| Agent | Purpose |
|-------|---------|
| `rust-pro` | Rust development |
| `backend-developer` | Backend services |
| `frontend-developer` | UI components |
| `mobile-developer` | Mobile apps |
| `superpowers:code-reviewer` | Code review |
| `superpowers:test-driven-development` | TDD approach |
| `superpowers:systematic-debugging` | Debugging methodology |
| `documentation-expert` | Technical documentation |

## Output Documents

All documents are created in `specification/[index]-[name]/` directory:

1. `[index]-requirements.md` - Clarified requirements
2. `[index]-research-report.md` - Research findings
3. `[index]-debug-analysis.md` - Debug analysis (bugs only)
4. `[index]-assessment.md` - Code assessment
5. `[index]-technical-spec.md` - Technical specification
6. `[index]-implementation-plan.md` - Implementation plan
7. `[index]-task-list.md` - Detailed task list
8. `[index]-implementation-summary.md` - Final summary

## License

MIT

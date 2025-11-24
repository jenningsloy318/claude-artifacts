---
name: dev-workflow
description: Complete development workflow for implementing features, fixing bugs, improving performance, or refactoring code. Use when asked to fix issues, implement features, resolve deprecations, or improve code. Orchestrates all development phases from requirements to deployment.
---

# Development Workflow

A systematic approach for all development tasks including bug fixes, new features, performance improvements, and refactoring.

**Announce at start:** "I'm using the dev-workflow skill to systematically implement this task."

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

Copy this checklist to track progress:

```
Development Workflow Progress:
- [ ] Phase 1: Specification Setup (identify/create spec directory)
- [ ] Phase 2: Requirements Clarification (gather requirements)
- [ ] Phase 3: Research (best practices, docs, patterns)
- [ ] Phase 4: Debug Analysis (for bugs only)
- [ ] Phase 5: Code Assessment (architecture, style, frameworks)
- [ ] Phase 6: Specification Writing (tech spec, plan, tasks)
- [ ] Phase 7: Specification Review (validate against requirements)
- [ ] Phase 8-9: Execution & Coordination (parallel agents)
- [ ] Phase 10: Cleanup (remove temp files, unused code)
- [ ] Phase 11: Commit & Push (descriptive message)
```

---

## Phase 1: Specification Setup

Analyze the information provided and identify which specification applies:

1. **Search for existing specs**: Look in `specification/` directory
2. **If related specs found**: Present choices, ask user to confirm
3. **If no specs found**: Create new subdirectory under `specification/`
   - Pattern: `[index]-[feature-name-or-fix-name]`
   - Example: `02-user-authentication`, `03-performance-optimization`

**Rules:**
- Never create documents under project root or directly under `specification/`
- All documents must be in a spec subdirectory
- Document naming: `[index]-[document-name].md`

---

## Phase 2: Requirements Clarification

**AGENT:** Invoke `dev-workflow:requirements-clarifier`

```
Task(
  prompt: "Gather requirements for: [task description]",
  subagent_type: "dev-workflow:requirements-clarifier"
)
```

The agent will ask appropriate questions for features or bug fixes and produce:

**Output:** `[index]-requirements.md` in spec directory

---

## Phase 3: Research Phase

**AGENT:** Invoke `dev-workflow:research-agent`

```
Task(
  prompt: "Research best practices for: [topic]",
  context: { technologies: [...], focus_areas: [...] },
  subagent_type: "dev-workflow:research-agent"
)
```

The research-agent uses `dev-workflow:search-agent` internally for retrieval.

**Output:** `[index]-research-report.md` in spec directory

---

## Phase 4: Debug Analysis (Bug Fixes Only)

**AGENT:** Invoke `dev-workflow:debug-analyzer`

```
Task(
  prompt: "Analyze bug: [issue description]",
  context: { evidence: [...], reproduction_steps: [...] },
  subagent_type: "dev-workflow:debug-analyzer"
)
```

Skip this phase for new features.

**Output:** `[index]-debug-analysis.md` in spec directory

---

## Phase 5: Code Assessment

**AGENT:** Invoke `dev-workflow:code-assessor`

```
Task(
  prompt: "Assess codebase for: [scope]",
  context: { focus: "architecture|standards|dependencies|patterns" },
  subagent_type: "dev-workflow:code-assessor"
)
```

**Output:** `[index]-assessment.md` in spec directory

---

## Phase 6: Specification Writing

**AGENT:** Invoke `dev-workflow:spec-writer`

```
Task(
  prompt: "Write specification for: [feature/fix name]",
  context: {
    requirements: "[path to requirements]",
    research: "[path to research report]",
    assessment: "[path to assessment]",
    debug_analysis: "[path to debug analysis if applicable]"
  },
  subagent_type: "dev-workflow:spec-writer"
)
```

**Output:** Three files in spec directory:
- `[index]-specification.md`
- `[index]-implementation-plan.md`
- `[index]-task-list.md`

---

## Phase 7: Specification Review

Review all documents for:

1. **Alignment**: Match requirements from Phase 2
2. **Best practices**: Follow current standards from research
3. **Code constraints**: Include patterns from assessment
4. **Executability**: Verify specification is executable and testable

**If issues found:** Return to relevant phase to fix

---

## Phase 8-9: Execution & Coordination

**AGENT:** Invoke `dev-workflow:execution-coordinator`

```
Task(
  prompt: "Execute implementation for: [feature/fix name]",
  context: {
    task_list: "[path to task list]",
    specification: "[path to specification]"
  },
  subagent_type: "dev-workflow:execution-coordinator"
)
```

**CRITICAL:** Do not pause or stop during execution. If multiple options exist, choose the one that continues implementation.

The execution-coordinator will invoke specialist agents as needed:
- `rust-pro`, `backend-developer`, `frontend-developer`, `mobile-developer`
- `superpowers:code-reviewer`, `superpowers:test-driven-development`
- `documentation-expert`

**Output:** Code, tests, and `[index]-implementation-summary.md`

---

## Phase 10: Cleanup Phase

Perform comprehensive cleanup:

1. Remove temporary files created during process
2. Delete obsolete code that was replaced
3. Remove unused imports and dependencies
4. Clean up debug logs and comments
5. Ensure no development artifacts remain

---

## Phase 11: Commit & Push

Upon completion of all tasks:

1. **Apply dev-rules**: Use `dev-workflow:dev-rules` for git practices
2. **Stage only changed files**: `git add file1 file2` (no `git add -A`)
3. **Create descriptive commit message**
4. **Push to repository**

---

## Agents Reference

| Agent | Purpose | Invoke Via |
|-------|---------|------------|
| `requirements-clarifier` | Gather requirements | `dev-workflow:requirements-clarifier` |
| `research-agent` | Research best practices | `dev-workflow:research-agent` |
| `search-agent` | Multi-source search | `dev-workflow:search-agent` |
| `debug-analyzer` | Root cause analysis | `dev-workflow:debug-analyzer` |
| `code-assessor` | Assess codebase | `dev-workflow:code-assessor` |
| `spec-writer` | Write specifications | `dev-workflow:spec-writer` |
| `execution-coordinator` | Coordinate implementation | `dev-workflow:execution-coordinator` |

## Skills Reference

| Skill | Purpose |
|-------|---------|
| `dev-workflow:dev-rules` | Core development rules and philosophy |

## External Agents to Use

- `superpowers:subagent-driven-development` - Parallel agent coordination
- `superpowers:systematic-debugging` - Debugging methodology
- `superpowers:code-reviewer` - Code review
- `rust-pro`, `backend-developer`, `frontend-developer`, `mobile-developer` - Specialist developers
- `documentation-expert` - Technical documentation

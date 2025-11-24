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
- [ ] Phase 8: Execution (parallel agents: dev, test, docs)
- [ ] Phase 9: Coordination (sequential task completion)
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

**SUB-SKILL:** Use `dev-workflow:requirements-clarifier`

### For Features, ask:
- Design available? (Figma, mockups)
- Technical stack to use
- Programming languages
- Project structure requirements
- Latest best practices considerations

### For Bug Fixes, ask:
- Environment (mobile/desktop)
- OS and Browser
- Screenshots with error messages
- Logs (build, runtime, debug)
- Steps to reproduce

**Output:** Clear requirements documented in spec directory

---

## Phase 3: Research Phase

**SUB-SKILL:** Use `dev-workflow:research-phase`

Conduct comprehensive research:

1. **Add timestamp**: Get current time from time MCP for context
2. **Research topics**:
   - Best practices and design patterns
   - Official documentation and API references
   - Blog posts and tutorials
   - GitHub issues and discussions
   - Performance considerations and edge cases

3. **Tools to use**:
   - MCP: `websearch`, `exa`, `context7`, `deepwiki`
   - Agents: `search-specialist`, `research-analyst`

4. **Find latest docs** for libraries/tools being used

**Output:** `[index]-research-report.md` in spec directory

---

## Phase 4: Debug Analysis (Bug Fixes Only)

**SUB-SKILL:** Use `dev-workflow:debug-analyzer`

For errors or bugs:

1. **Analyze codebase** based on Research Phase findings
2. **Use `ast-grep` skill** to identify and locate code patterns
3. **Propose root cause analysis**
4. **Utilize agents**: `debugging-toolkit:debugger`, `superpowers:systematic-debugging`

**Output:** `[index]-debug-analysis.md` in spec directory

---

## Phase 5: Code Assessment

**SUB-SKILL:** Use `dev-workflow:code-assessor`

Assess current codebase:

1. **Architecture evaluation**: Compare to best practices
2. **Code standards**: Check rules and formatting
3. **Dependencies**: Verify using latest packages/libraries/frameworks
4. **Alternatives**: Identify better options if available

**Output:** `[index]-assessment.md` in spec directory

---

## Phase 6: Specification Writing

**SUB-SKILL:** Use `dev-workflow:spec-writer`

Create comprehensive documents:

1. **Technical Specification**
   - Architecture decisions referencing previous phase documents
   - Follow API documentation for aligned API specifications
   - Use agents: `cloud-architect`, `backend-developer`, `frontend-developer`

2. **Implementation Plan**
   - Detailed milestones
   - Based on specification

3. **Task List**
   - Prioritized subtasks broken down from plan
   - Include final task: commit and push changes

**Output:** Three files in spec directory:
- `[index]-specification.md`
- `[index]-implementation-plan.md`
- `[index]-task-list.md`

---

## Phase 7: Specification Review

Review all documents for:

1. **Alignment**: Match requirements from Phase 2
2. **Best practices**: Follow current standards
3. **Code constraints**: Include industrial standards
4. **Executability**: Verify specification is executable and testable

**If issues found:** Return to relevant phase to fix

---

## Phase 8: Execution Phase

**SUB-SKILL:** Use `dev-workflow:execution-coordinator`
**ALSO USE:** `superpowers:subagent-driven-development`

**CRITICAL:** Do not pause or stop during execution. If multiple options exist, choose the one that continues implementation unless not feasible.

### Development Agent
Responsibilities:
- Generate code following established patterns
- Apply linting and formatting
- Build after each code generation
- Document implementation choices
- Use latest libraries and tools
- Fix all warnings/errors (don't suppress)
- Organize code in modular, loosely-coupled components
- Maintain consistent data schemas

**Agents:** `rust-pro`, `backend-developer`, `frontend-developer`, `mobile-developer`

### Testing Agent
Responsibilities:
- Validate builds run without errors
- Execute CodeRabbit analysis (background): `coderabbit --prompt-only`
- Write and run unit/integration tests
- Document edge cases and coverage
- For web projects: Use `playwright` and `chrome-devtools` MCP tools

**Agents:** `superpowers:code-reviewer`

### Documentation Agent
Responsibilities:
- Track implementation progress
- Create `implementation-summary.md`:
  - Technical decisions rationale
  - Code structure overview
  - Challenges and solutions
  - Performance metrics

**Agents:** `documentation-expert`

**Output:** Code, tests, and `[index]-implementation-summary.md`

---

## Phase 9: Coordination

Progress through tasks sequentially:

1. Assign next task only after previous completion
2. Ensure all agents work with consistent context
3. Maintain single source of truth for specifications
4. Request user confirmation only for:
   - Significant architectural changes
   - Blocking obstacles

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

## Sub-Skills Reference

| Skill | Purpose |
|-------|---------|
| `dev-workflow:dev-rules` | Core development rules and philosophy |
| `dev-workflow:requirements-clarifier` | Gather and document requirements |
| `dev-workflow:research-phase` | Research best practices and docs |
| `dev-workflow:debug-analyzer` | Root cause analysis for bugs |
| `dev-workflow:code-assessor` | Assess architecture and code quality |
| `dev-workflow:spec-writer` | Write specifications and plans |
| `dev-workflow:execution-coordinator` | Coordinate parallel development agents |

## External Skills/Agents to Use

- `superpowers:subagent-driven-development` - Parallel agent coordination
- `superpowers:systematic-debugging` - Debugging methodology
- `superpowers:code-reviewer` - Code review
- `ast-grep` - Code pattern search
- Specialist agents as needed (backend, frontend, mobile, etc.)

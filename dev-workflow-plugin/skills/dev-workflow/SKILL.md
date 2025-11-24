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
- [ ] Phase 5.3: Architecture Design (for complex features - optional)
- [ ] Phase 5.5: UI/UX Design (for features with UI - optional)
- [ ] Phase 6: Specification Writing (tech spec, plan, tasks)
- [ ] Phase 7: Specification Review (validate against requirements)
- [ ] Phase 8-9: Execution & Coordination (parallel agents)
- [ ] Phase 9.5: Quality Assurance (modality-specific testing)
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

## Phase 5.3: Architecture Design (Complex Features)

**AGENT:** Invoke `dev-workflow:architecture-agent`

```
Task(
  prompt: "Design architecture for: [feature/fix name]",
  context: {
    requirements: "[path to requirements]",
    assessment: "[path to assessment]"
  },
  subagent_type: "dev-workflow:architecture-agent"
)
```

Skip this phase for:
- Simple bug fixes
- Minor feature changes (< 3 files affected)
- Cosmetic updates
- Configuration changes

Use this phase for:
- New features with multiple components
- Significant refactoring
- Technology stack changes
- Security-related architectural changes

**Output:** `[index]-architecture.md` and ADRs in spec directory

---

## Phase 5.5: UI/UX Design (Features with UI)

**AGENT:** Invoke `dev-workflow:ui-ux-designer`

```
Task(
  prompt: "Create UI/UX design for: [feature/fix name]",
  context: {
    requirements: "[path to requirements]",
    assessment: "[path to assessment]"
  },
  subagent_type: "dev-workflow:ui-ux-designer"
)
```

Skip this phase for:
- Backend-only features
- CLI tools
- API-only changes

**Output:** `[index]-design-spec.md` in spec directory

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
    architecture: "[path to architecture if applicable]",
    design_spec: "[path to design spec if applicable]",
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
- `dev-workflow:code-reviewer`, `superpowers:test-driven-development`
- `documentation-expert`

**Output:** Code, tests, and `[index]-implementation-summary.md`

---

## Phase 9.5: Quality Assurance

**AGENT:** Invoke `dev-workflow:qa-agent`

```
Task(
  prompt: "Execute QA testing for: [feature/fix name]",
  context: {
    specification: "[path to specification]",
    implementation_summary: "[path to implementation summary]",
    modality: "cli|desktop-ui|web-app"
  },
  subagent_type: "dev-workflow:qa-agent"
)
```

The QA agent will execute modality-specific testing:

**CLI Applications:**
- Command enumeration via --help parsing
- Value matrix testing (valid/boundary/malformed)
- Sandbox execution with exit code assertions
- stdout/stderr regex matching
- Golden-file diffing

**Desktop UI Applications:**
- Launch in isolated VM/container
- Control tree discovery via AT-SPI/Accessibility API/UI-Automation
- Auto-generated interaction sequences
- Pixel-perfect screenshot comparison
- Accessibility tree hash verification

**Web Applications:**
- Single dev server guarantee
- Playwright MCP browser automation
- Chrome DevTools protocol monitoring
- Console error, network, a11y, perf metrics
- Route crawling from sitemap
- trace.zip recording per test
- DOM/CSSOM/HAR diff against spec snapshot

**Output:**
- `[index]-test-plan.md`
- `[index]-test-results.md`
- Test artifacts (traces, screenshots, logs)

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

### Workflow Agents

| Agent | Purpose | Invoke Via |
|-------|---------|------------|
| `requirements-clarifier` | Gather requirements | `dev-workflow:requirements-clarifier` |
| `research-agent` | Research best practices | `dev-workflow:research-agent` |
| `search-agent` | Multi-source search | `dev-workflow:search-agent` |
| `debug-analyzer` | Root cause analysis | `dev-workflow:debug-analyzer` |
| `code-assessor` | Assess codebase | `dev-workflow:code-assessor` |
| `code-reviewer` | Specification-aware code review | `dev-workflow:code-reviewer` |
| `architecture-agent` | Design architecture and create ADRs | `dev-workflow:architecture-agent` |
| `ui-ux-designer` | Create UI/UX design specifications | `dev-workflow:ui-ux-designer` |
| `spec-writer` | Write specifications | `dev-workflow:spec-writer` |
| `execution-coordinator` | Coordinate implementation | `dev-workflow:execution-coordinator` |
| `qa-agent` | Modality-specific QA testing | `dev-workflow:qa-agent` |

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
| `dev-workflow:dev-rules` | Core development rules and philosophy |

## External Agents to Use

- `superpowers:subagent-driven-development` - Parallel agent coordination
- `superpowers:systematic-debugging` - Debugging methodology
- `documentation-expert` - Technical documentation

**Note:** `superpowers:code-reviewer` has been replaced by `dev-workflow:code-reviewer` (internal agent).

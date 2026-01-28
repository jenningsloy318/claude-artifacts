---
name: super-dev
description: Coordinator-driven development workflow with parallel agent execution for implementing features, fixing bugs, improving performance, or refactoring code. Central Coordinator Agent orchestrates all phases and assigns tasks to specialized sub-agents.
---

# Super Dev Workflow

A coordinator-driven development system with parallel agent execution for all development tasks including bug fixes, new features, performance improvements, and refactoring.

**Announce at start:** "I'm using the super-dev skill to systematically implement this task with coordinator-driven orchestration."

## Architecture Overview

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

The Coordinator Agent orchestrates these phases automatically:

```
Development Workflow Progress:
- [ ] Phase 0: Apply Dev Rules (establish coding standards)
- [ ] Phase 1: Specification Setup (identify spec directory + create git worktree)
- [ ] Phase 2: Requirements Clarification (gather requirements)
- [ ] Phase 3: Research (best practices, docs, patterns) [Time MCP + Option Presentation]
- [ ] Phase 4: Debug Analysis (for bugs only) [grep/ast-grep]
- [ ] Phase 5: Code Assessment (architecture, style, frameworks) [grep/ast-grep]
- [ ] Phase 5.3: Architecture Design (for complex features - optional) [Option Presentation]
- [ ] Phase 5.5: UI/UX Design (for features with UI - optional) [Option Presentation]
- [ ] Phase 6: Specification Writing (tech spec, plan, tasks)
- [ ] Phase 7: Specification Review (validate against requirements)
- [ ] Phase 8: Execution & QA (PARALLEL: dev + qa executors)
- [ ] Phase 9: Code Review (spec-aware review using super-dev:code-reviewer)
- [ ] Iteration Rule: Loop Phase 8 and Phase 9 until no blocking issues remain (no Critical/High/Medium findings; all acceptance criteria met)
- [ ] Phase 10: Documentation Update (docs-executor sequential)
- [ ] Phase 11: Cleanup (remove temp files, unused code)
- [ ] Phase 11.5: Manual Confirmation (user review before merge - optional)
- [ ] Phase 12: Commit & Merge to Main (worktree workflow)
- [ ] Phase 13: Final Verification (Coordinator verifies all complete)
```

## Option Presentation Rule (MANDATORY)

**CRITICAL WORKFLOW RULE:** The super-dev workflow MUST present 3-5 options with detailed comparisons at key decision points. This is NOT optional - it is the DEFAULT and EXPECTED behavior.

### Phases Requiring Option Presentation

The following phases MUST present options to the user for selection:

| Phase | Agent | What Requires Options |
|-------|-------|---------------------|
| Phase 3 | `super-dev:research-agent` | Technology choices, libraries, frameworks, implementation approaches |
| Phase 5.3 | `super-dev:architecture-agent` | Architecture patterns, module decomposition, data access, communication patterns |
| Phase 5.5 | `super-dev:ui-ux-designer` | Layout patterns, navigation, components, interactions, visual design |

### Option Presentation Workflow

```
User Request
     │
     ▼
┌─────────────────┐
│   Coordinator   │
│     Agent       │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     Research/Architecture/Design     │
│         Agent Generates              │
│           3-5 Options                │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Present Options to User:          │
│   - Detailed descriptions            │
│   - Comparison matrix                │
│   - Strengths/Weaknesses             │
│   - Recommendation                   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     User Selects Option             │
│   (or requests modifications)        │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Coordinator Proceeds with         │
│      Selected Option                │
└─────────────────────────────────────┘
```

### Coordinator Responsibilities

The Coordinator Agent MUST:
1. **Ensure options are generated** - Verify that the relevant agent (research/architecture/design) has presented 3-5 options
2. **Wait for user selection** - Do NOT proceed to next phase until user has selected an option
3. **Document the decision** - Record the selected option in the specification
4. **Handle edge cases** - If user requests modifications, work with the agent to refine options

### Exception Handling

**Single answer is acceptable ONLY when:**
- Looking up specific API documentation
- Finding exact configuration values
- Retrieving specific error messages
- User explicitly requests "just give me the best option"
- Following established patterns without variation

**All other cases MUST present options.**

**CHECKPOINT RULE:** Coordinator ensures commits at each phase boundary.

Two indices are used throughout this workflow to organize specifications and their associated artifacts:

- Spec Index (spec-index): A numeric sequence that identifies each specification within the `specification/` directory. Naming convention: `[spec-index]-[spec-name]/`. Example: `01-user-auth/`, `02-payment-processing/`.

- doc Index (doc-index): A auto-incrementalnumeric sequence used to order and label files produced within a specific spec across workflow phases, not same with the phase index. These files are stored under the corresponding spec directory and use the doc index in their filenames. Naming convention: `[doc-index]-[document-type].md`. Example within `01-research-report.md`: `02-requirements.md`, `03-specification.md`.

Summary:
- Spec Index organizes specs at the directory level (which spec).
- Phase Index organizes documents within a spec by workflow phase (what was produced when).


## Entry Point: Coordinator Agent

**AGENT:** Invoke `super-dev:coordinator`

The Coordinator Agent is the CENTRAL AUTHORITY that:
1. Orchestrates ALL workflow phases
2. Assigns tasks to specialized sub-agents
3. Monitors execution - no unauthorized stops
4. Enforces quality gates
5. Manages build queue (Rust/Go serialization)
6. Performs final verification

```
Task(
  prompt: "Implement: [task description]",
  context: {
    task_type: "feature|bug|refactor|improvement",
    spec_directory: "[path to spec]"
  },
  subagent_type: "super-dev:coordinator"
)
```


## Documentation Update Rules (CRITICAL - MANDATORY)

**At every milestone/phase boundary, update these documents:**

### 1. Task List Updates (`[doc-index]-task-list.md`)
- [ ] Mark completed tasks with `[x]`
- [ ] Add any new tasks discovered during implementation
- [ ] Note any blocked or deferred tasks with reasons

### 2. Implementation Summary Updates (`[doc-index]-implementation-summary.md`)
- [ ] Add completed work to "Code Changes" section
- [ ] Document any technical decisions made
- [ ] Record challenges encountered and solutions found

### 3. Specification Updates (`[doc-index]-specification.md`)
- [ ] Update affected sections with `[UPDATED: date]` marker
- [ ] Document why the change was necessary

**FORBIDDEN:**
- ❌ Completing a milestone without updating task list
- ❌ Moving to next phase with outdated implementation summary
- ❌ Changing implementation without updating specification

---

## Phase 0: Apply Dev Rules

**SKILL:** Invoke `super-dev:dev-rules`

Establishes coding standards, git practices, and quality standards.

---

## Phase 1: Specification Setup

**IMPORTANT:** This phase performs two critical setup tasks in sequence:

1. **Identify or create spec directory** under `specification/` with pattern `[spec-index]-[spec-name]`
2. **Create git worktree** under `.worktree/` with the same name as the spec directory

### Step 1: Spec Directory Setup

Analyze the task and identify/create an appropriate spec directory:

1. **Check for existing specs**: Search `specification/` for directories matching the current task
   - If a relevant spec exists: reuse it (confirm with user if multiple matches)
   - If no match exists: create a new spec directory

2. **New spec directory naming**: `[spec-index]-[spec-name]/`
   - `spec-index`: Next sequential number (01, 02, 03, ...)
   - `spec-name`: Kebab-case descriptor (e.g., `user-auth`, `payment-integration`, `fix-login-bug`)

3. **Create spec directory structure**:
   ```bash
   mkdir -p "specification/[spec-index]-[spec-name]"
   ```

### Step 2: Git Worktree Creation

**CRITICAL:** ALL development work MUST be done in a git worktree for isolation.

After creating/identifying the spec directory, create a matching git worktree:

1. **Worktree location**: `.worktree/[spec-name]/` in project root
   - **DEFAULT**: `.worktree/` in project root (no confirmation required)
   - Worktree name matches spec directory name: `[spec-index]-[spec-name]`

2. **Check for existing worktrees**:
   ```bash
   git worktree list
   ```

3. **Create new worktree** if it doesn't exist:
   ```bash
   # Method 1: Using git worktree command directly
   git worktree add .worktree/[spec-index]-[spec-name] -b [spec-index]-[spec-name]

   # Method 2: Using zcf:git-worktree command (if available)
   /zcf/git-worktree add [spec-index]-[spec-name]
   ```

4. **Navigate to worktree** for all subsequent development:
   ```bash
   cd .worktree/[spec-index]-[spec-name]
   ```

5. **Create workflow-tracking.json** in specification root directory (NOT in sub spec directory):
   ```bash
   # File location: specification/[spec-index]-[spec-name]-workflow-tracking.json
   # IMPORTANT: Create this file in the root of specification/ directory
   # DO NOT create another copy inside specification/[spec-index]-[spec-name]/
   ```
   ```json
   {
     "worktreePath": ".worktree/[spec-index]-[spec-name]",
     "specDirectory": "specification/[spec-index]-[spec-name]",
     ...
   }
   ```

### Error Handling

- **Worktree already exists**: Reuse existing worktree automatically (cd to it)
- **Already in a worktree**: Verify the current worktree matches the spec directory. If not, navigate to correct worktree automatically.
- **Not in worktree after Phase 1**: WARNING: All subsequent phases should be run in the created worktree.

### Verification Checklist

Before proceeding to Phase 2, verify:
- [ ] Spec directory exists: `specification/[spec-index]-[spec-name]/`
- [ ] Git worktree exists: `.worktree/[spec-index]-[spec-name]/`
- [ ] Currently in the created worktree (check with `git worktree list`)
- [ ] `specification/[spec-index]-[spec-name]-workflow-tracking.json` created in specification root (NOT in sub spec directory)

---

## Phase 2: Requirements Clarification

**AGENT:** Invoke `super-dev:requirements-clarifier`

**Output:** `[doc-index]-requirements.md`

---

## Phase 3: Research Phase (Time MCP Enhanced)

**AGENT:** Invoke `super-dev:research-agent`

**CONTEXT:** Apply `research` mode for information gathering and exploration

The research-agent:
- Gets current timestamp via Time MCP
- Adds year context to queries
- Filters by recency
- Flags deprecated information

**Integrated Tools:**
- **continuous-learning skill**: Auto-extracts reusable patterns from research sessions
- **templates/reference/backend-patterns** and **templates/reference/frontend-patterns**: Reference for architectural patterns
- **templates/reference/coding-standards**: Language-specific best practices lookup

**Output:** `[doc-index]-research-report.md` with freshness scores

---

## Phase 4: Debug Analysis (grep/ast-grep Enhanced)

**AGENT:** Invoke `super-dev:debug-analyzer`

The debug-analyzer:
- Uses Grep for text pattern search
- Uses ast-grep for structural analysis
- Tracks file coverage for debugging scope

**Output:** `[doc-index]-debug-analysis.md`

---

## Phase 5: Code Assessment (grep/ast-grep Enhanced)

**AGENT:** Invoke `super-dev:code-assessor`

The code-assessor:
- Uses Grep for pattern matching
- Uses ast-grep for structural analysis
- Tracks file coverage percentage

**Output:** `[doc-index]-assessment.md`

---

## Phase 5.3: Architecture Design (Complex Features)

**AGENT:** Invoke `super-dev:architecture-agent`

**REFERENCE:** `templates/reference/architecture-patterns` - Architecture patterns, SOLID principles, ADR templates

**MANDATORY USER REVIEW:** Architecture design MUST be reviewed by user. Never skip this phase when architecture is involved.

**Output:** `[doc-index]-architecture.md` and ADRs

---

## Phase 5.5: UI/UX Design (Features with UI)

**AGENT:** Invoke `super-dev:ui-ux-designer`

**TOOL:** **Pencil MCP** for all UI/UX design work

**REFERENCE:** `templates/reference/ui-ux-patterns` - UI/UX patterns, wireframes, accessibility guidelines

**Design Guidelines:**
- **Apple Design Aesthetic**: Follow Apple Human Interface Guidelines patterns
- **No Dark Mode**: Design for light mode only
- **No Purple**: Avoid purple color schemes
- **Emit AI Flavor**: Create natural, human-feeling interfaces (avoid generic AI-generated aesthetics)

**Design Process:**
1. Prompt Pencil MCP to create the UI/UX design
2. Save the design to: `specification/[spec-index]-[spec-name]/[spec-index]-[spec-name].pen`
3. Generate design spec documentation

**MANDATORY USER REVIEW:** UI/UX design MUST be reviewed by user. Never skip this phase when UI is involved.

**Output:**
- `specification/[spec-index]-[spec-name]/[spec-index]-[spec-name].pen` - Pencil design file
- `[doc-index]-design-spec.md` - Design specification

**Enforcement Rule:** In all subsequent phases (Implementation, Code Review), if UI/UX work is involved, the implementation MUST follow the `[spec-index]-[spec-name].pen` design file.

---

## Phase 6: Specification Writing

**AGENT:** Invoke `super-dev:spec-writer`

**Input References:**
- If Phase 5.3 (Architecture) was completed: Reference `[doc-index]-architecture.md` and ADRs
- If Phase 5.5 (UI/UX Design) was completed: Reference `specification/[spec-index]-[spec-name]/[spec-index]-[spec-name].pen` design file

**Output:** Three files (or sub-specifications for large features)
- `[doc-index]-specification.md` - Technical specification
- `[doc-index]-implementation-plan.md` - Implementation plan
- `[doc-index]-task-list.md` - Task list
(Or sub-specifications for large features)

**UI/UX Design Integration (when applicable):**
- [ ] Specification references the `.pen` design file
- [ ] Implementation plan includes UI components from design
- [ ] Task list includes UI implementation tasks matching design elements
- [ ] Design file path included: `specification/[spec-index]-[spec-name]/[spec-index]-[spec-name].pen`

---

## Phase 7: Specification Review (VALIDATION GATES)

Coordinator reviews all documents for alignment and completeness.

**CRITICAL VALIDATION GATES - Spec Review MUST verify:**

### Naming Convention Requirements (MANDATORY)
- [ ] **No generic variable names** - All variables use feature-specific prefixes
  - Prohibited: `data`, `item`, `value`, `result`, `temp`, `obj`, `val`
  - Required: `[feature][entity][property]` (e.g., `userAuthState`, `orderTotal`)
- [ ] **No single-letter names** - Except loop indices (i, j, k)
- [ ] **No abbreviations** - Except well-known ones (id, url, api, http)
- [ ] **Function names use verb-noun pattern** - `[feature][Action]` or `[verb][Noun]`
- [ ] **Constants use UPPER_CASE** - `[FEATURE_NAME]_[CONSTANT]`
- [ ] **Booleans use is/has/should prefix** - `isAuthenticated`, `hasPermission`

### No Ambiguity Requirements (MANDATORY)
- [ ] **Single Implementation Guarantee** - Spec must result in exactly ONE valid implementation
- [ ] **All function names are specified** - No room for interpretation
- [ ] **All parameter names are specified** - No generic names allowed
- [ ] **All file paths are specified** - No ambiguity about where code goes
- [ ] **All conditional behaviors are documented** - No "if needed, do X"
- [ ] **All error cases are listed** - No "handle errors appropriately"
- [ ] **No pronouns** - Replace "it", "they", "this" with specific nouns
- [ ] **No "etc." or "and so on"** - List everything explicitly
- [ ] **No "appropriate" or "suitable"** - Specify exact values
- [ ] **No "handle" or "process"** - Specify exact actions
- [ ] **No optional behaviors** - Everything is required or explicitly conditional

### File Inventory Requirements (MANDATORY)
- [ ] **Files to be Created** - Complete list with specific file names
- [ ] **Files to be Modified** - Complete list with specific changes required
- [ ] **Files to be Deleted** - Complete list with reasons
- [ ] **File Summary** - Total counts for created/modified/deleted
- [ ] **Each milestone includes Files Affected section** - Created/Modified/Deleted

**REJECT SPEC IF ANY GATE FAILS** - Return to spec-writer for corrections

### Additional Review Criteria
- [ ] Requirements addressed in specification
- [ ] Research findings incorporated
- [ ] Architecture decisions documented (if applicable)
- [ ] Design specifications included (if UI feature)
- [ ] **Design file referenced** - If UI feature, `specification/[spec-index]-[spec-name]/[spec-index]-[spec-name].pen` is referenced in spec
- [ ] **UI tasks from design** - If UI feature, task list includes all UI components from design
- [ ] Implementation plan is feasible
- [ ] Task list is complete and actionable
- [ ] All acceptance criteria are testable

### UI/UX Design Validation (when applicable)
- [ ] **.pen design file exists** at `specification/[spec-index]-[spec-name]/[spec-index]-[spec-name].pen`
- [ ] **Specification references design file** - Design file path included in technical spec
- [ ] **Implementation plan includes UI components** - All design elements are in implementation plan
- [ ] **Task list covers design implementation** - Each design component has corresponding task

---

## Phase 8: Execution & QA (PARALLEL Agents)

**CONTEXT:** Apply `dev` mode for implementation focus

**CRITICAL CHANGE:** The Coordinator invokes TWO agents in PARALLEL, with CodeRabbit running proactively:

```
┌─────────────────────────────────────────────────────────────┐
│                PARALLEL EXECUTION & QA                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │dev-executor │  │   qa-agent  │  │   CodeRabbit     │    │
│  │             │  │             │  │   (Background)   │    │
│  │ Implements  │  │ Plans & runs│  │   Reviews code   │    │
│  │ code        │  │ tests       │  │   proactively    │    │
│  │             │  │             │  │                   │    │
│  │             │  │             │  │  → Report issues │    │
│  │             │  │             │  │     to dev       │    │
│  │             │  │             │  │  → Verify fixes  │    │
│  │             │  │             │  │                   │    │
│  └─────────────┘  └─────────────┘  └──────────────────┘    │
│                          │                                   │
│                   BUILD QUEUE                                │
│              (Rust/Go: one at a time)                       │
└─────────────────────────────────────────────────────────────┘
```

**Agents:**
- `super-dev:dev-executor` - Implements code, invokes specialist developers
- `super-dev:qa-agent` - Modality-specific testing and verification (merged planning + execution)
- **CodeRabbit CLI (Background)** - Proactive code review starting immediately when dev begins implementation

**Integrated Skills & Rules:**
- **tdd-workflow skill**: Test-first methodology with 80%+ coverage requirement
- **testing rules**: Enforces TDD, unit/integration/E2E test coverage
- **coding-style rules**: Immutability, file organization (200-400 lines typical), error handling
- **performance rules**: Model selection guidance (Haiku for lightweight, Sonnet for development)
- **patterns reference**: Common patterns for API responses, custom hooks, repository pattern

### Code Quality Standards (MANDATORY - Enforced During Implementation)

**The dev-executor MUST adhere to these standards during Phase 8:**

#### Naming Convention Requirements (MANDATORY)
- [ ] **No generic variable names** - All variables use feature-specific prefixes
  - Prohibited: `data`, `item`, `value`, `result`, `temp`, `obj`, `val`
  - Required: `[feature][entity][property]` (e.g., `userAuthState`, `orderTotal`)
- [ ] **No single-letter names** - Except loop indices (i, j, k)
- [ ] **No abbreviations** - Except well-known ones (id, url, api, http)
- [ ] **Function names use verb-noun pattern** - `[feature][Action]` or `[verb][Noun]`
- [ ] **Constants use UPPER_CASE** - `[FEATURE_NAME]_[CONSTANT]`
- [ ] **Booleans use is/has/should prefix** - `isAuthenticated`, `hasPermission`

#### No Ambiguity Requirements (MANDATORY)
- [ ] **Follow spec exactly** - Implementation must match specification unambiguously
- [ ] **Use specified names** - No deviation from spec-defined variable/function names
- [ ] **No generic names in code** - Even if spec allows, use descriptive names
- [ ] **Explicit error handling** - No "handle errors", specify exact error handling
- [ ] **No optional behaviors** - Everything is explicit or explicitly conditional

#### UI/UX Design Enforcement (MANDATORY when applicable)
- [ ] **Follow .pen design file** - If `specification/[spec-index]-[spec-name]/[spec-index]-[spec-name].pen` exists, implementation MUST follow it exactly
- [ ] **Open design file first** - Before implementing UI, use Pencil MCP to open and review the `.pen` file
- [ ] **Match visual specifications** - Layout, colors, spacing must match the design
- [ ] **Implement all components** - All UI elements from the design must be implemented
- [ ] **Apple aesthetic compliance** - Ensure light mode, no purple, natural feel

**CodeRabbit will flag violations of these standards.**

### CodeRabbit Proactive Execution

- Starts: As soon as dev agent signals implementation begins
- Mode: Background process with `--prompt-only` flag
- Purpose: Find issues early during implementation, not after completion
- Workflow:
  1. QA agent starts `coderabbit --prompt-only > coderabbit-output.log 2>&1 &`
  2. Monitors output for issues in real-time
  3. Reports issues to dev agent as they are found
  4. Dev agent fixes issues during implementation
  5. QA agent re-runs CodeRabbit to verify fixes
  6. Final CodeRabbit review before marking QA complete

**Build Policy (Rust/Go):**
- Only ONE build at a time
- Coordinator manages build queue
- Prevents resource conflicts

**Output:** Code, tests, and progress tracking

---

## Phase 9: Code Review

**CONTEXT:** Apply `review` mode for critical analysis

**AGENT:** Invoke `super-dev:code-reviewer`

**Integrated Skills & Rules:**
- **security-review skill**: Comprehensive security checklist validation
- **security rules**: Mandatory security checks (no hardcoded secrets, input validation, XSS/CSRF protection)
- **coding-style rules**: Code quality verification (immutability, no deep nesting, proper error handling)

Run specification-aware code review focused on correctness, security, performance, and maintainability. Scope to changed files and implementation summary; reference acceptance criteria from the spec.

**UI/UX Design Review (when applicable):**
- [ ] **Open .pen design file** - Use Pencil MCP to open `specification/[spec-index]-[spec-name]/[spec-index]-[spec-name].pen`
- [ ] **Compare implementation with design** - Verify UI matches the design file exactly
- [ ] **Check Apple aesthetic compliance** - Light mode, no purple, natural feel
- [ ] **Verify all components implemented** - All design elements are present in code
- [ ] **Screenshot validation** - Use `get_screenshot()` to compare visual output with design

**Iteration Rule (Coordinator-Enforced):**
- If verdict is Blocked or Changes Requested, or any Critical/High/Medium findings exist, or any acceptance criteria are Not Met/Partial → RE-ENTER Phase 8
- Create remediation tasks mapped from findings, run Execution & QA in parallel, then re-run Code Review
- Only proceed beyond Phase 9 when verdict is Approved or Approved with Comments (Low/Info only) and all acceptance criteria are met

**Output:** Code review report with severity, evidence, and verdict
- `[doc-index]-code-review.md`

---

## Phase 10: Documentation Update (Sequential)

**AGENT:** Invoke `super-dev:docs-executor`

After code review is complete and approved, update all documentation:
- Task list completion status
- Implementation summary with all changes
- Specification updates for any deviations
- Review findings integration

**Execution Model:** Sequential batch processing
- Runs after Phase 9 approval
- Processes all accumulated changes from Phases 8-9
- Single pass to update all documents
- Coordinates commit with code changes

**Output:** Updated
- `[doc-index]-task-list.md`
- `[doc-index]-implementation-summary.md`
- `[doc-index]-specification.md`

---

## Phase 11: Cleanup

Coordinator ensures:
1. No temp files remain
2. Unused code removed

---

## Phase 11.5: Manual Confirmation (OPTIONAL)

**PURPOSE:** Allow user to review changes before merging to main branch.

**Process:**
1. Present summary of all changes made
2. Ask user for confirmation to proceed with merge
3. Wait for user approval before proceeding to Phase 12

**Skip this phase if:**
- User explicitly requests automatic merge
- Changes are trivial (documentation, small fixes)

---

## Phase 12: Commit & Merge to Main

**Worktree Workflow:** Since development happens in isolated worktrees, changes are merged back to main branch rather than pushed.

**Process:**
1. **Read spec information**: Read `specification/[spec-index]-[spec-name]-workflow-tracking.json` to get:
   - `specDirectory`: The spec directory (e.g., `specification/01-user-auth/`)
   - `featureName`: The feature/fix name

2. **Stage all changes**: `git add [files]` (only files modified in this session)

3. **Generate commit message**:
   - Use the `generating-commit-messages` skill (MANDATORY per CLAUDE.md)
   - **Include spec info in commit title**: Prefix the title with `[spec-XX]` if changes are related to a spec
   - Format: `[spec-XX] <type>: <description>` or `<type>: <description>` if not spec-related
   - Example: `[spec-01] feat: implement user authentication`

4. **Commit**: `git commit -m "<commit message>"`

5. **Switch to main branch**: `git checkout main` (from main repo, not worktree)

6. **Merge worktree branch**: `git merge [spec-index]-[spec-name]`

7. **Clean up worktree**: `git worktree remove .worktree/[spec-index]-[spec-name]` (optional, after successful merge)

**CRITICAL REQUIREMENT:** When ALL tasks are complete, you MUST complete the merge to main.

**NEVER** mark workflow as complete without merging changes to main branch.

---

## Phase 13: Final Verification

Coordinator verifies:
- [ ] All specification documents created
- [ ] Implementation summary complete
- [ ] No missing code or files
- [ ] All changes committed
- [ ] Changes merged to main branch
- [ ] Git status clean (working tree clean)


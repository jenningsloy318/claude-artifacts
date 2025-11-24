# Task List: dev-workflow:code-reviewer Agent

**Plan:** `/home/jenningsl/development/claude-artifacts/specification/08-code-review-agent/08-implementation-plan.md`
**Total Tasks:** 21

## Tasks

### Milestone 1: Core Agent Definition

- [ ] **T1.1** Create agent file with YAML frontmatter
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Create new file with frontmatter: `name: code-reviewer`, `description: Review code for correctness, security, performance, and maintainability. Validates implementation against specification. Use after task completion in execution-coordinator.`, `model: sonnet`
  - **Acceptance:** File exists with valid YAML frontmatter

- [ ] **T1.2** Add opening persona statement
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Add: "You are a Code Reviewer Agent specialized in specification-aware code review across multiple quality dimensions. You validate that implementations match their specifications and provide actionable feedback with clear severity classifications."
  - **Acceptance:** Persona matches agent purpose

- [ ] **T1.3** Add Core Capabilities section
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Add 6 numbered capabilities: Specification Validation, Multi-Dimensional Review, Tool Integration, Actionable Feedback, Severity Classification, Git-Aware Scoping
  - **Acceptance:** All 6 capabilities listed with bold titles and descriptions

- [ ] **T1.4** Add Philosophy section
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Add review principles distilled from research: Specification-First, Signal over Noise, Actionable Feedback, Severity-Based Prioritization, Tool Augmentation
  - **Acceptance:** Philosophy principles documented

- [ ] **T1.5** Add Input Context section
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Define expected inputs: `specification` (path to tech spec), `implementation_summary` (changes description), `base_sha` (optional), `head_sha` (optional), `files_changed` (optional)
  - **Acceptance:** All inputs documented with descriptions

---

### Milestone 2: Review Process Implementation

- [ ] **T2.1** Add Step 1: Parse Context
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Document input validation, specification location, change scope determination. Include checklist for required vs optional inputs.
  - **Acceptance:** Step includes validation checklist

- [ ] **T2.2** Add Step 2: Read Specification
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Document specification parsing: extract acceptance criteria, non-goals, API contracts, data models, error cases, patterns. Include instructions for building validation checklist.
  - **Acceptance:** Specification extraction documented

- [ ] **T2.3** Add Step 3: Scope Changes
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Document Git SHA scoping using `git diff BASE_SHA HEAD_SHA --name-only` and `git diff BASE_SHA HEAD_SHA -- [file]`. Include fallback to file list when no SHA provided.
  - **Acceptance:** Both SHA and file-list scoping documented

- [ ] **T2.4** Add Step 4: Run Static Analysis
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Document linter detection and execution for each language: ESLint/Biome (JS/TS), Ruff (Python), Clippy (Rust), golangci-lint (Go). Include bash commands and output parsing.
  - **Acceptance:** All 4 language linters documented with detection logic

- [ ] **T2.5** Add Step 5: Dimension Reviews
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Document all 8 dimension reviews with specific checks:
    - Correctness (P0): Logic, spec compliance, edge cases
    - Security (P0): OWASP Top 10, input validation, secrets
    - Performance (P1): N+1, memory, complexity
    - Maintainability (P1): Readability, naming, docs
    - Testability (P1): DI, coverage, test structure
    - Error Handling (P1): Try/catch, messages, recovery
    - Consistency (P2): Pattern adherence
    - Accessibility (P2): WCAG, keyboard, contrast
  - **Acceptance:** All 8 dimensions with specific checks

- [ ] **T2.6** Add Step 6: Validate Against Specification
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Document comparison of implementation against specification checklist. Check each acceptance criterion. Flag non-goals that were accidentally implemented. Reference patterns from code-assessor.
  - **Acceptance:** Spec validation process documented

- [ ] **T2.7** Add Step 7: Synthesize Report
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Document aggregation, deduplication, prioritization of findings. Include verdict determination logic: Critical = Blocked, else based on High count and spec compliance.
  - **Acceptance:** Report synthesis documented with verdict logic

- [ ] **T2.8** Add verification checkpoints
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Add `<verification>` blocks after Steps 2, 4, and 6 with verification questions and proceed conditions
  - **Acceptance:** 3 verification checkpoints added

---

### Milestone 3: Output Format and Quality Standards

- [ ] **T3.1** Add Output Format section with review report template
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Add markdown template including:
    - Header with metadata (feature name, date, reviewer, status, SHAs)
    - Summary Statistics table (by severity, by dimension)
    - Specification Validation checklist (criterion, status, evidence)
    - Findings sections by severity (Critical, High, Medium, Low, Info)
    - Finding format: ID, file:line, description, suggestion, rationale
    - Strengths section
    - Recommendations section
  - **Acceptance:** Complete template with all sections

- [ ] **T3.2** Add Severity Reference table
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Document severity levels: Critical (blocks), High (should fix), Medium (maintainability), Low (nice to have), Info (no action). Include when to use each.
  - **Acceptance:** All 5 severity levels documented with criteria

- [ ] **T3.3** Add Dimension Reference table
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Document all 8 dimensions with priority (P0/P1/P2), focus areas, and example issues
  - **Acceptance:** All 8 dimensions documented with examples

- [ ] **T3.4** Add Quality Standards checklist
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Add checklist that every review must satisfy: spec read, all dimensions reviewed, linters run (if available), all findings have location+suggestion+rationale, verdict determined, blocking issues identified
  - **Acceptance:** Minimum 8 quality checkboxes

- [ ] **T3.5** Add Integration section
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
  - **Details:** Document: Triggered by execution-coordinator, Input (specification, implementation_summary, optional SHAs), Output (review report with findings and verdict)
  - **Acceptance:** Integration pattern documented

---

### Milestone 4: Workflow Integration Updates

- [ ] **T4.1** Update execution-coordinator.md Testing Agent table
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/execution-coordinator.md`
  - **Details:** Change `superpowers:code-reviewer` to `dev-workflow:code-reviewer` in the Specialist Agents table
  - **Acceptance:** Reference updated to internal agent

- [ ] **T4.2** Update SKILL.md External Agents section
  - **Files:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/skills/dev-workflow/SKILL.md`
  - **Details:** Remove or mark `superpowers:code-reviewer` as replaced. Add note that `dev-workflow:code-reviewer` is now used internally.
  - **Acceptance:** External dependency documented as replaced

---

### Final Tasks

- [ ] **TF.1** Run linting/formatting checks
  - **Command:** N/A (Markdown files, no linter)
  - **Acceptance:** Files are well-formatted

- [ ] **TF.2** Verify agent invocation pattern
  - **Command:** Search for Task invocation examples
  - **Acceptance:** Agent can be invoked with `Task(subagent_type: "dev-workflow:code-reviewer")`

- [ ] **TF.3** Commit changes
  - **Files:** All modified files in this task list
  - **Message format:** `feat(dev-workflow): Add code-reviewer agent`
  - **Acceptance:** Changes committed with descriptive message

---

## Task Dependencies

```
T1.1 ──▶ T1.2 ──▶ T1.3 ──▶ T1.4 ──▶ T1.5
                                      │
                                      ▼
T2.1 ──▶ T2.2 ──▶ T2.3 ──▶ T2.4 ──▶ T2.5 ──▶ T2.6 ──▶ T2.7 ──▶ T2.8
                                                                  │
                                                                  ▼
T3.1 ──▶ T3.2 ──▶ T3.3 ──▶ T3.4 ──▶ T3.5
                                      │
                                      ▼
                           T4.1 ──┬──▶ TF.1 ──▶ TF.2 ──▶ TF.3
                                  │
                           T4.2 ──┘
```

## Priority Order

1. **T1.1-T1.5** - Foundation must exist before adding content
2. **T2.1-T2.8** - Review process is the core functionality
3. **T3.1-T3.5** - Output format ensures structured, usable results
4. **T4.1-T4.2** - Integration updates enable actual usage
5. **TF.1-TF.3** - Final verification and commit

## Files Summary

| File | Operations |
|------|------------|
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md` | Create, add all sections (T1.1-T3.5) |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/execution-coordinator.md` | Update reference (T4.1) |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/skills/dev-workflow/SKILL.md` | Update external agents section (T4.2) |

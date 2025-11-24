# Implementation Plan: dev-workflow:code-reviewer Agent

**Specification:** `/home/jenningsl/development/claude-artifacts/specification/08-code-review-agent/08-specification.md`
**Estimated Phases:** 4

## Milestones

### Milestone 1: Core Agent Definition

**Goal:** Create the base agent file with proper structure, frontmatter, and core sections following established patterns

**Dependencies:** None

#### Deliverables

- [ ] Agent file created at `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`
- [ ] YAML frontmatter with name, description, model
- [ ] Opening persona statement
- [ ] Core Capabilities section (6 capabilities)
- [ ] Philosophy section with review principles
- [ ] Input Context section defining expected inputs

#### Acceptance Criteria

- File follows exact format of existing agents (qa-agent, code-assessor)
- Frontmatter includes `name: code-reviewer`, description, `model: sonnet`
- Core capabilities cover all 6 key functions from specification
- Input context matches Task invocation pattern

#### Files Affected

- `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md` (new file)

---

### Milestone 2: Review Process Implementation

**Goal:** Implement the complete 7-step review process with verification checkpoints

**Dependencies:** Milestone 1 complete

#### Deliverables

- [ ] Step 1: Parse Context and Validate Inputs
- [ ] Step 2: Read and Analyze Specification
- [ ] Step 3: Scope Changes (Git SHA or file list)
- [ ] Step 4: Run Static Analysis Integration
- [ ] Step 5: Dimension Reviews (all 8 dimensions)
- [ ] Step 6: Validate Against Specification
- [ ] Step 7: Synthesize and Generate Report
- [ ] Verification checkpoints at key steps

#### Acceptance Criteria

- Each step has clear instructions and checklists
- Static analysis detection covers TypeScript, Python, Rust, Go
- All 8 dimensions have specific review criteria
- Specification validation checks acceptance criteria and non-goals
- Verification blocks follow `<step_N_verification>` pattern

#### Files Affected

- `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`

---

### Milestone 3: Output Format and Quality Standards

**Goal:** Define structured output format and quality standards checklist

**Dependencies:** Milestone 2 complete

#### Deliverables

- [ ] Review Report markdown template
- [ ] Finding format with all required fields (location, severity, suggestion, rationale)
- [ ] Specification Validation section
- [ ] Summary Statistics section
- [ ] Verdict determination section
- [ ] Quality Standards checklist
- [ ] Integration section (triggered by, input, output)

#### Acceptance Criteria

- Output template matches specification data model
- All severity levels documented (Critical/High/Medium/Low/Info)
- All dimensions listed (Correctness, Security, Performance, etc.)
- Verdict logic documented (Critical = Blocked)
- Quality standards cover all essential requirements
- Integration matches execution-coordinator workflow

#### Files Affected

- `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`

---

### Milestone 4: Workflow Integration Updates

**Goal:** Update existing files to reference new internal agent instead of external dependency

**Dependencies:** Milestone 3 complete

#### Deliverables

- [ ] Update execution-coordinator.md Testing Agent table
- [ ] Update SKILL.md External Agents section
- [ ] Update spec-writer.md Task TF.3 reference (if needed)
- [ ] Verify agent is invokable via Task tool

#### Acceptance Criteria

- All references to `superpowers:code-reviewer` replaced with `dev-workflow:code-reviewer`
- SKILL.md marks external dependency as replaced
- Agent can be invoked with standard Task pattern
- No broken references remain

#### Files Affected

- `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/execution-coordinator.md`
- `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/skills/dev-workflow/SKILL.md`
- `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/spec-writer.md`

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Static analysis tools not available in execution environment | Medium | Low | Agent gracefully skips with warning; AI-only review still functional |
| Large diffs exceed context window | Low | Medium | Implement chunked review for >5000 lines |
| Specification format varies across projects | Medium | Low | Parser handles common markdown formats; falls back to generic review |
| External linter output format changes | Low | Low | JSON output parsing is stable; version-specific parsing if needed |

## Dependencies

### External Dependencies

- **Project linters**: ESLint, Biome, Ruff, Clippy, golangci-lint (optional, detected dynamically)
- **Git**: For SHA-based diff scoping (optional)

### Internal Dependencies

- **spec-writer output**: Technical specification document
- **code-assessor output**: Assessment with patterns to follow
- **execution-coordinator**: Invokes this agent during implementation phase

## Success Metrics

- [ ] Agent can be invoked via `Task(subagent_type: "dev-workflow:code-reviewer")`
- [ ] Review output includes all 8 dimensions
- [ ] Specification validation checks all acceptance criteria
- [ ] Static analysis integrates when linters available
- [ ] Findings include location, severity, suggestion, rationale
- [ ] Verdict correctly classifies Critical issues as blocking
- [ ] No external dependency on `superpowers:code-reviewer`
- [ ] Integration tests pass with sample implementation

## Timeline Estimate

| Milestone | Estimated Effort | Cumulative |
|-----------|------------------|------------|
| M1: Core Agent Definition | 30 minutes | 30 minutes |
| M2: Review Process | 45 minutes | 1.25 hours |
| M3: Output and Standards | 30 minutes | 1.75 hours |
| M4: Workflow Integration | 15 minutes | 2 hours |

**Total Estimated Effort:** 2 hours

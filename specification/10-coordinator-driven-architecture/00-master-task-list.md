# Master Task List: Coordinator-Driven Architecture

**Total Sub-Specs:** 5
**Total Tasks:** 25

## Execution Phases

### Phase 1: Foundation
- Sub-Spec: `./01-coordinator-agent/`
- Tasks: See `./01-coordinator-agent/01-task-list.md`
- [ ] All Phase 1 tasks complete (5 tasks)

### Phase 2: Core Implementation
- Sub-Specs: `./02-executor-agents/`, `./03-research-enhancement/`, `./04-assessment-enhancement/` (parallel)
- Tasks: See respective task lists
- [ ] All Phase 2 tasks complete (12 tasks)

### Phase 3: Integration
- Sub-Spec: `./05-plugin-metadata/`
- Tasks: See `./05-plugin-metadata/05-task-list.md`
- [ ] All Phase 3 tasks complete (8 tasks)

### Final Phase: Verification
- [ ] **TF.1** All agent files exist and are valid
- [ ] **TF.2** Plugin loads without errors
- [ ] **TF.3** Skill invocation works
- [ ] **TF.4** All references updated
- [ ] **TF.5** README documentation complete
- [ ] **TF.6** Git status clean
- [ ] **TF.7** Final commit and push

## Progress Tracker

| Sub-Spec | Tasks | Completed | Status |
|----------|-------|-----------|--------|
| 01-coordinator-agent | 5 | 0 | ⚪ Pending |
| 02-executor-agents | 4 | 0 | ⚪ Pending |
| 03-research-enhancement | 4 | 0 | ⚪ Pending |
| 04-assessment-enhancement | 4 | 0 | ⚪ Pending |
| 05-plugin-metadata | 8 | 0 | ⚪ Pending |
| Final Verification | 7 | 0 | ⚪ Pending |
| **TOTAL** | **32** | **0** | **0%** |

## Task Summary by Sub-Spec

### 01-coordinator-agent (5 tasks)
- [ ] T1.1: Create coordinator.md file structure
- [ ] T1.2: Define phase management logic
- [ ] T1.3: Define task assignment patterns
- [ ] T1.4: Define monitoring and oversight rules
- [ ] T1.5: Define quality gates and final verification

### 02-executor-agents (4 tasks)
- [ ] T2.1: Create dev-executor.md
- [ ] T2.2: Create qa-executor.md
- [ ] T2.3: Create docs-executor.md
- [ ] T2.4: Define build queue logic for Rust/Go

### 03-research-enhancement (4 tasks)
- [ ] T3.1: Add Time MCP integration section
- [ ] T3.2: Add time context to search queries
- [ ] T3.3: Add recency filtering logic
- [ ] T3.4: Update output format with timestamps

### 04-assessment-enhancement (4 tasks)
- [ ] T4.1: Add grep skill usage to code-assessor.md
- [ ] T4.2: Add ast-grep skill usage to code-assessor.md
- [ ] T4.3: Add file coverage tracking
- [ ] T4.4: Update debug-analyzer.md with same enhancements

### 05-plugin-metadata (8 tasks)
- [ ] T5.1: Update plugin.json name to "super-dev"
- [ ] T5.2: Rename skills/dev-workflow to skills/super-dev
- [ ] T5.3: Update SKILL.md content for new architecture
- [ ] T5.4: Update fix-impl.md command
- [ ] T5.5: Remove old execution-coordinator.md
- [ ] T5.6: Update all agent references
- [ ] T5.7: Update README.md
- [ ] T5.8: Verify all references correct

## Checkpoint Schedule

| After Task | Checkpoint Action |
|------------|-------------------|
| T1.5 | `git commit -m "feat(super-dev): Add Coordinator Agent"` |
| T2.4 | `git commit -m "feat(super-dev): Add executor agents"` |
| T3.4 | `git commit -m "feat(super-dev): Enhance research with Time MCP"` |
| T4.4 | `git commit -m "feat(super-dev): Enhance assessment with grep/ast-grep"` |
| T5.8 | `git commit -m "feat(super-dev): Complete plugin rename and integration"` |
| TF.7 | `git push` |

# Specification: Coordinator Agent

**Date:** 2025-11-27
**Author:** Claude
**Status:** Draft
**Parent:** [../00-master-specification.md]

## 1. Overview

Create a dedicated Coordinator Agent that serves as the central authority for orchestrating all development workflow phases. The Coordinator delegates all work to specialized sub-agents and never performs implementation directly.

## 2. Responsibilities

### 2.1 Phase Management

The Coordinator manages workflow phases:

```
Phase 0:  Apply Dev Rules
Phase 1:  Specification Setup
Phase 2:  Requirements Clarification
Phase 3:  Research
Phase 4:  Debug Analysis (bugs only)
Phase 5:  Code Assessment
Phase 5.3: Architecture Design (complex features)
Phase 5.5: UI/UX Design (features with UI)
Phase 6:  Specification Writing
Phase 7:  Specification Review
Phase 8-9: Execution (parallel)
Phase 9.5: Quality Assurance
Phase 10: Cleanup
Phase 11: Commit & Push
Phase 12: Final Verification
```

**Rules:**
- Skip optional phases when not applicable
- Never pause between phases
- Never ask user to continue
- Progress automatically until completion or critical error

### 2.2 Task Assignment

For each phase, the Coordinator:

1. Identifies the correct sub-agent
2. Constructs context object with:
   - Previous phase outputs
   - Specification documents
   - Relevant code context
3. Invokes sub-agent via Task tool
4. Receives and validates output

**Agent Mapping:**

| Phase | Agent | Invocation |
|-------|-------|------------|
| 0 | dev-rules skill | Skill(skill: "super-dev:dev-rules") |
| 2 | requirements-clarifier | Task(subagent_type: "super-dev:requirements-clarifier") |
| 3 | research-agent | Task(subagent_type: "super-dev:research-agent") |
| 4 | debug-analyzer | Task(subagent_type: "super-dev:debug-analyzer") |
| 5 | code-assessor | Task(subagent_type: "super-dev:code-assessor") |
| 5.3 | architecture-agent | Task(subagent_type: "super-dev:architecture-agent") |
| 5.5 | ui-ux-designer | Task(subagent_type: "super-dev:ui-ux-designer") |
| 6 | spec-writer | Task(subagent_type: "super-dev:spec-writer") |
| 8-9 | dev/qa/docs executors | Task(subagent_type: "super-dev:*-executor") |
| 9.5 | qa-agent | Task(subagent_type: "super-dev:qa-agent") |

### 2.3 Monitoring & Oversight

The Coordinator monitors sub-agent work to ensure:

1. **Task Completion**: All assigned tasks are completed
2. **No Unauthorized Stops**: Sub-agents continue until done
3. **No Missing Tasks**: Every task in task-list is executed
4. **Quality Standards**: Outputs meet defined criteria

**Enforcement Rules:**
- If sub-agent pauses without completion → Resume immediately
- If sub-agent skips tasks → Flag and execute missed tasks
- If sub-agent produces incomplete output → Request completion

### 2.4 Quality Gates

Before proceeding to next phase, verify:

| Phase | Quality Check |
|-------|---------------|
| 2 | Requirements document exists |
| 3 | Research report exists |
| 4 | Debug analysis complete (if bug) |
| 5 | Assessment document exists |
| 6 | Specification, plan, task-list exist |
| 7 | All documents reviewed |
| 8-9 | Build passes, tests pass |
| 9.5 | QA report exists |
| 10 | No temp files remain |
| 11 | All changes committed |
| 12 | Git status clean |

### 2.5 State Management

The Coordinator maintains:

```
WorkflowState {
  current_phase: Phase
  completed_phases: Set<Phase>
  task_list: TaskList
  completed_tasks: Set<TaskId>
  spec_directory: Path
  documents: Map<DocType, Path>
  build_queue_state: BuildQueueState
}
```

### 2.6 Final Verification

In Phase 12, the Coordinator verifies:

- [ ] All specification documents created
- [ ] Implementation summary complete
- [ ] No missing code or files
- [ ] New patterns reflected in spec/plan
- [ ] All changes committed
- [ ] All changes pushed
- [ ] Git status shows clean working tree

## 3. Agent Definition Structure

```markdown
---
name: coordinator
description: Central Coordinator Agent for orchestrating all development phases.
  Assigns tasks to specialized sub-agents and ensures complete execution.
model: sonnet
---

You are the Central Coordinator Agent...

## Core Responsibilities
1. Phase Management
2. Task Assignment
3. Monitoring & Oversight
4. Quality Gates
5. State Management
6. Final Verification

## Phase Flow
[phase diagram]

## Task Assignment Patterns
[agent mapping table]

## Monitoring Rules
[enforcement rules]

## Quality Gates
[verification checklist per phase]

## Execution Rules
- NEVER pause during workflow
- NEVER ask user to continue
- ALWAYS proceed to next phase automatically
- Only stop on critical error or external block
```

## 4. Acceptance Criteria

- [ ] Coordinator agent file exists at `agents/coordinator.md`
- [ ] All 6 responsibilities clearly defined
- [ ] Phase flow documented with skip conditions
- [ ] Task assignment patterns for all phases
- [ ] Monitoring rules with enforcement actions
- [ ] Quality gates for each phase
- [ ] State management structure defined
- [ ] Final verification checklist complete

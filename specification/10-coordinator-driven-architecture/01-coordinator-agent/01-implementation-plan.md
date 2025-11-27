# Implementation Plan: Coordinator Agent

**Date:** 2025-11-27
**Parent:** [../00-master-implementation-plan.md]

## 1. Implementation Approach

Create the Coordinator Agent as a single comprehensive markdown file that defines:
- Agent metadata (name, description, model)
- Core responsibilities
- Phase management logic
- Task assignment patterns
- Monitoring rules
- Quality gates

## 2. File to Create

**Path:** `~/.claude/plugins/.../dev-workflow-plugin/agents/coordinator.md`

## 3. Structure

```markdown
---
name: coordinator
description: Central Coordinator Agent...
model: sonnet
---

# Coordinator Agent

## Core Responsibilities
[6 responsibilities with details]

## Phase Management
[Phase flow with skip conditions]

## Task Assignment
[Agent mapping for each phase]

## Monitoring & Oversight
[Enforcement rules]

## Quality Gates
[Verification checklist per phase]

## State Management
[State structure definition]

## Execution Rules
[Critical execution rules]

## Final Verification
[Final phase checklist]
```

## 4. Dependencies

- None (foundation component)

## 5. Validation

After creation:
1. File exists and is valid markdown
2. All 6 responsibilities defined
3. Phase flow complete
4. Task assignment covers all phases
5. No syntax errors in markdown

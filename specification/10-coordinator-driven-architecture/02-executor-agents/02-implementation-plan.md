# Implementation Plan: Executor Agents

**Date:** 2025-11-27
**Parent:** [../00-master-implementation-plan.md]

## 1. Files to Create

1. `agents/dev-executor.md` - Development execution
2. `agents/qa-executor.md` - QA execution
3. `agents/docs-executor.md` - Documentation execution

## 2. Structure per Agent

Each agent follows structure:
```markdown
---
name: [dev|qa|docs]-executor
description: ...
model: sonnet
---

# [Name] Executor Agent

## Responsibilities
[List of responsibilities]

## Execution Patterns
[How agent performs work]

## Coordination
[How agent coordinates with others]

## Build Policy (dev/qa only)
[Build queue rules for Rust/Go]

## Output
[What agent produces]
```

## 3. Implementation Order

1. dev-executor.md (primary)
2. qa-executor.md (tests dev output)
3. docs-executor.md (documents both)

## 4. Dependencies

- Sub-Spec 01 (Coordinator Agent)

## 5. Validation

After creation:
1. All 3 files exist
2. Each has valid YAML frontmatter
3. Responsibilities clearly defined
4. Build policy documented for dev/qa
5. Coordination patterns clear

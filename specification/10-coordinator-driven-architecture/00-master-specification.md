# Master Specification: Coordinator-Driven Architecture Redesign

**Date:** 2025-11-27
**Author:** Claude
**Status:** Draft

## 1. Feature Overview

### 1.1 Summary

Complete architectural redesign of the dev-workflow plugin to implement a dedicated Coordinator Agent that orchestrates all development phases using a subagent-driven methodology, with parallel execution in the execution phase and comprehensive verification.

### 1.2 Goals

- Create a central Coordinator Agent as the single authority for workflow orchestration
- Enable parallel execution of dev/QA/docs agents during execution phase
- Implement build serialization for Rust/Go projects
- Enhance research agent with Time MCP for current information
- Update assessment/debug agents with grep/ast-grep skills
- Rename plugin from "dev-workflow" to "super-dev"

### 1.3 Scope Decomposition

This feature is split into the following sub-specifications:

| Index | Sub-Spec | Description | Dependencies |
|-------|----------|-------------|--------------|
| 01 | coordinator-agent | Create central Coordinator Agent | None |
| 02 | executor-agents | Create dev/qa/docs executor agents | 01 |
| 03 | research-enhancement | Add Time MCP to research agent | 01 |
| 04 | assessment-enhancement | Add grep/ast-grep to assessor/debug | 01 |
| 05 | plugin-metadata | Rename plugin, update skill | 01, 02, 03, 04 |

## 2. Sub-Specification Dependencies

```
01-coordinator-agent
       │
       ├───────────────────┬───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
02-executor-agents  03-research-enhancement  04-assessment-enhancement
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                  05-plugin-metadata
```

## 3. Integration Points

### 3.1 Interfaces Between Sub-Specs

| From | To | Interface | Contract |
|------|-----|-----------|----------|
| 01 | 02 | Coordinator invokes executors | Task(subagent_type: "super-dev:*-executor") |
| 01 | 03 | Coordinator invokes research | Task(subagent_type: "super-dev:research-agent") |
| 01 | 04 | Coordinator invokes assessor/debug | Task(subagent_type: "super-dev:code-assessor") |
| 02 | 05 | Executors registered in skill | Agent definitions in SKILL.md |
| 03 | 05 | Research registered in skill | Agent definitions in SKILL.md |
| 04 | 05 | Assessment registered in skill | Agent definitions in SKILL.md |

### 3.2 Shared Components

- **Coordinator context**: Used by sub-specs 02, 03, 04
- **Build queue logic**: Used by sub-spec 02 (dev-executor, qa-executor)
- **Skill documentation**: Aggregates all sub-spec agents in sub-spec 05

## 4. Implementation Order

**Phase 1:** Sub-spec 01 - Coordinator Agent (foundation)
**Phase 2:** Sub-specs 02, 03, 04 (parallel, depends on 01)
**Phase 3:** Sub-spec 05 - Plugin Metadata (integration, depends on all)

## 5. Success Criteria

- [ ] Coordinator Agent orchestrates all workflow phases
- [ ] Three executor agents run in parallel during execution
- [ ] Build serialization enforced for Rust/Go
- [ ] Research agent uses Time MCP for current information
- [ ] Assessment/debug agents use grep/ast-grep skills
- [ ] Plugin renamed to "super-dev" with all references updated
- [ ] All existing functionality preserved
- [ ] Documentation complete and accurate

## 6. References

- Sub-Spec 01: [./01-coordinator-agent/01-specification.md]
- Sub-Spec 02: [./02-executor-agents/02-specification.md]
- Sub-Spec 03: [./03-research-enhancement/03-specification.md]
- Sub-Spec 04: [./04-assessment-enhancement/04-specification.md]
- Sub-Spec 05: [./05-plugin-metadata/05-specification.md]

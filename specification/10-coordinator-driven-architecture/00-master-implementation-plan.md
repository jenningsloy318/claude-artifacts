# Master Implementation Plan: Coordinator-Driven Architecture

**Date:** 2025-11-27
**Author:** Claude
**Status:** Draft

## 1. Implementation Strategy

### 1.1 Approach

Implement in 3 phases following the dependency graph:
1. Foundation (Coordinator Agent)
2. Core Components (Executors, Research, Assessment) - can run in parallel
3. Integration (Plugin Metadata)

### 1.2 Risk Mitigation

- **Git Checkpoints**: Commit after each sub-spec completion
- **Incremental Testing**: Verify each component before proceeding
- **Backward Compatibility**: Keep directory name, only change internal names

## 2. Phase Breakdown

### Phase 1: Foundation (Sub-Spec 01)

**Goal:** Create the central Coordinator Agent

**Components:**
- `agents/coordinator.md` - Central orchestrator

**Estimated Tasks:** 5
**Dependencies:** None

**Deliverables:**
- Coordinator agent definition
- Phase management logic
- Task assignment patterns
- Monitoring rules
- Quality gate definitions

### Phase 2: Core Components (Sub-Specs 02, 03, 04)

**Goal:** Create executor agents and enhance existing agents

**Can Run in Parallel:**
- Sub-Spec 02: Executor Agents
- Sub-Spec 03: Research Enhancement
- Sub-Spec 04: Assessment Enhancement

**Components:**
- `agents/dev-executor.md` - Development execution
- `agents/qa-executor.md` - QA execution
- `agents/docs-executor.md` - Documentation execution
- `agents/research-agent.md` - Updated with Time MCP
- `agents/code-assessor.md` - Updated with grep/ast-grep
- `agents/debug-analyzer.md` - Updated with grep/ast-grep

**Estimated Tasks:** 12 (4 + 4 + 4)
**Dependencies:** Phase 1

**Deliverables:**
- Three executor agent definitions
- Parallel execution patterns
- Build queue logic
- Time MCP integration
- grep/ast-grep skill usage

### Phase 3: Integration (Sub-Spec 05)

**Goal:** Rename plugin and update skill documentation

**Components:**
- `.claude-plugin/plugin.json` - Plugin metadata
- `skills/super-dev/SKILL.md` - Main skill (renamed)
- `commands/fix-impl.md` - Slash command
- `README.md` - Documentation

**Estimated Tasks:** 8
**Dependencies:** Phases 1, 2

**Deliverables:**
- Updated plugin.json with name "super-dev"
- Renamed skill directory
- Updated skill documentation
- Updated command
- Updated README

## 3. Implementation Timeline

```
Phase 1: Foundation
├── Task 1.1: Create coordinator.md structure
├── Task 1.2: Define phase management
├── Task 1.3: Define task assignment
├── Task 1.4: Define monitoring rules
├── Task 1.5: Define quality gates
└── CHECKPOINT: Commit coordinator agent

Phase 2: Core Components (Parallel)
├── Sub-Spec 02: Executor Agents
│   ├── Task 2.1: Create dev-executor.md
│   ├── Task 2.2: Create qa-executor.md
│   ├── Task 2.3: Create docs-executor.md
│   └── Task 2.4: Define build queue logic
├── Sub-Spec 03: Research Enhancement
│   ├── Task 3.1: Add Time MCP section
│   ├── Task 3.2: Add time context to queries
│   ├── Task 3.3: Add recency filtering
│   └── Task 3.4: Update output format
├── Sub-Spec 04: Assessment Enhancement
│   ├── Task 4.1: Add grep skill usage
│   ├── Task 4.2: Add ast-grep skill usage
│   ├── Task 4.3: Add file coverage tracking
│   └── Task 4.4: Update debug-analyzer.md
└── CHECKPOINT: Commit all core components

Phase 3: Integration
├── Task 5.1: Update plugin.json
├── Task 5.2: Rename skill directory
├── Task 5.3: Update SKILL.md content
├── Task 5.4: Update fix-impl.md command
├── Task 5.5: Remove execution-coordinator.md
├── Task 5.6: Update README.md
├── Task 5.7: Final verification
└── Task 5.8: Final commit and push
```

## 4. Quality Gates

### Phase 1 Gate
- [ ] Coordinator agent file exists
- [ ] All 6 responsibilities defined
- [ ] Phase flow documented
- [ ] Task assignment patterns clear

### Phase 2 Gate
- [ ] All 3 executor agents exist
- [ ] Parallel execution documented
- [ ] Build queue logic defined
- [ ] Research agent has Time MCP
- [ ] Assessment agents have grep/ast-grep

### Phase 3 Gate
- [ ] plugin.json name is "super-dev"
- [ ] Skill directory renamed
- [ ] All agent references updated
- [ ] README reflects new architecture
- [ ] No broken references

## 5. Rollback Plan

If issues discovered:
1. Use git stash/revert to restore previous state
2. Each phase has checkpoint commit
3. Sub-specs are independent (except 05)
4. Can revert single sub-spec without affecting others

## 6. Sub-Spec Implementation Plans

Detailed implementation plans in:
- [./01-coordinator-agent/01-implementation-plan.md]
- [./02-executor-agents/02-implementation-plan.md]
- [./03-research-enhancement/03-implementation-plan.md]
- [./04-assessment-enhancement/04-implementation-plan.md]
- [./05-plugin-metadata/05-implementation-plan.md]

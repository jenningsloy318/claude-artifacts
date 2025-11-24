# Technical Specification: Dev Workflow Plugin

**Date:** 2025-11-23 21:40 PST
**Author:** Claude
**Status:** Approved

---

## 1. Overview

### 1.1 Summary

Convert the monolithic `fix-impl.md` command into a modular Claude Code plugin with:
- 8 skills covering all 11 workflow phases
- 1 entry command for invocation
- Development rules from CLAUDE.md integrated

### 1.2 Goals

- Modular, maintainable plugin structure
- Clear separation of concerns
- Reusable skills for individual phases
- Integration with specialist agents
- Comprehensive documentation

### 1.3 Non-Goals

- Custom hook scripts
- External API integrations
- User preference storage

---

## 2. Background

### 2.1 Context

Research findings indicate Claude Code plugins use a skill-based architecture where:
- Skills define processes and methodologies
- Agents (via Task tool) execute autonomous work
- Commands provide entry points

### 2.2 Current State

Original `fix-impl.md` is a 143-line monolithic command requiring conversion to plugin format.

### 2.3 Problem Statement

The monolithic command lacks modularity, making updates difficult and preventing skill reuse.

---

## 3. Technical Design

### 3.1 Architecture

```
dev-workflow-plugin/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── skills/
│   ├── dev-workflow/
│   │   └── SKILL.md            # Main orchestrator (Phase 1,7,10,11)
│   ├── dev-rules/
│   │   └── SKILL.md            # Development rules from CLAUDE.md
│   ├── requirements-clarifier/
│   │   └── SKILL.md            # Phase 2
│   ├── research-phase/
│   │   └── SKILL.md            # Phase 3
│   ├── debug-analyzer/
│   │   └── SKILL.md            # Phase 4
│   ├── code-assessor/
│   │   └── SKILL.md            # Phase 5
│   ├── spec-writer/
│   │   └── SKILL.md            # Phase 6
│   └── execution-coordinator/
│       └── SKILL.md            # Phase 8-9
├── commands/
│   └── fix-impl.md             # Entry command
└── README.md
```

### 3.2 Components

#### Component: dev-workflow (Main Skill)

- **Purpose:** Orchestrate all 11 phases
- **Responsibilities:**
  - Phase 1: Specification setup
  - Phase 7: Specification review
  - Phase 10: Cleanup
  - Phase 11: Commit & push
  - Invoke sub-skills for other phases
- **Interfaces:** Skill invocation via Skill tool

#### Component: dev-rules (Rules Skill)

- **Purpose:** Define development standards
- **Responsibilities:**
  - Git workflow rules
  - Development philosophy
  - Quality standards
  - Decision framework
- **Interfaces:** Referenced by other skills

#### Component: requirements-clarifier (Phase 2)

- **Purpose:** Gather complete requirements
- **Responsibilities:**
  - Problem statement analysis
  - Success criteria definition
  - Edge case identification
- **Interfaces:** Creates requirements.md

#### Component: research-phase (Phase 3)

- **Purpose:** Research best practices
- **Responsibilities:**
  - Documentation lookup
  - Pattern research
  - Best practices gathering
- **Interfaces:** Creates research-report.md

#### Component: debug-analyzer (Phase 4)

- **Purpose:** Root cause analysis for bugs
- **Responsibilities:**
  - Evidence collection
  - Hypothesis formation
  - Root cause identification
- **Interfaces:** Creates debug-analysis.md

#### Component: code-assessor (Phase 5)

- **Purpose:** Evaluate existing codebase
- **Responsibilities:**
  - Architecture evaluation
  - Standards review
  - Dependency analysis
- **Interfaces:** Creates assessment.md

#### Component: spec-writer (Phase 6)

- **Purpose:** Create technical documentation
- **Responsibilities:**
  - Technical specification
  - Implementation plan
  - Task list
- **Interfaces:** Creates spec, plan, tasks files

#### Component: execution-coordinator (Phase 8-9)

- **Purpose:** Coordinate implementation
- **Responsibilities:**
  - Agent assignment
  - Progress tracking
  - Build verification
- **Interfaces:** Spawns specialist agents

### 3.3 Data Model

**Specification Directory Structure:**
```
specification/[index]-[name]/
├── [index]-requirements.md
├── [index]-research-report.md
├── [index]-debug-analysis.md      # (bugs only)
├── [index]-assessment.md
├── [index]-technical-spec.md
├── [index]-implementation-plan.md
├── [index]-task-list.md
└── [index]-implementation-summary.md
```

### 3.4 Skill Invocation Flow

```
/dev-workflow:fix-impl [task]
        │
        ▼
   dev-workflow skill
        │
        ├──▶ requirements-clarifier (Phase 2)
        ├──▶ research-phase (Phase 3)
        ├──▶ debug-analyzer (Phase 4, bugs only)
        ├──▶ code-assessor (Phase 5)
        ├──▶ spec-writer (Phase 6)
        └──▶ execution-coordinator (Phase 8-9)
                    │
                    ├──▶ Task: backend-developer
                    ├──▶ Task: frontend-developer
                    ├──▶ Task: superpowers:code-reviewer
                    └──▶ Task: documentation-expert
```

---

## 4. Implementation Approach

### 4.1 Technology Stack

- Markdown with YAML frontmatter (skills)
- JSON (plugin.json, marketplace.json)
- Claude Code Plugin Architecture

### 4.2 Dependencies

- superpowers plugin (agent references)
- ast-grep skill (code search)
- MCP tools (browser testing)

### 4.3 Configuration

**plugin.json:**
```json
{
  "name": "dev-workflow",
  "description": "Comprehensive development workflow...",
  "version": "1.0.0",
  "author": { "name": "Jennings L" },
  "license": "MIT",
  "keywords": ["development", "workflow", "debugging"]
}
```

---

## 5. Testing Strategy

### 5.1 Manual Testing

- Invoke `/dev-workflow:fix-impl` with sample task
- Verify each skill is invoked correctly
- Check output documents are created

### 5.2 Edge Cases

- Bug vs feature detection
- Missing specification directory
- Parallel agent failures

---

## 6. Security Considerations

- No external API calls
- No credential storage
- Local file operations only

---

## 7. Performance Considerations

- Skills load on demand
- Agents run in parallel where possible
- Document generation is incremental

---

## 8. Rollout Plan

1. Create plugin structure
2. Implement all skills
3. Create entry command
4. Register in marketplace
5. Test end-to-end

---

## 9. Open Questions

None - all design decisions resolved.

---

## 10. References

- Research Report: `01-research-report.md`
- Assessment: `02-assessment.md`

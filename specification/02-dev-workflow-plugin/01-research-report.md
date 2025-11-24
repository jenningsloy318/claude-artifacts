# Research Report: Dev Workflow Plugin

**Date:** 2025-11-23 21:30 PST
**Feature:** Comprehensive Development Workflow Plugin for Claude Code

---

## 1. Executive Summary

This report documents research findings for converting the `~/.claude/commands/dev/fix-impl.md` command into a modular Claude Code plugin with skills and agents.

The original command is a 143-line development workflow that guides through 11 phases for implementing features, fixing bugs, and refactoring code.

---

## 2. Source Analysis

### 2.1 Original Command Structure

**Location:** `~/.claude/commands/dev/fix-impl.md`

**11 Phases:**
| Phase | Name | Purpose |
|-------|------|---------|
| 1 | Specification Setup | Find/create spec directory |
| 2 | Requirements Clarification | Gather complete requirements |
| 3 | Research | Find best practices |
| 4 | Debug Analysis | Root cause analysis (bugs only) |
| 5 | Code Assessment | Evaluate existing codebase |
| 6 | Specification Writing | Create tech spec, plan, tasks |
| 7 | Specification Review | Validate all documents |
| 8 | Execution | Implement with parallel agents |
| 9 | Coordination | Sequential task completion |
| 10 | Cleanup | Remove temporary files |
| 11 | Commit & Push | Save changes to repository |

### 2.2 Rules to Incorporate

**From `~/.claude/CLAUDE.md`:**

1. **Git Rules:**
   - Never create GitHub actions
   - Only commit files edited in current session
   - Use `git add file1 file2` not `git add -A`

2. **Development Philosophy:**
   - Incremental development (small commits)
   - Learn from existing code first
   - Pragmatic over dogmatic
   - Clear intent over clever code

3. **Quality Standards:**
   - Testability first
   - Readability (understandable in 6 months)
   - Consistency with project patterns
   - Simplicity (minimal complexity)

---

## 3. Claude Code Plugin Architecture

### 3.1 Plugin Structure

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/
│   └── skill-name/
│       └── SKILL.md         # Skill definition
├── commands/
│   └── command-name.md      # Slash command
├── hooks/
│   └── hook-name.py         # Hook scripts
└── README.md
```

### 3.2 Skills vs Agents

| Aspect | Skills | Agents |
|--------|--------|--------|
| Definition | Instructional templates in SKILL.md | Spawned via Task tool |
| Execution | Within current context | Independent subprocess |
| Purpose | Process/methodology guidance | Autonomous task execution |
| State | Shared with conversation | Isolated |
| Best for | Workflows, checklists, patterns | Code review, implementation, research |

### 3.3 Skill Format

```markdown
---
name: skill-name
description: When to use this skill
---

# Skill Name

Instructions and content...
```

### 3.4 Available Specialist Agents

| Agent | Purpose |
|-------|---------|
| `rust-pro` | Rust development |
| `backend-developer` | Backend services |
| `frontend-developer` | UI components |
| `mobile-developer` | Mobile apps |
| `superpowers:code-reviewer` | Code review |
| `superpowers:test-driven-development` | TDD approach |
| `superpowers:systematic-debugging` | Debugging methodology |
| `superpowers:root-cause-tracing` | Bug tracing |
| `documentation-expert` | Technical documentation |

---

## 4. Design Decision: Skills vs Agents

### 4.1 Analysis

**Should be Skills (methodology/process):**
- Dev workflow orchestration
- Development rules
- Requirements clarification process
- Research process
- Debug analysis methodology
- Code assessment checklist
- Specification writing templates
- Execution coordination

**Should reference Agents (autonomous work):**
- Actual code implementation
- Code review
- Testing execution
- Documentation writing

### 4.2 Conclusion

The workflow phases are best implemented as **skills** because they define processes, checklists, and methodologies that guide Claude's actions within the conversation context.

**Agents** should be referenced within skills (especially in execution-coordinator) for actual implementation work that can run autonomously.

---

## 5. Marketplace Integration

### 5.1 Plugin Registration

Plugins are registered in `.claude-plugin/marketplace.json`:

```json
{
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugin-directory",
      "description": "Description",
      "version": "1.0.0",
      "keywords": ["tag1", "tag2"],
      "category": "development"
    }
  ]
}
```

### 5.2 Installation

Users add to their Claude Code settings:

```json
{
  "plugins": [
    "https://github.com/owner/repo/tree/main/plugin-directory"
  ]
}
```

---

## 6. References

- Claude Code Plugin Documentation
- Superpowers Marketplace: `~/.claude/plugins/cache/superpowers/`
- Original command: `~/.claude/commands/dev/fix-impl.md`
- Development rules: `~/.claude/CLAUDE.md`

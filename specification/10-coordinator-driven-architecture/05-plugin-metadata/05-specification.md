# Specification: Plugin Metadata Update

**Date:** 2025-11-27
**Author:** Claude
**Status:** Draft
**Parent:** [../00-master-specification.md]

## 1. Overview

Rename the plugin from "dev-workflow" to "super-dev" and update all related files, references, and documentation.

## 2. Files to Modify

### 2.1 Plugin Configuration

**File:** `.claude-plugin/plugin.json`

**Changes:**
```json
{
  "name": "super-dev",  // was "dev-workflow"
  "description": "Coordinator-driven development workflow with parallel execution...",
  "version": "2.0.0",  // version bump
  // ... rest unchanged
}
```

### 2.2 Skill Directory

**Action:** Rename directory

```
skills/dev-workflow/  →  skills/super-dev/
```

### 2.3 Main Skill File

**File:** `skills/super-dev/SKILL.md` (after rename)

**Changes:**
1. Update title: "# Super Dev Workflow"
2. Update all `dev-workflow:` references to `super-dev:`
3. Add Coordinator Agent as entry point
4. Update agent tables
5. Add parallel execution documentation

### 2.4 Slash Command

**File:** `commands/fix-impl.md`

**Changes:**
```markdown
# Before
/dev-workflow:fix-impl

# After
/super-dev:fix-impl
```

Update command to invoke Coordinator:
```markdown
## Execution
1. Invoke: Skill(skill: "super-dev:dev-rules")
2. Invoke: Task(subagent_type: "super-dev:coordinator", ...)
```

### 2.5 Old Execution Coordinator

**File:** `agents/execution-coordinator.md`

**Action:** DELETE (replaced by new agents)

### 2.6 All Agent Files

**Files:** All `agents/*.md`

**Changes:**
- Update any `dev-workflow:` references to `super-dev:`
- Update inter-agent references

### 2.7 README.md

**File:** `README.md`

**Changes:**
1. Update title: "# Super Dev Plugin"
2. Update installation instructions
3. Update command examples
4. Update architecture diagram
5. Add Coordinator Agent documentation
6. Add parallel execution documentation
7. Update agent tables

## 3. Reference Update Map

| Old Reference | New Reference |
|---------------|---------------|
| `dev-workflow` | `super-dev` |
| `dev-workflow:requirements-clarifier` | `super-dev:requirements-clarifier` |
| `dev-workflow:research-agent` | `super-dev:research-agent` |
| `dev-workflow:debug-analyzer` | `super-dev:debug-analyzer` |
| `dev-workflow:code-assessor` | `super-dev:code-assessor` |
| `dev-workflow:spec-writer` | `super-dev:spec-writer` |
| `dev-workflow:execution-coordinator` | `super-dev:coordinator` |
| `dev-workflow:rust-developer` | `super-dev:rust-developer` |
| (all other agents) | (same pattern) |

## 4. New Agent References

| New Agent | Reference |
|-----------|-----------|
| coordinator | `super-dev:coordinator` |
| dev-executor | `super-dev:dev-executor` |
| qa-executor | `super-dev:qa-executor` |
| docs-executor | `super-dev:docs-executor` |

## 5. Verification Checklist

After all updates:

- [ ] `plugin.json` name is "super-dev"
- [ ] `skills/super-dev/` directory exists
- [ ] `skills/dev-workflow/` directory removed
- [ ] All `dev-workflow:` replaced with `super-dev:`
- [ ] `execution-coordinator.md` deleted
- [ ] New agents referenced in SKILL.md
- [ ] README.md updated
- [ ] No broken references remain

## 6. Acceptance Criteria

- [ ] Plugin loads without errors
- [ ] Skill invocable via `super-dev:super-dev`
- [ ] Command invocable via `/super-dev:fix-impl`
- [ ] All agents invocable via `super-dev:*`
- [ ] No references to old "dev-workflow" name
- [ ] Documentation complete and accurate

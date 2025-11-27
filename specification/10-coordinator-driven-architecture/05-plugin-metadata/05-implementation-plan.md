# Implementation Plan: Plugin Metadata Update

**Date:** 2025-11-27
**Parent:** [../00-master-implementation-plan.md]

## 1. Implementation Order

Execute in this order to minimize broken references:

1. Update plugin.json (metadata first)
2. Rename skill directory
3. Update SKILL.md content
4. Update fix-impl.md command
5. Delete execution-coordinator.md
6. Update all agent references
7. Update README.md
8. Verify all references

## 2. Detailed Steps

### Step 1: plugin.json
```bash
# Edit .claude-plugin/plugin.json
# Change: "name": "dev-workflow" → "name": "super-dev"
# Change: "version": "1.0.0" → "version": "2.0.0"
# Update description
```

### Step 2: Rename Skill Directory
```bash
mv skills/dev-workflow skills/super-dev
```

### Step 3: Update SKILL.md
- Update title
- Replace all `dev-workflow:` with `super-dev:`
- Add Coordinator as entry point
- Add new executor agents
- Update workflow diagram

### Step 4: Update Command
- Update command name
- Update invocation to use Coordinator

### Step 5: Delete Old Agent
```bash
rm agents/execution-coordinator.md
```

### Step 6: Update Agent References
For each agent file:
- Search for `dev-workflow:`
- Replace with `super-dev:`

### Step 7: Update README
- Complete rewrite for new architecture
- Add Coordinator documentation
- Add parallel execution docs

### Step 8: Verify
- Check no "dev-workflow" remains
- Test skill invocation
- Test command invocation

## 3. Dependencies

- Sub-Specs 01, 02, 03, 04 (all agents must exist first)

## 4. Risk Mitigation

- Make changes in order (metadata → content)
- Commit after each major change
- Use search to verify no missed references

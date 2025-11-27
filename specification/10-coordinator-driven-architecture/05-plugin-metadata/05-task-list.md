# Task List: Plugin Metadata Update

**Total Tasks:** 8

## Tasks

- [ ] **T5.1** Update plugin.json name to "super-dev"
  - Change name from "dev-workflow" to "super-dev"
  - Update version to "2.0.0"
  - Update description for new architecture

- [ ] **T5.2** Rename skills/dev-workflow to skills/super-dev
  - Rename directory
  - Verify SKILL.md exists in new location

- [ ] **T5.3** Update SKILL.md content for new architecture
  - Update title to "Super Dev Workflow"
  - Add Coordinator Agent as entry point
  - Add executor agents to workflow
  - Update all agent references
  - Add parallel execution documentation

- [ ] **T5.4** Update fix-impl.md command
  - Update command name reference
  - Update invocation to use Coordinator
  - Update examples

- [ ] **T5.5** Remove old execution-coordinator.md
  - Delete `agents/execution-coordinator.md`
  - Verify new agents exist as replacement

- [ ] **T5.6** Update all agent references
  - Search all agent files for "dev-workflow:"
  - Replace with "super-dev:"
  - Verify no missed references

- [ ] **T5.7** Update README.md
  - Update title and overview
  - Update installation instructions
  - Update architecture diagram
  - Add Coordinator documentation
  - Add parallel execution docs
  - Update all examples

- [ ] **T5.8** Verify all references correct
  - Search for any remaining "dev-workflow"
  - Test skill invocation (if possible)
  - Verify no broken links
  - Final review

## Checkpoint

After T5.8:
```bash
git add -A  # All changes in this phase
git commit -m "feat(super-dev): Complete plugin rename and integration

BREAKING CHANGE: Plugin renamed from dev-workflow to super-dev
- All agent references updated
- Coordinator-driven architecture implemented
- Parallel execution in execution phase
- execution-coordinator.md removed, replaced by:
  - coordinator.md
  - dev-executor.md
  - qa-executor.md
  - docs-executor.md"
```

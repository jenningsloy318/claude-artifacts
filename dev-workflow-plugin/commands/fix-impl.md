---
name: fix-impl
description: Execute the complete development workflow for implementing features or fixing bugs
---

# Development Workflow Command

This command orchestrates the complete development workflow.

## Usage

```
/fix-impl [description of task]
```

## What This Command Does

When invoked, this command activates the `dev-workflow:dev-workflow` skill which guides through all 11 phases:

1. **Specification Setup** - Find or create spec directory
2. **Requirements Clarification** - Gather complete requirements
3. **Research** - Find best practices and documentation
4. **Debug Analysis** - Root cause analysis (bugs only)
5. **Code Assessment** - Evaluate existing codebase
6. **Specification Writing** - Create tech spec, plan, tasks
7. **Specification Review** - Validate all documents
8. **Execution** - Implement with parallel agents
9. **Coordination** - Sequential task completion
10. **Cleanup** - Remove temporary files
11. **Commit & Push** - Save changes to repository

## Instructions

When this command is invoked:

1. **Activate main skill**: Use `dev-workflow:dev-workflow` skill
2. **Apply dev rules**: Use `dev-workflow:dev-rules` throughout
3. **Follow phases sequentially** unless user indicates to skip
4. **Use sub-skills** for each phase as documented
5. **Track progress** with TodoWrite tool

## Arguments

`$ARGUMENTS` contains the user's description of what needs to be done:
- Bug description
- Feature request
- Refactoring goal
- Performance issue

## Example Invocations

```
/fix-impl Fix the login button not responding on mobile
/fix-impl Implement user profile page with avatar upload
/fix-impl Refactor the authentication module for better testability
/fix-impl Improve API response time for product listing
```

## Notes

- This workflow is comprehensive - for quick fixes, user may request to skip phases
- All documents are created in `specification/[index]-[name]/` directory
- Final step always includes commit and push

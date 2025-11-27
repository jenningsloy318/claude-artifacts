---
name: super-dev:fix-impl
description: Execute the complete coordinator-driven development workflow for implementing features or fixing bugs
---

# Super Dev Workflow Command

This command orchestrates the complete coordinator-driven development workflow.

## Usage

```
/super-dev:fix-impl [description of task]
```

## What This Command Does

When invoked, this command activates the `super-dev:coordinator` agent which orchestrates all 12 phases:

1. **Phase 0: Apply Dev Rules** - Establish coding standards
2. **Phase 1: Specification Setup** - Find or create spec directory
3. **Phase 2: Requirements Clarification** - Gather complete requirements
4. **Phase 3: Research** - Find best practices with Time MCP
5. **Phase 4: Debug Analysis** - Root cause analysis (bugs only, uses grep/ast-grep)
6. **Phase 5: Code Assessment** - Evaluate existing codebase (uses grep/ast-grep)
7. **Phase 5.3: Architecture Design** - For complex features (optional)
8. **Phase 5.5: UI/UX Design** - For features with UI (optional)
9. **Phase 6: Specification Writing** - Create tech spec, plan, tasks
10. **Phase 7: Specification Review** - Validate all documents
11. **Phase 8-9: Execution** - PARALLEL agents (dev + qa + docs)
12. **Phase 9.5: Quality Assurance** - Modality-specific testing
13. **Phase 10-11: Cleanup & Commit** - Remove temp files, commit changes
14. **Phase 12: Final Verification** - Coordinator verifies all complete

## Instructions

When this command is invoked:

1. **Invoke Coordinator**: Use `super-dev:coordinator` agent
2. **Apply dev rules**: Coordinator applies `super-dev:dev-rules` at Phase 0
3. **Coordinator orchestrates** all phases automatically
4. **Parallel execution** during Phases 8-9 (dev, qa, docs agents)
5. **Track progress** with TodoWrite tool

## Arguments

`$ARGUMENTS` contains the user's description of what needs to be done:
- Bug description
- Feature request
- Refactoring goal
- Performance issue

## Example Invocations

```
/super-dev:fix-impl Fix the login button not responding on mobile
/super-dev:fix-impl Implement user profile page with avatar upload
/super-dev:fix-impl Refactor the authentication module for better testability
/super-dev:fix-impl Improve API response time for product listing
```

## Notes

- The Coordinator Agent is the central authority that orchestrates ALL phases
- Parallel execution (dev + qa + docs) maximizes efficiency
- Build queue policy: For Rust/Go, only ONE build at a time
- All documents are created in `specification/[index]-[name]/` directory
- Final verification ensures no missing code or documents

---
name: super-dev:update-documentation
description: Update documentation sequentially after code review and approval
---

# Phase 10: Documentation Update

Update all documentation sequentially after successful code review and implementation.

## Usage

```
/super-dev:phase-10 [specification directory path]
```

## What This Command Does

When invoked, this command activates the `super-dev:docs-executor` to:

1. **Updates task list**: Marks completed tasks and documents outcomes
2. **Updates implementation summary**: Records technical decisions and challenges
3. **Updates specifications**: Documents deviations from original specs
4. **Creates user documentation**: Generates user-facing documentation
5. **Creates developer documentation**: Documents API and integration details
6. **Ensures consistency**: Verifies all documentation is aligned

## Documentation Updates

### 1. Task List (`[index]-task-list.md`)
- Mark completed tasks with `[x]`
- Add any new tasks discovered during implementation
- Update task status and progress
- Note any blocked or deferred tasks

### 2. Implementation Summary (`[index]-implementation-summary.md`)
- Add completed work to "Code Changes" section
- Document technical decisions made
- Record challenges and solutions
- Note any deviations from plan
- Update status at milestone boundaries

### 3. Specification (`[index]-specification.md`)
- Update sections with `[UPDATED: YYYY-MM-DD]` marker
- Document implementation differences
- Explain why changes were necessary
- Keep spec aligned with actual implementation

### 4. User Documentation
- README updates
- Usage examples
- Configuration guides
- Troubleshooting sections

### 5. Developer Documentation
- API documentation
- Integration guides
- Development setup instructions
- Contribution guidelines

## Quality Gates

Before completing this phase, ensure:
- [ ] All implemented features are documented
- [ ] Task list reflects actual completion state
- [ ] Implementation summary is current
- [ ] Specification changes are documented
- [ ] User documentation is clear and accurate
- [ ] Developer documentation is complete

## Arguments

`$ARGUMENTS` should specify:
- Path to specification directory
- Type of documentation to focus on (optional)
- Any special documentation requirements

## Output

Updates/creates:
- Updated `[index]-task-list.md`
- Updated `[index]-implementation-summary.md`
- Updated `[index]-specification.md`
- User documentation files
- Developer documentation files

## Examples

```
/super-dev:phase-10 specification/12-user-authentication
/super-dev:phase-10 ./specs/payment-processing --focus user-docs
```

## Notes

- Critical for maintaining project knowledge
- Enables future maintenance and development
- Ensures documentation matches implementation
- Must be completed before final commit
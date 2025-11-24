---
name: execution-coordinator
description: Coordinate parallel development, testing, and documentation agents during implementation. Use in Phase 8-9 of dev-workflow for executing the implementation plan.
---

# Execution Coordinator

Orchestrate parallel agents for efficient implementation.

**Announce:** "I'm using the execution-coordinator skill to implement the plan with parallel agents."

## Critical Rules

**DO NOT pause or stop during execution phase.**

If multiple implementation options exist:
- Choose the option that continues implementation
- Only stop if not feasible or a clearly better solution exists

## Agent Structure

### Development Agent

**Responsibilities:**
- Generate code following established patterns
- Apply linting and formatting
- Build after each code generation
- Document implementation choices
- Use latest libraries and tools
- Fix all warnings/errors (never suppress)
- Organize code in modular, loosely-coupled components
- Maintain consistent data schemas

**Tools:**
- `ast-grep` skill for code pattern location
- Project-specific build commands
- Linting and formatting tools

**Specialist Agents:**
- `rust-pro` - Rust development
- `backend-developer` - Backend services
- `frontend-developer` - UI components
- `mobile-developer` - Mobile apps
- Language-specific specialists as needed

### Testing Agent

**Responsibilities:**
- Validate builds run without errors
- Execute CodeRabbit analysis: `coderabbit --prompt-only` (background)
- Write and run unit tests
- Write and run integration tests
- Document edge cases
- Track test coverage

**For Web Projects:**
- Use `playwright` MCP tools
- Use `chrome-devtools` MCP tools
- Exercise inputs, buttons, navigation
- Do NOT invoke npm or playwright directly

**Specialist Agents:**
- `superpowers:code-reviewer` - Code review
- `superpowers:test-driven-development` - TDD approach

### Documentation Agent

**Responsibilities:**
- Track implementation progress
- Create implementation summary
- Document technical decisions
- Record challenges and solutions
- Note performance metrics

**Specialist Agents:**
- `documentation-expert` - Technical docs

## Execution Process

### 1. Task Assignment

```
For each task in task list:
  1. Assign to appropriate agent
  2. Wait for completion
  3. Verify output
  4. Update task status
  5. Move to next task
```

### 2. Parallel Coordination

Use `superpowers:subagent-driven-development` for:
- Running development and testing in parallel where possible
- Managing agent context
- Ensuring consistency

### 3. Progress Tracking

Use `TodoWrite` tool to:
- Create todos from task list
- Mark in_progress when starting
- Mark completed when done
- Track blockers

### 4. Build Verification

After each code change:
```
1. Run build
2. Check for errors
3. Check for warnings
4. Fix any issues
5. Re-verify
```

### 5. Test Execution

For each implemented feature:
```
1. Write unit tests
2. Run tests
3. Fix failures
4. Add integration tests
5. Verify coverage
```

## Implementation Summary

At completion, create:

**File:** `[index]-implementation-summary.md`

```markdown
# Implementation Summary: [Feature/Fix Name]

**Date:** [timestamp]
**Duration:** [time from start to finish]

## Technical Decisions

### Decision 1: [Title]
- **Context:** [Why this decision was needed]
- **Options considered:** [List options]
- **Choice:** [What was chosen]
- **Rationale:** [Why]

## Code Structure

### Files Created
- `path/to/file.ts` - [Purpose]

### Files Modified
- `path/to/file.ts` - [What changed]

### Files Deleted
- `path/to/file.ts` - [Why removed]

## Challenges and Solutions

### Challenge 1: [Description]
- **Problem:** [Details]
- **Solution:** [How it was solved]
- **Lessons:** [What we learned]

## Test Coverage

| Area | Tests | Coverage |
|------|-------|----------|
| [Area] | [count] | [%] |

## Performance

### Metrics
- Build time: [duration]
- Test time: [duration]
- Bundle size: [if applicable]

### Optimizations
[Any optimizations made]

## Known Issues

[Any known issues or limitations]

## Future Improvements

[Suggested future work]
```

## Error Handling

### Build Failures
1. Read error message carefully
2. Locate the issue
3. Fix and rebuild
4. If stuck after 3 attempts: document and ask

### Test Failures
1. Analyze failure reason
2. Check if test or code is wrong
3. Fix appropriately
4. Re-run tests

### Blocking Issues
Only request user confirmation for:
- Significant architectural changes
- Ambiguous requirements
- External dependency issues
- Permission problems

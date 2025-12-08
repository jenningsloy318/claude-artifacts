---
name: super-dev:debug-analysis
description: Perform systematic root cause analysis for bugs and errors
---

# Phase 4: Debug Analysis

Execute systematic root cause analysis with evidence collection and reproducible steps.

## Usage

```
/super-dev:phase-4 [bug description or error details]
```

## What This Command Does

When invoked, this command activates the `super-dev:debug-analyzer` to:

1. **Collects evidence**: Gathers all relevant error information
2. **Analyzes patterns**: Searches codebase for related issues
3. **Identifies root causes**: Finds the underlying problem
4. **Creates reproduction steps**: Documents how to reproduce the issue
5. **Proposes solutions**: Recommends specific fixes
6. **Documents findings**: Creates `[index]-debug-analysis.md`

## Analysis Process

### Evidence Collection
- Parse error messages and stack traces
- Identify affected components
- Note environmental factors
- Collect logs and output

### Pattern Search (grep/ast-grep Enhanced)
- Search for similar error patterns
- Find related code sections
- Identify recent changes
- Track error frequency

### Root Cause Analysis
- Trace through execution flow
- Identify failure points
- Analyze data flow
- Check edge cases

### Reproduction Steps
- Document exact steps to reproduce
- Note required conditions
- Identify variable factors
- Create test scenarios

## Arguments

`$ARGUMENTS` should contain:
- Error messages or stack traces
- Description of unexpected behavior
- Steps already attempted
- Context about when the issue occurs

## Output

Creates `[index]-debug-analysis.md` with:
- Summary of the issue
- Evidence collected
- Root cause analysis
- Reproduction steps
- Proposed solutions
- Related findings

## Examples

```
/super-dev:phase-4 TypeError: Cannot read property 'user' of undefined
/super-dev:phase-4 Memory usage grows continuously with large files
/super-dev:phase-4 Build fails on production but not development
```

## Tools Used

- **grep**: Text pattern search
- **ast-grep**: Structural AST-based code search
- **Task tool**: For exploring codebase patterns

## Notes

- Only used for bugs and errors (skip for new features)
- Requires clear error description or logs
- Produces actionable fix recommendations
- Documents findings for future reference
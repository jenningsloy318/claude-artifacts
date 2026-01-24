---
name: debugging-patterns
description: Systematic debugging methodology, evidence collection, root cause analysis, and bug investigation techniques. Reference for Phase 4 (Debug Analysis) in super-dev workflow.
---

# Debugging Patterns Reference

Reference documentation for systematic root cause analysis and bug investigation. Use this during Phase 4 (Debug Analysis) of the super-dev workflow.

## Core Principles

### First Principles Analysis
Break down bugs to fundamental truths—what actually happens vs. what should happen—then build understanding from there.

### Evidence-Based Reasoning
Form hypotheses from concrete evidence, not assumptions; verify each with supporting/contradicting data.

### Systematic Investigation
Follow structured process—gather evidence, reproduce, trace execution, verify root cause—never skip steps.

### Minimal Reproduction
Reduce complex issues to minimal reproducible cases for faster root cause identification.

## Debug Process

### Step 1: Gather Evidence

Collect all available information before forming hypotheses.

**Error Information:**
- [ ] Error messages (exact text)
- [ ] Stack traces
- [ ] Error codes

**Logs:**
- [ ] Console logs
- [ ] Build logs
- [ ] Runtime logs
- [ ] Debug logs

**Visual Evidence:**
- [ ] Screenshots
- [ ] Screen recordings
- [ ] Network request/response data

**Context:**
- [ ] When did it start?
- [ ] Recent code changes
- [ ] Environment details

### Step 2: Reproduce the Issue

Verify the issue can be reproduced consistently.

1. Follow provided reproduction steps
2. Verify issue occurs consistently
3. Note any variations in behavior
4. Identify minimal reproduction case
5. Document exact conditions

**If cannot reproduce:**
- Request more information
- Try different environments
- Check for race conditions

### Step 3: Codebase Analysis

**Locate Relevant Code:**

Use code search tools to find:
- Error message strings in code
- Function definitions mentioned in stack trace
- Related class/module structures
- Import statements and dependencies

**Trace Execution Path:**

```
Entry Point
    ↓
Function A (line X)
    ↓
Function B (line Y) ← Error occurs here
    ↓
Expected: [behavior]
Actual: [behavior]
```

Document:
- Entry point to error location
- Data transformations along the path
- Conditional branches taken
- Error handling (or lack thereof)

### Step 4: Root Cause Analysis

**Hypothesis Formation:**

Form 2-3 hypotheses ranked by likelihood:

| Hypothesis | Likelihood | Supporting Evidence | Contradicting Evidence |
|------------|------------|---------------------|------------------------|
| [H1] | High/Med/Low | [evidence] | [evidence] |
| [H2] | High/Med/Low | [evidence] | [evidence] |

**Verification Process:**

For each hypothesis:
1. What evidence supports it?
2. What evidence contradicts it?
3. How can we verify it?
4. What would we expect to see if true?

**Confirm Root Cause:**

The root cause is confirmed when:
- Evidence strongly supports the hypothesis
- No contradicting evidence exists
- The fix can be logically derived

### Step 5: Document Findings

Every debug analysis must document:
- [ ] All available evidence
- [ ] Reproducible steps (rate + minimal repro)
- [ ] Code execution path with line numbers
- [ ] Multiple hypotheses considered
- [ ] Verified root cause with evidence
- [ ] Actionable fix and test plan
- [ ] Related issues and prevention steps

## Code Search Strategy

### Text Pattern Search (Grep)

Use Grep tool to find relevant code:

```bash
# Search for error message
Grep(
  pattern: "[exact error text]",
  path: "src/",
  output_mode: "content"
)
```

**Debug-Specific Patterns:**

| Purpose | Pattern | Notes |
|---------|---------|-------|
| Error message in code | `"[exact error text]"` | Find where error is thrown |
| Function from stack trace | `fn\\s+function_name\|function\\s+function_name` | Locate function |
| Error types | `Error\|Exception\|panic\|unwrap` | Find error handling |
| Logging statements | `log\\.\\w+\|console\\.\\w+\|print` | Find debug output |
| Config values | `env\\.\|config\\.` | Check configuration |
| State mutations | `setState\|set_\|mut\\s+` | Find state changes |

### Structural Analysis (ast-grep)

For complex code patterns, use ast-grep:

```
Skill(skill: "ast-grep")
```

**Debug Use Cases:**

| Purpose | Description |
|---------|-------------|
| Call hierarchy | Find all callers of a function |
| Error propagation | Trace error handling through call chain |
| State mutations | Find all places state is modified |
| Null checks | Find missing null/undefined checks |
| Async patterns | Find async/await usage patterns |

### Coverage for Debugging Scope

**CRITICAL:** Ensure all files in the bug's scope are searched.

```
# Step 1: Identify scope from stack trace
affected_files = [files mentioned in stack trace]
related_files = [files that import/use affected files]

# Step 2: Search all relevant files
Glob(pattern: "**/*", path: "[relevant directory]")

# Step 3: Track what was searched
| File | Searched | Relevant | Notes |
|------|----------|----------|-------|
| [file] | Yes/No | Yes/No | [notes] |

# Step 4: Report coverage
- Files in stack trace: [X] searched
- Related files: [Y] searched
- Total coverage: [%]
```

## Common Bug Patterns

### Null/Undefined Reference

**Symptoms:**
- `TypeError: Cannot read property 'X' of undefined`
- `NullPointerException`
- Variable accessed before initialization

**Debug Steps:**
1. Check variable initialization
2. Verify optional chaining usage
3. Trace object construction
4. Check API response structure

### Race Conditions

**Symptoms:**
- Intermittent failures
- Different results each run
- Timing-dependent issues

**Debug Steps:**
1. Add logging at critical points
2. Reproduce with controlled timing
3. Check shared state access
4. Verify synchronization mechanisms

### Off-by-One Errors

**Symptoms:**
- Index out of bounds
- Loop runs one too many/few times

**Debug Steps:**
1. Check loop conditions
2. Verify array indexing (0-based vs 1-based)
3. Trace iteration counts

### Type Errors

**Symptoms:**
- Type mismatch errors
- Implicit any errors

**Debug Steps:**
1. Check type annotations
2. Verify type assertions
3. Trace type conversions

## Debug Output Format

```markdown
# Debug Analysis: [Issue Description]

**Date:** [timestamp]
**Severity:** Critical/High/Medium/Low
**Status:** Analyzing/Root Cause Found/Blocked

## Issue Summary
[Brief description of the bug]

## Evidence Collected

### Error Messages
```
[Exact error text]
```

### Stack Trace
```
[Relevant stack trace]
```

### Logs
```
[Relevant log entries]
```

## Environment
- Platform: [desktop/mobile/server]
- OS: [name and version]
- Browser: [if applicable]
- Version: [app version]

## Reproduction

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Reproduction Rate
[Always/Sometimes/Rarely] - [X/Y attempts]

### Minimal Reproduction
[Simplest way to trigger the bug]

## Code Analysis

### Affected Files
| File | Lines | Description |
|------|-------|-------------|
| `path/to/file.ts` | 100-150 | [description] |

### Execution Path
```
[Entry] → [Function A] → [Function B] → [ERROR]
```

### Key Code Sections
```typescript:src/file.ts:100-110
[relevant code snippet]
```

## Root Cause Analysis

### Hypotheses Considered

#### Hypothesis 1: [Name]
- **Description:** [what might be wrong]
- **Likelihood:** High/Medium/Low
- **Supporting Evidence:**
  - [evidence 1]
  - [evidence 2]
- **Contradicting Evidence:**
  - [evidence if any]
- **Verification:** [how to verify]

### Confirmed Root Cause
**[Clear statement of the root cause]**

**Explanation:**
[Detailed explanation of why the bug occurs]

**Evidence:**
[Evidence that confirms this root cause]

## Recommended Fix

### Approach
[High-level description of the fix]

### Implementation
```typescript
// Suggested fix
[code snippet]
```

### Testing
[How to verify the fix works]

## Related Issues

### Technical Debt
[Related code quality issues discovered]

### Similar Bugs
[Other bugs that might have same root cause]

### Prevention
[How to prevent similar bugs in future]
```

## Debugging Best Practices

### DO's
- Start with evidence, not assumptions
- Reproduce the bug before fixing
- Use minimal reproduction cases
- Form multiple hypotheses
- Verify fixes with tests
- Document findings for future reference

### DON'Ts
- Skip reproduction steps
- Fix symptoms without finding root cause
- Make assumptions without evidence
- Change multiple things at once
- Ignore intermittent bugs
- Fix without adding tests

## Debugging Tools

### Logging Strategies
- **Structured logging**: Use consistent log formats
- **Log levels**: DEBUG, INFO, WARN, ERROR
- **Context**: Include relevant variables and state
- **Performance**: Avoid logging in hot loops

### Breakpoint Strategies
- **Line breakpoints**: Pause at specific line
- **Conditional breakpoints**: Pause when condition is met
- **Exception breakpoints**: Pause when exception thrown
- **Watchpoints**: Pause when variable is modified

## Reference

This is a reference document extracted from the `super-dev:debug-analyzer` agent. For full agent behavior during Phase 4, invoke:

```
Task(subagent_type: "super-dev:debug-analyzer", prompt: "Debug: [bug details]")
```

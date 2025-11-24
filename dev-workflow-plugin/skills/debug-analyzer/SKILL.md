---
name: debug-analyzer
description: Analyze bugs and errors to find root cause. Use in Phase 4 of dev-workflow for bug fixes only. Combines codebase analysis with systematic debugging.
---

# Debug Analyzer

Systematic root cause analysis for bugs and errors.

**Announce:** "I'm using the debug-analyzer skill to identify the root cause."

## When to Use

Only for bug fixes, errors, or unexpected behavior - skip this phase for new features.

## Debug Process

### 1. Gather Evidence

Collect all available information:
- [ ] Error messages (exact text)
- [ ] Stack traces
- [ ] Console logs
- [ ] Build logs
- [ ] Network requests/responses
- [ ] Screenshots

### 2. Reproduce the Issue

- [ ] Follow reproduction steps
- [ ] Verify the issue occurs consistently
- [ ] Note any variations in behavior
- [ ] Identify minimal reproduction case

### 3. Codebase Analysis

Using research findings from Phase 3:

#### Locate Relevant Code
Use `ast-grep` skill to find:
- Error-related code patterns
- Function definitions
- Class structures
- Import statements

#### Trace Execution Path
- Follow the code path from entry point
- Identify where the error occurs
- Check data transformations
- Review error handling

### 4. Root Cause Analysis

Apply systematic debugging:

#### Hypothesis Formation
1. Form initial hypothesis based on evidence
2. List 2-3 possible root causes
3. Rank by likelihood

#### Verification
For each hypothesis:
- What evidence supports it?
- What evidence contradicts it?
- How can we verify it?

### 5. Tools & Agents

| Tool/Agent | Purpose |
|------------|---------|
| `ast-grep` skill | Code pattern search |
| `debugging-toolkit:debugger` | Systematic debugging |
| `superpowers:systematic-debugging` | Debugging methodology |
| `superpowers:root-cause-tracing` | Trace bugs backward |

### 6. Document Findings

## Output

Create debug analysis in spec directory:

**File:** `[index]-debug-analysis.md`

**Structure:**
```markdown
# Debug Analysis: [Issue Description]

**Date:** [timestamp]
**Severity:** [Critical/High/Medium/Low]

## Issue Summary
[Brief description of the bug]

## Evidence Collected
- Error messages: [exact text]
- Stack trace: [relevant parts]
- Logs: [relevant entries]

## Reproduction Steps
1. [Step 1]
2. [Step 2]
...

## Code Analysis

### Affected Files
- `path/to/file1.ts` - [description]
- `path/to/file2.ts` - [description]

### Execution Path
[Trace of code execution leading to error]

## Root Cause Analysis

### Hypotheses Considered
1. [Hypothesis 1] - [Likelihood: High/Medium/Low]
2. [Hypothesis 2] - [Likelihood: High/Medium/Low]

### Confirmed Root Cause
[Detailed explanation of the actual root cause]

### Evidence
[Evidence supporting this conclusion]

## Recommended Fix
[High-level description of the fix]

## Related Issues
[Any related bugs or technical debt]
```

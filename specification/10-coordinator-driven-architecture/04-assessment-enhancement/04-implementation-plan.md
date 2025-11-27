# Implementation Plan: Assessment Enhancement

**Date:** 2025-11-27
**Parent:** [../00-master-implementation-plan.md]

## 1. Files to Modify

1. `agents/code-assessor.md`
2. `agents/debug-analyzer.md`

## 2. Modifications per File

### code-assessor.md

**Add Sections:**
1. "Search Strategy" - Grep patterns for code analysis
2. "Structural Analysis" - ast-grep skill usage
3. "File Coverage" - Tracking and reporting

**Location:** After existing "Evaluation Areas" section

### debug-analyzer.md

**Add Sections:**
1. "Code Search" - Grep patterns for debugging
2. "Structural Analysis" - ast-grep for pattern finding
3. "Coverage" - Ensure all relevant files searched

**Location:** After existing "Evidence Collection" section

## 3. Implementation Order

1. Update code-assessor.md (more comprehensive changes)
2. Update debug-analyzer.md (similar pattern)

## 4. Dependencies

- Sub-Spec 01 (Coordinator Agent)
- ast-grep skill must be available in user's environment

## 5. Validation

After modifications:
1. Grep tool usage documented
2. ast-grep skill invocation documented
3. File coverage tracking defined
4. Pattern examples clear
5. No syntax errors in markdown

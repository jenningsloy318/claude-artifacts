# Specification: Assessment Enhancement

**Date:** 2025-11-27
**Author:** Claude
**Status:** Draft
**Parent:** [../00-master-specification.md]

## 1. Overview

Enhance code-assessor and debug-analyzer agents to use grep and ast-grep skills for comprehensive code analysis, ensuring all relevant files are covered.

## 2. Current State

The existing agents:
- Use basic file reading and search
- Do NOT explicitly use grep skill
- Do NOT use ast-grep skill
- Do NOT track file coverage

## 3. Enhancement Requirements

### 3.1 Grep Skill Integration

**Add to code-assessor and debug-analyzer:**

```markdown
## Search Strategy

### Text Pattern Search (Grep)
Use Grep tool for text pattern matching:

```
Grep(
  pattern: "function\\s+\\w+",
  path: "src/",
  output_mode: "files_with_matches"
)
```

**Use Cases:**
- Find function definitions
- Search for error patterns
- Locate configuration values
- Find import statements
- Search for TODO/FIXME comments
```

### 3.2 ast-grep Skill Integration

**Add structural code analysis:**

```markdown
## Structural Analysis (ast-grep)

### Invoke ast-grep Skill
For structural code search:

```
Skill(skill: "ast-grep")
```

**Use Cases:**
- Find class/struct definitions
- Locate function signatures with specific patterns
- Identify design patterns (singleton, factory, etc.)
- Find async/await patterns
- Locate type definitions
```

### 3.3 File Coverage Tracking

**Ensure comprehensive analysis:**

```markdown
## File Coverage

### Enumerate Source Files
First, enumerate all relevant files:

```
Glob(pattern: "**/*.{ts,tsx,js,jsx}", path: "src/")
Glob(pattern: "**/*.rs", path: "src/")
Glob(pattern: "**/*.go", path: ".")
```

### Track Analysis Coverage
Maintain coverage tracking:

| File Type | Total | Analyzed | Coverage |
|-----------|-------|----------|----------|
| TypeScript | 50 | 50 | 100% |
| Rust | 20 | 20 | 100% |
| Go | 15 | 15 | 100% |

### Report Gaps
If any files not analyzed:
- List unanalyzed files
- Explain why (binary, generated, etc.)
- Ensure intentional exclusions only
```

## 4. Files to Modify

### 4.1 code-assessor.md

**Path:** `agents/code-assessor.md`

**Sections to Add:**
1. "Search Strategy" section with Grep patterns
2. "Structural Analysis" section with ast-grep
3. "File Coverage" section with tracking

### 4.2 debug-analyzer.md

**Path:** `agents/debug-analyzer.md`

**Sections to Add:**
1. "Code Search" section with Grep patterns
2. "Structural Analysis" section with ast-grep
3. "Coverage" section for debugging scope

## 5. Search Pattern Examples

### 5.1 Grep Patterns

| Purpose | Pattern | Options |
|---------|---------|---------|
| Function defs | `function\s+\w+` | glob: "*.js" |
| Class defs | `class\s+\w+` | glob: "*.ts" |
| Imports | `^import\s+` | output_mode: "content" |
| Errors | `throw\|Error\|panic` | type: "rust" |
| Config | `process\.env\.\w+` | - |

### 5.2 ast-grep Rules

| Purpose | Rule Description |
|---------|------------------|
| React components | Function components with JSX return |
| Async functions | Functions with async keyword |
| Error handlers | try/catch blocks |
| State mutations | useState/useReducer calls |

## 6. Acceptance Criteria

- [ ] Grep skill usage documented in code-assessor
- [ ] Grep skill usage documented in debug-analyzer
- [ ] ast-grep skill invocation documented
- [ ] File coverage tracking defined
- [ ] Search pattern examples provided
- [ ] Coverage reporting format defined

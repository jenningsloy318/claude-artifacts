---
name: code-assessor
description: Assess current codebase architecture, code style, and frameworks. Use in Phase 5 of dev-workflow to evaluate existing code before making changes.
---

# Code Assessor

Evaluate current codebase to ensure changes align with existing patterns.

**Announce:** "I'm using the code-assessor skill to assess the current codebase."

## Assessment Areas

### 1. Architecture Evaluation

Compare current architecture to best practices:

- [ ] **Overall structure**: Is it well-organized?
- [ ] **Separation of concerns**: Are responsibilities properly divided?
- [ ] **Module boundaries**: Are modules loosely coupled?
- [ ] **Data flow**: Is data flow clear and predictable?
- [ ] **Error handling**: Is it consistent and comprehensive?

Questions to answer:
- Does current architecture support the new changes?
- Are there architectural patterns we should follow?
- Any architectural debt that needs addressing?

### 2. Code Standards

Check rules and formatting:

- [ ] **Linting rules**: What linter is configured?
- [ ] **Formatting**: What formatter is used (Prettier, etc.)?
- [ ] **Naming conventions**: camelCase, snake_case, etc.
- [ ] **File organization**: How are files structured?
- [ ] **Import ordering**: Any conventions?

### 3. Dependencies

Review packages and frameworks:

- [ ] **Package versions**: Are they up to date?
- [ ] **Deprecated packages**: Any that need replacing?
- [ ] **Security vulnerabilities**: Any known issues?
- [ ] **Bundle size**: Any bloated dependencies?

### 4. Framework Patterns

Identify framework-specific patterns:

- [ ] **State management**: How is state handled?
- [ ] **Routing**: What patterns are used?
- [ ] **API integration**: How are APIs called?
- [ ] **Component structure**: How are components organized?
- [ ] **Testing patterns**: How are tests structured?

### 5. Better Options Analysis

Identify potential improvements:

- Are there better libraries available?
- Are there simpler approaches?
- Can we reduce complexity?
- What technical debt exists?

## Assessment Tools

| Tool | Purpose |
|------|---------|
| `Glob` | Find file patterns |
| `Grep` | Search code patterns |
| `Read` | Examine specific files |
| `ast-grep` skill | Structural code search |

### Files to Examine

- `package.json` / `Cargo.toml` / `go.mod` - Dependencies
- `.eslintrc` / `.prettierrc` - Linting/formatting
- `tsconfig.json` - TypeScript config
- Config files - Project configuration
- Test files - Testing patterns

## Output

Create assessment in spec directory:

**File:** `[index]-assessment.md`

**Structure:**
```markdown
# Code Assessment: [Project/Feature Area]

**Date:** [timestamp]
**Scope:** [What was assessed]

## Architecture

### Current State
[Description of current architecture]

### Comparison to Best Practices
| Aspect | Current | Best Practice | Gap |
|--------|---------|---------------|-----|
| [Aspect] | [Current] | [Best] | [Gap] |

### Recommendations
[Architectural recommendations]

## Code Standards

### Current Standards
- Linter: [name and version]
- Formatter: [name and config]
- Conventions: [list]

### Compliance
[How well code follows standards]

## Dependencies

### Current Dependencies
| Package | Current | Latest | Status |
|---------|---------|--------|--------|
| [pkg] | [ver] | [latest] | [OK/Update/Replace] |

### Security Issues
[Any vulnerabilities found]

### Recommendations
[Dependency recommendations]

## Framework Patterns

### Identified Patterns
[List of patterns found]

### Patterns to Follow
[Patterns new code should follow]

## Better Options

### Potential Improvements
[List of possible improvements]

### Technical Debt
[Identified technical debt]

## Summary

### Must Follow
[Critical patterns/standards to follow]

### Should Consider
[Recommended improvements]

### Future Work
[Items for future consideration]
```

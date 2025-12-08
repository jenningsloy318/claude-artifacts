---
name: super-dev:code-review
description: Perform specification-aware code review focused on correctness, security, performance, and maintainability
---

# Phase 9: Code Review

Perform specification-aware code review focused on correctness, security, performance, and maintainability.

## Usage

```
/super-dev:code-review [code changes context]
```

## What This Command Does

When invoked, this command activates the `super-dev:code-reviewer` agent to:

1. **Reviews code against specification**: Ensures implementation matches requirements
2. **Assesses correctness**: Verifies logic is sound and bug-free
3. **Security analysis**: Identifies potential vulnerabilities
4. **Performance evaluation**: Checks for performance bottlenecks
5. **Maintainability check**: Ensures code follows best practices
6. **Generates review report**: Provides actionable feedback

## Review Focus Areas

### Correctness
- Logic implementation matches specifications
- Edge cases are handled properly
- Error handling is comprehensive
- Data flow is correct

### Security
- No hardcoded secrets or API keys
- Proper input validation
- Authentication/authorization checks
- SQL injection and XSS prevention

### Performance
- Efficient algorithms and data structures
- No unnecessary database queries
- Proper caching strategies
- Resource usage optimization

### Maintainability
- Code follows project patterns
- Clear and readable code structure
- Adequate comments and documentation
- Modular and reusable components

## Arguments

`$ARGUMENTS` should include:
- Context of changes made
- Specification references
- Any specific areas of concern

## Output

Creates a review report with:
- Overall verdict (Approved, Needs Changes, Blocked)
- Findings categorized by severity (Critical, High, Medium, Low)
- Specific line references and suggestions
- Acceptance criteria status

## Examples

```
/super-dev:code-review Authentication system implementation
/super-dev:code-review Payment processing module changes
```

## Notes

- Specification-aware review using requirements and design docs
- Iterative: Loop back to execution if blocking issues found
- Only proceed when approved or low-impact issues remain
- Ensures code quality before final documentation
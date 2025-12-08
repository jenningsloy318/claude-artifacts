---
name: super-dev:code-assessment
description: Assess existing codebase for architecture, standards, and framework patterns
---

# Phase 5: Code Assessment

Execute comprehensive assessment of existing code architecture, standards compliance, and framework patterns.

## Usage

```
/super-dev:phase-5 [feature/area to assess]
```

## What This Command Does

When invoked, this command activates the `super-dev:code-assessor` to:

1. **Analyzes architecture**: Evaluates codebase structure and patterns
2. **Checks standards compliance**: Verifies coding standards adherence
3. **Identifies frameworks**: Maps technologies and frameworks in use
4. **Finds integration points**: Locates where new code should integrate
5. **Assesses technical debt**: Identifies areas needing improvement
6. **Creates assessment report**: Documents findings and recommendations

## Assessment Areas (grep/ast-grep Enhanced)

### Architecture Analysis
- Module organization and dependencies
- Design patterns in use
- Code structure and separation of concerns
- Integration points and boundaries

### Standards Compliance
- Coding style consistency
- Naming conventions
- Error handling patterns
- Testing practices

### Framework Usage
- Identify frameworks and libraries
- Check version compatibility
- Analyze integration patterns
- Note custom configurations

### Technical Debt
- Code complexity hotspots
- Duplication and redundancy
- Outdated patterns
- Performance concerns

## Tools Used

- **grep**: Text-based pattern matching
- **ast-grep**: AST-based structural analysis
- **Glob**: File discovery and pattern matching
- **Task tool**: For exploring codebase structure

## Arguments

`$ARGUMENTS` contains:
- Feature or area to be implemented
- Specific concerns or focus areas
- Integration requirements

## Output

Creates `[index]-assessment.md` with:
- Architecture overview
- Standards compliance findings
- Framework inventory
- Integration recommendations
- Technical debt assessment
- Implementation guidance

## Examples

```
/super-dev:phase-5 User authentication system
/super-dev:phase-5 Payment processing module
/super-dev:phase-5 API endpoint for user data
```

## Notes

- Maps existing patterns before implementing changes
- Identifies reuse opportunities
- Ensures new code follows established conventions
- Provides specific guidance for implementation
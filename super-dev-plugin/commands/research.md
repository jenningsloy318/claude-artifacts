---
name: super-dev:research
description: Conduct comprehensive research on best practices, patterns, and documentation
---

# Phase 3: Research

Research best practices, documentation, and patterns with Time MCP integration for recency awareness.

## Usage

```
/super-dev:phase-3 [research topic]
```

## What This Command Does

When invoked, this command activates the `super-dev:research-agent` to:

1. **Gets current timestamp**: Uses Time MCP for year context
2. **Researches best practices**: Searches for established patterns
3. **Finds official documentation**: Locates API references and guides
4. **Analyzes community knowledge**: Gathers insights from blogs, tutorials
5. **Checks for deprecations**: Identifies outdated patterns
6. **Creates research report**: Documents findings with freshness scores

## Research Areas

### Best Practices & Design Patterns
- Established patterns for the feature/fix type
- Anti-patterns to avoid
- Recommended architectures
- Industry standards

### Official Documentation
- API references for libraries/frameworks
- Configuration options
- Language-specific guidelines

### Community Knowledge
- Blog posts and tutorials
- Stack Overflow discussions
- GitHub issues and discussions
- Conference talks and videos

### Performance & Edge Cases
- Performance benchmarks
- Known limitations
- Security considerations
- Edge cases to handle

## Time MCP Integration

- Gets current timestamp before research
- Adds year context to queries (e.g., "2024 2025")
- Filters results by recency
- Flags potentially outdated information
- Computes freshness scores for sources

## Arguments

`$ARGUMENTS` contains the topic or technology to research.

## Output

Creates `[index]-research-report.md` with:
- Summary of findings
- Deprecation warnings
- Best practices and anti-patterns
- Official documentation references
- Community insights
- Performance considerations
- Source freshness analysis

## Examples

```
/super-dev:phase-3 React hooks best practices
/super-dev:phase-3 Rust async programming patterns
/super-dev:phase-3 GraphQL schema design
```

## Notes

- All searches use HTTP connector scripts (not direct MCP calls)
- Emphasizes recent sources (last 6-12 months)
- Proactively flags deprecated patterns
- Provides actionable recommendations
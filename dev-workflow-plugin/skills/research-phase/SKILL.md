---
name: research-phase
description: Conduct comprehensive research on best practices, documentation, and patterns. Use in Phase 3 of dev-workflow before implementation begins.
---

# Research Phase

Gather knowledge and best practices before writing specifications.

**Announce:** "I'm using the research-phase skill to gather best practices and documentation."

## Research Process

### 1. Establish Context
- Get current timestamp from time MCP
- Note the technology stack from requirements
- Identify key topics to research

### 2. Research Areas

#### Best Practices & Design Patterns
- Search for established patterns for this type of feature/fix
- Look for anti-patterns to avoid
- Find recommended architectures

#### Official Documentation
- API references for libraries being used
- Framework documentation
- Language-specific guidelines

#### Community Knowledge
- Informative blog posts and tutorials
- Stack Overflow discussions
- GitHub issues and discussions
- Conference talks or videos

#### Performance & Edge Cases
- Performance benchmarks
- Known limitations
- Edge cases to handle
- Security considerations

### 3. Tools to Use

| Tool | Purpose |
|------|---------|
| `mcp__exa__web_search_exa` | General web search |
| `mcp__exa__get_code_context_exa` | Code examples and patterns |
| `mcp__context7__resolve-library-id` | Find library documentation |
| `mcp__context7__get-library-docs` | Get specific library docs |
| `mcp__deepwiki__ask_question` | Ask about GitHub repos |

### 4. Specialist Agents

Delegate research to:
- `search-specialist` - Deep information retrieval
- `research-analyst` - Synthesis and analysis

### 5. Version Awareness

**CRITICAL:** Always research for the LATEST versions:
- Check current year (from timestamp)
- Look for latest stable versions
- Note any breaking changes in recent versions
- Avoid outdated patterns/APIs

## Output

Create research report in spec directory:

**File:** `[index]-research-report.md`

**Structure:**
```markdown
# Research Report: [Topic]

**Date:** [timestamp]
**Technologies:** [list]

## Summary
[Key findings overview]

## Best Practices
[Documented patterns and recommendations]

## Official Documentation
[Links and key excerpts]

## Community Insights
[Blog posts, discussions, issues]

## Performance Considerations
[Benchmarks, limitations]

## Edge Cases
[Known issues, edge cases to handle]

## Recommendations
[Synthesized recommendations for implementation]

## Sources
[All sources used]
```

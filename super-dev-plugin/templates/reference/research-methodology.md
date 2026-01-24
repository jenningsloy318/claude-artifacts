---
name: research-methodology
description: Comprehensive research methodology for software development, including multi-source search, version awareness, option presentation, and synthesis techniques. Reference for Phase 3 (Research) in super-dev workflow.
---

# Research Methodology Reference

Reference documentation for systematic research before software implementation. Use this during Phase 3 (Research) of the super-dev workflow.

## Core Principles

### Multi-Source Research
Search across code, documentation, academic papers, and community resources to get comprehensive understanding.

### Pattern Extraction
Identify established patterns and anti-patterns from multiple sources.

### Version Awareness
Always research for the latest stable versions; avoid outdated information.

### Synthesis
Compile findings into actionable recommendations with clear options and trade-offs.

## Research Process

### Step 1: Establish Context

1. **Get current timestamp** - Use Time MCP for year context
2. **Note the technology stack** - From requirements document
3. **Identify key topics** - What needs research?
4. **Plan search queries** - WITH year context for recency

### Step 2: Research Areas

Cover these areas systematically:

**Best Practices & Design Patterns:**
- Established patterns for this type of feature/fix
- Anti-patterns to avoid
- Recommended architectures
- Industry standards

**Official Documentation:**
- API references for libraries being used
- Framework documentation
- Language-specific guidelines
- Configuration options

**Community Knowledge:**
- Informative blog posts and tutorials
- Stack Overflow discussions
- GitHub issues and discussions
- Conference talks or videos

**Performance & Edge Cases:**
- Performance benchmarks
- Known limitations
- Edge cases to handle
- Security considerations

### Step 3: Execute Searches

Use search-agent for all retrieval:

```
Task(
  prompt: "Search for [query]",
  context: { mode: "code" | "docs" | "academic" | "web" | "all" },
  subagent_type: "super-dev:search-agent"
)
```

**Search Modes:**
| Mode | Use For |
|------|---------|
| `code` | Implementation patterns, code examples |
| `docs` | Official documentation, API references |
| `academic` | Research papers, benchmarks |
| `web` | Blog posts, tutorials, discussions |
| `all` | Comprehensive research |

### Step 4: Version Awareness (CRITICAL)

**Always research for the LATEST versions:**
- Check current year
- Look for latest stable versions
- Note any breaking changes in recent versions
- Avoid outdated patterns/APIs
- Verify deprecation status

### Step 5: Synthesize Findings

Compile all findings into structured recommendations:
- Prioritize by relevance and authority
- Cross-reference multiple sources
- Identify consensus patterns
- Note disagreements or alternatives

## Search Tools

### Exa (Web & Code Search)
```bash
# Web search
${CLAUDE_PLUGIN_ROOT}/scripts/exa/exa_search.sh --query "[query]" --type auto --results 10

# Code context search
${CLAUDE_PLUGIN_ROOT}/scripts/exa/exa_code.sh --query "[query]" --tokens 5000
```

### DeepWiki (GitHub Repo Documentation)
```bash
# Get repo docs structure
${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki/deepwiki_structure.sh --repo "[owner/repo]"

# Get repo docs contents
${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki/deepwiki_contents.sh --repo "[owner/repo]"

# Ask questions about a repo
${CLAUDE_PLUGIN_ROOT}/scripts/deepwiki/deepwiki_ask.sh --repo "[owner/repo]" --question "[question]"
```

### Context7 (Library Documentation)
```bash
# Resolve library ID
${CLAUDE_PLUGIN_ROOT}/scripts/context7/context7_resolve.sh --library "[library-name]"

# Get library documentation
${CLAUDE_PLUGIN_ROOT}/scripts/context7/context7_docs.sh --library-id "[/org/project]" --mode code --topic "[topic]"
```

### GitHub (Code & Repo Search)
```bash
# Search code across repos
${CLAUDE_PLUGIN_ROOT}/scripts/github/github_search_code.sh --query "[query]" --per-page 10

# Search repositories
${CLAUDE_PLUGIN_ROOT}/scripts/github/github_search_repos.sh --query "[query]" --sort stars

# Get file/directory contents
${CLAUDE_PLUGIN_ROOT}/scripts/github/github_file_contents.sh --owner "[owner]" --repo "[repo]" --path "[path]"
```

## Time MCP Integration

### Get Current Time First

Before ANY research, get current timestamp:

```
mcp__time-mcp__current_time(format: "YYYY-MM-DD")
```

### Query Enhancement Pattern

| Original Query | Enhanced Query |
|---------------|----------------|
| "React hooks best practices" | "React hooks best practices 2025" |
| "Rust async patterns" | "Rust async patterns 2024 2025" |
| "Next.js 15 features" | "Next.js 15 features latest" |
| "Go error handling" | "Go error handling 2024 2025 idioms" |

### Recency Scoring

Apply recency score to all sources:

| Age | Score | Flag |
|-----|-------|------|
| < 6 months | +2 | Fresh |
| 6-12 months | +1 | Current |
| 1-2 years | 0 | Dated |
| > 2 years | -1 | Potentially Outdated |

### Deprecation Detection

Flag sources that mention:
- "deprecated"
- "legacy"
- "old version"
- "no longer recommended"
- "superseded by"

## Option Presentation (MANDATORY)

**CRITICAL:** Always present 3-5 options with detailed comparisons for decision points.

### When to Present Options

**ALWAYS present options for:**
- Technology/library selection
- Framework choices
- Architecture patterns
- Implementation approaches
- Design decisions
- Tool selection
- API/client library choices

**Single answer only when:**
- Looking up specific API documentation
- Finding exact configuration values
- Retrieving specific error messages
- User explicitly requests a single answer

### Option Presentation Format

```markdown
## Options Comparison

### Option 1: [Name]
**Description:** [1-2 sentence summary]

**Strengths:**
- [Strength 1 with source citation]
- [Strength 2 with source citation]
- [Strength 3 with source citation]

**Weaknesses:**
- [Weakness 1 with source citation]
- [Weakness 2 with source citation]

**Best For:**
- [Use case 1]
- [Use case 2]

**Sources:**
- [Source 1](url)
- [Source 2](url)

### Option 2: [Name]
[Same structure]

### Option 3: [Name]
[Same structure]

### Comparison Matrix

| Criteria | Option 1 | Option 2 | Option 3 |
|----------|----------|----------|----------|
| Learning Curve | [rating] | [rating] | [rating] |
| Community Size | [rating] | [rating] | [rating] |
| Performance | [rating] | [rating] | [rating] |
| Maturity | [rating] | [rating] | [rating] |
| Documentation Quality | [rating] | [rating] | [rating] |
| Maintenance Activity | [rating] | [rating] | [rating] |

### Recommendation

**Recommended:** Option [X] - [Name]

**Rationale:** [2-3 sentences explaining why this option is recommended]

**Trade-offs:** [What you're gaining and what you're giving up]

**Alternative Consider:** Option [Y] - [Name] if [specific scenario]
```

## Research Output Format

```markdown
# Research Report: [Topic]

**Date:** [current date from Time MCP]
**Research Period:** [date range of oldest to newest source]
**Technologies:** [list]
**Freshness Score:** [% of sources < 1 year old]

## Summary
[Key findings overview - 3-5 bullet points]

## Options Comparison (REQUIRED)

[See Option Presentation Format above]

## Deprecation Warnings
[Any deprecated technologies or patterns found - if none, state "None identified"]

## Best Practices

### Recommended Patterns
1. **[Pattern Name]**
   - Description: [what it is]
   - Use when: [when to apply]
   - Source: [citation]

### Anti-Patterns to Avoid
1. **[Anti-Pattern Name]**
   - Description: [what to avoid]
   - Why problematic: [reasons]
   - Alternative: [better approach]
   - Source: [citation]

## Implementation Considerations

### Performance
- [Performance considerations from research]
- [Benchmarks or metrics]

### Security
- [Security considerations from research]
- [Known vulnerabilities or best practices]

### Compatibility
- [Browser/Node version requirements]
- [Platform-specific considerations]

## References

### Primary Sources
- [Source 1](url) - [description]
- [Source 2](url) - [description]

### Secondary Sources
- [Source 3](url) - [description]

### Community Discussions
- [Stack Overflow](url) - [description]
- [GitHub Issue](url) - [description]
```

## Evaluation Criteria

When comparing options, use these criteria:

| Criteria | Description | Weight |
|----------|-------------|--------|
| **Learning Curve** | How easy to learn? | High |
| **Community Size** | Support available? | High |
| **Performance** | Speed/efficiency | High |
| **Maturity** | Production-ready? | High |
| **Documentation Quality** | Well-documented? | High |
| **Maintenance Activity** | Actively maintained? | High |

**Scoring Rubric:**
- 5 = Excellent (best in class)
- 4 = Good (above average)
- 3 = Acceptable (meets needs)
- 2 = Fair (below average)
- 1 = Poor (significant concerns)
- 0 = Unacceptable (cannot be used)

## Research Best Practices

### DO's
- Always include year in search queries
- Cross-reference multiple sources
- Check for deprecation warnings
- Verify information recency
- Present 3-5 options for decisions
- Cite all sources
- Identify consensus vs disagreements

### DON'Ts
- Use information from 2+ years ago without verification
- Trust single sources without cross-referencing
- Ignore deprecation warnings
- Make decisions without option comparison
- Skip checking official documentation
- Assume blog posts are authoritative

## Reference

This is a reference document extracted from the `super-dev:research-agent`. For full agent behavior during Phase 3, invoke:

```
Task(subagent_type: "super-dev:research-agent", prompt: "Research: [topic]")
```

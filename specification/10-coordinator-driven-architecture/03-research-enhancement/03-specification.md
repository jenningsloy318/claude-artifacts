# Specification: Research Agent Enhancement

**Date:** 2025-11-27
**Author:** Claude
**Status:** Draft
**Parent:** [../00-master-specification.md]

## 1. Overview

Enhance the research-agent to always access the latest information by integrating Time MCP for current date/time context and implementing recency-aware search patterns.

## 2. Current State

The existing research-agent:
- Uses search-agent for multi-source retrieval
- Searches across Exa, Context7, DeepWiki, GitHub
- Does NOT include current timestamp in queries
- Does NOT filter by recency

## 3. Enhancement Requirements

### 3.1 Time MCP Integration

**Add to research-agent:**

```markdown
## Time-Aware Research

### Get Current Time
Before starting research, get current timestamp:

```
mcp__time-mcp__current_time(format: "YYYY-MM-DD")
```

### Include in Context
Pass current date to search-agent:
- Add year to technology queries: "React hooks 2025"
- Filter for recent publications
- Flag potentially outdated information
```

### 3.2 Time Context in Queries

**Query Enhancement Pattern:**

| Original Query | Enhanced Query |
|---------------|----------------|
| "React hooks best practices" | "React hooks best practices 2025" |
| "Rust async patterns" | "Rust async patterns 2024 2025" |
| "Next.js 15 features" | "Next.js 15 features latest" |

### 3.3 Recency Filtering

**Prioritize Recent Sources:**

```markdown
## Source Prioritization

### Recency Score
- < 6 months old: +2 relevance
- 6-12 months old: +1 relevance
- 1-2 years old: 0 relevance
- > 2 years old: -1 relevance (flag as potentially outdated)

### Deprecation Detection
If source mentions:
- "deprecated" → Flag in report
- "legacy" → Flag in report
- "old version" → Flag in report
```

### 3.4 Updated Output Format

**Research Report Enhancement:**

```markdown
# Research Report: [Topic]

**Date:** [current date from Time MCP]
**Research Period:** [date range of sources]
**Freshness Score:** [% of sources < 1 year old]

## Executive Summary
[summary]

## Findings

### [Finding 1]
- **Source:** [url]
- **Published:** [date]
- **Freshness:** [Fresh/Dated/Potentially Outdated]
- **Content:** [findings]

## Deprecation Warnings
[any deprecated technologies or patterns found]

## Recommendations
[recommendations with recency context]
```

## 4. File to Modify

**Path:** `agents/research-agent.md`

**Sections to Add/Update:**
1. Add "Time-Aware Research" section
2. Update query construction logic
3. Add recency filtering rules
4. Update output format template

## 5. Acceptance Criteria

- [ ] Time MCP invocation documented
- [ ] Query enhancement patterns defined
- [ ] Recency filtering rules added
- [ ] Output format includes timestamps
- [ ] Deprecation warning section added
- [ ] Freshness scoring defined

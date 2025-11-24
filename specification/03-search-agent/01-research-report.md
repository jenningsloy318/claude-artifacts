# Research Report: Search Agent Architecture

**Date:** 2025-11-23
**Feature:** Embeddable Search Agent for Dev Workflow Plugin

---

## 1. Executive Summary

This report documents research findings for creating a state-of-the-art search agent that ships with the dev-workflow plugin. The agent will provide unified search across code, documentation, issues, forums, and APIs with high retrieval quality.

---

## 2. Open Source Landscape Audit

### 2.1 Top Search/Research Agents

| Project | Stars | Architecture | Strengths | License |
|---------|-------|--------------|-----------|---------|
| **gpt-researcher** | 24.2k | Plan-and-Solve + RAG | Multi-agent, citation tracking, deep research | MIT |
| **Perplexica** | 27.4k | MetaSearchAgent + SearXNG | Focus modes, re-ranking, inline citations | MIT |
| **khoj** | 31.7k | Semantic search + RAG | Self-hosted, multi-source, offline support | AGPL-3.0 |
| **RAGFlow** | 68.2k | GraphRAG + Agent | Document understanding, multi-modal | Apache-2.0 |
| **LightRAG** | 24.2k | Graph-based RAG | Fast, lightweight, knowledge graph | MIT |
| **local-deep-research** | 3.6k | Multi-source search | 95% SimpleQA, privacy-focused | MIT |
| **deer-flow** | 18.2k | LangGraph multi-agent | Deep research, web crawling | Apache-2.0 |
| **R2R** | 7.5k | Agentic RAG | Production-ready, RESTful API | MIT |

### 2.2 Search APIs & Tools

| Tool | Purpose | Features |
|------|---------|----------|
| **Tavily** | LLM-optimized search | Structured results, relevance scoring |
| **SearXNG** | Meta-search engine | 70+ engines, privacy-focused |
| **Exa** | Neural search | Semantic understanding, code search |
| **Serper** | Google SERP API | Fast, affordable |

### 2.3 Re-ranking Models (MTEB Leaderboard)

| Model | Type | Context | Languages | Best For |
|-------|------|---------|-----------|----------|
| **BGE-M3** | Dense+Sparse+ColBERT | 8192 | 100+ | Hybrid retrieval |
| **bge-reranker-v2-m3** | Cross-encoder | 8192 | Multi | General re-ranking |
| **jina-reranker-v2** | Cross-encoder | 8192 | Multi | Code + SQL aware |
| **mxbai-colbert-large** | ColBERT | 512 | EN | Late interaction |
| **Cohere Rerank** | API | 4096 | Multi | Production |

---

## 3. Architectural Patterns Extracted

### 3.1 Query Expansion (from gpt-researcher)

```
User Query → LLM generates 3-5 sub-queries with specific goals
Example: "quantum computing" →
  - "Latest quantum computing breakthroughs 2024-2025"
  - "Quantum computing practical applications"
  - "Quantum vs classical computing comparison"
```

**Key Insight:** Each sub-query has a specific research goal, improving coverage.

### 3.2 Hybrid Retrieval Pipeline (from BGE-M3)

```
Query → [Dense Vector Search]  ─┐
      → [Sparse BM25 Search]   ─┼→ Fusion → Re-rank → Results
      → [Multi-vector ColBERT] ─┘
```

**Recommended Pipeline:**
1. Hybrid retrieval (dense + sparse)
2. Cross-encoder re-ranking
3. Confidence thresholding

### 3.3 Focus Modes (from Perplexica)

| Mode | Sources | Use Case |
|------|---------|----------|
| Web | All engines | General research |
| Academic | arXiv, Google Scholar, PubMed | Papers |
| Code | GitHub, StackOverflow | Implementation |
| Docs | Official docs, MDN | API reference |
| Reddit | Reddit | Community insights |
| YouTube | YouTube | Tutorials |

### 3.4 Citation & Provenance Tracking (from gpt-researcher)

```typescript
interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  confidence: number;      // 0-1 relevance score
  provenance: {
    source: string;        // "tavily" | "exa" | "searxng"
    query: string;         // Original query used
    timestamp: string;     // ISO timestamp
    hash: string;          // SHA256 of content for audit
  };
}
```

### 3.5 Self-Consistency & Verification (from Agentic RAG papers)

1. **Multi-query consensus:** Run same query through multiple sources
2. **Cross-reference:** Verify facts appear in multiple results
3. **Confidence aggregation:** Higher score if multiple sources agree

### 3.6 Cost-Aware LLM Routing (from gpt-researcher)

```
Simple query → gpt-4o-mini (cheap, fast)
Complex synthesis → gpt-4o (expensive, thorough)
Re-ranking → Cross-encoder model (no LLM needed)
```

---

## 4. Recommended Architecture

### 4.1 Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Search Agent                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    Query     │───▶│   Retriever  │───▶│   Reranker   │  │
│  │   Expander   │    │   (Multi)    │    │ (Confidence) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  LLM Router  │    │ Source Pool  │    │  Citation    │  │
│  │ (cost-aware) │    │ (Exa,Tavily) │    │  Tracker     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Interface Design

```typescript
interface SearchContext {
  mode: 'web' | 'code' | 'docs' | 'academic' | 'all';
  maxResults?: number;      // default: 10
  minConfidence?: number;   // default: 0.5
  rerank?: boolean;         // default: true
  expandQuery?: boolean;    // default: true
}

interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  confidence: number;
  provenance: {
    source: string;
    query: string;
    timestamp: string;
    hash: string;
  };
}

async function search(
  query: string,
  context?: SearchContext
): Promise<SearchResult[]>
```

### 4.3 Search Flow

1. **Query Analysis:** Determine intent and mode
2. **Query Expansion:** Generate 3-5 sub-queries (optional)
3. **Parallel Retrieval:** Search multiple sources concurrently
4. **Deduplication:** Remove duplicate URLs
5. **Re-ranking:** Cross-encoder scoring
6. **Confidence Filtering:** Remove low-confidence results
7. **Citation Tracking:** Add provenance to each result

---

## 5. Tool Integration for Claude Code

### 5.1 Available MCP Tools

| Tool | Use For |
|------|---------|
| `mcp__exa__web_search_exa` | Neural web search |
| `mcp__exa__get_code_context_exa` | Code/library docs |
| `mcp__deepwiki__ask_question` | GitHub repo docs |
| `mcp__context7__get-library-docs` | Library documentation |
| `mcp__github__search_code` | GitHub code search |
| `mcp__github__search_repositories` | GitHub repo search |
| `WebSearch` | General web search |
| `WebFetch` | Fetch and process URLs |

### 5.2 Search Mode Mapping

| Mode | Primary Tools | Fallback |
|------|---------------|----------|
| `web` | Exa, WebSearch | WebFetch |
| `code` | Exa code, GitHub search | Context7 |
| `docs` | Context7, DeepWiki | Exa |
| `academic` | Exa (arxiv filter) | WebSearch |
| `all` | All tools in parallel | - |

---

## 6. Licensing Summary

All referenced projects use permissive licenses suitable for embedding:

| Project | License | Commercial Use |
|---------|---------|----------------|
| gpt-researcher | MIT | Yes |
| Perplexica | MIT | Yes |
| BGE-M3 | MIT | Yes |
| R2R | MIT | Yes |
| LightRAG | MIT | Yes |

---

## 7. References

- gpt-researcher: https://github.com/assafelovic/gpt-researcher
- Perplexica: https://github.com/ItzCrazyKns/Perplexica
- BGE-M3: https://huggingface.co/BAAI/bge-m3
- Agentic RAG Survey: https://arxiv.org/abs/2501.09136
- MTEB Leaderboard: https://huggingface.co/spaces/mteb/leaderboard

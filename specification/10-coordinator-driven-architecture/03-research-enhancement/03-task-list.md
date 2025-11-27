# Task List: Research Enhancement

**Total Tasks:** 4

## Tasks

- [ ] **T3.1** Add Time MCP integration section
  - Add "Time-Aware Research" section
  - Document mcp__time-mcp__current_time usage
  - Add context construction example

- [ ] **T3.2** Add time context to search queries
  - Update query construction patterns
  - Add year suffix rules
  - Document query enhancement examples

- [ ] **T3.3** Add recency filtering logic
  - Add recency scoring (< 6 months, 6-12 months, etc.)
  - Add deprecation detection keywords
  - Document flagging patterns

- [ ] **T3.4** Update output format with timestamps
  - Add date header from Time MCP
  - Add research period field
  - Add freshness score
  - Add deprecation warnings section

## Checkpoint

After T3.4:
```bash
git add agents/research-agent.md
git commit -m "feat(super-dev): Enhance research agent with Time MCP"
```

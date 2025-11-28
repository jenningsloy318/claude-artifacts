# Exa MCP Search Script Specification

## Overview

Create executable Python scripts that wrap Exa MCP server tools, allowing agents to perform web searches by executing scripts via Bash rather than making direct MCP tool calls.

## Architecture

Based on the [Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) pattern:

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Research Agent │──────▶│  Python Script  │──────▶│  Exa MCP Server │
│                 │       │  (exa_search.py)│       │                 │
│  Executes via   │       │                 │       │  mcp-server-exa │
│  Bash tool      │◀──────│  Returns JSON   │◀──────│                 │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

## Components

### 1. Exa Search Script (`scripts/exa/exa_search.py`)

**Purpose:** Execute web searches using Exa MCP server

**Input Parameters:**
- `--query` or `-q`: Search query string (required)
- `--type`: Search type - `auto`, `fast`, `deep` (default: `auto`)
- `--results`: Number of results (default: 8)
- `--context-chars`: Max characters for context (default: 10000)

**Output:** JSON formatted search results

**Example Usage:**
```bash
python3 super-dev-plugin/scripts/exa/exa_search.py --query "React hooks best practices 2025"
```

### 2. Exa Code Context Script (`scripts/exa/exa_code.py`)

**Purpose:** Get code context for programming queries

**Input Parameters:**
- `--query` or `-q`: Code-related search query (required)
- `--tokens`: Number of tokens to return (default: 5000)

**Output:** JSON formatted code context

**Example Usage:**
```bash
python3 super-dev-plugin/scripts/exa/exa_code.py --query "Next.js 15 server components"
```

## Technical Implementation

### MCP Client Connection

Using the `mcp` Python SDK with stdio transport to connect to the Exa MCP server:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@anthropic/mcp-server-exa"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("web_search_exa", arguments={...})
```

### Environment Requirements

- `EXA_API_KEY` environment variable must be set
- Node.js and npx available for running the MCP server
- Python 3.10+ with `mcp` package installed

### Output Format

```json
{
  "success": true,
  "query": "search query",
  "results": [
    {
      "title": "Result title",
      "url": "https://example.com",
      "snippet": "Content excerpt...",
      "score": 0.95
    }
  ],
  "metadata": {
    "tool": "web_search_exa",
    "timestamp": "2025-11-27T10:00:00Z",
    "result_count": 8
  }
}
```

### Error Handling

```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ConnectionError|APIError|ValidationError"
}
```

## Integration with Research Agent

Update `super-dev-plugin/agents/research-agent.md` to include:

```markdown
### Exa Search via Script

For Exa searches, execute the script:

\```bash
python3 super-dev-plugin/scripts/exa/exa_search.py --query "[query]" --type auto --results 10
\```

Parse the JSON output and incorporate results into research report.
```

## File Structure

```
super-dev-plugin/
├── scripts/
│   └── exa/
│       ├── __init__.py
│       ├── exa_search.py      # Web search wrapper
│       ├── exa_code.py        # Code context wrapper
│       └── requirements.txt   # Python dependencies
└── agents/
    └── research-agent.md      # Updated with script usage
```

## Dependencies

**requirements.txt:**
```
mcp>=1.0.0
```

## Benefits

1. **Token Efficiency**: Only load tool definitions when needed
2. **Data Processing**: Filter/process results before returning to model
3. **Reusability**: Scripts can be used by any agent
4. **Testability**: Scripts can be tested independently
5. **Caching**: Can add result caching in the script layer

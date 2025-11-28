# Exa MCP HTTP Connector Scripts Specification

**Updated:** 2025-11-28
**Status:** Implemented
**Related:** [11-mcp-http-connector](../11-mcp-http-connector/01-specification.md)

## Overview

Python scripts that connect to Exa's **HTTP-based MCP server** at `https://mcp.exa.ai/mcp`, allowing agents to perform web searches and code context retrieval via Bash execution.

## Architecture

[UPDATED: 2025-11-28] Changed from stdio to HTTP connector approach.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────┐
│  Agent          │────▶│  Python Script  │────▶│  Exa MCP Server     │
│  (via Bash)     │     │  (HttpConnector)│     │  https://mcp.exa.ai │
└─────────────────┘     └─────────────────┘     └─────────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  ~/.claude.json │
                        │  (MCP Config)   │
                        └─────────────────┘
```

**Key Change:** Scripts use `mcp-use` library's `HttpConnector` to connect to the existing HTTP MCP server, rather than spawning a new stdio subprocess.

## Components

### 1. Exa Search Script (`scripts/exa/exa_search.py`)

**Purpose:** Execute web searches using Exa's `web_search_exa` tool

**Input Parameters:**
| Parameter | Short | Required | Default | Description |
|-----------|-------|----------|---------|-------------|
| `--query` | `-q` | Yes | - | Search query string |
| `--type` | `-t` | No | `auto` | Search type: `auto`, `fast`, `deep` |
| `--results` | `-r` | No | `8` | Number of results |
| `--context-chars` | `-c` | No | `10000` | Max context characters |

**Example Usage:**
```bash
python3 super-dev-plugin/scripts/exa/exa_search.py \
  --query "React 19 new features 2025" \
  --type deep \
  --results 10
```

### 2. Exa Code Context Script (`scripts/exa/exa_code.py`)

**Purpose:** Get code context using Exa's `get_code_context_exa` tool

**Input Parameters:**
| Parameter | Short | Required | Default | Description |
|-----------|-------|----------|---------|-------------|
| `--query` | `-q` | Yes | - | Code-related search query |
| `--tokens` | `-t` | No | `5000` | Token count (1000-50000) |

**Example Usage:**
```bash
python3 super-dev-plugin/scripts/exa/exa_code.py \
  --query "Next.js 15 app router middleware" \
  --tokens 10000
```

## Technical Implementation

### HttpConnector Approach [UPDATED: 2025-11-28]

Using `mcp-use` library's `HttpConnector` to connect to existing HTTP MCP server:

```python
from mcp_use.client.connectors import HttpConnector

# Read config from Claude Code settings
config = find_exa_config()  # Returns {name, url, headers}

# Connect to existing HTTP server (no subprocess spawning)
connector = HttpConnector(
    base_url=config["url"],      # https://mcp.exa.ai/mcp
    headers=config["headers"]     # {EXA_API_KEY: ...}
)
await connector.connect()

# Call tool
result = await connector.call_tool(
    name="web_search_exa",
    arguments={"query": query, "type": "auto", ...}
)

await connector.disconnect()
```

### Configuration Discovery

Scripts auto-discover Exa config from Claude Code settings:

1. `~/.claude.json` (primary)
2. `~/.claude/settings.json`
3. `~/.claude/settings.local.json`
4. `.claude/settings.json` (project)
5. `.claude/settings.local.json` (project)

**Expected Config Structure:**
```json
{
  "mcpServers": {
    "exa": {
      "type": "http",
      "url": "https://mcp.exa.ai/mcp",
      "headers": {
        "EXA_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Auto-Install Dependencies

Scripts auto-install `mcp-use` if not present:

```python
def ensure_mcp_use_installed():
    try:
        import mcp_use
        return True
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp-use", "-q"])
        return True
```

## Output Format

### Success Response
```json
{
  "success": true,
  "query": "React hooks best practices",
  "results": "...(search results content)...",
  "metadata": {
    "tool": "web_search_exa",
    "server": "exa",
    "url": "https://mcp.exa.ai/mcp",
    "timestamp": "2025-11-28T03:30:00+00:00"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "error_type": "ConfigurationError|ConnectionError|ToolError|DependencyError"
}
```

## File Structure

```
super-dev-plugin/
├── scripts/
│   ├── __init__.py              # Package docs
│   ├── README.md                # Usage guide
│   ├── template_connector.py    # Template for new connectors
│   └── exa/
│       ├── __init__.py          # Module docs
│       ├── exa_search.py        # Web search wrapper
│       ├── exa_code.py          # Code context wrapper
│       └── requirements.txt     # Dependencies
└── agents/
    └── research-agent.md        # Updated with script usage
```

## Integration with Research Agent

The research agent is configured to use these scripts:

```markdown
### Exa Search via Script (Recommended)

For Exa searches, execute the wrapper scripts via Bash:

```bash
python3 super-dev-plugin/scripts/exa/exa_search.py --query "[query]" --results 10
```

### When to Use Scripts vs Direct MCP Calls

| Use Scripts | Use Direct MCP Calls |
|-------------|---------------------|
| Multiple searches in batch | Single quick search |
| Processing/filtering needed | Simple result display |
| Token efficiency critical | Interactive exploration |
```

## Benefits

1. **No Separate API Key Needed** - Reads from existing Claude Code config
2. **Token Efficiency** - Results processed externally
3. **Auto-Install** - Handles mcp-use dependency automatically
4. **HTTP Connection** - Connects to existing server, no subprocess spawning
5. **Consistent Output** - Standardized JSON format
6. **Reusability** - Scripts usable by any agent

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-11-28 | Migrated to HttpConnector approach |
| 1.0.0 | 2025-11-27 | Initial stdio-based implementation |

# MCP HTTP Connector Pattern Specification

**Created:** 2025-11-28
**Status:** Reference Specification
**Purpose:** Define reusable pattern for creating scripts that connect to HTTP-based MCP servers

## Overview

This specification defines a standardized pattern for creating Python scripts that connect to **HTTP-based MCP servers** configured in Claude Code. These scripts enable agents to execute MCP tool calls via Bash, providing token efficiency, batch operations, and consistent output formatting.

## Problem Statement

Claude Code's MCP servers can be configured in two ways:

| Type | Transport | Can Connect Externally? |
|------|-----------|------------------------|
| `http` | HTTP/HTTPS endpoint | **Yes** - Server is already running |
| `stdio` | Subprocess stdin/stdout | **No** - Owned by Claude Code process |

Scripts can only connect to **HTTP-based** servers because:
- HTTP servers are independent services accessible via URL
- Stdio servers are subprocesses whose I/O is owned by Claude Code
- External processes cannot share stdio streams with Claude Code

## Architecture

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  Agent (via Bash)   │────▶│  HTTP Connector      │────▶│  MCP HTTP Server    │
│                     │     │  Script              │     │  (e.g., Exa, etc.)  │
└─────────────────────┘     └──────────────────────┘     └─────────────────────┘
                                     │
                                     ▼
                            ┌──────────────────────┐
                            │  Claude Code Config  │
                            │  ~/.claude.json      │
                            └──────────────────────┘
```

## Configuration Discovery

Scripts auto-discover MCP config from Claude Code settings in priority order:

1. `~/.claude.json` (global user config - primary)
2. `~/.claude/settings.json` (user settings)
3. `~/.claude/settings.local.json` (local user overrides)
4. `.claude/settings.json` (project settings)
5. `.claude/settings.local.json` (local project overrides)

### Expected Config Structure

```json
{
  "mcpServers": {
    "server-name": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "API_KEY": "your-api-key",
        "Authorization": "Bearer token"
      }
    }
  }
}
```

**Required Fields:**
- `type`: Must be `"http"` for external connection
- `url`: Full URL of the MCP HTTP endpoint

**Optional Fields:**
- `headers`: Key-value pairs for authentication/authorization

## Script Template Structure

### Core Components

Every HTTP connector script should include:

```python
#!/usr/bin/env python3
"""
[Tool Name] Script: [Brief description]

Usage:
    python3 script_name.py --query "..." [options]

Output:
    JSON formatted results to stdout
"""

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Configuration
SERVER_PATTERN = "server_name"  # Pattern to match in config
TOOL_NAME = "tool_name"         # MCP tool to call

# 1. Auto-install dependency
def ensure_mcp_use_installed(): ...

# 2. Config discovery
def find_mcp_config(server_pattern: str) -> dict | None: ...

# 3. Tool execution
async def call_tool(arguments: dict) -> dict: ...

# 4. CLI interface
def main(): ...
```

### 1. Dependency Auto-Install

```python
def ensure_mcp_use_installed():
    """Ensure mcp-use package is installed, install if missing."""
    try:
        import mcp_use
        return True
    except ImportError:
        print("Installing mcp-use package...", file=sys.stderr)
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "mcp-use", "-q"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            return False
```

### 2. Configuration Discovery

```python
def find_mcp_config(server_pattern: str) -> dict | None:
    """Find MCP server config from Claude Code settings."""
    config_paths = [
        Path.home() / ".claude.json",
        Path.home() / ".claude" / "settings.json",
        Path.home() / ".claude" / "settings.local.json",
        Path.cwd() / ".claude" / "settings.json",
        Path.cwd() / ".claude" / "settings.local.json",
    ]

    for path in config_paths:
        if path.exists():
            try:
                with open(path) as f:
                    config = json.load(f)

                mcp_servers = config.get("mcpServers", {})

                for name, server_config in mcp_servers.items():
                    if server_pattern in name.lower():
                        if server_config.get("type") == "http":
                            return {
                                "name": name,
                                "url": server_config.get("url"),
                                "headers": server_config.get("headers", {})
                            }
            except (json.JSONDecodeError, IOError):
                continue

    return None
```

### 3. HttpConnector Usage

```python
async def call_tool(arguments: dict) -> dict:
    """Call MCP tool via HttpConnector."""
    from mcp_use.client.connectors import HttpConnector

    config = find_mcp_config(SERVER_PATTERN)
    if not config:
        return {"success": False, "error": "Config not found", "error_type": "ConfigurationError"}

    connector = HttpConnector(
        base_url=config["url"],
        headers=config["headers"]
    )

    try:
        await connector.connect()

        # Verify tool exists
        tools = await connector.list_tools()
        if TOOL_NAME not in [t.name for t in tools]:
            return {"success": False, "error": f"Tool not found", "error_type": "ToolError"}

        # Call tool
        result = await connector.call_tool(name=TOOL_NAME, arguments=arguments)

        # Process result
        if result.content:
            content = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            return {
                "success": True,
                "data": json.loads(content) if content.startswith('{') else content,
                "metadata": {
                    "tool": TOOL_NAME,
                    "server": config["name"],
                    "url": config["url"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
    finally:
        await connector.disconnect()
```

## Output Format

### Success Response

```json
{
  "success": true,
  "data": {
    // Tool-specific response data
  },
  "metadata": {
    "tool": "tool_name",
    "server": "server_name",
    "url": "https://mcp.example.com/mcp",
    "timestamp": "2025-11-28T03:30:00+00:00"
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": "Descriptive error message",
  "error_type": "ErrorClassName"
}
```

### Standard Error Types

| Error Type | Description | Resolution |
|------------|-------------|------------|
| `DependencyError` | mcp-use package issue | Check pip install |
| `ConfigurationError` | MCP config not found | Verify Claude Code config |
| `ConnectionError` | Cannot connect to server | Check URL/network |
| `ToolError` | Tool not found or failed | Verify tool name |
| `TimeoutError` | Request timed out | Retry or increase timeout |

## Known HTTP MCP Servers

Based on typical Claude Code configurations:

| Server | URL Pattern | Config Name | Tools |
|--------|-------------|-------------|-------|
| Exa | `https://mcp.exa.ai/mcp` | `exa` | `web_search_exa`, `get_code_context_exa` |
| DeepWiki | `https://mcp.deepwiki.com/mcp` | `deepwiki` | `read_wiki_structure`, `read_wiki_contents`, `ask_question` |
| Context7 | `https://mcp.context7.com/mcp` | `context7` | `resolve-library-id`, `get-library-docs` |
| Figma | `https://mcp.figma.com/mcp` | `figma` | Design tools |
| GitHub | `https://api.githubcopilot.com/mcp/` | `github` | Repository tools |

## Creating a New Connector Script

### Step 1: Verify HTTP Server

Check if target MCP server is HTTP-based:
```bash
# In Claude Code, run /mcp to see server configs
# Look for type: "http" with a URL
```

### Step 2: Copy Template

```bash
cp specification/11-mcp-http-connector/template_connector.py \
   super-dev-plugin/scripts/new_server/new_tool.py
```

### Step 3: Customize

1. Set `SERVER_PATTERN` to match config name
2. Set `TOOL_NAME` to target tool
3. Update CLI arguments for tool parameters
4. Map arguments in `call_tool()`

### Step 4: Test

```bash
python3 super-dev-plugin/scripts/new_server/new_tool.py --query "test"
```

## Best Practices

### 1. Error Handling
- Always wrap connector operations in try/except/finally
- Disconnect connector even on errors
- Return structured error responses

### 2. Dependency Management
- Auto-install mcp-use if missing
- Use subprocess.check_call with quiet flags
- Report installation status to stderr

### 3. Output
- Always output valid JSON to stdout
- Use stderr for logs/warnings
- Exit with code 0 on success, 1 on error

### 4. CLI Design
- Use argparse with short and long options
- Set sensible defaults
- Include help text

## Integration with Agents

Agents can call scripts via Bash:

```python
# In agent (research-agent, search-agent, etc.)
result = await bash(
    f"python3 super-dev-plugin/scripts/exa/exa_search.py "
    f"--query '{query}' --results 10"
)
parsed = json.loads(result)
if parsed["success"]:
    # Process data
```

### When to Use Scripts vs Direct MCP

| Use Scripts | Use Direct MCP |
|-------------|---------------|
| Batch operations | Single queries |
| Processing/filtering | Simple display |
| Token efficiency | Interactive use |
| Agent subprocesses | Main conversation |

## File Organization

```
specification/
└── 11-mcp-http-connector/
    ├── 01-specification.md      # This specification
    └── template_connector.py    # Template for new scripts

super-dev-plugin/
└── scripts/
    ├── __init__.py              # Package documentation
    ├── README.md                # Usage guide
    ├── exa/                     # Exa server scripts
    │   ├── exa_search.py
    │   └── exa_code.py
    ├── deepwiki/                # DeepWiki server scripts (future)
    └── context7/                # Context7 server scripts (future)
```

## Related Specifications

- [exa-search-script](../exa-search-script/01-specification.md) - Exa implementation

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-28 | Initial specification |

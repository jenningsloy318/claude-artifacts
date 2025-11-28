# MCP Stdio Connector Specification

**Version:** 1.0.0
**Created:** 2025-11-28
**Status:** Active

## Overview

This specification defines the pattern for creating scripts that connect to MCP servers using stdio transport. Unlike HTTP connectors that connect to existing servers, stdio connectors **spawn a new server subprocess** and communicate via stdin/stdout.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Stdio Connector Flow                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐     ┌────────────┐ │
│  │ Python Script│──────│StdioConnector│─────│MCP Server  │ │
│  │              │      │              │     │(subprocess)│ │
│  │ call_tool()  │ args │  connect()   │spawn│            │ │
│  │              │──────│              │─────│ npx/python │ │
│  │              │result│  call_tool() │stdin│            │ │
│  │              │◄─────│              │────►│            │ │
│  │              │      │ disconnect() │stdout            │ │
│  └──────────────┘      └──────────────┘     └────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Key Differences from HTTP Connector

| Aspect | HTTP Connector | Stdio Connector |
|--------|----------------|-----------------|
| Server lifecycle | Connects to **existing** server | **Spawns new** server subprocess |
| Config discovery | Reads URL from Claude Code config | Reads command/args from config |
| Transport | HTTP/HTTPS network | stdin/stdout pipes |
| Server type | `type: "http"` | `type: "stdio"` |
| Use case | Remote/shared servers | Local/isolated servers |
| Port conflicts | None (connects to existing) | None (no ports used) |

## When to Use Stdio vs HTTP

### Use Stdio Connector When:
- MCP server is configured with `type: "stdio"`
- Server uses `command` and `args` in config
- You need isolated server instance per script run
- Server requires local file system access
- No shared state needed between calls

### Use HTTP Connector When:
- MCP server is configured with `type: "http"`
- Server has a URL endpoint
- Server is already running (managed by Claude Code)
- Shared state/session needed across calls

## Configuration Discovery

### Claude Code Config Locations

```python
config_paths = [
    Path.home() / ".claude.json",                    # Primary
    Path.home() / ".claude" / "settings.json",       # User settings
    Path.home() / ".claude" / "settings.local.json", # Local overrides
    Path.cwd() / ".claude" / "settings.json",        # Project settings
    Path.cwd() / ".claude" / "settings.local.json",  # Project local
]
```

### Stdio Server Config Structure

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

## StdioConnector API

### Import

```python
from mcp_use.client.connectors import StdioConnector
```

### Constructor

```python
connector = StdioConnector(
    command="npx",           # Command to execute
    args=["-y", "@mcp/server"],  # Command arguments
    env={"API_KEY": "..."},  # Environment variables
)
```

### Methods

| Method | Description |
|--------|-------------|
| `await connector.connect()` | Start subprocess and establish connection |
| `await connector.list_tools()` | List available tools |
| `await connector.call_tool(name, arguments)` | Call a tool |
| `await connector.disconnect()` | Stop subprocess and cleanup |

## Script Template Structure

```python
#!/usr/bin/env python3
"""
Template for stdio MCP connector scripts.
"""

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Server pattern to match in Claude Code config
SERVER_PATTERN = "your_server"
TOOL_NAME = "your_tool_name"


def ensure_mcp_use_installed():
    """Ensure mcp-use package is installed."""
    # Auto-install logic...


def find_stdio_config(server_pattern: str) -> dict | None:
    """Find stdio MCP server config from Claude Code settings."""
    config_paths = [
        Path.home() / ".claude.json",
        # ... more paths
    ]

    for path in config_paths:
        if path.exists():
            config = json.load(open(path))
            mcp_servers = config.get("mcpServers", {})

            for name, server_config in mcp_servers.items():
                if server_pattern in name.lower():
                    if server_config.get("type") == "stdio":
                        return {
                            "name": name,
                            "command": server_config.get("command"),
                            "args": server_config.get("args", []),
                            "env": server_config.get("env", {})
                        }
    return None


async def call_tool(arguments: dict) -> dict:
    """Call MCP tool via StdioConnector."""
    from mcp_use.client.connectors import StdioConnector

    config = find_stdio_config(SERVER_PATTERN)
    if not config:
        return {"success": False, "error": "Config not found"}

    connector = None
    try:
        connector = StdioConnector(
            command=config["command"],
            args=config["args"],
            env=config["env"]
        )
        await connector.connect()

        result = await connector.call_tool(name=TOOL_NAME, arguments=arguments)

        return {
            "success": True,
            "data": result.content[0].text if result.content else None,
            "metadata": {
                "tool": TOOL_NAME,
                "server": config["name"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    finally:
        if connector:
            await connector.disconnect()
```

## Output Format

All scripts should return consistent JSON:

```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "tool": "tool_name",
    "server": "server_name",
    "command": "npx",
    "timestamp": "2025-11-28T04:00:00+00:00"
  }
}
```

## Error Format

```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ConfigurationError|DependencyError|ToolError"
}
```

## Known Stdio MCP Servers

| Server | Package | Common Tools |
|--------|---------|--------------|
| Filesystem | `@modelcontextprotocol/server-filesystem` | read_file, write_file, list_directory |
| Git | `@modelcontextprotocol/server-git` | git_status, git_log, git_diff |
| SQLite | `@modelcontextprotocol/server-sqlite` | query, execute |
| Postgres | `@modelcontextprotocol/server-postgres` | query |
| Memory | `@modelcontextprotocol/server-memory` | store, retrieve |
| Puppeteer | `@modelcontextprotocol/server-puppeteer` | navigate, screenshot |
| Brave Search | `@modelcontextprotocol/server-brave-search` | brave_web_search |
| Fetch | `@modelcontextprotocol/server-fetch` | fetch |
| Slack | `@modelcontextprotocol/server-slack` | list_channels, post_message |
| Google Maps | `@modelcontextprotocol/server-google-maps` | geocode, directions |

## Best Practices

1. **Always disconnect**: Use `try/finally` to ensure subprocess cleanup
2. **Check config type**: Verify `type == "stdio"` before using StdioConnector
3. **Handle subprocess errors**: Server may fail to start
4. **Timeout handling**: Set appropriate timeouts for long-running tools
5. **Environment variables**: Pass required env vars from config

## File Organization

```
specification/
└── 12-mcp-stdio-connector/
    ├── 01-specification.md      # This specification
    └── template_stdio_connector.py  # Template script

super-dev-plugin/
└── scripts/
    ├── filesystem/              # Filesystem server scripts (future)
    └── memory/                  # Memory server scripts (future)
```

## Related Specifications

- [11-mcp-http-connector](../11-mcp-http-connector/01-specification.md) - HTTP connector pattern

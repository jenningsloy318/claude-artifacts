# MCP WebSocket Connector Specification

**Version:** 1.0.0
**Created:** 2025-11-28
**Status:** Active

## Overview

This specification defines the pattern for creating scripts that connect to MCP servers using WebSocket transport. WebSocket connectors establish bidirectional communication channels with MCP servers for real-time, low-latency interactions.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  WebSocket Connector Flow                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐     ┌────────────┐ │
│  │ Python Script│──────│  WebSocket   │─────│ MCP Server │ │
│  │              │      │  Connector   │     │ (remote)   │ │
│  │ call_tool()  │ args │              │ ws  │            │ │
│  │              │──────│  connect()   │─────│ws://server │ │
│  │              │result│              │bidir│            │ │
│  │              │◄─────│  call_tool() │◄───►│            │ │
│  │              │      │ disconnect() │     │            │ │
│  └──────────────┘      └──────────────┘     └────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Comparison of MCP Connector Types

| Aspect | HTTP Connector | Stdio Connector | WebSocket Connector |
|--------|----------------|-----------------|---------------------|
| Server lifecycle | Connects to **existing** | **Spawns** subprocess | Connects to **existing** |
| Config key | `url` | `command` + `args` | `ws_url` |
| Transport | HTTP + SSE | stdin/stdout pipes | WebSocket (ws://) |
| Direction | Request-response + SSE stream | Bidirectional pipes | Full bidirectional |
| Use case | Web APIs, cloud services | Local tools | Real-time, low-latency |
| Latency | Higher (HTTP overhead) | Low | Lowest |
| Connection | Per-request or keep-alive | Process lifetime | Persistent |

## When to Use WebSocket Connector

### Use WebSocket When:
- MCP server is configured with `ws_url`
- Real-time bidirectional communication needed
- Low latency is critical
- Server pushes updates to client
- Long-running connections preferred

### Use HTTP Connector When:
- Server uses standard HTTP/HTTPS URLs
- SSE streaming is sufficient
- Firewall restrictions prevent WebSocket

### Use Stdio Connector When:
- Running local subprocess servers
- Isolated per-invocation needed

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

### WebSocket Server Config Structure

```json
{
  "mcpServers": {
    "realtime-server": {
      "type": "websocket",
      "ws_url": "ws://localhost:8765/mcp",
      "headers": {
        "Authorization": "Bearer token"
      }
    }
  }
}
```

**Config key**: `ws_url` (not `url`) indicates WebSocket transport.

## WebSocketConnector API

### Import

```python
from mcp_use.client.connectors import WebSocketConnector
```

### Constructor

```python
connector = WebSocketConnector(
    ws_url="ws://localhost:8765/mcp",  # WebSocket URL
    headers={"Authorization": "Bearer ..."},  # Optional headers
)
```

### Methods

| Method | Description |
|--------|-------------|
| `await connector.connect()` | Establish WebSocket connection |
| `await connector.list_tools()` | List available tools |
| `await connector.call_tool(name, arguments)` | Call a tool |
| `await connector.disconnect()` | Close WebSocket connection |

## Script Template Structure

```python
#!/usr/bin/env python3
"""
Template for WebSocket MCP connector scripts.
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


def find_websocket_config(server_pattern: str) -> dict | None:
    """Find WebSocket MCP server config from Claude Code settings."""
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
                    # Check for ws_url (WebSocket indicator)
                    if server_config.get("ws_url"):
                        return {
                            "name": name,
                            "ws_url": server_config.get("ws_url"),
                            "headers": server_config.get("headers", {})
                        }
    return None


async def call_tool(arguments: dict) -> dict:
    """Call MCP tool via WebSocketConnector."""
    from mcp_use.client.connectors import WebSocketConnector

    config = find_websocket_config(SERVER_PATTERN)
    if not config:
        return {"success": False, "error": "Config not found"}

    connector = None
    try:
        connector = WebSocketConnector(
            ws_url=config["ws_url"],
            headers=config.get("headers", {})
        )
        await connector.connect()

        result = await connector.call_tool(name=TOOL_NAME, arguments=arguments)

        return {
            "success": True,
            "data": result.content[0].text if result.content else None,
            "metadata": {
                "tool": TOOL_NAME,
                "server": config["name"],
                "ws_url": config["ws_url"],
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
    "ws_url": "ws://localhost:8765/mcp",
    "timestamp": "2025-11-28T04:00:00+00:00"
  }
}
```

## Error Format

```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ConfigurationError|DependencyError|ToolError|ConnectionError"
}
```

## WebSocket-Specific Considerations

### Connection Lifecycle
- WebSocket connections are persistent
- Always disconnect in `finally` block
- Handle reconnection on connection drop

### Headers and Authentication
- Headers can be passed during handshake
- Some WebSocket servers require auth tokens

### Error Handling
- `ConnectionRefusedError`: Server not running
- `TimeoutError`: Connection timeout
- `websockets.exceptions.ConnectionClosed`: Connection dropped

## Best Practices

1. **Always disconnect**: Use `try/finally` to ensure cleanup
2. **Check for ws_url**: Use `ws_url` key to identify WebSocket configs
3. **Handle reconnection**: Implement retry logic for dropped connections
4. **Timeout handling**: Set appropriate timeouts for long-running operations
5. **Secure connections**: Use `wss://` for production (WebSocket Secure)

## File Organization

```
specification/
└── 13-mcp-websocket-connector/
    ├── 01-specification.md           # This specification
    └── template_websocket_connector.py  # Template script

super-dev-plugin/
└── scripts/
    └── websocket/                    # WebSocket server scripts (future)
```

## Related Specifications

- [11-mcp-http-connector](../11-mcp-http-connector/01-specification.md) - HTTP connector pattern (uses SSE)
- [12-mcp-stdio-connector](../12-mcp-stdio-connector/01-specification.md) - Stdio connector pattern

#!/usr/bin/env python3
"""
Template MCP WebSocket Connector Script

This is a template for creating new MCP WebSocket connector scripts.
Copy this file and customize for your target MCP server and tool.

Usage:
    cp template_websocket_connector.py new_server/new_tool.py
    # Then customize the marked sections below

Instructions:
    1. Update the docstring with your tool description
    2. Set SERVER_PATTERN to match your MCP server name in config
    3. Set TOOL_NAME to the specific tool you want to call
    4. Update CLI arguments as needed
    5. Map arguments to tool parameters in call_tool()

Key Difference from Other Connectors:
    - HTTP: Connects via HTTP + SSE for streaming
    - Stdio: Spawns a NEW server subprocess
    - WebSocket: Bidirectional persistent connection (lowest latency)
"""

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ============================================================================
# CUSTOMIZE THESE VALUES
# ============================================================================

# Pattern to match server name in Claude Code config (lowercase)
# Example: "realtime", "streaming", "live"
SERVER_PATTERN = "your_server"

# Name of the tool to call on the MCP server
# Run list_tools() first to see available tools
TOOL_NAME = "your_tool_name"

# ============================================================================
# CORE FUNCTIONS (usually no changes needed)
# ============================================================================


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
            print("mcp-use installed successfully.", file=sys.stderr)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install mcp-use: {e}", file=sys.stderr)
            return False


def find_websocket_config(server_pattern: str) -> dict | None:
    """Find WebSocket MCP server config from Claude Code settings.

    Args:
        server_pattern: Lowercase pattern to match server name

    Returns:
        Dict with name, ws_url, headers if found, None otherwise
    """
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
                        # Check for ws_url (WebSocket indicator)
                        ws_url = server_config.get("ws_url")
                        if ws_url:
                            return {
                                "name": name,
                                "ws_url": ws_url,
                                "headers": server_config.get("headers", {})
                            }
            except (json.JSONDecodeError, IOError):
                continue

    return None


async def call_tool(arguments: dict) -> dict:
    """Call MCP tool via WebSocketConnector.

    Args:
        arguments: Tool arguments as dict

    Returns:
        Result dict with success, data, and metadata
    """
    if not ensure_mcp_use_installed():
        return {
            "success": False,
            "error": "Failed to install mcp-use package",
            "error_type": "DependencyError"
        }

    try:
        from mcp_use.client.connectors import WebSocketConnector
    except ImportError:
        return {
            "success": False,
            "error": "mcp-use WebSocketConnector import failed",
            "error_type": "DependencyError"
        }

    # Find server config
    ws_config = find_websocket_config(SERVER_PATTERN)
    if not ws_config:
        return {
            "success": False,
            "error": f"WebSocket MCP server matching '{SERVER_PATTERN}' not found. "
                     "Ensure server is configured with 'ws_url' in Claude Code.",
            "error_type": "ConfigurationError"
        }

    ws_url = ws_config.get("ws_url")
    headers = ws_config.get("headers", {})

    if not ws_url:
        return {
            "success": False,
            "error": "MCP server ws_url not found in config",
            "error_type": "ConfigurationError"
        }

    connector = None
    try:
        # Create WebSocketConnector and connect
        connector = WebSocketConnector(
            ws_url=ws_url,
            headers=headers
        )
        await connector.connect()

        # List available tools (useful for debugging)
        tools = await connector.list_tools()
        tool_names = [t.name for t in tools]

        if TOOL_NAME not in tool_names:
            return {
                "success": False,
                "error": f"Tool '{TOOL_NAME}' not found. Available: {tool_names}",
                "error_type": "ToolError"
            }

        # Call the tool
        result = await connector.call_tool(name=TOOL_NAME, arguments=arguments)

        if getattr(result, "isError", False):
            return {
                "success": False,
                "error": str(result.content),
                "error_type": "ToolError"
            }

        # Extract content
        if result.content:
            content_text = (
                result.content[0].text
                if hasattr(result.content[0], 'text')
                else str(result.content[0])
            )
            try:
                parsed = json.loads(content_text)
            except json.JSONDecodeError:
                parsed = content_text

            return {
                "success": True,
                "data": parsed,
                "metadata": {
                    "tool": TOOL_NAME,
                    "server": ws_config.get("name"),
                    "ws_url": ws_url,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }

        return {"success": True, "data": None, "metadata": {}}

    except ConnectionRefusedError:
        return {
            "success": False,
            "error": f"WebSocket connection refused at {ws_url}. Is the server running?",
            "error_type": "ConnectionError"
        }
    except TimeoutError:
        return {
            "success": False,
            "error": f"WebSocket connection timed out at {ws_url}",
            "error_type": "ConnectionError"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
    finally:
        if connector:
            try:
                await connector.disconnect()
            except Exception:
                pass


# ============================================================================
# CUSTOMIZE: CLI Arguments and Argument Mapping
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description=f"Call {TOOL_NAME} on {SERVER_PATTERN} MCP server (WebSocket)"
    )

    # Add your CLI arguments here
    # Example arguments (customize for your tool):
    parser.add_argument(
        "--message", "-m",
        required=True,
        help="Message to send"
    )
    parser.add_argument(
        "--channel", "-c",
        default="default",
        help="Channel to send to"
    )

    # Parse arguments
    args = parser.parse_args()

    # ========================================================================
    # CUSTOMIZE: Map CLI args to tool parameters
    # ========================================================================
    # Check your MCP tool's expected parameters and map accordingly
    tool_arguments = {
        "message": args.message,
        "channel": args.channel,
        # Add more parameter mappings as needed
    }

    # Call the tool
    result = asyncio.run(call_tool(tool_arguments))

    # Output result as JSON
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

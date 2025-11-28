#!/usr/bin/env python3
"""
Template MCP Stdio Connector Script

This is a template for creating new MCP stdio connector scripts.
Copy this file and customize for your target MCP server and tool.

Usage:
    cp template_stdio_connector.py new_server/new_tool.py
    # Then customize the marked sections below

Instructions:
    1. Update the docstring with your tool description
    2. Set SERVER_PATTERN to match your MCP server name in config
    3. Set TOOL_NAME to the specific tool you want to call
    4. Update CLI arguments as needed
    5. Map arguments to tool parameters in call_tool()

Key Difference from HTTP Connector:
    - HTTP: Connects to EXISTING running server
    - Stdio: SPAWNS a NEW server subprocess
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
# Example: "filesystem", "memory", "sqlite", "git"
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


def find_stdio_config(server_pattern: str) -> dict | None:
    """Find stdio MCP server config from Claude Code settings.

    Args:
        server_pattern: Lowercase pattern to match server name

    Returns:
        Dict with name, command, args, env if found, None otherwise
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
                        # MUST be stdio type for subprocess spawning
                        if server_config.get("type") == "stdio":
                            return {
                                "name": name,
                                "command": server_config.get("command", "npx"),
                                "args": server_config.get("args", []),
                                "env": server_config.get("env", {})
                            }
            except (json.JSONDecodeError, IOError):
                continue

    return None


async def call_tool(arguments: dict) -> dict:
    """Call MCP tool via StdioConnector.

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
        from mcp_use.client.connectors import StdioConnector
    except ImportError:
        return {
            "success": False,
            "error": "mcp-use StdioConnector import failed",
            "error_type": "DependencyError"
        }

    # Find server config
    stdio_config = find_stdio_config(SERVER_PATTERN)
    if not stdio_config:
        return {
            "success": False,
            "error": f"Stdio MCP server matching '{SERVER_PATTERN}' not found. "
                     "Ensure server is configured with type: 'stdio' in Claude Code.",
            "error_type": "ConfigurationError"
        }

    command = stdio_config.get("command")
    args = stdio_config.get("args", [])
    env = stdio_config.get("env", {})

    if not command:
        return {
            "success": False,
            "error": "MCP server command not found in config",
            "error_type": "ConfigurationError"
        }

    connector = None
    try:
        # Create StdioConnector and connect (spawns subprocess)
        connector = StdioConnector(
            command=command,
            args=args,
            env=env
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
                    "server": stdio_config.get("name"),
                    "command": command,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }

        return {"success": True, "data": None, "metadata": {}}

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
        description=f"Call {TOOL_NAME} on {SERVER_PATTERN} MCP server (stdio)"
    )

    # Add your CLI arguments here
    # Example arguments (customize for your tool):
    parser.add_argument(
        "--path", "-p",
        required=True,
        help="Path to operate on"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Recursive operation"
    )

    # Parse arguments
    args = parser.parse_args()

    # ========================================================================
    # CUSTOMIZE: Map CLI args to tool parameters
    # ========================================================================
    # Check your MCP tool's expected parameters and map accordingly
    tool_arguments = {
        "path": args.path,
        "recursive": args.recursive,
        # Add more parameter mappings as needed
    }

    # Call the tool
    result = asyncio.run(call_tool(tool_arguments))

    # Output result as JSON
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

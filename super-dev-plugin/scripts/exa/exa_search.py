#!/usr/bin/env python3
"""
Exa Web Search Script: Execute web searches using Exa MCP server.

Connects to the existing Exa MCP HTTP server configured in Claude Code.
Uses mcp-use's HttpConnector to connect to the running Exa MCP endpoint.

Usage:
    python3 exa_search.py --query "search terms" [--type auto|fast|deep] [--results 8]

Output:
    JSON formatted search results to stdout
"""

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


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


def find_exa_config() -> dict | None:
    """Find Exa MCP server config from Claude Code settings."""
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

                # Look for mcpServers section
                mcp_servers = config.get("mcpServers", {})

                # Find Exa server
                for name, server_config in mcp_servers.items():
                    if "exa" in name.lower():
                        # Check if it's HTTP type (required for connection)
                        if server_config.get("type") == "http":
                            return {
                                "name": name,
                                "url": server_config.get("url"),
                                "headers": server_config.get("headers", {})
                            }
            except (json.JSONDecodeError, IOError):
                continue

    return None


async def search_with_mcp(query: str, search_type: str, num_results: int, context_chars: int) -> dict:
    """Execute search using mcp-use HttpConnector."""
    if not ensure_mcp_use_installed():
        return {
            "success": False,
            "error": "Failed to install mcp-use package",
            "error_type": "DependencyError"
        }

    try:
        from mcp_use.client.connectors import HttpConnector
    except ImportError:
        return {
            "success": False,
            "error": "mcp-use HttpConnector import failed",
            "error_type": "DependencyError"
        }

    # Find Exa config from Claude Code settings
    exa_config = find_exa_config()
    if not exa_config:
        return {
            "success": False,
            "error": "Exa HTTP MCP server not found in Claude Code config. Make sure Exa MCP is configured with type: 'http'",
            "error_type": "ConfigurationError"
        }

    url = exa_config.get("url")
    headers = exa_config.get("headers", {})

    if not url:
        return {
            "success": False,
            "error": "Exa MCP server URL not found in config",
            "error_type": "ConfigurationError"
        }

    try:
        # Create HttpConnector to connect to existing Exa MCP server
        connector = HttpConnector(base_url=url, headers=headers)

        # Connect to the server
        await connector.connect()

        # List tools to find the search tool
        tools = await connector.list_tools()
        tool_names = [t.name for t in tools]

        # Find web search tool
        search_tool = None
        for name in ["web_search_exa", "search", "web_search"]:
            if name in tool_names:
                search_tool = name
                break

        if not search_tool:
            await connector.disconnect()
            return {
                "success": False,
                "error": f"Search tool not found. Available tools: {tool_names}",
                "error_type": "ToolError"
            }

        # Call the search tool
        result = await connector.call_tool(
            name=search_tool,
            arguments={
                "query": query,
                "type": search_type,
                "numResults": num_results,
                "contextMaxCharacters": context_chars
            }
        )

        # Disconnect after use
        await connector.disconnect()

        if getattr(result, "isError", False):
            return {
                "success": False,
                "error": str(result.content),
                "error_type": "ToolError"
            }

        if result.content:
            content_text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            try:
                parsed = json.loads(content_text)
            except json.JSONDecodeError:
                parsed = content_text

            return {
                "success": True,
                "query": query,
                "results": parsed,
                "metadata": {
                    "tool": search_tool,
                    "server": exa_config.get("name"),
                    "url": url,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }

        return {"success": True, "query": query, "results": []}

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def main():
    parser = argparse.ArgumentParser(
        description="Web search using Exa MCP server (connects to existing HTTP endpoint)"
    )
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--type", "-t", choices=["auto", "fast", "deep"], default="auto")
    parser.add_argument("--results", "-r", type=int, default=8)
    parser.add_argument("--context-chars", "-c", type=int, default=10000)

    args = parser.parse_args()
    result = asyncio.run(search_with_mcp(args.query, args.type, args.results, args.context_chars))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

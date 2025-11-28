#!/usr/bin/env python3
"""
Exa Web Search Script: Execute web searches using Exa MCP server.

This script connects to the Exa MCP server configured in Claude Code settings
and calls the web_search_exa tool via mcp-use client.

Usage:
    python3 exa_search.py --query "search terms" [--type auto|fast|deep] [--results 8]

Output:
    JSON formatted search results to stdout
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
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


def load_mcp_config() -> dict | None:
    """Load MCP server configuration from Claude Code settings."""
    config_paths = [
        Path.home() / ".claude.json",
        Path.home() / ".claude" / "settings.json",
        Path.home() / ".claude" / "settings.local.json",
        Path.cwd() / ".claude" / "settings.json",
        Path.cwd() / ".claude" / "settings.local.json",
        Path.cwd() / ".claude.json",
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text())
                mcp_servers = config.get("mcpServers", {})

                # Look for exa server config
                if "exa" in mcp_servers:
                    return {"mcpServers": {"exa": mcp_servers["exa"]}}

                # Also check for @anthropic/mcp-server-exa or similar names
                for name, server_config in mcp_servers.items():
                    if "exa" in name.lower():
                        return {"mcpServers": {name: server_config}}

            except (json.JSONDecodeError, KeyError, TypeError):
                continue

    return None


async def search_with_mcp(query: str, search_type: str, num_results: int, context_chars: int) -> dict:
    """Execute search using mcp-use client connection to Exa server."""
    if not ensure_mcp_use_installed():
        return {
            "success": False,
            "error": "Failed to install mcp-use package. Run manually: pip install mcp-use",
            "error_type": "DependencyError"
        }

    try:
        from mcp_use import MCPClient
    except ImportError:
        return {
            "success": False,
            "error": "mcp-use package import failed after installation. Please restart and try again.",
            "error_type": "DependencyError"
        }

    # Load MCP config from Claude Code settings
    mcp_config = load_mcp_config()
    if not mcp_config:
        return {
            "success": False,
            "error": "Exa MCP server not found in Claude Code config. Please configure it in ~/.claude.json or project settings.",
            "error_type": "ConfigurationError"
        }

    client = MCPClient.from_dict(mcp_config)
    server_name = list(mcp_config["mcpServers"].keys())[0]

    try:
        await client.create_all_sessions()
        session = client.get_session(server_name)

        if not session:
            return {
                "success": False,
                "error": f"Failed to create session for {server_name}",
                "error_type": "ConnectionError"
            }

        # Call the web_search_exa tool
        result = await session.call_tool(
            name="web_search_exa",
            arguments={
                "query": query,
                "type": search_type,
                "numResults": num_results,
                "contextMaxCharacters": context_chars
            }
        )

        if getattr(result, "isError", False):
            return {
                "success": False,
                "error": str(result.content),
                "error_type": "ToolError"
            }

        if result.content:
            content_text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])

            try:
                parsed_results = json.loads(content_text)
            except json.JSONDecodeError:
                parsed_results = content_text

            return {
                "success": True,
                "query": query,
                "results": parsed_results,
                "metadata": {
                    "tool": "web_search_exa",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "search_type": search_type,
                    "requested_results": num_results
                }
            }

        return {
            "success": True,
            "query": query,
            "results": [],
            "metadata": {
                "tool": "web_search_exa",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "note": "No results returned"
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
    finally:
        await client.close_all_sessions()


def main():
    parser = argparse.ArgumentParser(
        description="Execute web searches using Exa MCP server (reads config from Claude Code settings)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 exa_search.py --query "React hooks best practices 2025"
    python3 exa_search.py -q "Python async patterns" --type deep --results 15

Configuration:
    Reads Exa MCP server config from Claude Code settings:
    - ~/.claude.json
    - ~/.claude/settings.json
    - .claude/settings.local.json (project)
        """
    )
    parser.add_argument("--query", "-q", required=True, help="Search query string")
    parser.add_argument("--type", "-t", choices=["auto", "fast", "deep"], default="auto",
                        help="Search type: auto (balanced), fast (quick), deep (comprehensive)")
    parser.add_argument("--results", "-r", type=int, default=8, help="Number of results (default: 8)")
    parser.add_argument("--context-chars", "-c", type=int, default=10000, help="Max context characters (default: 10000)")

    args = parser.parse_args()

    result = asyncio.run(search_with_mcp(
        query=args.query,
        search_type=args.type,
        num_results=args.results,
        context_chars=args.context_chars
    ))

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Exa Code Context Script: Get code context using Exa MCP server.

This script connects to the Exa MCP server configured in Claude Code settings
and calls the get_code_context_exa tool via mcp-use client.

Usage:
    python3 exa_code.py --query "search query" [--tokens 5000]

Output:
    JSON formatted code context to stdout
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


async def get_code_context(query: str, tokens: int) -> dict:
    """Get code context using mcp-use client connection to Exa server."""
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

        # Call the get_code_context_exa tool
        result = await session.call_tool(
            name="get_code_context_exa",
            arguments={
                "query": query,
                "tokensNum": tokens
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

            return {
                "success": True,
                "query": query,
                "context": content_text,
                "metadata": {
                    "tool": "get_code_context_exa",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "requested_tokens": tokens
                }
            }

        return {
            "success": True,
            "query": query,
            "context": "",
            "metadata": {
                "tool": "get_code_context_exa",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "note": "No context returned"
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
        description="Get code context using Exa MCP server (reads config from Claude Code settings)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 exa_code.py --query "React useState hook examples"
    python3 exa_code.py -q "Next.js 15 server components" --tokens 8000

Configuration:
    Reads Exa MCP server config from Claude Code settings:
    - ~/.claude.json
    - ~/.claude/settings.json
    - .claude/settings.local.json (project)
        """
    )
    parser.add_argument("--query", "-q", required=True, help="Code-related search query")
    parser.add_argument("--tokens", "-t", type=int, default=5000,
                        help="Number of tokens to return (default: 5000, range: 1000-50000)")

    args = parser.parse_args()

    if args.tokens < 1000 or args.tokens > 50000:
        print(json.dumps({
            "success": False,
            "error": "tokens must be between 1000 and 50000",
            "error_type": "ValidationError"
        }, indent=2))
        sys.exit(1)

    result = asyncio.run(get_code_context(
        query=args.query,
        tokens=args.tokens
    ))

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

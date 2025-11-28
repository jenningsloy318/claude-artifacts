#!/usr/bin/env python3
"""
Exa Code Context Script: Get code context using Exa MCP server.

This script wraps the Exa MCP server's get_code_context_exa tool, allowing agents
to get relevant code documentation and examples by executing this script via Bash.

Uses mcp-use library for MCP client connection.
Based on the "Code Execution with MCP" pattern from Anthropic.

Usage:
    python3 exa_code.py --query "search query" [--tokens 5000]

Environment:
    EXA_API_KEY: Required API key for Exa service

Output:
    JSON formatted code context to stdout
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime


async def get_code_context(query: str, tokens: int) -> dict:
    """Get code context using mcp-use client connection to Exa server."""
    try:
        from mcp_use import MCPClient
    except ImportError:
        return {
            "success": False,
            "error": "mcp-use package not installed. Run: pip install mcp-use",
            "error_type": "DependencyError"
        }

    # Check for API key
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "EXA_API_KEY environment variable not set",
            "error_type": "ConfigurationError"
        }

    # MCP server configuration for Exa
    config = {
        "mcpServers": {
            "exa": {
                "command": "npx",
                "args": ["-y", "@anthropic/mcp-server-exa"],
                "env": {
                    "EXA_API_KEY": api_key
                }
            }
        }
    }

    client = MCPClient.from_dict(config)

    try:
        # Initialize session
        await client.create_all_sessions()
        session = client.get_session("exa")

        if not session:
            return {
                "success": False,
                "error": "Failed to create Exa MCP session",
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

        # Check for errors
        if getattr(result, "isError", False):
            return {
                "success": False,
                "error": str(result.content),
                "error_type": "ToolError"
            }

        # Parse the result content
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

    except FileNotFoundError:
        return {
            "success": False,
            "error": "npx not found. Ensure Node.js is installed.",
            "error_type": "DependencyError"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
    finally:
        # Clean up
        await client.close_all_sessions()


def main():
    parser = argparse.ArgumentParser(
        description="Get code context using Exa MCP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 exa_code.py --query "React useState hook examples"
    python3 exa_code.py -q "Next.js 15 server components" --tokens 8000

Environment Variables:
    EXA_API_KEY    Required API key for Exa service
        """
    )
    parser.add_argument(
        "--query", "-q",
        required=True,
        help="Code-related search query"
    )
    parser.add_argument(
        "--tokens", "-t",
        type=int,
        default=5000,
        help="Number of tokens to return (default: 5000, range: 1000-50000)"
    )

    args = parser.parse_args()

    # Validate tokens range
    if args.tokens < 1000 or args.tokens > 50000:
        print(json.dumps({
            "success": False,
            "error": "tokens must be between 1000 and 50000",
            "error_type": "ValidationError"
        }, indent=2))
        sys.exit(1)

    # Run the async function
    result = asyncio.run(get_code_context(
        query=args.query,
        tokens=args.tokens
    ))

    # Output JSON to stdout
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

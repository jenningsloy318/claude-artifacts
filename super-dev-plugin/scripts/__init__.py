"""
MCP HTTP Connector Scripts

This package provides executable scripts that connect to HTTP-based MCP servers
configured in Claude Code using mcp-use's HttpConnector.

Architecture:
    Agent (Bash) --> Script --> HttpConnector --> MCP HTTP Server
                       |
                       v
                 ~/.claude.json (config)

Key Requirement:
    Only works with HTTP-based MCP servers (type: "http").
    Stdio-based servers cannot be connected to externally.

Available Scripts:
    exa/exa_search.py  - Web search using Exa's web_search_exa tool
    exa/exa_code.py    - Code context using Exa's get_code_context_exa tool

Usage:
    # From command line
    python3 scripts/exa/exa_search.py --query "search terms" --results 10
    python3 scripts/exa/exa_code.py --query "code query" --tokens 5000

    # From agent via Bash
    result = bash("python3 scripts/exa/exa_search.py --query 'React hooks'")

Creating New Scripts:
    1. Copy template_connector.py to your new directory
    2. Set SERVER_PATTERN to match your MCP server name
    3. Set TOOL_NAME to the target tool
    4. Customize CLI arguments and argument mapping
    5. Test with sample queries

See specification/11-mcp-http-connector/01-specification.md for detailed specification.

Output Format:
    {
        "success": true,
        "data": { ... },
        "metadata": {
            "tool": "tool_name",
            "server": "server_name",
            "url": "https://...",
            "timestamp": "2025-11-28T03:30:00+00:00"
        }
    }
"""

__version__ = "1.0.0"

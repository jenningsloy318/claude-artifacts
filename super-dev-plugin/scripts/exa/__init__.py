"""
Exa MCP HTTP Connector Scripts

Scripts for connecting to Exa's HTTP MCP server (https://mcp.exa.ai/mcp).

Available Scripts:
    exa_search.py  - Web search using web_search_exa tool
    exa_code.py    - Code context using get_code_context_exa tool

Configuration:
    Scripts auto-discover Exa config from Claude Code settings.
    Expected config in ~/.claude.json or ~/.claude/settings.json:

    {
        "mcpServers": {
            "exa": {
                "type": "http",
                "url": "https://mcp.exa.ai/mcp",
                "headers": {
                    "EXA_API_KEY": "your-api-key"
                }
            }
        }
    }

Usage:
    # Web search
    python3 exa_search.py --query "search terms" --type auto --results 8

    # Code context
    python3 exa_code.py --query "code query" --tokens 5000

Output:
    JSON with success, data/results, and metadata fields.
"""

__version__ = "1.0.0"

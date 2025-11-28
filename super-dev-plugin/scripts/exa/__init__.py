"""
Exa MCP Scripts: Wrapper scripts for Exa MCP server tools.

This module provides executable scripts that connect to the Exa MCP server
and call its tools, allowing agents to perform searches via Bash execution.

Scripts:
    exa_search.py - Web search using web_search_exa tool
    exa_code.py   - Code context using get_code_context_exa tool

Usage:
    python3 -m super_dev_plugin.scripts.exa.exa_search --query "search terms"
    python3 -m super_dev_plugin.scripts.exa.exa_code --query "code query"
"""

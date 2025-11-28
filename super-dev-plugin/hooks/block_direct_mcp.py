#!/usr/bin/env python3
"""
PreToolUse Hook: Block direct MCP tool calls and enforce script usage.

This hook intercepts MCP tool calls and blocks them, requiring the use of
wrapper scripts instead. This ensures token-efficient output and consistent
formatting across all agents in the super-dev workflow.

Input (stdin): JSON with tool call details
  {
    "tool_name": "mcp__exa__web_search_exa",
    "tool_input": {...}
  }

Output (stderr): Error message explaining the violation
Exit codes:
  0 - Allow the tool call (for exceptions like mcp__time-mcp)
  2 - Block the tool call (for forbidden direct MCP calls)

Configuration:
  Add to .claude/settings.local.json:
  {
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "mcp__exa__.*|mcp__deepwiki__.*|mcp__context7__.*|mcp__github__search.*|mcp__github__get_file.*",
          "hooks": [
            {
              "type": "command",
              "command": "python3 super-dev-plugin/hooks/block_direct_mcp.py"
            }
          ]
        }
      ]
    }
  }
"""

import sys
import json

# ============================================================================
# Configuration
# ============================================================================

# MCP tools that are FORBIDDEN (must use scripts instead)
FORBIDDEN_TOOLS = {
    # Exa tools
    "mcp__exa__web_search_exa": "python3 super-dev-plugin/scripts/exa/exa_search.py",
    "mcp__exa__get_code_context_exa": "python3 super-dev-plugin/scripts/exa/exa_code.py",

    # DeepWiki tools
    "mcp__deepwiki__read_wiki_structure": "python3 super-dev-plugin/scripts/deepwiki/deepwiki_structure.py",
    "mcp__deepwiki__read_wiki_contents": "python3 super-dev-plugin/scripts/deepwiki/deepwiki_contents.py",
    "mcp__deepwiki__ask_question": "python3 super-dev-plugin/scripts/deepwiki/deepwiki_ask.py",

    # Context7 tools
    "mcp__context7__resolve-library-id": "python3 super-dev-plugin/scripts/context7/context7_resolve.py",
    "mcp__context7__get-library-docs": "python3 super-dev-plugin/scripts/context7/context7_docs.py",

    # GitHub tools (search and file access)
    "mcp__github__search_code": "python3 super-dev-plugin/scripts/github/github_search_code.py",
    "mcp__github__search_repositories": "python3 super-dev-plugin/scripts/github/github_search_repos.py",
    "mcp__github__get_file_contents": "python3 super-dev-plugin/scripts/github/github_file_contents.py",
}

# MCP tools that are ALLOWED (exceptions)
ALLOWED_TOOLS = {
    "mcp__time-mcp__current_time",  # No script wrapper available
}

# ============================================================================
# Main Logic
# ============================================================================

def main():
    try:
        # Read tool call info from stdin
        input_data = sys.stdin.read()
        if not input_data.strip():
            # No input, allow by default
            sys.exit(0)

        tool_info = json.loads(input_data)
        tool_name = tool_info.get("tool_name", "")

        # Check if tool is explicitly allowed
        if tool_name in ALLOWED_TOOLS:
            sys.exit(0)  # Allow

        # Check if tool is forbidden
        if tool_name in FORBIDDEN_TOOLS:
            script = FORBIDDEN_TOOLS[tool_name]

            # Print error message to stderr (visible to Claude)
            error_msg = f"""
⛔ BLOCKED: Direct MCP tool call detected!

Tool: {tool_name}

FORBIDDEN: Direct MCP tool calls are not allowed.
REQUIRED: Use the wrapper script instead:

  {script}

Why scripts?
- Token-efficient output formatting
- Consistent JSON response structure
- Automatic MCP config resolution
- Better error handling

See super-dev-plugin/scripts/README.md for usage details.
"""
            print(error_msg, file=sys.stderr)
            sys.exit(2)  # Block the tool call

        # Check for pattern matches (tools we might have missed)
        forbidden_prefixes = [
            "mcp__exa__",
            "mcp__deepwiki__",
            "mcp__context7__",
        ]

        for prefix in forbidden_prefixes:
            if tool_name.startswith(prefix):
                error_msg = f"""
⛔ BLOCKED: Direct MCP tool call detected!

Tool: {tool_name}

This MCP tool should be called via wrapper scripts.
Check super-dev-plugin/scripts/ for available wrappers.
"""
                print(error_msg, file=sys.stderr)
                sys.exit(2)  # Block

        # GitHub search/get patterns
        if tool_name.startswith("mcp__github__search") or tool_name.startswith("mcp__github__get_file"):
            error_msg = f"""
⛔ BLOCKED: Direct MCP tool call detected!

Tool: {tool_name}

Use the GitHub wrapper scripts instead:
- github_search_code.py
- github_search_repos.py
- github_file_contents.py

Check super-dev-plugin/scripts/github/ for details.
"""
            print(error_msg, file=sys.stderr)
            sys.exit(2)  # Block

        # Not a forbidden tool, allow it
        sys.exit(0)

    except json.JSONDecodeError:
        # Can't parse input, allow by default
        sys.exit(0)
    except Exception as e:
        # Unexpected error, log and allow
        print(f"[block_direct_mcp] Error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

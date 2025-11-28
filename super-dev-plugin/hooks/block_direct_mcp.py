#!/usr/bin/env python3
"""
PreToolUse Hook: Block direct MCP tool calls and redirect to scripts.

This hook intercepts MCP tool calls, blocks them, and provides the EXACT
script command to execute instead - with all arguments translated.

Input (stdin): JSON with tool call details
  {
    "tool_name": "mcp__exa__web_search_exa",
    "tool_input": {"query": "...", ...}
  }

Output (stderr): Error message with exact replacement command
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
import shlex

# ============================================================================
# Configuration: Tool -> Script mapping with argument translation
# ============================================================================

TOOL_TRANSLATIONS = {
    # Exa tools
    "mcp__exa__web_search_exa": {
        "script": "python3 super-dev-plugin/scripts/exa/exa_search.py",
        "args_map": {
            "query": "--query",
            "type": "--type",
            "numResults": "--results",
        }
    },
    "mcp__exa__get_code_context_exa": {
        "script": "python3 super-dev-plugin/scripts/exa/exa_code.py",
        "args_map": {
            "query": "--query",
            "tokensNum": "--tokens",
        }
    },

    # DeepWiki tools
    "mcp__deepwiki__read_wiki_structure": {
        "script": "python3 super-dev-plugin/scripts/deepwiki/deepwiki_structure.py",
        "args_map": {
            "repoName": "--repo",
        }
    },
    "mcp__deepwiki__read_wiki_contents": {
        "script": "python3 super-dev-plugin/scripts/deepwiki/deepwiki_contents.py",
        "args_map": {
            "repoName": "--repo",
        }
    },
    "mcp__deepwiki__ask_question": {
        "script": "python3 super-dev-plugin/scripts/deepwiki/deepwiki_ask.py",
        "args_map": {
            "repoName": "--repo",
            "question": "--question",
        }
    },

    # Context7 tools
    "mcp__context7__resolve-library-id": {
        "script": "python3 super-dev-plugin/scripts/context7/context7_resolve.py",
        "args_map": {
            "libraryName": "--library",
        }
    },
    "mcp__context7__get-library-docs": {
        "script": "python3 super-dev-plugin/scripts/context7/context7_docs.py",
        "args_map": {
            "context7CompatibleLibraryID": "--library-id",
            "topic": "--topic",
            "mode": "--mode",
            "page": "--page",
        }
    },

    # GitHub tools
    "mcp__github__search_code": {
        "script": "python3 super-dev-plugin/scripts/github/github_search_code.py",
        "args_map": {
            "query": "--query",
            "perPage": "--per-page",
            "page": "--page",
        }
    },
    "mcp__github__search_repositories": {
        "script": "python3 super-dev-plugin/scripts/github/github_search_repos.py",
        "args_map": {
            "query": "--query",
            "perPage": "--per-page",
            "page": "--page",
            "sort": "--sort",
            "order": "--order",
        }
    },
    "mcp__github__get_file_contents": {
        "script": "python3 super-dev-plugin/scripts/github/github_file_contents.py",
        "args_map": {
            "owner": "--owner",
            "repo": "--repo",
            "path": "--path",
            "ref": "--ref",
        }
    },
}

# MCP tools that are ALLOWED (exceptions)
ALLOWED_TOOLS = {
    "mcp__time-mcp__current_time",  # No script wrapper available
}

# ============================================================================
# Argument Translation
# ============================================================================

def translate_to_script_command(tool_name: str, tool_input: dict) -> str:
    """Translate MCP tool call to equivalent script command."""
    if tool_name not in TOOL_TRANSLATIONS:
        return None

    translation = TOOL_TRANSLATIONS[tool_name]
    script = translation["script"]
    args_map = translation["args_map"]

    # Build command arguments
    cmd_parts = [script]

    for mcp_arg, script_flag in args_map.items():
        if mcp_arg in tool_input and tool_input[mcp_arg] is not None:
            value = tool_input[mcp_arg]
            # Quote string values that might contain spaces
            if isinstance(value, str):
                cmd_parts.append(f'{script_flag} {shlex.quote(value)}')
            elif isinstance(value, bool):
                if value:
                    cmd_parts.append(script_flag)
            else:
                cmd_parts.append(f'{script_flag} {value}')

    return " ".join(cmd_parts)

# ============================================================================
# Main Logic
# ============================================================================

def main():
    try:
        # Read tool call info from stdin
        input_data = sys.stdin.read()
        if not input_data.strip():
            sys.exit(0)

        tool_info = json.loads(input_data)
        tool_name = tool_info.get("tool_name", "")
        tool_input = tool_info.get("tool_input", {})

        # Check if tool is explicitly allowed
        if tool_name in ALLOWED_TOOLS:
            sys.exit(0)

        # Check if tool has a translation
        if tool_name in TOOL_TRANSLATIONS:
            script_cmd = translate_to_script_command(tool_name, tool_input)

            error_msg = f"""
⛔ BLOCKED: Direct MCP tool call intercepted!

Tool: {tool_name}

🚫 Direct MCP calls are FORBIDDEN in super-dev workflow.

✅ EXECUTE THIS COMMAND INSTEAD:

```bash
{script_cmd}
```

⚠️ IMPORTANT: You MUST run the above Bash command immediately.
Do NOT try to call the MCP tool directly again.
"""
            print(error_msg, file=sys.stderr)
            sys.exit(2)

        # Check for pattern matches (tools we might have missed)
        forbidden_prefixes = [
            ("mcp__exa__", "super-dev-plugin/scripts/exa/"),
            ("mcp__deepwiki__", "super-dev-plugin/scripts/deepwiki/"),
            ("mcp__context7__", "super-dev-plugin/scripts/context7/"),
        ]

        for prefix, script_dir in forbidden_prefixes:
            if tool_name.startswith(prefix):
                error_msg = f"""
⛔ BLOCKED: Direct MCP tool call detected!

Tool: {tool_name}

🚫 Direct MCP calls are FORBIDDEN.
✅ Use scripts from: {script_dir}

Check available scripts and use Bash to execute them.
"""
                print(error_msg, file=sys.stderr)
                sys.exit(2)

        # GitHub patterns
        if tool_name.startswith("mcp__github__search") or tool_name.startswith("mcp__github__get_file"):
            error_msg = f"""
⛔ BLOCKED: Direct MCP tool call detected!

Tool: {tool_name}

🚫 Direct MCP calls are FORBIDDEN.
✅ Use scripts from: super-dev-plugin/scripts/github/

Available scripts:
- github_search_code.py
- github_search_repos.py
- github_file_contents.py
"""
            print(error_msg, file=sys.stderr)
            sys.exit(2)

        # Not a forbidden tool, allow it
        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        print(f"[block_direct_mcp] Error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Command Hook: Intercepts slash command execution and runs corresponding scripts.

This hook is triggered by PreToolUse when SlashCommand tool is used.
It detects context-keeper commands and runs the appropriate Python script.

Input (stdin): JSON with tool_name and tool_input
Output (stdout): Script output to inject into response
Exit codes:
  0 - Success
  1 - Not a context-keeper command (pass through)
"""

import sys
import json
import subprocess
from pathlib import Path


def read_hook_input() -> dict:
    """Read JSON input from stdin."""
    try:
        input_data = sys.stdin.read()
        return json.loads(input_data) if input_data.strip() else {}
    except json.JSONDecodeError:
        return {}


def get_scripts_dir() -> Path:
    """Get the scripts directory for this plugin."""
    # CLAUDE_PLUGIN_ROOT is set by Claude Code
    plugin_root = Path(__file__).parent.parent
    return plugin_root / "scripts"


# Map command names to script files
COMMAND_SCRIPTS = {
    "context-keeper:list-sessions": "list_sessions.py",
    "context-keeper:list-context": "list_context.py",
    "context-keeper:load-context": "load_context.py",
}


def main():
    hook_input = read_hook_input()

    # Check if this is a SlashCommand tool use
    tool_name = hook_input.get("tool_name", "")
    if tool_name != "SlashCommand":
        # Not a slash command, exit with code 1 to pass through
        sys.exit(1)

    # Get the command being invoked
    tool_input = hook_input.get("tool_input", {})
    command = tool_input.get("command", "")

    # Extract command name (e.g., "/context-keeper:load-context arg" -> "context-keeper:load-context")
    command_parts = command.lstrip("/").split()
    command_name = command_parts[0] if command_parts else ""
    command_args = command_parts[1:] if len(command_parts) > 1 else []

    # Check if this is one of our commands
    if command_name not in COMMAND_SCRIPTS:
        # Not our command, pass through
        sys.exit(1)

    # Get the script to run
    script_name = COMMAND_SCRIPTS[command_name]
    scripts_dir = get_scripts_dir()
    script_path = scripts_dir / script_name

    if not script_path.exists():
        print(f"Error: Script not found: {script_path}", file=sys.stderr)
        sys.exit(1)

    # Run the script with arguments
    try:
        cmd = ["python3", str(script_path)] + command_args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=hook_input.get("cwd", str(Path.cwd()))
        )

        # Output the script result
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        sys.exit(result.returncode)

    except subprocess.TimeoutExpired:
        print(f"Error: Script timed out: {script_name}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running script: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

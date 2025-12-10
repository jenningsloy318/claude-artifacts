#!/usr/bin/env python3
"""
Save Thread Script: Persists full Claude Code session threads at session end.

This script is designed to be called when a Claude Code session ends.
It uses the thread_persist MCP tool from nowledge to save the complete conversation thread.

Usage:
  python save_thread.py --session-id <id> --project-path <path> --summary <text>

Nowledge Integration:
- At session end: Saves full thread using thread_persist MCP tool

Exit codes:
  0 - Success
  1 - Error occurred

Environment variables:
  None required
"""

import sys
import json
import os
import argparse
import logging
from pathlib import Path
from mcp_use.client.connectors import HttpConnector



def parse_arguments():
    """Parse command line arguments (optional overrides)."""
    parser = argparse.ArgumentParser(
        description="Save Claude Code session thread to nowledge"
    )
    parser.add_argument("--session-id", help="Session ID")
    parser.add_argument("--project-path", help="Project path")
    parser.add_argument("--summary", default="", help="Summary")
    parser.add_argument(
        "--persist-mode",
        default="current",
        choices=["current", "all"],
        help="Persist mode"
    )
    return parser.parse_args()



def find_mcp_config(server_pattern: str) -> dict | None:
    """Find MCP server config from Claude Code settings.

    Args:
        server_pattern: Lowercase pattern to match server name

    Returns:
        Dict with name, url, headers if found, None otherwise
    """
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
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                mcp_servers = config.get("mcpServers", {})

                for name, server_config in mcp_servers.items():
                    if server_pattern in name.lower():
                        # Handle different URL field names
                        url = server_config.get("url") or server_config.get("httpUrl")

                        # Substitute environment variables in headers
                        headers = server_config.get("headers", {})
                        processed_headers = {}
                        for key, value in headers.items():
                            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                                env_var = value[2:-1]
                                env_value = os.getenv(env_var)
                                if env_value:
                                    # For Authorization headers, ensure proper format
                                    if key.lower() == "authorization" and not env_value.startswith("Bearer "):
                                        processed_headers[key] = f"Bearer {env_value}"
                                    else:
                                        processed_headers[key] = env_value
                            else:
                                processed_headers[key] = value

                        if url:
                            return {
                                "name": name,
                                "url": url,
                                "headers": processed_headers
                            }
            except (json.JSONDecodeError, IOError):
                continue

    return None

async def persist_thread_to_nowledge(session_id: str, project_path: str, summary: str, persist_mode: str = "current") -> bool:
    """Persist thread to nowledge using thread_persist MCP tool.

    Args:
        session_id: Session ID
        project_path: Project working directory path
        summary: Brief session summary
        persist_mode: 'current' (most recent) or 'all' (all sessions)

    Returns:
        True if successful, False otherwise
    """
    # Find nowledge MCP configuration
    NOWLEDGE_SERVER_PATTERN = "nowledge-mem"
    mcp_config = find_mcp_config(NOWLEDGE_SERVER_PATTERN)

    if not mcp_config:
        logging.error("[save-thread] Nowledge MCP server not found in Claude settings")
        return False

    logging.info(f"[save-thread] Connecting to nowledge MCP server: {mcp_config['name']}")
    logging.info(f"   URL: {mcp_config['url']}")

    connector = None
    try:
        # Create HttpConnector and connect
        connector = HttpConnector(base_url=mcp_config['url'], headers=mcp_config['headers'])
        await connector.connect()

        # List available tools
        tools = await connector.list_tools()
        tool_names = [t.name for t in tools]
        logging.info(f"[save-thread] Available tools: {tool_names}")

        # Check if thread_persist is available
        if "thread_persist" not in tool_names:
            logging.error("[save-thread] thread_persist tool not found")
            return False

        # Call thread_persist tool
        logging.info(f"[save-thread] Calling thread_persist for session {session_id[:8]}...")

        arguments = {
            "client": "claude-code",
            "project_path": project_path,
            "persist_mode": persist_mode
        }

        # Add optional parameters if provided
        if summary:
            arguments["summary"] = summary

        result = await connector.call_tool(
            name="thread_persist",
            arguments=arguments
        )

        # Check result
        if hasattr(result, 'isError') and result.isError:
            logging.error(f"[save-thread] thread_persist failed: {result.content}")
            return False

        if result.content:
            content_text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            logging.info("[save-thread] Thread persisted successfully!")
            logging.info(f"   Result: {content_text[:200]}...")
            return True

        logging.info("[save-thread] Thread persisted successfully!")
        return True

    except Exception as e:
        logging.error(f"[save-thread] Error persisting thread: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False

    finally:
        if connector:
            try:
                await connector.disconnect()
                logging.info("[save-thread] Disconnected from nowledge MCP server")
            except:
                pass


def main():
    """Main execution function."""
    # Configure logging to stderr
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
        #    logging.FileHandler('/tmp/context-keeper-thread-persist.log'),
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(sys.stderr)
        ]
    )
        
    logging.info("\n" + "=" * 60)
    logging.info("[save-thread] SessionEnd Hook Running...")
    logging.info("=" * 60)

    try:
        # 1. Try to read from stdin (Hook mode)
        try:
             # Check if stdin has data
             if not sys.stdin.isatty():
                 stdin_content = sys.stdin.read()
                 hook_input = json.loads(stdin_content) if stdin_content else {}
             else:
                 hook_input = {}
        except Exception:
             hook_input = {}

        # 2. Parse args (CLI mode overrides)
        args = parse_arguments()

        # 3. Resolve final values (Args > Stdin)
        session_id = args.session_id or hook_input.get("session_id")
        project_path = args.project_path or hook_input.get("cwd")
        # transcript_path = hook_input.get("transcript_path") # Not used anymore
        
        # Validation
        if not session_id or not project_path:
            logging.error("Missing required session_id or project_path (cwd)")
            logging.error(f"Stdin had: session_id={bool(hook_input.get('session_id'))}, cwd={bool(hook_input.get('cwd'))}")
            logging.error(f"Args had: session_id={bool(args.session_id)}, project_path={bool(args.project_path)}")
            sys.exit(1)

        summary = args.summary 
        persist_mode = args.persist_mode

        # Processing session (No incremental logic anymore)
        logging.info(f"[save-thread] Processing session {session_id[:8]}...")
        logging.info(f"[save-thread] Project: {project_path}")


        # Persist thread to nowledge
        logging.info("[save-thread] Connecting to nowledge...")

        import asyncio
        success = asyncio.run(persist_thread_to_nowledge(
            session_id,
            project_path,
            summary,
            persist_mode
        ))

        if success:
            logging.info("[save-thread] Session thread persisted successfully!")
            logging.info("=" * 60 + "\n")
            sys.exit(0)
        else:
            logging.error("[save-thread] Failed to persist thread to nowledge")
            logging.info("=" * 60 + "\n")
            sys.exit(1)

    except Exception as e:
        logging.error(f"[save-thread] Unexpected error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        logging.info("=" * 60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
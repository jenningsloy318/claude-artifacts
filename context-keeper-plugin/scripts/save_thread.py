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

def get_memories_dir(project_path: str) -> Path:
    """
    Get the directory where memories are stored.
    Tries project-local defaults first, acts as a fallback or standard getter.
    """
    # 1. Try local .claude/memories in the project
    if project_path:
         local_memories = Path(project_path) / ".claude" / "memories"
         if local_memories.exists():
             return local_memories
             
    # 2. Try global ~/.claude/memories (standard location)
    global_memories = Path.home() / ".claude" / "memories"
    return global_memories

def get_last_compact_time(session_id: str, project_path: str = None, transcript_path: str = None) -> str | None:
    """
    Get the timestamp (event_end) of the last compaction for this session.
    
    Strategy:
    1. Scan the transcript file for 'compact_boundary' events (most reliable).
    2. Fallback to local metadata.json if transcript scan fails.
    """
    # 1. Try scanning transcript_path if provided
    if transcript_path and os.path.exists(transcript_path):
        try:
            found_timestamps = []
            with open(transcript_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Check for system compact event
                    if '"subtype":"compact_boundary"' in line or '"subtype": "compact_boundary"' in line:
                         try:
                             data = json.loads(line)
                             if data.get("timestamp"):
                                 found_timestamps.append(data.get("timestamp"))
                         except json.JSONDecodeError:
                             pass
                    # Check for stdout marker (fallback)
                    elif "Compacted" in line and "<local-command-stdout>" in line:
                        try:
                             data = json.loads(line)
                             if data.get("timestamp"):
                                 found_timestamps.append(data.get("timestamp"))
                        except json.JSONDecodeError:
                             pass
            
            if found_timestamps:
                found_timestamps.sort(reverse=True)
                return found_timestamps[0]
                
        except Exception as e:
            logging.warning(f"Failed to scan transcript for compaction time: {e}")

    # 2. Try local metadata first (fastest)
    try:
        memories_dir = get_memories_dir(project_path)
        latest_meta_path = memories_dir / session_id / "latest" / "metadata.json"
        
        if latest_meta_path.exists():
            meta = json.loads(latest_meta_path.read_text(encoding='utf-8'))
            return meta.get("event_end") or meta.get("timestamp")
    except Exception as e:
        logging.warning(f"Failed to read last compaction time locally: {e}")
        
    return None

def get_transcript_times(transcript_path: str) -> tuple[str | None, str | None]:
    """
    Scan transcript for the first and last message timestamps.
    Returns (start_time, end_time).
    """
    start_time = None
    end_time = None
    
    if not transcript_path or not os.path.exists(transcript_path):
        return None, None

    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    ts = data.get("created_at") or data.get("timestamp")
                    # Check nested message
                    if not ts and "message" in data and isinstance(data["message"], dict):
                        ts = data["message"].get("created_at") or data["message"].get("timestamp")
                        
                    if ts:
                        if start_time is None or ts < start_time:
                            start_time = ts
                        if end_time is None or ts > end_time:
                            end_time = ts
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logging.warning(f"Failed to scan transcript times: {e}")

    return start_time, end_time
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
        print(f"❌ [save-thread] Nowledge MCP server not found in Claude settings", file=sys.stderr)
        return False

    print(f"📡 [save-thread] Connecting to nowledge MCP server: {mcp_config['name']}", file=sys.stderr)
    print(f"   URL: {mcp_config['url']}", file=sys.stderr)

    connector = None
    try:
        # Create HttpConnector and connect
        connector = HttpConnector(base_url=mcp_config['url'], headers=mcp_config['headers'])
        await connector.connect()

        # List available tools
        tools = await connector.list_tools()
        tool_names = [t.name for t in tools]
        print(f"🔧 [save-thread] Available tools: {tool_names}", file=sys.stderr)

        # Check if thread_persist is available
        if "thread_persist" not in tool_names:
            print(f"❌ [save-thread] thread_persist tool not found", file=sys.stderr)
            return False

        # Call thread_persist tool
        print(f"💾 [save-thread] Calling thread_persist for session {session_id[:8]}...", file=sys.stderr)

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
            print(f"❌ [save-thread] thread_persist failed: {result.content}", file=sys.stderr)
            return False

        if result.content:
            content_text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            print(f"✅ [save-thread] Thread persisted successfully!", file=sys.stderr)
            print(f"   Result: {content_text[:200]}...", file=sys.stderr)
            return True

        print(f"✅ [save-thread] Thread persisted successfully!", file=sys.stderr)
        return True

    except Exception as e:
        print(f"❌ [save-thread] Error persisting thread: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

    finally:
        if connector:
            try:
                await connector.disconnect()
                print("🔌 [save-thread] Disconnected from nowledge MCP server", file=sys.stderr)
            except:
                pass


def main():
    """Main execution function."""
    # Configure logging to stderr
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Also add stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logging.getLogger().addHandler(stdout_handler)
    
    print("\n" + "=" * 60, file=sys.stderr)
    print("🔄 [save-thread] SessionEnd Hook Running...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    try:
        # 1. Try to read from stdin (Hook mode)
        hook_input = json.loads(sys.stdin.read())
        # 2. Parse args (CLI mode overrides)
        args = parse_arguments()

        # 3. Resolve final values (Args > Stdin)
        session_id = args.session_id or hook_input.get("session_id")
        project_path = args.project_path or hook_input.get("cwd")
        transcript_path = hook_input.get("transcript_path")
        
        # Validation
        if not session_id or not project_path:
            logging.error("Missing required session_id or project_path (cwd)")
            logging.error(f"Stdin had: session_id={bool(hook_input.get('session_id'))}, cwd={bool(hook_input.get('cwd'))}")
            logging.error(f"Args had: session_id={bool(args.session_id)}, project_path={bool(args.project_path)}")
            sys.exit(1)

        summary = args.summary 
        persist_mode = args.persist_mode

        # Incremental Logic: Enhance summary with time range
        try:
            start_time = get_last_compact_time(session_id, project_path, transcript_path)
            _, end_time = get_transcript_times(transcript_path) # We only care about end_time of current session
            
            if start_time and end_time:
                time_info = f" [Incremental Session: {start_time} to {end_time}]"
                summary = (summary or "") + time_info
                print(f"🔄 [save-thread] Identified incremental range: {start_time} -> {end_time}", file=sys.stderr)
            elif end_time:
                # First run or no compaction found
                time_info = f" [Session End: {end_time}]"
                summary = (summary or "") + time_info
        except Exception as e:
            logging.warning(f"Failed to calculate incremental times: {e}")

        print(f"📋 [save-thread] Processing session {session_id[:8]}...", file=sys.stderr)
        print(f"📁 [save-thread] Project: {project_path}", file=sys.stderr)

        # Persist thread to nowledge
        print("☁️  [save-thread] Connecting to nowledge...", file=sys.stderr)

        import asyncio
        success = asyncio.run(persist_thread_to_nowledge(
            session_id,
            project_path,
            summary,
            persist_mode
        ))

        if success:
            print("✅ [save-thread] Session thread persisted successfully!", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            sys.exit(0)
        else:
            print("❌ [save-thread] Failed to persist thread to nowledge", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"❌ [save-thread] Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        print("=" * 60 + "\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
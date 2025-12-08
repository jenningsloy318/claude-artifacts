#!/usr/bin/env python3
"""
List Context Script: List all saved contexts, optionally filtered by session ID.

Uses jq subprocess for efficient extraction, falls back to full JSON parsing.
"""

import sys
import json
import subprocess
from pathlib import Path


def get_memories_dir() -> Path:
    """Get the memories directory for the current project."""
    cwd = Path.cwd()
    return cwd / ".claude" / "memories"


def load_index_with_jq(index_path: Path, session_filter: str = None) -> list:
    """Load memories using jq for efficiency."""
    try:
        if session_filter:
            # Filter by session_id prefix
            jq_query = f'.memories | map(select(.session_id | startswith("{session_filter}"))) | map({{session_id, timestamp, created_at, trigger, message_count, memory_path}})'
        else:
            jq_query = '.memories | map({session_id, timestamp, created_at, trigger, message_count, memory_path})'

        result = subprocess.run(
            ['jq', '-c', jq_query],
            stdin=open(index_path, 'r'),
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError, json.JSONDecodeError):
        pass
    return None


def load_index_fallback(index_path: Path, session_filter: str = None) -> list:
    """Fallback: load full index.json and filter."""
    try:
        index = json.loads(index_path.read_text(encoding='utf-8'))
        memories = index.get("memories", [])
        if session_filter:
            memories = [s for s in memories if s.get("session_id", "").startswith(session_filter)]
        return memories
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def format_timestamp(created_at: str) -> str:
    """Format ISO timestamp to readable format."""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return created_at[:16] if created_at else "unknown"


def list_all_contexts(memories: list):
    """List all contexts in a table."""
    print("## All Saved Contexts\n")
    print("| # | Session ID | Timestamp | Trigger | Messages |")
    print("|---|------------|-----------|---------|----------|")

    for i, s in enumerate(memories, 1):
        sid = s.get("session_id", "unknown")
        short_sid = f"{sid[:8]}..." if len(sid) > 8 else sid
        ts = format_timestamp(s.get("created_at", ""))
        trigger = s.get("trigger", "-")
        msgs = s.get("message_count", 0)
        print(f"| {i} | {short_sid} | {ts} | {trigger} | {msgs} |")

    session_ids = set(s.get("session_id") for s in memories)
    print(f"\nTotal: {len(memories)} context memories across {len(session_ids)} sessions")
    print("\nUse `/context-keeper:load-context <session-id>` to load a specific context.")
    print("Use `/context-keeper:list-context <session-id>` to see details for one session.")


def list_session_contexts(memories: list, session_filter: str):
    """List detailed contexts for a specific session."""
    if not memories:
        print(f"No contexts found for session '{session_filter}'.")
        return

    full_sid = memories[0].get("session_id", session_filter)
    print(f"## Context History for Session {full_sid[:16]}...\n")

    for i, s in enumerate(memories, 1):
        ts = format_timestamp(s.get("created_at", ""))
        print(f"### Compaction {i}: {ts}")
        print(f"- **Trigger:** {s.get('trigger', '-')}")
        print(f"- **Messages:** {s.get('message_count', 0)}")
        print(f"- **Summary Path:** {s.get('memory_path', '-')}")
        print()

    print("Would you like me to load one of these contexts?")


def main():
    memories_dir = get_memories_dir()
    index_path = memories_dir / "index.json"

    if not index_path.exists():
        print("No context memories found. Run `/compact` to create your first memory.")
        return

    # Get optional session filter from args
    session_filter = sys.argv[1] if len(sys.argv) > 1 else None

    # Try jq first, then fallback
    memories = load_index_with_jq(index_path, session_filter)
    if memories is None:
        memories = load_index_fallback(index_path, session_filter)

    if not memories:
        if session_filter:
            print(f"No contexts found for session '{session_filter}'.")
        else:
            print("No context memories found. Run `/compact` to create your first memory.")
        return

    if session_filter:
        list_session_contexts(memories, session_filter)
    else:
        list_all_contexts(memories)


if __name__ == "__main__":
    main()

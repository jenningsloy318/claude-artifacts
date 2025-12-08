#!/usr/bin/env python3
"""
List Sessions Script: Efficiently list all stored sessions from index.json.

Uses jq subprocess for efficient extraction, falls back to full JSON parsing.
"""

import sys
import json
import subprocess
from pathlib import Path
from collections import defaultdict


def get_memories_dir() -> Path:
    """Get the memories directory for the current project."""
    cwd = Path.cwd()
    return cwd / ".claude" / "memories"


def load_index_with_jq(index_path: Path) -> list:
    """Load memories using jq for efficiency."""
    try:
        # Extract only needed fields: session_id, timestamp, created_at, trigger, project, message_count
        jq_query = '.memories | map({session_id, timestamp, created_at, trigger, project, message_count})'
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


def load_index_fallback(index_path: Path) -> list:
    """Fallback: load full index.json."""
    try:
        index = json.loads(index_path.read_text(encoding='utf-8'))
        return index.get("memories", [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def format_timestamp(created_at: str) -> str:
    """Format ISO timestamp to readable format."""
    try:
        # Parse ISO format and format nicely
        from datetime import datetime
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return created_at[:16] if created_at else "unknown"


def main():
    memories_dir = get_memories_dir()
    index_path = memories_dir / "index.json"

    if not index_path.exists():
        print("No sessions found. Context memories are created automatically when you run `/compact`.")
        return

    # Try jq first, then fallback
    memories = load_index_with_jq(index_path)
    if memories is None:
        memories = load_index_fallback(index_path)

    if not memories:
        print("No sessions recorded yet. Your first context will be saved on the next compaction.")
        return

    # Group by session_id
    sessions = defaultdict(lambda: {
        "compaction_count": 0,
        "latest_timestamp": None,
        "latest_created": "",
        "project": "",
        "total_messages": 0
    })

    for memory in memories:
        sid = memory.get("session_id", "unknown")
        sessions[sid]["compaction_count"] += 1
        sessions[sid]["total_messages"] += memory.get("message_count", 0)
        sessions[sid]["project"] = memory.get("project", "")

        created = memory.get("created_at", "")
        if not sessions[sid]["latest_created"] or created > sessions[sid]["latest_created"]:
            sessions[sid]["latest_created"] = created
            sessions[sid]["latest_timestamp"] = format_timestamp(created)

    # Sort by latest activity
    sorted_sessions = sorted(
        sessions.items(),
        key=lambda x: x[1]["latest_created"],
        reverse=True
    )

    # Output markdown table
    print("## Stored Sessions\n")
    print("| # | Session ID | Compactions | Latest Activity | Project | Messages |")
    print("|---|------------|-------------|-----------------|---------|----------|")

    for i, (sid, data) in enumerate(sorted_sessions, 1):
        short_sid = f"{sid[:8]}..." if len(sid) > 8 else sid
        project = Path(data["project"]).name if data["project"] else "-"
        print(f"| {i} | {short_sid} | {data['compaction_count']} | {data['latest_timestamp']} | {project} | {data['total_messages']} |")

    print(f"\n**Total:** {len(sessions)} sessions with {len(memories)} context memories")
    print("\n### Quick Actions")
    print("- Use `/context-keeper:list-context <session-id>` to see all contexts for a session")
    print("- Use `/context-keeper:load-context <session-id>` to load the latest context from a session")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Load Context Script: Load a specific context memory by session ID or timestamp.

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


def load_latest_with_jq(index_path: Path) -> dict:
    """Load the latest memory entry using jq."""
    try:
        result = subprocess.run(
            ['jq', '-c', '.memories[0]'],
            stdin=open(index_path, 'r'),
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip() and result.stdout.strip() != 'null':
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError, json.JSONDecodeError):
        pass
    return None


def find_by_identifier_with_jq(index_path: Path, identifier: str) -> dict:
    """Find a memory by session_id or timestamp prefix using jq."""
    try:
        # Search by session_id prefix or timestamp
        jq_query = f'.memories | map(select(.session_id | startswith("{identifier}")) // select(.timestamp | startswith("{identifier}"))) | .[0]'
        result = subprocess.run(
            ['jq', '-c', jq_query],
            stdin=open(index_path, 'r'),
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip() and result.stdout.strip() != 'null':
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
        from datetime import datetime
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return created_at[:19] if created_at else "unknown"


def main():
    memories_dir = get_memories_dir()
    index_path = memories_dir / "index.json"

    if not memories_dir.exists() or not index_path.exists():
        print("No context memories found. Run `/compact` to create your first memory.")
        return

    # Get optional identifier from args
    identifier = sys.argv[1] if len(sys.argv) > 1 else None

    entry = None

    if identifier:
        # Try jq first
        entry = find_by_identifier_with_jq(index_path, identifier)
        if entry is None:
            # Fallback
            memories = load_index_fallback(index_path)
            for s in memories:
                if s.get("session_id", "").startswith(identifier) or s.get("timestamp", "").startswith(identifier):
                    entry = s
                    break
    else:
        # Load latest
        entry = load_latest_with_jq(index_path)
        if entry is None:
            memories = load_index_fallback(index_path)
            entry = memories[0] if memories else None

    if not entry:
        if identifier:
            print(f"No context found for '{identifier}'.")
            print("\nAvailable contexts:")
            memories = load_index_fallback(index_path)
            for s in memories[:5]:
                sid = s.get("session_id", "unknown")[:8]
                ts = format_timestamp(s.get("created_at", ""))
                print(f"  - [{sid}...] {ts}")
        else:
            print("No context memories found.")
        return

    # Load the actual memory file
    memory_path = memories_dir / entry.get("memory_path", "")
    if not memory_path.exists():
        print(f"Memory file not found: {memory_path}")
        return

    # Read memory as JSON
    try:
        memory_data = json.loads(memory_path.read_text(encoding='utf-8'))
        memory_content = memory_data.get('content', '')
    except (json.JSONDecodeError, FileNotFoundError):
        memory_content = memory_path.read_text(encoding='utf-8')  # Fallback for old .md files

    # Display the context
    print("## Context Memory Loaded\n")
    print(f"**Session ID:** {entry.get('session_id', 'unknown')}")
    print(f"**Created:** {format_timestamp(entry.get('created_at', ''))}")
    print(f"**Trigger:** {entry.get('trigger', '-')}")
    print(f"**Messages:** {entry.get('message_count', 0)}")
    print()
    print("---")
    print()
    print(memory_content)
    print()
    print("---")
    print("Would you like me to use this context for our conversation?")


if __name__ == "__main__":
    main()

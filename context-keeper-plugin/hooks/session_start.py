#!/usr/bin/env python3
"""
SessionStart Hook: Reloads latest session memory into context after compaction.

This hook triggers when a session starts or resumes (including after compaction).
It reads the most recent memory and outputs it to stdout, which Claude uses as context.

Input (stdin): JSON with session metadata
Output (stdout): Context to inject (becomes system context)
Exit codes:
  0 - Success (stdout becomes context)
  1 - Non-blocking error

Environment variables:
  None required
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


def read_hook_input() -> dict:
    """Read JSON input from stdin."""
    try:
        input_data = sys.stdin.read()
        return json.loads(input_data) if input_data.strip() else {}
    except json.JSONDecodeError:
        return {}


def get_memories_dir(project_path: str) -> Path:
    """Get the memories directory for the project."""
    return Path(project_path) / ".claude" / "memories"


def load_latest_memory(project_path: str, session_id: str = None) -> tuple[str, dict]:
    """
    Load the most recent memory for context injection.

    Returns:
        tuple: (memory_content, metadata) or (None, None) if not found
    """
    memories_dir = get_memories_dir(project_path)

    if not memories_dir.exists():
        return None, None

    # Try to load from specific session if provided
    if session_id:
        session_dir = memories_dir / session_id
        if session_dir.exists():
            latest_link = session_dir / "latest"
            if latest_link.exists():
                # Resolve symlink
                if latest_link.is_symlink():
                    target = session_dir / latest_link.resolve().name
                else:
                    target = latest_link

                memory_path = target / "memory.json" if target.is_dir() else None
                metadata_path = target / "metadata.json" if target.is_dir() else None

                if memory_path and memory_path.exists():
                    try:
                        memory_data = json.loads(memory_path.read_text(encoding='utf-8'))
                        memory = memory_data.get('content', '')
                    except json.JSONDecodeError:
                        # Fallback for old .md files
                        memory_path_old = target / "memory.md"
                        if memory_path_old.exists():
                            memory = memory_path_old.read_text(encoding='utf-8')
                        else:
                            memory = ""
                    metadata = {}
                    if metadata_path and metadata_path.exists():
                        try:
                            metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
                        except json.JSONDecodeError:
                            pass
                    return memory, metadata

    # Fallback: Load from index (most recent across all sessions)
    index_path = memories_dir / "index.json"
    if not index_path.exists():
        return None, None

    # Try using jq for efficient extraction (only reads first entry)
    latest = None
    try:
        result = subprocess.run(
            ['jq', '-r', '.memories[0]'],
            stdin=open(index_path, 'r'),
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip() and result.stdout.strip() != 'null':
            latest = json.loads(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        # jq not available or failed, fall back to full JSON parsing
        pass

    # Fallback: Read full JSON if jq failed
    if latest is None:
        try:
            index = json.loads(index_path.read_text(encoding='utf-8'))
            memories = index.get("memories", [])
            if not memories:
                return None, None
            latest = memories[0]
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"[context-keeper] Error: Failed to load from index: {e}", file=sys.stderr)
            return None, None

    try:
        memory_path = memories_dir / latest["memory_path"]
        if memory_path.exists():
            memory = memory_path.read_text(encoding='utf-8')
            return memory, latest
    except (KeyError, TypeError) as e:
        print(f"[context-keeper] Error: Invalid index entry: {e}", file=sys.stderr)

    return None, None


def format_context(memory: str, metadata: dict, source: str, permission_mode: str = "default") -> str:
    """Format memory for context injection."""

    timestamp = metadata.get('timestamp', metadata.get('created_at', 'unknown'))
    session_id = metadata.get('session_id', 'unknown')
    trigger = metadata.get('trigger', 'unknown')
    message_count = metadata.get('message_count', 0)

    # Create context wrapper
    context = f"""<previous-session-context>
## Session Continuity Notice

This context was automatically loaded from a previous session memory.
- **Previous Session ID:** {session_id[:16]}...
- **Summary Created:** {timestamp}
- **Compaction Trigger:** {trigger}
- **Message Count:** {message_count}
- **Reload Source:** {source}
- **Permission Mode:** {permission_mode}

---

{memory}

---

*Use this context to maintain continuity with the previous conversation. The above memory captures what was discussed and accomplished before context compaction.*
</previous-session-context>"""

    return context


def main():
    # Print visible banner to stderr
    print("\n" + "=" * 60, file=sys.stderr)
    print("🔄 [context-keeper] Session Start Hook Running...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    try:
        # Read input from Claude Code
        hook_input = read_hook_input()

        # Extract session information (all available fields)
        session_id = hook_input.get("session_id", "")
        transcript_path = hook_input.get("transcript_path", "")
        permission_mode = hook_input.get("permission_mode", "default")
        hook_event_name = hook_input.get("hook_event_name", "SessionStart")
        source = hook_input.get("source", "unknown")  # startup, resume, clear, compact
        cwd = hook_input.get("cwd", "")

        print(f"📋 [context-keeper] Source: {source}, Permission: {permission_mode}", file=sys.stderr)

        # Only inject context on resume (after compaction) or compact
        # Skip if this is a clear event (user explicitly cleared)
        if source == "clear":
            print("ℹ️  [context-keeper] Skipping context injection (clear event)", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            sys.exit(0)

        # Skip on fresh startup - only load context on resume/compact
        if source == "startup":
            print("ℹ️  [context-keeper] Skipping context injection (fresh startup)", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            sys.exit(0)

        if not cwd:
            print("ℹ️  [context-keeper] Skipping context injection (no cwd)", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            sys.exit(0)

        # Load latest memory
        print("📂 [context-keeper] Searching for previous session context...", file=sys.stderr)
        memory, metadata = load_latest_memory(cwd, session_id)

        if not memory:
            # No memory available - this is fine, just exit cleanly
            print("ℹ️  [context-keeper] No previous session context found", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            sys.exit(0)

        print(f"📄 [context-keeper] Found context for session {session_id[:8] if session_id else 'unknown'}...", file=sys.stderr)

        # Check if this memory is recent enough to be relevant
        # Skip if the memory is from a very old session (>24 hours)
        try:
            created_at = metadata.get('timestamp', metadata.get('created_at', ''))
            if created_at:
                # Parse ISO format
                memory_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                now = datetime.now(memory_time.tzinfo) if memory_time.tzinfo else datetime.now()
                age_hours = (now - memory_time.replace(tzinfo=None)).total_seconds() / 3600

                if age_hours > 24:
                    # Summary is old, skip injection but don't error
                    print(f"ℹ️  [context-keeper] Context is {age_hours:.1f}h old, skipping (>24h)", file=sys.stderr)
                    print("=" * 60 + "\n", file=sys.stderr)
                    sys.exit(0)
        except (ValueError, TypeError):
            # Can't parse date, continue anyway
            pass

        # Format and output context
        print("📥 [context-keeper] Loading context into session...", file=sys.stderr)
        context = format_context(memory, metadata or {}, source, permission_mode)
        print(context)

        # Print visible completion message
        print("✅ [context-keeper] Previous session context loaded successfully!", file=sys.stderr)
        print("=" * 60 + "\n", file=sys.stderr)

        sys.exit(0)

    except Exception as e:
        print(f"❌ [context-keeper] Error: {e}", file=sys.stderr)
        print("=" * 60 + "\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

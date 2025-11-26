#!/usr/bin/env python3
"""
SessionStart Hook: Reloads latest session summary into context after compaction.

This hook triggers when a session starts or resumes (including after compaction).
It reads the most recent summary and outputs it to stdout, which Claude uses as context.

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
from pathlib import Path
from datetime import datetime


def read_hook_input() -> dict:
    """Read JSON input from stdin."""
    try:
        input_data = sys.stdin.read()
        return json.loads(input_data) if input_data.strip() else {}
    except json.JSONDecodeError:
        return {}


def get_summaries_dir(project_path: str) -> Path:
    """Get the summaries directory for the project."""
    return Path(project_path) / ".claude" / "summaries"


def load_latest_summary(project_path: str, session_id: str = None) -> tuple[str, dict]:
    """
    Load the most recent summary for context injection.

    Returns:
        tuple: (summary_content, metadata) or (None, None) if not found
    """
    summaries_dir = get_summaries_dir(project_path)

    if not summaries_dir.exists():
        return None, None

    # Try to load from specific session if provided
    if session_id:
        session_dir = summaries_dir / session_id
        if session_dir.exists():
            latest_link = session_dir / "latest"
            if latest_link.exists():
                # Resolve symlink
                if latest_link.is_symlink():
                    target = session_dir / latest_link.resolve().name
                else:
                    target = latest_link

                summary_path = target / "summary.md" if target.is_dir() else None
                metadata_path = target / "metadata.json" if target.is_dir() else None

                if summary_path and summary_path.exists():
                    summary = summary_path.read_text(encoding='utf-8')
                    metadata = {}
                    if metadata_path and metadata_path.exists():
                        try:
                            metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
                        except json.JSONDecodeError:
                            pass
                    return summary, metadata

    # Fallback: Load from index (most recent across all sessions)
    index_path = summaries_dir / "index.json"
    if not index_path.exists():
        return None, None

    try:
        index = json.loads(index_path.read_text(encoding='utf-8'))
        summaries = index.get("summaries", [])

        if not summaries:
            return None, None

        # Get most recent
        latest = summaries[0]
        summary_path = summaries_dir / latest["summary_path"]

        if summary_path.exists():
            summary = summary_path.read_text(encoding='utf-8')
            return summary, latest

    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"[context-keeper] Error: Failed to load from index: {e}", file=sys.stderr)

    return None, None


def format_context(summary: str, metadata: dict, source: str, permission_mode: str = "default") -> str:
    """Format summary for context injection."""

    timestamp = metadata.get('timestamp', metadata.get('created_at', 'unknown'))
    session_id = metadata.get('session_id', 'unknown')
    trigger = metadata.get('trigger', 'unknown')
    files_modified = metadata.get('files_modified', [])

    # Create context wrapper
    context = f"""<previous-session-context>
## Session Continuity Notice

This context was automatically loaded from a previous session summary.
- **Previous Session ID:** {session_id[:16]}...
- **Summary Created:** {timestamp}
- **Compaction Trigger:** {trigger}
- **Files Modified:** {len(files_modified)}
- **Reload Source:** {source}
- **Permission Mode:** {permission_mode}

---

{summary}

---

*Use this context to maintain continuity with the previous conversation. The above summary captures what was discussed and accomplished before context compaction.*
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

        # Load latest summary
        print("📂 [context-keeper] Searching for previous session context...", file=sys.stderr)
        summary, metadata = load_latest_summary(cwd, session_id)

        if not summary:
            # No summary available - this is fine, just exit cleanly
            print("ℹ️  [context-keeper] No previous session context found", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            sys.exit(0)

        print(f"📄 [context-keeper] Found context for session {session_id[:8] if session_id else 'unknown'}...", file=sys.stderr)

        # Check if this summary is recent enough to be relevant
        # Skip if the summary is from a very old session (>24 hours)
        try:
            created_at = metadata.get('timestamp', metadata.get('created_at', ''))
            if created_at:
                # Parse ISO format
                summary_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                now = datetime.now(summary_time.tzinfo) if summary_time.tzinfo else datetime.now()
                age_hours = (now - summary_time.replace(tzinfo=None)).total_seconds() / 3600

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
        context = format_context(summary, metadata or {}, source, permission_mode)
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

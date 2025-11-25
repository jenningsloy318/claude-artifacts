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

# Debug log file path
DEBUG_LOG_PATH = Path.home() / ".claude" / "session-start-debug.log"


def _write_to_debug_log(message: str):
    """Append message to debug log file."""
    try:
        with open(DEBUG_LOG_PATH, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass  # Silently ignore log failures


def log_debug(message: str):
    """Log debug info to debug file and stderr."""
    _write_to_debug_log(f"DEBUG: {message}")
    print(f"[SessionStart Debug] {message}", file=sys.stderr)


def log_info(message: str):
    """Log info to debug file and stderr."""
    _write_to_debug_log(f"INFO: {message}")
    print(f"[SessionStart] {message}", file=sys.stderr)


def read_hook_input() -> dict:
    """Read JSON input from stdin."""
    try:
        input_data = sys.stdin.read()
        return json.loads(input_data) if input_data.strip() else {}
    except json.JSONDecodeError:
        return {}


def log_error(message: str):
    """Log error to stderr and debug file."""
    _write_to_debug_log(f"ERROR: {message}")
    print(f"[SessionStart Error] {message}", file=sys.stderr)


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
        log_error(f"Failed to load from index: {e}")

    return None, None


def format_context(summary: str, metadata: dict, event_type: str) -> str:
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
- **Reload Event:** {event_type}

---

{summary}

---

*Use this context to maintain continuity with the previous conversation. The above summary captures what was discussed and accomplished before context compaction.*
</previous-session-context>"""

    return context


def main():
    log_debug("=" * 60)
    log_debug("=== SESSION START HOOK RUNNING ===")
    log_debug(f"Python version: {sys.version}")
    log_debug(f"Script path: {__file__}")
    log_debug("=" * 60)

    try:
        # Read input from Claude Code
        log_debug("Reading hook input from stdin...")
        hook_input = read_hook_input()
        log_debug(f"Hook input received: {bool(hook_input)}")

        # Extract session information
        cwd = hook_input.get("cwd", "")
        event_type = hook_input.get("event_type", "unknown")
        session_id = hook_input.get("session_id", "")

        log_debug(f"Session ID: {session_id}")
        log_debug(f"Event type: {event_type}")
        log_debug(f"CWD: {cwd}")

        # Only inject context on resume (after compaction) or startup
        # Skip if this is a clear event
        if event_type == "clear":
            log_info("Skipping context injection (clear event)")
            sys.exit(0)

        if not cwd:
            log_info("Skipping context injection (no cwd)")
            sys.exit(0)

        # Load latest summary
        log_debug("Loading latest summary...")
        summary, metadata = load_latest_summary(cwd, session_id)

        if not summary:
            # No summary available - this is fine, just exit cleanly
            log_info("No summary available, skipping context injection")
            sys.exit(0)

        log_info(f"Found summary for session {session_id[:8] if session_id else 'unknown'}...")

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
                    log_info(f"Summary is {age_hours:.1f} hours old, skipping (>24h)")
                    sys.exit(0)
                log_debug(f"Summary age: {age_hours:.1f} hours")
        except (ValueError, TypeError) as e:
            # Can't parse date, continue anyway
            log_debug(f"Could not parse summary timestamp: {e}")
            pass

        # Format and output context
        log_debug("Formatting context for injection...")
        context = format_context(summary, metadata or {}, event_type)
        print(context)

        log_info("Context injected successfully")
        log_debug("=" * 60)
        log_debug("=== SESSION START HOOK COMPLETED ===")
        log_debug("=" * 60)

        sys.exit(0)

    except Exception as e:
        log_error(f"Unexpected error: {e}")
        log_debug("=== SESSION START HOOK FAILED ===")
        import traceback
        _write_to_debug_log(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

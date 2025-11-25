#!/usr/bin/env python3
"""
PreCompact Hook: Summarizes and persists Claude Code sessions before compaction.

This hook triggers before context compaction (manual /compact or automatic).
It reads the full transcript, generates a summary, and saves it locally.

Input (stdin): JSON with session metadata
Output (stdout): Status message for user
Exit codes:
  0 - Success
  1 - Non-blocking error (logged but doesn't block compaction)

Environment variables:
  CLAUDE_SUMMARY_API_KEY - API key for Claude summarization (preferred)
  ANTHROPIC_API_KEY - Fallback API key
  CLAUDE_SUMMARY_API_URL - Custom API base URL (optional, e.g., for proxy or region)
"""

import sys
import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# ============================================================================
# Configuration
# ============================================================================

SUMMARY_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4000
TIMEOUT_SECONDS = 90


# ============================================================================
# Input/Output Helpers
# ============================================================================

def read_hook_input() -> dict:
    """Read JSON input from stdin."""
    try:
        input_data = sys.stdin.read()
        return json.loads(input_data) if input_data.strip() else {}
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse hook input: {e}")
        return {}


def log_error(message: str):
    """Log error to stderr."""
    print(f"[PreCompact Error] {message}", file=sys.stderr)


def log_info(message: str):
    """Log info to stdout (visible to user)."""
    print(f"[PreCompact] {message}")


# ============================================================================
# Transcript Parsing
# ============================================================================

def parse_transcript(transcript_path: str) -> list[dict]:
    """Parse JSONL transcript file into messages."""
    messages = []
    path = Path(transcript_path).expanduser()

    if not path.exists():
        log_error(f"Transcript file not found: {transcript_path}")
        return messages

    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        log_error(f"Failed to parse line {line_num} in transcript")
    except Exception as e:
        log_error(f"Failed to read transcript: {e}")

    return messages


def extract_conversation_content(messages: list[dict]) -> dict:
    """Extract relevant content from transcript messages."""
    user_messages = []
    assistant_messages = []
    tool_calls = []
    files_modified = set()

    for msg in messages:
        msg_type = msg.get('type', '')

        # Handle Claude Code transcript format (nested message object)
        nested_msg = msg.get('message', {})
        role = nested_msg.get('role', '') if isinstance(nested_msg, dict) else ''
        content = nested_msg.get('content', '') if isinstance(nested_msg, dict) else msg.get('content', '')

        # User messages
        if msg_type == 'user' or role == 'user':
            if isinstance(content, str) and content.strip():
                # Skip system reminders
                if '<system-reminder>' not in content:
                    user_messages.append(content[:2000])
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text = block.get('text', '')
                        if text and '<system-reminder>' not in text:
                            user_messages.append(text[:2000])

        # Assistant messages
        elif msg_type == 'assistant' or role == 'assistant':
            if isinstance(content, str) and content.strip():
                assistant_messages.append(content[:2000])
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        block_type = block.get('type', '')
                        if block_type == 'text':
                            text = block.get('text', '')
                            if text:
                                assistant_messages.append(text[:2000])
                        elif block_type == 'tool_use':
                            tool_name = block.get('name', 'unknown')
                            tool_input = block.get('input', {})
                            tool_calls.append({
                                'tool': tool_name,
                                'input': tool_input
                            })
                            # Track file modifications
                            if tool_name in ['Edit', 'Write', 'MultiEdit', 'NotebookEdit']:
                                file_path = tool_input.get('file_path', tool_input.get('notebook_path', ''))
                                if file_path:
                                    files_modified.add(file_path)

        # Handle tool_use messages directly (older format)
        elif msg_type == 'tool_use':
            tool_name = msg.get('name', 'unknown')
            tool_input = msg.get('input', {})
            tool_calls.append({
                'tool': tool_name,
                'input': tool_input
            })
            if tool_name in ['Edit', 'Write', 'MultiEdit', 'NotebookEdit']:
                file_path = tool_input.get('file_path', tool_input.get('notebook_path', ''))
                if file_path:
                    files_modified.add(file_path)

    return {
        'user_messages': user_messages,
        'assistant_messages': assistant_messages,
        'tool_calls': tool_calls,
        'files_modified': list(files_modified),
        'message_count': len(messages)
    }


# ============================================================================
# Summary Generation
# ============================================================================

def get_settings_env() -> dict:
    """Load env vars from ~/.claude/settings.json as fallback."""
    settings_path = Path.home() / ".claude" / "settings.json"
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding='utf-8'))
            return settings.get("env", {})
        except (json.JSONDecodeError, Exception):
            pass
    return {}


def get_api_key() -> Optional[str]:
    """Get API key from environment with fallback to settings.json."""
    # First try shell environment
    key = os.environ.get("CLAUDE_SUMMARY_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    # Fallback to settings.json env section
    settings_env = get_settings_env()
    return settings_env.get("CLAUDE_SUMMARY_API_KEY") or settings_env.get("ANTHROPIC_API_KEY")


def get_api_url() -> Optional[str]:
    """Get custom API URL from environment with fallback to settings.json."""
    # First try shell environment
    url = os.environ.get("CLAUDE_SUMMARY_API_URL")
    if url:
        return url
    # Fallback to settings.json env section
    settings_env = get_settings_env()
    return settings_env.get("CLAUDE_SUMMARY_API_URL")


def generate_summary_with_llm(content: dict, session_info: dict) -> Optional[str]:
    """Generate comprehensive summary using Claude API."""
    api_key = get_api_key()
    if not api_key:
        log_info("No API key found (CLAUDE_SUMMARY_API_KEY or ANTHROPIC_API_KEY)")
        return None

    try:
        import anthropic
    except ImportError:
        log_error("anthropic package not installed. Run: pip install anthropic")
        return None

    # Prepare content for summarization (truncate to avoid token limits)
    user_msgs = content.get('user_messages', [])[:20]  # Last 20 user messages
    assistant_msgs = content.get('assistant_messages', [])[:20]
    tool_calls = content.get('tool_calls', [])[:50]
    files_modified = content.get('files_modified', [])

    prompt = f"""Analyze this Claude Code session and create a comprehensive summary for future context restoration.

## Session Information
- Session ID: {session_info.get('session_id', 'unknown')}
- Project: {session_info.get('cwd', 'unknown')}
- Trigger: {session_info.get('trigger', 'unknown')}
- Timestamp: {session_info.get('timestamp', 'unknown')}
- Total Messages: {content.get('message_count', 0)}

## User Messages (sample)
{json.dumps(user_msgs[:10], indent=2, ensure_ascii=False)[:3000]}

## Assistant Responses (sample)
{json.dumps(assistant_msgs[:10], indent=2, ensure_ascii=False)[:3000]}

## Tool Calls
{json.dumps(tool_calls[:30], indent=2, ensure_ascii=False)[:2000]}

## Files Modified
{json.dumps(files_modified, indent=2)}

---

Create a summary with these sections:

## Topics Discussed
- List main themes and subjects covered

## Code Changes
- Files modified with brief descriptions of changes
- Key code snippets if relevant

## Decisions Made
- Important decisions with rationale
- Trade-offs considered

## Key Outcomes
- What was accomplished
- Problems solved

## Context for Continuation
- Important context needed to continue this work
- Current state of implementation
- Next steps if mentioned

## Tags
- Relevant hashtags for categorization (e.g., #authentication #api #bugfix)

Be comprehensive but concise. Focus on information that would help resume this work later."""

    try:
        # Build client with optional custom base URL
        api_url = get_api_url()
        if api_url:
            client = anthropic.Anthropic(api_key=api_key, base_url=api_url)
            log_info(f"Using custom API URL: {api_url}")
        else:
            client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model=SUMMARY_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        log_error(f"LLM summarization failed: {e}")
        return None


def generate_summary_structured(content: dict, session_info: dict) -> str:
    """Generate structured summary without LLM (fallback)."""
    files_modified = content.get('files_modified', [])
    tool_calls = content.get('tool_calls', [])
    user_messages = content.get('user_messages', [])

    # Extract topics from user messages (simple keyword extraction)
    topics = set()
    for msg in user_messages[:20]:
        # Extract words that look like topics
        words = re.findall(r'\b[a-zA-Z]{4,}\b', msg.lower())
        topics.update(words[:5])

    # Count tool usage
    tool_counts = {}
    for tc in tool_calls:
        tool = tc.get('tool', 'unknown')
        tool_counts[tool] = tool_counts.get(tool, 0) + 1

    summary = f"""# Session Summary (Structured Extraction)

## Metadata
- **Session ID:** {session_info.get('session_id', 'unknown')}
- **Project:** {session_info.get('cwd', 'unknown')}
- **Trigger:** {session_info.get('trigger', 'unknown')}
- **Timestamp:** {session_info.get('timestamp', 'unknown')}
- **Total Messages:** {content.get('message_count', 0)}

## Files Modified
{chr(10).join(f'- `{f}`' for f in files_modified) if files_modified else '- None tracked'}

## Tool Usage
{chr(10).join(f'- {tool}: {count} calls' for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1])[:10]) if tool_counts else '- None tracked'}

## Sample User Requests
{chr(10).join(f'- {msg[:200]}...' if len(msg) > 200 else f'- {msg}' for msg in user_messages[:5]) if user_messages else '- None captured'}

## Keywords
{', '.join(list(topics)[:15]) if topics else 'None extracted'}

---
*Note: This is a structured extraction. LLM-based summary unavailable (no API key or error).*
"""
    return summary


def generate_summary(content: dict, session_info: dict) -> str:
    """Generate summary with LLM, falling back to structured extraction."""
    # Try LLM first
    llm_summary = generate_summary_with_llm(content, session_info)
    if llm_summary:
        return llm_summary

    # Fall back to structured extraction
    log_info("Using structured extraction (LLM unavailable)")
    return generate_summary_structured(content, session_info)


# ============================================================================
# File Storage
# ============================================================================

def get_summaries_dir(project_path: str) -> Path:
    """Get the summaries directory for the project."""
    return Path(project_path) / ".claude" / "summaries"


def save_summary(
    session_id: str,
    summary: str,
    metadata: dict,
    project_path: str
) -> Path:
    """Save summary and metadata to file system with timestamp versioning."""
    summaries_dir = get_summaries_dir(project_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create session/timestamp directory
    session_dir = summaries_dir / session_id / timestamp
    session_dir.mkdir(parents=True, exist_ok=True)

    # Save summary
    summary_path = session_dir / "summary.md"
    summary_path.write_text(summary, encoding='utf-8')

    # Save metadata
    metadata['summary_timestamp'] = timestamp
    metadata_path = session_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')

    # Update latest symlink
    latest_link = summaries_dir / session_id / "latest"
    if latest_link.is_symlink():
        latest_link.unlink()
    elif latest_link.exists():
        latest_link.unlink()

    try:
        latest_link.symlink_to(timestamp)
    except OSError as e:
        log_error(f"Failed to create latest symlink: {e}")

    # Update global index
    update_index(summaries_dir, session_id, timestamp, metadata)

    return summary_path


def update_index(summaries_dir: Path, session_id: str, timestamp: str, metadata: dict):
    """Update the summaries index file."""
    index_path = summaries_dir / "index.json"

    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            index = {"summaries": [], "last_session": None}
    else:
        index = {"summaries": [], "last_session": None}

    # Add new entry at the beginning
    entry = {
        "session_id": session_id,
        "timestamp": timestamp,
        "created_at": metadata.get('timestamp', ''),
        "trigger": metadata.get('trigger', ''),
        "project": metadata.get('cwd', ''),
        "files_modified": metadata.get('files_modified', []),
        "message_count": metadata.get('message_count', 0),
        "summary_path": f"{session_id}/{timestamp}/summary.md"
    }

    index["summaries"].insert(0, entry)
    index["last_session"] = session_id

    # Keep only last 100 entries
    index["summaries"] = index["summaries"][:100]

    # Ensure directory exists
    summaries_dir.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding='utf-8')


def extract_topics_from_summary(summary: str) -> list[str]:
    """Extract topic tags from summary."""
    # Look for hashtags
    hashtags = re.findall(r'#(\w+)', summary)
    return list(set(hashtags))[:10]


# ============================================================================
# Main Execution
# ============================================================================

def main():
    try:
        # Read input from Claude Code
        hook_input = read_hook_input()

        if not hook_input:
            log_error("No input received")
            sys.exit(1)

        # Extract session information
        session_id = hook_input.get("session_id", "unknown")
        transcript_path = hook_input.get("transcript_path", "")
        trigger = hook_input.get("trigger", "unknown")
        cwd = hook_input.get("cwd", os.getcwd())

        log_info(f"Processing session {session_id[:8]}... (trigger: {trigger})")

        # Parse transcript
        if not transcript_path:
            log_error("No transcript path provided")
            sys.exit(1)

        messages = parse_transcript(transcript_path)
        if not messages:
            log_info("No messages in transcript, skipping summary")
            sys.exit(0)

        log_info(f"Parsed {len(messages)} messages from transcript")

        # Extract content
        content = extract_conversation_content(messages)

        # Prepare session info
        session_info = {
            "session_id": session_id,
            "trigger": trigger,
            "cwd": cwd,
            "timestamp": datetime.now().astimezone().isoformat()
        }

        # Generate summary
        log_info("Generating summary...")
        summary = generate_summary(content, session_info)

        # Prepare metadata
        metadata = {
            **session_info,
            "topics": extract_topics_from_summary(summary),
            "files_modified": content.get("files_modified", []),
            "message_count": content.get("message_count", 0),
            "tool_call_count": len(content.get("tool_calls", []))
        }

        # Save to project directory
        summary_path = save_summary(session_id, summary, metadata, cwd)

        log_info(f"Summary saved: {summary_path}")
        log_info(f"Files modified: {len(metadata['files_modified'])}")
        log_info(f"Topics: {', '.join(metadata['topics'][:5]) if metadata['topics'] else 'none extracted'}")

        sys.exit(0)

    except Exception as e:
        log_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

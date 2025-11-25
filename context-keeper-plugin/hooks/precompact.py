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
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

# ============================================================================
# Configuration
# ============================================================================

SUMMARY_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4000
TIMEOUT_SECONDS = 90

# Debug log file path (always logs here so we can check what happened)
DEBUG_LOG_PATH = Path.home() / ".claude" / "precompact-debug.log"


# ============================================================================
# Input/Output Helpers
# ============================================================================

def _write_to_debug_log(message: str):
    """Append message to debug log file."""
    try:
        with open(DEBUG_LOG_PATH, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass  # Silently ignore log failures


def _ensure_package_installed(package_name: str) -> bool:
    """Ensure a Python package is installed, auto-installing if needed."""
    try:
        __import__(package_name.replace("-", "_"))
        return True
    except ImportError:
        pass

    _write_to_debug_log(f"{package_name} package not found, attempting auto-install...")

    # Try different pip installation methods
    install_commands = [
        [sys.executable, "-m", "pip", "install", "--user", package_name],
        [sys.executable, "-m", "pip", "install", package_name],
        ["pip3", "install", "--user", package_name],
        ["pip3", "install", "--break-system-packages", package_name],
    ]

    for cmd in install_commands:
        try:
            _write_to_debug_log(f"Trying: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                _write_to_debug_log(f"Successfully installed {package_name} via: {' '.join(cmd)}")
                # Verify import works now
                try:
                    mod = __import__(package_name.replace("-", "_"))
                    _write_to_debug_log(f"{package_name} version: {getattr(mod, '__version__', 'unknown')}")
                    return True
                except ImportError:
                    _write_to_debug_log("Import still failed after installation")
                    continue
            else:
                _write_to_debug_log(f"Command failed: {result.stderr[:200] if result.stderr else 'no error'}")
        except subprocess.TimeoutExpired:
            _write_to_debug_log(f"Command timed out: {' '.join(cmd)}")
        except Exception as e:
            _write_to_debug_log(f"Command error: {e}")

    _write_to_debug_log("All installation attempts failed")
    return False


def _ensure_anthropic_installed() -> bool:
    """Ensure the anthropic package is installed, auto-installing if needed."""
    return _ensure_package_installed("anthropic")


def read_hook_input() -> dict:
    """Read JSON input from stdin."""
    try:
        input_data = sys.stdin.read()
        return json.loads(input_data) if input_data.strip() else {}
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse hook input: {e}")
        return {}


def log_error(message: str):
    """Log error to stderr and debug file."""
    print(f"[PreCompact Error] {message}", file=sys.stderr)
    _write_to_debug_log(f"ERROR: {message}")


def log_info(message: str):
    """Log info to stdout (visible to user) and debug file."""
    print(f"[PreCompact] {message}")
    _write_to_debug_log(f"INFO: {message}")


def log_debug(message: str):
    """Log debug info to debug file (always) and stderr."""
    _write_to_debug_log(f"DEBUG: {message}")
    print(f"[PreCompact Debug] {message}", file=sys.stderr)


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
    log_debug(f"Looking for settings.json at: {settings_path}")

    if not settings_path.exists():
        log_debug(f"settings.json NOT FOUND at {settings_path}")
        return {}

    log_debug(f"settings.json EXISTS at {settings_path}")
    try:
        raw_content = settings_path.read_text(encoding='utf-8')
        log_debug(f"settings.json content length: {len(raw_content)} chars")
        settings = json.loads(raw_content)
        log_debug(f"settings.json parsed successfully, keys: {list(settings.keys())}")

        env_section = settings.get("env", {})
        if env_section:
            log_debug(f"Found 'env' section with keys: {list(env_section.keys())}")
            # Mask sensitive values in debug output
            for key in env_section:
                value = env_section[key]
                if value:
                    masked = value[:4] + "..." + value[-4:] if len(value) > 10 else "***"
                    log_debug(f"  env[{key}] = {masked}")
        else:
            log_debug("'env' section is EMPTY or NOT FOUND in settings.json")

        return env_section
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse settings.json: {e}")
        return {}
    except Exception as e:
        log_error(f"Failed to read settings.json: {e}")
        return {}


def get_api_key() -> Optional[str]:
    """Get API key from environment with fallback to settings.json."""
    log_debug("=== get_api_key() START ===")

    # First try shell environment
    log_debug("Checking shell environment for API key...")
    env_key = os.environ.get("CLAUDE_SUMMARY_API_KEY")
    env_key_anthropic = os.environ.get("ANTHROPIC_API_KEY")

    if env_key:
        masked = env_key[:4] + "..." + env_key[-4:] if len(env_key) > 10 else "***"
        log_debug(f"Found CLAUDE_SUMMARY_API_KEY in shell env: {masked}")
        log_debug("=== get_api_key() END (from shell env) ===")
        return env_key
    elif env_key_anthropic:
        masked = env_key_anthropic[:4] + "..." + env_key_anthropic[-4:] if len(env_key_anthropic) > 10 else "***"
        log_debug(f"Found ANTHROPIC_API_KEY in shell env: {masked}")
        log_debug("=== get_api_key() END (from shell env) ===")
        return env_key_anthropic
    else:
        log_debug("NO API key found in shell environment")

    # Fallback to settings.json env section
    log_debug("Falling back to settings.json...")
    settings_env = get_settings_env()

    settings_key = settings_env.get("CLAUDE_SUMMARY_API_KEY")
    settings_key_anthropic = settings_env.get("ANTHROPIC_API_KEY")

    if settings_key:
        masked = settings_key[:4] + "..." + settings_key[-4:] if len(settings_key) > 10 else "***"
        log_debug(f"Found CLAUDE_SUMMARY_API_KEY in settings.json: {masked}")
        log_debug("=== get_api_key() END (from settings.json) ===")
        return settings_key
    elif settings_key_anthropic:
        masked = settings_key_anthropic[:4] + "..." + settings_key_anthropic[-4:] if len(settings_key_anthropic) > 10 else "***"
        log_debug(f"Found ANTHROPIC_API_KEY in settings.json: {masked}")
        log_debug("=== get_api_key() END (from settings.json) ===")
        return settings_key_anthropic

    log_debug("NO API key found in settings.json either")
    log_debug("=== get_api_key() END (NO KEY FOUND) ===")
    return None


def get_api_url() -> Optional[str]:
    """Get custom API URL from environment with fallback to settings.json."""
    log_debug("=== get_api_url() START ===")

    # First try shell environment
    log_debug("Checking shell environment for API URL...")
    env_url = os.environ.get("CLAUDE_SUMMARY_API_URL")

    if env_url:
        log_debug(f"Found CLAUDE_SUMMARY_API_URL in shell env: {env_url}")
        log_debug("=== get_api_url() END (from shell env) ===")
        return env_url
    else:
        log_debug("NO API URL found in shell environment")

    # Fallback to settings.json env section
    log_debug("Falling back to settings.json...")
    settings_env = get_settings_env()

    settings_url = settings_env.get("CLAUDE_SUMMARY_API_URL")
    if settings_url:
        log_debug(f"Found CLAUDE_SUMMARY_API_URL in settings.json: {settings_url}")
        log_debug("=== get_api_url() END (from settings.json) ===")
        return settings_url

    log_debug("NO API URL found in settings.json either")
    log_debug("=== get_api_url() END (NO URL FOUND) ===")
    return None


def generate_summary_with_llm(content: dict, session_info: dict) -> Optional[str]:
    """Generate comprehensive summary using Claude API."""
    log_debug("=== generate_summary_with_llm() START ===")

    api_key = get_api_key()
    if not api_key:
        log_info("No API key found (CLAUDE_SUMMARY_API_KEY or ANTHROPIC_API_KEY)")
        log_debug("=== generate_summary_with_llm() END (no API key) ===")
        return None

    log_debug(f"API key obtained, length: {len(api_key)} chars")

    # Ensure anthropic package is installed (auto-install if needed)
    if not _ensure_anthropic_installed():
        log_error("anthropic package not available and auto-install failed")
        log_debug("=== generate_summary_with_llm() END (no anthropic) ===")
        return None

    import anthropic
    log_debug(f"anthropic package imported successfully, version: {getattr(anthropic, '__version__', 'unknown')}")

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
        log_debug(f"API URL obtained: {api_url if api_url else 'None (using default)'}")

        if api_url:
            log_debug(f"Creating Anthropic client with custom base_url: {api_url}")
            client = anthropic.Anthropic(api_key=api_key, base_url=api_url)
            log_info(f"Using custom API URL: {api_url}")
        else:
            log_debug("Creating Anthropic client with default base_url")
            client = anthropic.Anthropic(api_key=api_key)

        log_debug(f"Calling LLM with model: {SUMMARY_MODEL}, max_tokens: {MAX_TOKENS}")
        response = client.messages.create(
            model=SUMMARY_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        log_debug(f"LLM response received, content length: {len(response.content[0].text)} chars")
        log_debug("=== generate_summary_with_llm() END (success) ===")
        return response.content[0].text
    except Exception as e:
        log_error(f"LLM summarization failed: {e}")
        log_debug(f"Exception type: {type(e).__name__}")
        log_debug("=== generate_summary_with_llm() END (exception) ===")
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
# Nowledge MCP Integration
# ============================================================================

NOWLEDGE_MCP_URL = "http://localhost:14242/mcp"


def persist_to_nowledge(summary: str, metadata: dict, content: dict) -> bool:
    """
    Persist memory and thread to nowledge MCP server.

    Uses mcp-use Python client to call nowledge MCP tools:
    - memory_add: Add distilled memory with key insights
    - thread_persist: Save full conversation thread

    Returns True if successful, False otherwise.
    Non-blocking - failures don't affect local summary storage.
    """
    log_debug("=== persist_to_nowledge() START ===")

    # Check if mcp-use is installed
    if not _ensure_package_installed("mcp-use"):
        log_debug("mcp-use not available, skipping nowledge integration")
        return False

    try:
        import asyncio
        from mcp_use import MCPClient

        log_debug("mcp-use imported successfully")
    except ImportError as e:
        log_debug(f"Failed to import mcp-use: {e}")
        return False

    async def _persist_async():
        """Async function to call nowledge MCP tools."""
        config = {
            "mcpServers": {
                "nowledge-mem": {
                    "url": NOWLEDGE_MCP_URL,
                    "type": "streamableHttp",
                    "headers": {
                        "APP": "context-keeper"
                    }
                }
            }
        }

        client = MCPClient.from_dict(config)
        results = {"memory": False, "thread": False}

        try:
            log_debug("Creating MCP session...")
            await client.create_all_sessions()
            session = client.get_session("nowledge-mem")

            if not session:
                log_debug("Failed to get nowledge-mem session")
                return results

            # List available tools to verify connection
            log_debug("Listing available tools...")
            tools = await session.list_tools()
            tool_names = [t.name for t in tools]
            log_debug(f"Available tools: {tool_names}")

            # 1. Add memory with distilled insights
            if "memory_add" in tool_names:
                log_debug("Calling memory_add...")
                try:
                    # Extract key insights for memory
                    topics = metadata.get("topics", [])
                    files_modified = metadata.get("files_modified", [])
                    session_id = metadata.get("session_id", "unknown")
                    project = metadata.get("cwd", "unknown")

                    # Create a concise memory content
                    memory_content = f"""Session {session_id[:8]} - {project}

Key topics: {', '.join(topics[:5]) if topics else 'None'}
Files modified: {len(files_modified)}
Message count: {metadata.get('message_count', 0)}

Summary excerpt:
{summary[:1500]}"""

                    memory_result = await session.call_tool(
                        name="memory_add",
                        arguments={
                            "content": memory_content,
                            "title": f"Claude Code Session: {', '.join(topics[:3]) if topics else session_id[:8]}",
                            "importance": 0.7,
                            "labels": ",".join(["claude-code", "session-summary"] + topics[:3]),
                            "source": "context-keeper-precompact"
                        }
                    )
                    log_debug(f"memory_add result: {memory_result}")
                    results["memory"] = True
                    log_info("Memory persisted to nowledge")
                except Exception as e:
                    log_debug(f"memory_add failed: {e}")

            # 2. Persist full thread
            if "thread_persist" in tool_names:
                log_debug("Calling thread_persist...")
                try:
                    thread_result = await session.call_tool(
                        name="thread_persist",
                        arguments={
                            "client": "claude-code",
                            "project_path": metadata.get("cwd", ""),
                            "persist_mode": "current",
                            "summary": f"Session {metadata.get('session_id', 'unknown')[:8]}: {', '.join(metadata.get('topics', [])[:3])}"[:100]
                        }
                    )
                    log_debug(f"thread_persist result: {thread_result}")
                    results["thread"] = True
                    log_info("Thread persisted to nowledge")
                except Exception as e:
                    log_debug(f"thread_persist failed: {e}")

            return results

        except Exception as e:
            log_debug(f"MCP session error: {e}")
            return results
        finally:
            try:
                await client.close_all_sessions()
            except Exception:
                pass

    # Run the async function
    try:
        # Check if nowledge server is reachable first
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 14242))
        sock.close()

        if result != 0:
            log_debug("Nowledge MCP server not reachable on localhost:14242")
            log_debug("=== persist_to_nowledge() END (server not running) ===")
            return False

        log_debug("Nowledge server is reachable, proceeding with persistence...")
        results = asyncio.run(_persist_async())
        success = results.get("memory", False) or results.get("thread", False)
        log_debug(f"=== persist_to_nowledge() END (success={success}) ===")
        return success

    except Exception as e:
        log_debug(f"persist_to_nowledge error: {e}")
        log_debug("=== persist_to_nowledge() END (exception) ===")
        return False


# ============================================================================
# Main Execution
# ============================================================================

def main():
    log_debug("=" * 60)
    log_debug("=== PRECOMPACT HOOK STARTED ===")
    log_debug(f"Python version: {sys.version}")
    log_debug(f"Script path: {__file__}")
    log_debug(f"Working directory: {os.getcwd()}")
    log_debug(f"HOME: {Path.home()}")
    log_debug("=" * 60)

    try:
        # Read input from Claude Code
        log_debug("Reading hook input from stdin...")
        hook_input = read_hook_input()
        log_debug(f"Hook input received: {bool(hook_input)}")

        if not hook_input:
            log_error("No input received")
            log_debug("=== PRECOMPACT HOOK ENDED (no input) ===")
            sys.exit(1)

        # Extract session information
        session_id = hook_input.get("session_id", "unknown")
        transcript_path = hook_input.get("transcript_path", "")
        trigger = hook_input.get("trigger", "unknown")
        cwd = hook_input.get("cwd", os.getcwd())

        log_debug(f"Session ID: {session_id}")
        log_debug(f"Transcript path: {transcript_path}")
        log_debug(f"Trigger: {trigger}")
        log_debug(f"CWD: {cwd}")

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
        log_debug("Saving summary to project directory...")
        summary_path = save_summary(session_id, summary, metadata, cwd)

        log_info(f"Summary saved: {summary_path}")
        log_info(f"Files modified: {len(metadata['files_modified'])}")
        log_info(f"Topics: {', '.join(metadata['topics'][:5]) if metadata['topics'] else 'none extracted'}")

        # Persist to nowledge (non-blocking, optional)
        log_debug("Attempting to persist to nowledge...")
        try:
            nowledge_success = persist_to_nowledge(summary, metadata, content)
            if nowledge_success:
                log_debug("Nowledge persistence successful")
            else:
                log_debug("Nowledge persistence skipped or failed (non-blocking)")
        except Exception as e:
            log_debug(f"Nowledge persistence error (non-blocking): {e}")

        log_debug("=" * 60)
        log_debug("=== PRECOMPACT HOOK COMPLETED SUCCESSFULLY ===")
        log_debug("=" * 60)
        sys.exit(0)

    except Exception as e:
        log_error(f"Unexpected error: {e}")
        log_debug("=== PRECOMPACT HOOK ENDED (exception) ===")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

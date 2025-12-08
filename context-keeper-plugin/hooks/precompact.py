#!/usr/bin/env python3
"""
PreCompact Hook: Summarizes and persists Claude Code sessions before compaction.

This hook triggers before context compaction (manual /compact or automatic).
It reads the full transcript, generates a memory, and saves it locally.

Input (stdin): JSON with session metadata
Output (stdout): Status message for user
Exit codes:
  0 - Success
  1 - Non-blocking error (logged but doesn't block compaction)

Environment variables:
  CLAUDE_SUMMARY_API_KEY - Dedicated API key for Claude summarization (required for LLM memory)
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

# ============================================================================
# Input/Output Helpers
# ============================================================================

def _ensure_package_installed(package_name: str) -> bool:
    """Ensure a Python package is installed, auto-installing if needed."""
    try:
        __import__(package_name.replace("-", "_"))
        return True
    except ImportError:
        pass

    print(f"[PreCompact] {package_name} not found, attempting auto-install...", file=sys.stderr)

    # Try different pip installation methods
    install_commands = [
        [sys.executable, "-m", "pip", "install", "--user", package_name],
        [sys.executable, "-m", "pip", "install", package_name],
        ["pip3", "install", "--user", package_name],
        ["pip3", "install", "--break-system-packages", package_name],
    ]

    for cmd in install_commands:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                # Verify import works now
                try:
                    __import__(package_name.replace("-", "_"))
                    print(f"[PreCompact] ✅ Successfully installed {package_name}", file=sys.stderr)
                    return True
                except ImportError:
                    continue
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass

    print(f"[PreCompact] ❌ Failed to install {package_name}", file=sys.stderr)
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
    """Log error to stderr."""
    print(f"[PreCompact] ❌ {message}", file=sys.stderr)


def log_info(message: str):
    """Log info to stdout (visible to user)."""
    print(f"[PreCompact] {message}")


def log_debug(message: str):
    """No-op debug logging (disabled)."""
    pass  # Debug logging disabled - use visible messages instead


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
    """Get CLAUDE_SUMMARY_API_KEY from environment with fallback to settings.json."""
    log_debug("=== get_api_key() START ===")

    # First try shell environment
    log_debug("Checking shell environment for CLAUDE_SUMMARY_API_KEY...")
    env_key = os.environ.get("CLAUDE_SUMMARY_API_KEY")

    if env_key:
        masked = env_key[:4] + "..." + env_key[-4:] if len(env_key) > 10 else "***"
        log_debug(f"Found CLAUDE_SUMMARY_API_KEY in shell env: {masked}")
        log_debug("=== get_api_key() END (from shell env) ===")
        return env_key

    log_debug("CLAUDE_SUMMARY_API_KEY not found in shell environment")

    # Fallback to settings.json env section
    log_debug("Falling back to settings.json...")
    settings_env = get_settings_env()

    settings_key = settings_env.get("CLAUDE_SUMMARY_API_KEY")

    if settings_key:
        masked = settings_key[:4] + "..." + settings_key[-4:] if len(settings_key) > 10 else "***"
        log_debug(f"Found CLAUDE_SUMMARY_API_KEY in settings.json: {masked}")
        log_debug("=== get_api_key() END (from settings.json) ===")
        return settings_key

    log_debug("CLAUDE_SUMMARY_API_KEY not found in settings.json either")
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


def generate_memory_with_llm(content: dict, session_info: dict) -> Optional[str]:
    """Generate comprehensive memory using Claude API."""
    log_debug("=== generate_memory_with_llm() START ===")

    api_key = get_api_key()
    if not api_key:
        log_info("No API key found (set CLAUDE_SUMMARY_API_KEY)")
        log_debug("=== generate_memory_with_llm() END (no API key) ===")
        return None

    log_debug(f"API key obtained, length: {len(api_key)} chars")

    # Ensure anthropic package is installed (auto-install if needed)
    if not _ensure_anthropic_installed():
        log_error("anthropic package not available and auto-install failed")
        log_debug("=== generate_memory_with_llm() END (no anthropic) ===")
        return None

    import anthropic
    log_debug(f"anthropic package imported successfully, version: {getattr(anthropic, '__version__', 'unknown')}")

    # Prepare content for summarization (truncate to avoid token limits)
    user_msgs = content.get('user_messages', [])[:20]  # Last 20 user messages
    assistant_msgs = content.get('assistant_messages', [])[:20]
    tool_calls = content.get('tool_calls', [])[:50]
    files_modified = content.get('files_modified', [])

    # Build custom instructions section if provided
    custom_instructions = session_info.get('custom_instructions', '')
    custom_section = ""
    if custom_instructions:
        custom_section = f"""
## User's Custom Instructions
The user provided these specific instructions for this compaction:
{custom_instructions}

**Important:** Incorporate the user's custom instructions into your memory. Focus on what they've asked for.
"""

    prompt = f"""Analyze this Claude Code session and create a comprehensive memory for future context restoration.

## What MUST be preserved:
- Key architecture changes (system design, structural modifications, refactoring decisions)
- Key UI/UX changes (component updates, interface modifications, user experience improvements)
- Key specification changes (requirements changes, business rules, validation logic updates)
- Multiple rounds of conversation that clarify issues and requirements
- Indirect or direct logs that show errors (error messages, stack traces, failure information)

## What should be refined/summarized:
- Repetitive conversations that converge on a solution
- Long error traces refined to show only key error indicators
- Multiple similar questions condensed into single entries

## What should be avoided:
- Plenty of unrelated logs posted by user (random logs, test outputs)
- LLM thinking process and internal reasoning
- Meaningless acknowledgments ("I understand", "Got it", "Thanks", etc.)
- Raw tool outputs without meaningful context
- Duplicate or very similar messages

## Session Information
- Session ID: {session_info.get('session_id', 'unknown')}
- Project: {session_info.get('cwd', 'unknown')}
- Trigger: {session_info.get('trigger', 'unknown')}
- Permission Mode: {session_info.get('permission_mode', 'default')}
- Hook Event: {session_info.get('hook_event_name', 'PreCompact')}
- Timestamp: {session_info.get('timestamp', 'unknown')}
- Total Messages: {content.get('message_count', 0)}
{custom_section}

## Filtered Content
This session has been filtered to preserve only essential content as specified above. The following were excluded:
- Unrelated logs and system outputs
- LLM internal thinking processes
- Filler acknowledgments and pleasantries
- Repetitive minor interactions
- Raw tool outputs without context

## Key Messages Preserved
{json.dumps([msg for msg in user_messages if len(msg.strip()) and '<system-reminder>' not in msg][:15], indent=2, ensure_ascii=False)[:3000]}

## Key Assistant Responses
{json.dumps([msg for msg in assistant_messages if len(msg.strip())][:15], indent=2, ensure_ascii=False)[:3000]}

## Important Tool Operations
{json.dumps([tc for tc in tool_calls if tc.get('tool') in ['Edit', 'Write', 'Read', 'Bash'] and not any(tc.get('tool') in ['NotebookEdit', 'NotebookEdit'] or tc.get('tool') == 'Read' and not tc.get('input', {}).get('file_path'))][:10], indent=2, ensure_ascii=False)[:2000]}

---

Create a memory with these sections:

## Topics Discussed
- List main themes and subjects covered

## Architecture Changes
- Files modified with brief descriptions of changes
- Key design patterns and decisions

## UI/UX Changes
- Interface updates and component modifications
- User flow improvements
- Design system updates

## Specification Changes
- Requirements and business rules updates
- Validation logic changes
- API contract modifications

## Code Changes
- Files modified with brief descriptions
- Key snippets or patterns implemented

## Decisions Made
- Important decisions with rationale
- Trade-offs considered
- Architecture choices

## Key Outcomes
- What was accomplished
- Problems solved
- Features implemented

## Context for Continuation
- Important context needed to continue this work
- Current state of implementation
- Next steps if mentioned
- File changes that were made

## Tags
- Relevant hashtags for categorization (e.g., #authentication #api #bugfix #refactor)

Be comprehensive but concise. Focus on the essential context that would help resume this work later."""
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
        log_debug("=== generate_memory_with_llm() END (success) ===")
        return response.content[0].text
    except Exception as e:
        log_error(f"LLM summarization failed: {e}")
        log_debug(f"Exception type: {type(e).__name__}")
        log_debug("=== generate_memory_with_llm() END (exception) ===")
        return None


def generate_memory_structured(content: dict, session_info: dict) -> str:
    """Generate structured memory without LLM (fallback)."""
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

    # Include custom instructions if provided
    custom_instructions = session_info.get('custom_instructions', '')
    custom_section = ""
    if custom_instructions:
        custom_section = f"""
## Custom Instructions
{custom_instructions}
"""

    memory = f"""# Session Summary (Structured Extraction)

## Metadata
- **Session ID:** {session_info.get('session_id', 'unknown')}
- **Project:** {session_info.get('cwd', 'unknown')}
- **Trigger:** {session_info.get('trigger', 'unknown')}
- **Permission Mode:** {session_info.get('permission_mode', 'default')}
- **Hook Event:** {session_info.get('hook_event_name', 'PreCompact')}
- **Timestamp:** {session_info.get('timestamp', 'unknown')}
- **Total Messages:** {content.get('message_count', 0)}
{custom_section}

## Files Modified
{chr(10).join(f'- `{f}`' for f in files_modified) if files_modified else '- None tracked'}

## Tool Usage
{chr(10).join(f'- {tool}: {count} calls' for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1])[:10]) if tool_counts else '- None tracked'}

## Sample User Requests
{chr(10).join(f'- {msg[:200]}...' if len(msg) > 200 else f'- {msg}' for msg in user_messages[:5]) if user_messages else '- None captured'}

## Keywords
{', '.join(list(topics)[:15]) if topics else 'None extracted'}

---
*Note: This is a structured extraction. LLM-based memory unavailable (no API key or error).*
"""
    return memory


def generate_memory(content: dict, session_info: dict) -> str:
    """Generate memory with LLM, falling back to structured extraction."""
    # Try LLM first
    llm_memory = generate_memory_with_llm(content, session_info)
    if llm_memory:
        return llm_memory

    # Fall back to structured extraction
    log_info("Using structured extraction (LLM unavailable)")
    return generate_memory_structured(content, session_info)


# ============================================================================
# File Storage
# ============================================================================

def get_memories_dir(project_path: str) -> Path:
    """Get the memories directory for the project."""
    return Path(project_path) / ".claude" / "memories"


def save_memory(
    session_id: str,
    memory: str,
    metadata: dict,
    project_path: str
) -> Path:
    """Save memory and metadata to file system with timestamp versioning."""
    memories_dir = get_memories_dir(project_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create session/timestamp directory
    session_dir = memories_dir / session_id / timestamp
    session_dir.mkdir(parents=True, exist_ok=True)

    # Save memory as JSON
    memory_data = {
        "content": memory,
        "timestamp": timestamp,
        "session_id": session_id
    }
    memory_path = session_dir / "memory.json"
    memory_path.write_text(json.dumps(memory_data, indent=2, ensure_ascii=False), encoding='utf-8')

    # Save metadata
    metadata['memory_timestamp'] = timestamp
    metadata_path = session_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')

    # Update latest symlink
    latest_link = memories_dir / session_id / "latest"
    if latest_link.is_symlink():
        latest_link.unlink()
    elif latest_link.exists():
        latest_link.unlink()

    try:
        latest_link.symlink_to(timestamp)
    except OSError as e:
        log_error(f"Failed to create latest symlink: {e}")

    # Update global index
    update_index(memories_dir, session_id, timestamp, metadata)

    return memory_path


def update_index(memories_dir: Path, session_id: str, timestamp: str, metadata: dict):
    """Update the memories index file."""
    index_path = memories_dir / "index.json"

    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            index = {"memories": [], "last_session": None}
    else:
        index = {"memories": [], "last_session": None}

    # Add new entry at the beginning
    entry = {
        "session_id": session_id,
        "timestamp": timestamp,
        "created_at": metadata.get('timestamp', ''),
        "trigger": metadata.get('trigger', ''),
        "project": metadata.get('cwd', ''),
        "message_count": metadata.get('message_count', 0),
        "memory_path": f"{session_id}/{timestamp}/memory.json"
    }

    index["memories"].insert(0, entry)
    index["last_session"] = session_id

    # Keep only last 100 entries
    index["memories"] = index["memories"][:100]

    # Ensure directory exists
    memories_dir.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding='utf-8')


def extract_topics_from_memory(memory: str) -> list[str]:
    """Extract topic tags from memory."""
    # Look for hashtags
    hashtags = re.findall(r'#(\w+)', memory)
    return list(set(hashtags))[:10]


# ============================================================================
# Nowledge MCP Integration (HttpConnector)
# Follows pattern from: specification/11-mcp-http-connector/template_connector.py
# ============================================================================

# Server pattern to match in Claude Code config (lowercase)
NOWLEDGE_SERVER_PATTERN = "nowledge"


def find_mcp_config(server_pattern: str) -> dict | None:
    """Find MCP server config from Claude Code settings.

    This function follows the standard MCP HTTP Connector pattern from
    specification/11-mcp-http-connector/template_connector.py

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
                        # Accept http or streamableHttp types for HTTP-based servers
                        server_type = server_config.get("type", "")
                        if server_type in ("http", "streamableHttp"):
                            return {
                                "name": name,
                                "url": server_config.get("url"),
                                "headers": server_config.get("headers", {})
                            }
            except (json.JSONDecodeError, IOError):
                continue

    return None


async def call_nowledge_tools(mcp_config: dict, memory: str, metadata: dict) -> dict:
    """Call nowledge MCP tools via HttpConnector.

    This function follows the standard MCP HTTP Connector pattern from
    specification/11-mcp-http-connector/template_connector.py

    Args:
        mcp_config: Dict with name, url, headers from find_mcp_config()
        memory: Session memory to persist
        metadata: Session metadata

    Returns:
        Dict with success status for each tool
    """
    from mcp_use.client.connectors import HttpConnector

    url = mcp_config.get("url")
    headers = mcp_config.get("headers", {})
    results = {"memory": False, "thread": False}

    if not url:
        log_debug("MCP server URL not found in config")
        return results

    connector = None
    try:
        # Create HttpConnector and connect
        connector = HttpConnector(base_url=url, headers=headers)
        await connector.connect()

        # List available tools (useful for debugging)
        tools = await connector.list_tools()
        tool_names = [t.name for t in tools]
        log_debug(f"Available tools: {tool_names}")

        # 1. Add memory with distilled insights
        if "memory_add" in tool_names:
            log_debug("Calling memory_add...")
            try:
                topics = metadata.get("topics", [])
                files_modified = metadata.get("files_modified", [])
                session_id = metadata.get("session_id", "unknown")
                project = metadata.get("cwd", "unknown")

                memory_content = f"""Session {session_id[:8]} - {project}

Key topics: {', '.join(topics[:5]) if topics else 'None'}
Files modified: {len(files_modified)}
Message count: {metadata.get('message_count', 0)}

Summary excerpt:
{memory[:1500]}"""

                result = await connector.call_tool(
                    name="memory_add",
                    arguments={
                        "content": memory_content,
                        "title": f"Claude Code Session: {', '.join(topics[:3]) if topics else session_id[:8]}",
                        "importance": 0.7,
                        "labels": ",".join(["claude-code", "session-memory"] + topics[:3]),
                        "source": "context-keeper-precompact"
                    }
                )
                log_debug(f"memory_add result: {result}")
                results["memory"] = True
                log_info("Memory persisted to nowledge")
            except Exception as e:
                log_debug(f"memory_add failed: {e}")

        # 2. Persist full thread
        if "thread_persist" in tool_names:
            log_debug("Calling thread_persist...")
            try:
                result = await connector.call_tool(
                    name="thread_persist",
                    arguments={
                        "client": "claude-code",
                        "project_path": metadata.get("cwd", ""),
                        "persist_mode": "current",
                        "memory": f"Session {metadata.get('session_id', 'unknown')[:8]}: {', '.join(metadata.get('topics', [])[:3])}"[:100]
                    }
                )
                log_debug(f"thread_persist result: {result}")
                results["thread"] = True
                log_info("Thread persisted to nowledge")
            except Exception as e:
                log_debug(f"thread_persist failed: {e}")

        return results

    except Exception as e:
        log_debug(f"HttpConnector error: {e}")
        return results
    finally:
        if connector:
            try:
                await connector.disconnect()
            except Exception:
                pass


def persist_to_nowledge(memory: str, metadata: dict, content: dict) -> bool:
    """
    Persist memory and thread to nowledge MCP server using HttpConnector.

    Uses mcp-use HttpConnector to connect to existing HTTP MCP server.
    Follows pattern from: specification/11-mcp-http-connector/

    Returns True if successful, False otherwise.
    Non-blocking - failures don't affect local memory storage.
    """
    log_debug("=== persist_to_nowledge() START ===")

    # Find server config using standard pattern
    mcp_config = find_mcp_config(NOWLEDGE_SERVER_PATTERN)
    if not mcp_config:
        log_debug(f"HTTP MCP server matching '{NOWLEDGE_SERVER_PATTERN}' not found in Claude Code settings")
        log_debug("=== persist_to_nowledge() END (no config) ===")
        return False

    log_debug(f"Found config: {mcp_config['name']} at {mcp_config['url']}")

    # Check if mcp-use is installed
    if not _ensure_package_installed("mcp-use"):
        log_debug("mcp-use not available, skipping nowledge integration")
        return False

    try:
        from mcp_use.client.connectors import HttpConnector
        log_debug("mcp-use HttpConnector imported successfully")
    except ImportError as e:
        log_debug(f"Failed to import mcp-use HttpConnector: {e}")
        return False

    # Check server connectivity before attempting connection
    try:
        from urllib.parse import urlparse
        import socket

        parsed = urlparse(mcp_config["url"])
        host = parsed.hostname or "localhost"
        port = parsed.port or 80

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()

        if result != 0:
            log_debug(f"MCP server not reachable at {host}:{port}")
            log_debug("=== persist_to_nowledge() END (server not running) ===")
            return False
    except Exception as e:
        log_debug(f"Connectivity check failed: {e}")
        return False

    # Run async tool calls
    try:
        import asyncio
        log_debug("Calling nowledge tools...")
        results = asyncio.run(call_nowledge_tools(mcp_config, memory, metadata))
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
    # Print visible banner to stderr
    print("\n" + "=" * 60, file=sys.stderr)
    print("🔄 [context-keeper] PreCompact Hook Running...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    try:
        # Read input from Claude Code
        hook_input = read_hook_input()

        if not hook_input:
            log_error("No input received")
            print("=" * 60 + "\n", file=sys.stderr)
            sys.exit(1)

        # Extract session information (all available fields)
        session_id = hook_input.get("session_id", "unknown")
        transcript_path = hook_input.get("transcript_path", "")
        trigger = hook_input.get("trigger", "unknown")
        cwd = hook_input.get("cwd", os.getcwd())
        permission_mode = hook_input.get("permission_mode", "default")
        hook_event_name = hook_input.get("hook_event_name", "PreCompact")
        custom_instructions = hook_input.get("custom_instructions", "")

        print(f"📋 [context-keeper] Processing session {session_id[:8]}... (trigger: {trigger})", file=sys.stderr)

        # Parse transcript
        if not transcript_path:
            log_error("No transcript path provided")
            print("=" * 60 + "\n", file=sys.stderr)
            sys.exit(1)

        print("📖 [context-keeper] Parsing transcript...", file=sys.stderr)
        messages = parse_transcript(transcript_path)
        if not messages:
            print("ℹ️  [context-keeper] No messages in transcript, skipping", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            sys.exit(0)

        print(f"📊 [context-keeper] Found {len(messages)} messages", file=sys.stderr)

        # Extract content
        content = extract_conversation_content(messages)

        # Prepare session info (include all available fields)
        session_info = {
            "session_id": session_id,
            "trigger": trigger,
            "cwd": cwd,
            "timestamp": datetime.now().astimezone().isoformat(),
            "permission_mode": permission_mode,
            "hook_event_name": hook_event_name,
            "custom_instructions": custom_instructions
        }

        # Show custom instructions if provided
        if custom_instructions:
            print(f"📝 [context-keeper] Custom instructions: {custom_instructions[:50]}{'...' if len(custom_instructions) > 50 else ''}", file=sys.stderr)

        # Generate memory
        print("🤖 [context-keeper] Generating memory with AI...", file=sys.stderr)
        memory = generate_memory(content, session_info)

        # Prepare metadata
        metadata = {
            **session_info,
            "topics": extract_topics_from_memory(memory),
            "files_modified": content.get("files_modified", []),
            "message_count": content.get("message_count", 0),
            "tool_call_count": len(content.get("tool_calls", []))
        }

        # Save to project directory
        print("💾 [context-keeper] Saving memory...", file=sys.stderr)
        memory_path = save_memory(session_id, memory, metadata, cwd)

        log_info(f"Summary saved: {memory_path}")
        log_info(f"Files modified: {len(metadata['files_modified'])}")
        log_info(f"Topics: {', '.join(metadata['topics'][:5]) if metadata['topics'] else 'none extracted'}")

        # Persist to nowledge (non-blocking, optional)
        try:
            nowledge_success = persist_to_nowledge(memory, metadata, content)
            if nowledge_success:
                print("☁️  [context-keeper] Persisted to nowledge", file=sys.stderr)
        except Exception:
            pass  # Non-blocking

        # Print visible completion message
        print("✅ [context-keeper] Session context saved successfully!", file=sys.stderr)
        print("=" * 60 + "\n", file=sys.stderr)
        sys.exit(0)

    except Exception as e:
        log_error(f"Unexpected error: {e}")
        print("=" * 60 + "\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

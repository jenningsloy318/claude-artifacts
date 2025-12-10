#!/usr/bin/env python3
"""
Save Memory Script: Summarizes and persists Claude Code sessions before compaction.

This script triggers before context compaction (manual /compact or automatic).
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

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import anthropic
from mcp_use.client.connectors import HttpConnector



# ============================================================================
# MCP Import
# ============================================================================

# ============================================================================
# Configuration
# ============================================================================


# ============================================================================
# Configuration
# ============================================================================

MAX_TOKENS = 4000
TIMEOUT_SECONDS = 90

# ============================================================================
# Type Safety Helpers
# ============================================================================

def ensure_list(value, default=None):
    """Ensure value is a list, return default or empty list if not."""
    if isinstance(value, list):
        return value
    return default if default is not None else []

def ensure_string(value, default=""):
    """Ensure value is a string, return default if not."""
    if isinstance(value, str):
        return value
    return default

# ============================================================================
# Input/Output Helpers
# ============================================================================

import logging

# ============================================================================
# Logging Configuration
# ============================================================================

# Configure logging to write to stderr
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



# ============================================================================
# Transcript Parsing
# ============================================================================

def parse_transcript(transcript_path: str) -> list[dict]:
    """Parse JSONL transcript file into messages."""
    messages = []
    path = Path(transcript_path).expanduser()

    if not path.exists():
        logging.error(f"Transcript file not found: {transcript_path}")
        return messages

    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        logging.error(f"Failed to parse line {line_num} in transcript")
    except Exception as e:
        logging.error(f"Failed to read transcript: {e}")

    return messages


def extract_conversation_content(messages: list[dict]) -> dict:
    """Extract relevant content from transcript messages."""
    user_messages = []
    assistant_messages = []
    tool_calls = []
    files_modified = set()

    # Ensure we have a list of messages
    if not isinstance(messages, list):
        logging.debug(f"Expected list of messages, got {type(messages)}")
        messages = []

    for msg in messages:
        # Skip invalid messages
        if not isinstance(msg, dict):
            continue

        msg_type = msg.get('type', '')

        # Handle Claude Code transcript format (nested message object)
        nested_msg = msg.get('message', {})
        if not isinstance(nested_msg, dict):
            nested_msg = {}

        role = nested_msg.get('role', '')
        content = nested_msg.get('content', '') if isinstance(nested_msg, dict) else msg.get('content', '')

        # User messages
        if msg_type == 'user' or role == 'user':
            if isinstance(content, str) and content.strip():
                # Skip system reminders
                if '<system-reminder>' not in content:
                    user_messages.append(content[:2000])
            elif isinstance(content, list) and content:
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text = block.get('text', '')
                        if text and '<system-reminder>' not in text:
                            user_messages.append(text[:2000])

        # Assistant messages
        elif msg_type == 'assistant' or role == 'assistant':
            if isinstance(content, str) and content.strip():
                assistant_messages.append(content[:2000])
            elif isinstance(content, list) and content:
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

    # Debug the values before returning
    logging.debug(f"[DEBUG] Before return - user_messages type: {type(user_messages)}, len: {len(user_messages) if isinstance(user_messages, list) else 'N/A'}")
    logging.debug(f"[DEBUG] Before return - assistant_messages type: {type(assistant_messages)}, len: {len(assistant_messages) if isinstance(assistant_messages, list) else 'N/A'}")
    logging.debug(f"[DEBUG] Before return - tool_calls type: {type(tool_calls)}, len: {len(tool_calls) if isinstance(tool_calls, list) else 'N/A'}")
    logging.debug(f"[DEBUG] Before return - files_modified type: {type(list(files_modified))}, len: {len(list(files_modified))}")
    logging.debug(f"[DEBUG] Before return - message_count: {len(messages)}")

    result = {
        'user_messages': user_messages,
        'assistant_messages': assistant_messages,
        'tool_calls': tool_calls,
        'files_modified': list(files_modified),
        'message_count': len(messages)
    }
    logging.debug(f"[DEBUG] Returning dict with keys: {list(result.keys())}")
    return result


# ============================================================================
# Summary Generation
# ============================================================================

def get_claude_env() -> dict:
    """Read env section from ~/.claude.json."""
    config_path = Path.home() / ".claude.json"
    logging.debug(f"Reading Claude config from: {config_path}")

    if not config_path.exists():
        logging.debug(f"Config file not found: {config_path}")
        return {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        env = config.get("env", {})
        logging.debug(f"Loaded env keys: {list(env.keys())}")
        return env
    except Exception as e:
        logging.error(f"Failed to read ~/.claude.json: {e}")
        return {}


def get_api_key() -> Optional[str]:
    """Get CLAUDE_SUMMARY_API_KEY from ~/.claude.json."""
    env = get_claude_env()
    key = env.get("CLAUDE_SUMMARY_API_KEY")
    
    if key:
        masked = key[:4] + "..." + key[-4:] if len(key) > 10 else "***"
        logging.debug(f"Found CLAUDE_SUMMARY_API_KEY in config: {masked}")
        return key
    
    logging.debug("CLAUDE_SUMMARY_API_KEY not found in config")
    return None


def get_api_url() -> Optional[str]:
    """Get CLAUDE_SUMMARY_API_URL from ~/.claude.json."""
    env = get_claude_env()
    url = env.get("CLAUDE_SUMMARY_API_URL")
    
    if url:
        logging.debug(f"Found CLAUDE_SUMMARY_API_URL in config: {url}")
        return url
        
    logging.debug("CLAUDE_SUMMARY_API_URL not found in config")
    return None


def get_model_name() -> str:
    """Get model name from ~/.claude.json or default."""
    env = get_claude_env()
    
    # 1. User specified summary model
    model = env.get("CLAUDE_SUMMARY_MODEL")
    if model:
        logging.debug(f"Using CLAUDE_SUMMARY_MODEL: {model}")
        return model
    
    logging.debug("CLAUDE_SUMMARY_MODEL not found in config")
    return None


def generate_memory_with_llm(content: dict, session_info: dict) -> Optional[str]:
    """Generate comprehensive memory using Claude API."""
    logging.debug("=== generate_memory_with_llm() START ===")

    api_key = get_api_key()
    if not api_key:
        logging.info("No API key found (set CLAUDE_SUMMARY_API_KEY)")
        logging.debug("=== generate_memory_with_llm() END (no API key) ===")
        return None

    logging.debug(f"API key obtained, length: {len(api_key)} chars")

    # Prepare content for summarization (truncate to avoid token limits)
    # Ensure all values are lists before slicing
    logging.debug(f"[DEBUG] Content type: {type(content)}")
    logging.debug(f"[DEBUG] Content keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")

    user_msgs_list = content.get('user_messages', [])
    assistant_msgs_list = content.get('assistant_messages', [])
    tool_calls_list = content.get('tool_calls', [])
    files_modified_list = content.get('files_modified', [])

    # Debug the types we got
    logging.debug(f"[DEBUG] user_msgs_list type: {type(user_msgs_list)}, value (first 100): {str(user_msgs_list)[:100]}")
    logging.debug(f"[DEBUG] assistant_msgs_list type: {type(assistant_msgs_list)}, value (first 100): {str(assistant_msgs_list)[:100]}")
    logging.debug(f"[DEBUG] tool_calls_list type: {type(tool_calls_list)}, value (first 100): {str(tool_calls_list)[:100]}")
    logging.debug(f"[DEBUG] files_modified_list type: {type(files_modified_list)}, value (first 100): {str(files_modified_list)[:100]}")

    # Ensure they are actually lists
    if not isinstance(user_msgs_list, list):
        logging.debug(f"[DEBUG] Converting user_msgs_list from {type(user_msgs_list)} to list")
        user_msgs_list = []
    if not isinstance(assistant_msgs_list, list):
        logging.debug(f"[DEBUG] Converting assistant_msgs_list from {type(assistant_msgs_list)} to list")
        assistant_msgs_list = []
    if not isinstance(tool_calls_list, list):
        logging.debug(f"[DEBUG] Converting tool_calls_list from {type(tool_calls_list)} to list")
        tool_calls_list = []
    if not isinstance(files_modified_list, list):
        logging.debug(f"[DEBUG] Converting files_modified_list from {type(files_modified_list)} to list")
        files_modified_list = []

    # Debug: Check the content of the lists before slicing
    logging.debug(f"[DEBUG] About to slice user_msgs_list (len: {len(user_msgs_list) if isinstance(user_msgs_list, list) else 'not list'})")
    logging.debug(f"[DEBUG] About to slice assistant_msgs_list (len: {len(assistant_msgs_list) if isinstance(assistant_msgs_list, list) else 'not list'})")
    logging.debug(f"[DEBUG] About to slice tool_calls_list (len: {len(tool_calls_list) if isinstance(tool_calls_list, list) else 'not list'})")

    user_msgs = user_msgs_list[:20]  # Last 20 user messages
    assistant_msgs = assistant_msgs_list[:20]
    tool_calls = tool_calls_list[:50]
    files_modified = files_modified_list

    # Debug: Check variables before building prompt
    logging.debug(f"[DEBUG] user_msgs type: {type(user_msgs)}, len: {len(user_msgs) if isinstance(user_msgs, list) else 'not list'}")
    logging.debug(f"[DEBUG] assistant_msgs type: {type(assistant_msgs)}, len: {len(assistant_msgs) if isinstance(assistant_msgs, list) else 'not list'}")
    logging.debug(f"[DEBUG] tool_calls type: {type(tool_calls)}, len: {len(tool_calls) if isinstance(tool_calls, list) else 'not list'}")
    logging.debug(f"[DEBUG] files_modified type: {type(files_modified)}, len: {len(files_modified) if isinstance(files_modified, list) else 'not list'}")

    # Check first elements of each list
    if isinstance(user_msgs, list) and len(user_msgs) > 0:
        logging.debug(f"[DEBUG] First user_msg type: {type(user_msgs[0])}")
    if isinstance(assistant_msgs, list) and len(assistant_msgs) > 0:
        logging.debug(f"[DEBUG] First assistant_msg type: {type(assistant_msgs[0])}")
    if isinstance(tool_calls, list) and len(tool_calls) > 0:
        logging.debug(f"[DEBUG] First tool_call type: {type(tool_calls[0])}")

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

    logging.debug("[DEBUG] About to build prompt string...")
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
{json.dumps([msg for msg in user_msgs if isinstance(msg, str) and len(str(msg).strip()) > 0 and '<system-reminder>' not in str(msg)][:15], indent=2, ensure_ascii=False)[:3000]}

## Key Assistant Responses
{json.dumps([msg for msg in assistant_msgs if isinstance(msg, str) and len(str(msg).strip()) > 0][:15], indent=2, ensure_ascii=False)[:3000]}

## Important Tool Operations
{json.dumps([tc for tc in tool_calls if isinstance(tc, dict) and isinstance(tc.get('tool'), str) and tc.get('tool') in ['Edit', 'Write', 'Read', 'Bash'] and not tc.get('tool') in ['NotebookEdit', 'NotebookEdit'] and not (tc.get('tool') == 'Read' and not tc.get('input', {}).get('file_path'))][:10], indent=2, ensure_ascii=False)[:2000]}

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
    logging.debug("[DEBUG] Prompt string built successfully, about to call API...")
    try:
        # Build client with optional custom base URL
        api_url = get_api_url()
        logging.debug(f"API URL obtained: {api_url if api_url else 'None (using default)'}")

        if api_url:
            logging.debug(f"Creating Anthropic client with custom base_url: {api_url}")
            client = anthropic.Anthropic(api_key=api_key, base_url=api_url)
            logging.info(f"Using custom API URL: {api_url}")
        else:
            logging.debug("Creating Anthropic client with default base_url")
            client = anthropic.Anthropic(api_key=api_key)

        model_name = get_model_name()
        logging.debug(f"Calling LLM with model: {model_name}, max_tokens: {MAX_TOKENS}")
        response = client.messages.create(
            model=model_name,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )

        # Safely extract text from response
        if hasattr(response, 'content') and response.content and len(response.content) > 0:
            content_block = response.content[0]
            if hasattr(content_block, 'text'):
                memory_text = content_block.text
                logging.debug(f"LLM response received, content length: {len(memory_text)} chars")
                logging.debug("=== generate_memory_with_llm() END (success) ===")
                return memory_text
            else:
                logging.error(f"Content block missing 'text' attribute, type: {type(content_block)}")
        else:
            logging.error(f"Unexpected response structure: {type(response)}")
            logging.error(f"Response content: {getattr(response, 'content', 'No content attr')}")

        logging.debug("=== generate_memory_with_llm() END (failed to extract text) ===")
        return None
    except Exception as e:
        logging.error(f"LLM summarization failed: {e}")
        logging.debug(f"Exception type: {type(e).__name__}")
        logging.debug("=== generate_memory_with_llm() END (exception) ===")
        return None


def generate_memory_structured(content: dict, session_info: dict) -> str:
    """Generate structured memory without LLM (fallback)."""
    files_modified = content.get('files_modified', [])
    tool_calls = content.get('tool_calls', [])
    user_messages = content.get('user_messages', [])

    # Ensure they are actually lists
    if not isinstance(files_modified, list):
        files_modified = []
    if not isinstance(tool_calls, list):
        tool_calls = []
    if not isinstance(user_messages, list):
        user_messages = []

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
    logging.info("Using structured extraction (LLM unavailable)")
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
        logging.error(f"Failed to create latest symlink: {e}")

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
NOWLEDGE_SERVER_PATTERN = "nowledge-mem"


def find_mcp_config(server_pattern: str) -> dict | None:
    """Find MCP server config from Claude Code settings.

    This function follows the standard MCP HTTP Connector pattern but
    exclusively checks ~/.claude.json as per user configuration.

    Args:
        server_pattern: Lowercase pattern to match server name

    Returns:
        Dict with name, url, headers if found, None otherwise
    """
    # Only check the main configuration file
    config_path = Path.home() / ".claude.json"
    
    logging.debug(f"Checking for MCP config in: {config_path}")

    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            mcp_servers = config.get("mcpServers", {})
            logging.debug(f"Found mcpServers: {list(mcp_servers.keys())}")

            for name, server_config in mcp_servers.items():
                # Check if pattern matches
                if server_pattern in name.lower():
                    logging.debug(f"Found matching server: {name}")
                    
                    # Accept http or streamableHttp types for HTTP-based servers
                    # Also accept missing type if url is present (common in some configs)
                    server_type = server_config.get("type", "unknown")
                    url = server_config.get("url")
                    
                    if url and (server_type in ("http", "streamableHttp") or server_type == "unknown"):
                        return {
                            "name": name,
                            "url": url,
                            "headers": server_config.get("headers", {})
                        }
                    else:
                        logging.debug(f"Server {name} skipped: type={server_type}, has_url={bool(url)}")
                        
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Failed to read config: {e}")

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
    
    # Check if mcp-use is available (handled by top-level import now, 
    # capturing ImportWarning/Error if module missing might be done at module level or here if we want to be safe)
    # But user requested top level import.
    
    url = mcp_config.get("url")
    headers = mcp_config.get("headers", {})
    results = {"memory": False}

    if not url:
        logging.debug("MCP server URL not found in config")
        return results

    connector = None
    try:
        # Create HttpConnector and connect
        logging.debug(f"Creating HttpConnector to {url}")
        connector = HttpConnector(base_url=url, headers=headers)
        await connector.connect()

        # List available tools (useful for debugging)
        tools = await connector.list_tools()
        tool_names = [t.name for t in tools]
        logging.debug(f"Available tools: {tool_names}")

        # Ensure we have lists for metadata
        topics = metadata.get("topics", [])
        if not isinstance(topics, list):
            topics = []

        files_modified = metadata.get("files_modified", [])
        if not isinstance(files_modified, list):
            files_modified = []

        # 1. Add memory with distilled insights
        if "memory_add" in tool_names:
            logging.debug("Calling memory_add...")
            try:
                session_id = metadata.get("session_id", "unknown")
                project = metadata.get("cwd", "unknown")

                memory_content = f"""Session {session_id[:8]} - {project}

Key topics: {', '.join(topics[:5]) if topics else 'None'}
Files modified: {len(files_modified)}
Message count: {metadata.get('message_count', 0)}

Full Session Memory:
{memory}"""

                result = await connector.call_tool(
                    name="memory_add",
                    arguments={
                        "content": memory_content,
                        "title": f"Claude Code Session: {', '.join(topics[:3]) if topics else session_id[:8]}",
                        "importance": 0.7,
                        "labels": ",".join(["claude-code", "session-memory"] + topics[:3])
                    }
                )
                logging.debug(f"memory_add result: {result}")
                results["memory"] = True
                logging.info("Memory persisted to nowledge")
            except Exception as e:
                logging.debug(f"memory_add failed: {e}")

        # Note: Thread persistence is handled by save_thread.py at session end

        return results

    except Exception as e:
        logging.debug(f"HttpConnector error: {e}")
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
    logging.debug("=== persist_to_nowledge() START ===")

    # Find server config using standard pattern
    mcp_config = find_mcp_config(NOWLEDGE_SERVER_PATTERN)
    if not mcp_config:
        logging.debug(f"HTTP MCP server matching '{NOWLEDGE_SERVER_PATTERN}' not found in Claude Code settings")
        logging.debug("=== persist_to_nowledge() END (no config) ===")
        return False

    logging.debug(f"Found config: {mcp_config['name']} at {mcp_config['url']}")
    # Run async tool calls
    try:
        import asyncio
        logging.debug("Calling nowledge tools...")
        results = asyncio.run(call_nowledge_tools(mcp_config, memory, metadata))
        success = results.get("memory", False)
        logging.debug(f"=== persist_to_nowledge() END (success={success}) ===")
        return success

    except Exception as e:
        logging.debug(f"persist_to_nowledge error: {e}")
        logging.debug("=== persist_to_nowledge() END (exception) ===")
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
        raw_input = sys.stdin.read()
        
        if not raw_input.strip():
            logging.error("No input received (stdin is empty)")
            print("=" * 60 + "\n", file=sys.stderr)
            sys.exit(1)
            
        try:
            hook_input = json.loads(raw_input)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON input: {e}")
            logging.debug(f"Raw input snippet: {raw_input[:200]}")
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
            logging.error("No transcript path provided")
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
        logging.debug("[DEBUG] Starting extract_conversation_content...")
        content = extract_conversation_content(messages)
        logging.debug(f"[DEBUG] Extracted content type: {type(content)}")
        logging.debug(f"[DEBUG] Extracted content keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")

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
        
        logging.info(f"Summary saved: {memory_path}")
        logging.info(f"Files modified: {len(metadata['files_modified'])}")
        logging.info(f"Topics: {', '.join(metadata['topics'][:5]) if metadata['topics'] else 'none extracted'}")

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
        logging.error(f"Unexpected error: {e}")
        print("=" * 60 + "\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Save Thread Script: Persists full Claude Code session threads at session end.

This script is designed to be called when a Claude Code session ends.
It parses the local transcript and sends the complete conversation thread
directly to the Nowledge REST API.

Usage:
  python save_thread.py --session-id <id> --project-path <path> --summary <text>

Integration:
- Reads: Local transcript JSONL file
- Sends to: http://127.0.0.1:14242/threads (POST)

Exit codes:
  0 - Success
  1 - Error occurred
"""

import sys
import json
import os
import argparse
import logging
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ============================================================================
# Configuration
# ============================================================================

NOWLEDGE_API_URL = "http://127.0.0.1:14242/threads"

# ============================================================================
# Argument Parsing
# ============================================================================

def parse_arguments():
    """Parse command line arguments (optional overrides)."""
    parser = argparse.ArgumentParser(
        description="Save Claude Code session thread to nowledge"
    )
    parser.add_argument("--session-id", help="Session ID")
    parser.add_argument("--project-path", help="Project path")
    parser.add_argument("--summary", default="", help="Summary")
    parser.add_argument("--transcript-path", help="Path to transcript file")
    return parser.parse_args()

# ============================================================================
# Transcript Parsing (Logic ported from save_memory.py)
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

def extract_thread_content(messages: list[dict]) -> list[dict]:
    """
    Extract clean sequence of messages for the thread.
    Returns: List of {role, content, timestamp}
    """
    clean_messages = []
    
    for msg in messages:
        if not isinstance(msg, dict):
            continue

        # Handle Claude Code transcript format
        nested_msg = msg.get('message', {})
        if not isinstance(nested_msg, dict):
            # Fallback for simpler format
            nested_msg = msg 
            
        role = nested_msg.get('role') or msg.get('type')
        content = nested_msg.get('content') or msg.get('content')
        timestamp = nested_msg.get('created_at') or msg.get('timestamp') or msg.get('created_at')

        # Normalize content
        final_content = ""
        
        if isinstance(content, str):
            final_content = content
        elif isinstance(content, list):
            # Concatenate text blocks
            parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get('type') == 'text':
                        parts.append(block.get('text', ''))
                    elif block.get('type') == 'tool_use':
                        parts.append(f"[Tool Call: {block.get('name')}]")
            final_content = "\n".join(parts)
            
        if final_content and role in ['user', 'assistant']:
             # Skip empty system prompts or reminders if requested
            if '<system-reminder>' in final_content:
                continue

            clean_messages.append({
                "role": role,
                "content": final_content,
                "created_at": timestamp
            })

    return clean_messages

# ============================================================================
# Persistence Logic
# ============================================================================

def persist_thread_to_nowledge(session_id: str, project_path: str, clean_messages: list, metadata: dict) -> bool:
    """Send thread to Nowledge REST API."""
    
    # Construct Payload
    # Using 'slug' as the stable identifier for updates if supported, or just 'title'
    title = f"Session {session_id[:8]} ({os.path.basename(project_path)})"
    
    payload = {
        "thread_id": session_id,
        "title": title,
        "messages": clean_messages,
        "metadata": {
            **metadata,
            "session_id": session_id,
            "project_path": project_path,
            "message_count": len(clean_messages),
            "source": "claude-code-context-keeper"
        },
        # Extra fields that might be supported/useful
        "external_id": session_id,
        "provider": "claude-code",
        "tags": ["claude-session", "auto-save"]
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            NOWLEDGE_API_URL, 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        
        logging.info(f"[save-thread] Sending {len(clean_messages)} messages to {NOWLEDGE_API_URL}...")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if 200 <= response.status < 300:
                logging.info(f"[save-thread] Success via REST API. Status: {response.status}")
                return True
            else:
                logging.error(f"[save-thread] Failed. Status: {response.status}")
                return False
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='ignore')
        logging.error(f"[save-thread] Connection failed: {e}")
        logging.error(f"[save-thread] Server Response: {error_body}")
        return False
    except Exception as e:
        logging.error(f"[save-thread] Connection failed: {e}")
        return False

# ============================================================================
# Main
# ============================================================================

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(funcName)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler('/tmp/context-keeper-thread-debug.log'),
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(sys.stderr)
        ]
    )
    
    logging.info("\n" + "=" * 60)
    logging.info("[save-thread] Thread Persistence Hook Running...")
    logging.info("=" * 60)

    try:
        # 1. Read Input
        hook_input = {}
        if not sys.stdin.isatty():
             try:
                 hook_input = json.loads(sys.stdin.read())
             except:
                 pass
                 
        args = parse_arguments()
        
        session_id = args.session_id or hook_input.get("session_id")
        project_path = args.project_path or hook_input.get("cwd")
        transcript_path = args.transcript_path or hook_input.get("transcript_path")
        
        if not session_id or not project_path:
            logging.error("Missing session_id or project_path")
            sys.exit(1)
            
        if not transcript_path or not os.path.exists(transcript_path):
            # Try to infer transcript path if not provided (fallback)
            # Typically Claude provides it. If missing, we can't save thread.
            logging.error(f"Transcript not found: {transcript_path}")
            sys.exit(1)

        # 2. Parse Transcript
        logging.info(f"Parsing transcript: {transcript_path}")
        raw_messages = parse_transcript(transcript_path)
        clean_messages = extract_thread_content(raw_messages)
        logging.info(f"Extracted {len(clean_messages)} valid messages")
        
        # 3. Persist
        metadata = {
            "trigger": hook_input.get("trigger", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
        
        success = persist_thread_to_nowledge(session_id, project_path, clean_messages, metadata)
        
        if success:
             logging.info("✅ [context-keeper] Thread saved to Nowledge")
             sys.exit(0)
        else:
             logging.error("❌ [context-keeper] Failed to save thread")
             sys.exit(1)

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
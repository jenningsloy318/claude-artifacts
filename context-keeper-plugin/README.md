# Context Keeper Plugin for Claude Code

Automatically summarize and persist conversation context before compaction, with automatic context restoration on resume.

## Features

- **Automatic Context Memories**: Generates comprehensive memories before context compaction (manual `/compact` or automatic)
- **Context Restoration**: Automatically reloads context when resuming after compaction
- **Timestamp-based Versioning**: Multiple compactions create versioned snapshots
- **Manual Loading**: Load previous memories via `/load-memory` command
- **Context Management Skill**: Natural language context queries ("list my contexts", "load previous context")
- **LLM or Structured Extraction**: Uses Claude API for intelligent memories, with graceful fallback to structured extraction

## Installation

### Step 1: Add Marketplace and Install Plugin

```bash
# Add the marketplace
claude plugin marketplace add jenningsloy318/super-skill-claude-artifacts

# Install the plugin
claude plugin install context-keeper@super-skill-claude-artifacts
```

### Step 2: Restart Claude Code

Restart Claude Code for the plugin to take effect. The hooks are automatically registered from the plugin manifest - no manual configuration needed.

## Quick Start

```bash
# 1. Add marketplace and install plugin
claude plugin marketplace add jenningsloy318/super-skill-claude-artifacts
claude plugin install context-keeper@super-skill-claude-artifacts

# 2. (Optional) Set API key for LLM-based memories
export CLAUDE_SUMMARY_API_KEY="your-api-key"

# 3. Restart Claude Code

# 4. Use Claude Code normally - memories are automatic!
```

## Requirements

- Python 3.8+
- `anthropic` Python package (for LLM-based memories)

```bash
pip install anthropic
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `CLAUDE_SUMMARY_API_KEY` | Dedicated API key for Claude LLM summarization | No |
| `CLAUDE_SUMMARY_API_URL` | Custom API base URL (for proxy or regional endpoints) | No |

**Note**: Without `CLAUDE_SUMMARY_API_KEY`, the plugin will use structured extraction (keyword-based memory) instead of LLM-generated memories.

### Setting Environment Variables

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export CLAUDE_SUMMARY_API_KEY="your-api-key-here"
# Optional: Custom API URL
# export CLAUDE_SUMMARY_API_URL="https://your-proxy.example.com/v1"
```

## How It Works

### On Compaction (PreCompact Hook)

1. Hook receives context metadata via stdin
2. Reads full transcript from transcript_path
3. Extracts: user messages, assistant responses, tool calls, files modified
4. Generates memory (LLM if API key available, structured extraction otherwise)
5. Saves to `.claude/memories/{context_id}/{timestamp}/`
6. Updates index.json
7. Creates/updates "latest" symlink

### On Resume (SessionStart Hook)

1. Hook receives context metadata
2. Checks for existing memories in project
3. Loads most recent memory (within 24 hours)
4. Outputs context to stdout (injected into Claude's context)

## Storage Structure

Summaries are stored per-project:

```
{PROJECT}/.claude/memories/
├── index.json                          # Global index of all memories
└── {context_id}/
    ├── {timestamp}/
    │   ├── memory.json                # Memory stored as JSON
    │   └── metadata.json               # Machine-readable metadata
    └── latest -> {timestamp}           # Symlink to most recent
```

## Usage

### Automatic (After Compaction)

Just use Claude Code normally. When compaction occurs:
1. PreCompact hook automatically saves context memory
2. SessionStart hook automatically reloads context

### Manual Loading

```
/load-memory              # Load most recent memory
/load-memory abc123       # Load specific memory by ID
```

### Context Management

Ask Claude naturally:
- "What contexts do I have?"
- "List my context history"
- "Load the previous context"
- "Show memories for this project"

## Summary Content

### With LLM (API key available)

- **Topics Discussed**: Main themes and subjects
- **Code Changes**: Files modified with descriptions
- **Decisions Made**: Key decisions with rationale
- **Key Outcomes**: What was accomplished
- **Context for Continuation**: Important context for resuming
- **Tags**: Hashtags for categorization

### Structured Extraction (No API key)

- **Metadata**: Context ID, project, trigger, timestamp
- **Files Modified**: List of files created/edited
- **Tool Usage**: Breakdown of tools used
- **Sample User Requests**: Key user messages
- **Keywords**: Extracted keywords for searchability

## Troubleshooting

### Hook Not Triggering

1. Verify plugin is installed: `claude plugin list`
2. Ensure Python 3 is available: `which python3`

### No Summary Generated

1. Check stderr for errors
2. Verify transcript_path exists and is readable

### LLM Summary Failing

1. Verify API key is set: `echo $CLAUDE_SUMMARY_API_KEY`
2. Check anthropic package is installed: `pip show anthropic`
3. Verify API key has appropriate permissions

## Repository

- **GitHub**: https://github.com/jenningsloy318/super-skill-claude-artifacts
- **Issues**: https://github.com/jenningsloy318/super-skill-claude-artifacts/issues

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please open an issue or submit a pull request at https://github.com/jenningsloy318/super-skill-claude-artifacts

## Changelog

### v1.1.0

- Remove `ANTHROPIC_API_KEY` fallback
- Use dedicated `CLAUDE_SUMMARY_API_KEY` exclusively for summarization
- Simplify configuration with single API key requirement
- Add nowledge MCP integration via HttpConnector

### v1.0.0

- Initial release
- PreCompact hook for automatic context summarization
- SessionStart hook for context restoration
- Slash command for manual context loading
- Context management skill
- Support for custom API URL
- Graceful fallback to structured extraction

# Session Persistence Plugin for Claude Code

Automatically summarize and persist Claude Code sessions before context compaction, with automatic context restoration on resume.

## Features

- **Automatic Session Summaries**: Generates comprehensive summaries before context compaction (manual `/compact` or automatic)
- **Context Restoration**: Automatically reloads session context when resuming after compaction
- **Timestamp-based Versioning**: Multiple compactions within the same session create versioned snapshots
- **Manual Loading**: Load previous sessions via `/load-session` command
- **Session Management Skill**: Natural language session queries ("list my sessions", "load previous session")
- **LLM or Structured Extraction**: Uses Claude API for intelligent summaries, with graceful fallback to structured extraction

## Installation

### Option 1: Via Marketplace (Recommended)

```bash
# Add the marketplace
claude plugin marketplace add jenningsloy318/claude-artifacts

# Install the plugin
claude plugin install session-persistence@claude-artifacts
```

### Option 2: Clone and Use with --plugin-dir

```bash
# Clone the repository
git clone https://github.com/jenningsloy318/claude-artifacts.git
cd claude-artifacts

# Run Claude Code with the plugin loaded
claude --plugin-dir ./session-persistence-plugin
```

### Option 3: Clone Plugin Only

```bash
# Clone the repository
git clone https://github.com/jenningsloy318/claude-artifacts.git

# Copy the plugin to your preferred location
cp -r claude-artifacts/session-persistence-plugin ~/plugins/

# Run Claude Code with the plugin
claude --plugin-dir ~/plugins/session-persistence-plugin
```

### Option 4: Manual Installation

Copy the contents to your Claude Code user directory:

```bash
# Clone first
git clone https://github.com/jenningsloy318/claude-artifacts.git
cd claude-artifacts/session-persistence-plugin

# Create directories
mkdir -p ~/.claude/hooks
mkdir -p ~/.claude/commands
mkdir -p ~/.claude/skills/session-manager

# Copy files
cp hooks/precompact.py ~/.claude/hooks/
cp hooks/session_start.py ~/.claude/hooks/
cp commands/load-session.md ~/.claude/commands/
cp skills/session-manager/SKILL.md ~/.claude/skills/session-manager/

# Make hooks executable
chmod +x ~/.claude/hooks/precompact.py
chmod +x ~/.claude/hooks/session_start.py
```

Then add the following to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/precompact.py",
            "timeout": 120
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "resume|compact",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/session_start.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

## Requirements

- Python 3.8+
- `anthropic` Python package (for LLM-based summaries)

```bash
pip install anthropic
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `CLAUDE_SUMMARY_API_KEY` | API key for Claude LLM summarization | No (has fallback) |
| `ANTHROPIC_API_KEY` | Fallback API key | No |
| `CLAUDE_SUMMARY_API_URL` | Custom API base URL (for proxy or regional endpoints) | No |

**Note**: Without an API key, the plugin will use structured extraction (keyword-based summary) instead of LLM-generated summaries.

### Setting Environment Variables

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export CLAUDE_SUMMARY_API_KEY="your-api-key-here"
# Optional: Custom API URL
# export CLAUDE_SUMMARY_API_URL="https://your-proxy.example.com/v1"
```

## Quick Start

```bash
# Option A: Via marketplace (recommended)
claude plugin marketplace add jenningsloy318/claude-artifacts
claude plugin install session-persistence@claude-artifacts

# Option B: Via --plugin-dir
git clone https://github.com/jenningsloy318/claude-artifacts.git
cd claude-artifacts
claude --plugin-dir ./session-persistence-plugin
```

Then optionally set up LLM-based summaries:

```bash
export CLAUDE_SUMMARY_API_KEY="your-api-key"
```

## How It Works

### On Compaction (PreCompact Hook)

1. Hook receives session metadata via stdin
2. Reads full transcript from transcript_path
3. Extracts: user messages, assistant responses, tool calls, files modified
4. Generates summary (LLM if API key available, structured extraction otherwise)
5. Saves to `.claude/summaries/{session_id}/{timestamp}/`
6. Updates index.json
7. Creates/updates "latest" symlink

### On Session Resume (SessionStart Hook)

1. Hook receives session metadata
2. Checks for existing summaries in project
3. Loads most recent summary (within 24 hours)
4. Outputs context to stdout (injected into Claude's context)

## Storage Structure

Summaries are stored per-project:

```
{PROJECT}/.claude/summaries/
├── index.json                          # Global index of all summaries
└── {session_id}/
    ├── {timestamp}/
    │   ├── summary.md                  # Human-readable summary
    │   └── metadata.json               # Machine-readable metadata
    └── latest -> {timestamp}           # Symlink to most recent
```

## Usage

### Automatic (After Compaction)

Just use Claude Code normally. When compaction occurs:
1. PreCompact hook automatically saves session summary
2. SessionStart hook automatically reloads context

### Manual Loading

```
/load-session              # Load most recent session
/load-session abc123       # Load specific session by ID
```

### Session Management

Ask Claude naturally:
- "What sessions do I have?"
- "List my session history"
- "Load the previous session"
- "Show summaries for this project"

## Summary Content

### With LLM (API key available)

- **Topics Discussed**: Main themes and subjects
- **Code Changes**: Files modified with descriptions
- **Decisions Made**: Key decisions with rationale
- **Key Outcomes**: What was accomplished
- **Context for Continuation**: Important context for resuming
- **Tags**: Hashtags for categorization

### Structured Extraction (No API key)

- **Metadata**: Session ID, project, trigger, timestamp
- **Files Modified**: List of files created/edited
- **Tool Usage**: Breakdown of tools used
- **Sample User Requests**: Key user messages
- **Keywords**: Extracted keywords for searchability

## Troubleshooting

### Hook Not Triggering

1. Verify plugin is loaded: check Claude Code startup messages
2. For manual install: verify hooks are in `~/.claude/hooks/`
3. Check `~/.claude/settings.json` has correct hook configuration
4. Ensure Python 3 is available: `which python3`

### No Summary Generated

1. Check stderr for errors: `python3 ~/.claude/hooks/precompact.py < test_input.json`
2. Verify transcript_path exists and is readable
3. Check file permissions on hooks directory

### LLM Summary Failing

1. Verify API key is set: `echo $CLAUDE_SUMMARY_API_KEY`
2. Check anthropic package is installed: `pip show anthropic`
3. Verify API key has appropriate permissions

## Repository

- **GitHub**: https://github.com/jenningsloy318/claude-artifacts
- **Issues**: https://github.com/jenningsloy318/claude-artifacts/issues

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please open an issue or submit a pull request at https://github.com/jenningsloy318/claude-artifacts

## Changelog

### v1.0.0

- Initial release
- PreCompact hook for automatic session summarization
- SessionStart hook for context restoration
- Slash command for manual session loading
- Session management skill
- Support for custom API URL
- Graceful fallback to structured extraction

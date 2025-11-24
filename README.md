# Claude Artifacts

A collection of Claude Code plugins, tools, and extensions.

## Plugins

| Plugin | Description | Status |
|--------|-------------|--------|
| [session-persistence](./session-persistence-plugin/) | Automatically summarize and persist Claude Code sessions before context compaction | v1.0.0 |

## Installation

### Using Claude CLI

```bash
# Install a specific plugin (once published to marketplace)
claude plugin install <plugin-name>

# Or load from local directory
claude --plugin-dir ./session-persistence-plugin
```

### Manual Installation

See individual plugin README files for manual installation instructions.

## Plugins Overview

### Session Persistence Plugin

Automatically saves session summaries before context compaction and restores context on resume.

**Features:**
- PreCompact hook for automatic session summarization
- SessionStart hook for context restoration
- `/load-session` command for manual loading
- Session management skill for natural language queries
- LLM-based or structured extraction summaries

**Quick Start:**
```bash
# Optional: Set API key for LLM-based summaries
export CLAUDE_SUMMARY_API_KEY="your-api-key"

# Load the plugin
claude --plugin-dir ./session-persistence-plugin
```

See [session-persistence-plugin/README.md](./session-persistence-plugin/README.md) for full documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See individual plugin directories for specific licenses.

## Repository Structure

```
claude-artifacts/
├── README.md                      # This file
├── session-persistence-plugin/    # Session persistence plugin
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── hooks/
│   ├── commands/
│   ├── skills/
│   └── README.md
├── specification/                 # Design documents and specs
└── [future-plugins]/              # More plugins to come
```

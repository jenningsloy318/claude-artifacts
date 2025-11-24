# Claude Artifacts

A Claude Code plugin marketplace for session management, context persistence, and productivity tools.

**Repository**: https://github.com/jenningsloy318/claude-artifacts

## Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| [session-persistence](./session-persistence-plugin/) | Automatically summarize and persist Claude Code sessions before context compaction | v1.0.0 |

## Installation

### Method 1: Add as Marketplace (Recommended)

Add this repository as a marketplace to install plugins easily:

```bash
# Add the marketplace
claude plugin marketplace add jenningsloy318/claude-artifacts

# Install a plugin from this marketplace
claude plugin install session-persistence@claude-artifacts
```

### Method 2: Clone and Use with --plugin-dir

```bash
# Clone the repository
git clone https://github.com/jenningsloy318/claude-artifacts.git
cd claude-artifacts

# Run Claude Code with a specific plugin
claude --plugin-dir ./session-persistence-plugin
```

### Method 3: Manual Installation

See individual plugin README files for manual installation instructions.

## Quick Start: Session Persistence Plugin

```bash
# Option A: Via marketplace (after adding)
claude plugin marketplace add jenningsloy318/claude-artifacts
claude plugin install session-persistence@claude-artifacts

# Option B: Via --plugin-dir
git clone https://github.com/jenningsloy318/claude-artifacts.git
cd claude-artifacts
claude --plugin-dir ./session-persistence-plugin
```

Then optionally set up environment variables for LLM-based summaries:

```bash
export CLAUDE_SUMMARY_API_KEY="your-api-key"
```

## Marketplace Management

```bash
# Add this marketplace
claude plugin marketplace add jenningsloy318/claude-artifacts

# List all marketplaces
claude plugin marketplace list

# Update marketplace (fetch latest plugins)
claude plugin marketplace update claude-artifacts

# Remove marketplace
claude plugin marketplace remove claude-artifacts
```

## Plugins Overview

### Session Persistence Plugin

Automatically saves session summaries before context compaction and restores context on resume.

**Features:**
- PreCompact hook for automatic session summarization
- SessionStart hook for context restoration
- `/load-session` command for manual loading
- Session management skill for natural language queries
- LLM-based or structured extraction summaries

**Environment Variables:**

| Variable | Description | Required |
|----------|-------------|----------|
| `CLAUDE_SUMMARY_API_KEY` | API key for Claude LLM summarization | No (has fallback) |
| `ANTHROPIC_API_KEY` | Fallback API key | No |
| `CLAUDE_SUMMARY_API_URL` | Custom API base URL | No |

See [session-persistence-plugin/README.md](./session-persistence-plugin/README.md) for full documentation.

## Repository Structure

```
claude-artifacts/
├── .claude-plugin/
│   └── marketplace.json           # Marketplace manifest
├── README.md                      # This file
├── session-persistence-plugin/    # Session persistence plugin
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── hooks/
│   │   ├── hooks.json
│   │   ├── precompact.py
│   │   └── session_start.py
│   ├── commands/
│   │   └── load-session.md
│   ├── skills/
│   │   └── session-manager/
│   │       └── SKILL.md
│   ├── README.md
│   └── LICENSE
├── specification/                 # Design documents and specs
│   └── 01-session-persistence-plugin/
└── [future-plugins]/              # More plugins to come
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

**Issues**: https://github.com/jenningsloy318/claude-artifacts/issues

## License

MIT License - See individual plugin directories for specific licenses.

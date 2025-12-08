# Claude Artifacts

A Claude Code plugin marketplace for context persistence and productivity tools.

**Repository**: https://github.com/jenningsloy318/super-skill-claude-artifacts

## Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| [context-keeper](./context-keeper-plugin/) | Automatically summarize and persist conversation context before compaction | v1.0.0 |
| [dev-workflow](./dev-workflow-plugin/) | Comprehensive development workflow with structured phases for implementing features, fixing bugs, and refactoring | v1.0.0 |

## Getting Started

### Step 1: Install uv

If you don't have `uv` installed, install it first:

```bash
# Install uv using pipx (recommended)
pipx install uv

# Or install using curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Create Virtual Environment

Navigate to the project root and create a virtual environment with `uv`:

```bash
cd ~/.claude/plugins/marketplaces/super-skill-claude-artifacts/

# Create virtual environment with seed
uv venv --seed

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\\Scripts\\activate
```

### 3. Plugin Installation

```bash
# Add the marketplace
claude plugin marketplace add jenningsloy318/super-skill-claude-artifacts

# Install plugins
claude plugin install context-keeper@super-skill-claude-artifacts
claude plugin install dev-workflow@super-skill-claude-artifacts
```

### 4. (Optional) Configure LLM-based summaries in context-keeper

```bash
export CLAUDE_SUMMARY_API_KEY="your-api-key"
export CLAUDE_SUMMARY_API_URL="https://api.anthropic.com"
```

### 5. Use Claude Code normally - plugins are active!

**Important**: Always activate the virtual environment before running claude code:
```bash
source .venv/bin/activate
```

## Marketplace Management

```bash
# Add this marketplace
claude plugin marketplace add jenningsloy318/super-skill-claude-artifacts

# List all marketplaces
claude plugin marketplace list

# Update marketplace (fetch latest plugins)
claude plugin marketplace update super-skill-claude-artifacts

# Remove marketplace
claude plugin marketplace remove super-skill-claude-artifacts
```

## Plugins Overview

### Context Keeper Plugin

Automatically saves context summaries before compaction and restores context on resume.

**Features:**
- PreCompact hook for automatic context summarization
- SessionStart hook for context restoration
- `/load-memory` command for manual loading
- Context management skill for natural language queries
- LLM-based or structured extraction summaries

**Environment Variables:**

| Variable | Description | Required |
|----------|-------------|----------|
| `CLAUDE_SUMMARY_API_KEY` | API key for Claude LLM summarization | No (has fallback) |
| `CLAUDE_SUMMARY_API_URL` | Custom API base URL | No |

See [context-keeper-plugin/README.md](./context-keeper-plugin/README.md) for full documentation.

### Dev Workflow Plugin

A comprehensive 11-phase development workflow for implementing features, fixing bugs, and refactoring code.

**Features:**
- Structured specification and planning phases
- Research-driven implementation with multi-source search
- Specialized agents for each phase (requirements, research, debugging, coding)
- Built-in quality gates and code review

**Workflow Agents:**
| Agent | Purpose |
|-------|---------|
| `requirements-clarifier` | Gather and document complete requirements |
| `research-agent` | Find best practices and documentation |
| `search-agent` | Multi-source search for retrieval |
| `debug-analyzer` | Root cause analysis for bugs |
| `code-assessor` | Evaluate existing codebase |
| `architecture-agent` | Design architecture and create ADRs |
| `ui-ux-designer` | Create UI/UX design specifications |
| `spec-writer` | Create tech specs and implementation plans |
| `execution-coordinator` | Coordinate parallel implementation |
| `code-reviewer` | Specification-aware code review |
| `qa-agent` | Modality-specific QA testing |

**Developer Agents:**
| Agent | Purpose |
|-------|---------|
| `rust-developer` | Rust systems programming |
| `golang-developer` | Go backend development |
| `frontend-developer` | React/Next.js/TypeScript development |
| `backend-developer` | Node.js/Python backend development |
| `android-developer` | Kotlin/Jetpack Compose development |
| `ios-developer` | Swift/SwiftUI development |
| `windows-app-developer` | C#/.NET/WinUI development |
| `macos-app-developer` | Swift/SwiftUI/AppKit development |

**Skills:**
| Skill | Purpose |
|-------|---------|
| `super-dev` | Complete development workflow orchestration |
| `dev-rules` | Core development rules and philosophy |

**Commands:**
| Command | Purpose |
|---------|---------|
| `/super-dev:run` | Quick task execution for fixes and implementations |

**Usage:**
```bash
/super-dev:run Fix the login button not responding on mobile
/super-dev:run Implement user profile page with avatar upload
```

See [dev-workflow-plugin/README.md](./dev-workflow-plugin/README.md) for full documentation.

## Repository Structure

```
claude-artifacts/
├── .claude-plugin/
│   └── marketplace.json           # Marketplace manifest
├── README.md                      # This file
├── context-keeper-plugin/         # Context persistence plugin
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── hooks/
│   ├── commands/
│   ├── skills/
│   └── README.md
├── super-dev-plugin/           # Development workflow plugin
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── agents/                    # Specialized workflow agents
│   ├── commands/
│   ├── skills/
│   └── README.md
├── specification/                 # Design documents and specs
└── [future-plugins]/              # More plugins to come
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

**Issues**: https://github.com/jenningsloy318/super-skill-claude-artifacts/issues

## License

MIT License - See individual plugin directories for specific licenses.

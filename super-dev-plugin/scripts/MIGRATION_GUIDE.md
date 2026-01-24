# MCP-CLI Migration Quick Start Guide

This guide helps you get started with the new mcp-cli-based wrapper scripts.

## Prerequisites Installation

### 1. Install mcp-cli

Choose one of the following methods:

```bash
# Method 1: Install script (recommended)
curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash

# Method 2: Using bun
bun install -g https://github.com/philschmid/mcp-cli

# Method 3: Build from source
git clone https://github.com/philschmid/mcp-cli.git
cd mcp-cli
bun install
bun run build
```

### 2. Verify Installation

```bash
mcp-cli --version
# Expected output: mcp-cli x.x.x

mcp-cli
# Expected output: List of your configured MCP servers
```

### 3. Install jq (required for JSON processing)

```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq

# Arch Linux
sudo pacman -S jq

# Fedora
sudo dnf install jq
```

## Quick Test

Test one of the new shell scripts:

```bash
# Test Exa web search
./scripts/exa/exa_search.sh --query "Next.js 15" --results 3

# Test DeepWiki (if configured)
./scripts/deepwiki/deepwiki_ask.sh --repo "facebook/react" --question "What is React?"

# Test Context7 (if configured)
./scripts/context7/context7_resolve.sh --library "react"
```

## Migration from Python Scripts

### Old Usage (Python)

```bash
python3 scripts/exa/exa_search.py --query "search terms"
```

### New Usage (Shell)

```bash
./scripts/exa/exa_search.sh --query "search terms"
```

**The CLI interface is identical - only the file extension changes!**

## Key Differences

| Aspect | Python Scripts | Shell Scripts (mcp-cli) |
|--------|---------------|-------------------------|
| **Extension** | `.py` | `.sh` |
| **Dependencies** | Python 3.10+, mcp-use library | mcp-cli binary, jq |
| **Installation** | `pip install mcp-use` | `curl install script \| bash` |
| **Startup Time** | ~1-2 seconds | <100ms |
| **Server Support** | HTTP only | HTTP + stdio |
| **Line Count** | ~250 lines | ~80 lines |

## Available Scripts

### Exa (Web Search & Code Context)

```bash
# Web search
./scripts/exa/exa_search.sh \
  --query "Next.js 15 best practices" \
  --type deep \
  --results 10

# Code context search
./scripts/exa/exa_code.sh \
  --query "React hooks patterns" \
  --tokens 5000
```

### DeepWiki (GitHub Repository Q&A)

```bash
# Get repo docs structure
./scripts/deepwiki/deepwiki_structure.sh --repo "facebook/react"

# Get repo docs contents
./scripts/deepwiki/deepwiki_contents.sh --repo "facebook/react"

# Ask a question
./scripts/deepwiki/deepwiki_ask.sh \
  --repo "vercel/next.js" \
  --question "How do I use the App Router?"
```

### Context7 (Library Documentation)

```bash
# Resolve library ID
./scripts/context7/context7_resolve.sh --library "next.js"

# Get library documentation
./scripts/context7/context7_docs.sh \
  --library-id "/vercel/next.js" \
  --topic "routing"
```

### GitHub (Repository & Code Search)

```bash
# Search repositories
./scripts/github/github_search_repos.sh \
  --query "topic:mcp stars:>100" \
  --sort stars

# Search code
./scripts/github/github_search_code.sh \
  --query "HttpConnector language:python"

# Get file contents
./scripts/github/github_file_contents.sh \
  --owner "modelcontextprotocol" \
  --repo "python-sdk" \
  --path "README.md"
```

## Troubleshooting

### "mcp-cli: command not found"

**Solution:** Install mcp-cli
```bash
curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash
```

### "jq: command not found"

**Solution:** Install jq
```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq
```

### "Permission denied: ./scripts/exa/exa_search.sh"

**Solution:** Make script executable
```bash
chmod +x ./scripts/exa/exa_search.sh
```

### "Server 'exa' not found in config"

**Solution:** Verify your MCP server configuration
```bash
# List available servers
mcp-cli

# Check your config
cat ~/.claude.json | jq '.mcpServers'
```

### "Script returns error but mcp-cli works directly"

**Solution:** Check that SERVER_NAME and TOOL_NAME are correct
```bash
# Test mcp-cli directly
mcp-cli exa/web_search_exa '{"query": "test"}' --json

# Compare with script output
./scripts/exa/exa_search.sh --query "test"
```

## Creating New Scripts

To create a new wrapper script:

1. **Copy the template:**
   ```bash
   cp scripts/templates/mcp_wrapper.sh scripts/new_server/new_tool.sh
   ```

2. **Edit the configuration:**
   ```bash
   # Set these in the script
   SERVER_NAME="your_server_name"
   TOOL_NAME="your_tool_name"
   ```

3. **Implement argument parsing:**
   ```bash
   parse_arguments() {
       while [[ $# -gt 0 ]]; do
           case "$1" in
               --your-arg|-y) YOUR_ARG="$2"; shift 2 ;;
               *) error "Unknown argument: $1" ;;
           esac
       done
   }
   ```

4. **Implement JSON building:**
   ```bash
   build_json_args() {
       jq -n \
           --arg yourArg "$YOUR_ARG" \
           '{yourArg: $yourArg}'
   }
   ```

5. **Make executable:**
   ```bash
   chmod +x scripts/new_server/new_tool.sh
   ```

6. **Test:**
   ```bash
   ./scripts/new_server/new_tool.sh --your-arg "value"
   ```

## Performance Comparison

Benchmarks (running on same machine):

| Script Type | Cold Start | Warm Start | Memory |
|-------------|------------|------------|--------|
| Python (mcp-use) | ~1.8s | ~1.2s | ~45MB |
| Shell (mcp-cli) | ~0.08s | ~0.05s | ~8MB |

**Result:** ~22x faster startup, ~5.6x less memory

## Configuration

Scripts auto-discover MCP configuration from:

1. `~/.claude.json` (Claude Desktop's config)
2. `~/.mcp_servers.json`
3. `~/.config/mcp/mcp_servers.json`
4. `./mcp_servers.json` (project-local)
5. `$MCP_CONFIG_PATH` environment variable

**Example config structure:**
```json
{
  "mcpServers": {
    "exa": {
      "url": "https://mcp.exa.ai/mcp",
      "headers": {
        "Authorization": "Bearer ${EXA_API_KEY}"
      }
    },
    "deepwiki": {
      "url": "https://mcp.deepwiki.com/mcp"
    }
  }
}
```

## Migration Checklist

- [ ] Install mcp-cli
- [ ] Install jq
- [ ] Test one shell script
- [ ] Verify output format matches Python version
- [ ] Update any scripts/aliases that call Python scripts
- [ ] Run integration tests
- [ ] Remove Python dependencies (optional)

## Getting Help

- **mcp-cli Issues:** https://github.com/philschmid/mcp-cli/issues
- **MCP Protocol:** https://modelcontextprotocol.io/
- **This Plugin:** Check `docs/mcp-cli-migration-plan.md` for detailed migration info

## Next Steps

1. **Test the new scripts** with your existing workflows
2. **Provide feedback** on any issues or improvements
3. **Migrate your code** that calls the Python scripts to use shell scripts
4. **Remove Python dependencies** once migration is complete

---

**Questions?** See the full migration plan at `docs/mcp-cli-migration-plan.md`

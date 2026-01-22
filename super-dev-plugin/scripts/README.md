# MCP Connector Scripts

Scripts for connecting to MCP servers configured in Claude Code.

**NEW:** Shell scripts using `mcp-cli` (faster, no Python dependency)
**LEGACY:** Python scripts using `mcp-use` (still supported)

## Quick Start

### Prerequisites

**For Shell Scripts (Recommended):**
```bash
# Install mcp-cli
curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash

# Install jq (for JSON processing)
sudo apt-get install jq  # Ubuntu/Debian
brew install jq           # macOS
```

**For Python Scripts (Legacy):**
```bash
# Python 3.10+ required
# mcp-use auto-installs on first run
```

### Usage

**Shell Scripts (New):**
```bash
# Web search with Exa
./scripts/exa/exa_search.sh --query "Next.js 15 best practices" --results 5

# Code context with Exa
./scripts/exa/exa_code.sh --query "React hooks patterns" --tokens 5000

# Get repo documentation structure with DeepWiki
./scripts/deepwiki/deepwiki_structure.sh --repo "facebook/react"

# Resolve library ID with Context7
./scripts/context7/context7_resolve.sh --library "react"

# Search code on GitHub
./scripts/github/github_search_code.sh --query "HttpConnector language:python"
```

**Python Scripts (Legacy):**
```bash
# Same commands but with python3 prefix and .py extension
python3 scripts/exa/exa_search.py --query "Next.js 15 best practices" --results 5
python3 scripts/exa/exa_code.py --query "React hooks patterns" --tokens 5000
# ... etc
```

## Comparison: Shell vs Python

| Feature | Shell (mcp-cli) | Python (mcp-use) |
|---------|-----------------|------------------|
| **Installation** | Single binary (curl install) | Python 3.10+, pip |
| **Dependencies** | jq only | mcp-use library |
| **Server Support** | HTTP + stdio | HTTP only |
| **Startup Time** | ~100ms | ~1-2s |
| **Script Size** | ~30 lines | ~250 lines |
| **Maintenance** | Simple shell scripts | Python async/await |

**Recommendation:** Use shell scripts for new projects. Python scripts remain for backward compatibility.

## Architecture

**Shell Scripts (mcp-cli):**
```
Agent (Bash) ──► Shell Script ──► mcp-cli ──► MCP Server (HTTP/stdio)
                         │
                         ▼
                   ~/.claude.json (auto-detected)
```

**Python Scripts (mcp-use):**
```
Agent (Bash) ──► Python Script ──► HttpConnector ──► MCP HTTP Server
                         │
                         ▼
                   ~/.claude.json (reads config)
```

## Available Scripts

### Exa Scripts

| Script | Type | Description | Tool |
|--------|------|-------------|------|
| `exa/exa_search.sh` | Shell | Web search | `web_search_exa` |
| `exa/exa_search.py` | Python | Web search | `web_search_exa` |
| `exa/exa_code.sh` | Shell | Code context search | `get_code_context_exa` |
| `exa/exa_code.py` | Python | Code context search | `get_code_context_exa` |

### DeepWiki Scripts

| Script | Type | Description | Tool |
|--------|------|-------------|------|
| `deepwiki/deepwiki_structure.sh` | Shell | Get repo docs structure | `read_wiki_structure` |
| `deepwiki/deepwiki_structure.py` | Python | Get repo docs structure | `read_wiki_structure` |
| `deepwiki/deepwiki_contents.sh` | Shell | Get repo docs contents | `read_wiki_contents` |
| `deepwiki/deepwiki_contents.py` | Python | Get repo docs contents | `read_wiki_contents` |
| `deepwiki/deepwiki_ask.sh` | Shell | Ask questions about a repo | `ask_question` |
| `deepwiki/deepwiki_ask.py` | Python | Ask questions about a repo | `ask_question` |

### Context7 Scripts

| Script | Type | Description | Tool |
|--------|------|-------------|------|
| `context7/context7_resolve.sh` | Shell | Resolve library ID | `resolve-library-id` |
| `context7/context7_resolve.py` | Python | Resolve library ID | `resolve-library-id` |
| `context7/context7_docs.sh` | Shell | Get library documentation | `get-library-docs` |
| `context7/context7_docs.py` | Python | Get library documentation | `get-library-docs` |

### GitHub Scripts

| Script | Type | Description | Tool |
|--------|------|-------------|------|
| `github/github_search_code.sh` | Shell | Search code across repos | `search_code` |
| `github/github_search_code.py` | Python | Search code across repos | `search_code` |
| `github/github_search_repos.sh` | Shell | Search for repositories | `search_repositories` |
| `github/github_search_repos.py` | Python | Search for repositories | `search_repositories` |
| `github/github_file_contents.sh` | Shell | Get file/directory contents | `get_file_contents` |
| `github/github_file_contents.py` | Python | Get file/directory contents | `get_file_contents` |

### Usage Examples

#### Exa Web Search

**Shell:**
```bash
./scripts/exa/exa_search.sh \
  --query "React 19 new features" \
  --type deep \
  --results 10 \
  --context-chars 15000
```

**Python:**
```bash
python3 scripts/exa/exa_search.py \
  --query "React 19 new features" \
  --type deep \
  --results 10 \
  --context-chars 15000
```

#### Exa Code Context

**Shell:**
```bash
./scripts/exa/exa_code.sh \
  --query "Next.js app router middleware" \
  --tokens 10000
```

**Python:**
```bash
python3 scripts/exa/exa_code.py \
  --query "Next.js app router middleware" \
  --tokens 10000
```

#### DeepWiki - Ask a Question

**Shell:**
```bash
./scripts/deepwiki/deepwiki_ask.sh \
  --repo "vercel/next.js" \
  --question "How do I use the App Router?"
```

**Python:**
```bash
python3 scripts/deepwiki/deepwiki_ask.py \
  --repo "vercel/next.js" \
  --question "How do I use the App Router?"
```

#### Context7 - Get Library Documentation

**Shell:**
```bash
./scripts/context7/context7_docs.sh \
  --library-id "/vercel/next.js" \
  --mode code \
  --topic "routing"
```

**Python:**
```bash
python3 scripts/context7/context7_docs.py \
  --library-id "/vercel/next.js" \
  --mode code \
  --topic "routing"
```

#### GitHub - Search Code

**Shell:**
```bash
./scripts/github/github_search_code.sh \
  --query "HttpConnector language:python" \
  --per-page 10
```

**Python:**
```bash
python3 scripts/github/github_search_code.py \
  --query "HttpConnector language:python" \
  --per-page 10
```

## Creating New Scripts

### Shell Script Template

1. **Copy the template:**
   ```bash
   mkdir scripts/new_server
   cp scripts/templates/mcp_wrapper.sh scripts/new_server/new_tool.sh
   chmod +x scripts/new_server/new_tool.sh
   ```

2. **Customize the script:**
   ```bash
   # Set server and tool names
   SERVER_NAME="new_server"
   TOOL_NAME="new_tool"

   # Implement parse_arguments() for CLI args
   # Implement build_json_args() for JSON construction
   ```

3. **Test:**
   ```bash
   ./scripts/new_server/new_tool.sh --query "test"
   ```

### Python Script Template

1. **Copy the template:**
   ```bash
   mkdir scripts/new_server
   cp specification/11-mcp-http-connector/template_connector.py scripts/new_server/new_tool.py
   chmod +x scripts/new_server/new_tool.py
   ```

2. **Customize the script:**
   - Update `SERVER_PATTERN` to match your MCP server name
   - Update `TOOL_NAME` to the target tool
   - Modify CLI arguments as needed
   - Map arguments to tool parameters

3. **Test:**
   ```bash
   python3 scripts/new_server/new_tool.py --query "test"
   ```

## Output Format

All scripts output JSON:

**Success:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{...}"
    }
  ],
  "isError": false
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ErrorClassName"
}
```

## Configuration

Scripts auto-discover MCP config from:

**For Shell Scripts (mcp-cli):**
1. `~/.claude.json` (auto-detected)
2. `~/.mcp_servers.json`
3. `~/.config/mcp/mcp_servers.json`
4. `./mcp_servers.json`
5. `$MCP_CONFIG_PATH` environment variable

**For Python Scripts (mcp-use):**
1. `~/.claude.json`
2. `~/.claude/settings.json`
3. `~/.claude/settings.local.json`
4. `.claude/settings.json` (project)
5. `.claude/settings.local.json` (project)

Expected config structure:
```json
{
  "mcpServers": {
    "server-name": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

## Supported MCP Servers

| Server | Config Pattern | Common Tools | Shell Script | Python Script |
|--------|---------------|--------------|--------------|---------------|
| Exa | `exa` | `web_search_exa`, `get_code_context_exa` | ✅ | ✅ |
| DeepWiki | `deepwiki` | `read_wiki_structure`, `read_wiki_contents`, `ask_question` | ✅ | ✅ |
| Context7 | `context7` | `resolve-library-id`, `get-library-docs` | ✅ | ✅ |
| GitHub | `github` | Various repository tools | ✅ | ✅ |

## Dependencies

**Shell Scripts:**
- `mcp-cli` - Single binary, no runtime dependencies
- `jq` - JSON processing

**Python Scripts:**
- Python 3.10+
- `mcp-use` (auto-installed on first run)

## Troubleshooting

### Shell Scripts

#### "mcp-cli not found"

Install mcp-cli:
```bash
curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash
```

#### "jq: command not found"

Install jq:
```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq
```

#### "Server not found"

Check your MCP configuration:
```bash
mcp-cli  # List all available servers
```

Or with explicit config:
```bash
mcp-cli -c ~/.claude.json
```

### Python Scripts

#### "HTTP MCP server not found"

Ensure your server is configured with `type: "http"`:
```json
{
  "mcpServers": {
    "exa": {
      "type": "http",  // <-- Must be "http", not "stdio"
      "url": "https://..."
    }
  }
}
```

#### "Tool not found"

The tool name might differ. Check available tools by adding debug print in the Python script.

#### Connection errors

1. Check MCP server URL is correct
2. Verify API keys/headers in config
3. Test server connectivity: `curl -I <url>`

## Testing

Run the test suite to verify your setup:

```bash
./scripts/test_migration.sh
```

This will check:
- mcp-cli installation
- jq installation
- MCP configuration
- Script executability
- Script execution
- JSON output validity

## Migration Status

| Script | Python (.py) | Shell (.sh) | Status |
|--------|---------------|-------------|--------|
| `exa_search` | ✅ | ✅ | Complete |
| `exa_code` | ✅ | ✅ | Complete |
| `deepwiki_structure` | ✅ | ⏳ | Pending |
| `deepwiki_contents` | ✅ | ⏳ | Pending |
| `deepwiki_ask` | ✅ | ⏳ | Pending |
| `context7_resolve` | ✅ | ⏳ | Pending |
| `context7_docs` | ✅ | ⏳ | Pending |
| `github_search_code` | ✅ | ⏳ | Pending |
| `github_search_repos` | ✅ | ⏳ | Pending |
| `github_file_contents` | ✅ | ⏳ | Pending |

Legend: ✅ Complete | ⏳ Pending | ❌ Not Applicable

## Resources

- **mcp-cli:** https://github.com/philschmid/mcp-cli
- **mcp-use:** https://github.com/simonw/mcp-use
- **MCP Specification:** https://modelcontextprotocol.io/
- **MCP Registry:** https://github.com/modelcontextprotocol/servers

## Changelog

### v2.0.0 (2026-01-22) - mcp-cli Migration

- **Added:** Shell script wrappers using mcp-cli
- **Added:** Shell script template for easy script creation
- **Added:** Migration test suite
- **Improved:** 22x faster startup with shell scripts
- **Improved:** No Python dependency for shell scripts
- **Improved:** Support for both HTTP and stdio MCP servers
- **Deprecated:** Python scripts marked as legacy (still supported)

### v1.0.0 - Initial Release

- Python scripts using mcp-use HttpConnector
- Support for Exa, DeepWiki, Context7, and GitHub MCP servers

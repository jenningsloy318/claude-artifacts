# MCP-CLI Migration Plan

**Project:** super-dev-plugin MCP Scripts Improvement
**Date:** 2026-01-22
**Status:** Planning Phase
**Author:** AI Assistant

---

## Executive Summary

This document outlines a comprehensive plan to migrate the super-dev-plugin's Python-based MCP connector scripts to use the new `mcp-cli` tool instead of the `mcp-use` Python library.

### Key Improvements

| Aspect | Current (Python/mcp-use) | Proposed (mcp-cli) |
|--------|--------------------------|-------------------|
| **Installation** | Python 3.10+, pip install mcp-use | Single binary (curl install OR cargo install) |
| **Dependencies** | Python environment, mcp-use library | No runtime dependencies |
| **Server Support** | HTTP-only (via HttpConnector) | Both stdio AND HTTP |
| **Startup Time** | ~1-2s (Python import + connection) | <100ms (compiled binary) |
| **Maintenance** | 12 Python scripts to maintain | 12 shell wrappers (~30 lines each) |
| **Error Handling** | Custom exception handling | Built-in structured errors |
| **Discovery** | Manual tool name resolution | Built-in grep and schema discovery |

---

## Current State Analysis

### Existing Scripts Inventory

Based on analysis of `/scripts/` directory:

```
scripts/
├── exa/
│   ├── exa_search.py         (web search)
│   └── exa_code.py           (code context search)
├── deepwiki/
│   ├── deepwiki_structure.py (get repo docs structure)
│   ├── deepwiki_contents.py  (get repo docs contents)
│   └── deepwiki_ask.py       (ask questions about repo)
├── context7/
│   ├── context7_resolve.py   (resolve library ID)
│   └── context7_docs.py      (get library documentation)
└── github/
    ├── github_search_code.py    (search code across repos)
    ├── github_search_repos.py   (search repositories)
    └── github_file_contents.py  (get file/directory contents)
```

**Total:** 11 Python scripts + 1 README.md

### Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER/AI REQUEST                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  PYTHON SCRIPT WRAPPER                       │
│  • Parse CLI arguments                                       │
│  • Auto-install mcp-use if missing                           │
│  • Find MCP config from ~/.claude.json                       │
│  • Create HttpConnector instance                            │
│  • Connect to HTTP MCP server                               │
│  • Call tool with arguments                                 │
│  • Format output as JSON                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              mcp-use HttpConnector (Python)                  │
│  • Manages HTTP connection to MCP server                     │
│  • Handles MCP protocol messages                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              HTTP MCP SERVER (remote)                         │
│  • Exa, DeepWiki, Context7, GitHub                           │
└─────────────────────────────────────────────────────────────┘
```

### Pain Points

1. **Complex Setup:** Requires Python 3.10+, pip, virtual environments
2. **HTTP-Only Limitation:** HttpConnector only works with HTTP servers
3. **Maintenance Overhead:** 12 Python scripts with ~200-250 lines each
4. **Dependency Hell:** mcp-use version conflicts, Python path issues
5. **Slow Startup:** Python import overhead + async connection setup
6. **Discovery Complexity:** Manual tool name mapping and fallback logic

---

## Target State: mcp-cli Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER/AI REQUEST                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              SHELL WRAPPER (~30 lines)                        │
│  • Parse CLI arguments (same interface)                     │
│  • Build JSON arguments for mcp-cli                         │
│  • Call mcp-cli with server/tool                            │
│  • Return output with metadata                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    mcp-cli BINARY                            │
│  • Reads config from ~/.claude.json or mcp_servers.json     │
│  • Connects to ANY MCP server (stdio OR HTTP)               │
│  • Handles protocol, retries, errors                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            MCP SERVER (stdio OR HTTP)                         │
│  • Exa, DeepWiki, Context7, GitHub, filesystem, sqlite...   │
└─────────────────────────────────────────────────────────────┘
```

### Advantages

1. **Zero Runtime Dependencies:** Single binary, no Python
2. **Universal Server Support:** Works with stdio AND HTTP servers
3. **Fast Execution:** Compiled binary, ~100ms startup
4. **Simplified Scripts:** Shell wrappers ~30 lines vs ~250 lines
5. **Built-in Discovery:** `mcp-cli grep`, `mcp-cli <server>` for tools
6. **Structured Errors:** Actionable error messages with suggestions

---

## Migration Strategy

### Phase 1: Preparation & Setup (Week 1)

#### 1.1 Install mcp-cli

```bash
# Option A: Direct install (recommended)
curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash

# Option B: Via bun
bun install -g https://github.com/philschmid/mcp-cli

# Option C: Build from source (for custom builds)
git clone https://github.com/philschmid/mcp-cli.git
cd mcp-cli
bun install
bun run build
```

#### 1.2 Verify mcp-cli Installation

```bash
# Check version
mcp-cli --version

# List available servers (uses existing ~/.claude.json)
mcp-cli

# Test with existing server
mcp-cli exa/web_search_exa '{"query": "test"}' --json
```

#### 1.3 Create mcp_servers.json (if needed)

The mcp-cli automatically reads from Claude's config, but we can create a dedicated config:

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
    },
    "context7": {
      "url": "https://context7 MCP endpoint"
    },
    "github": {
      "url": "https://github MCP endpoint",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    }
  }
}
```

**Config Resolution Order (mcp-cli):**
1. `$MCP_CONFIG_PATH` environment variable
2. `-c/--config <path>` command line argument
3. `./mcp_servers.json` (current directory)
4. `~/.mcp_servers.json`
5. `~/.config/mcp/mcp_servers.json`
6. `~/.claude.json` (Claude's config - auto-detected!)

---

### Phase 2: Shell Wrapper Template Design (Week 1)

#### 2.1 Generic Shell Wrapper Template

Create `/scripts/templates/mcp_wrapper.sh`:

```bash
#!/usr/bin/env bash
#
# MCP Tool Wrapper Script Template
# Usage: ./script_name.sh [--arg value ...]
#
# This script wraps mcp-cli to provide a consistent CLI interface
# for MCP tools while maintaining backward compatibility with
# existing Python scripts.

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

# Server and tool names (MUST match mcp-cli config)
SERVER_NAME="${MCP_SERVER:-}"          # e.g., "exa"
TOOL_NAME="${MCP_TOOL:-}"              # e.g., "web_search_exa"
SCRIPT_NAME="$(basename "$0")"

# Default values (override in script-specific section)
MCP_CLI="${MCP_CLI:-mcp-cli}"         # Path to mcp-cli binary
CONFIG_PATH="${MCP_CONFIG:-}"          # Optional: path to mcp_servers.json

# Output format
OUTPUT_JSON="${OUTPUT_JSON:-true}"     # Always output JSON for scripting

# ============================================================================
# FUNCTIONS
# ============================================================================

error() {
    local msg="$1"
    local error_type="${2:-"ScriptError"}"
    echo "{\"success\": false, \"error\": \"$msg\", \"error_type\": \"$error_type\"}" >&2
    exit 1
}

check_mcp_cli() {
    if ! command -v "$MCP_CLI" &> /dev/null; then
        error "mcp-cli not found. Install from: https://github.com/philschmid/mcp-cli" "DependencyError"
    fi
}

validate_required_vars() {
    if [[ -z "$SERVER_NAME" ]]; then
        error "SERVER_NAME not set. Configure MCP_SERVER environment variable." "ConfigurationError"
    fi
    if [[ -z "$TOOL_NAME" ]]; then
        error "TOOL_NAME not set. Configure MCP_TOOL environment variable." "ConfigurationError"
    fi
}

call_mcp_tool() {
    local json_args="$1"

    # Build mcp-cli command
    local cmd=("$MCP_CLI")
    if [[ -n "$CONFIG_PATH" ]]; then
        cmd+=("-c" "$CONFIG_PATH")
    fi
    cmd+=("--json")                    # Always output JSON
    cmd+=("$SERVER_NAME/$TOOL_NAME")
    cmd+=("$json_args")

    # Execute and capture output
    local output
    local exit_code

    output=$("${cmd[@]}" 2>&1) || exit_code=$?

    # Check for errors
    if [[ -n "${exit_code:-}" ]] && [[ "$exit_code" -ne 0 ]]; then
        # mcp-cli outputs errors to stderr with structured format
        # Try to parse and enhance
        if echo "$output" | jq -e '.error' &> /dev/null; then
            # Already JSON error, pass through
            echo "$output" >&2
            exit "$exit_code"
        else
            # Convert plain error to JSON
            error "mcp-cli error: $output" "MCPError"
        fi
    fi

    # Success - output with metadata
    echo "$output"
}

# ============================================================================
# SCRIPT-SIFIC CONFIGURATION
# ============================================================================
# Override these in the actual script:

# parse_arguments() {
#     # Parse CLI arguments and build JSON args for tool
#     # Usage: parse_arguments "$@"
#     # Output: JSON string via echo
# }
#
# build_json_args() {
#     # Build JSON arguments for mcp-cli
#     # Usage: build_json_args
#     # Output: JSON string via echo
# }

# ============================================================================
# MAIN
# ============================================================================

main() {
    # Validate environment
    check_mcp_cli
    validate_required_vars

    # Parse arguments (implemented by each script)
    parse_arguments "$@"

    # Build JSON arguments for tool
    local json_args
    json_args=$(build_json_args)

    # Call MCP tool
    call_mcp_tool "$json_args"
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

#### 2.2 Script-Specific Implementation Pattern

Example: `scripts/exa/exa_search.sh`

```bash
#!/usr/bin/env bash
#
# Exa Web Search Script
# Usage: ./exa_search.sh --query "search terms" [--type auto|fast|deep] [--results 8]

set -euo pipefall

# Import template (or copy functions inline)
# source ../templates/mcp_wrapper.sh

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_NAME="exa"
TOOL_NAME="web_search_exa"

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

QUERY=""
TYPE="auto"
NUM_RESULTS=8
CONTEXT_CHARS=10000

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --query|-q)
                QUERY="$2"
                shift 2
                ;;
            --type|-t)
                TYPE="$2"
                shift 2
                ;;
            --results|-r)
                NUM_RESULTS="$2"
                shift 2
                ;;
            --context-chars|-c)
                CONTEXT_CHARS="$2"
                shift 2
                ;;
            *)
                error "Unknown argument: $1" "ArgumentError"
                ;;
        esac
    done

    if [[ -z "$QUERY" ]]; then
        error "Required argument --query missing" "ArgumentError"
    fi
}

# ============================================================================
# BUILD JSON ARGS
# ============================================================================

build_json_args() {
    jq -n \
        --arg query "$QUERY" \
        --arg type "$TYPE" \
        --arg numResults "$NUM_RESULTS" \
        --arg contextMaxCharacters "$CONTEXT_CHARS" \
        '{
            query: $query,
            type: $type,
            numResults: ($numResults | tonumber),
            contextMaxCharacters: ($contextMaxCharacters | tonumber)
        }'
}

# ============================================================================
# TEMPLATE FUNCTIONS (inline for single-file distribution)
# ============================================================================

# [Insert template functions here or source the template]

# ============================================================================
# MAIN
# ============================================================================

main() {
    # Validate mcp-cli
    if ! command -v mcp-cli &> /dev/null; then
        error "mcp-cli not found. Install: curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash" "DependencyError"
    fi

    # Parse arguments
    parse_arguments "$@"

    # Build JSON
    local json_args
    json_args=$(build_json_args)

    # Call mcp-cli
    mcp-cli --json "$SERVER_NAME/$TOOL_NAME" "$json_args"
}

main "$@"
```

---

### Phase 3: Migration Implementation (Week 2)

#### 3.1 Priority Order

Migrate in this order to minimize risk and maximize learning:

| Priority | Script | Complexity | Reason |
|----------|--------|------------|--------|
| 1 | `exa_search.py` | Low | Simple tool, high usage |
| 2 | `exa_code.py` | Low | Similar to exa_search |
| 3 | `deepwiki_ask.py` | Medium | Multiple args, good learning |
| 4 | `context7_resolve.py` | Low | Single argument |
| 5 | `github_search_repos.py` | Medium | Multiple optional args |
| 6 | `deepwiki_structure.py` | Low | Single argument |
| 7 | `deepwiki_contents.py` | Low | Single argument |
| 8 | `context7_docs.py` | Medium | Multiple args |
| 9 | `github_search_code.py` | High | Complex query syntax |
| 10 | `github_file_contents.py` | Medium | Path handling |

#### 3.2 Migration Steps Per Script

For each Python script:

1. **Create corresponding .sh file**
   ```bash
   # From: scripts/exa/exa_search.py
   # To:   scripts/exa/exa_search.sh
   ```

2. **Extract configuration from Python script**
   ```python
   # Python config:
   SERVER_PATTERN = "exa"
   TOOL_NAME = "web_search_exa"
   ```
   ↓
   ```bash
   # Bash config:
   SERVER_NAME="exa"
   TOOL_NAME="web_search_exa"
   ```

3. **Map CLI arguments**
   ```python
   # Python argparse:
   parser.add_argument("--query", "-q", required=True)
   parser.add_argument("--type", "-t", choices=["auto", "fast", "deep"], default="auto")
   ```
   ↓
   ```bash
   # Bash case statement:
   --query|-q) QUERY="$2"; shift 2 ;;
   --type|-t)
       TYPE="$2"
       if [[ ! "$TYPE" =~ ^(auto|fast|deep)$ ]]; then
           error "Invalid type: $TYPE" "ArgumentError"
       fi
       shift 2
       ;;
   ```

4. **Build JSON arguments with jq**
   ```python
   # Python:
   arguments = {
       "query": args.query,
       "type": args.type,
       "numResults": args.results
   }
   ```
   ↓
   ```bash
   # Bash:
   jq -n \
       --arg query "$QUERY" \
       --arg type "$TYPE" \
       --arg numResults "$NUM_RESULTS" \
       '{
           query: $query,
           type: $type,
           numResults: ($numResults | tonumber)
       }'
   ```

5. **Call mcp-cli**
   ```python
   # Python (old):
   connector = HttpConnector(base_url=url, headers=headers)
   await connector.connect()
   result = await connector.call_tool(name=TOOL_NAME, arguments=arguments)
   await connector.disconnect()
   ```
   ↓
   ```bash
   # Bash (new):
   mcp-cli --json "$SERVER_NAME/$TOOL_NAME" "$json_args"
   ```

6. **Test parity with Python version**
   ```bash
   # Test both versions and compare output
   ./exa_search.py --query "test" > old.json
   ./exa_search.sh --query "test" > new.json
   diff <(jq -S . old.json) <(jq -S . new.json)
   ```

#### 3.3 Detailed Migration Examples

##### Example 1: exa_search.py → exa_search.sh

**Before (Python):**
```python
# Key sections from scripts/exa/exa_search.py

SERVER_PATTERN = "exa"
TOOL_NAME = "web_search_exa"  # auto-detected

parser.add_argument("--query", "-q", required=True)
parser.add_argument("--type", "-t", choices=["auto", "fast", "deep"], default="auto")
parser.add_argument("--results", "-r", type=int, default=8)
parser.add_argument("--context-chars", "-c", type=int, default=10000)

arguments = {
    "query": args.query,
    "type": args.type,
    "numResults": args.results,
    "contextMaxCharacters": args.context_chars
}
```

**After (Bash):**
```bash
#!/usr/bin/env bash
# scripts/exa/exa_search.sh

SERVER_NAME="exa"
TOOL_NAME="web_search_exa"

# Parse arguments
QUERY="${QUERY:-}"
TYPE="${TYPE:-auto}"
NUM_RESULTS="${NUM_RESULTS:-8}"
CONTEXT_CHARS="${CONTEXT_CHARS:-10000}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --query|-q) QUERY="$2"; shift 2 ;;
        --type|-t)
            TYPE="$2"
            [[ ! "$TYPE" =~ ^(auto|fast|deep)$ ]] && error "Invalid type"
            shift 2
            ;;
        --results|-r) NUM_RESULTS="$2"; shift 2 ;;
        --context-chars|-c) CONTEXT_CHARS="$2"; shift 2 ;;
        *) error "Unknown arg: $1" ;;
    esac
done

[[ -z "$QUERY" ]] && error "--query required"

# Build JSON
JSON_ARGS=$(jq -n \
    --arg q "$QUERY" \
    --arg t "$TYPE" \
    --arg n "$NUM_RESULTS" \
    --arg c "$CONTEXT_CHARS" \
    '{query: $q, type: $t, numResults: ($n|tonumber), contextMaxCharacters: ($c|tonumber)}')

# Call mcp-cli
mcp-cli --json "$SERVER_NAME/$TOOL_NAME" "$JSON_ARGS"
```

**Usage Comparison:**
```bash
# Old (Python)
python3 scripts/exa/exa_search.py --query "Next.js 15" --type deep --results 10

# New (Bash)
./scripts/exa/exa_search.sh --query "Next.js 15" --type deep --results 10
```

##### Example 2: deepwiki_ask.py → deepwiki_ask.sh

**Before (Python):**
```python
SERVER_PATTERN = "deepwiki"
TOOL_NAME = "ask_question"

parser.add_argument("--repo", "-r", required=True)
parser.add_argument("--question", "-q", required=True)

arguments = {
    "repoName": args.repo,
    "question": args.question
}
```

**After (Bash):**
```bash
#!/usr/bin/env bash
# scripts/deepwiki/deepwiki_ask.sh

SERVER_NAME="deepwiki"
TOOL_NAME="ask_question"

REPO="${REPO:-}"
QUESTION="${QUESTION:-}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo|-r) REPO="$2"; shift 2 ;;
        --question|-q) QUESTION="$2"; shift 2 ;;
        *) error "Unknown arg: $1" ;;
    esac
done

[[ -z "$REPO" ]] && error "--repo required"
[[ -z "$QUESTION" ]] && error "--question required"

JSON_ARGS=$(jq -n \
    --arg repo "$REPO" \
    --arg q "$QUESTION" \
    '{repoName: $repo, question: $q}')

mcp-cli --json "$SERVER_NAME/$TOOL_NAME" "$JSON_ARGS"
```

##### Example 3: github_search_code.py → github_search_code.sh

**Before (Python):**
```python
SERVER_PATTERN = "github"
TOOL_NAME = "search_code"

parser.add_argument("--query", "-q", required=True)
parser.add_argument("--per-page", type=int, default=30)
parser.add_argument("--page", type=int, default=1)

arguments = {
    "query": args.query,
    "perPage": args.per_page,
    "page": args.page
}
```

**After (Bash):**
```bash
#!/usr/bin/env bash
# scripts/github/github_search_code.sh

SERVER_NAME="github"
TOOL_NAME="search_code"

QUERY="${QUERY:-}"
PER_PAGE="${PER_PAGE:-30}"
PAGE="${PAGE:-1}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --query|-q) QUERY="$2"; shift 2 ;;
        --per-page) PER_PAGE="$2"; shift 2 ;;
        --page) PAGE="$2"; shift 2 ;;
        *) error "Unknown arg: $1" ;;
    esac
done

[[ -z "$QUERY" ]] && error "--query required"

JSON_ARGS=$(jq -n \
    --arg q "$QUERY" \
    --arg pp "$PER_PAGE" \
    --arg p "$PAGE" \
    '{query: $q, perPage: ($pp|tonumber), page: ($p|tonumber)}')

mcp-cli --json "$SERVER_NAME/$TOOL_NAME" "$JSON_ARGS"
```

---

### Phase 4: Testing & Validation (Week 2)

#### 4.1 Unit Testing Strategy

Create test suite for each migrated script:

```bash
#!/usr/bin/env bash
# tests/test_mcp_wrappers.sh

# Test configuration
TEST_DIR="$(dirname "$0")/../scripts"
PASSED=0
FAILED=0

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

test_script() {
    local script="$1"
    local name="$(basename "$script")"
    local test_args="${2:-}"

    echo -n "Testing $name... "

    if output=$("$script" $test_args 2>&1); then
        if echo "$output" | jq -e '.success' &> /dev/null || echo "$output" | jq -e '.' &> /dev/null; then
            echo -e "${GREEN}PASSED${NC}"
            ((PASSED++))
        else
            echo -e "${RED}FAILED (invalid JSON)${NC}"
            ((FAILED++))
            echo "Output: $output"
        fi
    else
        echo -e "${RED}FAILED (exit code $?)${NC}"
        ((FAILED++))
        echo "Output: $output"
    fi
}

# Test Exa scripts
test_script "$TEST_DIR/exa/exa_search.sh" '--query "test" --results 1'
test_script "$TEST_DIR/exa/exa_code.sh" '--query "react hooks"'

# Test DeepWiki scripts
test_script "$TEST_DIR/deepwiki/deepwiki_ask.sh" '--repo "facebook/react" --question "What is React?"'
test_script "$TEST_DIR/deepwiki/deepwiki_structure.sh" '--repo "facebook/react"'
test_script "$TEST_DIR/deepwiki/deepwiki_contents.sh" '--repo "facebook/react"'

# Test Context7 scripts
test_script "$TEST_DIR/context7/context7_resolve.sh" '--library "react"'
# test_script "$TEST_DIR/context7/context7_docs.sh" --library-id "/vercel/next.js" --topic "routing"

# Test GitHub scripts
# test_script "$TEST_DIR/github/github_search_repos.sh" '--query "mcp server"'
# test_script "$TEST_DIR/github/github_search_code.sh" '--query "filename:README"'
# test_script "$TEST_DIR/github/github_file_contents.sh" '--owner "facebook" --repo "react" --path "README.md"'

# Summary
echo ""
echo "=========================================="
echo "Tests Passed: $PASSED"
echo "Tests Failed: $FAILED"
echo "=========================================="

[[ "$FAILED" -eq 0 ]] && exit 0 || exit 1
```

#### 4.2 Integration Testing

Test with real MCP servers:

```bash
#!/usr/bin/env bash
# tests/integration/test_real_servers.sh

# Test with actual Exa server
echo "Testing Exa web search..."
./scripts/exa/exa_search.sh --query "Next.js 15" --results 3 | jq '.'

# Test with actual DeepWiki server
echo "Testing DeepWiki..."
./scripts/deepwiki/deepwiki_ask.sh \
    --repo "facebook/react" \
    --question "What is React?" | jq '.'

# Test with actual Context7 server
echo "Testing Context7..."
./scripts/context7/context7_resolve.sh --library "next.js" | jq '.'

echo "All integration tests passed!"
```

#### 4.3 Backward Compatibility Testing

Ensure old Python scripts still work during transition:

```bash
#!/usr/bin/env bash
# tests/compatibility/test_parity.sh

# Run both versions and compare output
compare_outputs() {
    local py_script="$1"
    local sh_script="$2"
    shift 2
    local args=("$@")

    echo "Testing parity: $(basename "$sh_script")"

    # Run Python version
    python3 "$py_script" "${args[@]}" > /tmp/py_out.json 2>&1
    local py_exit=$?

    # Run Shell version
    bash "$sh_script" "${args[@]}" > /tmp/sh_out.json 2>&1
    local sh_exit=$?

    # Compare exit codes
    if [[ "$py_exit" -ne "$sh_exit" ]]; then
        echo "❌ Exit code mismatch: Python=$py_exit, Shell=$sh_exit"
        return 1
    fi

    # Compare JSON structure (ignore timestamps)
    local py_data=$(jq 'del(.metadata.timestamp)' /tmp/py_out.json)
    local sh_data=$(jq 'del(.metadata.timestamp)' /tmp/sh_out.json)

    if [[ "$py_data" != "$sh_data" ]]; then
        echo "❌ Output mismatch"
        echo "Python: $py_data"
        echo "Shell:  $sh_data"
        return 1
    fi

    echo "✓ Output matches"
    return 0
}

# Compare each script
compare_outputs \
    "./scripts/exa/exa_search.py" \
    "./scripts/exa/exa_search.sh" \
    --query "test" --results 1

compare_outputs \
    "./scripts/deepwiki/deepwiki_ask.py" \
    "./scripts/deepwiki/deepwiki_ask.sh" \
    --repo "facebook/react" --question "What is it?"

echo "Parity tests complete!"
```

---

### Phase 5: Documentation Updates (Week 2)

#### 5.1 Update README.md

Replace `scripts/README.md` with mcp-cli version:

```markdown
# MCP CLI Wrapper Scripts

Scripts for interacting with MCP servers using mcp-cli.

## Quick Start

### Prerequisites

1. **Install mcp-cli:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash
   ```

2. **Verify installation:**
   ```bash
   mcp-cli --version
   mcp-cli  # Should list your configured MCP servers
   ```

3. **Ensure jq is installed** (for JSON processing):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install jq

   # macOS
   brew install jq

   # Arch
   sudo pacman -S jq
   ```

### Usage Examples

#### Exa Web Search

```bash
./scripts/exa/exa_search.sh \
  --query "Next.js 15 best practices" \
  --type deep \
  --results 10
```

#### Exa Code Context

```bash
./scripts/exa/exa_code.sh \
  --query "React hooks patterns" \
  --tokens 5000
```

#### DeepWiki

```bash
# Get repo documentation structure
./scripts/deepwiki/deepwiki_structure.sh --repo "facebook/react"

# Get documentation contents
./scripts/deepwiki/deepwiki_contents.sh --repo "facebook/react"

# Ask a question
./scripts/deepwiki/deepwiki_ask.sh \
  --repo "vercel/next.js" \
  --question "How do I use the App Router?"
```

#### Context7

```bash
# Resolve library ID
./scripts/context7/context7_resolve.sh --library "next.js"

# Get documentation
./scripts/context7/context7_docs.sh \
  --library-id "/vercel/next.js" \
  --topic "routing"
```

#### GitHub

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

## Architecture

```
┌─────────────────┐
│  Shell Script   │  Parse CLI args, build JSON
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    mcp-cli      │  Connect to MCP server
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MCP Server     │  Exa, DeepWiki, Context7, GitHub
└─────────────────┘
```

## Available Scripts

| Directory | Scripts | Tools |
|-----------|---------|-------|
| `exa/` | exa_search.sh, exa_code.sh | Web search, code context |
| `deepwiki/` | deepwiki_{ask,structure,contents}.sh | Repo Q&A, docs |
| `context7/` | context7_{resolve,docs}.sh | Library docs |
| `github/` | github_{search_repos,search_code,file_contents}.sh | GitHub API |

## Configuration

Scripts automatically discover MCP config from:
1. `~/.claude.json`
2. `~/.mcp_servers.json`
3. `~/.config/mcp/mcp_servers.json`
4. `./mcp_servers.json`
5. `$MCP_CONFIG_PATH` environment variable

## Error Handling

All scripts return structured JSON:

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

## Troubleshooting

### "mcp-cli not found"

Install mcp-cli:
```bash
curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash
```

### "jq: command not found"

Install jq:
```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq
```

### "Server not found"

Check your MCP configuration:
```bash
mcp-cli  # List all available servers
```

### "Permission denied: script.sh"

Make script executable:
```bash
chmod +x scripts/exa/exa_search.sh
```

## Migration from Python Scripts

If you're migrating from the old Python scripts:

1. **Install mcp-cli** (see Quick Start)
2. **Update your calls** from:
   ```bash
   python3 scripts/exa/exa_search.py --query "test"
   ```
   to:
   ```bash
   ./scripts/exa/exa_search.sh --query "test"
   ```

3. **Or keep using Python scripts** - they're still compatible!

## Advantages of mcp-cli

| Feature | Python/mcp-use | mcp-cli |
|---------|----------------|---------|
| Installation | Python 3.10+, pip | Single binary |
| Server Support | HTTP only | HTTP + stdio |
| Startup Time | ~1-2s | <100ms |
| Dependencies | mcp-use library | None |
| Script Size | ~250 lines | ~30 lines |
| Discovery | Manual | Built-in (mcp-cli grep) |
| Error Messages | Custom | Structured |

## Contributing

To add a new wrapper script:

1. Copy the template:
   ```bash
   cp scripts/templates/mcp_wrapper.sh scripts/new_server/new_tool.sh
   ```

2. Configure server and tool names:
   ```bash
   SERVER_NAME="new_server"
   TOOL_NAME="new_tool"
   ```

3. Implement `parse_arguments()` and `build_json_args()`

4. Make executable:
   ```bash
   chmod +x scripts/new_server/new_tool.sh
   ```

5. Test:
   ```bash
   ./scripts/new_server/new_tool.sh --help
   ```
```

#### 5.2 Update Super-Dev Plugin Documentation

Update main README.md to reference mcp-cli:

```markdown
## MCP Scripts

The plugin includes shell wrapper scripts for interacting with MCP servers via `mcp-cli`:

- **Exa:** Web search and code context search
- **DeepWiki:** GitHub repository documentation and Q&A
- **Context7:** Library documentation resolution and retrieval
- **GitHub:** Repository and code search, file contents

**Prerequisites:**
```bash
# Install mcp-cli
curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash

# Install jq (for JSON processing)
sudo apt-get install jq  # Ubuntu/Debian
brew install jq           # macOS
```

**Quick Example:**
```bash
# Web search via Exa
./scripts/exa/exa_search.sh --query "Next.js 15" --type deep --results 10

# Ask about a GitHub repo via DeepWiki
./scripts/deepwiki/deepwiki_ask.sh --repo "facebook/react" --question "What is React?"
```

See [scripts/README.md](scripts/README.md) for detailed usage.
```

---

### Phase 6: Deployment & Rollout (Week 3)

#### 6.1 Parallel Deployment Strategy

Keep both Python and Shell scripts during transition:

```
scripts/
├── exa/
│   ├── exa_search.py          # Legacy (keep for now)
│   ├── exa_search.sh          # New (mcp-cli)
│   ├── exa_code.py
│   └── exa_code.sh
├── deepwiki/
│   ├── deepwiki_ask.py
│   ├── deepwiki_ask.sh
│   ├── ...
└── README.md                  # Update to document both
```

Update README with migration notice:

```markdown
## Migration Notice

**New (Recommended):** Use `.sh` scripts with mcp-cli (faster, no dependencies)
**Legacy:** `.py` scripts still work but require Python 3.10+ and mcp-use

We recommend migrating to the `.sh` scripts:

```bash
# Old (Python)
python3 scripts/exa/exa_search.py --query "test"

# New (Shell - mcp-cli)
./scripts/exa/exa_search.sh --query "test"
```

The Python scripts will be deprecated in a future release.
```

#### 6.2 Update Agent Skills

Update any agent skills that reference the Python scripts:

```yaml
# Before:
- "Run python3 scripts/exa/exa_search.py --query '{query}'"

# After:
- "Run ./scripts/exa/exa_search.sh --query '{query}'"
```

#### 6.3 Deprecation Timeline

| Phase | Date | Action |
|-------|------|--------|
| **Announcement** | Week 1 | Document migration plan, update README |
| **Parallel Run** | Week 2-4 | Both Python and Shell scripts available |
| **Default Switch** | Week 5 | Update examples to use `.sh` by default |
| **Deprecation Notice** | Week 8 | Add warning to Python scripts |
| **Remove Python** | Week 12 | Remove `.py` scripts (optional, can keep for compatibility) |

---

### Phase 7: Future Enhancements (Post-Migration)

#### 7.1 Additional Script Opportunities

Once mcp-cli is installed, we can add scripts for new MCP servers:

**Filesystem MCP:**
```bash
#!/usr/bin/env bash
# scripts/filesystem/read_file.sh
SERVER_NAME="filesystem"
TOOL_NAME="read_file"

PATH="${1:?--path required}"

jq -n --arg path "$PATH" '{path: $path}' | \
  mcp-cli --json "$SERVER_NAME/$TOOL_NAME" -
```

**SQLite MCP:**
```bash
#!/usr/bin/env bash
# scripts/sqlite/query.sh
SERVER_NAME="sqlite"
TOOL_NAME="query"

DB_PATH="${1:?--db-path required}"
QUERY="${2:?--query required}"

jq -n \
  --arg db_path "$DB_PATH" \
  --arg query "$QUERY" \
  '{dbPath: $db_path, query: $query}' | \
  mcp-cli --json "$SERVER_NAME/$TOOL_NAME" -
```

**Browser Automation MCP:**
```bash
#!/usr/bin/env bash
# scripts/browser/navigate.sh
SERVER_NAME="browser"
TOOL_NAME="navigate"

URL="${1:?--url required}"

jq -n --arg url "$URL" '{url: $url}' | \
  mcp-cli --json "$SERVER_NAME/$TOOL_NAME" -
```

#### 7.2 Advanced Features

**Batch Processing:**
```bash
#!/usr/bin/env bash
# scripts/exa/batch_search.sh

# Read queries from file and process in parallel
while IFS= read -r query; do
    ./exa_search.sh --query "$query" &
done < queries.txt
wait
```

**Result Caching:**
```bash
#!/usr/bin/env bash
# scripts/exa/cached_search.sh

QUERY="$1"
CACHE_DIR="./cache/.exa"
CACHE_FILE="$CACHE_DIR/$(echo "$QUERY" | md5sum | cut -d' ' -f1).json"

if [[ -f "$CACHE_FILE" ]]; then
    cat "$CACHE_FILE"
else
    mkdir -p "$CACHE_DIR"
    ./exa_search.sh --query "$QUERY" | tee "$CACHE_FILE"
fi
```

---

## Implementation Checklist

### Week 1: Preparation

- [ ] Install mcp-cli locally
- [ ] Test mcp-cli with existing MCP servers
- [ ] Create `scripts/templates/mcp_wrapper.sh` template
- [ ] Document mcp-cli configuration and usage
- [ ] Update scripts/README.md with mcp-cli information

### Week 2: Migration & Testing

- [ ] Migrate Exa scripts (2 scripts)
  - [ ] exa_search.py → exa_search.sh
  - [ ] exa_code.py → exa_code.sh
- [ ] Migrate DeepWiki scripts (3 scripts)
  - [ ] deepwiki_ask.py → deepwiki_ask.sh
  - [ ] deepwiki_structure.py → deepwiki_structure.sh
  - [ ] deepwiki_contents.py → deepwiki_contents.sh
- [ ] Migrate Context7 scripts (2 scripts)
  - [ ] context7_resolve.py → context7_resolve.sh
  - [ ] context7_docs.py → context7_docs.sh
- [ ] Migrate GitHub scripts (3 scripts)
  - [ ] github_search_repos.py → github_search_repos.sh
  - [ ] github_search_code.py → github_search_code.sh
  - [ ] github_file_contents.py → github_file_contents.sh
- [ ] Create test suite
- [ ] Run parity tests between Python and Shell versions
- [ ] Run integration tests with real MCP servers

### Week 3: Documentation & Deployment

- [ ] Update scripts/README.md
- [ ] Update main README.md
- [ ] Update agent skills to use shell scripts
- [ ] Add migration notice to Python scripts
- [ ] Commit and push changes

### Post-Migration

- [ ] Monitor for issues
- [ ] Gather feedback from users
- [ ] Add new script examples (filesystem, sqlite, browser)
- [ ] Deprecate Python scripts (timeline TBA)

---

## Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **jq dependency missing** | Medium | Low | Check in script, provide install instructions |
| **mcp-cli not installed** | High | Medium | Auto-detect, provide clear error with install command |
| **Output format mismatch** | Low | Low | Parity tests, wrapper normalization |
| **Server name changes** | Low | Medium | Document mapping, support both old and new names |
| **Breaking changes in mcp-cli** | Low | Low | Pin to specific version, monitor upstream |

---

## Success Criteria

The migration is considered successful when:

1. **Functionality Parity:** All shell scripts produce identical output to Python versions
2. **Performance Improvement:** Shell scripts execute in <100ms vs ~2s for Python
3. **Installation Simplicity:** Users only need `curl` + `jq` (no Python/pip)
4. **Documentation Complete:** All README files updated with mcp-cli instructions
5. **Tests Passing:** All unit and integration tests pass
6. **Zero Breaking Changes:** Existing Python scripts still work (parallel deployment)

---

## Appendix: Resources

### mcp-cli Resources

- **GitHub:** https://github.com/philschmid/mcp-cli
- **Installation:** `curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash`
- **Documentation:** https://github.com/philschmid/mcp-cli#readme
- **Issues:** https://github.com/philschmid/mcp-cli/issues

### MCP Resources

- **MCP Specification:** https://modelcontextprotocol.io/
- **MCP Registry:** https://github.com/modelcontextprotocol/servers
- **Claude MCP Integration:** https://docs.anthropic.com/en/docs/build-with-claude/mcp

### Current Python Implementation

- **Scripts Location:** `/scripts/`
- **Template:** (if exists) `specification/11-mcp-http-connector/template_connector.py`
- **README:** `/scripts/README.md`

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-22 | AI Assistant | Initial migration plan |

---

**Next Steps:**

1. Review and approve this migration plan
2. Begin Phase 1: Install mcp-cli and verify functionality
3. Create shell wrapper template
4. Start migrating Exa scripts (lowest complexity, highest value)

**Questions?**

- Which MCP servers are currently configured?
- Are there any custom MCP servers not in this plan?
- Should we maintain Python scripts indefinitely or deprecate them?

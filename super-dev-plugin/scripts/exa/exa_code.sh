#!/usr/bin/env bash
#
# Exa Code Context Script (mcp-cli version)
#
# Get code context using Exa MCP server via mcp-cli.
#
# Usage:
#   ./exa_code.py --query "search query" [--tokens 5000]
#
# Examples:
#   ./exa_code.sh --query "React hooks patterns" --tokens 5000
#   ./exa_code.sh -q "TypeScript generics" -t 10000
#
# Output:
#   JSON formatted code context to stdout
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_NAME="exa"
TOOL_NAME="get_code_context_exa"
SCRIPT_NAME="$(basename "$0")"

# Default values
QUERY=""
TOKENS="${TOKENS:-5000}"

# MCP config (auto-detect Claude config)
MCP_CONFIG="${MCP_CONFIG:-${CLAUDE_CONFIG_PATH:-}}"
if [[ -z "$MCP_CONFIG" ]] && [[ -f "$HOME/.claude.json" ]]; then
    MCP_CONFIG="$HOME/.claude.json"
fi

# ============================================================================
# ERROR HANDLING
# ============================================================================

error() {
    local msg="$1"
    local error_type="${2:-"ScriptError"}"
    echo "{\"success\": false, \"error\": \"$msg\", \"error_type\": \"$error_type\"}" >&2
    exit 1
}

# ============================================================================
# DEPENDENCY CHECKS
# ============================================================================

check_dependencies() {
    # Check mcp-cli
    if ! command -v mcp-cli &> /dev/null; then
        error "mcp-cli not found. Install: curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash" "DependencyError"
    fi

    # Check jq
    if ! command -v jq &> /dev/null; then
        error "jq not found. Install: sudo apt-get install jq (Ubuntu) or brew install jq (macOS)" "DependencyError"
    fi
}

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --query|-q)
                QUERY="$2"
                shift 2
                ;;
            --tokens|-t)
                TOKENS="$2"
                if ! [[ "$TOKENS" =~ ^[0-9]+$ ]]; then
                    error "Invalid tokens count: $TOKENS. Must be a positive integer" "ArgumentError"
                fi
                # Validate range (1000-50000)
                if [[ "$TOKENS" -lt 1000 ]] || [[ "$TOKENS" -gt 50000 ]]; then
                    error "Tokens must be between 1000 and 50000" "ArgumentError"
                fi
                shift 2
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                error "Unknown argument: $1. Use --help for usage information" "ArgumentError"
                ;;
        esac
    done

    # Validate required arguments
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
        --arg tokensNum "$TOKENS" \
        '{
            query: $query,
            tokensNum: ($tokensNum | tonumber)
        }'
}

# ============================================================================
# HELP
# ============================================================================

show_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Get code context using Exa MCP server.

Options:
  --query, -q <text>    Code-related search query (required)
  --tokens, -t <num>    Number of tokens: 1000-50000 (default: 5000)
  --help, -h            Show this help message

Examples:
  # Basic code search
  $SCRIPT_NAME --query "React hooks patterns"

  # Get more context
  $SCRIPT_NAME -q "TypeScript generics" -t 10000

  # Minimal context (faster)
  $SCRIPT_NAME -q "Python async/await" -t 2000

Output:
  JSON formatted code context to stdout

Requires:
  - mcp-cli: https://github.com/philschmid/mcp-cli
  - jq: sudo apt-get install jq (Ubuntu) or brew install jq (macOS)

For more information about Exa MCP server:
  https://github.com/ModelCloud/exa-mcp-server
EOF
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    # Check dependencies
    check_dependencies

    # Parse arguments
    parse_arguments "$@"

    # Build JSON arguments
    local json_args
    json_args=$(build_json_args)

    # Call mcp-cli with config if available
    if [[ -n "$MCP_CONFIG" ]]; then
        mcp-cli -c "$MCP_CONFIG" --json "$SERVER_NAME/$TOOL_NAME" "$json_args"
    else
        mcp-cli --json "$SERVER_NAME/$TOOL_NAME" "$json_args"
    fi
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

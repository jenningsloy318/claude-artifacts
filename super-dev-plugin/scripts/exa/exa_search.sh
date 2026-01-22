#!/usr/bin/env bash
#
# Exa Web Search Script (mcp-cli version)
#
# Execute web searches using Exa MCP server via mcp-cli.
#
# Usage:
#   ./exa_search.sh --query "search terms" [--type auto|fast|deep] [--results N] [--context-chars N]
#
# Examples:
#   ./exa_search.sh --query "Next.js 15 best practices" --type deep --results 10
#   ./exa_search.sh -q "React hooks" -t fast -r 5
#
# Output:
#   JSON formatted search results to stdout
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_NAME="exa"
TOOL_NAME="web_search_exa"
SCRIPT_NAME="$(basename "$0")"

# Default values
QUERY=""
TYPE="${TYPE:-auto}"
NUM_RESULTS="${NUM_RESULTS:-8}"
CONTEXT_CHARS="${CONTEXT_CHARS:-10000}"

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
            --type|-t)
                TYPE="$2"
                if [[ ! "$TYPE" =~ ^(auto|fast|deep)$ ]]; then
                    error "Invalid type: $TYPE. Must be one of: auto, fast, deep" "ArgumentError"
                fi
                shift 2
                ;;
            --results|-r)
                NUM_RESULTS="$2"
                if ! [[ "$NUM_RESULTS" =~ ^[0-9]+$ ]]; then
                    error "Invalid results count: $NUM_RESULTS. Must be a positive integer" "ArgumentError"
                fi
                shift 2
                ;;
            --context-chars|-c)
                CONTEXT_CHARS="$2"
                if ! [[ "$CONTEXT_CHARS" =~ ^[0-9]+$ ]]; then
                    error "Invalid context chars: $CONTEXT_CHARS. Must be a positive integer" "ArgumentError"
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
# HELP
# ============================================================================

show_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Execute web searches using Exa MCP server.

Options:
  --query, -q <text>       Search query (required)
  --type, -t <type>        Search type: auto|fast|deep (default: auto)
  --results, -r <num>      Number of results (default: 8)
  --context-chars, -c <n>  Context max characters (default: 10000)
  --help, -h               Show this help message

Examples:
  # Basic search
  $SCRIPT_NAME --query "Next.js 15 best practices"

  # Deep search with more results
  $SCRIPT_NAME -q "React hooks patterns" -t deep -r 15

  # Fast search with less context
  $SCRIPT_NAME -q "TypeScript types" -t fast -c 5000

Output:
  JSON formatted search results to stdout

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

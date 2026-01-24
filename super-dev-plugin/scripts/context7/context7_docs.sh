#!/usr/bin/env bash
#
# Context7 Docs Script (mcp-cli version)
#
# Get library documentation from Context7 MCP server via mcp-cli.
#
# Usage:
#   ./context7_docs.sh --library-id "/vercel/next.js" [--mode code|info] [--topic "routing"] [--page 1]
#
# Examples:
#   ./context7_docs.sh --library-id "/vercel/next.js" --mode code --topic "routing"
#   ./context7_docs.sh -l "/mongodb/docs" -m info -t "aggregation"
#
# Output:
#   JSON formatted documentation to stdout
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_NAME="context7"
TOOL_NAME="get-library-docs"
SCRIPT_NAME="$(basename "$0")"

# Default values
LIBRARY_ID=""
MODE="code"
TOPIC=""
PAGE=1

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
    if ! command -v mcp-cli &> /dev/null; then
        error "mcp-cli not found. Install: curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash" "DependencyError"
    fi

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
            --library-id|-l)
                LIBRARY_ID="$2"
                shift 2
                ;;
            --mode|-m)
                MODE="$2"
                shift 2
                ;;
            --topic|-t)
                TOPIC="$2"
                shift 2
                ;;
            --page|-p)
                PAGE="$2"
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
    if [[ -z "$LIBRARY_ID" ]]; then
        error "Required argument --library-id missing" "ArgumentError"
    fi

    # Validate mode
    if [[ "$MODE" != "code" && "$MODE" != "info" ]]; then
        error "Invalid mode: $MODE. Must be 'code' or 'info'" "ArgumentError"
    fi

    # Validate page is a number
    if ! [[ "$PAGE" =~ ^[0-9]+$ ]]; then
        error "Invalid page: $PAGE. Must be a number" "ArgumentError"
    fi
}

# ============================================================================
# BUILD JSON ARGS
# ============================================================================

build_json_args() {
    local base_json
    base_json=$(jq -n \
        --arg libraryId "$LIBRARY_ID" \
        --arg mode "$MODE" \
        --argjson page "$PAGE" \
        '{
            context7CompatibleLibraryID: $libraryId,
            mode: $mode,
            page: $page
        }')

    # Add optional topic if provided
    if [[ -n "$TOPIC" ]]; then
        base_json=$(echo "$base_json" | jq --arg topic "$TOPIC" '. + {topic: $topic}')
    fi

    echo "$base_json"
}

# ============================================================================
# HELP
# ============================================================================

show_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Get library documentation from Context7 MCP server.

Options:
  --library-id, -l <id>    Context7-compatible library ID (required, e.g., "/vercel/next.js")
  --mode, -m <mode>        Documentation mode: 'code' (default) or 'info'
  --topic, -t <topic>      Optional topic to focus on (e.g., "routing", "hooks")
  --page, -p <number>      Page number for pagination (1-10, default: 1)
  --help, -h               Show this help message

Examples:
  # Get Next.js API documentation
  $SCRIPT_NAME --library-id "/vercel/next.js" --mode code

  # Get MongoDB documentation about aggregation
  $SCRIPT_NAME -l "/mongodb/docs" -m info -t "aggregation"

  # Get React documentation about hooks, page 2
  $SCRIPT_NAME -l "/facebook/react" -m code -t "hooks" -p 2

Output:
  JSON formatted documentation to stdout

Requires:
  - mcp-cli: https://github.com/philschmid/mcp-cli
  - jq: sudo apt-get install jq (Ubuntu) or brew install jq (macOS)

Note:
  Use context7_resolve.sh to find library IDs.
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

    # Call mcp-cli
    mcp-cli --json "$SERVER_NAME/$TOOL_NAME" "$json_args"
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

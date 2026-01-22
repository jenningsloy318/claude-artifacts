#!/usr/bin/env bash
#
# Context7 Resolve Script (mcp-cli version)
#
# Resolve library name to Context7-compatible library ID using Context7 MCP server via mcp-cli.
#
# Usage:
#   ./context7_resolve.sh --library "library-name"
#
# Examples:
#   ./context7_resolve.sh --library "react"
#   ./context7_resolve.sh --library "next.js"
#   ./context7_resolve.sh -l "mongodb"
#
# Output:
#   JSON formatted list of matching libraries with IDs to stdout
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_NAME="context7"
TOOL_NAME="resolve-library-id"
SCRIPT_NAME="$(basename "$0")"

# Default values
LIBRARY=""

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
            --library|-l)
                LIBRARY="$2"
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
    if [[ -z "$LIBRARY" ]]; then
        error "Required argument --library missing" "ArgumentError"
    fi
}

# ============================================================================
# BUILD JSON ARGS
# ============================================================================

build_json_args() {
    # Note: The tool might require both libraryName and query
    # Based on mcp-use scripts, we provide both for compatibility
    jq -n \
        --arg libraryName "$LIBRARY" \
        --arg query "Find documentation for library: $LIBRARY" \
        '{
            libraryName: $libraryName,
            query: $query
        }'
}

# ============================================================================
# HELP
# ============================================================================

show_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Resolve library name to Context7-compatible library ID.

Options:
  --library, -l <name>     Library name to search for (required)
  --help, -h               Show this help message

Examples:
  # Find React documentation
  $SCRIPT_NAME --library "react"

  # Find Next.js documentation
  $SCRIPT_NAME -l "next.js"

  # Find MongoDB documentation
  $SCRIPT_NAME -l "mongodb"

Output:
  JSON formatted list of matching libraries with their Context7 IDs

  Example output:
  {
    "results": [
      {
        "id": "/facebook/react",
        "name": "react",
        "description": "A JavaScript library for building user interfaces",
        "score": 0.95
      }
    ]
  }

Requires:
  - mcp-cli: https://github.com/philschmid/mcp-cli
  - jq: sudo apt-get install jq (Ubuntu) or brew install jq (macOS)

Next Steps:
  Use the library ID with context7_docs.sh to fetch documentation:
  $ ./context7_docs.sh --library-id "/facebook/react" --topic "hooks"

For more information about Context7:
  https://context7.io
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

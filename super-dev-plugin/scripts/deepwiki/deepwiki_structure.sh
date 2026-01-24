#!/usr/bin/env bash
#
# DeepWiki Structure Script (mcp-cli version)
#
# Get documentation structure for a GitHub repository using DeepWiki MCP server via mcp-cli.
#
# Usage:
#   ./deepwiki_structure.sh --repo "owner/repo"
#
# Examples:
#   ./deepwiki_structure.sh --repo "facebook/react"
#   ./deepwiki_structure.sh -r "vercel/next.js"
#
# Output:
#   JSON formatted topic list to stdout
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_NAME="deepwiki"
TOOL_NAME="read_wiki_structure"
SCRIPT_NAME="$(basename "$0")"

# Default values
REPO=""

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
            --repo|-r)
                REPO="$2"
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
    if [[ -z "$REPO" ]]; then
        error "Required argument --repo missing" "ArgumentError"
    fi

    # Validate repo format (basic check for owner/repo pattern)
    if [[ ! "$REPO" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
        error "Invalid repo format: $REPO. Expected format: owner/repo (e.g., facebook/react)" "ArgumentError"
    fi
}

# ============================================================================
# BUILD JSON ARGS
# ============================================================================

build_json_args() {
    jq -n \
        --arg repoName "$REPO" \
        '{
            repoName: $repoName
        }'
}

# ============================================================================
# HELP
# ============================================================================

show_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Get documentation structure for a GitHub repository using DeepWiki MCP server.

Options:
  --repo, -r <owner/repo>   GitHub repository (required, e.g., "facebook/react")
  --help, -h                Show this help message

Examples:
  # Get React documentation structure
  $SCRIPT_NAME --repo "facebook/react"

  # Get Next.js documentation structure
  $SCRIPT_NAME -r "vercel/next.js"

Output:
  JSON formatted topic list to stdout

Requires:
  - mcp-cli: https://github.com/philschmid/mcp-cli
  - jq: sudo apt-get install jq (Ubuntu) or brew install jq (macOS)

For more information about DeepWiki:
  https://deepwiki.com
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

#!/usr/bin/env bash
#
# DeepWiki Ask Script (mcp-cli version)
#
# Ask questions about a GitHub repository using DeepWiki MCP server via mcp-cli.
#
# Usage:
#   ./deepwiki_ask.sh --repo "owner/repo" --question "Your question"
#
# Examples:
#   ./deepwiki_ask.sh --repo "facebook/react" --question "What is React?"
#   ./deepwiki_ask.sh -r "vercel/next.js" -q "How do I use the App Router?"
#
# Output:
#   JSON formatted answer to stdout
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_NAME="deepwiki"
TOOL_NAME="ask_question"
SCRIPT_NAME="$(basename "$0")"

# Default values
REPO=""
QUESTION=""

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
            --question|-q)
                QUESTION="$2"
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

    if [[ -z "$QUESTION" ]]; then
        error "Required argument --question missing" "ArgumentError"
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
        --arg question "$QUESTION" \
        '{
            repoName: $repoName,
            question: $question
        }'
}

# ============================================================================
# HELP
# ============================================================================

show_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Ask questions about a GitHub repository using DeepWiki MCP server.

Options:
  --repo, -r <owner/repo>   GitHub repository (required, e.g., "facebook/react")
  --question, -q <text>     Question to ask about the repository (required)
  --help, -h                Show this help message

Examples:
  # Ask about React
  $SCRIPT_NAME --repo "facebook/react" --question "What is React?"

  # Ask about Next.js App Router
  $SCRIPT_NAME -r "vercel/next.js" -q "How do I use the App Router?"

  # Ask about a specific feature
  $SCRIPT_NAME -r "facebook/react" -q "What are React hooks?"

Output:
  JSON formatted answer to stdout

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

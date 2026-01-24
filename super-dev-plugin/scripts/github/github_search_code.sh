#!/usr/bin/env bash
#
# GitHub Search Code Script (mcp-cli version)
#
# Search code across all GitHub repositories using GitHub MCP server via mcp-cli.
#
# Usage:
#   ./github_search_code.sh --query "function search" [--sort indexed] [--order asc|desc] [--page 1] [--per-page 30]
#
# Examples:
#   ./github_search_code.sh --query "HttpConnector language:python"
#   ./github_search_code.sh -q "repo:owner/repo MyClass" --sort indexed --order desc
#
# Output:
#   JSON formatted search results to stdout
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_NAME="github"
TOOL_NAME="search_code"
SCRIPT_NAME="$(basename "$0")"

# Default values
QUERY=""
SORT=""
ORDER=""
PAGE=1
PER_PAGE=30

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
            --query|-q)
                QUERY="$2"
                shift 2
                ;;
            --sort|-s)
                SORT="$2"
                shift 2
                ;;
            --order|-o)
                ORDER="$2"
                shift 2
                ;;
            --page|-p)
                PAGE="$2"
                shift 2
                ;;
            --per-page)
                PER_PAGE="$2"
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

    # Validate sort
    if [[ -n "$SORT" && "$SORT" != "indexed" ]]; then
        error "Invalid sort: $SORT. Only 'indexed' is supported" "ArgumentError"
    fi

    # Validate order
    if [[ -n "$ORDER" && "$ORDER" != "asc" && "$ORDER" != "desc" ]]; then
        error "Invalid order: $ORDER. Must be 'asc' or 'desc'" "ArgumentError"
    fi

    # Validate page is a number
    if ! [[ "$PAGE" =~ ^[0-9]+$ ]]; then
        error "Invalid page: $PAGE. Must be a number" "ArgumentError"
    fi

    # Validate per_page is a number
    if ! [[ "$PER_PAGE" =~ ^[0-9]+$ ]]; then
        error "Invalid per-page: $PER_PAGE. Must be a number" "ArgumentError"
    fi
}

# ============================================================================
# BUILD JSON ARGS
# ============================================================================

build_json_args() {
    local base_json
    base_json=$(jq -n \
        --arg query "$QUERY" \
        --argjson page "$PAGE" \
        --argjson perPage "$PER_PAGE" \
        '{
            query: $query,
            page: $page,
            perPage: $perPage
        }')

    # Add optional sort if provided
    if [[ -n "$SORT" ]]; then
        base_json=$(echo "$base_json" | jq --arg sort "$SORT" '. + {sort: $sort}')
    fi

    # Add optional order if provided
    if [[ -n "$ORDER" ]]; then
        base_json=$(echo "$base_json" | jq --arg order "$ORDER" '. + {order: $order}')
    fi

    echo "$base_json"
}

# ============================================================================
# HELP
# ============================================================================

show_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Search code across all GitHub repositories using GitHub MCP server.

Options:
  --query, -q <text>       Search query using GitHub code search syntax (required)
  --sort, -s <field>       Sort field (only 'indexed' is supported)
  --order, -o <order>      Sort order: 'asc' or 'desc'
  --page, -p <number>      Page number for pagination (min 1, default: 1)
  --per-page <number>      Results per page (min 1, max 100, default: 30)
  --help, -h               Show this help message

Examples:
  # Search for a function in Python
  $SCRIPT_NAME --query "function search language:python"

  # Search in a specific repository
  $SCRIPT_NAME -q "repo:owner/repo HttpConnector"

  # Search by path
  $SCRIPT_NAME -q "path:src/ class MyClass"

  # Search with sorting
  $SCRIPT_NAME -q "useState hooks" --sort indexed --order desc

Output:
  JSON formatted search results to stdout

Requires:
  - mcp-cli: https://github.com/philschmid/mcp-cli
  - jq: sudo apt-get install jq (Ubuntu) or brew install jq (macOS)

GitHub Code Search Syntax:
  https://docs.github.com/en/search-github/searching-on-github/searching-code
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

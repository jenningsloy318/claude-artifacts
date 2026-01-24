#!/usr/bin/env bash
#
# GitHub File Contents Script (mcp-cli version)
#
# Get file or directory contents from a GitHub repository using GitHub MCP server via mcp-cli.
#
# Usage:
#   ./github_file_contents.sh --owner "facebook" --repo "react" --path "README.md"
#   ./github_file_contents.sh --owner "facebook" --repo "react" --path "src/"
#
# Examples:
#   ./github_file_contents.sh -o "facebook" -r "react" -p "README.md"
#   ./github_file_contents.sh -o "facebook" -r "react" -p "src/" --ref "main"
#
# Output:
#   JSON formatted file/directory contents to stdout
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_NAME="github"
TOOL_NAME="get_file_contents"
SCRIPT_NAME="$(basename "$0")"

# Default values
OWNER=""
REPO=""
PATH="/"
REF=""
SHA=""

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
            --owner|-o)
                OWNER="$2"
                shift 2
                ;;
            --repo|-r)
                REPO="$2"
                shift 2
                ;;
            --path|-p)
                PATH="$2"
                shift 2
                ;;
            --ref)
                REF="$2"
                shift 2
                ;;
            --sha)
                SHA="$2"
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
    if [[ -z "$OWNER" ]]; then
        error "Required argument --owner missing" "ArgumentError"
    fi

    if [[ -z "$REPO" ]]; then
        error "Required argument --repo missing" "ArgumentError"
    fi
}

# ============================================================================
# BUILD JSON ARGS
# ============================================================================

build_json_args() {
    local base_json
    base_json=$(jq -n \
        --arg owner "$OWNER" \
        --arg repo "$REPO" \
        --arg path "$PATH" \
        '{
            owner: $owner,
            repo: $repo,
            path: $path
        }')

    # Add optional ref if provided
    if [[ -n "$REF" ]]; then
        base_json=$(echo "$base_json" | jq --arg ref "$REF" '. + {ref: $ref}')
    fi

    # Add optional sha if provided (takes precedence over ref)
    if [[ -n "$SHA" ]]; then
        base_json=$(echo "$base_json" | jq --arg sha "$SHA" '. + {sha: $sha}')
    fi

    echo "$base_json"
}

# ============================================================================
# HELP
# ============================================================================

show_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Get file or directory contents from a GitHub repository.

Options:
  --owner, -o <name>       Repository owner (username or organization, required)
  --repo, -r <name>        Repository name (required)
  --path, -p <path>        Path to file or directory (directories must end with '/', default: '/')
  --ref <ref>              Git ref such as 'refs/tags/v1.0.0', 'refs/heads/main'
  --sha <sha>              Commit SHA (if specified, used instead of ref)
  --help, -h               Show this help message

Examples:
  # Get README file contents
  $SCRIPT_NAME --owner "facebook" --repo "react" --path "README.md"

  # List directory contents
  $SCRIPT_NAME -o "facebook" -r "react" -p "src/"

  # Get file from specific branch
  $SCRIPT_NAME -o "facebook" -r "react" -p "README.md" --ref "main"

  # Get file from specific commit
  $SCRIPT_NAME -o "facebook" -r "react" -p "package.json" --sha "abc123"

Output:
  JSON formatted file/directory contents to stdout

Requires:
  - mcp-cli: https://github.com/philschmid/mcp-cli
  - jq: sudo apt-get install jq (Ubuntu) or brew install jq (macOS)

Note:
  Directories must end with a slash '/' (e.g., 'src/', 'components/')
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

#!/usr/bin/env bash
#
# MCP Tool Wrapper Script Template
#
# This template provides a standard pattern for creating shell wrapper scripts
# that interface with mcp-cli to call MCP tools.
#
# Usage:
#   1. Copy this template to your script location
#   2. Set SERVER_NAME and TOOL_NAME
#   3. Implement parse_arguments() to handle CLI arguments
#   4. Implement build_json_args() to build JSON for mcp-cli
#   5. Make executable: chmod +x script.sh
#
# Example:
#   ./my_script.sh --query "search terms" --type deep
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

# MCP server and tool configuration (customize these)
SERVER_NAME="${MCP_SERVER:-example_server}"      # e.g., "exa", "deepwiki"
TOOL_NAME="${MCP_TOOL:-example_tool}"           # e.g., "web_search_exa", "ask_question"
SCRIPT_NAME="$(basename "$0")"

# mcp-cli configuration
MCP_CLI="${MCP_CLI:-mcp-cli}"                   # Path to mcp-cli binary
CONFIG_PATH="${MCP_CONFIG:-}"                    # Optional: path to mcp_servers.json
VERBOSE="${MCP_VERBOSE:-false}"                  # Enable verbose output

# ============================================================================
# ERROR HANDLING
# ============================================================================

error() {
    local msg="$1"
    local error_type="${2:-"ScriptError"}"

    # Output error as JSON to stderr
    echo "{\"success\": false, \"error\": \"$msg\", \"error_type\": \"$error_type\", \"script\": \"$SCRIPT_NAME\"}" >&2
    exit 1
}

log() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo "[INFO] $*" >&2
    fi
}

# ============================================================================
# DEPENDENCY CHECKS
# ============================================================================

check_mcp_cli() {
    if ! command -v "$MCP_CLI" &> /dev/null; then
        error "mcp-cli not found. Install from: https://github.com/philschmid/mcp-cli

Install command:
  curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash

Or with bun:
  bun install -g https://github.com/philschmid/mcp-cli" "DependencyError"
    fi
    log "Found mcp-cli: $($MCP_CLI --version)"
}

check_jq() {
    if ! command -v jq &> /dev/null; then
        error "jq not found. Install jq:

Ubuntu/Debian: sudo apt-get install jq
macOS:       brew install jq
Arch:        sudo pacman -S jq" "DependencyError"
    fi
    log "Found jq: $(jq --version)"
}

validate_required_vars() {
    if [[ -z "$SERVER_NAME" ]]; then
        error "SERVER_NAME not set. Configure MCP_SERVER environment variable or set SERVER_NAME in script." "ConfigurationError"
    fi
    if [[ -z "$TOOL_NAME" ]]; then
        error "TOOL_NAME not set. Configure MCP_TOOL environment variable or set TOOL_NAME in script." "ConfigurationError"
    fi
    log "Server: $SERVER_NAME, Tool: $TOOL_NAME"
}

# ============================================================================
# MCP TOOL INVOCATION
# ============================================================================

call_mcp_tool() {
    local json_args="$1"

    log "Building mcp-cli command..."
    log "Arguments: $json_args"

    # Build mcp-cli command
    local cmd=("$MCP_CLI")
    if [[ -n "$CONFIG_PATH" ]]; then
        cmd+=("-c" "$CONFIG_PATH")
        log "Using config: $CONFIG_PATH"
    fi
    cmd+=("--json")                    # Always output JSON
    cmd+=("$SERVER_NAME/$TOOL_NAME")
    cmd+=("$json_args")

    # Execute and capture output
    local output
    local exit_code

    log "Executing: ${cmd[*]}"
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
            error "mcp-cli error (exit code $exit_code): $output" "MCPError"
        fi
    fi

    # Success - output with metadata
    log "Command successful"
    echo "$output"
}

# ============================================================================
# SCRIPT-SPECIFIC IMPLEMENTATION
# ============================================================================
# Override these functions in your script:

# parse_arguments() {
#     # Parse CLI arguments and set variables
#     # Usage: parse_arguments "$@"
#     #
#     # Example:
#     #   while [[ $# -gt 0 ]]; do
#     #       case "$1" in
#     #           --query|-q) QUERY="$2"; shift 2 ;;
#     #           --type|-t)   TYPE="$2"; shift 2 ;;
#     #           *) error "Unknown argument: $1" ;;
#     #       esac
#     #   done
#     #
#     #   # Validate required arguments
#     #   [[ -z "$QUERY" ]] && error "--query is required"
# }

# build_json_args() {
#     # Build JSON arguments for mcp-cli using jq
#     # Usage: build_json_args
#     # Output: JSON string via echo
#     #
#     # Example:
#     #   jq -n \
#     #       --arg query "$QUERY" \
#     #       --arg type "$TYPE" \
#     #       --arg numResults "$NUM_RESULTS" \
#     #       '{
#     #           query: $query,
#     #           type: $type,
#     #           numResults: ($numResults | tonumber)
#     #       }'
# }

# show_help() {
#     # Display help message
#     # Usage: show_help
#     #
#     # Example:
#     #   cat <<EOF
#     # Usage: $SCRIPT_NAME [OPTIONS]
#     #
#     # Options:
#     #   --query, -q     Search query (required)
#     #   --type, -t      Search type: auto|fast|deep (default: auto)
#     #   --results, -r   Number of results (default: 8)
#     #   --help, -h      Show this help message
#     #
#     # Example:
#     #   $SCRIPT_NAME --query "Next.js 15" --type deep --results 10
#     # EOF
# }

# ============================================================================
# DEFAULT HELP (override show_help() for custom help)
# ============================================================================

show_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

A wrapper script for calling MCP tool: $SERVER_NAME/$TOOL_NAME

Options:
  --help, -h          Show this help message
  --verbose, -v       Enable verbose output
  --config, -c <path> Path to mcp_servers.json

Environment Variables:
  MCP_SERVER          Override server name (default: $SERVER_NAME)
  MCP_TOOL            Override tool name (default: $TOOL_NAME)
  MCP_CLI             Path to mcp-cli binary
  MCP_CONFIG          Path to mcp_servers.json
  MCP_VERBOSE         Enable verbose output

mcp-cli must be installed:
  curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash

For more information, see: https://github.com/philschmid/mcp-cli
EOF
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    # Handle help flag
    if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
        show_help
        exit 0
    fi

    # Handle verbose flag
    if [[ "${1:-}" == "--verbose" ]] || [[ "${1:-}" == "-v" ]]; then
        VERBOSE=true
        shift
    fi

    # Handle config flag
    if [[ "${1:-}" == "--config" ]] || [[ "${1:-}" == "-c" ]]; then
        CONFIG_PATH="$2"
        shift 2
    fi

    log "Starting script: $SCRIPT_NAME"

    # Validate environment
    check_mcp_cli
    check_jq
    validate_required_vars

    # Parse arguments (implemented by each script)
    if declare -f parse_arguments > /dev/null; then
        parse_arguments "$@"
        log "Arguments parsed successfully"
    else
        error "parse_arguments() not implemented. Please implement this function in your script." "NotImplementedError"
    fi

    # Build JSON arguments for tool
    if declare -f build_json_args > /dev/null; then
        local json_args
        json_args=$(build_json_args)
        log "JSON arguments built: $json_args"
    else
        error "build_json_args() not implemented. Please implement this function in your script." "NotImplementedError"
    fi

    # Call MCP tool
    call_mcp_tool "$json_args"
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

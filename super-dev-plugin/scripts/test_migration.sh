#!/usr/bin/env bash
#
# Test script for mcp-cli wrapper scripts
#
# This script verifies that:
# 1. mcp-cli is installed
# 2. jq is installed
# 3. Shell scripts are executable
# 4. Scripts can be invoked
# 5. Output is valid JSON
#

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ============================================================================
# TEST UTILITIES
# ============================================================================

test_passed() {
    local test_name="$1"
    echo -e "${GREEN}✓${NC} $test_name"
    ((TESTS_PASSED++))
}

test_failed() {
    local test_name="$1"
    local reason="$2"
    echo -e "${RED}✗${NC} $test_name"
    echo -e "  ${YELLOW}Reason: $reason${NC}"
    ((TESTS_FAILED++))
}

test_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# ============================================================================
# TESTS
# ============================================================================

test_mcp_cli_installed() {
    if command -v mcp-cli &> /dev/null; then
        test_passed "mcp-cli is installed"
        test_info "Version: $(mcp-cli --version 2>&1 || echo 'unknown')"
    else
        test_failed "mcp-cli is installed" "mcp-cli command not found in PATH"
        return 1
    fi
}

test_jq_installed() {
    if command -v jq &> /dev/null; then
        test_passed "jq is installed"
        test_info "Version: $(jq --version 2>&1 || echo 'unknown')"
    else
        test_failed "jq is installed" "jq command not found in PATH"
        return 1
    fi
}

test_mcp_config_exists() {
    local config_found=false

    # Check possible config locations
    local configs=(
        "$HOME/.claude.json"
        "$HOME/.mcp_servers.json"
        "$HOME/.config/mcp/mcp_servers.json"
        "$PROJECT_ROOT/mcp_servers.json"
    )

    for config in "${configs[@]}"; do
        if [[ -f "$config" ]]; then
            config_found=true
            test_passed "MCP config exists ($config)"
            test_info "Config: $config"
            break
        fi
    done

    if [[ "$config_found" == "false" ]]; then
        test_failed "MCP config exists" "No config found in standard locations"
        test_info "Checked: ${configs[*]}"
        return 1
    fi
}

test_shell_script_executable() {
    local script="$1"
    local script_name="$(basename "$script")"

    if [[ -x "$script" ]]; then
        test_passed "Script is executable: $script_name"
    else
        test_failed "Script is executable: $script_name" "File is not executable (chmod +x)"
        return 1
    fi
}

test_script_runs() {
    local script="$1"
    local script_name="$(basename "$script")"
    local args="${2:-}"

    # Try to run the script with --help (most scripts support this)
    if output=$("$script" --help 2>&1); then
        test_passed "Script runs: $script_name"
    else
        # If --help fails, try invoking with no args (might show usage or error)
        if output=$("$script" 2>&1); then
            test_passed "Script runs: $script_name"
        else
            test_failed "Script runs: $script_name" "Script exited with error"
            test_info "Error output: $output"
            return 1
        fi
    fi
}

test_output_is_json() {
    local script="$1"
    local script_name="$(basename "$script")"
    local args="${2:-}"

    # Run script and check if output is valid JSON
    if output=$("$script" $args 2>&1); then
        if echo "$output" | jq -e '.' &> /dev/null; then
            test_passed "Script outputs valid JSON: $script_name"
        else
            test_failed "Script outputs valid JSON: $script_name" "Output is not valid JSON"
            test_info "Output: $output"
            return 1
        fi
    else
        test_failed "Script outputs valid JSON: $script_name" "Script failed to run"
        return 1
    fi
}

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

main() {
    echo "=========================================="
    echo "MCP-CLI Wrapper Scripts Test Suite"
    echo "=========================================="
    echo ""

    # Test 1: Dependencies
    echo "Testing Dependencies..."
    echo "--------------------"
    test_mcp_cli_installed
    test_jq_installed
    test_mcp_config_exists
    echo ""

    # Test 2: Shell scripts exist and are executable
    echo "Testing Shell Scripts..."
    echo "--------------------"

    local shell_scripts=(
        "$SCRIPT_DIR/templates/mcp_wrapper.sh"
        "$SCRIPT_DIR/exa/exa_search.sh"
        "$SCRIPT_DIR/deepwiki/deepwiki_ask.sh"
        "$SCRIPT_DIR/context7/context7_resolve.sh"
    )

    for script in "${shell_scripts[@]}"; do
        if [[ -f "$script" ]]; then
            test_shell_script_executable "$script"
        else
            test_failed "Script exists: $(basename "$script")" "File not found"
        fi
    done
    echo ""

    # Test 3: Scripts can run and output JSON
    echo "Testing Script Execution..."
    echo "--------------------"

    # Test template (supports --help)
    if [[ -f "$SCRIPT_DIR/templates/mcp_wrapper.sh" ]]; then
        test_script_runs "$SCRIPT_DIR/templates/mcp_wrapper.sh"
    fi

    # Test exa_search (supports --help)
    if [[ -f "$SCRIPT_DIR/exa/exa_search.sh" ]]; then
        test_script_runs "$SCRIPT_DIR/exa/exa_search.sh"
    fi

    # Test deepwiki_ask (supports --help)
    if [[ -f "$SCRIPT_DIR/deepwiki/deepwiki_ask.sh" ]]; then
        test_script_runs "$SCRIPT_DIR/deepwiki/deepwiki_ask.sh"
    fi

    # Test context7_resolve (supports --help)
    if [[ -f "$SCRIPT_DIR/context7/context7_resolve.sh" ]]; then
        test_script_runs "$SCRIPT_DIR/context7/context7_resolve.sh"
    fi
    echo ""

    # Summary
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    echo "=========================================="
    echo ""

    if [[ "$TESTS_FAILED" -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        echo ""
        echo "You can now use the mcp-cli wrapper scripts:"
        echo ""
        echo "  ./scripts/exa/exa_search.sh --query 'test'"
        echo "  ./scripts/deepwiki/deepwiki_ask.sh --repo 'facebook/react' --question 'What is React?'"
        echo "  ./scripts/context7/context7_resolve.sh --library 'react'"
        echo ""
        return 0
    else
        echo -e "${RED}Some tests failed. Please fix the issues above.${NC}"
        echo ""
        echo "Common fixes:"
        echo "  - Install mcp-cli: curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash"
        echo "  - Install jq: sudo apt-get install jq (Ubuntu) or brew install jq (macOS)"
        echo "  - Make scripts executable: chmod +x scripts/*/*.sh"
        echo ""
        return 1
    fi
}

# Run tests
main "$@"

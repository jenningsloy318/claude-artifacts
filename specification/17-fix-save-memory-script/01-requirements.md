# Fix save_memory.py Script - Requirements

## Current Issues
1. **Script failure**: The script is throwing "'bool' object is not iterable" error during the "Generating memory with AI" phase
2. **No local storage**: No memory is being saved to .claude/memories directory
3. **No remote storage**: No memory is being sent to nowledge MCP server

## Reproduction Steps
Based on the error message and code analysis:
1. The script runs when triggered by context compaction
2. It successfully parses the transcript
3. It fails during the "Generating memory with AI" phase
4. Error occurs: "'bool' object is not iterable"

## Expected Behavior
1. Script should parse transcript without errors
2. Generate memory using AI (Claude API) or fall back to structured extraction
3. Save memory locally to .claude/memories directory
4. Optionally persist to nowledge MCP server if configured

## Error Context
- Error type: TypeError
- Error message: "'bool' object is not iterable"
- Phase: "Generating memory with AI"
- Line: Unknown (needs debugging)

## Environment Variables
- CLAUDE_SUMMARY_API_KEY: Required for LLM-based memory generation
- CLAUDE_SUMMARY_API_URL: Optional custom API URL

## Dependencies
- anthropic: Python package for Claude API
- mcp-use: Python package for MCP HttpConnector (optional)
- nowledge MCP server: Optional remote storage
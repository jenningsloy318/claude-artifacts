# mcp-use Agents Adapters Research Summary

**Date:** 2025-11-28
**Status:** Research Complete
**Conclusion:** Not suitable for session summarization; useful for tool-use integration

## Overview

The `mcp-use` library provides adapters in `mcp_use.agents.adapters` for converting MCP tools to formats compatible with different AI frameworks. This research evaluated whether these adapters could be used to simplify the precompact hook's summarization workflow.

## Available Adapters

| Adapter Class | Provider | Output Format | Dependency |
|---------------|----------|---------------|------------|
| `BaseAdapter` | Abstract base | N/A | None |
| `LangChainAdapter` | LangChain | `BaseTool` | `langchain` |
| `AnthropicMCPAdapter` | Anthropic | `dict` with `input_schema` | `anthropic` |
| `OpenAIMCPAdapter` | OpenAI | `{"type": "function", ...}` | `openai` |
| `GoogleMCPAdapter` | Google | `types.FunctionDeclaration` | `google-genai` |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BaseAdapter (Abstract)                    │
├─────────────────────────────────────────────────────────────┤
│ - fix_schema()        - Schema standardization               │
│ - parse_result()      - Result parsing                       │
│ - load_tools_for_connector()   - Tool loading with caching  │
│ - _convert_tool()     - Abstract: framework-specific        │
│ - _convert_resource() - Abstract: framework-specific        │
│ - _convert_prompt()   - Abstract: framework-specific        │
└───────────────────────────┬─────────────────────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
    ▼                       ▼                       ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Anthropic  │    │   OpenAI    │    │   Google    │
│  Adapter    │    │   Adapter   │    │   Adapter   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Key Features

1. **Tool Executors**: Each adapter maintains a `tool_executors` dict mapping tool names to async callables
2. **Schema Conversion**: Converts MCP JSON schemas to provider-specific formats
3. **Resource as Tools**: MCP resources are converted to "read-only" tools
4. **Prompt as Tools**: MCP prompts become callable tools with parameters
5. **Disallowed Tools**: Filter out specific tools via constructor parameter

## Purpose of Adapters

The adapters are designed to:
- Convert MCP tools to LLM-compatible tool formats
- Enable LLMs to use MCP server tools via their native tool-use APIs
- Bridge MCP protocol with AI framework conventions

**Important:** The adapters do NOT provide:
- Direct text generation capabilities
- Session summarization functionality
- API key management for LLM calls

## Evaluation for Precompact Hook

### Question
Can `AnthropicMCPAdapter` be used to call Claude API for summarization, eliminating the need for `CLAUDE_SUMMARY_API_KEY`?

### Answer
**No.** The adapters are for tool format conversion, not for making LLM API calls.

### Reasons

1. **Wrong abstraction level**: Adapters convert MCP tools to LLM tool formats, not vice versa
2. **API key still required**: Using `MCPAgent` with `ChatAnthropic` still requires `ANTHROPIC_API_KEY`
3. **No summarization support**: Adapters don't provide text generation capabilities

### Alternative Approaches Considered

| Approach | Feasibility | Notes |
|----------|-------------|-------|
| Use `AnthropicMCPAdapter` directly | Not applicable | Wrong use case |
| Use `MCPAgent` + `ChatAnthropic` | Requires API key | Same as current approach |
| Use local LLM MCP server | Possible | Would need separate setup |
| Keep current direct API call | Recommended | Simplest solution |

## Decision

Keep the current implementation with:
- `CLAUDE_SUMMARY_API_KEY` - Dedicated API key for summarization
- `CLAUDE_SUMMARY_API_URL` - Optional custom endpoint
- Direct use of `anthropic` Python SDK

This provides:
- Clear separation of concerns
- Dedicated API key for summarization feature
- No dependency on mcp-use adapters for this use case

## When to Use Adapters

The mcp-use adapters ARE useful for:

1. **Building AI agents** that orchestrate MCP tools
   ```python
   from mcp_use import MCPAgent
   from langchain_anthropic import ChatAnthropic

   agent = MCPAgent(llm=ChatAnthropic(...), client=client)
   result = await agent.run("Search for X and summarize")
   ```

2. **Multi-provider tool integration**
   ```python
   # Same MCP tools, different providers
   anthropic_tools = AnthropicMCPAdapter().load_tools_for_connector(connector)
   openai_tools = OpenAIMCPAdapter().load_tools_for_connector(connector)
   ```

3. **Custom agent implementations**
   ```python
   adapter = AnthropicMCPAdapter(disallowed_tools=["dangerous_tool"])
   tools = await adapter.load_tools_for_connector(connector)
   # Use tools with Anthropic tool-use API
   ```

## Source Files

Location: `libraries/python/mcp_use/agents/adapters/`

| File | Size | Description |
|------|------|-------------|
| `__init__.py` | 582B | Exports all adapter classes |
| `base.py` | 12,497B | Abstract base adapter |
| `anthropic.py` | 3,753B | Anthropic adapter |
| `openai.py` | 4,236B | OpenAI adapter |
| `google.py` | 4,284B | Google adapter |
| `langchain_adapter.py` | 8,905B | LangChain adapter |

## Related Specifications

- [11-mcp-http-connector](../11-mcp-http-connector/01-specification.md) - HTTP connector pattern
- [12-mcp-stdio-connector](../12-mcp-stdio-connector/01-specification.md) - Stdio connector pattern
- [13-mcp-websocket-connector](../13-mcp-websocket-connector/01-specification.md) - WebSocket connector pattern

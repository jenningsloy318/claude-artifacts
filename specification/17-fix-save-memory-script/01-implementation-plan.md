# Implementation Plan - Fix save_memory.py Script

## Phase 1: Critical Fixes (Priority: High)

### Task 1.1: Add Type Validation Helper Function
- Location: Top of script after imports
- Create `ensure_list()` helper function
- Add `ensure_string()` helper function

### Task 1.2: Fix extract_conversation_content() Function
- Lines 156-204: Add type checking before iterating over `content`
- Ensure `user_messages`, `assistant_messages`, `tool_calls` are always lists
- Add guards for boolean/None values

### Task 1.3: Fix generate_memory_with_llm() Function
- Lines 341-344: Ensure sliced values are lists
- Add type validation before list operations
- Fix prompt generation with safe list comprehensions

### Task 1.4: Fix List Comprehensions in Prompt
- Lines 398-404: Add type guards in JSON serialization
- Ensure safe iteration even with malformed data

## Phase 2: Defensive Programming (Priority: Medium)

### Task 2.1: Add Input Validation
- Validate transcript message structure
- Add guards for nested dictionary access
- Ensure consistent data types

### Task 2.2: Improve Error Messages
- Add debug logging for type errors
- Include more context in error messages
- Log problematic data structure

## Phase 3: Testing (Priority: Medium)

### Task 3.1: Create Test Script
- Create test_transcripts/ directory
- Add various transcript formats (normal, edge cases, malformed)
- Create simple test runner

### Task 3.2: Manual Testing
- Test with sample transcripts
- Verify local memory storage
- Test MCP integration if available

## Implementation Details

### Code Changes Summary

1. **Helper Functions** (add after line 27):
```python
def ensure_list(value, default=None):
    """Ensure value is a list, return default or empty list if not."""
    if isinstance(value, list):
        return value
    return default if default is not None else []

def ensure_string(value, default=""):
    """Ensure value is a string, return default if not."""
    if isinstance(value, str):
        return value
    return default
```

2. **Fix extract_conversation_content()**:
```python
# Replace content iteration with safe version
if isinstance(content, str) and content.strip():
    # ... existing string logic
elif isinstance(content, list) and content:  # Add 'and content' guard
    for block in content:
        if isinstance(block, dict):
            # ... existing dict logic
```

3. **Fix generate_memory_with_llm()**:
```python
# Ensure lists before slicing
user_msgs = ensure_list(content.get('user_messages', []))[:20]
assistant_msgs = ensure_list(content.get('assistant_messages', []))[:20]
tool_calls = ensure_list(content.get('tool_calls', []))[:50]
files_modified = ensure_list(content.get('files_modified', []))
```

## Rollback Plan
If issues arise:
1. Git revert to original version
2. Apply minimal fix: just add type checks before iteration
3. Keep changes isolated to prevent side effects

## Verification Steps
1. Run script with various transcript types
2. Check .claude/memories directory for output
3. Verify no "'bool' object is not iterable" errors
4. Test MCP integration if configured
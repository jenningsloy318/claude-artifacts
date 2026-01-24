---
name: specification-templates
description: Technical specification templates, naming conventions, validation gates, and quality standards for writing unambiguous implementation specifications. Reference for Phase 6 (Specification Writing) in super-dev workflow.
---

# Specification Templates Reference

Reference documentation for writing comprehensive technical specifications. Use this during Phase 6 (Specification Writing) of the super-dev workflow.

## Core Principles

### Single Implementation Guarantee
Specification MUST result in exactly ONE valid implementation.

### No Ambiguity
All code elements must be explicitly specified - no room for interpretation.

### Feature-Specific Naming
All names use feature-specific prefixes to avoid generic names.

## Document Templates

### Document 1: Technical Specification

```markdown
# Technical Specification: [Feature/Fix Name]

**Date:** [timestamp]
**Author:** Claude
**Status:** Draft

## 1. Overview

### 1.1 Summary
[Brief description of what will be built/fixed]

### 1.2 Goals
- [Goal 1]
- [Goal 2]

### 1.3 Non-Goals
- [What is explicitly out of scope]

## 2. Background

### 2.1 Context
> From Research Report: [key finding]

### 2.2 Current State
> From Assessment: [key finding]

### 2.3 Problem Statement
> From Debug Analysis: [root cause]

## 3. Technical Design

### 3.1 Architecture

┌─────────────────┐     ┌─────────────────┐
│   Component A   │────▶│   Component B   │
│                 │     │                 │
│ - Responsibility│     │ - Responsibility│
└─────────────────┘     └─────────────────┘
       │                       │
       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Component C   │     │   Component D   │
└─────────────────┘     └─────────┘

### 3.2 Components

#### Component 1: [Name]
- **Purpose:** [description]
- **Responsibilities:**
  - [responsibility 1]
  - [responsibility 2]
- **Interface:**
  ```typescript
  interface [SpecificComponentName] {
    [descriptiveMethod](): ReturnType;
    [anotherDescriptiveMethod](): AnotherType;
  }
  ```
- **File Location:** `path/to/[specific-filename].ts`

#### Component 2: [Name]
[same structure]

### 3.3 Data Model (MANDATORY: Specific Field Names)

```typescript
/**
 * [FeatureName][EntityName] - [Brief description]
 */
interface [FeatureName][EntityName] {
  // Primary identification
  [entity]Id: string;              // e.g., userId, orderId
  [entity]Name: string;            // e.g., userName, productName

  // Core attributes
  [entity][Property]: Type;        // e.g., userEmail, productPrice
  [entity][Attribute]: Type;       // e.g., userStatus, orderStatus

  // Metadata
  [entity]CreatedAt: Date;         // Always use descriptive suffix
  [entity]UpdatedAt: Date;         // Always use descriptive suffix
}
```

### 3.4 API Design

#### Endpoint 1: [Method] [Path]
- **Function Name:** `[feature][Action]` (e.g., `userLogin`, `orderCreate`)
- **Request:**
  ```json
  {
    "[entity][Property]": "value",
    "[entity][Attribute]": "value"
  }
  ```
- **Response:**
  ```json
  {
    "[feature][Entity]": {
      "[entity]Id": "string",
      "[entity]Name": "string"
    }
  }
  ```
- **Errors:**
  - `400`: [specific error condition]
  - `404`: [specific error condition]

### 3.5 Function Specifications (MANDATORY: No Ambiguity)

#### Function: [FeatureName][Action]

```typescript
/**
 * [One-sentence description]
 * @param [descriptiveParamName] - [description]
 * @returns [description of return value]
 * @throws [SpecificErrorType] - [when this error is thrown]
 */
async function [featureName][action](
  [descriptiveParamName]: ParamType,
  [anotherDescriptiveParam]: AnotherType
): Promise<ReturnType> {
  // Implementation is unambiguous because:
  // 1. All parameter names are feature-specific and descriptive
  // 2. Return type is explicitly defined
  // 3. Error conditions are documented
  // 4. No "data", "result", or "value" generic names
}
```

### 3.6 Variable Naming Conventions (MANDATORY)

| Variable Type | Naming Pattern | Examples | Prohibited |
|---------------|----------------|----------|------------|
| Local variables | `[feature][entity][property]` | `userAuthState`, `orderTotal` | `data`, `val`, `temp` |
| Parameters | `[descriptive][entity]` | `userData`, `requestConfig` | `obj`, `arg`, `param` |
| Constants | `[FEATURE_NAME]_[CONSTANT]` | `MAX_LOGIN_ATTEMPTS` | `limit`, `max` |
| Booleans | `[is/has/should][Condition]` | `isAuthenticated` | `flag`, `status` |
| Arrays | `[entity][List/Array]` | `userList`, `orderArray` | `items`, `list` |
| Functions | `[verb][Noun]` or `[feature][Action]` | `getUserById()` | `process()`, `handle()` |

### 3.7 Error Handling

| Error Case | Handler | User Feedback |
|------------|---------|---------------|
| [specific case] | [handler] | [message] |

## 4. Implementation Approach

### 4.1 Technology Stack
- Language: [language]
- Framework: [framework]
- Libraries: [list]

### 4.2 Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| [name] | [version] | [why needed] |

### 4.3 Configuration
```
[Configuration changes needed]
```

## 5. Testing Strategy

### 5.1 Unit Tests
| Component | Test Function Name | Test Cases |
|-----------|-------------------|------------|
| [component] | `[feature][Action][Should/When]` | [cases] |

**Test Naming Convention:**
- Format: `[featureName]_[action]_should_[expectedOutcome]`
- Examples:
  - `userLogin_should_returnToken_when_credentialsValid`
  - `orderCreate_should_failInsufficientFunds_when_balanceLow`

### 5.2 Edge Cases
| Edge Case | Expected Behavior |
|-----------|-------------------|
| [case] | [behavior] |

## 6. Security Considerations

### 6.1 Input Validation
| Input | Validation | Sanitization |
|-------|------------|--------------|
| [input field] | [validation rules] | [sanitization method] |

### 6.2 Authentication & Authorization
- **Auth required:** [yes/no]
- **Permission checks:** [list of permissions]
- **Role restrictions:** [roles that can access]

### 6.3 Data Protection
- **Sensitive data:** [list of sensitive fields]
- **Encryption:** [requirements]
- **Logging:** [what to log, what to redact]

### 6.4 OWASP Considerations
| Risk | Applicable | Mitigation |
|------|------------|------------|
| Injection | [yes/no] | [mitigation] |
| Broken Auth | [yes/no] | [mitigation] |
| XSS | [yes/no] | [mitigation] |
| CSRF | [yes/no] | [mitigation] |

## 7. Performance Considerations

### 7.1 Caching Strategy
| Data | Cache Type | Duration | Trigger |
|------|-----------|----------|--------|
| [data] | [memory/redis/cdn] | [duration] | [trigger] |

### 7.4 Scalability
- **Bottlenecks:** [identified bottlenecks]
- **Horizontal scaling:** [considerations]

## 8. Rollout Plan
1. [Step 1]
2. [Step 2]

## 9. Unambiguous Implementation Requirements (MANDATORY)

### 9.1 Single Implementation Guarantee
This specification MUST result in exactly ONE valid implementation:

- [ ] **All function names are specified** - No room for interpretation
- [ ] **All parameter names are specified** - No generic names
- [ ] **All variable names follow conventions** - Feature-specific prefixes
- [ ] **All file paths are specified** - No ambiguity about where code goes
- [ ] **All conditional behaviors are documented** - No "if needed, do X"
- [ ] **All error cases are listed** - No "handle errors appropriately"
- [ ] **All data structures are fully defined** - No "etc." or "and so on"

### 9.2 Ambiguity Checklist

- [ ] **No pronouns** - Replace "it", "they", "this" with specific nouns
- [ ] **No "etc." or "and so on"** - List everything explicitly
- [ ] **No "appropriate" or "suitable"** - Specify exact values
- [ ] **No "handle" or "process"** - Specify exact actions
- [ ] **No "if needed" or "when applicable"** - Specify exact conditions
- [ ] **No generic names** - All names are feature-specific
- [ ] **No optional behaviors** - Everything is required or explicitly conditional

### 9.3 Naming Convention Verification

- [ ] **No generic variable names** (data, item, value, result, temp, obj)
- [ ] **No single-letter names** (except loop indices i, j, k)
- [ ] **No abbreviations** (except id, url, api, http, etc.)
- [ ] **All names use feature-specific prefixes**
- [ ] **All functions use verb-noun pattern**
- [ ] **All constants use UPPER_CASE**
- [ ] **All booleans use is/has/should prefix**

## 10. Open Questions
- [ ] [Question 1]
- [ ] [Question 2]

## 11. References (MUST include canonical links to source documents)
- Requirements: [link]
- Research Report: [link]
- Assessment: [link]
- Architecture: [link if applicable]
- Design Spec: [link if applicable]
- Debug Analysis: [link if applicable]
```

### Document 2: Implementation Plan

```markdown
# Implementation Plan: [Feature/Fix Name]

**Specification:** [link to spec]
**Estimated Phases:** [number]

## File Inventory (MANDATORY)

### Files to be Created
| File Path | Purpose | Component/Feature |
|-----------|---------|-------------------|
| `path/to/[SpecificFileName].ts` | [description] | [component] |

### Files to be Modified
| File Path | Changes Required | Functions Affected |
|-----------|----------------|-------------------|
| `path/to/existing/file.ts` | [description] | `[functionName]` |

### Files to be Deleted
| File Path | Reason | Replacement |
|-----------|--------|-------------|
| `path/to/old/file.ts` | [reason] | `path/to/new/file.ts` |

### File Summary
- **Total Files Created:** [count]
- **Total Files Modified:** [count]
- **Total Files Deleted:** [count]

## Milestones

### Milestone 1 (Phase 1): [Name]
**Goal:** [What this milestone achieves]
**Dependencies:** [Prerequisites]

#### Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

#### Acceptance Criteria
- [Criterion 1]
- [Criterion 2]

#### Files Affected (MANDATORY)
**Created:**
- `path/to/[SpecificFile1].ts`

**Modified:**
- `path/to/existing/file.ts` (add `[functionName]`)

**Deleted:**
- `path/to/old/file.ts`

### Milestone 2 (Phase 2): [Name]
[same structure]

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [risk] | [High/Med/Low] | [High/Med/Low] | [mitigation] |
```

### Document 3: Task List

```markdown
# Task List: [Feature/Fix Name]

**Specification:** [link]
**Implementation Plan:** [link]

## Tasks

### Phase 1: [Milestone Name]

- [ ] **Task 1.1:** [Specific action with clear deliverable]
  - **File:** `path/to/file.ts`
  - **Acceptance:** [how to verify completion]
  - **Estimated:** [time estimate]

- [ ] **Task 1.2:** [Specific action]
  - **Files:** `path/to/file1.ts`, `path/to/file2.ts`
  - **Dependencies:** Task 1.1
  - **Acceptance:** [verification method]

### Phase 2: [Milestone Name]

- [ ] **Task 2.1:** [Specific action]
  - **File:** `path/to/file.ts`
  - **Tests:** `path/to/file.test.ts`

## Acceptance Criteria

All tasks are complete when:
- [ ] All acceptance criteria met
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
```

## Naming Convention Rules (MANDATORY)

### Prohibited Generic Names
**AVOID these variable names:**
- `data`
- `item`
- `value`
- `result`
- `temp`
- `obj`
- `val`

**USE feature-specific prefixes:**
- `userAuth...`, `orderProcess...`, `productCatalog...`

### Function Naming
- **Pattern:** `[verb][Noun]` or `[feature][Action]`
- Examples:
  - `getUserById()` ✓
  - `authenticateUser()` ✓
  - `process()` ✗
  - `handle()` ✗

### Constant Naming
- **Pattern:** `[FEATURE_NAME]_[CONSTANT]`
- Examples:
  - `MAX_LOGIN_ATTEMPTS` ✓
  - `DEFAULT_TIMEOUT` ✓
  - `MAX` ✗
  - `LIMIT` ✗

### Boolean Naming
- **Pattern:** `[is/has/should][Condition]`
- Examples:
  - `isAuthenticated` ✓
  - `hasPermission` ✓
  - `flag` ✗
  - `status` ✗

### Array Naming
- **Pattern:** `[entity][List/Array]`
- Examples:
  - `userList` ✓
  - `orderArray` ✓
  - `items` ✗
  - `list` ✗

## Validation Gates (MANDATORY)

### Before Submitting Specification

#### Naming Convention Verification
- [ ] **No generic variable names** (data, item, value, result, temp, obj)
- [ ] **No single-letter names** (except loop indices i, j, k)
- [ ] **No abbreviations** (except id, url, api, http, etc.)
- [ ] **All names use feature-specific prefixes**
- [ ] **All functions use verb-noun pattern**
- [ ] **All constants use UPPER_CASE**
- [ ] **All booleans use is/has/should prefix**

#### No Ambiguity Verification
- [ ] **All function names are specified** - No room for interpretation
- [ ] **All parameter names are specified** - No generic names allowed
- [ ] **All file paths are specified** - No ambiguity about where code goes
- [ ] **All conditional behaviors are documented** - No "if needed, do X"
- [ ] **All error cases are listed** - No "handle errors appropriately"
- [ ] **No pronouns** - Replace "it", "they", "this" with specific nouns
- [ ] **No "etc." or "and so on"** - List everything explicitly
- [ ] **No "appropriate" or "suitable"** - Specify exact values
- [ ] **No "handle" or "process"** - Specify exact actions
- [ ] **No optional behaviors** - Everything is required or explicitly conditional

#### File Inventory Verification
- [ ] **Files to be Created** - Complete list with specific file names
- [ ] **Files to be Modified** - Complete list with specific changes required
- [ ] **Files to be Deleted** - Complete list with reasons
- [ ] **File Summary** - Total counts for created/modified/deleted
- [ ] **Each milestone includes Files Affected section** - Created/Modified/Deleted

#### Function Specification Verification
- [ ] All functions have descriptive names
- [ ] All parameters have descriptive names
- [ ] Return types are explicitly defined
- [ ] Error cases are documented
- [ ] No optional behaviors exist without explicit conditions

## Quality Checklist

### Specification Completeness
- [ ] Overview section complete with goals and non-goals
- [ ] Background section references all input documents
- [ ] Technical design includes architecture and components
- [ ] Data model fully defined with specific field names
- [ ] API design includes all endpoints with request/response formats
- [ ] Function specifications provided for all key functions
- [ ] Variable naming conventions followed
- [ ] Error handling documented
- [ ] Testing strategy outlined
- [ ] Security considerations addressed
- [ ] Performance considerations documented
- [ ] Rollout plan defined
- [ ] References to all input documents included

### Unambiguous Implementation
- [ ] Single implementation guarantee satisfied
- [ ] No pronouns used
- [ ] No "etc." or "and so on"
- [ ] No generic names (data, item, value, result, temp, obj)
- [ ] All file paths specified
- [ ] All conditional behaviors documented
- [ ] All error cases listed

## Common Specification Mistakes

### DON'T: Leave Ambiguity
❌ "Handle errors appropriately"
✅ "Return `UserNotFoundError` when user not found, return `ValidationError` on invalid input"

❌ "Process the data"
✅ "Validate and transform user input for database storage"

❌ "Use appropriate caching"
✅ "Cache user sessions in Redis for 30 minutes"

### DON'T: Use Generic Names
❌ `const data = await fetchData()`
✅ `const userResponse = await fetchUserProfile()`

❌ `function process(items) { ... }`
✅ `function transformOrderItems(orderItems) { ... }`

### DON'T: Skip File Inventory
❌ "Create necessary files"
✅ **File Inventory:**
  - Created: `src/components/UserProfile.tsx`, `src/services/userApi.ts`
  - Modified: `src/types/user.ts` (add `UserProfile` interface)

### DON'T: Skip References
❌ "See research report"
✅ "**Research Report** (specification/02-research-report.md)"
```

## Reference

This is a reference document extracted from the `super-dev:spec-writer` agent. For full agent behavior during Phase 6, invoke:

```
Task(subagent_type: "super-dev:spec-writer", prompt: "Write specification for: [feature]")
```

# Technical Specification: dev-workflow:code-reviewer Agent

**Date:** 2025-11-24
**Author:** Claude
**Status:** Draft

## 1. Overview

### 1.1 Summary

Create a specification-aware code review agent for the dev-workflow plugin that validates implementation against technical specifications, ensures code quality across eight dimensions, and provides actionable feedback with clear severity classifications. This agent replaces the external dependency on `superpowers:code-reviewer`.

### 1.2 Goals

- Remove external dependency on `superpowers:code-reviewer`
- Provide specification-aware code review that validates implementation against stated requirements
- Review code across 8 quality dimensions (correctness, security, performance, maintainability, testability, error handling, consistency, accessibility)
- Integrate with project-specific linting and static analysis tools
- Produce structured, actionable feedback with severity tiers (Critical/High/Medium/Low/Info)
- Support incremental review via Git SHA scoping (BASE_SHA to HEAD_SHA)

### 1.3 Non-Goals

- Full multi-agent CodeAgent-style architecture (future enhancement)
- Learning from rejected suggestions (future enhancement)
- CI/CD pipeline integration (future enhancement)
- Custom review rules per team/project (future enhancement)
- Metrics dashboard for review quality (future enhancement)

## 2. Background

### 2.1 Context

> From Research Report: CodeAgent (arXiv:2402.02172) establishes the academic gold standard for multi-agent LLM code review with a supervisory QA-Checker agent. The superpowers:code-reviewer skill demonstrates effective Claude Code integration with structured feedback (Strengths/Issues/Assessment) and git SHA-based diff scoping. Industry research shows AI+SAST hybrid approaches reduce false positives by up to 91%.

Key patterns to incorporate:
1. **Multi-aspect review** with specialized passes per dimension
2. **Specification-aware validation** comparing implementation to requirements
3. **Structured output** with severity tiers and file:line references
4. **Tool integration** running linters/SAST before AI review
5. **Git SHA scoping** for precise diff-based review

### 2.2 Current State

> From Assessment: The dev-workflow plugin currently depends on external `superpowers:code-reviewer` agent referenced in execution-coordinator.md and SKILL.md. This creates an external dependency that may not be available, may not understand our workflow context, and cannot be customized for our documentation chain.

Current references to replace:
- `execution-coordinator.md`: Testing Agent Specialist table
- `SKILL.md`: External Agents section
- `spec-writer.md`: Task TF.3 agent reference

### 2.3 Problem Statement

> From Requirements: The real value of code review is ensuring the code solves the right problem correctly, not just formatting compliance. Without specification awareness, reviews become generic style/lint checks that miss functional correctness and design intent.

## 3. Technical Design

### 3.1 Architecture

```
+------------------------------------------------------------------+
|                    Code Reviewer Orchestrator                      |
|                                                                    |
|  1. Parse Input Context (specification, implementation summary)   |
|  2. Scope Changes (BASE_SHA to HEAD_SHA or file list)            |
|  3. Run Static Analysis (detect and invoke project linters)       |
|  4. Execute Dimension Reviews (8 specialized passes)              |
|  5. Synthesize Findings (aggregate, deduplicate, prioritize)     |
|  6. Generate Report (structured markdown output)                  |
+------------------------------------------------------------------+
         |              |              |              |
         v              v              v              v
+----------------+ +----------------+ +----------------+ +----------------+
| Specification  | | Static         | | Dimension      | | Report         |
| Validator      | | Analysis       | | Review         | | Generator      |
|                | | Integrator     | | Modules        |                  |
| - Parse spec   | | - Detect tools | | - Correctness  | | - Aggregate    |
| - Extract      | | - Run linters  | | - Security     | | - Deduplicate  |
|   criteria     | | - Parse output | | - Performance  | | - Prioritize   |
| - Build        | | - Filter noise | | - Maintain.    | | - Format       |
|   checklist    | |                | | - Testability  | |                |
|                | |                | | - Error Hdlg   | |                |
|                | |                | | - Consistency  | |                |
|                | |                | | - Access.      | |                |
+----------------+ +----------------+ +----------------+ +----------------+
```

### 3.2 Components

#### Component 1: Input Parser

- **Purpose:** Parse and validate all input context for the review
- **Responsibilities:**
  - Extract specification document path and contents
  - Extract implementation summary (file list, change description)
  - Extract git diff scope (BASE_SHA, HEAD_SHA) if provided
  - Validate all required inputs are present
- **Interface:**
  ```typescript
  interface InputContext {
    specification: string;           // Path to tech spec
    implementation_summary: string;  // Summary of changes
    base_sha?: string;              // Git SHA before changes
    head_sha?: string;              // Git SHA after changes
    files_changed?: string[];       // List of changed files
    project_root: string;           // Root path of project
  }
  ```

#### Component 2: Specification Validator

- **Purpose:** Parse specification and build validation checklist
- **Responsibilities:**
  - Read and parse technical specification document
  - Extract acceptance criteria
  - Extract non-goals (to verify not accidentally implemented)
  - Build checklist of requirements to verify
  - Reference patterns from code-assessor output
- **Interface:**
  ```typescript
  interface SpecificationChecklist {
    acceptance_criteria: string[];
    non_goals: string[];
    api_contracts: APIContract[];
    data_models: DataModel[];
    error_cases: ErrorCase[];
    patterns_to_follow: Pattern[];
  }
  ```

#### Component 3: Static Analysis Integrator

- **Purpose:** Detect and run project-specific linting/SAST tools
- **Responsibilities:**
  - Detect project linting configuration
  - Run appropriate linter commands
  - Parse linter output into structured findings
  - Filter out noise (style-only issues already fixed)
  - Pass meaningful findings to AI review
- **Detection Logic:**
  ```bash
  # TypeScript/JavaScript
  if [ -f "eslint.config.js" ] || [ -f ".eslintrc*" ]; then
      npx eslint --format json [files]
  fi
  if [ -f "biome.json" ]; then
      npx biome check --reporter json [files]
  fi

  # Python
  if [ -f "pyproject.toml" ] || [ -f "ruff.toml" ]; then
      ruff check --output-format json [files]
  fi

  # Rust
  if [ -f "Cargo.toml" ]; then
      cargo clippy --message-format json
  fi

  # Go
  if [ -f "go.mod" ]; then
      golangci-lint run --out-format json
  fi
  ```

#### Component 4: Dimension Review Modules

- **Purpose:** Perform specialized review for each quality dimension
- **Responsibilities:** Execute focused analysis per dimension

| Dimension | Focus Areas | Priority | Key Checks |
|-----------|-------------|----------|------------|
| **Correctness** | Logic, specification compliance | P0 | Does code match spec? Are acceptance criteria met? |
| **Security** | Vulnerabilities, OWASP Top 10 | P0 | Input validation, auth, injection, secrets |
| **Performance** | Efficiency, scalability | P1 | N+1 queries, memory leaks, unnecessary computation |
| **Maintainability** | Readability, complexity | P1 | Cognitive complexity, naming, documentation |
| **Testability** | Test structure, coverage | P1 | Dependency injection, pure functions, test coverage |
| **Error Handling** | Graceful degradation | P1 | Try/catch, error messages, recovery paths |
| **Consistency** | Pattern adherence | P2 | Follows project patterns from assessment |
| **Accessibility** | WCAG compliance | P2 | Screen reader, keyboard nav, contrast (UI only) |

#### Component 5: Report Generator

- **Purpose:** Synthesize findings into structured review report
- **Responsibilities:**
  - Aggregate findings across all dimensions
  - Deduplicate overlapping issues
  - Prioritize by severity
  - Format as structured markdown
  - Determine overall verdict

### 3.3 Data Model

```typescript
// Issue severity levels (SonarQube-aligned)
enum Severity {
  Critical = "Critical",  // Must be fixed immediately; blocks approval
  High = "High",          // Should be fixed before merge
  Medium = "Medium",      // Should be addressed; maintainability
  Low = "Low",            // Nice to have; minor improvement
  Info = "Info"           // Informational; no action required
}

// Review dimension categories
enum Dimension {
  Correctness = "Correctness",
  Security = "Security",
  Performance = "Performance",
  Maintainability = "Maintainability",
  Testability = "Testability",
  ErrorHandling = "Error Handling",
  Consistency = "Consistency",
  Accessibility = "Accessibility"
}

// Single review finding
interface Finding {
  id: string;                // Unique identifier (e.g., "F-001")
  severity: Severity;
  dimension: Dimension;
  location: {
    file: string;           // Absolute file path
    line_start: number;
    line_end?: number;
  };
  description: string;      // Clear explanation of the issue
  suggestion: string;       // Concrete fix recommendation
  rationale: string;        // Why this matters (ref to spec/pattern)
  source?: string;          // "ai" | "linter" | "sast"
}

// Specification validation result
interface SpecValidation {
  criterion: string;
  status: "met" | "not_met" | "partial" | "not_applicable";
  evidence?: string;        // Code location or explanation
}

// Review verdict
enum Verdict {
  Approved = "Approved",
  ApprovedWithComments = "Approved with Comments",
  ChangesRequested = "Changes Requested",
  Blocked = "Blocked"
}

// Complete review report
interface ReviewReport {
  metadata: {
    feature_name: string;
    date: string;
    reviewer: string;
    status: Verdict;
    base_sha?: string;
    head_sha?: string;
  };
  summary: {
    total_findings: number;
    by_severity: Record<Severity, number>;
    by_dimension: Record<Dimension, number>;
  };
  spec_validation: SpecValidation[];
  findings: Finding[];
  strengths: string[];
  recommendations: string[];
}
```

### 3.4 Review Process Flow

```
Input Context
     |
     v
+--------------------+
| 1. Parse Inputs    |
+--------------------+
     |
     v
+--------------------+
| 2. Read Spec       |
| - Extract criteria |
| - Build checklist  |
+--------------------+
     |
     v
+--------------------+
| 3. Scope Changes   |
| - git diff if SHA  |
| - or file list     |
+--------------------+
     |
     v
+--------------------+
| 4. Run Linters     |
| - Detect tools     |
| - Execute          |
| - Parse output     |
+--------------------+
     |
     +---------------+---------------+
     |               |               |
     v               v               v
+---------+   +---------+   +---------+
| Correct |   | Secure  |   | Perform |  ... (8 dimensions)
+---------+   +---------+   +---------+
     |               |               |
     +---------------+---------------+
                     |
                     v
+--------------------+
| 5. Aggregate       |
| - Deduplicate      |
| - Prioritize       |
+--------------------+
     |
     v
+--------------------+
| 6. Validate Spec   |
| - Check criteria   |
| - Flag deviations  |
+--------------------+
     |
     v
+--------------------+
| 7. Determine       |
|    Verdict         |
+--------------------+
     |
     v
+--------------------+
| 8. Generate Report |
+--------------------+
```

### 3.5 Verdict Determination Logic

```
IF any Critical findings:
    verdict = Blocked
ELSE IF Critical count == 0 AND (High > 3 OR spec criteria not met):
    verdict = Changes Requested
ELSE IF High or Medium findings exist:
    verdict = Approved with Comments
ELSE:
    verdict = Approved
```

Per requirements, **only Critical severity issues block approval**.

### 3.6 Error Handling

| Error Case | Handler | User Feedback |
|------------|---------|---------------|
| Specification not found | Log warning, proceed with generic review | "Warning: Specification not found at [path]. Review will be generic." |
| Linter not installed | Skip linter, continue with AI review | "Info: [linter] not available. Skipping static analysis." |
| Git SHA invalid | Fall back to file list review | "Warning: Could not resolve git diff. Reviewing all specified files." |
| File not readable | Skip file, log warning | "Warning: Could not read [file]. Skipping." |
| Large diff (>5000 lines) | Chunk review into batches | "Info: Large changeset. Reviewing in [N] batches." |

## 4. Implementation Approach

### 4.1 Technology Stack

- **Language:** Markdown agent definition (Claude Code plugin format)
- **Framework:** Claude Code plugin agent system
- **Tools Used:** Read, Grep, Bash (for linter execution)

### 4.2 Agent Definition Structure

Following the established agent patterns from assessment:

```markdown
---
name: code-reviewer
description: Review code for correctness, security, performance, and maintainability.
             Validates implementation against specification. Use after task completion
             in execution-coordinator.
model: sonnet
---

You are a Code Reviewer Agent specialized in specification-aware code review...

## Core Capabilities
1. **Specification Validation**: Verify implementation matches requirements
2. **Multi-Dimensional Review**: Analyze 8 quality dimensions
3. **Tool Integration**: Run project linters before AI analysis
4. **Actionable Feedback**: Every finding has location, suggestion, rationale
5. **Severity Classification**: Critical/High/Medium/Low/Info tiers
6. **Git-Aware Scoping**: Review only changed code via SHA diff

## Input Context
[Input specification]

## Review Process
### Step 1: Parse Context
### Step 2: Read Specification
### Step 3: Scope Changes
### Step 4: Run Static Analysis
### Step 5: Dimension Reviews
### Step 6: Validate Against Spec
### Step 7: Synthesize Report

## Output Format
[Markdown template]

## Quality Standards
[Checklist]

## Integration
[Workflow integration details]
```

### 4.3 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Claude Code | Current | Agent runtime |
| Read tool | Built-in | Read files and specifications |
| Grep tool | Built-in | Search code patterns |
| Bash tool | Built-in | Execute linters |

### 4.4 Configuration

The agent automatically detects project linting configuration:

| Config File | Linter | Command |
|-------------|--------|---------|
| `eslint.config.js`, `.eslintrc*` | ESLint | `npx eslint --format json` |
| `biome.json` | Biome | `npx biome check --reporter json` |
| `pyproject.toml`, `ruff.toml` | Ruff | `ruff check --output-format json` |
| `Cargo.toml` | Clippy | `cargo clippy --message-format json` |
| `go.mod` | golangci-lint | `golangci-lint run --out-format json` |

## 5. Testing Strategy

### 5.1 Unit Tests

| Component | Test Cases |
|-----------|------------|
| Input Parser | Valid inputs, missing specification, missing files, invalid SHA |
| Spec Validator | Parse criteria, extract non-goals, handle malformed spec |
| Static Analysis | Detect each linter, parse output, handle missing tools |
| Dimension Review | Each dimension produces findings, severity classification |
| Report Generator | Aggregation, deduplication, verdict logic |

### 5.2 Integration Tests

- End-to-end review with specification
- Review with linter output integration
- Git SHA-based diff review
- Large changeset handling

### 5.3 Edge Cases

| Edge Case | Expected Behavior | Test |
|-----------|-------------------|------|
| No specification provided | Generic review with warning | Missing spec test |
| Empty diff (no changes) | Report with no findings | Empty diff test |
| All findings are Info level | Verdict = Approved | All info test |
| Single Critical finding | Verdict = Blocked | Critical blocks test |
| Linter times out | Continue with AI-only review | Timeout test |
| Generated code in diff | Skip with note | Generated code test |

## 6. Security Considerations

- **Secret Detection:** Flag any hardcoded credentials, API keys, or secrets in code
- **OWASP Compliance:** Check for OWASP Top 10 vulnerabilities
- **Input Validation:** Verify all user inputs are validated
- **Output Encoding:** Check for proper encoding to prevent XSS
- **Authentication:** Verify auth checks are in place
- **Authorization:** Verify access controls are enforced
- **Cryptography:** Flag weak algorithms or hardcoded keys

## 7. Performance Considerations

- **Incremental Review:** Use Git SHA scoping to review only changed lines
- **Parallel Analysis:** Run linters while preparing AI context
- **Static First:** Eliminate linter-catchable issues before AI reasoning
- **Chunked Review:** For large diffs (>5000 lines), review in batches
- **Caching:** Avoid re-reviewing unchanged sections (future enhancement)

## 8. Rollout Plan

1. **Phase 1:** Create agent definition file with core structure
2. **Phase 2:** Implement all 8 dimension review sections
3. **Phase 3:** Add static analysis integration
4. **Phase 4:** Add specification validation
5. **Phase 5:** Update execution-coordinator.md references
6. **Phase 6:** Update SKILL.md external agents section
7. **Phase 7:** Test with sample implementation task
8. **Phase 8:** Documentation update

## 9. Open Questions

- [ ] Should generated/vendored code paths be configurable or hardcoded?
- [ ] How should review severity align with QA agent defect severity?
- [ ] Should there be a configuration for project-specific review rules?

## 10. References

- Requirements: `/home/jenningsl/development/claude-artifacts/specification/08-code-review-agent/08-requirements.md`
- Research Report: `/home/jenningsl/development/claude-artifacts/specification/08-code-review-agent/08-research-report.md`
- Assessment: `/home/jenningsl/development/claude-artifacts/specification/08-code-review-agent/08-assessment.md`
- CodeAgent Paper: arXiv:2402.02172
- SonarQube Clean Code: https://docs.sonarsource.com/sonarqube-server/
- superpowers:code-reviewer: obra/superpowers GitHub

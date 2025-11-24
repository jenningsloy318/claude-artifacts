# Requirements: Code Review Agent for dev-workflow Plugin

**Date:** 2025-11-24
**Type:** Feature
**Priority:** High

## Executive Summary

The dev-workflow plugin currently depends on an external agent (`superpowers:code-reviewer`) for code review during Phase 8-9 (Execution & Coordination). To make the plugin self-contained and ensure consistent, high-quality code review aligned with the workflow's philosophy, we need to create our own `dev-workflow:code-reviewer` agent. This agent should distill the best practices from leading code review methodologies (CodeAgent multi-agent architecture, SonarQube Clean Code principles, industry checklists) into a systematic, specification-aware review process.

## The Real Need (Root Cause Analysis)

### Surface Request
"Create a code-review agent for the dev-workflow plugin to replace external dependency on `superpowers:code-reviewer`"

### 5 Whys Analysis

1. **Why create our own code-reviewer?**
   - The plugin currently depends on external `superpowers:code-reviewer` which may not be available or may change

2. **Why is external dependency problematic?**
   - External agents may not understand our workflow context, specifications, or project patterns

3. **Why does workflow context matter for code review?**
   - Code review should verify implementation matches the specification, follows patterns from code-assessor, and aligns with research findings

4. **Why is specification-awareness important?**
   - Without specification awareness, reviews become generic style/lint checks that miss functional correctness and design intent

5. **Why focus on design intent?**
   - The real value of code review is ensuring the code solves the right problem correctly, not just formatting compliance

### Root Need
A specification-aware code review agent that validates implementation against requirements, ensures pattern consistency, and provides actionable feedback integrated with the dev-workflow's document chain.

### Job to Be Done

**When** the execution-coordinator completes implementation tasks and needs quality assurance before commit,
**I want to** have an automated code review that validates correctness, security, performance, and maintainability against the specification,
**So I can** confidently merge changes knowing they meet requirements and follow project standards.

**Job Type:**
- **Functional**: Verify code correctness, security, performance, and maintainability
- **Emotional**: Confidence that code meets quality standards before commit
- **Social**: Professional, well-reviewed code that reflects team quality standards

## Workflow Context

### Current State

The dev-workflow plugin references `superpowers:code-reviewer` in multiple places:
- `execution-coordinator.md`: Lists as Testing Agent specialist
- `spec-writer.md`: Task TF.3 references this agent
- `SKILL.md`: External agents section

Current invocation pattern:
```
Task(
  prompt: "Review implementation for: [feature/fix name]",
  context: { specification, implementation_summary },
  subagent_type: "superpowers:code-reviewer"
)
```

### Pain Points
- External dependency may not be available
- No guarantee of specification-awareness
- Cannot customize review criteria for our workflow
- Review output format may not align with our documentation chain
- Missing integration with requirements, research, and assessment documents

### Workflow Map

```
[Phase 1-7: Specification Chain]
         |
         v
[Phase 8-9: Execution]
         |
    Task Completion
         |
         v
+------------------------+
| dev-workflow:          |
| code-reviewer          |  <-- NEW AGENT
+------------------------+
         |
    Review Report
         |
         v
[Phase 9.5: QA Testing]
         |
         v
[Phase 10-11: Cleanup & Commit]
```

### Stakeholders
- **Execution Coordinator**: Invokes code-reviewer for each completed task
- **Developer Agents**: Receive feedback to fix issues
- **QA Agent**: Uses review report as input for testing focus
- **End Users**: Benefit from higher quality code

## Requirements

### Functional Requirements

#### FR-1: Multi-Dimensional Code Review

The agent MUST evaluate code across these dimensions:

| Dimension | Description | Priority |
|-----------|-------------|----------|
| **Correctness** | Does code implement the specification correctly? | P0 |
| **Security** | Are there vulnerabilities (injection, auth, data exposure)? | P0 |
| **Performance** | Are there inefficiencies (N+1 queries, memory leaks)? | P1 |
| **Maintainability** | Is code readable, documented, and follows patterns? | P1 |
| **Testability** | Is code structured for easy testing? | P1 |
| **Error Handling** | Are errors handled gracefully and consistently? | P1 |
| **Consistency** | Does code follow existing project patterns? | P2 |
| **Accessibility** | Are UI components accessible (if applicable)? | P2 |

#### FR-2: Specification-Aware Review

The agent MUST:
1. Read and understand the technical specification document
2. Compare implementation against specification requirements
3. Flag deviations from specified behavior
4. Verify all acceptance criteria are addressed
5. Check that non-goals are not accidentally implemented

#### FR-3: Context-Aware Review

The agent SHOULD:
1. Reference patterns identified in code-assessor output
2. Apply best practices from research-agent findings
3. Verify requirements from requirements-clarifier are met
4. Consider architecture decisions from architecture-agent (if applicable)
5. Check UI implementation matches design-spec (if applicable)

#### FR-4: Actionable Feedback

Each issue MUST include:
1. **Location**: File path and line numbers
2. **Severity**: Critical / High / Medium / Low / Info
3. **Category**: Which dimension (correctness, security, etc.)
4. **Description**: Clear explanation of the issue
5. **Suggestion**: Concrete fix or improvement recommendation
6. **Rationale**: Why this matters (reference to spec/pattern/best practice)

#### FR-5: Review Verdict

The agent MUST provide:
1. **Overall Verdict**: Approved / Approved with Comments / Request Changes / Block
2. **Summary Statistics**: Issues by severity and category
3. **Blocking Issues**: List of critical issues that must be fixed
4. **Recommendations**: Non-blocking suggestions for improvement

#### FR-6: Integration with Execution Coordinator

The agent MUST:
1. Accept context from execution-coordinator (specification, implementation summary)
2. Return structured review report
3. Support re-review after fixes are applied
4. Track review iterations

### Non-Functional Requirements

#### NFR-1: Performance
- Should complete review within reasonable time (proportional to codebase size)
- Should use parallel analysis where possible

#### NFR-2: Consistency
- Same code should receive same review (deterministic when possible)
- Review criteria should be configurable via project settings

#### NFR-3: Extensibility
- Should support language-specific review rules
- Should support project-specific review rules

#### NFR-4: Documentation
- All review rules should be documented
- Rationale for each rule should be available

### Anticipated Downstream Needs

Based on workflow analysis:

1. **Review History Tracking**: Future need to track review iterations and improvement over time
2. **Learning from Rejections**: Future need to learn from rejected suggestions to reduce false positives
3. **Team-Specific Rules**: Future need to support custom review rules per team/project
4. **Integration with CI/CD**: Future need to run as part of automated pipelines
5. **Metrics Dashboard**: Future need to aggregate review metrics for quality insights

## Proposed Solution Options

### Option 1: Minimal Viable (Single-Pass Review)

Simple single-pass review agent with hardcoded review criteria.

**Approach:**
- Single prompt with comprehensive checklist
- Reviews all dimensions in one pass
- Returns structured report

**Pros:**
- Simple to implement
- Fast execution
- Easy to maintain

**Cons:**
- May miss nuanced issues
- No specialization for different dimensions
- Limited depth of analysis

### Option 2: Recommended (Modular Multi-Aspect Review)

Modular architecture with specialized review passes per dimension.

**Approach:**
- Core orchestrator coordinates review passes
- Specialized review modules for each dimension
- Synthesis phase combines findings
- Specification comparison layer

**Pros:**
- Deep analysis per dimension
- Modular and extensible
- Can prioritize dimensions based on context
- Better specification awareness

**Cons:**
- More complex implementation
- Longer execution time
- More to maintain

### Option 3: Comprehensive (Multi-Agent CodeAgent-Style)

Full multi-agent system inspired by CodeAgent paper.

**Approach:**
- Multiple specialized reviewer agents
- Supervisory QA-Checker agent for quality
- Consensus-based issue detection
- Full specification validation pipeline

**Pros:**
- Highest quality review
- Catches subtle issues through consensus
- Most specification-aware
- Academic backing (CodeAgent paper)

**Cons:**
- Most complex to implement
- Highest resource usage
- May be overkill for typical use cases

## Impact Assessment

### Business Outcome
- Self-contained dev-workflow plugin (no external dependencies)
- Consistent, high-quality code review aligned with workflow philosophy
- Specification-aware review catches implementation deviations

### Success Metrics
- **Coverage**: All code review dimensions addressed
- **Accuracy**: Low false positive rate (< 10% of suggestions rejected as irrelevant)
- **Completeness**: All specification requirements verified
- **Actionability**: 100% of issues have clear remediation guidance
- **Efficiency**: Review time proportional to code complexity

### Behavior Change Expected
- Execution coordinator invokes `dev-workflow:code-reviewer` instead of external agent
- Review reports reference specification and workflow documents
- Higher confidence in code quality before QA phase

## Technical Considerations

### Integration Points
- **Input From**: execution-coordinator, specification documents
- **Output To**: execution-coordinator (for fixes), qa-agent (for test focus)
- **Tools Used**: Read tool, Grep tool, language-specific analysis

### Technical Constraints
- Must follow existing agent definition format (markdown with frontmatter)
- Must be invokable via Task tool with `dev-workflow:code-reviewer`
- Must produce structured markdown output for documentation chain

### Reference Implementations
- **CodeAgent** (arXiv:2402.02172): Multi-agent LLM system for code review
- **SonarQube**: Clean Code attributes (consistent, intentional, adaptable, responsible)
- **Industry Checklists**: 8-10 pillar frameworks from leading sources

## Assumptions

1. **Specification Exists**: The code-reviewer will always have access to specification documents
2. **Implementation Summary Available**: Execution coordinator provides summary of changes
3. **Language Support**: Initial focus on languages used in current codebase (TypeScript, Rust, Go, Python)
4. **Single Session**: Review happens within the same conversation context as implementation

## User Decisions (Confirmed)

The following decisions were confirmed during requirements gathering:

| Decision | User Choice | Implication |
|----------|-------------|-------------|
| **Implementation Approach** | Option 2: Modular | Specialized review passes per dimension with core orchestrator |
| **Review Dimensions** | Full Coverage | All 8 dimensions: correctness, security, performance, maintainability, testability, error handling, consistency, accessibility |
| **Tool Integration** | Required Tooling | MUST integrate with project-specific linting and static analysis tools |
| **Blocking Threshold** | Critical Only | Only Critical severity issues block approval; High/Medium/Low are non-blocking |

## Open Questions

- [ ] Should the agent support incremental review (only new changes) vs. full review?
- [ ] How should review severity levels align with existing QA agent defect severity?
- [x] ~~Should there be a configurable severity threshold for blocking issues?~~ **Decided: Critical only blocks**
- [ ] How to handle review of generated/vendored code?
- [x] ~~Should the agent integrate with external linting tools via MCP?~~ **Decided: Required integration**

## Acceptance Criteria

### Core Functionality
- [ ] Agent reviews code for correctness against specification
- [ ] Agent reviews code for security vulnerabilities
- [ ] Agent reviews code for performance issues
- [ ] Agent reviews code for maintainability
- [ ] Agent reviews code for testability
- [ ] Agent reviews code for error handling
- [ ] Agent reviews code for consistency with project patterns

### Specification Awareness
- [ ] Agent reads and references specification document
- [ ] Agent verifies acceptance criteria are met
- [ ] Agent flags deviations from specification
- [ ] Agent references patterns from code-assessor

### Output Quality
- [ ] Each issue includes location, severity, category, description, suggestion, rationale
- [ ] Review verdict provided with summary statistics
- [ ] Blocking issues clearly identified
- [ ] Output format matches workflow documentation chain

### Integration
- [ ] Invokable via `Task(subagent_type: "dev-workflow:code-reviewer")`
- [ ] Accepts specification and implementation_summary context
- [ ] Returns structured review report
- [ ] Works with execution-coordinator workflow

## Recommendations

Based on the analysis and user confirmation, we will implement:

### Confirmed: Option 2 (Modular Multi-Aspect Review)

**Architecture:**
```
+------------------------------------------+
|        Code Reviewer Orchestrator        |
+------------------------------------------+
          |              |              |
          v              v              v
+----------------+ +----------------+ +----------------+
| Specification  | | Static Analysis| | Pattern        |
| Validator      | | Integration    | | Consistency    |
+----------------+ +----------------+ +----------------+
          |              |              |
          v              v              v
+------------------------------------------+
|     Review Dimension Modules             |
|  - Correctness   - Security              |
|  - Performance   - Maintainability       |
|  - Testability   - Error Handling        |
|  - Consistency   - Accessibility         |
+------------------------------------------+
          |
          v
+------------------------------------------+
|        Synthesis & Report Generation     |
+------------------------------------------+
```

**Key Design Decisions:**
1. **Full Coverage**: All 8 dimensions reviewed for comprehensive quality assurance
2. **Required Tooling**: MUST integrate with project linters/SAST (eslint, rustfmt, go vet, etc.)
3. **Critical-Only Blocking**: Only Critical issues block approval; allows iterative improvement

### Implementation Phases

1. **Phase 1: Core Orchestrator**
   - Agent definition with modular review structure
   - Specification parsing and comparison
   - Basic report generation

2. **Phase 2: Dimension Modules**
   - Implement each review dimension as a logical section
   - Language-specific rules per dimension
   - Severity classification

3. **Phase 3: Tool Integration**
   - Detect project linting configuration
   - Run static analysis tools via Bash
   - Incorporate tool output into review

4. **Phase 4: Report Synthesis**
   - Aggregate findings across dimensions
   - Generate structured review report
   - Verdict determination (Critical-only blocking)

## Research References

### Academic Sources
- **CodeAgent**: arXiv:2402.02172 - Multi-agent LLM system for code review
  - Supervisory QA-Checker agent
  - Four review tasks: consistency, security, style, revision suggestions

### Industry Frameworks
- **SonarQube Clean Code**: Consistency, Intentionality, Adaptability, Responsibility
  - Three software qualities: Security, Reliability, Maintainability
  - Severity levels: Critical, High, Medium, Low, Info

### Best Practice Sources
- Graphite AI Code Review Guide: Human-in-the-loop methodology
- SmartBear Research: Code reviews improve quality, knowledge sharing, learning
- DORA Research: Teams with faster code reviews have 50% higher delivery performance

### Review Checklist Pillars (Industry Consensus)
1. Code Functionality and Logic
2. Code Readability and Formatting
3. Security Vulnerabilities
4. Performance and Efficiency
5. Error Handling and Edge Cases
6. Testability and Test Coverage
7. Documentation and Comments
8. Consistency with Project Patterns

---

## Next Steps

**Status: Requirements Confirmed**

The following implementation steps are ready to proceed:

1. [x] ~~Confirm Option 2 (Modular Multi-Aspect Review) as implementation approach~~ **CONFIRMED**
2. [ ] Create agent definition file at `dev-workflow-plugin/agents/code-reviewer.md`
3. [ ] Update execution-coordinator.md to reference new agent (`dev-workflow:code-reviewer`)
4. [ ] Update spec-writer.md task TF.3 to reference new agent
5. [ ] Update SKILL.md external agents section to mark `superpowers:code-reviewer` as replaced
6. [ ] Update README.md to document new agent
7. [ ] Create static analysis tool detection logic
8. [ ] Test integration with execution-coordinator workflow

**Output Location:** `/home/jenningsl/development/claude-artifacts/specification/08-code-review-agent/08-requirements.md`

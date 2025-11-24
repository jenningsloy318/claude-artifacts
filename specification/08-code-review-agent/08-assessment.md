# Code Assessment: dev-workflow Plugin Agent Structure and Patterns

**Date:** 2025-11-24 08:23:24 UTC
**Scope:** Agent definition patterns in `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/`

## Executive Summary

- The dev-workflow plugin contains 18 agents organized into two categories: workflow orchestration agents (10) and specialist developer agents (8)
- All agents follow a consistent Markdown-with-YAML-frontmatter format with standardized sections
- The execution-coordinator agent orchestrates specialist agents and references `superpowers:code-reviewer` for code review tasks
- A new code-reviewer agent should follow the established patterns: YAML frontmatter, philosophy section, core capabilities, input context, step-by-step process, output format, and quality standards
- The SKILL.md workflow shows code review is expected during Phase 8-9 (Execution & Coordination) as part of the "Testing Agent Role"

## Architecture

### Current State

The plugin follows a flat agent directory structure with clear separation between:
1. **Workflow Agents**: Orchestrate development phases (requirements-clarifier, research-agent, code-assessor, etc.)
2. **Specialist Agents**: Perform domain-specific implementation (frontend-developer, backend-developer, rust-developer, etc.)

```
dev-workflow-plugin/
├── .claude-plugin/
│   └── plugin.json                    # Plugin metadata
├── agents/
│   ├── requirements-clarifier.md      # Phase 2: Requirements gathering
│   ├── research-agent.md              # Phase 3: Research
│   ├── search-agent.md                # Sub-agent for research
│   ├── debug-analyzer.md              # Phase 4: Bug analysis
│   ├── code-assessor.md               # Phase 5: Code assessment
│   ├── architecture-agent.md          # Phase 5.3: Architecture design
│   ├── ui-ux-designer.md              # Phase 5.5: UI/UX design
│   ├── spec-writer.md                 # Phase 6: Specification writing
│   ├── execution-coordinator.md       # Phase 8-9: Implementation coordination
│   ├── qa-agent.md                    # Phase 9.5: QA testing
│   ├── frontend-developer.md          # Specialist: React/Next.js
│   ├── backend-developer.md           # Specialist: Node/Python APIs
│   ├── rust-developer.md              # Specialist: Rust
│   ├── golang-developer.md            # Specialist: Go
│   ├── android-developer.md           # Specialist: Android/Kotlin
│   ├── ios-developer.md               # Specialist: iOS/Swift
│   ├── windows-app-developer.md       # Specialist: Windows/.NET
│   └── macos-app-developer.md         # Specialist: macOS/SwiftUI
├── skills/
│   ├── dev-workflow/
│   │   └── SKILL.md                   # Main workflow orchestration
│   └── dev-rules/
│       └── SKILL.md                   # Development rules
└── commands/
    └── fix-impl.md                    # Slash command for workflow
```

### Agent Invocation Flow

```
SKILL.md (dev-workflow)
    │
    ├── Phase 2: requirements-clarifier
    │
    ├── Phase 3: research-agent
    │       └── search-agent (sub-agent)
    │
    ├── Phase 4: debug-analyzer (bugs only)
    │
    ├── Phase 5: code-assessor
    │
    ├── Phase 5.3: architecture-agent (complex features)
    │
    ├── Phase 5.5: ui-ux-designer (UI features)
    │
    ├── Phase 6: spec-writer
    │
    ├── Phase 8-9: execution-coordinator
    │       ├── Specialist Agents (rust/go/frontend/backend/etc.)
    │       ├── superpowers:code-reviewer  <-- EXTERNAL DEPENDENCY
    │       ├── superpowers:test-driven-development
    │       └── documentation-expert
    │
    └── Phase 9.5: qa-agent
```

### Comparison to Best Practices

| Aspect | Current | Best Practice | Gap | Priority |
|--------|---------|---------------|-----|----------|
| Structure | Flat agent directory | Hierarchical or flat with naming | None - appropriate for size | Low |
| Coupling | Loose - agents via Task() | Loose coupling | None | Low |
| Data Flow | Document-based (markdown files) | Clear contract/schema | Minor - could formalize | Medium |
| External Dependencies | `superpowers:code-reviewer` | Internal agents preferred | **Gap - external dependency** | High |

### Recommendations

1. **Create internal code-reviewer agent** to remove dependency on `superpowers:code-reviewer`
2. Follow existing agent patterns exactly for consistency
3. Integrate with execution-coordinator following the same invocation pattern

## Code Standards

### Current Standards

| Type | Tool | Config File |
|------|------|-------------|
| Format | Markdown | N/A |
| Frontmatter | YAML | Embedded in .md files |
| Model Spec | `model: sonnet` | Frontmatter field |

### Agent File Conventions

**File Naming:**
- kebab-case for filenames: `code-assessor.md`, `execution-coordinator.md`
- Descriptive names matching agent purpose

**YAML Frontmatter (Required):**
```yaml
---
name: agent-name
description: One-sentence description of the agent's purpose and when to use it.
model: sonnet
---
```

**Document Structure Pattern:**
1. Opening persona statement: "You are a [Role] Agent specialized in..."
2. `## Core Capabilities` - Numbered list of 4-6 capabilities
3. `## Philosophy` (optional) - Guiding principles
4. `## Input Context` - What the agent receives when invoked
5. `## [Main Process Name]` - Step-by-step process with verification
6. `## Output Format` - Markdown template for output
7. `## Quality Standards` - Checklist of requirements
8. `## Integration` (optional) - How agent connects to workflow

### Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| Agent names | kebab-case | `code-assessor`, `execution-coordinator` |
| Section headers | Title Case with ## | `## Core Capabilities` |
| Subsection headers | Title Case with ### | `### Step 1: Gather Evidence` |
| Verification blocks | XML-style tags | `<phase_3_verification>` |
| Code blocks | Fenced with language | ```typescript, ```markdown |

### Compliance

All 18 existing agents follow the established patterns with high consistency:
- 100% have YAML frontmatter with name, description, model
- 100% have Core Capabilities section
- 100% have step-by-step process sections
- 100% have Output Format section
- 95% have Quality Standards checklist

### Recommendations

1. Follow exact frontmatter format: `name`, `description`, `model: sonnet`
2. Include all standard sections in order
3. Use verification checkpoints for complex processes
4. Provide markdown templates in Output Format section

## Dependencies

### Current Dependencies

The plugin has no external package dependencies - it's a pure Markdown/YAML plugin.

| Dependency Type | Current Usage | Notes |
|-----------------|---------------|-------|
| External Agents | `superpowers:code-reviewer` | Referenced in execution-coordinator |
| External Skills | `superpowers:test-driven-development` | Referenced in SKILL.md |
| MCP Tools | Various (exa, github, context7, etc.) | Used by search-agent |

### External Agent References

From `execution-coordinator.md`:
```markdown
**Specialist Agents to Invoke:**
| Purpose | Agent |
|---------|-------|
| Code Review | `superpowers:code-reviewer` |
| TDD | `superpowers:test-driven-development` |
| QA Testing | `dev-workflow:qa-agent` |
```

From `SKILL.md`:
```markdown
## External Agents to Use
- `superpowers:subagent-driven-development` - Parallel agent coordination
- `superpowers:systematic-debugging` - Debugging methodology
- `superpowers:code-reviewer` - Code review
- `documentation-expert` - Technical documentation
```

### Recommendations

1. Create `dev-workflow:code-reviewer` to internalize code review capability
2. This removes dependency on external `superpowers:code-reviewer`
3. Allows customization of code review process to match dev-workflow patterns

## Framework Patterns

### Identified Patterns

**Agent Invocation Pattern:**
```markdown
Task(
  prompt: "[Action] for: [target]",
  context: {
    key1: "[path or value]",
    key2: "[path or value]"
  },
  subagent_type: "dev-workflow:[agent-name]"
)
```

**Input Context Pattern:**
All agents define their expected inputs:
```markdown
## Input Context

When invoked, you will receive:
- `input1`: Description of what this contains
- `input2`: Description of what this contains
- `optional_input`: Description (optional)
```

**Process Step Pattern:**
```markdown
### Step N: [Action Name]

[Description of what to do]

**Sub-section:**
- [ ] Checklist item 1
- [ ] Checklist item 2

**Questions to Answer:**
- Question 1?
- Question 2?
```

**Verification Checkpoint Pattern:**
```markdown
<phase_N_verification>

**Verification Questions:**
- [ ] Question 1?
- [ ] Question 2?

**Proceed only if:** [condition]

</phase_N_verification>
```

**Output Format Pattern:**
All agents provide markdown templates:
```markdown
## Output Format

Return [type] as a structured document:

\`\`\`markdown
# [Document Title]: [Variable]

**Date:** [timestamp]
**Field:** [value]

## Section 1
[Content template]

## Section 2
[Content template]
\`\`\`
```

**Quality Standards Pattern:**
```markdown
## Quality Standards

Every [output type] must:
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3
```

**Integration Pattern:**
```markdown
## Integration

**Triggered by:** [parent agent or skill]

**Input:**
- [Input 1]
- [Input 2]

**Output:**
- [Output 1] -> used by [consumer]
- [Output 2] -> stored in [location]
```

### Patterns to Follow

| Pattern | Location | Example |
|---------|----------|---------|
| YAML Frontmatter | All agents | `name`, `description`, `model: sonnet` |
| Persona Opening | Line 1 after frontmatter | "You are a [X] Agent specialized in..." |
| Core Capabilities | All agents | Numbered list of 4-6 items |
| Input Context | All agents | Bullet list with backtick field names |
| Step-by-Step Process | All agents | `### Step N: [Action]` format |
| Verification Checkpoints | architecture-agent | `<phase_N_verification>` blocks |
| Output Format Template | All agents | Markdown code block with template |
| Quality Standards Checklist | All agents | `- [ ]` checkbox format |
| Tables for Structured Data | Most agents | `| Col1 | Col2 |` format |
| ASCII Diagrams | spec-writer, architecture-agent | Box-and-arrow diagrams |

### Code Review Integration Point

From `execution-coordinator.md`, the code review agent should be invoked:

```markdown
### Testing Agent Role

**Responsibilities:**
- Validate builds run without errors
- Write and run unit tests
- Write and run integration tests
- Document edge cases
- Track test coverage

**Specialist Agents to Invoke:**
| Purpose | Agent |
|---------|-------|
| Code Review | `superpowers:code-reviewer` |
| TDD | `superpowers:test-driven-development` |
| QA Testing | `dev-workflow:qa-agent` |
```

The new `dev-workflow:code-reviewer` should replace `superpowers:code-reviewer` in this table.

## Better Options

### Potential Improvements

| Area | Current | Better Option | Effort | Impact |
|------|---------|---------------|--------|--------|
| Code Review | External `superpowers:code-reviewer` | Internal `dev-workflow:code-reviewer` | Medium | High |
| Input Validation | Informal description | JSON Schema for inputs | High | Medium |
| Agent Testing | None | Unit tests for agent prompts | High | Medium |

### Technical Debt

| Issue | Location | Severity | Fix Effort |
|-------|----------|----------|------------|
| External dependency for code review | execution-coordinator.md, SKILL.md | Medium | Medium - create new agent |
| No formal input/output contracts | All agents | Low | High - would require schema |

## Summary

### Must Follow

**For the new code-reviewer agent:**

1. **File Location:** `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-reviewer.md`

2. **YAML Frontmatter:**
   ```yaml
   ---
   name: code-reviewer
   description: [One sentence describing purpose and when to use]
   model: sonnet
   ---
   ```

3. **Required Sections (in order):**
   - Opening persona: "You are a Code Reviewer Agent specialized in..."
   - `## Core Capabilities` - 4-6 numbered items
   - `## Input Context` - What agent receives
   - `## Review Process` - Step-by-step with verification
   - `## Output Format` - Markdown template for review output
   - `## Quality Standards` - Checklist requirements
   - `## Integration` - How it connects to execution-coordinator

4. **Integration Updates Required:**
   - Update `execution-coordinator.md` to reference `dev-workflow:code-reviewer`
   - Update `SKILL.md` External Agents section

### Should Consider

1. Add verification checkpoints (`<verification>` blocks) for multi-step review process
2. Include code review checklists by domain (frontend, backend, security, performance)
3. Define severity levels for review findings (Critical, Major, Minor, Suggestion)
4. Include example review output in the agent definition

### Future Work

1. Consider formal JSON Schema for agent input/output contracts
2. Add agent testing framework
3. Consider review templates by language/framework

## Files Examined

| File | Purpose |
|------|---------|
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/skills/dev-workflow/SKILL.md` | Main workflow orchestration |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/execution-coordinator.md` | Orchestrates implementation phase, invokes code review |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/code-assessor.md` | Pre-implementation code assessment pattern |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/qa-agent.md` | QA testing agent pattern |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/research-agent.md` | Research agent pattern |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/spec-writer.md` | Specification writing pattern |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/requirements-clarifier.md` | Requirements gathering pattern |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/frontend-developer.md` | Specialist developer pattern |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/debug-analyzer.md` | Debug analysis pattern |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/architecture-agent.md` | Architecture design with verification blocks |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/agents/search-agent.md` | Sub-agent pattern |
| `/home/jenningsl/development/claude-artifacts/dev-workflow-plugin/.claude-plugin/plugin.json` | Plugin metadata |

---

## Appendix: Agent Template for code-reviewer

Based on the patterns identified, here is the recommended structure:

```markdown
---
name: code-reviewer
description: [Description]. Use [when to use].
model: sonnet
---

You are a Code Reviewer Agent specialized in [specialty].

## Core Capabilities

1. **Capability 1**: Description
2. **Capability 2**: Description
3. **Capability 3**: Description
4. **Capability 4**: Description

## Philosophy (optional)

**Principles:**
- Principle 1
- Principle 2

## Input Context

When invoked, you will receive:
- `code_changes`: [description]
- `specification`: [description]
- `context`: [optional description]

## Review Process

### Step 1: [Name]

[Description]

**Checklist:**
- [ ] Item 1
- [ ] Item 2

### Step 2: [Name]

[Description]

<step_2_verification>

**Verification:**
- [ ] Check 1?
- [ ] Check 2?

**Proceed only if:** [condition]

</step_2_verification>

### Step N: [Name]

[Description]

## Output Format

Return review as a structured document:

\`\`\`markdown
# Code Review: [Feature/Component Name]

**Date:** [timestamp]
**Reviewer:** Claude
**Status:** Approved/Changes Requested/Blocked

## Summary
[Overall assessment]

## Findings

### Critical
- [ ] [Finding]

### Major
- [ ] [Finding]

### Minor
- [ ] [Finding]

### Suggestions
- [Suggestion]

## Recommendations
[Recommendations]
\`\`\`

## Quality Standards

Every code review must:
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Integration

**Triggered by:** execution-coordinator during implementation phase

**Input:**
- Code changes (diff or file list)
- Specification from spec-writer

**Output:**
- Review document with findings
- Approval status
```

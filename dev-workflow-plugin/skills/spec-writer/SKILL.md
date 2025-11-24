---
name: spec-writer
description: Write technical specifications, implementation plans, and task lists. Use in Phase 6 of dev-workflow to create comprehensive documentation before implementation.
---

# Specification Writer

Create comprehensive technical documentation for implementation.

**Announce:** "I'm using the spec-writer skill to create specifications and plans."

## Documents to Create

This skill produces three documents:
1. Technical Specification
2. Implementation Plan
3. Task List

## Document 1: Technical Specification

### Purpose
Capture all technical decisions and architecture for the implementation.

### Content

```markdown
# Technical Specification: [Feature/Fix Name]

**Date:** [timestamp]
**Author:** Claude
**Status:** Draft/Review/Approved

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
[Reference research report findings]

### 2.2 Current State
[Reference assessment findings]

### 2.3 Problem Statement
[Reference debug analysis if applicable]

## 3. Technical Design

### 3.1 Architecture
[High-level architecture diagram in ASCII]

```
┌─────────────┐     ┌─────────────┐
│ Component A │────▶│ Component B │
└─────────────┘     └─────────────┘
```

### 3.2 Components

#### Component 1
- Purpose: [description]
- Responsibilities: [list]
- Interfaces: [API definitions]

### 3.3 Data Model
[Data structures, schemas, database changes]

### 3.4 API Design
[Endpoints, request/response formats]

### 3.5 Error Handling
[Error cases and how they're handled]

## 4. Implementation Approach

### 4.1 Technology Stack
[Languages, frameworks, libraries]

### 4.2 Dependencies
[New dependencies needed]

### 4.3 Configuration
[Config changes needed]

## 5. Testing Strategy

### 5.1 Unit Tests
[What will be unit tested]

### 5.2 Integration Tests
[Integration test approach]

### 5.3 Edge Cases
[Known edge cases to test]

## 6. Security Considerations
[Security implications and mitigations]

## 7. Performance Considerations
[Performance implications and optimizations]

## 8. Rollout Plan
[How this will be deployed]

## 9. Open Questions
[Unresolved questions]

## 10. References
- Research Report: [link]
- Assessment: [link]
- Debug Analysis: [link if applicable]
```

## Document 2: Implementation Plan

### Purpose
Break down the specification into implementable milestones.

### Content

```markdown
# Implementation Plan: [Feature/Fix Name]

**Specification:** [link to spec]
**Estimated Effort:** [rough estimate]

## Milestones

### Milestone 1: [Name]
**Goal:** [What this milestone achieves]
**Dependencies:** [Prerequisites]

#### Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

#### Acceptance Criteria
- [Criterion 1]
- [Criterion 2]

### Milestone 2: [Name]
...

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk] | High/Med/Low | High/Med/Low | [Mitigation] |

## Dependencies
[External dependencies and blockers]
```

## Document 3: Task List

### Purpose
Granular tasks for execution phase.

### Content

```markdown
# Task List: [Feature/Fix Name]

**Plan:** [link to implementation plan]

## Tasks

### Milestone 1: [Name]

- [ ] **T1.1** [Task description]
  - Files: `path/to/file.ts`
  - Details: [specifics]

- [ ] **T1.2** [Task description]
  - Files: `path/to/file.ts`
  - Details: [specifics]

### Milestone 2: [Name]

- [ ] **T2.1** [Task description]
...

### Final Tasks

- [ ] **TF.1** Run all tests and fix failures
- [ ] **TF.2** Update documentation
- [ ] **TF.3** Code review
- [ ] **TF.4** Commit and push changes
```

## Specialist Agents

Use these agents for domain expertise:

| Domain | Agent |
|--------|-------|
| Backend | `backend-developer` |
| Frontend | `frontend-developer` |
| Database | Database specialist |
| Cloud | `cloud-architect` |
| API Design | API specialist |

## Quality Checklist

Before completing:
- [ ] Spec references all previous phase documents
- [ ] API specifications are aligned with existing APIs
- [ ] Plan has clear milestones
- [ ] Tasks are specific and actionable
- [ ] Final commit task is included

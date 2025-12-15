---
name: super-dev:architecture-design
description: Design architecture and create Architecture Decision Records (ADRs) for complex features
---

# Phase 5.3: Architecture Design

Design comprehensive architecture and create Architecture Decision Records (ADRs) for complex features.

## Usage

```
/super-dev:architecture-design [feature requirements and context]
```

## What This Command Does

When invoked, this command activates the `super-dev:architecture-agent` to:

1. **Analyzes requirements**: Reviews feature requirements and constraints
2. **Designs architecture**: Creates detailed architectural design
3. **Creates ADRs**: Documents key architectural decisions
4. **Defines interfaces**: Specifies component boundaries and contracts
5. **Plans integration**: Maps how new architecture fits with existing
6. **Creates architecture spec**: Generates `[phase-index]-architecture.md`

## Architecture Design Process

### Option Generation and Evaluation (mandatory)
- For every significant architectural decision, propose at least 3 viable options
- Evaluate options across multiple dimensions:
  - Technical: modularity, coupling/cohesion, scalability, performance, security
  - Delivery: implementation complexity, risk, time-to-value, maintainability, testability
  - Operational: observability, reliability, cost, supportability, reversibility
- Use a normalized scoring rubric (0–5 per criterion) and weighted totals
- Provide a comparative summary and a final recommendation with explicit trade-offs

### Reuse and Glue Code Enforcement
- No Wheel Reinvention: Prefer reusing mature open-source components over custom builds; identify candidates and justify selections
- Glue Code: Use minimal AI-generated adapters/integration layers to connect reused components to existing systems; outline responsibilities and tests

### Interface-First Modularity
- Define contracts (interfaces/ports, data models, events) before implementations
- Ensure components are replaceable and composable; document boundaries and stability guidelines

### Requirements Analysis
- Review functional and non-functional requirements
- Identify performance, scalability, and security needs
- Map integration requirements
- Note technical constraints

### System Design
- Define component architecture
- Design data flows
- Specify interfaces and contracts
- Plan deployment architecture

### Architecture Decision Records (ADRs)
- Document significant decisions
- Record alternatives considered (≥3 options with pros/cons)
- Note consequences and trade-offs
- Include an evaluation matrix:
  - Criteria across technical/delivery/operational with weights (sum = 1.0)
  - Scores per option (0–5) and weighted totals
- Add a reversibility plan (triggers, rollback approach, cost/time estimate)

### Integration Planning
- Map to existing architecture
- Define migration strategy
- Plan backward compatibility
- Identify impact areas

## When to Use This Phase

- Complex features requiring architectural decisions
- New modules or major components
- Cross-cutting concerns (authentication, logging, etc.)
- Performance-critical features
- Systems requiring specific non-functional requirements

## Arguments

`$ARGUMENTS` should include:
- Feature requirements
- Performance or scalability needs
- Integration constraints
- Existing system context

## Output

Creates:
- `[phase-index]-architecture.md` - Main architecture document
- ADRs in `adrs/` subdirectory
- Component diagrams and interface specifications
- Integration strategy document

## Examples

```
/super-dev:phase-5.3 Microservices for user management
/super-dev:phase-5.3 Real-time notification system
/super-dev:phase-5.3 Event-driven order processing
```

## Notes

- Optional phase - skip for simple features
- Creates living documentation for architecture
- Enables future architecture decisions
- Provides implementation guidance

## Validation Gates (must-pass)
- Reuse Gate: OSS components documented (justification, licenses, and mapping to architecture). If not reusing, provide approved exceptions
- Glue Code Gate: Adapters/integration layers listed with responsibilities and unit/integration tests
- Interface-first Gate: Finalized interface contracts (types/methods/events), boundary diagrams, and stability guidelines before implementation details
---
name: super-dev:architecture-design
description: Design architecture and create Architecture Decision Records (ADRs) for complex features
---

# Phase 5.3: Architecture Design

Design comprehensive architecture and create Architecture Decision Records (ADRs) for complex features.

## Usage

```
/super-dev:phase-5.3 [feature requirements and context]
```

## What This Command Does

When invoked, this command activates the `super-dev:architecture-agent` to:

1. **Analyzes requirements**: Reviews feature requirements and constraints
2. **Designs architecture**: Creates detailed architectural design
3. **Creates ADRs**: Documents key architectural decisions
4. **Defines interfaces**: Specifies component boundaries and contracts
5. **Plans integration**: Maps how new architecture fits with existing
6. **Creates architecture spec**: Generates `[index]-architecture.md`

## Architecture Design Process

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
- Record alternatives considered
- Note consequences and trade-offs
- Create decision matrix

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
- `[index]-architecture.md` - Main architecture document
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
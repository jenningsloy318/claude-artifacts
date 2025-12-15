---
name: super-dev:ui-ux-design
description: Create UI/UX design specifications for features with user interfaces
---

# Phase 5.5: UI/UX Design

Create comprehensive UI/UX design specifications for features requiring user interfaces.

## Usage

```
/super-dev:ui-ux-design [UI requirements and user context]
```

## What This Command Does

When invoked, this command activates the `super-dev:ui-ux-designer` to:

1. **Analyzes user needs**: Understands user context and requirements
2. **Creates wireframes**: Designs interface layouts and structure
3. **Defines interactions**: Specifies user flows and interactions
4. **Establishes design tokens**: Creates consistent design system
5. **Plans responsive design**: Ensures cross-device compatibility
6. **Creates design spec**: Generates `[phase-index]-design-spec.md`

## Design Process

### User Analysis
- Identify user personas and use cases
- Map user journeys and flows
- Define user goals and pain points
- Analyze accessibility needs

### Interface Design
- Create wireframes and mockups
- Design component hierarchy
- Plan information architecture
- Define navigation patterns

### Interaction Design
- Map user flows
- Design interaction patterns
- Define micro-interactions
- Plan state transitions

### Design System
- Define color palette and typography
- Create component library
- Establish spacing and sizing tokens
- Document design guidelines

### Responsive Design
- Plan mobile-first approach
- Define breakpoints
- Design adaptive layouts
- Ensure touch-friendly interfaces

### Option Generation and Evaluation

Definitions (concise):
- No Wheel Reinvention: Prefer reusing mature open-source UI components and design systems over building custom solutions.
- Glue Code: Minimal integration adapters/layers that connect reused UI components to the existing framework and data flows.
- Interface-first Modularity: Define component/module contracts (interfaces, events) before implementations; ensure components are replaceable and composable.

Enforcement principles:
- No Wheel Reinvention: Maximize reuse of mature open-source UI components and design systems; avoid rebuilding from scratch.
- Glue Code: Use AI to generate minimal "glue code" to integrate reused components into the existing framework and data flows.
- Modularity: Interface-first (contract-first); define component/module interfaces and events before implementation. Components should be replaceable and composable.

For any significant UI/UX decision, propose at least 3 viable options and evaluate them across multiple dimensions. Provide a comparative summary, a final recommendation with rationale, and a documented reversibility plan.

Default criteria weights (total equals 1.0; adjust as needed):
- Delivery (0.30)
  - Implementation Feasibility: 0.05
  - Complexity: 0.08
  - Risk: 0.07
  - Time-to-Value: 0.07
  - Maintainability: 0.05
  - Testability: 0.03
- Technical/UI System (0.45)
  - Accessibility: 0.10
  - Performance: 0.08
  - Design System Alignment: 0.07
  - Scalability of UI Patterns: 0.05
  - Consistency: 0.05
  - Observability (telemetry from UI): 0.03
  - Reliability (error-state handling): 0.03
  - Supportability (docs/training): 0.02
  - Reversibility: 0.02
- Experiential (0.25)
  - Usability: 0.10
  - Learnability: 0.05
  - Discoverability: 0.05
  - Aesthetic Fit: 0.05

Normalized scoring rubric:
- Score each criterion 0–5 (0 = unacceptable, 3 = acceptable baseline, 5 = excellent)
- Weighted total option score = sum(score_i × weight_i)
- Prefer higher total scores; if selecting a lower-scoring option, explicitly document the trade-offs and optimization goal

Evaluation matrix template:
| Criteria | Weight | Option 1 | Option 2 | Option 3 |
|----------|--------|----------|----------|----------|
| Accessibility | 0.10 | [0–5] | [0–5] | [0–5] |
| Performance | 0.08 | [0–5] | [0–5] | [0–5] |
| Design System Alignment | 0.07 | [0–5] | [0–5] | [0–5] |
| Implementation Feasibility | 0.05 | [0–5] | [0–5] | [0–5] |
| Scalability of UI Patterns | 0.05 | [0–5] | [0–5] | [0–5] |
| Consistency | 0.05 | [0–5] | [0–5] | [0–5] |
| Complexity | 0.08 | [0–5] | [0–5] | [0–5] |
| Risk | 0.07 | [0–5] | [0–5] | [0–5] |
| Time-to-Value | 0.07 | [0–5] | [0–5] | [0–5] |
| Maintainability | 0.05 | [0–5] | [0–5] | [0–5] |
| Testability | 0.03 | [0–5] | [0–5] | [0–5] |
| Usability | 0.10 | [0–5] | [0–5] | [0–5] |
| Learnability | 0.05 | [0–5] | [0–5] | [0–5] |
| Discoverability | 0.05 | [0–5] | [0–5] | [0–5] |
| Aesthetic Fit | 0.05 | [0–5] | [0–5] | [0–5] |
| Observability | 0.03 | [0–5] | [0–5] | [0–5] |
| Reliability | 0.03 | [0–5] | [0–5] | [0–5] |
| Supportability | 0.02 | [0–5] | [0–5] | [0–5] |
| Reversibility | 0.02 | [0–5] | [0–5] | [0–5] |

Scoring helper (conceptual):
- Total(option) = sum over all criteria of score × weight
- Rank options by total descending
- Document the final recommendation and the reversibility plan (triggers, rollback approach, cost/time estimate)

Validation gates (must be satisfied before completion):
- Reuse Gate: Document selected open-source UI components/design system parts, justification, licenses, and how they map to the UI specification. If not reusing, provide documented, approved exceptions.
- Glue Code Gate: Provide the list of adapters/integration layers, their responsibilities, and how they are tested (unit + integration).
- Interface-first Gate: Include finalized component contracts (props, events, states), interaction flows, and stability guidelines before implementation details.

## When to Use This Phase

- Features with user interfaces
- Major UI changes or redesigns
- New user workflows
- Components requiring specific UX considerations
- Accessibility improvements

## Arguments

`$ARGUMENTS` should include:
- UI requirements and constraints
- Target users and use cases
- Brand or design guidelines
- Platform considerations (web, mobile, desktop)

## Output

Creates `[index]-design-spec.md` with:
- User personas and journeys
- Wireframes and layouts
- Component specifications
- Interaction designs
- Design tokens and guidelines
- Responsive design plans
- ≥3 UI/UX options and comparative evaluation
- Final recommendation with rationale and reversibility plan
- Reuse plan: selected open-source components, rationale, and integration approach
- Interface-first specification: component contracts, events, and adapter/glue code plan

## Examples

```
/super-dev:ui-ux-design User dashboard with analytics charts
/super-dev:ui-ux-design Mobile checkout flow
/super-dev:ui-ux-design Settings page redesign
```

## Notes

- Optional phase - skip for backend-only features
- Follows existing design system when available
- Ensures accessibility compliance
- Creates implementation-ready specifications
- Requires ≥3 options with multi-dimensional evaluation and a documented reversibility plan
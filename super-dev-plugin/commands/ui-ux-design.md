---
name: super-dev:ui-ux-design
description: Create UI/UX design specifications for features with user interfaces
---

# Phase 5.5: UI/UX Design

Create comprehensive UI/UX design specifications for features requiring user interfaces.

## Usage

```
/super-dev:phase-5.5 [UI requirements and user context]
```

## What This Command Does

When invoked, this command activates the `super-dev:ui-ux-designer` to:

1. **Analyzes user needs**: Understands user context and requirements
2. **Creates wireframes**: Designs interface layouts and structure
3. **Defines interactions**: Specifies user flows and interactions
4. **Establishes design tokens**: Creates consistent design system
5. **Plans responsive design**: Ensures cross-device compatibility
6. **Creates design spec**: Generates `[index]-design-spec.md`

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

## Examples

```
/super-dev:phase-5.5 User dashboard with analytics charts
/super-dev:phase-5.5 Mobile checkout flow
/super-dev:phase-5.5 Settings page redesign
```

## Notes

- Optional phase - skip for backend-only features
- Follows existing design system when available
- Ensures accessibility compliance
- Creates implementation-ready specifications
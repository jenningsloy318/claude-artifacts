---
name: ui-ux-patterns
description: UI/UX design patterns, principles, and best practices for user interface design. Reference for Phase 5.5 (UI/UX Design) in super-dev workflow.
---

# UI/UX Patterns Reference

Reference documentation for user interface and experience design. Use this during Phase 5.5 (UI/UX Design) of the super-dev workflow.

## Core Principles

### YAGNI (You Aren't Gonna Need It)
- Design only screens/components explicitly required
- No speculative UI variants
- Each UI element must serve documented requirements

### Boring Patterns First
- Prefer familiar, proven UI patterns over novel interactions
- Users shouldn't need training for standard actions
- Standard components reduce cognitive load

### Simple > Clever
- If standard components work, don't create custom
- If flat information architecture works, don't add hierarchy
- Working design first → pixel-perfect later

### Key Definitions
- **No Wheel Reinvention**: Prefer reusing mature open-source UI components and design systems
- **Glue Code**: Minimal integration adapters that connect reused UI components to existing frameworks
- **Interface-first Modularity**: Define component contracts (props, events, states) before implementations

## UX Research: Foundational Questions

### Who is this for and why?
- **Primary user persona characteristics**
- **User goals and success criteria**
- **Pain points being solved**
- **Context of use** (environment, device, urgency)

### What is the core user journey?
- **Entry points** (how users discover/access)
- **Critical path** (minimum steps to goal)
- **Decision points and branches**
- **Exit points and next actions**

### What are usability priorities?
- **Learnability**: How quickly can new users understand?
- **Efficiency**: How fast can experts complete tasks?
- **Error prevention**: What could go wrong?
- **Satisfaction**: What creates delight vs frustration?

### What are design constraints?
- **Accessibility** (screen readers, keyboard, contrast)
- **Performance** (load time, interaction latency)
- **Content** (text length, image sizes)
- **Technical** (browser support, API limitations)

## Layout Patterns

### Common Layout Patterns

#### Card Layout
```
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Image  │ │  Image  │ │  Image  │
│  Title  │ │  Title  │ │  Title  │
│  Action │ │  Action │ │  Action │
└─────────┘ └─────────┘ └─────────┘
```
**Best for:** Product listings, dashboards, content grids
**Pros:** Scalable, flexible, responsive-friendly

#### List Layout
```
┌────────────────────────────────┐
│ • Item 1        [Action]       │
│ • Item 2        [Action]       │
│ • Item 3        [Action]       │
└────────────────────────────────┘
```
**Best for:** Data tables, settings, navigation
**Pros:** High information density, scan-friendly

#### Split View (Master-Detail)
```
┌─────────────┬──────────────────┐
│ Item 1      │ Detail View      │
│ Item 2      │ for selected     │
│ Item 3      │ item             │
└─────────────┴──────────────────┘
```
**Best for:** Email, file browsers, dashboards
**Pros:** Maintains context, supports exploration

#### Dashboard Layout
```
┌────────────────────────────────┐
│ Header + Search + Actions      │
├──────┬───────────┬─────────────┤
│Filter│ Chart     │ KPI Cards    │
│      │           │             │
│      │ List      │ Activity     │
└──────┴───────────┴─────────────┘
```
**Best for:** Analytics, admin panels, monitoring

## Navigation Patterns

### Top Navigation (Tabs)
```
Home | Products | About | Contact
```
**Best for:** 3-5 sections, equal importance
**Pros:** Visible, scan-friendly, mobile-friendly

### Sidebar Navigation
```
┌──────────┐
│ Home     │
│ Products │
│ About    │
│ Contact  │
└──────────┘
```
**Best for:** 5+ sections, hierarchical content
**Pros:** Scalable, supports sub-navigation

### Breadcrumbs
```
Home > Products > Category > Item
```
**Best for:** Deep hierarchies, e-commerce
**Pros:** Shows location, supports back navigation

### Mega Menu
```
┌────────────────────────────────────┐
│ Products ▼                          │
│ ┌─────┬─────┬─────┬─────┐          │
│ │Cat 1│Cat 2│Cat 3│Cat 4│          │
│ └─────┴─────┴─────┴─────┘          │
└────────────────────────────────────┘
```
**Best for:** Large sites with many categories
**Pros:** Preview content, reduces clicks

## Component Patterns

### Buttons
```typescript
// Button states and variants
<Button variant="primary" size="md" disabled={false}>
  Click Me
</Button>

// Variants: primary, secondary, ghost, danger
// Sizes: sm, md, lg
// States: default, hover, active, disabled, loading
```

### Form Patterns

#### Single Column Form
```
┌─────────────────────────┐
│ Label                   │
│ [Input            ]    │
│ Helper text             │
│                        │
│ Label                   │
│ [Input            ]    │
│                        │
│        [Submit Button]  │
└─────────────────────────┘
```
**Best for:** Simple forms, mobile-first

#### Two Column Form
```
┌──────────────┬──────────────┐
│ Label        │ Label        │
│ [Input    ]  │ [Input    ]  │
├──────────────┴──────────────┤
│ Label                        │
│ [Input                     ]│
│                              │
│        [Submit Button]       │
└──────────────────────────────┘
```
**Best for:** Desktop, related field grouping

#### Wizard/Stepped Form
```
Step 1 → Step 2 → Step 3 → Complete
┌─────────────────────────────┐
│ Current step content         │
│                             │
│ [Back]        [Next →]       │
└─────────────────────────────┘
```
**Best for:** Complex forms, multi-step processes

### Data Display Patterns

#### Table
```
┌──────┬─────────┬─────────┐
│ Name │ Status  │ Actions │
├──────┼─────────┼─────────┤
│ Item1│ Active  │ [Edit]  │
│ Item2│ Pending │ [Edit]  │
└──────┴─────────┴─────────┘
```
**Best for:** Comparable data, sortable/filterable

#### List Group
```
┌────────────────────────────┐
│ Title          [Meta]      │
│ Description text           │
├────────────────────────────┤
│ Title          [Meta]      │
│ Description text           │
└────────────────────────────┘
```
**Best for:** Items with rich previews, actions

## Interaction Patterns

### Modals (Dialogs)
```
┌────────────────────────────────┐
│           Title          [X]   │
├────────────────────────────────┤
│                                │
│  Content                       │
│                                │
├────────────────────────────────┤
│           [Cancel] [Confirm]   │
└────────────────────────────────┘
```
**Use for:** Critical confirmations, focused input
**Avoid for:** Non-critical info, large content

### Inline Expansion
```
▶ Item Header  (click to expand)
  ▸ Expanded content here
```
**Use for:** Progressive disclosure, FAQs
**Pros:** Maintains context, reduces cognitive load

### Side Panel (Drawer)
```
Main Content  ┌──────────┐
               │ Panel    │
               │ content  │
               │          │
               └──────────┘
```
**Use for:** Edit forms, details, filters
**Pros:** Context preserved, larger space

### Toast Notifications
```
┌────────────────────────────────┐
│ ✓ Success message         [X]  │
└────────────────────────────────┘
```
**Use for:** Non-blocking feedback
**Positions:** top-right, bottom-right, bottom-center

## State Patterns

### Empty States
```
┌────────────────────────────────┐
│                                │
│      [Icon/Illustration]        │
│                                │
│  No items found                │
│  Try adjusting your filters     │
│                                │
│        [Create New Item]        │
└────────────────────────────────┘
```

### Loading States
```
┌────────────────────────────────┐
│  ⏳ Loading...                 │
│  Skeleton placeholders         │
│  ┌──────────────────────────┐  │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
```

### Error States
```
┌────────────────────────────────┐
│  ⚠️ Error loading data         │
│                                │
│  [Retry] [Go Back]             │
└────────────────────────────────┘
```

## Design Tokens

### Typography
```yaml
typography:
  font_families:
    primary: "Inter, system-ui, sans-serif"
    monospace: "Fira Code, monospace"
  font_sizes:
    xs: "0.75rem"    # 12px
    sm: "0.875rem"   # 14px
    md: "1rem"       # 16px
    lg: "1.125rem"   # 18px
    xl: "1.25rem"    # 20px
    2xl: "1.5rem"    # 24px
    3xl: "1.875rem"  # 30px
  font_weights:
    normal: 400
    medium: 500
    semibold: 600
    bold: 700
  line_heights:
    tight: 1.25
    normal: 1.5
    relaxed: 1.75
```

### Spacing (8px Grid)
```yaml
spacing:
  0: "0"
  1: "0.25rem"   # 4px
  2: "0.5rem"    # 8px
  3: "0.75rem"   # 12px
  4: "1rem"      # 16px
  5: "1.25rem"   # 20px
  6: "1.5rem"    # 24px
  8: "2rem"      # 32px
  10: "2.5rem"   # 40px
  12: "3rem"     # 48px
```

### Colors (Semantic)
```yaml
colors:
  primary:
    main: "#3B82F6"
    light: "#60A5FA"
    dark: "#2563EB"
  secondary:
    main: "#6B7280"
    light: "#9CA3AF"
    dark: "#4B5563"
  success:
    main: "#10B981"
    light: "#34D399"
    dark: "#059669"
  warning:
    main: "#F59E0B"
    light: "#FBBF24"
    dark: "#D97706"
  error:
    main: "#EF4444"
    light: "#F87171"
    dark: "#DC2626"
```

### Border Radius
```yaml
border_radius:
  none: "0"
  sm: "0.125rem"   # 2px
  md: "0.375rem"   # 6px
  lg: "0.5rem"     # 8px
  xl: "0.75rem"    # 12px
  full: "9999px"   # Pill
```

## Accessibility (WCAG 2.1 AA)

### Color Contrast
- **Normal text**: Minimum 4.5:1 contrast ratio
- **Large text (18px+)**: Minimum 3:1 contrast ratio
- **Interactive elements**: Minimum 3:1 contrast ratio

### Keyboard Navigation
- All interactive elements must be keyboard accessible
- Visible focus indicator on all focusable elements
- Logical tab order (left-to-right, top-to-bottom)
- Skip links for main content

### Screen Reader Support
- Semantic HTML (`<nav>`, `<main>`, `<article>`, `<button>`)
- ARIA labels for icon-only buttons
- ARIA live regions for dynamic content
- Descriptive link text (avoid "click here")

### Touch Targets
- Minimum size: 44×44 CSS pixels
- Adequate spacing between targets
- Swipe gestures have alternative controls

## Responsive Design

### Breakpoints
```yaml
breakpoints:
  xs: "0px"        # Mobile
  sm: "640px"      # Mobile landscape
  md: "768px"      # Tablet
  lg: "1024px"     # Desktop
  xl: "1280px"     # Large desktop
  2xl: "1536px"    # Extra large desktop
```

### Mobile-First Considerations
- Touch-friendly controls (min 44px)
- Single column layout for mobile
- Simplified navigation (hamburger menu)
- Optimized images (lazy loading, responsive images)
- Reduced motion support

### Common Responsive Patterns
```
Mobile (< 768px):
- Single column
- Full-width cards
- Bottom navigation or hamburger menu
- Stacked forms

Tablet (768-1024px):
- Two column grid
- Side-by-side content
- Tab navigation

Desktop (> 1024px):
- Multi-column grid
- Max-width content containers
- Persistent navigation
```

## Visual Design Best Practices

### Visual Hierarchy
1. **Size**: Larger = more important
2. **Color**: Bright/bold = more important
3. **Position**: Top/left = more important
4. **Contrast**: High contrast = more attention

### Whitespace
- **Micro whitespace**: Between related elements (4-8px)
- **Macro whitespace**: Between sections (16-32px)
- Use whitespace to guide the eye, create breathing room

### Alignment
- **Left-align text** for readability
- **Center-align** only for short headings
- **Right-align numbers** for comparison
- **Consistent alignment** creates visual flow

### Consistency
- Use same component for similar actions
- Maintain consistent spacing
- Reuse color semantics (not arbitrary colors)
- Follow established patterns from design system

## Wireframe Template

```
Screen: [Screen Name]
Purpose: [What user accomplishes]
Entry: [How user arrives]
Exit: [What happens after]

Layout:
┌─────────────────────────────────────┐
│ Header: [Logo] [Nav] [User Menu]   │
├─────────────────────────────────────┤
│ ┌─────────────┬───────────────────┐ │
│ │ Sidebar     │ Main Content      │ │
│ │ - Item 1    │ [Hero/Heading]    │ │
│ │ - Item 2    │ [Content Area]    │ │
│ │ - Item 3    │ [Action Buttons]  │ │
│ └─────────────┴───────────────────┘ │
├─────────────────────────────────────┤
│ Footer: [Links] [Copyright]        │
└─────────────────────────────────────┘

Interactive Elements:
- [Element]: [Action] → [Result]

States:
- Default: [Description]
- Hover: [Changes]
- Active/Focus: [Changes]
- Disabled: [Appearance]
- Error: [Appearance + Message]
- Loading: [Indicator]
- Empty: [Empty state message]

Responsive:
- Mobile (< 768px): [Changes]
- Tablet (768-1024px): [Changes]
- Desktop (> 1024px): [Default]
```

## Reference

This is a reference document extracted from the `super-dev:ui-ux-designer` agent. For full agent behavior during Phase 5.5, invoke:

```
Task(subagent_type: "super-dev:ui-ux-designer", prompt: "Design UI/UX for: [feature]")
```

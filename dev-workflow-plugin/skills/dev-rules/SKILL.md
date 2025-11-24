---
name: dev-rules
description: Core development rules and philosophy. Use at the start of any development task to establish coding standards, git practices, and quality guidelines. Triggers on any implementation, fix, or refactoring task.
---

# Development Rules and Philosophy

These rules define coding standards and practices that MUST be followed for all development work.

## Figma MCP Integration Rules

When implementing designs from Figma:

### Required Flow (do not skip)
1. Run `get_design_context` first to fetch the structured representation for the exact node(s)
2. If response is too large or truncated, run `get_metadata` to get the high-level node map, then re-fetch only required node(s)
3. Run `get_screenshot` for a visual reference of the node variant being implemented
4. Only after you have both `get_design_context` and `get_screenshot`, download any assets needed and start implementation
5. Translate output into project's conventions, styles and framework. Reuse project's color tokens, components, and typography
6. Validate against Figma for 1:1 look and behavior before marking complete

### Implementation Rules
- Treat Figma MCP output as a representation of design and behavior, not as final code style
- Replace Tailwind utility classes with project's preferred utilities/design-system tokens when applicable
- Reuse existing components (buttons, inputs, typography, icon wrappers) instead of duplicating
- Use project's color system, typography scale, and spacing tokens consistently
- Respect existing routing, state management, and data-fetch patterns
- Strive for 1:1 visual parity with Figma design
- Validate final UI against Figma screenshot for both look and behavior

## Time MCP Rules (MUST follow)

- In every prompt, add the current date and time as extra context

## Git Rules (MUST follow)

- Never create GitHub Actions when creating new projects or updating code
- If GitHub Actions already exist, don't add to git cache, don't commit, don't push
- When committing, only commit files you edited - ignore files not created/edited by you in this session
- Don't use `git add -A` - use `git add file1 file2` (only files you edited/created/deleted)
- Before committing, **ALWAYS** generate proper commit messages

## Development Philosophy

### Core Principles
- **Incremental Development**: Small commits, each must compile and pass tests
- **Learn from Existing Code**: Research and plan before implementing
- **Pragmatic over Dogmatic**: Adapt to project's actual situation
- **Clear Intent over Clever Code**: Choose simple, clear solutions
- Avoid over-engineering - keep code simple, easy to understand, practical
- Watch cyclomatic complexity - maximize code reuse
- Focus on modular design - use design patterns where appropriate
- Minimize changes - avoid modifying code in other modules

### New Requirements Process
1. **Don't rush to code**: When user proposes new requirements, discuss the solution first
2. **Use ASCII diagrams**: When necessary, draw comparison diagrams for multiple solutions, let user choose
3. **Confirm before developing**: Only start development after user explicitly confirms the solution

### Implementation Process
1. **Understand existing patterns**: Study 3 similar features/components in the codebase
2. **Identify common patterns**: Find project conventions and patterns
3. **Follow existing standards**: Use same libraries/tools, follow existing test patterns
4. **Implement in phases**: Break complex work into 3-5 phases

### Quality Standards
- Every commit must compile successfully
- Pass all existing tests
- Include tests for new functionality
- Follow project formatting/linting rules

### Refactoring Process
1. First analyze project according to Clean Code principles
2. Create an incremental refactoring checklist, sorted by priority (high to low)
3. Execute one by one, update todo status after completing each item
4. Each step must be confirmed by user before proceeding

### Decision Framework Priority
1. **Testability** - Is it easy to test?
2. **Readability** - Will it be understandable in 6 months?
3. **Consistency** - Does it match project patterns?
4. **Simplicity** - Is it the simplest viable solution?
5. **Reversibility** - How hard to modify later?

### Error Handling & When Stuck
- Stop after maximum 3 attempts
- Record failure reasons and specific error messages
- Research 2-3 alternative implementation approaches
- Question basic assumptions: Is it over-abstracted? Can it be decomposed?

## Using This Skill

Announce at the start of any development task:
"I'm applying the dev-rules skill to ensure we follow project standards and best practices."

These rules should be referenced throughout the development workflow, especially during:
- Code implementation
- Code review
- Commit preparation
- Refactoring decisions

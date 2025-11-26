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

## Git Safety & Checkpoint Rules (CRITICAL)

### Frequent Checkpoints (MANDATORY)
To prevent losing work during context compaction or errors:

1. **Stash Before Major Operations**
   - Before starting a new phase, run `git stash push -m "checkpoint: [phase name]"`
   - Before risky operations (refactoring, large changes), create a stash
   - Use `git stash list` to verify stashes exist

2. **Commit After Every Completed Task**
   - After completing ANY task from the task list, commit immediately
   - Don't batch multiple tasks into one commit
   - Small, frequent commits > large, infrequent commits
   - Each commit should be atomic and compilable

3. **Verification Before Phase Transitions**
   - Before moving to next phase, run `git status` to check for uncommitted changes
   - ALL modified/created/deleted files MUST be either committed or stashed
   - Never leave files in "Changes not staged for commit" state between phases

4. **End-of-Session Cleanup**
   - Before ending work (or if context is getting large), ensure:
     - All work is committed OR stashed
     - Run `git status` - should show "nothing to commit, working tree clean"
     - If not clean, commit with WIP message or stash

### Checkpoint Triggers
Create a checkpoint (commit or stash) when:
- [ ] Completing a task from the task list
- [ ] Before starting a new phase
- [ ] After successful test run
- [ ] Before any refactoring
- [ ] Every 15-20 minutes of active coding
- [ ] Before context compaction warning appears

### Recovery Commands
If files are lost, use:
```bash
git stash list                    # List all stashes
git stash pop                     # Restore most recent stash
git reflog                        # Find lost commits
git checkout -- <file>            # Restore file from last commit
```

## Documentation Update Rules (CRITICAL)

### Keep Spec Documents Current (MANDATORY)
All specification documents MUST be updated as work progresses:

1. **Task List (`[index]-task-list.md`)**
   - Mark tasks complete immediately when done: `- [x] Task description`
   - Add new tasks discovered during implementation
   - Update status at every milestone boundary
   - Never leave task list stale between commits

2. **Implementation Summary (`[index]-implementation-summary.md`)**
   - Update after EACH milestone/phase completion
   - Document files created/modified/deleted
   - Record technical decisions and rationale
   - Track challenges encountered and solutions
   - Note any deviations from original specification

3. **Specification (`[index]-specification.md`)**
   - Update when implementation differs from original spec
   - Use `[UPDATED: YYYY-MM-DD]` marker for changed sections
   - Document why the change was necessary
   - Keep spec aligned with actual implementation

### Documentation Commit Rules
- **Commit docs WITH code**: Never commit code without updating related docs
- **Atomic doc updates**: Each task completion = task list update
- **Milestone summaries**: Add summary section at each phase boundary
- **Spec sync**: If code deviates from spec, update spec in same commit

### Enforcement Checklist
Before moving to next task/phase:
- [ ] Task list reflects actual completion state
- [ ] Implementation summary has latest progress
- [ ] Spec changes are documented with [UPDATED] markers
- [ ] Docs are committed together with code

**FORBIDDEN:**
❌ Completing tasks without updating task list
❌ Finishing milestones without updating implementation summary
❌ Implementing differently than spec without documenting deviation
❌ Committing code changes without corresponding doc updates

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

### Bug/Error Reporting Requirements (MANDATORY)

When a user reports a bug or error, **ALWAYS** ask for reproduction steps before attempting to fix:

#### Required Information
Ask user to provide:
1. **Steps to Reproduce** - Exact sequence of actions to trigger the bug
2. **Expected Behavior** - What should happen
3. **Actual Behavior** - What actually happens (error message, wrong output, etc.)
4. **Environment** (if relevant) - OS, browser, Node version, etc.

#### Example Questions to Ask
```
To help fix this bug, please provide:
1. What steps trigger this error? (e.g., "Run `npm test`, click button X, enter value Y")
2. What did you expect to happen?
3. What actually happened? (paste full error message if available)
4. Any relevant environment details?
```

#### Why This Matters
- Cannot reliably fix bugs without understanding how to reproduce them
- Prevents guessing and multiple failed fix attempts
- Ensures the fix actually addresses the user's specific issue
- Enables proper verification that the fix works

#### Exceptions
Only skip reproduction steps if:
- Error is clearly visible in provided stack trace/logs
- User provides comprehensive context upfront
- It's a typo or obvious code error the user points to directly

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

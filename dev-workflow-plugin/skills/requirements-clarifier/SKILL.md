---
name: requirements-clarifier
description: Gather and document requirements for features or bug fixes. Use when starting Phase 2 of dev-workflow to clarify what needs to be built or fixed.
---

# Requirements Clarifier

Systematically gather requirements before implementation begins.

**Announce:** "I'm using the requirements-clarifier skill to gather complete requirements."

## For New Features

Ask these questions (adapt as needed):

### Design & UI
- [ ] Is there a design? (Figma, mockups, wireframes)
- [ ] If yes, provide Figma link or design files
- [ ] Are there brand guidelines to follow?

### Technical Requirements
- [ ] What technical stack will be used?
- [ ] What programming languages?
- [ ] What frameworks/libraries preferred?
- [ ] Any specific architecture patterns required?

### Structure & Integration
- [ ] How does this fit into existing project structure?
- [ ] What existing components can be reused?
- [ ] What APIs or services will it integrate with?
- [ ] Are there database changes required?

### Constraints
- [ ] Performance requirements?
- [ ] Security considerations?
- [ ] Browser/device compatibility?
- [ ] Accessibility requirements?

## For Bug Fixes

Ask these questions:

### Environment
- [ ] Desktop or mobile?
- [ ] Operating system and version?
- [ ] Browser and version?
- [ ] Device type (if mobile)?

### Evidence
- [ ] Screenshots showing the error?
- [ ] Error messages (exact text)?
- [ ] Console logs?
- [ ] Build logs?
- [ ] Runtime/debug logs?

### Reproduction
- [ ] Steps to reproduce?
- [ ] Does it happen consistently?
- [ ] When did it start occurring?
- [ ] Any recent changes that might be related?

### Impact
- [ ] How many users affected?
- [ ] Is there a workaround?
- [ ] Priority level?

## Output

Document requirements in spec directory:
- File: `[index]-requirements.md`
- Include all gathered information
- Note any assumptions made
- List any open questions for later phases

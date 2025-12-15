## Figma MCP Integration Rules
These rules define how to translate Figma inputs into code for this project and must be followed for every Figma-driven change.

### Required flow (do not skip)
1. Run get_design_context first to fetch the structured representation for the exact node(s).
2. If the response is too large or truncated, run get_metadata to get the high‑level node map and then re‑fetch only the required node(s) with get_design_context.
3. Run get_screenshot for a visual reference of the node variant being implemented.
4. Only after you have both get_design_context and get_screenshot, download any assets needed and start implementation.
5. Translate the output  into this project's conventions, styles and framework.  Reuse the project's color tokens, components, and typography wherever possible.
6. Validate against Figma for 1:1 look and behavior before marking complete.

### Implementation rules
- Treat the Figma MCP output  as a representation of design and behavior, not as final code style.
- Replace Tailwind utility classes with the project's preferred utilities/design‑system tokens when applicable.
- Reuse existing components (e.g., buttons, inputs, typography, icon wrappers) instead of duplicating functionality.
- Use the project's color system, typography scale, and spacing tokens consistently.
- Respect existing routing, state management, and data‑fetch patterns already adopted in the repo.
- Strive for 1:1 visual parity with the Figma design. When conflicts arise, prefer design‑system tokens and adjust spacing or sizes minimally to match visuals.
- Validate the final UI against the Figma screenshot for both look and behavior.

## Time MCP rules (MUST follow)

- in every prompt, add the current date and time as an extra info for context

## github rule (MUST follow)
- whenerver create new project or update / fix the code, don't create github action
- if there is already some github actions, don't add to git cache, don't commit, don't push
- when commit and push, only commit those file you edited, ignore the files which are not created or edit by you at the moment
- don't use git add -A, just use git add file1 file2( only files edit/created/delete by you in this session)

## Development Philosophy Integration (MUST follow)

- **Incremental development**: Make small, atomic commits; each commit must compile/build successfully and pass all tests.
- **Learn from existing code**: Research and plan before beginning implementation.
- **Pragmatic, not dogmatic**: Adapt to project realities.
- **Explicit intent over clever code**: Choose simple, clear solutions.
- Avoid over-engineering; keep code simple, readable, and practical.
- Manage cyclomatic complexity; maximize code reuse.
- Emphasize modular design; use design patterns where appropriate.
- Minimize changes; avoid modifying unrelated module code.
- Occam's Razor (do not add code unless necessary)

### New Requirements Process (MUST follow)
1. **Do not rush into coding during initial communication**: When the user proposes a new requirement, first conduct a solution discussion.
2. **Use ASCII diagrams**: When necessary, create comparative ASCII diagrams for multiple solution options to enable the user to select the optimal approach.

### Implementation Process (MUST follow)
1. Understand existing patterns: study three analogous features/components in the codebase.
2. Identify common patterns: determine project conventions and recurring patterns.
3. Adhere to existing standards: use the same libraries/tools and follow the established testing patterns.
4. Implement in phases: decompose complex work into 3–5 stages.
5. No reinventing the wheel: extensively reuse open-source components, and use AI to write the "glue code" that binds them together.
6. Modularity: develop like assembling building blocks—define interfaces first, implement afterward.
8. for api implementation, always use version api endpoints like `/api/v1/xxx`
9. In Next.js, do not use deprecated or global middleware for request proxying. Prefer implementing a proxy via Route Handlers (e.g., /app/api/proxy/route.ts) or a dedicated proxy.ts/js helper, and use next.config.js rewrites/redirects when appropriate.
10. If the project includes both frontend and backend, split them into two directories (e.g., /frontend and /backend) and maintain separate build/test pipelines for each.
### Quality Standards (MUST follow)
- Each commit must compile successfully
- Pass all existing tests
- Include tests for new functionality
- Adhere to project formatting and linting checks

### refactor Process

1. First analyze the project according to Clean Code principles.
2. Prepare an incremental refactoring checklist and prioritize items from highest to lowest.
3. Execute items one by one; after completing each item, update the to‑do status.
4. Obtain my approval for each step before proceeding to the next.

### Decision Framework Priority
1. **Testability** - Is it easy to test?
2. **Readability** - Will it still be understandable in six months?
3. **Consistency** - Does it conform to project patterns?
4. **Simplicity** - Is it the simplest viable solution?
5. **Reversibility** - What is the difficulty of making subsequent changes?

### Error Handling & When Stuck
- Stop after a maximum of three attempts.
- Record the failure cause and the specific error message(s).
- Investigate 2–3 alternative implementation approaches.
- Challenge foundational assumptions: Is the solution over-abstracted? Can it be decomposed into smaller parts?


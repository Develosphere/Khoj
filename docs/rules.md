# AI Development Rules

1. Always read `/docs/overview.md` before starting a new development module.

2. Treat the current module prompt as the authoritative specification for that module.

3. Read only files that are:
   - explicitly referenced by the prompt,
   - directly imported by those files,
   - or genuinely required to complete the task.

4. Do not scan the entire repository unless explicitly instructed.

5. If additional files are required, inspect the smallest relevant set first.

6. Never invent existing files, APIs, database fields, routes, schemas, functions, environment variables, or completed features. Verify them from the repository before using them.

7. Do not modify unrelated modules or perform unsolicited refactors.

8. Reuse existing components, utilities, types, schemas, and patterns when available rather than creating duplicates.

9. Keep implementations within the approved stack defined in `overview.md`.

10. Keep responses concise. Do not repeat project context, explain obvious implementation steps, or produce large summaries unless requested.

11. After implementation, run the relevant type-check/build/test commands and fix errors caused by the changes.

12. At the end of a meaningful development phase, update:
    - `/docs/CURRENT_STATE.md`
    - `/docs/NEXT.md`

    only if those files exist or the prompt explicitly requests them.

13. Never overwrite stable documentation with speculative information.

14. When uncertain about an existing implementation detail, inspect the relevant source file instead of guessing.

15. Optimize for the smallest correct change that satisfies the current task.

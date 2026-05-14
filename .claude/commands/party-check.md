# /party-check — Quick status read

Show current state at a glance. No code, no changes — information only.

## Output

Read and summarize in a compact table or list:

- **Phase:** current milestone and status (from `baton-pass.state.json`)
- **Last agent:** who last touched this (from `baton-pass.state.json`)
- **Done:** bullet list from `docs/current-state.md` → "What's done"
- **In progress:** from `docs/current-state.md` → "What's in progress"
- **Blockers:** from `docs/current-state.md` → "Blockers"
- **Next task:** one-line summary from `docs/next-task.md`

Keep the output under 20 lines.

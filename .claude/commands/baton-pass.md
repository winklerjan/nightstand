# /baton-pass — Transfer session

Commit staged work, update state docs, and hand off to the next agent or human.

## Steps

1. Verify everything compiles / type-checks:
   - `pnpm --filter frontend check` (if frontend changed)
   - `cargo clippy` from `src-tauri/` (if Rust changed)
   - Restart sidecar and hit `/health` (if backend changed)
2. Stage and commit any uncommitted changes with a focused commit message.
3. Update `docs/current-state.md`:
   - Move completed items to "What's done"
   - Clear "What's in progress"
   - Note any blockers
4. Update `docs/next-task.md` with the next task, acceptance criteria, and do-not-touch list.
5. Append a new entry to `docs/progress.md` with: date, agent, what was completed, deviations from spec, state at end.
6. Update `baton-pass.state.json`: set `state` to `idle`, update `lastMove`, `lastAgent`, `updatedAt`, `summary`.
7. Report the handoff summary to the user.

## Rules

- Do not amend commits. Create new ones.
- Do not skip verification. A green check > a fast handoff.
- If something is broken at handoff time, document it in `current-state.md` blockers rather than hiding it.

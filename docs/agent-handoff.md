# Agent Handoff — Operating Doc

## Resume order (read these in sequence)

1. `AGENTS.md` — shared rules, architecture, forbidden ops, conventions
2. `CLAUDE.md` (if Claude) — RTK prefix, skills, memory location
3. `docs/current-state.md` — what's done, what's in progress, blockers
4. `docs/next-task.md` — the single next task with acceptance criteria
5. `docs/progress.md` — append-only session log (skim for context)
6. `docs/NIGHTSTAND_BUILD.md` — full product brief (reference, not re-read every session)

## Source-of-truth hierarchy

When state files conflict with code or git history, this order wins:

> user request > code > git log > `current-state.md` > `next-task.md` > `progress.md` > older docs

## Repo-specific rules

- Never run `calibredb embed_metadata`. See AGENTS.md §4.
- Calibre GUI must be closed for any calibredb write. M1 has no writes.
- Frontend fetches use `http://localhost`, not `http://127.0.0.1`. See AGENTS.md §3.
- Every `subprocess.run()` that calls calibredb passes `env=_clean_env()`. See AGENTS.md §3.
- Run `pnpm --filter frontend check` after any frontend change.
- Run `cargo clippy` from `src-tauri/` after any Rust change.

## Claiming a session

Run foresight before writing any code. In Claude, use `/foresight`. In Codex TUI, use `$baton-pass run foresight` or plain language such as "Use Baton Pass to run foresight for this repo"; `/foresight` is not a native Codex slash command.

## Ending a session

Run `/baton-pass` to commit staged work, update `current-state.md`, `next-task.md`, and append to `progress.md`.

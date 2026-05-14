# /new-game — Bootstrap baton-pass system

Initialize all baton-pass config and state files for a new project. Run this once at project start.

## Steps

1. Confirm the user wants to overwrite existing state (if `baton-pass.state.json` already exists, warn).
2. Create or reset:
   - `baton-pass.config.json` — paths, command map, rules
   - `baton-pass.state.json` — initial state: `{ state: "idle", milestone: "M0", lastAgent: null, ... }`
   - `docs/current-state.md` — blank template
   - `docs/next-task.md` — blank template
   - `docs/agent-handoff.md` — operating doc from AGENTS.md
   - `docs/progress.md` — empty log with header
3. Verify `AGENTS.md` exists. If not, ask the user to create it before proceeding.
4. Report: "Baton-pass system initialized. Run /foresight to claim the first session."

For the Nightstand project, these files already exist. Do not run /new-game — it would overwrite current state. Use /foresight to start a session instead.

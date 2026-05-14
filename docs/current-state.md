# Current State

**Updated:** 2026-05-14
**Phase:** M1 — Library Browser (implementation written, manual app verification pending)
**Last agent:** Codex GPT-5.5

---

## What's done

- **M0 — Project scaffolding:** complete
  - Tauri 2 shell with sidecar spawn, port handoff, window lifecycle
  - Python FastAPI sidecar with `/health` and `/calibre/probe` endpoints
  - SvelteKit frontend showing sidecar and Calibre status cards
  - `pnpm dev` runs the full stack end-to-end
  - `_clean_env()` in calibre service strips venv to prevent shebang collision

- **Agentic workflow setup:** complete
  - `AGENTS.md` — shared source-of-truth for all agents
  - `CLAUDE.md` — Claude-specific config (skills, RTK, memory)
  - `docs/current-state.md`, `docs/next-task.md`, `docs/agent-handoff.md`, `docs/progress.md`
  - `baton-pass.config.json`, `baton-pass.state.json`
  - `.claude/settings.json` — deny rules added
  - `.claude/settings.local.json` — permission allowlist (gitignored)
  - `.claude/commands/` — foresight, baton-pass, save-state, party-check, dragon-dance, hindsight, new-game
  - `docs/ai/project.md` — tech stack quick-ref

- **M1 design:** complete and committed
  - `docs/superpowers/specs/2026-05-14-m1-library-browser-design.md` — approved design spec
  - Key decisions: single load (~300 books), both table + grid views (toggle, localStorage), slide-in detail panel, AND/OR filter toggle, lazy cover loading, metadata extras embedded in book detail response

- **M1 implementation:** written, not committed
  - Backend: read-only `/library/books`, `/library/books/{id}`, `/library/books/{id}/cover`, and `/library/tags` routes
  - Backend: Calibre list/detail/tag/cover helpers, metadata extras reader, `CalibreLockedError` mapped to HTTP 423
  - Frontend: Svelte stores, in-browser filtering, table/grid views, lazy cover placeholders, filter sidebar, detail panel, disabled M2 edit button
  - Plan saved at `docs/superpowers/plans/2026-05-14-m1-library-browser.md`

## What's in progress

M1 needs manual app/API verification and review before commit. The worktree is not clean. In addition to M1 files, repo-local Codex Baton Pass plugin files are present but untracked:

- `.agents/plugins/marketplace.json`
- `plugins/baton-pass/.codex-plugin/plugin.json`
- `plugins/baton-pass/skills/baton-pass/SKILL.md`

## Blockers

No code blocker found. Sandbox network isolation prevented curl from reaching the locally started sidecar, so `/library/*` endpoint behavior still needs manual verification in a normal dev shell. Decide later whether the repo-local Codex plugin files should be committed or kept local-only.

## Next

Run manual verification in a normal shell: start `pnpm dev`, confirm the M1 browser loads, exercise table/grid, filters, detail panel, covers, and Calibre lock behavior, then commit the M1 implementation separately from the repo-local Codex plugin files.

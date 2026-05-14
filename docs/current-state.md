# Current State

**Updated:** 2026-05-14
**Phase:** M1 — Library Browser (design approved, implementation not started)
**Last agent:** Claude Sonnet 4.6

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

## What's in progress

Nothing. Clean handoff.

## Blockers

None.

## Next

Implement M1 per `docs/superpowers/specs/2026-05-14-m1-library-browser-design.md`. The next agent should invoke `/foresight` then `writing-plans` to create the implementation plan before touching code.

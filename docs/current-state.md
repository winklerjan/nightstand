# Current State

**Updated:** 2026-05-14
**Phase:** M0 complete, M1 ready to start
**Last agent:** Claude Sonnet 4.6

---

## What's done

- **M0 — Project scaffolding:** complete
  - Tauri 2 shell (`src-tauri/`) with sidecar spawn, port handoff, window lifecycle
  - Python FastAPI sidecar (`backend/`) with `/health` and `/calibre/probe` endpoints
  - SvelteKit frontend (`frontend/`) showing sidecar and Calibre status cards
  - `pnpm dev` runs the full stack end-to-end
  - `_clean_env()` in calibre service strips venv to prevent shebang collision

- **Agentic workflow setup:** complete
  - `AGENTS.md` — shared source-of-truth for all agents
  - `CLAUDE.md` — Claude-specific config (skills, RTK, memory)
  - Baton-pass docs and config wired up
  - `.claude/settings.local.json` — permission whitelist
  - `.claude/commands/` — custom slash commands

## What's in progress

Nothing. Clean handoff.

## Blockers

None.

## Next

M1 — Library Browser. Open questions in `docs/M1_LIBRARY_BROWSER.md` must be resolved with the user before implementation starts.

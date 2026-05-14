# Next Task

**Task:** M1 — Library Browser (manual verification and commit)
**Spec:** `docs/superpowers/specs/2026-05-14-m1-library-browser-design.md`
**Plan:** `docs/superpowers/plans/2026-05-14-m1-library-browser.md`

---

## Verification checklist

1. Run `pnpm dev` from repo root in a normal shell.
2. Confirm the app launches and retrieves the sidecar port.
3. Confirm `GET /library/books`, `GET /library/tags`, `GET /library/books/{id}`, and `GET /library/books/{id}/cover` behave as expected.
4. Confirm Calibre GUI lock returns HTTP 423 and the UI shows the lock banner/panel error.
5. Confirm table/grid toggle works and persists in `localStorage`.
6. Confirm search, tag OR, tag AND, and language filters work.
7. Confirm clicking a book opens the right-side detail panel.
8. Confirm missing covers show placeholders, not broken image UI.
9. Confirm no raw file paths are visible in the UI.
10. Confirm no Calibre write commands were added.

## Current changed files

**Backend:**
- `backend/nightstand/services/calibre.py`
- `backend/nightstand/api/library.py`
- `backend/nightstand/main.py`

**Frontend:**
- `frontend/src/routes/+page.svelte`
- `frontend/src/lib/types.ts`
- `frontend/src/lib/store/library.ts`
- `frontend/src/lib/components/FilterSidebar.svelte`
- `frontend/src/lib/components/BookTable.svelte`
- `frontend/src/lib/components/BookGrid.svelte`
- `frontend/src/lib/components/BookRow.svelte`
- `frontend/src/lib/components/BookCard.svelte`
- `frontend/src/lib/components/BookDetail.svelte`

**Docs/state:**
- `docs/superpowers/plans/2026-05-14-m1-library-browser.md`
- `baton-pass.state.json`
- `docs/current-state.md`
- `docs/next-task.md`
- `docs/progress.md`
- `docs/agent-handoff.md`

**Untracked local plugin files, decide separately:**
- `.agents/plugins/marketplace.json`
- `plugins/baton-pass/.codex-plugin/plugin.json`
- `plugins/baton-pass/skills/baton-pass/SKILL.md`

## Do not touch

- `src-tauri/` — no Rust changes needed for M1
- Any calibredb write operations

## Verification already run

- `env UV_CACHE_DIR=/tmp/nightstand-uv-cache uv run python -m compileall nightstand` — passed
- `env UV_CACHE_DIR=/tmp/nightstand-uv-cache uv run python -c 'import nightstand.main; print("import ok")'` — passed
- `pnpm --filter frontend check` — passed with one existing warning: missing type definition file for `node`
- `pnpm --filter frontend build` — passed
- `rg "127\\.0\\.0\\.1" frontend -n` — passed, no matches
- Manual curl/API verification — not run due sandbox network isolation

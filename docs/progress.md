# Progress Log

Append-only. Never overwrite — only add new entries at the bottom.

---

## 2026-05-14 — Session 1 (Claude Sonnet 4.6)

**Completed:**
- Read `docs/NIGHTSTAND_BUILD.md` and `docs/M0_SCAFFOLDING.md`
- Confirmed stack (SvelteKit + Tauri 2 + Python FastAPI)
- Implemented M0 in full:
  - Tauri shell with sidecar spawn + port handoff + window lifecycle
  - Python FastAPI sidecar with `/health` and `/calibre/probe`
  - SvelteKit frontend showing sidecar + Calibre status cards
  - `_clean_env()` to prevent venv/calibredb shebang collision
- Wrote `docs/M1_LIBRARY_BROWSER.md` outline
- Wrote `docs/superpowers/specs/2026-05-14-agentic-setup-design.md`

**Deviations from spec:** none

**State at end:** M0 complete, agentic setup spec written

---

## 2026-05-14 — Session 2 (Claude Sonnet 4.6)

**Completed:**
- Implemented agentic workflow setup from `docs/superpowers/specs/2026-05-14-agentic-setup-design.md`:
  - Created `AGENTS.md` (shared source-of-truth for all agents)
  - Updated `CLAUDE.md` (Claude-specific config)
  - Created `docs/current-state.md`, `docs/next-task.md`, `docs/agent-handoff.md`, `docs/progress.md`
  - Created `baton-pass.config.json`, `baton-pass.state.json`
  - Updated `.claude/settings.json`, created `.claude/settings.local.json`
  - Created all `.claude/commands/` slash command files

**Deviations from spec:**
- Hookify files not created — hookify plugin not confirmed available; noted in open items
- `docs/ai/project.md` created as tech-stack quick-ref (not specified in spec but natural complement)

**State at end:** Agentic setup complete. Awaiting M1 design Q&A with user before implementation.

---

## 2026-05-14 — Session 3 (Claude Sonnet 4.6)

**Completed:**
- Ran brainstorming skill for M1 Library Browser
- Resolved all open design questions with user:
  - Both table + grid views with toggle (localStorage persistence)
  - Slide-in detail panel
  - Read `~/.config/calibre_helper/metadata.json` extras (embedded in book detail response)
  - Single load of all books (~300), in-browser filtering
  - AND/OR filter toggle (user-selectable)
  - Lazy cover loading (`loading="lazy"`)
- Wrote and committed `docs/superpowers/specs/2026-05-14-m1-library-browser-design.md`
- Updated `docs/current-state.md`, `docs/next-task.md`, `baton-pass.state.json`

**Deviations from spec:** none

**State at end:** M1 design approved and committed. Implementation not started. Next agent should invoke writing-plans before writing code.

---

## 2026-05-14 — Session 4 (Codex GPT-5.5)

**Completed:**
- Ran Baton Pass foresight in Codex after confirming `/foresight` is not a native Codex TUI slash command.
- Re-read `baton-pass.state.json`, `docs/current-state.md`, `docs/next-task.md`, latest `docs/progress.md`, recent git commits, and `docs/superpowers/specs/2026-05-14-m1-library-browser-design.md`.
- Corrected handoff docs to record the actual worktree state.

**Deviations from spec:** none

**Verification:** not run - documentation-only handoff correction.

**State at end:** M1 implementation not started. Worktree is not clean because repo-local Codex Baton Pass plugin files are untracked.

---

## 2026-05-14 — Session 5 (Codex GPT-5.5)

**Completed:**
- Wrote `docs/superpowers/plans/2026-05-14-m1-library-browser.md`.
- Implemented read-only backend Calibre helpers and `/library/*` API routes.
- Implemented Svelte stores, filter sidebar, table view, grid view, cover placeholders, and slide-in detail panel.
- Replaced the M0 status-card page with the M1 library browser shell.

**Deviations from spec:**
- Comments render as plain text rather than raw HTML to avoid unnecessary webview exposure.
- Manual API curl verification could not be completed inside the sandbox because local server processes were not reachable from separate curl sessions.

**Verification:**
- `env UV_CACHE_DIR=/tmp/nightstand-uv-cache uv run python -m compileall nightstand` — passed
- `env UV_CACHE_DIR=/tmp/nightstand-uv-cache uv run python -c 'import nightstand.main; print("import ok")'` — passed
- `pnpm --filter frontend check` — passed with one existing warning: missing type definition file for `node`
- `pnpm --filter frontend build` — passed
- `rg "127\\.0\\.0\\.1" frontend -n` — passed
- Manual `pnpm dev` UI verification — not run due sandbox/dev-server constraints

**State at end:** M1 implementation is written but uncommitted. Next step is manual verification in a normal shell, then commit M1 separately from the untracked repo-local Codex plugin files.

---

## 2026-05-15 — Session 6 (Claude Sonnet 4.6)

**Completed:**
- Analysed app state; found `docs/current-state.md` was stale (M1 was already committed as `af73161`).
- Took Calibre data backup to `/Documents/Kindle/calibre backup 2026-05-15/` (library + config, 557 MB).
- Diagnosed and fixed three M1 runtime bugs (commit `abf191d`):
  1. **Covers not loading** — `get_cover_path` called `calibredb get_metadata --for-machine`, which is not a valid flag for that subcommand. Replaced with `_folder_cache` (lazily built from `calibredb list --fields id,formats`) that derives `cover.jpg` from each book's format directory.
  2. **Covers reloading on view switch** — added `Cache-Control: public, max-age=3600` to the cover `FileResponse`.
  3. **Concurrent calibredb traffic** — `list_books` now pre-populates `_folder_cache` so all subsequent cover requests are pure dict lookups with no calibredb process spawned.
  4. **Book detail comments hang** — `calibredb list --fields ...,comments,...` hangs on this library; comments now read directly from `metadata.opf` via `xml.etree.ElementTree`.
  5. **BookDetail loading pattern** — replaced manual `requestToken`/`$effect` with `{#await bookPromise}`; Svelte owns the lifecycle, eliminating the token-mismatch failure mode.
- Confirmed backend endpoint works standalone: `curl http://localhost:8765/library/books/3` returns correct JSON in < 1 s.

**Deviations from spec:** none (bug fixes only, no scope change).

**Verification:**
- `pnpm --filter frontend check` — 0 errors, 1 pre-existing node-types warning
- `uv run python -c 'import nightstand.main'` — passed
- `curl http://localhost:8765/library/books/3` — correct JSON with comments returned

**State at end:** M1 bug fixes committed. Book detail fix (`{#await}` + folder cache) has not been user-verified in `pnpm dev` — the session ended before the user could test. Covers and caching fixes were confirmed working by the user ("everything's fixed except for loading book").

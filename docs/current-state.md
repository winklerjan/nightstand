# Current State

**Updated:** 2026-05-15
**Phase:** M1 — Library Browser (implemented and committed; three runtime bugs fixed; book detail loading fix unverified)
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

- **M1 design:** complete and committed

- **M1 implementation:** complete and committed (`af73161`)

- **M1 runtime bug fixes:** committed (`abf191d`)
  - **Covers not loading:** `get_cover_path` was calling `calibredb get_metadata --for-machine` — `--for-machine` is invalid for `get_metadata`. Replaced with a `_folder_cache` (populated lazily from `calibredb list --fields id,formats`) that derives `cover.jpg` path from the book's format directory.
  - **Covers reloading on view switch:** added `Cache-Control: public, max-age=3600` to the cover `FileResponse`.
  - **Concurrent calibredb calls:** `list_books` now pre-populates `_folder_cache` so all subsequent cover requests are pure dict lookups — zero calibredb processes spawned during lazy cover loading.
  - **Book detail comments hang:** `calibredb list --fields ...,comments,...` hangs on this library; comments are now read directly from the book folder's `metadata.opf` via `xml.etree.ElementTree`.
  - **BookDetail loading pattern:** replaced manual `requestToken` / `$effect` pattern with `{#await bookPromise}` — Svelte owns the loading/error lifecycle, eliminating the token-mismatch failure mode.

- **Calibre data backup:** taken 2026-05-15 at `/Documents/Kindle/calibre backup 2026-05-15/` (library + config, 557 MB).

## What's in progress

Nothing.

## Blockers

**Book detail "Loading book..." still unverified.** The last user report ("nah didn't help") referred to the previous fix (removing `--search` from calibredb). The current fix (pre-populated folder cache + `{#await}`) has NOT yet been tested by the user — the baton-pass was requested immediately after. The backend endpoint was confirmed working in isolation via curl. Next agent should verify the fix works in `pnpm dev` before moving on.

## Next

Verify book detail loading in `pnpm dev`. If still broken, open Tauri devtools (F12), check the Network tab when clicking a book, and report what the `/library/books/{id}` request does (hangs, errors, or succeeds). Then move to M2 design.

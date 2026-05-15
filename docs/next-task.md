# Next Task

**Task:** Verify book detail loading fix, then begin M2 design
**Spec:** `docs/M1_LIBRARY_BROWSER.md` (for M2 scope reference)

---

## Step 1 — Verify book detail fix (required before M2)

1. Run `pnpm dev` from repo root.
2. Wait for library to load.
3. Click any book — the right-side detail panel should open and show book data within a second or two.
4. If it still shows "Loading book..." indefinitely:
   - Open Tauri devtools (right-click → Inspect or F12)
   - Go to Network tab
   - Click a book and observe what `/library/books/{id}` does (pending, error, or response)
   - Report the finding — do NOT attempt further fixes without this evidence

## Step 2 — M2 design (only after Step 1 passes)

Run the brainstorming skill before any design or implementation. M2 scope is metadata editing — likely:
- Edit tags, series, language, pubdate fields
- Write back via `calibredb set_metadata`
- The "Coming in M2" button in the detail panel is the entry point

Ask the user about scope before writing any spec.

## Do not touch

- `src-tauri/` — no Rust changes needed
- `calibredb embed_metadata` — forbidden (destroys normalized filenames)
- Any of the M1 read endpoints unless they're still broken

## Verification already run

- `pnpm --filter frontend check` — 0 errors, 1 pre-existing warning
- `uv run python -c 'import nightstand.main'` — passes
- `curl http://localhost:8765/library/books/3` (standalone backend) — returns correct JSON with comments

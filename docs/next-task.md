# Next Task

**Task:** M1 — Library Browser (implementation)
**Spec:** `docs/superpowers/specs/2026-05-14-m1-library-browser-design.md`
**Prerequisite:** Invoke `writing-plans` skill to generate the implementation plan before writing any code.

---

## Acceptance criteria

1. `GET /library/books` returns full book list from `calibredb list --for-machine`
2. `GET /library/books/{id}` returns full metadata + extras from `~/.config/calibre_helper/metadata.json` (if present)
3. `GET /library/books/{id}/cover` streams cover image, returns 404 if no cover
4. `GET /library/tags` returns deduplicated tag list
5. `CalibreLockedError` → HTTP 423 on all endpoints (not 500)
6. Frontend: filter sidebar with tag chips, language chips, AND/OR toggle, search bar
7. Frontend: table view and grid view, toggled top-right, preference in `localStorage`
8. Frontend: clicking a book slides in a detail panel from the right
9. Frontend: detail panel shows full metadata + extras, placeholder Edit button
10. Frontend: lazy cover loading, placeholder for missing covers
11. No Calibre writes anywhere

## Files expected to change

**Backend:**
- `backend/nightstand/services/calibre.py` — add `list_books()`, `get_book()`, `get_tags()`, `read_metadata_extras()`
- `backend/nightstand/api/library.py` — new file, FastAPI router
- `backend/nightstand/api/__init__.py` — may need updating
- `backend/nightstand/main.py` — register library router

**Frontend:**
- `frontend/src/routes/+page.svelte` — replace M0 skeleton with library shell
- `frontend/src/lib/types.ts` — new file: Book, BookDetail, Filters interfaces
- `frontend/src/lib/store/library.ts` — new file: stores + filteredBooks derived
- `frontend/src/lib/components/FilterSidebar.svelte` — new
- `frontend/src/lib/components/BookTable.svelte` — new
- `frontend/src/lib/components/BookGrid.svelte` — new
- `frontend/src/lib/components/BookRow.svelte` — new
- `frontend/src/lib/components/BookCard.svelte` — new
- `frontend/src/lib/components/BookDetail.svelte` — new

## Do not touch

- `src-tauri/` — no Rust changes needed for M1
- Existing calibre.py functions (`version()`, `list_first()`) — only add, don't modify
- Any calibredb write operations

## Reference

- `docs/superpowers/specs/2026-05-14-m1-library-browser-design.md` — full design
- `AGENTS.md` §0 — M1 read-only scope enforcement
- `AGENTS.md` §3 — critical gotchas (localhost not 127.0.0.1, _clean_env, etc.)

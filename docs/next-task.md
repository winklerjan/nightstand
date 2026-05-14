# Next Task

**Task:** M1 — Library Browser
**Prerequisite:** Resolve open questions in `docs/M1_LIBRARY_BROWSER.md` with the user first.

---

## Acceptance criteria

1. `GET /library/books` returns paginated book list from `calibredb list`
2. `GET /library/books/{id}` returns full metadata for one book
3. `GET /library/books/{id}/cover` streams the cover image
4. `GET /library/tags` returns distinct tag list
5. Frontend shows a book list with filter sidebar and search bar
6. Clicking a book shows a detail panel (slide-in or route — confirm with user)
7. No Calibre writes anywhere in M1

## Files expected to change

**Backend:**
- `backend/nightstand/services/calibre.py` — add `list_books()`, `get_book()`
- `backend/nightstand/api/library.py` — new FastAPI router (new file)
- `backend/nightstand/main.py` — register library router

**Frontend:**
- `frontend/src/routes/+page.svelte` — replace skeleton with library list UI
- `frontend/src/lib/` — new components (BookList, BookRow, BookDetail, FilterSidebar)

## Do not touch

- `src-tauri/` — no Rust changes needed for M1
- `backend/nightstand/services/calibre.py` — only add, don't modify existing functions
- Any calibredb write operations

## Reference

`docs/M1_LIBRARY_BROWSER.md` — outline and API spec
`docs/NIGHTSTAND_BUILD.md` §3 M1 — feature requirements
`AGENTS.md` §0 — M1 read-only scope enforcement

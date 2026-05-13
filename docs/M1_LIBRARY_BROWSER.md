# Nightstand — M1: Library Browser (draft outline)

**Status:** Proposed — review and revise with user before implementation starts.

---

## Goal

A read-only list view of the Calibre library that feels genuinely better than Calibre's own UI. The user can browse, filter, and inspect books. No writes yet — that comes in M2 with Smart Import.

Success criterion: open the app, see the full library in a clean list, click a book to see its detail panel (cover + metadata). Nothing else.

---

## API endpoints (backend)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/library/books` | Paginated list of all books. Query params: `page`, `per_page` (default 50), `tag`, `language`, `search` (substring on title/author). |
| `GET` | `/library/books/{id}` | Full metadata for one book: title, authors, tags, series, series_index, languages, pubdate, cover URL, file formats + paths. |
| `GET` | `/library/books/{id}/cover` | Serves the cover image bytes (calibredb get_metadata → cover path, then stream the file). |
| `GET` | `/library/tags` | Distinct tag list (for filter sidebar). |

All backed by `calibredb list --for-machine`. No DB writes in M1.

---

## UI screens

### List view (main screen)

- Left sidebar: filter chips by tag, language. Search bar at top.
- Main area: table or card grid of books.
  - Per row/card: cover thumbnail, title, author, year, tags, format badges (EPUB/MOBI/…).
  - Click row → detail panel slides in from the right (or navigates to detail route).
- Pagination or virtual scroll (calibredb list can return thousands of books).

### Detail panel / page

- Cover (large), title, author(s), series (if set), year, language, tags.
- File paths / formats listed.
- Nightstand extras (subgenres, themes) — shown as read-only, sourced from `~/.config/calibre_helper/metadata.json` if present, otherwise empty.
- Placeholder "Edit" button (wired up in a later milestone).

---

## Backend service additions

- `backend/nightstand/services/calibre.py` — add `list_books(library_path, fields, search, limit, offset)` and `get_book(library_path, book_id)`.
- `backend/nightstand/api/library.py` — new FastAPI router, registered in `main.py`.
- Cover serving: `calibredb get_metadata --with-library <path> <id>` outputs a cover path; stream it with `FileResponse`.

---

## Out of scope for M1

- Any writes to Calibre (inline edit, tag changes). Those are M2+.
- AI/metadata enrichment. M2.
- Kindle sync. M6.
- Nightstand sidecar DB (SQLite). Can wait until there's something to store.
- Theming / Omarchy palette. Works fine with the plain dark base from M0.

---

## Open questions to resolve before M1 starts

1. **List layout:** table rows or cover-grid cards? (Recommendation: table with small thumbnail — faster to scan for title/author.)
2. **Pagination vs virtual scroll:** with ~300 books, a single load of 500 records from `calibredb list` is fast enough. Virtual scroll adds complexity; paginate for now?
3. **Detail panel UX:** slide-in panel (keeps list visible) or separate route? (Recommendation: slide-in panel — stays in context.)
4. **Cover quality:** serve covers at what max dimension? (Recommendation: 300 px wide for list thumbnail, full-size for detail panel.)
5. **Nightstand metadata file:** should M1 read `~/.config/calibre_helper/metadata.json` to show subgenres/themes, or leave that for M2? (Recommendation: read it if present, show as read-only extras in detail panel — zero cost, gives immediate value.)

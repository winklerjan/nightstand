# M1 Library Browser — Design Spec

**Date:** 2026-05-14
**Status:** Approved

---

## Decisions log

- **Single load:** all ~300 books fetched once on mount, filtering done in-browser. No server-side pagination.
- **Both views:** table and grid, toggled top-right, preference persisted in `localStorage`.
- **Slide-in detail panel:** opens from the right, list stays visible.
- **Filter mode:** OR by default, AND/OR toggle in the sidebar. Tag/language filters combine with AND between categories (search AND tags AND language).
- **Lazy cover loading:** `loading="lazy"` on all `<img>` tags, browser handles it.
- **Metadata extras:** embedded in `/library/books/{id}` response, not a separate endpoint. Reads `~/.config/calibre_helper/metadata.json` if present; silent fallback to empty if absent or book not found.
- **Calibre locked error:** structured JSON response, not a 500. Shown as a top banner in the UI.

---

## Backend

### New functions in `backend/nightstand/services/calibre.py`

```python
def list_books(library_path: str) -> list[dict]: ...
def get_book(library_path: str, book_id: int) -> dict | None: ...
def get_tags(library_path: str) -> list[str]: ...
def read_metadata_extras(book_title: str, book_authors: list[str]) -> dict: ...
```

- `list_books`: shells `calibredb list --for-machine --fields id,title,authors,tags,series,series_index,languages,pubdate,formats`. Returns full list.
- `get_book`: shells `calibredb list --for-machine --search "id:<id>" --fields id,title,authors,tags,series,series_index,languages,pubdate,comments,formats`. Returns one dict or `None`.
- `get_tags`: shells `calibredb list --for-machine --fields tags`, flattens and deduplicates tag arrays. Returns sorted list.
- `read_metadata_extras`: reads `~/.config/calibre_helper/metadata.json`, looks up by case-insensitive exact match on normalized title + first author. Returns `{"subgenres": [...], "themes": [...]}` or `{}` if not found or file absent.

All functions pass `env=_clean_env()`. `CalibreLockedError` propagates to callers.

### New file `backend/nightstand/api/library.py`

FastAPI router with prefix `/library`:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/books` | Returns full book list from `list_books()`. No query params used server-side — filtering is in-browser. |
| `GET` | `/books/{book_id}` | Returns full metadata from `get_book()` + extras from `read_metadata_extras()`. Returns 404 if book not found. |
| `GET` | `/books/{book_id}/cover` | Reads cover path from `calibredb get_metadata`, streams file via `FileResponse`. Returns 404 if no cover. |
| `GET` | `/tags` | Returns deduplicated tag list from `get_tags()`. |

`CalibreLockedError` on any endpoint returns `{"error": "calibre_locked", "message": "..."}` with HTTP 423.

### `backend/nightstand/main.py`

Register the library router:
```python
from nightstand.api import library
app.include_router(library.router)
```

---

## Frontend

### File structure

```
frontend/src/
├── routes/
│   └── +page.svelte
├── lib/
│   ├── store/
│   │   └── library.ts
│   ├── components/
│   │   ├── FilterSidebar.svelte
│   │   ├── BookTable.svelte
│   │   ├── BookGrid.svelte
│   │   ├── BookRow.svelte
│   │   ├── BookCard.svelte
│   │   └── BookDetail.svelte
│   └── types.ts
```

### `lib/types.ts`

```typescript
export interface Book {
  id: number;
  title: string;
  authors: string[];
  tags: string[];
  series: string | null;
  series_index: number | null;
  languages: string[];
  pubdate: string | null;
  formats: string[];  // format names only e.g. ["EPUB", "MOBI"]
}

export interface BookDetail extends Book {
  comments: string | null;
  extras: { subgenres: string[]; themes: string[] };
}

export interface Filters {
  search: string;
  tags: string[];
  languages: string[];
  tagMode: 'AND' | 'OR';
}
```

### `lib/store/library.ts`

Writable stores:
- `books: Writable<Book[]>` — full unfiltered list
- `tags: Writable<string[]>` — all distinct tags
- `filters: Writable<Filters>` — current filter state
- `viewMode: Writable<'table' | 'grid'>` — initialized from `localStorage`, writes back on change
- `selectedBookId: Writable<number | null>`
- `loading: Writable<boolean>`
- `error: Writable<string | null>`

Derived store:
- `filteredBooks: Readable<Book[]>` — derived from `books` + `filters`

Filter logic:
1. Search: case-insensitive substring on `title` + joined `authors`
2. Tag filter: if `tagMode === 'OR'`, book must have at least one selected tag; if `AND`, book must have all selected tags
3. Language filter: book must have at least one selected language (always OR)
4. All three conditions combine with AND

### `+page.svelte`

On mount:
1. Call `invoke("get_backend_port")` to get port
2. `Promise.all([fetch(/library/books), fetch(/library/tags)])` — write results into stores
3. On `CalibreLockedError` (HTTP 423): set `error` store → banner shown

Renders: `FilterSidebar` | main area (`BookTable` or `BookGrid` based on `viewMode`) + `BookDetail` slide-in. View toggle button top-right of main area.

### `FilterSidebar.svelte`

- Search input (binds to `filters.search`)
- Tag chips: all tags from store, highlighted if in `filters.tags`, click to toggle
- Language chips: same pattern
- AND/OR toggle: small segmented control below tag chips, binds to `filters.tagMode`
- "Clear filters" button

### `BookTable.svelte` / `BookGrid.svelte`

Both consume `filteredBooks`. Switching views preserves filter state and selected book.

**Table row** (`BookRow.svelte`): 48px cover thumbnail (`loading="lazy"`), title, author(s), year (first 4 chars of `pubdate` ISO string), tag pills, format badges (EPUB/MOBI/… — format name only, not path). Click → set `selectedBookId`.

**Grid card** (`BookCard.svelte`): cover image (~200px wide, `loading="lazy"`), title, author below. Click → set `selectedBookId`.

Cover `src`: `http://localhost:{port}/library/books/{id}/cover`. Placeholder: grey rectangle with a book icon, shown while loading and if cover returns 404.

### `BookDetail.svelte`

Reactive on `selectedBookId`. When non-null:
- Fetches `GET /library/books/{selectedBookId}` (full metadata + extras)
- Slides in from the right (CSS transform transition)
- Shows: large cover, title, author(s), series + index, year, language, tags, format list, comments (if any), extras (subgenres + themes as chips, section hidden if empty)
- Placeholder "Edit" button (disabled, labelled "Coming in M2")
- Close button sets `selectedBookId` to null

On Calibre locked error: shows error message inside panel, does not crash the list.

---

## Error states

| Situation | UI behaviour |
|-----------|-------------|
| `/library/books` fails (locked) | Top banner: "Calibre is open — close it and refresh." Retry button. |
| `/library/books` fails (other) | Full-page error with message + retry button. |
| Book has no cover | Placeholder shown (grey rect + book icon). No broken image. |
| Book detail fetch fails | Error message inside slide-in panel. List unaffected. |
| `metadata.json` absent / book not in it | Extras section hidden. No error. |

---

## Out of scope

- Any Calibre writes
- Inline editing (placeholder button only)
- Nightstand sidecar SQLite DB
- Theming / Omarchy palette
- Tests (added before M2 per AGENTS.md open items)

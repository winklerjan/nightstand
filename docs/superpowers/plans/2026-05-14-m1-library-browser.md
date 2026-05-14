# M1 Library Browser Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the read-only M1 Calibre library browser with list/detail API endpoints and a Svelte table/grid UI.

**Architecture:** The Python sidecar remains the only layer that calls `calibredb`; every Calibre subprocess call uses `_clean_env()` and read-only commands. The frontend gets the sidecar port through Tauri `invoke("get_backend_port")`, fetches `http://localhost:<port>/library/*`, stores the full library in Svelte stores, and filters in-browser.

**Tech Stack:** Python 3.12, FastAPI, `calibredb`, Svelte 5, SvelteKit SPA, Tauri 2, TypeScript strict mode.

---

## File Structure

- Modify `backend/nightstand/services/calibre.py`: add read-only Calibre helpers for listing books, fetching one book, reading tags, cover metadata, and optional metadata extras.
- Create `backend/nightstand/api/library.py`: FastAPI router for `/library/books`, `/library/books/{book_id}`, `/library/books/{book_id}/cover`, and `/library/tags`.
- Modify `backend/nightstand/main.py`: register the library router.
- Create `frontend/src/lib/types.ts`: shared frontend types for books, details, filters, and view mode.
- Create `frontend/src/lib/store/library.ts`: Svelte stores, filtering logic, and `localStorage` view-mode persistence.
- Create `frontend/src/lib/components/FilterSidebar.svelte`: search, tag chips, language chips, AND/OR toggle, clear filters.
- Create `frontend/src/lib/components/BookRow.svelte`: table row for one book.
- Create `frontend/src/lib/components/BookTable.svelte`: filtered table view.
- Create `frontend/src/lib/components/BookCard.svelte`: grid card for one book.
- Create `frontend/src/lib/components/BookGrid.svelte`: filtered grid view.
- Create `frontend/src/lib/components/BookDetail.svelte`: slide-in detail panel with full metadata and disabled M2 edit affordance.
- Replace `frontend/src/routes/+page.svelte`: load backend data and compose the M1 shell.

## Constraints

- Do not add any Calibre write command. Allowed Calibre commands are `calibredb list` and `calibredb get_metadata`.
- Do not log or render raw library paths, book file paths, or user filesystem data.
- Frontend fetch URLs must use `http://localhost`, not `http://127.0.0.1`.
- Keep `src-tauri/` unchanged for M1.
- Existing untracked repo-local Codex plugin files are unrelated to M1 and should not be mixed into M1 commits unless the user explicitly asks.

---

### Task 1: Backend Calibre Service Helpers

**Files:**
- Modify: `backend/nightstand/services/calibre.py`

- [ ] **Step 1: Add service helper imports**

Add these imports near the top of `backend/nightstand/services/calibre.py`:

```python
from pathlib import Path
from typing import Any
```

- [ ] **Step 2: Add shared Calibre execution helper**

Add this function after `CalibreLockedError`:

```python
def _run_calibredb(args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["calibredb", *args],
        capture_output=True,
        text=True,
        env=_clean_env(),
    )
    if result.returncode != 0:
        if "Another calibre program" in result.stderr:
            raise CalibreLockedError("Calibre GUI is open - close it and retry.")
        raise RuntimeError(result.stderr.strip() or "calibredb command failed")
    return result
```

- [ ] **Step 3: Update `list_first()` to use `_run_calibredb()`**

Replace the body of `list_first()` with:

```python
def list_first(library_path: str) -> dict:
    result = _run_calibredb(
        [
            "list",
            "--library-path",
            library_path,
            "--limit",
            "1",
            "--fields",
            "title,authors",
            "--for-machine",
        ]
    )
    books = json.loads(result.stdout)
    return books[0] if books else {}
```

- [ ] **Step 4: Add normalization helpers**

Add these functions below `list_first()`:

```python
def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(value)]


def _normalize_book(book: dict[str, Any]) -> dict[str, Any]:
    formats = _as_list(book.get("formats"))
    return {
        "id": int(book["id"]),
        "title": str(book.get("title") or ""),
        "authors": _as_list(book.get("authors")),
        "tags": _as_list(book.get("tags")),
        "series": book.get("series"),
        "series_index": book.get("series_index"),
        "languages": _as_list(book.get("languages")),
        "pubdate": book.get("pubdate"),
        "formats": [Path(format_path).suffix.lstrip(".").upper() for format_path in formats],
    }


def _normalize_lookup(value: str) -> str:
    return " ".join(value.casefold().split())
```

- [ ] **Step 5: Add `list_books()`**

Add:

```python
def list_books(library_path: str) -> list[dict[str, Any]]:
    result = _run_calibredb(
        [
            "list",
            "--library-path",
            library_path,
            "--for-machine",
            "--fields",
            "id,title,authors,tags,series,series_index,languages,pubdate,formats",
        ]
    )
    books = json.loads(result.stdout)
    return [_normalize_book(book) for book in books]
```

- [ ] **Step 6: Add `get_book()`**

Add:

```python
def get_book(library_path: str, book_id: int) -> dict[str, Any] | None:
    result = _run_calibredb(
        [
            "list",
            "--library-path",
            library_path,
            "--for-machine",
            "--search",
            f"id:{book_id}",
            "--fields",
            "id,title,authors,tags,series,series_index,languages,pubdate,comments,formats",
        ]
    )
    books = json.loads(result.stdout)
    if not books:
        return None
    book = _normalize_book(books[0])
    book["comments"] = books[0].get("comments")
    return book
```

- [ ] **Step 7: Add `get_tags()`**

Add:

```python
def get_tags(library_path: str) -> list[str]:
    result = _run_calibredb(
        [
            "list",
            "--library-path",
            library_path,
            "--for-machine",
            "--fields",
            "tags",
        ]
    )
    books = json.loads(result.stdout)
    tags = {tag for book in books for tag in _as_list(book.get("tags"))}
    return sorted(tags, key=str.casefold)
```

- [ ] **Step 8: Add metadata extras reader**

Add:

```python
def read_metadata_extras(book_title: str, book_authors: list[str]) -> dict[str, list[str]]:
    metadata_path = Path.home() / ".config" / "calibre_helper" / "metadata.json"
    if not metadata_path.exists():
        return {}

    try:
        raw_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    first_author = book_authors[0] if book_authors else ""
    wanted_title = _normalize_lookup(book_title)
    wanted_author = _normalize_lookup(first_author)

    records = raw_metadata if isinstance(raw_metadata, list) else raw_metadata.values()
    for record in records:
        if not isinstance(record, dict):
            continue
        title = _normalize_lookup(str(record.get("title") or ""))
        authors = _as_list(record.get("authors") or record.get("author"))
        author = _normalize_lookup(authors[0]) if authors else ""
        if title == wanted_title and author == wanted_author:
            return {
                "subgenres": _as_list(record.get("subgenres")),
                "themes": _as_list(record.get("themes")),
            }
    return {}
```

- [ ] **Step 9: Add cover path reader**

Add:

```python
def get_cover_path(library_path: str, book_id: int) -> Path | None:
    result = _run_calibredb(
        [
            "get_metadata",
            "--library-path",
            library_path,
            "--for-machine",
            str(book_id),
        ]
    )
    metadata = json.loads(result.stdout)
    cover = metadata.get("cover")
    if not cover:
        return None
    cover_path = Path(str(cover))
    if not cover_path.is_file():
        return None
    return cover_path
```

- [ ] **Step 10: Verify backend imports**

Run:

```bash
cd backend && uv run python -m compileall nightstand
```

Expected: no syntax errors.

- [ ] **Step 11: Commit service helpers**

```bash
git add backend/nightstand/services/calibre.py
git commit -m "feat: add read-only calibre library helpers"
```

---

### Task 2: Backend Library API Router

**Files:**
- Create: `backend/nightstand/api/library.py`
- Modify: `backend/nightstand/main.py`

- [ ] **Step 1: Create the library router**

Create `backend/nightstand/api/library.py`:

```python
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from nightstand.services import calibre
from nightstand.services.calibre import CalibreLockedError

router = APIRouter(prefix="/library")


def _library_path() -> str:
    return os.environ.get(
        "NIGHTSTAND_CALIBRE_LIBRARY", os.path.expanduser("~/Calibre Library")
    )


def _locked_response(error: CalibreLockedError) -> JSONResponse:
    return JSONResponse(
        status_code=423,
        content={"error": "calibre_locked", "message": str(error)},
    )


@router.get("/books")
def books() -> list[dict[str, Any]] | JSONResponse:
    try:
        return calibre.list_books(_library_path())
    except CalibreLockedError as error:
        return _locked_response(error)


@router.get("/books/{book_id}")
def book(book_id: int) -> dict[str, Any] | JSONResponse:
    try:
        found = calibre.get_book(_library_path(), book_id)
    except CalibreLockedError as error:
        return _locked_response(error)
    if found is None:
        raise HTTPException(status_code=404, detail="Book not found")
    found["extras"] = calibre.read_metadata_extras(found["title"], found["authors"])
    return found


@router.get("/books/{book_id}/cover")
def cover(book_id: int) -> FileResponse | JSONResponse:
    try:
        cover_path = calibre.get_cover_path(_library_path(), book_id)
    except CalibreLockedError as error:
        return _locked_response(error)
    if cover_path is None:
        raise HTTPException(status_code=404, detail="Cover not found")
    return FileResponse(Path(cover_path))


@router.get("/tags")
def tags() -> list[str] | JSONResponse:
    try:
        return calibre.get_tags(_library_path())
    except CalibreLockedError as error:
        return _locked_response(error)
```

- [ ] **Step 2: Register the router**

Modify `backend/nightstand/main.py` imports:

```python
from nightstand.api import library
```

Then add this after CORS setup:

```python
app.include_router(library.router)
```

- [ ] **Step 3: Verify backend imports**

Run:

```bash
cd backend && uv run python -m compileall nightstand
```

Expected: no syntax errors.

- [ ] **Step 4: Manually verify API startup**

Run:

```bash
cd backend && uv run python -m nightstand.main --port 8765
```

Expected: stdout prints `NIGHTSTAND_PORT=8765` and the server stays running.

In a second terminal, run:

```bash
curl -i http://localhost:8765/library/tags
```

Expected: `HTTP/1.1 200 OK` with a JSON array, or `HTTP/1.1 423 Locked` with `{"error":"calibre_locked",...}` if Calibre GUI is open.

- [ ] **Step 5: Commit router**

```bash
git add backend/nightstand/api/library.py backend/nightstand/main.py
git commit -m "feat: expose read-only library api"
```

---

### Task 3: Frontend Types and Stores

**Files:**
- Create: `frontend/src/lib/types.ts`
- Create: `frontend/src/lib/store/library.ts`

- [ ] **Step 1: Create frontend types**

Create `frontend/src/lib/types.ts`:

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
  formats: string[];
}

export interface BookDetail extends Book {
  comments: string | null;
  extras: {
    subgenres: string[];
    themes: string[];
  };
}

export interface Filters {
  search: string;
  tags: string[];
  languages: string[];
  tagMode: "AND" | "OR";
}

export type ViewMode = "table" | "grid";
```

- [ ] **Step 2: Create library stores**

Create `frontend/src/lib/store/library.ts`:

```typescript
import { derived, writable } from "svelte/store";
import type { Book, Filters, ViewMode } from "$lib/types";

const defaultFilters: Filters = {
  search: "",
  tags: [],
  languages: [],
  tagMode: "OR",
};

const initialViewMode = (): ViewMode => {
  if (typeof localStorage === "undefined") return "table";
  return localStorage.getItem("nightstand:viewMode") === "grid" ? "grid" : "table";
};

export const books = writable<Book[]>([]);
export const tags = writable<string[]>([]);
export const filters = writable<Filters>({ ...defaultFilters });
export const viewMode = writable<ViewMode>(initialViewMode());
export const selectedBookId = writable<number | null>(null);
export const loading = writable<boolean>(true);
export const error = writable<string | null>(null);
export const backendBase = writable<string | null>(null);

if (typeof localStorage !== "undefined") {
  viewMode.subscribe((value) => {
    localStorage.setItem("nightstand:viewMode", value);
  });
}

export const languages = derived(books, ($books) => {
  const values = new Set<string>();
  for (const book of $books) {
    for (const language of book.languages) values.add(language);
  }
  return [...values].sort((a, b) => a.localeCompare(b));
});

export const filteredBooks = derived([books, filters], ([$books, $filters]) => {
  const query = $filters.search.trim().toLocaleLowerCase();
  return $books.filter((book) => {
    const haystack = `${book.title} ${book.authors.join(" ")}`.toLocaleLowerCase();
    const matchesSearch = query === "" || haystack.includes(query);
    const matchesTags =
      $filters.tags.length === 0 ||
      ($filters.tagMode === "AND"
        ? $filters.tags.every((tag) => book.tags.includes(tag))
        : $filters.tags.some((tag) => book.tags.includes(tag)));
    const matchesLanguages =
      $filters.languages.length === 0 ||
      $filters.languages.some((language) => book.languages.includes(language));
    return matchesSearch && matchesTags && matchesLanguages;
  });
});

export const resetFilters = (): void => {
  filters.set({ ...defaultFilters });
};
```

- [ ] **Step 3: Verify frontend types**

Run:

```bash
pnpm --filter frontend check
```

Expected: check passes or fails only because components are not created yet if imports were added early.

- [ ] **Step 4: Commit stores**

```bash
git add frontend/src/lib/types.ts frontend/src/lib/store/library.ts
git commit -m "feat: add library frontend stores"
```

---

### Task 4: Frontend List and Filter Components

**Files:**
- Create: `frontend/src/lib/components/FilterSidebar.svelte`
- Create: `frontend/src/lib/components/BookRow.svelte`
- Create: `frontend/src/lib/components/BookTable.svelte`
- Create: `frontend/src/lib/components/BookCard.svelte`
- Create: `frontend/src/lib/components/BookGrid.svelte`

- [ ] **Step 1: Create `FilterSidebar.svelte`**

Create controls bound to `filters`, `tags`, and `languages`. Chip buttons toggle array membership, the segmented control switches `tagMode`, and the clear button calls `resetFilters()`.

- [ ] **Step 2: Create row/card components**

Create `BookRow.svelte` and `BookCard.svelte` with props:

```typescript
import type { Book } from "$lib/types";

interface Props {
  book: Book;
  base: string;
}

let { book, base }: Props = $props();
```

Both components use `src={`${base}/library/books/${book.id}/cover`}`, `loading="lazy"`, and set `selectedBookId` on click. On image error, hide the image and show a styled placeholder.

- [ ] **Step 3: Create list containers**

Create `BookTable.svelte` and `BookGrid.svelte` that consume `filteredBooks` and `backendBase`, then render rows/cards. If `backendBase` is null or there are no results, render a compact empty state.

- [ ] **Step 4: Verify frontend**

Run:

```bash
pnpm --filter frontend check
```

Expected: Svelte check passes.

- [ ] **Step 5: Commit list UI**

```bash
git add frontend/src/lib/components/FilterSidebar.svelte frontend/src/lib/components/BookRow.svelte frontend/src/lib/components/BookTable.svelte frontend/src/lib/components/BookCard.svelte frontend/src/lib/components/BookGrid.svelte
git commit -m "feat: add library list views"
```

---

### Task 5: Frontend Detail Panel and Page Shell

**Files:**
- Create: `frontend/src/lib/components/BookDetail.svelte`
- Modify: `frontend/src/routes/+page.svelte`

- [ ] **Step 1: Create `BookDetail.svelte`**

Create a slide-in panel that subscribes to `selectedBookId` and `backendBase`. When a book is selected, fetch `${base}/library/books/${id}`. Render cover, title, authors, series, year, languages, tags, formats, comments, extras chips, a disabled `Edit` button labelled `Coming in M2`, and a close button that sets `selectedBookId` to null. If the detail fetch returns `423`, show `Calibre is open - close it and retry.` inside the panel.

- [ ] **Step 2: Replace `+page.svelte`**

Replace the M0 status cards with the library shell:

- `onMount` invokes `get_backend_port`
- sets `backendBase` to `http://localhost:${port}`
- fetches `/library/books` and `/library/tags` with `Promise.all`
- handles `423` as the top banner message `Calibre is open - close it and refresh.`
- renders `FilterSidebar`, a main toolbar with table/grid toggle, the selected view, and `BookDetail`
- provides a retry button that reruns the load

- [ ] **Step 3: Verify frontend**

Run:

```bash
pnpm --filter frontend check
```

Expected: Svelte check passes.

- [ ] **Step 4: Commit shell**

```bash
git add frontend/src/lib/components/BookDetail.svelte frontend/src/routes/+page.svelte
git commit -m "feat: build m1 library browser shell"
```

---

### Task 6: End-to-End Verification and Handoff

**Files:**
- Modify: `docs/current-state.md`
- Modify: `docs/next-task.md`
- Modify: `docs/progress.md`
- Modify: `baton-pass.state.json`

- [ ] **Step 1: Run backend verification**

Run:

```bash
cd backend && uv run python -m compileall nightstand
```

Expected: no syntax errors.

- [ ] **Step 2: Run frontend verification**

Run:

```bash
pnpm --filter frontend check
```

Expected: check passes.

- [ ] **Step 3: Run the app**

Run:

```bash
pnpm dev
```

Expected: Tauri launches, the sidecar prints a `NIGHTSTAND_PORT=...` line, and the UI loads the M1 browser or shows a Calibre lock banner.

- [ ] **Step 4: Manual browser checks**

Verify:

- table/grid toggle works and persists after reload
- search filters by title and author
- tag OR mode matches books with any selected tag
- tag AND mode matches books with all selected tags
- language chips filter books
- clicking a book opens the detail panel
- missing cover shows placeholder, not a broken image
- no raw file paths are visible in the UI

- [ ] **Step 5: Update Baton Pass state**

Update handoff docs with:

- M1 implementation status
- files changed
- verification status using `passed` only for commands that actually ran cleanly
- remaining risks or blockers
- next task

- [ ] **Step 6: Commit handoff docs**

```bash
git add baton-pass.state.json docs/current-state.md docs/next-task.md docs/progress.md
git commit -m "chore: baton-pass m1 implementation handoff"
```

---

## Self-Review

- Spec coverage: backend books, detail, cover, tags, locked handling, frontend filters, table/grid views, detail panel, lazy covers, placeholders, extras, and no Calibre writes are all covered.
- Placeholder scan: no `TBD`, `TODO`, or open-ended "add appropriate" instructions remain.
- Type consistency: backend returns `series_index`, `pubdate`, `formats`, and `extras`; frontend types and components use those same names.

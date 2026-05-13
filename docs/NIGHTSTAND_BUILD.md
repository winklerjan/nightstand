# Nightstand — Build Brief

A friendlier Calibre. Local-first GUI on top of the Calibre CLI toolchain, with the workflows Calibre is bad at (rich metadata fetch, multi-source cover picker, libgen/Anna's Archive search, automated text cleanup, Kindle/KOReader sync) built in.

**This document is a starting point, not a finished spec.** Iterate with the user constantly. Ask before guessing. Keep the dialogue going.

---

## 0. Who this is for

- Primary user (Jan): personal Calibre library, Kindle Paperwhite running KOReader, bilingual (Czech/English), tagging conventions documented in `~/CLAUDE.md`.
- Eventual public users: anyone with a Calibre install who wants a nicer UI. Will be published to **GitHub Releases + AUR** (Arch) and **PyPI** (`pipx install nightstand`) eventually.
- **Therefore: nothing hardcoded to Jan's setup.** All paths, tag vocabularies, language pairs, sync targets are config. Jan's current values become *defaults* in a first-run wizard, not constants in code.

---

## 1. Stack

Nightstand is a **desktop app**: native window, taskbar entry, own icon, no browser involved. The UI inside the window is web tech (because cover grids, diff views, and theming are dramatically easier in HTML/CSS than in any native toolkit). The whole thing ships as a **single binary**.

- **Shell:** [Tauri 2](https://tauri.app/) — Rust-based native window host. Produces a single binary, ~10–30 MB, with built-in auto-updater, native menus, and tray support.
- **Frontend:** SvelteKit (or React — confirm with user). Built to static assets, embedded in the Tauri binary.
- **Backend:** Python 3.12 + FastAPI, run as a **Tauri sidecar** — Tauri spawns the Python process on launch, talks to it over localhost HTTP, kills it on exit. Python is bundled via **PyInstaller** as a standalone executable that Tauri embeds.
- **Database:** SQLite (sidecar Nightstand metadata, never replaces Calibre's DB).
- **Calibre integration:** shell out to `calibredb`, `ebook-convert`, `ebook-meta`, `ebook-edit`, `ebook-polish`. Never link to Calibre Python internals — they break across versions. Calibre stays an **external runtime dep** (declared in the AUR PKGBUILD; documented as a prerequisite for tarball installs).
- **Theming:** the Tauri window is transparent-capable and Wayland-native. Default theme will follow Omarchy's current palette (read CSS vars at runtime from a small theme config); user can swap themes via Settings.

### Why Tauri over alternatives

| Option | Verdict |
|---|---|
| **Tauri + Python sidecar** ✅ | Real single binary, ~10–30 MB, native window, auto-update built in. Adds Rust to the build chain but the agent handles that. Best long-term distribution story. |
| **Electron + Python sidecar** | Same shape but 100+ MB binaries and heavier RAM use. Not worth it. |
| **PyInstaller + pywebview** | Simpler mental model (pure Python) but binaries are 100+ MB and slower to start; no built-in updater. |
| **Pure Python desktop (PySide6)** | No web UI tech — loses the cover picker / diff-view ergonomics that motivated the design. |

### Process model at runtime

1. User launches `nightstand` (binary, `.desktop` entry, or AUR-installed command).
2. Tauri opens a native window and spawns the Python sidecar on a random local port.
3. Sidecar exposes the FastAPI surface; frontend talks to it over `http://127.0.0.1:<port>`.
4. On window close, Tauri sends SIGTERM to the sidecar.

### Existing code to reuse

Located on the user's machine (read before touching):

- `~/import_books.py` — current import script. Lift `sanitize()`, `make_filename()`, `to_last_first()`, `extract_metadata()`, `convert_to_epub()`, `lookup_first_year()`, `calibre_search_dupes()`, `calibre_add()`, `calibre_set_metadata()`.
- `/home/jan/calibre_import_spec.md` — the most recent design for the import flow, including the `metadata.json` subgenre/promotion mechanism. **Read this first.** Nightstand's import flow should match its semantics; the spec just becomes a service module instead of a standalone script.
- `/home/jan/migrate_calibre_library.py` — bulk migration logic. Becomes Nightstand's "Library Maintenance" feature.
- `/home/jan/kindle_setup_instructions.md` — Kindle/KOReader paths and conventions.

---

## 2. Architecture

```
nightstand/
├── src-tauri/            Tauri (Rust) shell — window, lifecycle, sidecar spawn
│   ├── src/main.rs
│   ├── tauri.conf.json
│   └── Cargo.toml
├── frontend/             SvelteKit — built into src-tauri/ as embedded assets
│   ├── src/routes/
│   ├── src/lib/
│   └── package.json
├── backend/              Python sidecar — built by PyInstaller into a single exe
│   ├── nightstand/
│   │   ├── api/          FastAPI routes
│   │   ├── services/
│   │   │   ├── calibre.py    calibredb / ebook-convert wrappers
│   │   │   ├── metadata.py   Open Library, Google Books, Anthropic
│   │   │   ├── covers.py     candidate fetching + Sonnet vision
│   │   │   ├── search.py     libgen / Anna's Archive / Z-library
│   │   │   ├── cleanup.py    text-cleanup pipeline (regex + heuristics, LLM later)
│   │   │   ├── sync.py       Kindle / KOReader sync
│   │   │   └── config.py     user config + first-run wizard state
│   │   ├── db.py             SQLite (sidecar Nightstand DB)
│   │   └── main.py           FastAPI entrypoint
│   └── pyproject.toml
├── tests/
└── packaging/
    ├── aur/PKGBUILD
    ├── github-actions/   build matrix for Linux x86_64 (+ arm64 later)
    └── install.sh
```

**Calibre database:** Nightstand reads/writes the user's existing Calibre library via `calibredb`. It never opens `metadata.db` directly. **Calibre GUI must be closed** during writes — show a clear modal if a write fails with the "database is locked, another Calibre process is running" error.

**Nightstand's sidecar DB** (`~/.local/share/nightstand/nightstand.db`) stores:
- Per-book extras (subgenres, themes, cleanup history, AI-call audit trail, cover-decision log)
- Search/import session history
- API cost ledger
- LLM response cache (keyed by `sha1(title+author)`, 30-day TTL)

The mapping is `calibre_id ↔ nightstand row`. If a book is deleted from Calibre, its row is kept (soft-tombstoned) so cost/audit history survives.

---

## 3. Feature list (v1)

Group features into milestones. Build → demo to user → iterate before moving on.

### M1 — Library browser
- List view of the Calibre library (read via `calibredb list`).
- Filters: tag, language, series, has-cover, format, read/unread (if Calibre column exists).
- Per-book detail panel: cover, metadata, file paths, tags, series info, Nightstand extras (subgenres/themes from sidecar).
- Inline edit of title/author/tags/series. Writes via `calibredb set_metadata`. **Never** `embed_metadata`.

### M2 — Smart import (replaces `import_books.py`)
- Configurable scan directories (default: `~/Downloads`).
- Drag-drop zone in the UI.
- Per-book wizard implementing `calibre_import_spec.md` §6–§9:
  - Metadata normalization via Haiku
  - First-pub year via Open Library → Haiku fallback
  - Cover quality check via Sonnet vision--definable by user in the settings. Possibility to use the program without any AI agents must be kept. 
- Cover picker UI: grid of candidates from Google Books + Open Library, current cover highlighted, click to select, "fetch more" button. AI recommendation visible but overridable.
- Confirmation card: shows projected tags, series, cost. Edit → save → import.
- Skip-PDF behavior is opt-in via config, not hardcoded.

### M3 — Format conversion
- "Convert to…" action per book or batch. Shells `ebook-convert` with a sensible default profile (`--subset-embedded-fonts`, `--enable-heuristics` toggleable).
- Convert-and-replace vs. convert-and-add-as-new toggle.
- Progress + log stream in UI.

### M4 — Text cleanup (v1: heuristics only)
- Per-book "Clean up text" action.
- v1 pipeline:
  1. `ebook-convert input.epub cleaned.epub --enable-heuristics --markup-chapter-headings --unwrap-lines --delete-blank-paragraphs --format-scene-breaks`
  2. Optional `ebook-polish --smarten-punctuation --subset-fonts --embed-fonts`
  3. Show before/after preview (Monaco/CodeMirror diff of HTML or rendered preview pane)
  4. User accepts → replaces original; rejects → discards
- v2 (later, separate brief): LLM-tagged structure pass for hard cases. Designed in `calibre_import_spec.md`-style; do **not** start until v1 is solid.

### M5 — Online search (libgen / Anna's Archive)
- Search bar with source selector (Anna's Archive primary; libgen + Z-library fallbacks).
- Results table: title, author, year, language, format, size, score.
- Click → fetch → drop into the import flow at M2.
- **Expect scrapers to break.** Encapsulate each source behind a `Source` interface and ship integration tests with VCR cassettes so breakage is loud.

### M6 — Kindle / KOReader sync
- Configurable device profiles (path on mount, filename formula, folder layout). Jan's flat-by-tags default ships as one profile; a Calibre-classic "by author" layout ships as another.
- "Send to device" (or ideally "Sync") button: copies, updates KOReader collections if profile says so, regenerates `collection.lua` (port from `~/gen_collections.py`).
- Detects mounted devices via `udisksctl` or polling common mount points. Manual path override always available.
- Keeps data synced with the device. If possible, on Sync only updates whatever has been changed in Nightstand. We want device to mirror the local computer library, unlike in Calibre which is used way more flexibly.

### M7 — Library maintenance
- Bulk operations: re-project tags from `nightstand.db` (the `--reproject` future-work from the import spec), prune unused tags, recompute filenames, batch cover refresh.
- Port `migrate_calibre_library.py` as a guided wizard with dry-run preview.

### M8 — Settings & first-run wizard
- Detects Calibre install, asks for library path.
- Asks for Anthropic API key (env var or `~/.config/nightstand/key`).
- Tag vocabulary editor (defaults seeded but editable — no hardcoded "sci-fi/fantasy/chess" list in code).
- Cover aesthetic prompt editor (Jan's "minimalist, designer feel with illustrations (no photos whenever possible) and good typography" preference is a default, not a constant).
- Language list editor (defaults `en`; Jan adds `cs`).
- Device sync profiles.

---

## 4. Cross-cutting concerns

- **No hardcoded paths.** Everything from `XDG_*` and user config.
- **Cost ledger.** Every Anthropic call is logged with model, tokens, USD cost. UI shows running total per session and lifetime. Pricing table is a module constant; bump it when models change.
- **LLM response cache.** Keyed by content hash; respected unless user clicks "re-run AI".
- **Audit trail.** Every write to Calibre goes through one `CalibreWriter` class that logs the command, args, stdout/stderr, and the diff it intended. Makes debugging "where did this tag come from" trivial.
- **No `calibredb embed_metadata`. Ever.** Enforce in `CalibreWriter`. Document why (renames files back to Calibre's internal form).
- **Calibre GUI lock detection.** Friendly modal, not a stack trace.
- **i18n-ready.** Don't translate v1, but route all user-visible strings through a single module so future translation is trivial.

---

## 5. Packaging & distribution

**Build pipeline (GitHub Actions, runs on tag push):**

1. `npm run build` in `frontend/` → static assets
2. `pyinstaller --onefile backend/nightstand/main.py` → `nightstand-backend` single executable
3. Place backend exe in `src-tauri/binaries/nightstand-backend-<target-triple>` (Tauri sidecar convention)
4. `tauri build` → produces:
   - Single-file Linux binary (`nightstand`)
   - `.deb` and `.rpm` bundles
   - AppImage (cross-distro portable)
5. Generate AUR `PKGBUILD` and `.SRCINFO`, push to AUR repo
6. Attach all artifacts to the GitHub Release

**AUR PKGBUILD** declares `calibre` as a runtime dep; installs the prebuilt binary to `/usr/bin/nightstand`, a `.desktop` file to `/usr/share/applications/`, and an icon. No Python interpreter needed on the user's machine — it's embedded in the binary.

**Other distros:** AppImage from the release page, or the install script which fetches the binary and drops the `.desktop` file.

**Auto-updater:** Tauri's built-in updater checks GitHub Releases, opt-in via Settings.

**README:** screenshots, quickstart, contributor guide. Mention Calibre as a hard prerequisite.

---

## 6. Working agreement with the user

This brief is a **first draft**. The user explicitly wants iteration. Before writing meaningful code:

1. **Confirm the stack** (Python + FastAPI + SvelteKit/React). User mentioned sharing — confirm packaging targets (AUR + PyPI + GitHub Releases).
2. **Walk the feature list together.** Cut anything that doesn't excite the user, add anything missing. Sequence the milestones in the order the user wants to *see things working*, not the order that's architecturally clean.
3. **Pick M1 scope and design it in detail** before any code is written. Sketch the screen, agree on the API endpoints, then implement.
4. **Demo at the end of every milestone.** Don't batch.
5. **Ask before introducing new dependencies, new abstractions, or features not in this doc.**

Questions to raise in the first dialogue session:

- Frontend framework: SvelteKit vs React? (Recommendation: SvelteKit — smaller, faster to iterate.)
- Should Nightstand assume Calibre is installed, or offer a "Calibre-less mode" later? (Recommendation: assume Calibre installed for v1.)
- Should the AI features be optional? (Recommendation: yes — degrade gracefully without an API key; library browse/import/convert/sync still work.)
- Tag/genre vocabulary — ship a default vocabulary, or always make the user define theirs on first run? (Recommendation: ship a small default, mark it editable.)
- Telemetry/analytics: anything? (Recommendation: none. Local-first means local-only.)
- Theming: follow Omarchy palette automatically, or own theme system from day one? (Recommendation: own theme system with an Omarchy-matching default + light/dark variants.)
- Platforms: Linux-only for v1, or keep macOS/Windows builds in the GitHub Actions matrix as a stretch goal? (Recommendation: Linux-only for v1 to avoid Calibre-path / mount-detection branching everywhere.)

---

## 7. Out of scope for v1

- Mobile/tablet UI (works in a phone browser, but no responsive polish)
- Multi-user / multi-library
- Cloud sync of the sidecar DB
- The LLM-assisted text restructuring pass (deferred to v2 — see M4 v2 note)
- Reading the books in-browser (KOReader exists; don't compete)
- Calibre plugin system compatibility

---

## 8. Deliverable for *this* session

**Not code.** A continued conversation with the user that:
1. Confirms or revises the stack and packaging plan.
2. Walks the feature list and reorders/edits to taste.
3. Settles M1 scope to the point that the next session can start building.

Only after the user explicitly says "okay, start building M1" should any code be written.

# Nightstand — M0: Project Scaffolding

**Audience:** a Claude Sonnet agent starting a fresh implementation session for Nightstand.
**Prerequisite reading (in order, do not skip):**

1. `docs/NIGHTSTAND_BUILD.md` — the overall brief. Read it end-to-end.
2. `/home/jan/calibre_import_spec.md` — the most recent import-flow design. You will not implement this yet, but you must understand it because it dictates how `backend/services/calibre.py`, `metadata.py`, and `covers.py` should be shaped.
3. `/home/jan/import_books.py` — the current import script. Skim only — you are lifting helpers from it later, not now.
4. `/home/jan/CLAUDE.md` — Jan's Kindle + Calibre conventions.

You are working from `/home/jan/dev/code/nightstand`. Treat this directory as the project root.

---

## 0. Working agreement (read this twice)

- **You are in dialogue mode, not autopilot mode.** Constant communication with the user is the explicit expectation. Ask before guessing. Show progress in small increments.
- **No code until §2 questions are answered.** Run §1 first.
- **No new dependencies, abstractions, or files beyond what this doc specifies.** If you think something is missing, raise it with the user.
- **Demo at every checkpoint.** Each phase below ends with something the user can see/run. Stop there and wait for feedback.
- **Never run `calibredb embed_metadata`.** Burn this into your defaults.
- **Calibre GUI must be closed** for any `calibredb` write. Nightstand will eventually detect this; for now, just don't write yet.

---

## 1. Goal of M0

Get a **runnable skeleton** of the three-layer stack talking to itself:

```
[Tauri window]  ←HTTP→  [Python FastAPI sidecar]  ←shell→  [calibredb]
   (SvelteKit UI)         (spawned by Tauri)              (read-only probe)
```

Success criterion: user runs `cargo tauri dev` (or equivalent), a window opens, the UI calls a `/health` endpoint on the Python sidecar, the sidecar runs `calibredb --version` and `calibredb list --limit=1` against the user's library, and the result renders in the window. Nothing else.

**No features. No styling beyond a sensible base. No M1 logic.**

---

## 2. Open questions — ASK THE USER BEFORE WRITING CODE

The build doc lists open questions. Resolve at least these before scaffolding:

1. **Frontend framework: SvelteKit or React?**  (Recommendation: SvelteKit.)
2. **Package manager for frontend:** `pnpm` (recommended, matches the user's `~/dev/code/CLAUDE.md` RTK conventions) or `npm`?
3. **Calibre library path:** confirm `/home/jan/Calibre Library` for development, and confirm Nightstand should read it from config (not hardcoded) from day one.
4. **License:** what license should `LICENSE` carry? (MIT recommended for shareable tooling; ask.)
5. **Repo init:** `git init` here, or wait? (Recommendation: init now so progress is committable.)
6. **Python version:** confirm 3.12. The user is on Arch; check `python --version` first.
7. **Tauri 2 vs Tauri 1:** v1 doc says Tauri 2; confirm. (v2 is current GA, recommended.)

Ask these as one short, batched prompt. Do **not** start scaffolding until they are answered.

---

## 3. Phases

Each phase ends with a checkpoint. Stop and check in with the user at every "🛑 CHECKPOINT" line.

### Phase A — Repo skeleton

1. `git init`, add `.gitignore` covering Rust (`target/`), Node (`node_modules/`, `.svelte-kit/`, `dist/`, `build/`), Python (`__pycache__/`, `.venv/`, `*.pyc`, `dist/`, `build/`), and editor noise.
2. Create the directory layout from `docs/NIGHTSTAND_BUILD.md` §2 — empty for now, just the dirs and a `.gitkeep` in each leaf.
3. Add `LICENSE` and a one-paragraph `README.md` (just project name, one-line description, status: "scaffolding"). Do **not** write usage docs yet.

🛑 **CHECKPOINT A:** show the user the tree (`tree -L 3` output) and the diff. Wait for go-ahead.

### Phase B — Python sidecar

Scope: a single FastAPI app with two endpoints, runnable standalone with `uvicorn`.

1. `backend/pyproject.toml` — use `uv` (already on user's machine) and `hatchling`. Deps: `fastapi`, `uvicorn[standard]`. **No other deps yet.** No `anthropic`, no `requests`, no `ebooklib`. Those come with the features that need them.
2. `backend/nightstand/main.py` — FastAPI app, binds to `127.0.0.1`, reads port from `--port` CLI arg (default 0 = random, prints chosen port to stdout as `NIGHTSTAND_PORT=<n>` for Tauri to parse).
3. Two endpoints:
   - `GET /health` → `{"status": "ok", "version": "<from pyproject>"}`.
   - `GET /calibre/probe` → shells `calibredb --version` and `calibredb --library-path <path> list --limit 1 --fields title,authors --for-machine`. Returns `{"calibredb_version": "...", "first_book": {...}}`. The library path comes from a `NIGHTSTAND_CALIBRE_LIBRARY` env var for now; config-file-based config is a later phase.
4. One thin wrapper module `backend/nightstand/services/calibre.py` with two functions: `version()` and `list_first()`. Both shell out via `subprocess.run`, parse, return Python dicts. No abstractions, no `CalibreWriter` class yet — the doc mentions it but it's earned later when there's something to write.
5. Manual test commands documented in `backend/README.md`: how to `uv run uvicorn` it and curl both endpoints.

🛑 **CHECKPOINT B:** demo by running the sidecar and curling both endpoints in front of the user. Wait for feedback.

### Phase C — Tauri shell + frontend

1. `pnpm create tauri-app` (or chosen framework's equivalent) into a temp dir, then merge into the chosen layout (`src-tauri/` and `frontend/`). Do not accept the template wholesale — strip example components, keep only the routing skeleton.
2. `src-tauri/tauri.conf.json`:
   - Window title "Nightstand", size 1200×800, resizable.
   - Sidecar binary path: `binaries/nightstand-backend-<target-triple>` (use the convention even though we're in dev — we'll resolve via the dev script).
3. `src-tauri/src/main.rs`:
   - On app startup, spawn the Python sidecar (in dev: `uv run python -m nightstand.main --port 0`; in prod: the bundled sidecar binary).
   - Capture stdout, parse `NIGHTSTAND_PORT=<n>`, store the port in Tauri state.
   - Expose a Tauri command `get_backend_port() -> u16` to the frontend.
   - On window close: SIGTERM the sidecar.
4. Frontend root page (`frontend/src/routes/+page.svelte` or `App.tsx`):
   - On mount: call `get_backend_port()`, then `fetch('http://127.0.0.1:' + port + '/health')` and `/calibre/probe`.
   - Render the JSON in a monospace `<pre>`. Two cards: "Sidecar" and "Calibre".
   - No styling library yet. A minimal global CSS file with sensible defaults (system font stack, dark background, comfortable line-height) is fine.
5. A top-level `package.json` script `dev` that runs Tauri dev mode end-to-end.

🛑 **CHECKPOINT C:** run `pnpm tauri dev` together with the user. Window opens, two cards render with real data. **This is the end of M0.**

---

## 4. Out of scope for M0 (do not do these yet)

- Any UI library (Tailwind, shadcn, etc.). Plain CSS only.
- Any theming work. Omarchy theming comes when there's a UI worth theming.
- Anthropic SDK / Open Library / Google Books integration.
- SQLite / sidecar DB.
- PyInstaller bundling / `tauri build` / packaging — `dev` mode only.
- GitHub Actions CI.
- AUR PKGBUILD.
- Any `calibredb` writes. Read-only probe only.
- Reusing helpers from `import_books.py`. That happens in M2.
- Tests. (M0 is a scaffolding spike; the next batch will introduce the test layout.)

---

## 5. Deliverables for the M0 session

1. Repo in the state described above.
2. A one-paragraph summary message to the user at the end describing:
   - What got built.
   - What surprises or deviations from this doc occurred (and why).
   - The exact commands to run it (`pnpm tauri dev` etc.).
3. A short proposal for what M1 should cover, written as a new file `docs/M1_LIBRARY_BROWSER.md`. **Just the outline**, not the implementation — the user will review and revise it before M1 starts.

---

## 6. When to break the rules

The only legitimate reason to skip a step in this doc is if the user, mid-session, tells you to. In that case, log the deviation in the closing summary so the next session knows.

If something is unclear in this doc, **ask the user**, do not improvise. The cost of one short question is far smaller than the cost of redoing scaffolding.

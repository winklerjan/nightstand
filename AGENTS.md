# Nightstand — Shared Agent Rules

All agents (Claude, Codex, opencode) read this file. CLAUDE.md contains Claude-specific config only.

---

## 0. Current scope

**M1 is read-only.** The only permitted Calibre operations are listing books, fetching metadata, and serving cover images via `calibredb list` and `calibredb get_metadata`. Do not implement:

- Calibre DB writes of any kind (`calibredb add`, `set_metadata`, `remove_format`, etc.)
- File moves, imports, or deletes
- Metadata embedding

When the intended scope is unclear, ask — don't assume the next milestone has started.

---

## 1. Architecture

Tauri 2 desktop shell (Rust) owns the process lifecycle. On startup it spawns a Python child process (`uv run python -m nightstand.main --port 0` from the `backend/` directory). The child prints `NIGHTSTAND_PORT=<n>` to stdout; Rust reads this via `BufReader` and stores it in a `Mutex<SidecarState>`. A drain thread consumes remaining stdout to prevent SIGPIPE.

The SvelteKit frontend (SPA mode, `adapter-static`) is embedded in the Tauri webview. On mount it calls `invoke("get_backend_port")` to retrieve the port, then fetches `http://localhost:<port>/...`. All Calibre reads go through the Python sidecar — no direct DB access from Rust or the frontend.

The Python sidecar wraps `calibredb` via `subprocess.run()`. Every subprocess call must pass `env=_clean_env()` to strip venv environment variables that corrupt calibredb's Python shebang resolution.

---

## 2. Commands

| Purpose | Command | Run from |
|---------|---------|----------|
| Start everything | `pnpm dev` | repo root |
| Frontend type check | `pnpm --filter frontend check` | repo root |
| Rust lint | `cargo clippy` | `src-tauri/` |
| Rust type check | `cargo check` | `src-tauri/` |
| Backend standalone | `uv run python -m nightstand.main --port 8765` | `backend/` |
| Backend tests | `uv run pytest` | `backend/` |

Prefix all commands with `rtk` for token-efficient output (see CLAUDE.md).

---

## 3. Critical gotchas

**`_clean_env()` on every calibredb subprocess.** The uv venv puts its own `python3` first in `PATH`. calibredb has a `#!/usr/bin/env python3` shebang — without env cleaning it picks up the venv Python, which lacks system site-packages (`msgpack`), and fails. `_clean_env()` strips `VIRTUAL_ENV`, `PYTHONPATH`, `PYTHONHOME`, and removes the venv bin dir from `PATH`. It lives in `backend/nightstand/services/calibre.py` and must be passed to every `subprocess.run()` that invokes calibredb.

**Frontend fetches must use `http://localhost`, never `http://127.0.0.1`.** WebKitGTK on Linux blocks requests to `127.0.0.1` from the webview. Both resolve to the same address but only `localhost` is permitted. This is the first thing to check when a fetch silently fails in the webview.

**Calibre GUI must be closed before any `calibredb` CLI call.** When open it holds an exclusive lock. `calibredb` exits non-zero with "Another calibre program is running" in stderr. The API handles this gracefully via `CalibreLockedError` and returns `{"locked": true}` — do not convert this to a 500.

**MutexGuard lifetimes in Rust.** `state.0.lock().unwrap().take()` inside a closure fails to compile (E0597). Bind the guard to an explicit variable first: `let mut guard = state.0.lock().unwrap(); guard.take()`.

---

## 4. Forbidden / never do

- `calibredb embed_metadata` — renames files to Calibre's internal format, destroying normalized filenames permanently
- Any Calibre DB write in M1
- Logging library paths, book paths, or user filesystem data
- Hardcoding the library path — always read from `NIGHTSTAND_CALIBRE_LIBRARY` env var, fallback `~/Calibre Library`
- `http://127.0.0.1` in frontend fetch calls (use `http://localhost`)
- `unwrap()` in production Rust paths (use `?` and propagate)

---

## 5. Project structure

```
nightstand/
├── src-tauri/
│   ├── tauri.conf.json          ← window config, beforeDevCommand, frontendDist
│   ├── capabilities/
│   │   └── default.json         ← Tauri capability grants (core:default only)
│   ├── Cargo.toml
│   └── src/
│       └── lib.rs               ← SidecarState, spawn_sidecar(), get_backend_port command
│                                   on_window_event(Destroyed) kills child process
├── frontend/
│   ├── package.json             ← name: "frontend" (required for pnpm --filter)
│   └── src/
│       └── routes/
│           └── +page.svelte     ← main UI entry point
├── backend/
│   ├── pyproject.toml           ← hatchling build, fastapi + uvicorn[standard]
│   └── nightstand/
│       ├── main.py              ← FastAPI app, CORS middleware, port binding
│       ├── api/
│       │   └── library.py       ← /library/* routes (added in M1)
│       └── services/
│           └── calibre.py       ← _clean_env(), CalibreLockedError, version(), list_first()
├── pnpm-workspace.yaml          ← packages: [frontend], allowBuilds: esbuild: true
└── package.json                 ← root: "dev": "tauri dev", @tauri-apps/cli ^2
```

---

## 6. Code conventions

**Python**
- Type hints required on all function signatures
- Every `subprocess.run()` that calls calibredb must pass `env=_clean_env()`
- No bare `except:` — catch specific exceptions or `Exception` with a message
- Use `CalibreLockedError` (not a generic error) for lock detection so callers can handle it distinctly

**TypeScript / Svelte**
- Strict mode, no `any`
- Use `invoke()` from `@tauri-apps/api/core` for all Tauri commands
- Scoped `<style>` blocks in Svelte components — no inline styles
- No `// @ts-ignore`

**Rust**
- No `unwrap()` in production paths — use `?` and let errors propagate to the Tauri command boundary as strings
- No `#[allow(unused)]` without an explanatory comment
- Keep `lib.rs` focused on process lifecycle; add new Tauri commands in separate modules as the project grows

**All layers**
- Comments only when WHY is non-obvious: a hidden constraint, a workaround for a specific bug, a subtle invariant. Never comment what the code does.

---

## 7. Workflow rules

- **Minimal scope** — only change what was explicitly asked. A bug fix is not an invitation to clean up surrounding code.
- **Small focused commits** after each logical subtask, not at the end of a long session.
- **Change budget** — more than 10 files or 300 LOC changed in one task: pause and ask before continuing.
- **Verification after each layer change:**
  - Frontend change → `pnpm --filter frontend check`
  - Rust change → `cargo clippy` in `src-tauri/`
  - Backend change → restart sidecar and verify manually (no automated harness yet)
- **No `--no-verify`** on commits. If a hook fails, fix the underlying issue.
- **Propose rollback steps** before any operation that touches files outside the repo (Calibre library, Kindle mount).
- Never guess a command. If uncertain, propose the safe discovery step first.

---

## 8. Security

**Acceptable logging:** HTTP method + route path only. No query parameters, no file paths, no book titles, no author names, no user data of any kind.

**Library path:** sourced from `NIGHTSTAND_CALIBRE_LIBRARY` env var → fallback `os.path.expanduser("~/Calibre Library")`. The path is never hardcoded, never logged, never returned raw in API responses (only the resolved path for probe/debug endpoints, and only in dev).

**calibredb subprocess:** always runs with `env=_clean_env()`. This is also an isolation measure — the venv environment should not leak into the Calibre process.

**CORS:** `allow_origin_regex` permits only `localhost` and `127.0.0.1` ports plus `tauri://localhost`. No wildcards. Enforced in `main.py`.

**No credentials** exist in this project — Calibre is local-only. If external services are added in future milestones, they go in `.env` (gitignored, never logged).

---

## 9. Debugging

| Symptom | Likely cause | First check |
|---------|-------------|-------------|
| "TypeError: Load failed" in webview | Fetching `127.0.0.1` instead of `localhost` | Search frontend for `127.0.0.1` |
| `calibredb` fails inside venv | Venv Python intercepts shebang | Confirm `_clean_env()` is passed to subprocess |
| "Another calibre program is running" | Calibre GUI is open | Close Calibre |
| Sidecar port never received by Rust | BufReader blocked or stdout not flushed | Confirm sidecar prints `NIGHTSTAND_PORT=` with `flush=True`; confirm drain thread is running |
| Rust E0597 lifetime error | MutexGuard dropped inside closure | Bind guard to explicit variable before the block |
| Frontend fetches succeed but data is wrong | Stale port from previous run | Restart `pnpm dev` cleanly |
| `pnpm dev` fails — esbuild blocked | pnpm build script approval pending | Add `allowBuilds: esbuild: true` to `pnpm-workspace.yaml` |

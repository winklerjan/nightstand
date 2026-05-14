# Nightstand — Tech Stack Quick Reference

## Runtime stack

| Layer | Technology |
|-------|-----------|
| Desktop shell | Tauri 2 (Rust) |
| Frontend | SvelteKit (adapter-static, SPA mode) |
| Backend | Python 3.12 + FastAPI + uvicorn |
| Calibre integration | `calibredb` CLI via subprocess |
| Database | SQLite (sidecar DB, future) |
| Package manager | pnpm (frontend + root), uv (backend) |

## Key paths

| What | Path |
|------|------|
| Tauri config | `src-tauri/tauri.conf.json` |
| Tauri source | `src-tauri/src/lib.rs` |
| Frontend routes | `frontend/src/routes/` |
| Backend entrypoint | `backend/nightstand/main.py` |
| Calibre service | `backend/nightstand/services/calibre.py` |
| Library API | `backend/nightstand/api/library.py` |

## Dev commands

```bash
pnpm dev                                    # full stack (from repo root)
uv run python -m nightstand.main --port 8765  # backend only (from backend/)
pnpm --filter frontend dev                  # frontend only
cargo check                                 # Rust type check (from src-tauri/)
cargo clippy                                # Rust lint (from src-tauri/)
```

## Environment variables

| Var | Default | Purpose |
|-----|---------|---------|
| `NIGHTSTAND_CALIBRE_LIBRARY` | `~/Calibre Library` | Path to Calibre library |

## Milestones

| ID | Name | Status |
|----|------|--------|
| M0 | Scaffolding | Complete |
| M1 | Library Browser | Next |
| M2 | Smart Import | Future |
| M3 | Format Conversion | Future |
| M4 | Text Cleanup | Future |
| M5 | Online Search | Future |
| M6 | Kindle/KOReader Sync | Future |
| M7 | Library Maintenance | Future |
| M8 | Settings & First-Run Wizard | Future |

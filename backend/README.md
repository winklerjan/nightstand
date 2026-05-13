# Nightstand Backend

Python 3.14 + FastAPI sidecar. Spawned by Tauri on launch; talks to `calibredb` on localhost.

## Setup

```bash
cd backend
uv sync
```

## Run

```bash
NIGHTSTAND_CALIBRE_LIBRARY="/home/jan/Calibre Library" \
  uv run python -m nightstand.main --port 8765
# Prints: NIGHTSTAND_PORT=8765
# Use port 0 to let the OS pick a free port.
```

## Test endpoints

```bash
# Health check
curl http://127.0.0.1:8765/health

# Calibre probe (requires Calibre GUI to be closed)
curl http://127.0.0.1:8765/calibre/probe
```

## Notes

- Set `NIGHTSTAND_CALIBRE_LIBRARY` to your Calibre library path (default: `~/Calibre Library`).
- `calibredb list` requires the Calibre GUI to be closed. The probe returns `"locked": true` with a message if it detects the lock — the UI will show a modal.
- Never run `calibredb embed_metadata`. It renames files back to Calibre's internal form.

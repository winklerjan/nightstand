import argparse
import importlib.metadata
import os
import socket

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from nightstand.services import calibre
from nightstand.services.calibre import CalibreLockedError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?|tauri://localhost",
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    version = importlib.metadata.version("nightstand")
    return {"status": "ok", "version": version}


@app.get("/calibre/probe")
def calibre_probe():
    library_path = os.environ.get(
        "NIGHTSTAND_CALIBRE_LIBRARY", os.path.expanduser("~/Calibre Library")
    )
    ver = calibre.version()
    try:
        first_book = calibre.list_first(library_path)
        locked = False
        lock_message = None
    except CalibreLockedError as e:
        first_book = None
        locked = True
        lock_message = str(e)
    return {
        "calibredb_version": ver["raw"],
        "library_path": library_path,
        "first_book": first_book,
        "locked": locked,
        "lock_message": lock_message,
    }


def _pick_port(requested: int) -> int:
    if requested != 0:
        return requested
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()

    port = _pick_port(args.port)
    print(f"NIGHTSTAND_PORT={port}", flush=True)

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()

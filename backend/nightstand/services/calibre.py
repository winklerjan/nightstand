import json
import os
import subprocess


def _clean_env() -> dict:
    """Return os.environ without venv overrides so calibredb uses system Python."""
    venv = os.environ.get("VIRTUAL_ENV", "")
    path_parts = [p for p in os.environ.get("PATH", "").split(":") if not p.startswith(venv)]
    env = dict(os.environ)
    env["PATH"] = ":".join(path_parts)
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    return env


def version() -> dict:
    result = subprocess.run(
        ["calibredb", "--version"],
        capture_output=True,
        text=True,
        check=True,
        env=_clean_env(),
    )
    return {"raw": result.stdout.strip()}


class CalibreLockedError(RuntimeError):
    pass


def list_first(library_path: str) -> dict:
    result = subprocess.run(
        [
            "calibredb",
            "list",
            "--library-path", library_path,
            "--limit", "1",
            "--fields", "title,authors",
            "--for-machine",
        ],
        capture_output=True,
        text=True,
        env=_clean_env(),
    )
    if result.returncode != 0:
        if "Another calibre program" in result.stderr:
            raise CalibreLockedError("Calibre GUI is open — close it and retry.")
        raise RuntimeError(result.stderr.strip())
    books = json.loads(result.stdout)
    return books[0] if books else {}

import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


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


# Maps book_id → book folder (parent of format files). Built once, reused for covers and comments.
_folder_cache: dict[int, Path] | None = None


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


def _build_folder_cache(library_path: str) -> dict[int, Path]:
    result = _run_calibredb(
        ["list", "--library-path", library_path, "--for-machine", "--fields", "id,formats"]
    )
    cache: dict[int, Path] = {}
    for book in json.loads(result.stdout):
        bid = int(book.get("id", -1))
        formats = _as_list(book.get("formats"))
        if formats:
            cache[bid] = Path(formats[0]).parent
    return cache


def _book_folder(library_path: str, book_id: int) -> Path | None:
    global _folder_cache
    if _folder_cache is None:
        _folder_cache = _build_folder_cache(library_path)
    return _folder_cache.get(book_id)


def _read_opf_comments(folder: Path) -> str | None:
    opf = folder / "metadata.opf"
    if not opf.is_file():
        return None
    try:
        root = ET.parse(str(opf)).getroot()
        elem = root.find(".//{http://purl.org/dc/elements/1.1/}description")
        return elem.text if elem is not None else None
    except ET.ParseError:
        return None


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


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(value)]


def _normalize_formats(formats: list[str]) -> list[str]:
    names: list[str] = []
    for item in formats:
        suffix = Path(item).suffix.lstrip(".").upper()
        names.append(suffix or item.upper())
    return names


def _normalize_book(book: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": int(book["id"]),
        "title": str(book.get("title") or ""),
        "authors": _as_list(book.get("authors")),
        "tags": _as_list(book.get("tags")),
        "series": book.get("series"),
        "series_index": book.get("series_index"),
        "languages": _as_list(book.get("languages")),
        "pubdate": book.get("pubdate"),
        "formats": _normalize_formats(_as_list(book.get("formats"))),
    }


def _normalize_lookup(value: str) -> str:
    return " ".join(value.casefold().split())


def list_books(library_path: str) -> list[dict[str, Any]]:
    global _folder_cache
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
    # Pre-populate folder cache while we already have format paths.
    # This ensures cover requests never need to spawn a calibredb process.
    if _folder_cache is None:
        cache: dict[int, Path] = {}
        for book in books:
            bid = int(book.get("id", -1))
            formats = _as_list(book.get("formats"))
            if formats:
                cache[bid] = Path(formats[0]).parent
        _folder_cache = cache
    return [_normalize_book(book) for book in books]


def get_book(library_path: str, book_id: int) -> dict[str, Any] | None:
    # Fetch all books without the comments field (calibredb list with comments hangs on large
    # libraries), filter by id in Python, then read comments from the book's metadata.opf directly.
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
    match = next((b for b in books if int(b.get("id", -1)) == book_id), None)
    if match is None:
        return None
    book = _normalize_book(match)
    folder = _book_folder(library_path, book_id)
    book["comments"] = _read_opf_comments(folder) if folder else None
    return book


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
    if isinstance(raw_metadata, list):
        records = raw_metadata
    elif isinstance(raw_metadata, dict):
        records = raw_metadata.values()
    else:
        return {}

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


def get_cover_path(library_path: str, book_id: int) -> Path | None:
    folder = _book_folder(library_path, book_id)
    if folder is None:
        return None
    cover = folder / "cover.jpg"
    return cover if cover.is_file() else None

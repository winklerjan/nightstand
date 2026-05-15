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


@router.get("/books", response_model=None)
def books() -> list[dict[str, Any]] | JSONResponse:
    try:
        return calibre.list_books(_library_path())
    except CalibreLockedError as error:
        return _locked_response(error)


@router.get("/books/{book_id}", response_model=None)
def book(book_id: int) -> dict[str, Any] | JSONResponse:
    try:
        found = calibre.get_book(_library_path(), book_id)
    except CalibreLockedError as error:
        return _locked_response(error)
    if found is None:
        raise HTTPException(status_code=404, detail="Book not found")
    found["extras"] = calibre.read_metadata_extras(found["title"], found["authors"])
    return found


@router.get("/books/{book_id}/cover", response_model=None)
def cover(book_id: int) -> FileResponse | JSONResponse:
    try:
        cover_path = calibre.get_cover_path(_library_path(), book_id)
    except CalibreLockedError as error:
        return _locked_response(error)
    if cover_path is None:
        raise HTTPException(status_code=404, detail="Cover not found")
    return FileResponse(Path(cover_path), headers={"Cache-Control": "public, max-age=3600"})


@router.get("/tags", response_model=None)
def tags() -> list[str] | JSONResponse:
    try:
        return calibre.get_tags(_library_path())
    except CalibreLockedError as error:
        return _locked_response(error)

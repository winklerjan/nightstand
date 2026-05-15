from pathlib import Path

from nightstand.services import calibre


def test_read_metadata_extras_returns_empty_lists_when_file_is_missing(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert calibre.read_metadata_extras("Title", ["Author"]) == {
        "subgenres": [],
        "themes": [],
    }

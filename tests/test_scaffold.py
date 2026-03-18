from __future__ import annotations

from app.scaffold import scaffold_object


def test_scaffold_object_creates_expected_files(tmp_path) -> None:
    result = scaffold_object("concept", "demo-concept", root=tmp_path)

    assert result.target_dir.exists()
    assert (result.target_dir / "meta.yml").exists()
    assert (result.target_dir / "note.en.qmd").exists()
    assert (result.target_dir / "note.nb.qmd").exists()

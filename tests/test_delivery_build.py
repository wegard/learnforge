from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from app.config import REPO_ROOT
from app.delivery import (
    DeliveryBuildResult,
    _load_delivery,
    scaffold_delivery,
    write_delivery_report,
)
from app.indexer import load_repository
from app.models import DeliveryManifest


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)


def _write_manifest(root: Path, overrides: dict | None = None) -> Path:
    deliveries_dir = root / "deliveries"
    deliveries_dir.mkdir(exist_ok=True)
    payload = {
        "id": "ec202-spring-2026",
        "course": "ec202",
        "term": "spring-2026",
        "language": "en",
        "created": "2026-01-15",
        "updated": "2026-03-26",
        "lectures": [
            {"lecture": "lecture-04", "date": "2026-01-20", "ready": True},
        ],
        "assignments": [
            {"assignment": "assignment-01", "due_date": "2026-02-14", "ready": False},
        ],
        "default_formats": ["html", "revealjs", "pdf", "handout"],
        "default_audiences": ["student", "teacher"],
    }
    if overrides:
        payload.update(overrides)
    manifest_path = deliveries_dir / f"{payload['id']}.yml"
    manifest_path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )
    return manifest_path


def test_scaffold_delivery_creates_manifest(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    from datetime import date

    path = scaffold_delivery(
        "ec202",
        term="spring-2026",
        language="en",
        start_date=date(2026, 1, 20),
        root=tmp_path,
    )
    assert path.exists()
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert payload["id"] == "ec202-spring-2026"
    assert payload["course"] == "ec202"
    assert payload["term"] == "spring-2026"
    assert payload["language"] == "en"
    assert len(payload["lectures"]) == 1  # ec202 has 1 lecture
    assert payload["lectures"][0]["lecture"] == "lecture-04"
    assert payload["lectures"][0]["date"] == "2026-01-20"
    assert payload["lectures"][0]["ready"] is False
    assert len(payload["assignments"]) == 1
    assert payload["assignments"][0]["assignment"] == "assignment-01"


def test_scaffold_delivery_with_weekly_dates(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    from datetime import date

    # Use a course with multiple lectures — copy tem0052
    path = scaffold_delivery(
        "tem0052",
        term="fall-2026",
        language="en",
        start_date=date(2026, 8, 24),
        root=tmp_path,
    )
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    lectures = payload["lectures"]
    assert len(lectures) == 10  # tem0052 has 10 lectures
    assert lectures[0]["date"] == "2026-08-24"
    assert lectures[1]["date"] == "2026-08-31"
    assert lectures[2]["date"] == "2026-09-07"


def test_load_delivery_from_index(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    _write_manifest(tmp_path)
    index, _ = load_repository(tmp_path, collect_errors=True)
    delivery, _ = _load_delivery("ec202-spring-2026", root=tmp_path, index=index)
    assert delivery.model.id == "ec202-spring-2026"
    assert delivery.model.course == "ec202"


def test_load_delivery_raises_for_missing(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    index, _ = load_repository(tmp_path, collect_errors=True)
    import pytest

    with pytest.raises(ValueError, match="not found"):
        _load_delivery("nonexistent", root=tmp_path, index=index)


def test_write_delivery_report(tmp_path: Path) -> None:
    result = DeliveryBuildResult(
        manifest_id="ec202-spring-2026",
        built_lectures=["lecture-04"],
        built_assignments=[],
        skipped_lectures=[],
        skipped_assignments=["assignment-01"],
    )
    manifest = DeliveryManifest.model_validate(
        {
            "id": "ec202-spring-2026",
            "course": "ec202",
            "term": "spring-2026",
            "language": "en",
            "created": "2026-01-15",
            "updated": "2026-03-26",
        }
    )
    report_path = write_delivery_report(result, manifest, tmp_path)
    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["manifest_id"] == "ec202-spring-2026"
    assert payload["built_lectures"] == ["lecture-04"]
    assert payload["skipped_assignments"] == ["assignment-01"]
    assert payload["artifact_count"] == 0


def test_delivery_manifest_validates_after_scaffold(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    from datetime import date

    scaffold_delivery(
        "ec202",
        term="spring-2026",
        language="en",
        start_date=date(2026, 1, 20),
        root=tmp_path,
    )
    # Loading the repository should pick up the manifest without errors
    index, errors = load_repository(tmp_path, collect_errors=True)
    delivery_errors = [e for e in errors if "deliveries" in str(e.path)]
    assert delivery_errors == []
    assert "ec202-spring-2026" in index.deliveries

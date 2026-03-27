from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from app.config import REPO_ROOT
from app.validator import validate_repository


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)
    shutil.copy(
        REPO_ROOT / "representative-targets.yml",
        target_root / "representative-targets.yml",
    )


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
            {
                "lecture": "lecture-04",
                "date": "2026-01-20",
                "ready": False,
            },
        ],
        "assignments": [
            {
                "assignment": "assignment-01",
                "due_date": "2026-02-14",
                "ready": False,
            },
        ],
    }
    if overrides:
        payload.update(overrides)
    manifest_path = deliveries_dir / f"{payload['id']}.yml"
    manifest_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return manifest_path


def test_valid_delivery_produces_no_delivery_errors(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    _write_manifest(tmp_path)
    report = validate_repository(tmp_path, run_build_checks=False)
    delivery_issues = [i for i in report.issues if i.code.startswith("delivery-")]
    assert delivery_issues == []
    assert report.delivery_count == 1


def test_missing_course_produces_error(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    _write_manifest(tmp_path, {"course": "nonexistent-course"})
    report = validate_repository(tmp_path, run_build_checks=False)
    assert any(i.code == "delivery-missing-course" for i in report.issues)


def test_missing_lecture_collection_produces_error(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    _write_manifest(
        tmp_path,
        {
            "lectures": [
                {"lecture": "nonexistent-lecture", "date": "2026-01-20", "ready": False},
            ],
        },
    )
    report = validate_repository(tmp_path, run_build_checks=False)
    assert any(i.code == "delivery-missing-lecture" for i in report.issues)


def test_missing_assignment_collection_produces_error(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    _write_manifest(
        tmp_path,
        {
            "assignments": [
                {"assignment": "nonexistent-assign", "due_date": "2026-02-14", "ready": False},
            ],
        },
    )
    report = validate_repository(tmp_path, run_build_checks=False)
    assert any(i.code == "delivery-missing-assignment" for i in report.issues)


def test_missing_addition_produces_error(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    _write_manifest(
        tmp_path,
        {
            "lectures": [
                {
                    "lecture": "lecture-04",
                    "date": "2026-01-20",
                    "ready": False,
                    "additions": ["nonexistent-object"],
                },
            ],
        },
    )
    report = validate_repository(tmp_path, run_build_checks=False)
    assert any(i.code == "delivery-missing-addition" for i in report.issues)


def test_invalid_removal_produces_error(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    _write_manifest(
        tmp_path,
        {
            "lectures": [
                {
                    "lecture": "lecture-04",
                    "date": "2026-01-20",
                    "ready": False,
                    "removals": ["not-in-collection"],
                },
            ],
        },
    )
    report = validate_repository(tmp_path, run_build_checks=False)
    assert any(i.code == "delivery-invalid-removal" for i in report.issues)


def test_non_chronological_dates_produces_warning(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    _write_manifest(
        tmp_path,
        {
            "lectures": [
                {"lecture": "lecture-04", "date": "2026-02-01", "ready": False},
                {"lecture": "lecture-04", "date": "2026-01-15", "ready": False},
            ],
        },
    )
    report = validate_repository(tmp_path, run_build_checks=False)
    warnings = [i for i in report.issues if i.code == "delivery-dates-not-chronological"]
    assert len(warnings) == 1
    assert warnings[0].severity == "warning"


def test_ready_with_unapproved_content_produces_warning(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    # Set iv-intuition to draft so the ready check triggers
    meta_path = tmp_path / "content" / "concepts" / "iv-intuition" / "meta.yml"
    text = meta_path.read_text(encoding="utf-8")
    text = text.replace("status: approved", "status: draft", 1)
    meta_path.write_text(text, encoding="utf-8")

    _write_manifest(
        tmp_path,
        {
            "lectures": [
                {"lecture": "lecture-04", "date": "2026-01-20", "ready": True},
            ],
        },
    )
    report = validate_repository(tmp_path, run_build_checks=False)
    warnings = [i for i in report.issues if i.code == "delivery-ready-unapproved-content"]
    assert len(warnings) >= 1
    assert warnings[0].severity == "warning"


def test_wrong_collection_kind_for_lecture(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    # assignment-01 is an assignment, not a lecture
    _write_manifest(
        tmp_path,
        {
            "lectures": [
                {"lecture": "assignment-01", "date": "2026-01-20", "ready": False},
            ],
            "assignments": [],
        },
    )
    report = validate_repository(tmp_path, run_build_checks=False)
    assert any(i.code == "delivery-wrong-collection-kind" for i in report.issues)


def test_no_deliveries_directory_is_fine(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    report = validate_repository(tmp_path, run_build_checks=False)
    assert report.delivery_count == 0

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml
from typer.testing import CliRunner

from app.cli import app
from app.config import REPO_ROOT

runner = CliRunner()


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
            {"lecture": "lecture-04", "date": "2026-01-20", "ready": True},
        ],
        "assignments": [
            {"assignment": "assignment-01", "due_date": "2026-02-14", "ready": False},
        ],
    }
    if overrides:
        payload.update(overrides)
    manifest_path = deliveries_dir / f"{payload['id']}.yml"
    manifest_path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )
    return manifest_path


def test_new_delivery_creates_manifest(tmp_path: Path, monkeypatch) -> None:
    copy_repo_subset(tmp_path)
    monkeypatch.setattr("app.cli.REPO_ROOT", tmp_path)
    result = runner.invoke(
        app,
        ["new-delivery", "ec202", "--term", "spring-2026", "--lang", "en", "--start", "2026-01-20"],
    )
    assert result.exit_code == 0, result.output
    assert "ec202-spring-2026" in result.output
    manifest_path = tmp_path / "deliveries" / "ec202-spring-2026.yml"
    assert manifest_path.exists()
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert payload["course"] == "ec202"
    assert payload["term"] == "spring-2026"
    assert len(payload["lectures"]) == 1
    assert payload["lectures"][0]["lecture"] == "lecture-04"
    assert payload["lectures"][0]["date"] == "2026-01-20"


def test_new_delivery_fails_for_nonexistent_course(tmp_path: Path, monkeypatch) -> None:
    copy_repo_subset(tmp_path)
    monkeypatch.setattr("app.cli.REPO_ROOT", tmp_path)
    result = runner.invoke(
        app,
        ["new-delivery", "nonexistent", "--term", "spring-2026"],
    )
    assert result.exit_code == 1


def test_new_delivery_fails_if_already_exists(tmp_path: Path, monkeypatch) -> None:
    copy_repo_subset(tmp_path)
    monkeypatch.setattr("app.cli.REPO_ROOT", tmp_path)
    runner.invoke(
        app,
        ["new-delivery", "ec202", "--term", "spring-2026", "--start", "2026-01-20"],
    )
    result = runner.invoke(
        app,
        ["new-delivery", "ec202", "--term", "spring-2026", "--start", "2026-01-20"],
    )
    assert result.exit_code == 1
    assert "already exists" in result.output


def test_delivery_status_displays_overview(tmp_path: Path, monkeypatch) -> None:
    copy_repo_subset(tmp_path)
    _write_manifest(tmp_path)
    monkeypatch.setattr("app.cli.REPO_ROOT", tmp_path)
    monkeypatch.setattr("app.delivery.REPO_ROOT", tmp_path)
    result = runner.invoke(app, ["delivery-status", "ec202-spring-2026"])
    assert result.exit_code == 0, result.output
    assert "ec202-spring-2026" in result.output
    assert "Lectures:" in result.output
    assert "Assignments:" in result.output
    assert "Summary:" in result.output


def test_delivery_status_json(tmp_path: Path, monkeypatch) -> None:
    copy_repo_subset(tmp_path)
    _write_manifest(tmp_path)
    monkeypatch.setattr("app.cli.REPO_ROOT", tmp_path)
    monkeypatch.setattr("app.delivery.REPO_ROOT", tmp_path)
    result = runner.invoke(app, ["delivery-status", "ec202-spring-2026", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["id"] == "ec202-spring-2026"
    assert payload["summary"]["total_lectures"] == 1


def test_delivery_status_fails_for_unknown_manifest(tmp_path: Path, monkeypatch) -> None:
    copy_repo_subset(tmp_path)
    monkeypatch.setattr("app.cli.REPO_ROOT", tmp_path)
    monkeypatch.setattr("app.delivery.REPO_ROOT", tmp_path)
    result = runner.invoke(app, ["delivery-status", "nonexistent"])
    assert result.exit_code == 1

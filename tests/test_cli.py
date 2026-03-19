from __future__ import annotations

import json
import shutil
from pathlib import Path

from typer.testing import CliRunner

import app.cli as cli_module
from app.cli import app
from app.config import REPO_ROOT

runner = CliRunner()


def test_validate_command_succeeds() -> None:
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "Errors: 0" in result.stdout
    assert "Warnings: 11" in result.stdout
    assert "Build summary: build/reports/build-summary.json" in result.stdout
    assert "Resource workflow:" in result.stdout


def test_validate_command_json_output_includes_build_summary() -> None:
    result = runner.invoke(app, ["validate", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed_with_warnings"
    assert '"build_summary_path": "build/reports/build-summary.json"' in result.stdout
    assert payload["resource_workflow"]["status_counts"]["candidate"] == 1


def test_search_command_finds_iv_content() -> None:
    result = runner.invoke(app, ["search", "instrumental variables"])
    assert result.exit_code == 0
    assert "iv-intuition" in result.stdout


def test_approve_command_updates_reviewed_resource(tmp_path: Path, monkeypatch) -> None:
    copy_repo_subset(tmp_path)
    monkeypatch.setattr(cli_module, "REPO_ROOT", tmp_path)

    result = runner.invoke(
        app,
        ["approve", "iv-reviewed-primer", "--by", "vegard", "--on", "2026-03-18"],
    )

    meta = (tmp_path / "content" / "resources" / "iv-reviewed-primer" / "meta.yml").read_text(
        encoding="utf-8"
    )

    assert result.exit_code == 0
    assert "Updated iv-reviewed-primer -> approved" in result.stdout
    assert "status: approved" in meta
    assert "approved_by: vegard" in meta
    assert "approved_on: '2026-03-18'" in meta or "approved_on: 2026-03-18" in meta


def test_stale_resources_command_writes_report(tmp_path: Path, monkeypatch) -> None:
    copy_repo_subset(tmp_path)
    monkeypatch.setattr(cli_module, "REPO_ROOT", tmp_path)

    result = runner.invoke(app, ["stale", "resources", "--today", "2026-03-18"])

    report_path = tmp_path / "build" / "reports" / "stale-resources.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert "Stale resources: 1 / 4." in result.stdout
    assert report_path.exists()
    assert payload["stale_resource_count"] == 1
    assert payload["stale_resources"][0]["id"] == "iv-policy-brief-stale"


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)
    shutil.copy(
        REPO_ROOT / "representative-targets.yml",
        target_root / "representative-targets.yml",
    )

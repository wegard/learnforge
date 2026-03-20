from __future__ import annotations

import json
import shutil
from pathlib import Path

from typer.testing import CliRunner

import app.cli as cli_module
from app.cli import app
from app.config import REPO_ROOT
from app.publish import PublishArtifact

runner = CliRunner()


def test_validate_command_succeeds() -> None:
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "Errors: 0" in result.stdout
    assert "Warnings:" in result.stdout
    assert "Build summary: build/reports/build-summary.json" in result.stdout
    assert "Resource workflow:" in result.stdout


def test_validate_command_json_output_includes_build_summary() -> None:
    result = runner.invoke(app, ["validate", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed_with_warnings"
    assert '"build_summary_path": "build/reports/build-summary.json"' in result.stdout
    assert payload["resource_workflow"]["status_counts"]["candidate"] >= 1


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
    assert (
        f"Stale resources: {payload['stale_resource_count']} / {payload['resource_count']}."
        in result.stdout
    )
    assert report_path.exists()
    assert payload["stale_resource_count"] == 1
    assert payload["stale_resources"][0]["id"] == "iv-policy-brief-stale"


def test_translation_status_command_reports_bik2551_en(tmp_path: Path, monkeypatch) -> None:
    copy_repo_subset(tmp_path)
    monkeypatch.setattr(cli_module, "REPO_ROOT", tmp_path)

    result = runner.invoke(app, ["translation-status", "bik2551", "--lang", "en", "--json"])

    payload = json.loads(result.stdout)
    course_entry = next(entry for entry in payload["entries"] if entry["identifier"] == "bik2551")
    concept_entry = next(
        entry
        for entry in payload["entries"]
        if entry["identifier"] == "generative-ai-fundamentals"
    )
    exercise_entry = next(
        entry
        for entry in payload["entries"]
        if entry["identifier"] == "prompt-improvement-workshop"
    )

    assert result.exit_code == 0
    assert payload["course_id"] == "bik2551"
    assert payload["language"] == "en"
    assert payload["missing_count"] == 0
    assert course_entry["translation_status"] == "approved"
    assert course_entry["note_exists"] is True
    assert course_entry["source_word_count_nb"] == 448
    assert concept_entry["translation_status"] == "approved"
    assert concept_entry["note_exists"] is True
    assert concept_entry["source_word_count_nb"] == 468
    assert exercise_entry["translation_status"] == "approved"
    assert exercise_entry["note_exists"] is True
    assert exercise_entry["solution_exists"] is True


def test_publish_command_reports_bundle_paths(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cli_module, "REPO_ROOT", tmp_path)

    def fake_publish_student_site(*, languages, root):
        assert languages == ["en"]
        assert root == tmp_path
        return PublishArtifact(
            publish_root=tmp_path / "build" / "publish" / "student-site",
            manifest_path=tmp_path
            / "build"
            / "reports"
            / "publish"
            / "student-site"
            / "publish-manifest.json",
            languages=("en",),
            total_target_count=1,
            target_counts_by_language={"en": {"home": 1}},
        )

    monkeypatch.setattr(cli_module, "publish_student_site", fake_publish_student_site)

    result = runner.invoke(app, ["publish", "--lang", "en"])

    assert result.exit_code == 0
    assert "Published student site -> build/publish/student-site" in result.stdout
    assert (
        "Publish manifest: build/reports/publish/student-site/publish-manifest.json"
        in result.stdout
    )
    assert "Languages: en" in result.stdout


def test_publish_command_rejects_unknown_language() -> None:
    result = runner.invoke(app, ["publish", "--lang", "sv"])

    assert result.exit_code != 0
    assert "lang must be one of" in result.output


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)
    shutil.copy(
        REPO_ROOT / "representative-targets.yml",
        target_root / "representative-targets.yml",
    )

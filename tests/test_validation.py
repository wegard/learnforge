from __future__ import annotations

import json
import shutil
from pathlib import Path

from app.config import REPO_ROOT
from app.validator import load_representative_targets, validate_repository, write_validation_report


def test_validation_report_json_includes_build_summary(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)

    report = validate_repository(tmp_path, run_build_checks=False)
    report_path, build_summary_path = write_validation_report(report, tmp_path)

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    build_summary = json.loads(build_summary_path.read_text(encoding="utf-8"))

    assert payload["status"] == "passed_with_warnings"
    assert payload["error_count"] == 0
    assert payload["warning_count"] == 6
    assert payload["build_summary_path"] == "build/reports/build-summary.json"
    assert "translation_coverage" in payload
    assert "resource_workflow" in payload
    assert payload["resource_workflow"]["status_counts"]["candidate"] == 1
    assert build_summary["status"] == "skipped"
    assert build_summary["target_count"] == 13


def test_validator_reports_missing_reference(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    meta_path = tmp_path / "content" / "concepts" / "iv-intuition" / "meta.yml"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace("- iv-dag-figure", "- missing-object"),
        encoding="utf-8",
    )

    report = validate_repository(tmp_path, run_build_checks=False)

    assert any(
        issue.code == "missing-reference" and issue.object_id == "iv-intuition"
        for issue in report.issues
    )


def test_validator_reports_missing_translation_warning(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    meta_path = tmp_path / "content" / "resources" / "angrist-podcast-iv" / "meta.yml"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace("nb: approved", "nb: machine_draft", 1),
        encoding="utf-8",
    )

    report = validate_repository(tmp_path, run_build_checks=False)

    assert report.ok
    assert any(
        issue.code == "missing-approved-translation"
        and issue.severity == "warning"
        and issue.object_id == "angrist-podcast-iv"
        for issue in report.issues
    )
    assert report.translation_coverage["missing_variant_count"] >= 1
    assert any(
        entry["id"] == "angrist-podcast-iv"
        and "nb" in entry["missing_languages"]
        for entry in report.translation_coverage["missing_variants"]
    )


def test_validator_reports_missing_local_asset(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    note_path = tmp_path / "content" / "concepts" / "iv-intuition" / "note.en.qmd"
    note_path.write_text(
        note_path.read_text(encoding="utf-8") + "\n\n![](assets/missing-figure.svg)\n",
        encoding="utf-8",
    )

    report = validate_repository(tmp_path, run_build_checks=False)

    assert any(
        issue.code == "missing-local-asset" and issue.object_id == "iv-intuition"
        for issue in report.issues
    )


def test_validator_reports_missing_figure_fallback_asset(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    figure_pdf = tmp_path / "content" / "figures" / "iv-dag-figure" / "figure.pdf"
    figure_pdf.unlink()

    report = validate_repository(tmp_path, run_build_checks=False)

    assert any(
        issue.code == "missing-figure-pdf" and issue.object_id == "iv-dag-figure"
        for issue in report.issues
    )
    assert any(
        issue.code == "interactive-figure-missing-static-fallback"
        and issue.object_id == "iv-dag-figure"
        for issue in report.issues
    )


def test_load_representative_targets_returns_expected_registry() -> None:
    targets = load_representative_targets(REPO_ROOT)
    target_keys = {
        (target.id, target.audience, target.language, target.format)
        for target in targets
    }

    assert ("iv-intuition", "student", "en", "html") in target_keys
    assert ("iv-dag-figure", "student", "en", "html") in target_keys
    assert ("iv-dag-figure", "teacher", "en", "pdf") in target_keys
    assert ("angrist-podcast-iv", "student", "en", "html") in target_keys
    assert ("tem0052-lecture-05", "student", "en", "html") in target_keys
    assert ("resource-inbox", "teacher", "en", "html") in target_keys
    assert ("lecture-04", "teacher", "nb", "revealjs") in target_keys
    assert ("assignment-01", "student", "en", "exercise-sheet") in target_keys
    assert ("assignment-01", "teacher", "en", "exercise-sheet") in target_keys


def test_full_validation_build_summary_tracks_representative_outputs() -> None:
    report = validate_repository(REPO_ROOT)

    assert report.ok
    assert report.build_summary["status"] == "passed"
    assert report.build_summary["failure_count"] == 0
    assert report.resource_workflow["stale_resource_count"] == 1

    concept_target = next(
        target
        for target in report.build_summary["targets"]
        if target["target_id"] == "iv-intuition" and target["format"] == "html"
    )
    lecture_target = next(
        target
        for target in report.build_summary["targets"]
        if target["target_id"] == "lecture-04" and target["format"] == "revealjs"
    )
    tem0052_lecture_target = next(
        target
        for target in report.build_summary["targets"]
        if target["target_id"] == "tem0052-lecture-05" and target["format"] == "html"
    )
    figure_html_target = next(
        target
        for target in report.build_summary["targets"]
        if target["target_id"] == "iv-dag-figure"
        and target["format"] == "html"
        and target["audience"] == "student"
    )
    figure_pdf_target = next(
        target
        for target in report.build_summary["targets"]
        if target["target_id"] == "iv-dag-figure"
        and target["format"] == "pdf"
        and target["audience"] == "teacher"
    )
    assignment_html_target = next(
        target
        for target in report.build_summary["targets"]
        if target["target_id"] == "assignment-01"
        and target["format"] == "html"
        and target["audience"] == "student"
    )
    resource_page_target = next(
        target
        for target in report.build_summary["targets"]
        if target["target_id"] == "angrist-podcast-iv"
        and target["format"] == "html"
        and target["audience"] == "student"
    )
    resource_inbox_target = next(
        target
        for target in report.build_summary["targets"]
        if target["target_id"] == "resource-inbox"
        and target["format"] == "html"
        and target["audience"] == "teacher"
    )

    assert concept_target["integrity"]["status"] == "passed"
    assert concept_target["integrity"]["broken_link_count"] == 0
    assert lecture_target["status"] == "passed"
    assert tem0052_lecture_target["status"] == "passed"
    assert figure_html_target["status"] == "passed"
    assert figure_pdf_target["status"] == "passed"
    assert resource_page_target["status"] == "passed"
    assert resource_inbox_target["status"] == "passed"
    assert assignment_html_target["leakage_status"] == "clean"
    assert Path(REPO_ROOT / concept_target["output_path"]).exists()


def test_validation_report_tracks_resource_workflow_state() -> None:
    report = validate_repository(REPO_ROOT, run_build_checks=False)

    assert report.resource_workflow["status_counts"] == {
        "candidate": 1,
        "reviewed": 1,
        "approved": 1,
        "published": 1,
    }
    assert report.resource_workflow["student_visible_resource_ids"] == ["angrist-podcast-iv"]
    assert any(
        entry["id"] == "iv-policy-brief-stale"
        for entry in report.resource_workflow["stale_resources"]
    )
    assert any(
        issue.code == "stale-resource" and issue.object_id == "iv-policy-brief-stale"
        for issue in report.issues
    )


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)
    shutil.copy(
        REPO_ROOT / "representative-targets.yml",
        target_root / "representative-targets.yml",
    )

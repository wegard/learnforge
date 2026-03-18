from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from app.build import build_target, write_student_site_search_index
from app.config import REPO_ROOT
from app.indexer import load_repository


def test_student_build_writes_manifests_and_clean_leakage_report() -> None:
    artifact = build_target(
        "iv-intuition",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    student_html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    dependency_manifest = json.loads(artifact.dependency_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert artifact.output_path.exists()
    assert artifact.build_manifest_path.exists()
    assert artifact.dependency_manifest_path.exists()
    assert artifact.leakage_report_path.exists()
    assert artifact.search_index_path is not None
    assert artifact.search_index_path.exists()
    assert "Prompt the room" not in student_html
    assert "Related links" in student_html
    assert "Search LearnForge" in student_html
    assert "Language:" in student_html
    assert build_manifest["target"]["identifier"] == "iv-intuition"
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["figure_id"] == "iv-dag-figure"
    assert build_manifest["figure_uses"][0]["interactive_included"] is True
    assert (
        build_manifest["search_index_path"]
        == "build/exports/student/en/html/assets/search-index.json"
    )
    assert any(
        edge["target_id"] == "lecture-04" for edge in dependency_manifest["dependency_edges"]
    )
    assert leakage_report["status"] == "clean"
    assert leakage_report["teacher_blocks_found"] == 1
    assert leakage_report["teacher_blocks_removed"] == 1


def test_course_page_build_contains_generated_listings() -> None:
    artifact = build_target(
        "ec202",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert "Topics" in html
    assert "Exercises" in html
    assert "Assignments" in html
    assert "Resources" in html
    assert "Search LearnForge" in html
    assert "Breadcrumbs:" in html
    assert "../../collection/assignment-01/assignment-01.html" in html
    assert "../../listing/topic-causal-inference/topic-causal-inference.html" in html
    assert "../../listing/resources-ec202/resources-ec202.html" in html
    assert "../../exercise/ex-iv-concept-check/ex-iv-concept-check.html" in html
    assert "topic-causal-inference" in build_manifest["referenced_listing_targets"]
    assert "resources-ec202" in build_manifest["referenced_listing_targets"]


def test_listing_build_writes_reports() -> None:
    artifact = build_target(
        "topic-causal-inference",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(artifact.dependency_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Causal Inference" in html
    assert "Breadcrumbs:" in html
    assert any(
        edge["relationship"] == "topic-match" for edge in dependency_manifest["dependency_edges"]
    )
    assert leakage_report["status"] == "clean"


def test_student_resource_page_build_is_only_for_published_resource() -> None:
    artifact = build_target(
        "angrist-podcast-iv",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Resource details" in html
    assert "Workflow state" in html
    assert "published" in html
    assert "Instructor note" not in html
    assert build_manifest["resource_workflow"]["resource"]["visible_to_student"] is True
    assert leakage_report["status"] == "clean"


def test_student_resource_listing_excludes_non_approved_and_stale_resources() -> None:
    artifact = build_target(
        "resources-ec202",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "angrist-podcast-iv" in html
    assert "iv-candidate-newsletter" not in html
    assert "iv-reviewed-primer" not in html
    assert "iv-policy-brief-stale" not in html
    assert build_manifest["resource_workflow"]["included_resource_ids"] == ["angrist-podcast-iv"]
    assert {item["id"] for item in build_manifest["resource_workflow"]["excluded_resources"]} == {
        "iv-candidate-newsletter",
        "iv-reviewed-primer",
        "iv-policy-brief-stale",
    }
    assert leakage_report["status"] == "clean"


def test_teacher_resource_inbox_build_surfaces_candidate_reviewed_and_stale_resources() -> None:
    artifact = build_target(
        "resource-inbox",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert "Resource Inbox" in html
    assert "Candidate resources" in html
    assert "Reviewed resources" in html
    assert "Stale resources" in html
    assert "iv-candidate-newsletter" in html
    assert "iv-reviewed-primer" in html
    assert "iv-policy-brief-stale" in html
    assert build_manifest["resource_workflow"]["status_counts"] == {
        "candidate": 1,
        "reviewed": 1,
        "approved": 1,
        "published": 1,
    }


def test_home_page_build_contains_navigation_and_search() -> None:
    artifact = build_target(
        "home",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    search_index = json.loads(artifact.search_index_path.read_text(encoding="utf-8"))

    assert artifact.output_path.name == "index.html"
    assert "Browse by Course" in html
    assert "Browse by Topic" in html
    assert "Featured Resources" in html
    assert "Search LearnForge" in html
    assert 'href="course/ec202/ec202.html"' in html
    assert any(entry["id"] == "home" for entry in search_index["entries"])
    assert any(entry["id"] == "ec202" for entry in search_index["entries"])
    assert any(entry["id"] == "assignment-01" for entry in search_index["entries"])


def test_student_lecture_page_has_course_context_breadcrumbs_and_export_links() -> None:
    build_target(
        "lecture-04",
        audience="student",
        language="en",
        output_format="revealjs",
        root=REPO_ROOT,
    )
    build_target(
        "lecture-04",
        audience="student",
        language="en",
        output_format="pdf",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "lecture-04",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")

    assert "Course context" in html
    assert "EC202 - Applied Econometrics" in html
    assert "Breadcrumbs:" in html
    assert "Slides" in html
    assert "PDF" in html
    assert 'data-figure-id="iv-dag-figure"' in html
    assert "Highlight relevance" in html


def test_teacher_lecture_reveal_build_reports_static_figure_fallback() -> None:
    artifact = build_target(
        "lecture-04",
        audience="teacher",
        language="nb",
        output_format="revealjs",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert 'data-figure-id="iv-dag-figure"' in html
    assert "Highlight relevance" not in html
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["interactive_included"] is False
    assert build_manifest["figure_uses"][0]["fallback_asset_path"].endswith("figure.svg")


def test_student_exercise_page_has_language_switch_and_related_links() -> None:
    artifact = build_target(
        "ex-iv-concept-check",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")

    assert "Exercise details" in html
    assert "Related links" in html
    assert "Used in assignments" in html
    assert "Language:" in html
    assert "Norsk" in html
    assert "Sjekk av IV-intuisjon" not in html
    assert "strong first stage" not in html
    assert "../../collection/assignment-01/assignment-01.html" in html


def test_student_assignment_page_build_has_navigation_exports_and_clean_leakage() -> None:
    build_target(
        "assignment-01",
        audience="student",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "assignment-01",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Assignment details" in html
    assert "Included exercises" in html
    assert "Course context" in html
    assert "Related resources" in html
    assert "Search LearnForge" in html
    assert "Breadcrumbs:" in html
    assert "../../course/ec202/ec202.html" in html
    assert "assignment-01-exercise-sheet.pdf" in html
    assert "assignment-01-solution-sheet.pdf" not in html
    assert build_manifest["assignment"]["included_exercise_ids"] == [
        "ex-iv-assumption-sort",
        "ex-iv-concept-check",
    ]
    assert build_manifest["assignment"]["course_context_ids"] == ["ec202"]
    assert build_manifest["assignment"]["linked_concept_ids"] == ["iv-intuition"]
    assert build_manifest["assignment"]["linked_resource_ids"] == ["angrist-podcast-iv"]
    assert build_manifest["assignment"]["included_solution_files"] == []
    assert {item["format"] for item in build_manifest["generated_artifacts"]} >= {
        "html",
        "exercise-sheet",
    }
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 2
    assert leakage_report["solution_files_included"] == 0


def test_student_figure_page_build_has_interactive_markup_and_manifest() -> None:
    artifact = build_target(
        "iv-dag-figure",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Figure details" in html
    assert 'data-figure-id="iv-dag-figure"' in html
    assert "Highlight relevance" in html
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["interactive_included"] is True
    assert build_manifest["figure_uses"][0]["fallback_asset_path"].endswith("figure.svg")
    assert leakage_report["status"] == "clean"


def test_teacher_figure_pdf_build_uses_pdf_fallback() -> None:
    artifact = build_target(
        "iv-dag-figure",
        audience="teacher",
        language="en",
        output_format="pdf",
        root=REPO_ROOT,
    )

    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert artifact.output_path.exists()
    assert artifact.output_path.name == "iv-dag-figure.pdf"
    assert build_manifest["figure_observation_count"] == 1
    assert build_manifest["figure_uses"][0]["interactive_included"] is False
    assert build_manifest["figure_uses"][0]["fallback_asset_path"].endswith("figure.pdf")


def test_teacher_assignment_page_shows_teacher_export_only() -> None:
    build_target(
        "assignment-01",
        audience="teacher",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "assignment-01",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert "Available outputs" in html
    assert "assignment-01-solution-sheet.pdf" in html
    assert "assignment-01-exercise-sheet.pdf" not in html
    assert build_manifest["assignment"]["included_solution_files"] == []
    assert {item["format"] for item in build_manifest["generated_artifacts"]} >= {
        "html",
        "exercise-sheet",
    }


def test_student_assignment_sheet_build_excludes_solution_content_and_reports_clean() -> None:
    artifact = build_target(
        "assignment-01",
        audience="student",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )

    generated = artifact.source_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    dependency_manifest = json.loads(artifact.dependency_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert artifact.output_path.exists()
    assert artifact.output_path.name == "assignment-01-exercise-sheet.pdf"
    assert "## Exercise sheet" in generated
    assert "strong first stage" not in generated
    assert "lf-solution-block" not in generated
    assert build_manifest["target"]["identifier"] == "assignment-01"
    assert build_manifest["output_path"] == (
        "build/exports/student/en/exercise-sheet/collection/assignment-01/"
        "assignment-01-exercise-sheet.pdf"
    )
    assert any(
        edge["relationship"] == "assignment-item"
        and edge["target_id"] == "ex-iv-assumption-sort"
        for edge in dependency_manifest["dependency_edges"]
    )
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 2
    assert leakage_report["solution_files_included"] == 0
    assert not leakage_report["generated_source_contains_solution_marker"]
    assert all(not item["included_in_output"] for item in leakage_report["solution_details"])


def test_teacher_solution_sheet_build_includes_solution_content() -> None:
    artifact = build_target(
        "assignment-01",
        audience="teacher",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )

    generated = artifact.source_path.read_text(encoding="utf-8")
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert artifact.output_path.exists()
    assert artifact.output_path.name == "assignment-01-solution-sheet.pdf"
    assert "Teacher solution sheet" in generated
    assert "strong first stage" in generated
    assert "lf-solution-block" in generated
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 2
    assert leakage_report["solution_files_included"] == 2


def test_building_nb_home_search_index_excludes_unapproved_translation(tmp_path) -> None:
    copy_repo_subset(tmp_path)
    meta_path = tmp_path / "content" / "resources" / "angrist-podcast-iv" / "meta.yml"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace("nb: approved", "nb: machine_draft", 1),
        encoding="utf-8",
    )

    index, _ = load_repository(tmp_path, collect_errors=False)
    search_index_path = write_student_site_search_index(index=index, language="nb", root=tmp_path)
    payload = json.loads(search_index_path.read_text(encoding="utf-8"))

    assert all(entry["id"] != "angrist-podcast-iv" for entry in payload["entries"])
    assert all(entry["id"] != "iv-candidate-newsletter" for entry in payload["entries"])


def test_student_build_rejects_stale_resource_page() -> None:
    from app.build import BuildError

    with pytest.raises(BuildError):
        build_target(
            "iv-policy-brief-stale",
            audience="student",
            language="en",
            output_format="html",
            root=REPO_ROOT,
        )


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)

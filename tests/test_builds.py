from __future__ import annotations

import json
import shutil
from pathlib import Path

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
    assert "Resources" in html
    assert "Search LearnForge" in html
    assert "Breadcrumbs:" in html
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
    assert "Language:" in html
    assert "Norsk" in html
    assert "Sjekk av IV-intuisjon" not in html


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


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)

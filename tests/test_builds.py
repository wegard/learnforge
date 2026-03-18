from __future__ import annotations

import json

from app.build import build_target
from app.config import REPO_ROOT


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
    assert "Prompt the room" not in student_html
    assert "Related content" in student_html
    assert build_manifest["target"]["identifier"] == "iv-intuition"
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
    assert "Resources" in html
    assert "../../listing/topic-causal-inference/topic-causal-inference.html" in html
    assert "../../listing/resources-ec202/resources-ec202.html" in html
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
    assert any(
        edge["relationship"] == "topic-match" for edge in dependency_manifest["dependency_edges"]
    )
    assert leakage_report["status"] == "clean"

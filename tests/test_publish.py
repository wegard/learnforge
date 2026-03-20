from __future__ import annotations

import json
import shutil
from pathlib import Path

import app.build as build_module
import app.publish as publish_module
from app.build import StudentSiteTarget, student_site_targets, write_student_site_search_index
from app.config import REPO_ROOT
from app.indexer import load_repository
from app.publish import publish_student_site


def test_student_site_targets_match_search_index_surface(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    index, _ = load_repository(tmp_path, collect_errors=False)

    targets = student_site_targets(index=index, language="en")
    search_index_path = write_student_site_search_index(index=index, language="en", root=tmp_path)
    payload = json.loads(search_index_path.read_text(encoding="utf-8"))

    assert [(target.target_id, target.target_kind) for target in targets] == [
        (entry["id"], entry["kind"]) for entry in payload["entries"]
    ]


def test_student_site_targets_exclude_non_publishable_nb_content(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    meta_path = tmp_path / "content" / "resources" / "angrist-podcast-iv" / "meta.yml"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace("nb: approved", "nb: machine_draft", 1),
        encoding="utf-8",
    )

    index, _ = load_repository(tmp_path, collect_errors=False)
    target_ids = {target.target_id for target in student_site_targets(index=index, language="nb")}

    assert "home" in target_ids
    assert "ec202" in target_ids
    assert "resource-inbox" not in target_ids
    assert "iv-candidate-newsletter" not in target_ids
    assert "iv-reviewed-primer" not in target_ids
    assert "iv-policy-brief-stale" not in target_ids
    assert "angrist-podcast-iv" not in target_ids


def test_publish_student_site_writes_bundle_manifest_and_excludes_teacher_outputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    copy_repo_subset(tmp_path)

    def limited_targets(*, index, language):
        targets = [StudentSiteTarget(target_id="home", target_kind="home")]
        if language == "en":
            targets.append(StudentSiteTarget(target_id="ec202", target_kind="course"))
        return targets

    monkeypatch.setattr(build_module, "student_site_targets", limited_targets)
    monkeypatch.setattr(publish_module, "student_site_targets", limited_targets)

    artifact = publish_student_site(root=tmp_path)
    manifest = json.loads(artifact.manifest_path.read_text(encoding="utf-8"))
    chooser_html = (artifact.publish_root / "index.html").read_text(encoding="utf-8")
    course_html = (artifact.publish_root / "en" / "course" / "ec202" / "ec202.html").read_text(
        encoding="utf-8"
    )

    assert artifact.publish_root == tmp_path / "build" / "publish" / "student-site"
    assert artifact.manifest_path == (
        tmp_path / "build" / "reports" / "publish" / "student-site" / "publish-manifest.json"
    )
    assert artifact.languages == ("en", "nb")
    assert (artifact.publish_root / "en" / "index.html").exists()
    assert (artifact.publish_root / "nb" / "index.html").exists()
    assert (artifact.publish_root / "en" / "assets" / "learnforge-shell.css").exists()
    assert (artifact.publish_root / "en" / "assets" / "search-index.json").exists()
    assert "English" in chooser_html
    assert "Norsk bokmål" in chooser_html
    assert "../../assets/learnforge-shell.css" in course_html
    assert "../../assets/search-index.json" in course_html
    assert manifest["languages"] == ["en", "nb"]
    assert manifest["exclusions"]["audiences_excluded"] == ["teacher"]
    assert manifest["exclusions"]["formats_excluded"] == [
        "pdf",
        "revealjs",
        "slides-pdf",
        "handout",
        "exercise-sheet",
    ]
    assert manifest["language_details"][0]["source_export_root"] == "build/exports/student/en/html"
    assert manifest["language_details"][0]["target_kind_counts"]["course"] == 1
    assert (artifact.publish_root / ".nojekyll").exists()
    assert not (artifact.publish_root / "teacher").exists()
    assert not any("exercise-sheet" in str(path) for path in artifact.publish_root.rglob("*"))


def test_publish_student_site_single_language_builds_single_public_root(
    tmp_path: Path,
    monkeypatch,
) -> None:
    copy_repo_subset(tmp_path)

    def home_only_targets(*, index, language):
        return [StudentSiteTarget(target_id="home", target_kind="home")]

    monkeypatch.setattr(build_module, "student_site_targets", home_only_targets)
    monkeypatch.setattr(publish_module, "student_site_targets", home_only_targets)

    artifact = publish_student_site(languages=("en",), root=tmp_path)
    chooser_html = (artifact.publish_root / "index.html").read_text(encoding="utf-8")

    assert artifact.languages == ("en",)
    assert (artifact.publish_root / "en" / "index.html").exists()
    assert not (artifact.publish_root / "nb").exists()
    assert "English" in chooser_html
    assert "Norsk bokmål" not in chooser_html


def test_publish_workflow_uses_manual_dispatch_and_publish_artifacts() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "publish-student-site.yml").read_text(
        encoding="utf-8"
    )

    assert "workflow_dispatch:" in workflow
    assert "teach publish" in workflow
    assert "build/publish/student-site/" in workflow
    assert "build/reports/publish/student-site/" in workflow
    assert "upload-pages-artifact" in workflow
    assert "deploy-pages" in workflow


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)

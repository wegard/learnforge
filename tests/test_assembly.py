from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app.assembly import AssemblyError, assemble_target
from app.config import REPO_ROOT
from app.indexer import load_repository


def test_collection_assembly_expands_items_from_ids() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert assembly.target.kind == "collection"
    assert edge_targets == [
        "iv-intuition",
        "iv-dag-figure",
        "ex-iv-concept-check",
        "angrist-podcast-iv",
    ]
    assert "## Why IV shows up at all" in assembly.markdown
    assert "## Why this resource is on the list" in assembly.markdown


def test_collection_assembly_updates_when_object_changes(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)

    index, _ = load_repository(tmp_path, collect_errors=False)
    original = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="html",
        root=tmp_path,
    )

    concept_note = tmp_path / "content" / "concepts" / "iv-intuition" / "note.en.qmd"
    concept_note.write_text(
        concept_note.read_text(encoding="utf-8").replace(
            "An instrument gives you variation in treatment",
            "A revised instrument explanation gives you variation in treatment",
        ),
        encoding="utf-8",
    )

    refreshed_index, _ = load_repository(tmp_path, collect_errors=False)
    refreshed = assemble_target(
        "lecture-04",
        index=refreshed_index,
        audience="teacher",
        language="en",
        output_format="html",
        root=tmp_path,
    )

    assert "A revised instrument explanation" not in original.markdown
    assert "A revised instrument explanation" in refreshed.markdown


def test_topic_listing_matches_snapshot() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "topic-causal-inference",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    snapshot = (
        REPO_ROOT / "tests" / "snapshots" / "topic-causal-inference.student.en.html.qmd"
    ).read_text(encoding="utf-8").rstrip()

    assert topic_snapshot_fragment(assembly.markdown) == snapshot


def test_resource_page_generates_related_content() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "angrist-podcast-iv",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert "iv-intuition" in related_ids
    assert "lecture-04" in related_ids
    assert "## Related links" in assembly.markdown


def test_home_page_assembly_includes_course_and_topic_navigation() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "home",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    assert assembly.target.kind == "home"
    assert "## Browse by Course" in assembly.markdown
    assert "## Browse by Topic" in assembly.markdown
    assert "course/ec202/ec202.html" in assembly.markdown
    assert "listing/topic-causal-inference/topic-causal-inference.html" in assembly.markdown


def test_language_switch_falls_back_when_counterpart_is_not_approved(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    meta_path = tmp_path / "content" / "resources" / "angrist-podcast-iv" / "meta.yml"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace("nb: approved", "nb: machine_draft", 1),
        encoding="utf-8",
    )

    index, _ = load_repository(tmp_path, collect_errors=False)
    assembly = assemble_target(
        "angrist-podcast-iv",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=tmp_path,
    )

    assert "Norsk home" in assembly.markdown
    assert "build/exports/student/nb/html/resource/angrist-podcast-iv" not in assembly.markdown

    with pytest.raises(AssemblyError):
        assemble_target(
            "angrist-podcast-iv",
            index=index,
            audience="student",
            language="nb",
            output_format="html",
            root=tmp_path,
        )


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)


def topic_snapshot_fragment(markdown: str) -> str:
    start = markdown.index("Topic: Causal Inference")
    end = markdown.index('<footer class="lf-page-footer">')
    return markdown[start:end].rstrip()

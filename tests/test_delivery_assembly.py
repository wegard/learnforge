from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

from app.assembly import DeliveryContext, assemble_target
from app.config import REPO_ROOT
from app.indexer import load_repository


def copy_repo_subset(target_root: Path) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)


def test_delivery_context_injects_date_into_frontmatter(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    index, _ = load_repository(tmp_path, collect_errors=False)
    context = DeliveryContext(
        date=date(2026, 1, 20),
        term="spring-2026",
        manifest_id="ec202-spring-2026",
    )
    doc = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="html",
        root=tmp_path,
        delivery_context=context,
    )
    assert "date: '2026-01-20'" in doc.markdown


def test_delivery_context_without_date_has_no_date_field(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    index, _ = load_repository(tmp_path, collect_errors=False)
    doc = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="html",
        root=tmp_path,
    )
    assert "date:" not in doc.markdown.split("---")[1]


def test_delivery_context_removes_items(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    index, _ = load_repository(tmp_path, collect_errors=False)

    # First check the item is present without context
    doc_normal = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=tmp_path,
    )
    assert "iv-dag-figure" in doc_normal.markdown or "IV DAG" in doc_normal.markdown

    # Now remove it
    context = DeliveryContext(
        date=date(2026, 1, 20),
        term="spring-2026",
        manifest_id="ec202-spring-2026",
        removals=["iv-dag-figure"],
    )
    doc = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=tmp_path,
        delivery_context=context,
    )
    # The figure content should not appear in the assembled document
    assert "iv-dag-figure" not in str(doc.listing_entries)


def test_delivery_context_adds_items(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    index, _ = load_repository(tmp_path, collect_errors=False)

    # ex-iv-assumption-sort is not in lecture-04 items, but exists as an exercise
    context = DeliveryContext(
        date=date(2026, 1, 20),
        term="spring-2026",
        manifest_id="ec202-spring-2026",
        additions=["ex-iv-assumption-sort"],
    )
    doc = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=tmp_path,
        delivery_context=context,
    )
    # The added item should appear in the listing entries
    item_ids = [entry.identifier for entry in doc.listing_entries]
    assert "ex-iv-assumption-sort" in item_ids


def test_delivery_context_overrides_title(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    index, _ = load_repository(tmp_path, collect_errors=False)
    context = DeliveryContext(
        date=date(2026, 1, 20),
        term="spring-2026",
        manifest_id="ec202-spring-2026",
        title_override="Custom Lecture Title",
    )
    doc = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=tmp_path,
        delivery_context=context,
    )
    assert "Custom Lecture Title" in doc.markdown
    assert doc.target.title == "Custom Lecture Title"


def test_delivery_context_empty_does_not_change_output(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    index, _ = load_repository(tmp_path, collect_errors=False)

    doc_normal = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=tmp_path,
    )
    context = DeliveryContext(
        date=date(2026, 1, 20),
        term="spring-2026",
        manifest_id="ec202-spring-2026",
    )
    doc_delivery = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=tmp_path,
        delivery_context=context,
    )
    # Same listing entries
    normal_ids = [e.identifier for e in doc_normal.listing_entries]
    delivery_ids = [e.identifier for e in doc_delivery.listing_entries]
    assert normal_ids == delivery_ids


def test_delivery_output_root_changes_planned_path(tmp_path: Path) -> None:
    copy_repo_subset(tmp_path)
    index, _ = load_repository(tmp_path, collect_errors=False)
    delivery_root = tmp_path / "build" / "deliveries" / "ec202-spring-2026"
    context = DeliveryContext(
        date=date(2026, 1, 20),
        term="spring-2026",
        manifest_id="ec202-spring-2026",
    )
    doc = assemble_target(
        "lecture-04",
        index=index,
        audience="teacher",
        language="en",
        output_format="revealjs",
        root=tmp_path,
        delivery_context=context,
        delivery_output_root=delivery_root,
    )
    assert "deliveries/ec202-spring-2026" in str(doc.planned_output_path)

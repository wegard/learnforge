from __future__ import annotations

import shutil
from datetime import date

from app.config import REPO_ROOT
from app.models import Concept, Exercise, Resource
from app.tui.data import (
    load_tui_index,
    needs_attention,
)

# ---------------------------------------------------------------------------
# Payload helpers — minimal valid payloads for model construction
# ---------------------------------------------------------------------------


def _concept_payload(**overrides):
    base = {
        "id": "test-concept",
        "kind": "concept",
        "status": "approved",
        "visibility": "student",
        "languages": ["en"],
        "title": {"en": "Test concept"},
        "courses": [],
        "topics": [],
        "tags": [],
        "outputs": ["html"],
        "owners": ["vegard"],
        "updated": date(2026, 3, 18),
        "translation_status": {"en": "approved"},
        "ai": {"generated_fields": []},
        "level": "intermediate",
        "prerequisites": [],
        "related": [],
    }
    base.update(overrides)
    return base


def _exercise_payload(**overrides):
    base = {
        "id": "test-exercise",
        "kind": "exercise",
        "status": "approved",
        "visibility": "student",
        "languages": ["en"],
        "title": {"en": "Test exercise"},
        "courses": [],
        "topics": [],
        "tags": [],
        "outputs": ["html"],
        "owners": ["vegard"],
        "updated": date(2026, 3, 18),
        "translation_status": {"en": "approved"},
        "ai": {"generated_fields": []},
        "exercise_type": "conceptual",
        "difficulty": "easy",
        "estimated_time_minutes": 5,
        "concepts": [],
        "solution_storage": "separate-file",
        "solution_visibility": "teacher",
    }
    base.update(overrides)
    return base


def _resource_payload(**overrides):
    base = {
        "id": "test-resource",
        "kind": "resource",
        "status": "published",
        "visibility": "student",
        "languages": ["en"],
        "title": {"en": "Test resource"},
        "courses": ["ec202"],
        "topics": [],
        "tags": [],
        "outputs": ["html"],
        "owners": ["vegard"],
        "updated": date(2026, 3, 18),
        "translation_status": {"en": "approved"},
        "ai": {"generated_fields": []},
        "resource_kind": "article",
        "authors": ["vegard"],
        "published_on": date(2026, 3, 1),
        "url": "https://example.org/test",
        "difficulty": "introductory",
        "estimated_time_minutes": 10,
        "summary": {"en": "Summary"},
        "why_selected": {"en": "Reason"},
        "freshness": "evergreen",
        "approved_by": "vegard",
        "approved_on": date(2026, 3, 18),
        "approval_history": [
            {"action": "approved", "by": "vegard", "acted_on": "2026-03-18"},
        ],
        "stale_flag": False,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Unit tests — needs_attention()
# ---------------------------------------------------------------------------


def test_needs_attention_returns_draft_for_draft_concept() -> None:
    model = Concept.model_validate(_concept_payload(status="draft"))
    assert needs_attention(model) == ["draft"]


def test_needs_attention_returns_empty_for_approved_concept() -> None:
    model = Concept.model_validate(_concept_payload(status="approved"))
    assert needs_attention(model) == []


def test_needs_attention_returns_review_for_review_exercise() -> None:
    model = Exercise.model_validate(_exercise_payload(status="review"))
    assert needs_attention(model) == ["review"]


def test_needs_attention_returns_candidate_for_candidate_resource() -> None:
    model = Resource.model_validate(
        _resource_payload(
            status="candidate",
            approved_by=None,
            approved_on=None,
            summary={},
            why_selected={},
        )
    )
    assert needs_attention(model) == ["candidate"]


def test_needs_attention_returns_reviewed_for_reviewed_resource() -> None:
    model = Resource.model_validate(
        _resource_payload(
            status="reviewed",
            approved_by=None,
            approved_on=None,
            summary={},
            why_selected={},
        )
    )
    assert needs_attention(model) == ["reviewed"]


def test_needs_attention_returns_stale_for_flagged_resource() -> None:
    model = Resource.model_validate(_resource_payload(stale_flag=True))
    assert "stale" in needs_attention(model)


def test_needs_attention_returns_stale_for_overdue_resource() -> None:
    model = Resource.model_validate(
        _resource_payload(
            freshness="time-sensitive",
            review_after=date(2026, 1, 1),
        )
    )
    assert "stale" in needs_attention(model, today=date(2026, 3, 24))


def test_needs_attention_returns_empty_for_published_resource() -> None:
    model = Resource.model_validate(_resource_payload())
    assert needs_attention(model) == []


# ---------------------------------------------------------------------------
# Integration tests — load_tui_index()
# ---------------------------------------------------------------------------


def test_load_tui_index_excludes_archived_courses() -> None:
    tui_index = load_tui_index(REPO_ROOT)
    course_ids = {c.model.id for c in tui_index.active_courses}
    assert "ec202" not in course_ids
    assert "tem00uu" not in course_ids


def test_load_tui_index_includes_approved_courses() -> None:
    tui_index = load_tui_index(REPO_ROOT)
    course_ids = {c.model.id for c in tui_index.active_courses}
    assert "edi3400" in course_ids
    assert "tem0052" in course_ids
    assert "gra4164" in course_ids
    assert "gra4150" in course_ids


def test_load_tui_index_sorts_courses_by_id() -> None:
    tui_index = load_tui_index(REPO_ROOT)
    ids = [c.model.id for c in tui_index.active_courses]
    assert ids == sorted(ids)


def test_load_tui_index_attention_bubbles_to_collections(tmp_path) -> None:
    copy_repo_subset(tmp_path)
    # Force a concept to draft status so it triggers attention
    meta_path = tmp_path / "content" / "concepts" / "iv-intuition" / "meta.yml"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace("status: approved", "status: draft", 1),
        encoding="utf-8",
    )

    tui_index = load_tui_index(tmp_path)

    assert "iv-intuition" in tui_index.attention_items
    # lecture-04 contains iv-intuition
    assert tui_index.collection_attention_counts.get("lecture-04", 0) > 0


def test_load_tui_index_attention_bubbles_to_courses(tmp_path) -> None:
    copy_repo_subset(tmp_path)
    meta_path = tmp_path / "content" / "concepts" / "iv-intuition" / "meta.yml"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace("status: approved", "status: draft", 1),
        encoding="utf-8",
    )

    tui_index = load_tui_index(tmp_path)

    # ec202 is archived, but iv-intuition is also in other courses' collections
    # The course that has lecture-04 in its plan should have a non-zero count
    assert any(count > 0 for count in tui_index.course_attention_counts.values())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def copy_repo_subset(target_root) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)
    shutil.copy(
        REPO_ROOT / "representative-targets.yml",
        target_root / "representative-targets.yml",
    )

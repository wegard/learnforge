from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from app.config import REPO_ROOT
from app.indexer import IndexedCourse, RepositoryIndex, load_repository
from app.models import Collection, Resource
from app.resource_workflow import resource_is_stale


@dataclass(slots=True)
class AttentionItem:
    object_id: str
    kind: str
    title: str
    reasons: list[str]
    course_ids: list[str]


@dataclass(slots=True)
class TUIIndex:
    repo_index: RepositoryIndex
    active_courses: list[IndexedCourse]
    attention_items: dict[str, AttentionItem]
    collection_attention_counts: dict[str, int]
    course_attention_counts: dict[str, int]


def needs_attention(
    model: Resource | Collection | object, *, today: date | None = None
) -> list[str]:
    """Return attention reasons for an object, or an empty list."""
    reasons: list[str] = []

    if isinstance(model, Resource):
        if model.status in {"candidate", "reviewed"}:
            reasons.append(model.status)
        if resource_is_stale(model, today=today):
            reasons.append("stale")
    else:
        if hasattr(model, "status") and model.status in {"draft", "review"}:
            reasons.append(model.status)

    return reasons


def load_tui_index(root: Path = REPO_ROOT, *, today: date | None = None) -> TUIIndex:
    """Load and pre-process repository data for TUI display."""
    reference_date = today or date.today()
    repo_index, _ = load_repository(root, collect_errors=True)

    active_courses = sorted(
        [c for c in repo_index.courses.values() if c.model.status != "archived"],
        key=lambda c: c.model.id,
    )

    attention_items: dict[str, AttentionItem] = {}
    for obj_id, obj in repo_index.objects.items():
        reasons = needs_attention(obj.model, today=reference_date)
        if reasons:
            title = obj.model.title.get("en") or next(iter(obj.model.title.values()), obj_id)
            attention_items[obj_id] = AttentionItem(
                object_id=obj_id,
                kind=obj.model.kind,
                title=title,
                reasons=reasons,
                course_ids=list(obj.model.courses),
            )

    collection_attention_counts: dict[str, int] = {}
    for obj_id, obj in repo_index.objects.items():
        if isinstance(obj.model, Collection):
            count = sum(1 for item_id in obj.model.items if item_id in attention_items)
            if count > 0:
                collection_attention_counts[obj_id] = count

    course_attention_counts: dict[str, int] = {}
    for course in active_courses:
        all_collection_ids = list(course.plan.lectures) + list(course.plan.assignments)
        flagged: set[str] = set()
        for coll_id in all_collection_ids:
            if coll_id in attention_items:
                flagged.add(coll_id)
            coll_obj = repo_index.objects.get(coll_id)
            if coll_obj is not None and isinstance(coll_obj.model, Collection):
                for item_id in coll_obj.model.items:
                    if item_id in attention_items:
                        flagged.add(item_id)
        if flagged:
            course_attention_counts[course.model.id] = len(flagged)

    return TUIIndex(
        repo_index=repo_index,
        active_courses=active_courses,
        attention_items=attention_items,
        collection_attention_counts=collection_attention_counts,
        course_attention_counts=course_attention_counts,
    )

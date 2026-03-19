from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from app.config import REPO_ROOT
from app.indexer import IndexedCourse, IndexedObject, load_repository
from app.models import Collection, Exercise


@dataclass(slots=True)
class TranslationStatusEntry:
    identifier: str
    kind: str
    languages: list[str]
    translation_status: str
    note_exists: bool | None
    solution_exists: bool | None
    source_word_count_nb: int | None
    path: str


def build_course_translation_report(
    course_id: str,
    *,
    language: str,
    root: Path = REPO_ROOT,
) -> dict[str, object]:
    index, _ = load_repository(root, collect_errors=False)
    course_record = index.courses.get(course_id)
    if course_record is None:
        raise ValueError(f"unknown course id: {course_id}")

    entries = [_course_status_entry(course_record, language=language, root=root)]
    for record in _ordered_course_objects(course_record, index.objects):
        entries.append(_object_status_entry(record, language=language, root=root))

    approved_count = sum(1 for entry in entries if entry.translation_status == "approved")
    return {
        "course_id": course_id,
        "language": language,
        "entry_count": len(entries),
        "approved_count": approved_count,
        "missing_count": len(entries) - approved_count,
        "entries": [asdict(entry) for entry in entries],
    }


def _ordered_course_objects(
    course_record: IndexedCourse,
    objects: dict[str, IndexedObject],
) -> list[IndexedObject]:
    ordered: list[IndexedObject] = []
    seen: set[str] = set()

    def add(identifier: str) -> None:
        if identifier in seen or identifier not in objects:
            return
        ordered.append(objects[identifier])
        seen.add(identifier)

    for collection_id in [*course_record.plan.lectures, *course_record.plan.assignments]:
        add(collection_id)
        collection_record = objects.get(collection_id)
        if (
            collection_record is None
            or not isinstance(collection_record.model, Collection)
        ):
            continue
        for item_id in collection_record.model.items:
            add(item_id)

    remaining = sorted(
        (
            record
            for record in objects.values()
            if course_record.model.id in record.model.courses and record.model.id not in seen
        ),
        key=lambda record: (
            _kind_sort_key(record),
            record.model.id,
        ),
    )
    ordered.extend(remaining)
    return ordered


def _kind_sort_key(record: IndexedObject) -> tuple[int, str]:
    kind = _entry_kind(record)
    order = {
        "lecture": 0,
        "assignment": 1,
        "concept": 2,
        "exercise": 3,
        "resource": 4,
        "figure": 5,
        "module": 6,
        "reading-list": 7,
        "collection": 8,
    }
    return order.get(kind, 99), kind


def _course_status_entry(
    record: IndexedCourse,
    *,
    language: str,
    root: Path,
) -> TranslationStatusEntry:
    syllabus_exists = record.syllabus_path(language).exists()
    translation_status = (
        "approved"
        if language in record.model.languages and syllabus_exists
        else "missing"
    )
    return TranslationStatusEntry(
        identifier=record.model.id,
        kind="course",
        languages=list(record.model.languages),
        translation_status=translation_status,
        note_exists=syllabus_exists,
        solution_exists=None,
        source_word_count_nb=_word_count(record.syllabus_path("nb")),
        path=str(record.course_path.relative_to(root)),
    )


def _object_status_entry(
    record: IndexedObject,
    *,
    language: str,
    root: Path,
) -> TranslationStatusEntry:
    note_exists = None
    solution_exists = None
    if not isinstance(record.model, Collection):
        note_exists = record.note_path(language).exists()
    if isinstance(record.model, Exercise):
        solution_exists = record.solution_path(language).exists()

    return TranslationStatusEntry(
        identifier=record.model.id,
        kind=_entry_kind(record),
        languages=list(record.model.languages),
        translation_status=record.model.translation_status.get(language, "missing"),
        note_exists=note_exists,
        solution_exists=solution_exists,
        source_word_count_nb=(
            None if isinstance(record.model, Collection) else _word_count(record.note_path("nb"))
        ),
        path=str(record.meta_path.relative_to(root)),
    )


def _entry_kind(record: IndexedObject) -> str:
    if isinstance(record.model, Collection):
        return record.model.collection_kind
    return record.model.kind


def _word_count(path: Path) -> int | None:
    if not path.exists():
        return None
    return len(path.read_text(encoding="utf-8").split())

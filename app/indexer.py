from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from app.config import (
    COLLECTION_DIRS,
    CONTENT_KIND_DIRS,
    REPO_ROOT,
    deliveries_dir,
    index_dir,
    object_note_filename,
    solution_note_filename,
)
from app.models import (
    Collection,
    Concept,
    ContentModel,
    CourseDefinition,
    CoursePlan,
    DeliveryManifest,
    Exercise,
    Figure,
    Resource,
)

MODEL_BY_KIND = {
    "concept": Concept,
    "exercise": Exercise,
    "figure": Figure,
    "resource": Resource,
    "collection": Collection,
}


@dataclass(slots=True)
class LoadError:
    path: Path
    message: str


@dataclass(slots=True)
class IndexedObject:
    directory: Path
    meta_path: Path
    model: ContentModel

    @property
    def id(self) -> str:
        return self.model.id

    def note_path(self, language: str) -> Path:
        return self.directory / object_note_filename(language)

    def solution_path(self, language: str) -> Path:
        if not isinstance(self.model, Exercise):
            raise ValueError(f"{self.model.id} is not an exercise")
        return self.directory / solution_note_filename(language)


@dataclass(slots=True)
class IndexedCourse:
    directory: Path
    course_path: Path
    plan_path: Path
    model: CourseDefinition
    plan: CoursePlan

    @property
    def id(self) -> str:
        return self.model.id

    def syllabus_path(self, language: str) -> Path:
        return self.directory / f"syllabus.{language}.qmd"


@dataclass(slots=True)
class IndexedDelivery:
    manifest_path: Path
    model: DeliveryManifest

    @property
    def id(self) -> str:
        return self.model.id


@dataclass(slots=True)
class RepositoryIndex:
    objects: dict[str, IndexedObject]
    courses: dict[str, IndexedCourse]
    deliveries: dict[str, IndexedDelivery]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("expected a mapping at the document root")
    return data


def iter_object_meta_paths(root: Path = REPO_ROOT) -> list[Path]:
    paths: list[Path] = []
    for relative_dir in CONTENT_KIND_DIRS.values():
        paths.extend(sorted((root / relative_dir).glob("*/meta.yml")))
    for relative_dir in COLLECTION_DIRS.values():
        paths.extend(sorted((root / relative_dir).glob("*/meta.yml")))
    return paths


def iter_course_paths(root: Path = REPO_ROOT) -> list[Path]:
    return sorted(
        path
        for path in (root / "courses").glob("*/course.yml")
        if (path.parent / "plan.yml").exists()
    )


def iter_delivery_paths(root: Path = REPO_ROOT) -> list[Path]:
    path = deliveries_dir(root)
    if not path.exists():
        return []
    return sorted(path.glob("*.yml"))


def load_repository(
    root: Path = REPO_ROOT,
    *,
    collect_errors: bool = False,
) -> tuple[RepositoryIndex, list[LoadError]]:
    objects: dict[str, IndexedObject] = {}
    courses: dict[str, IndexedCourse] = {}
    errors: list[LoadError] = []

    for meta_path in iter_object_meta_paths(root):
        try:
            payload = load_yaml(meta_path)
            kind = payload.get("kind")
            model_cls = MODEL_BY_KIND.get(kind)
            if model_cls is None:
                raise ValueError(f"unsupported object kind: {kind!r}")
            model = model_cls.model_validate(payload)
            if model.id in objects:
                raise ValueError(f"duplicate object id: {model.id}")
            objects[model.id] = IndexedObject(
                directory=meta_path.parent,
                meta_path=meta_path,
                model=model,
            )
        except (OSError, ValueError, ValidationError) as exc:
            errors.append(LoadError(path=meta_path, message=str(exc)))

    for course_path in iter_course_paths(root):
        plan_path = course_path.parent / "plan.yml"
        try:
            course_model = CourseDefinition.model_validate(load_yaml(course_path))
            plan_model = CoursePlan.model_validate(load_yaml(plan_path))
            if course_model.id in courses:
                raise ValueError(f"duplicate course id: {course_model.id}")
            courses[course_model.id] = IndexedCourse(
                directory=course_path.parent,
                course_path=course_path,
                plan_path=plan_path,
                model=course_model,
                plan=plan_model,
            )
        except (OSError, ValueError, ValidationError) as exc:
            errors.append(LoadError(path=course_path, message=str(exc)))

    deliveries: dict[str, IndexedDelivery] = {}
    for manifest_path in iter_delivery_paths(root):
        try:
            model = DeliveryManifest.model_validate(load_yaml(manifest_path))
            if model.id in deliveries:
                raise ValueError(f"duplicate delivery id: {model.id}")
            deliveries[model.id] = IndexedDelivery(
                manifest_path=manifest_path,
                model=model,
            )
        except (OSError, ValueError, ValidationError) as exc:
            errors.append(LoadError(path=manifest_path, message=str(exc)))

    if errors and not collect_errors:
        first_error = errors[0]
        raise ValueError(f"{first_error.path}: {first_error.message}")

    return RepositoryIndex(objects=objects, courses=courses, deliveries=deliveries), errors


def write_search_index(index: RepositoryIndex, root: Path = REPO_ROOT) -> Path:
    payload = {
        "objects": [
            {
                "id": record.model.id,
                "kind": record.model.kind,
                "title": record.model.title,
                "topics": record.model.topics,
                "tags": record.model.tags,
                "courses": record.model.courses,
                "path": str(record.directory.relative_to(root)),
            }
            for record in sorted(index.objects.values(), key=lambda item: item.model.id)
        ],
        "courses": [
            {
                "id": record.model.id,
                "title": record.model.title,
                "summary": record.model.summary,
                "path": str(record.directory.relative_to(root)),
            }
            for record in sorted(index.courses.values(), key=lambda item: item.model.id)
        ],
    }
    index_dir(root).mkdir(parents=True, exist_ok=True)
    output_path = root / "build" / "index" / "content-index.json"
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.assembly import (
    SOLUTION_BLOCK_MARKER,
    AssemblyDocument,
    AssemblyError,
    assemble_target,
    collect_topics,
    humanize_slug,
    planned_target_output_path,
    student_search_index_path,
)
from app.config import REPO_ROOT, exports_dir, reports_dir
from app.indexer import IndexedObject, RepositoryIndex, load_repository
from app.models import Collection, Resource

RenderableFormat = Literal["html", "pdf", "revealjs", "handout", "exercise-sheet"]

FORMAT_TO_QUARTO = {
    "html": "html",
    "pdf": "pdf",
    "revealjs": "revealjs",
    "handout": "pdf",
    "exercise-sheet": "pdf",
}


@dataclass(slots=True)
class BuildArtifact:
    target_id: str
    target_kind: str
    output_format: str
    audience: str
    language: str
    source_path: Path
    output_path: Path
    command: list[str]
    build_manifest_path: Path
    dependency_manifest_path: Path
    leakage_report_path: Path
    search_index_path: Path | None = None


class BuildError(RuntimeError):
    pass


def build_target(
    target_id: str,
    *,
    audience: str,
    language: str,
    output_format: RenderableFormat,
    root: Path = REPO_ROOT,
) -> BuildArtifact:
    index, errors = load_repository(root, collect_errors=False)
    if errors:
        raise BuildError("repository contains load errors")

    try:
        assembly = assemble_target(
            target_id,
            index=index,
            audience=audience,
            language=language,
            output_format=output_format,
            root=root,
        )
    except AssemblyError as exc:
        raise BuildError(str(exc)) from exc

    output_dir = assembly.planned_output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_name = assembly.planned_output_path.name
    command = [
        "quarto",
        "render",
        str(assembly.generated_path.relative_to(root)),
        "--profile",
        f"{audience},{language}",
        "--to",
        FORMAT_TO_QUARTO[output_format],
        "--output",
        output_name,
        "--output-dir",
        str(output_dir.relative_to(root)),
    ]

    result = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        env=build_env(root),
    )
    if result.returncode != 0:
        raise BuildError(result.stderr.strip() or result.stdout.strip() or "quarto render failed")

    sync_site_libs(root, output_dir)
    output_path = assembly.planned_output_path
    search_index_path = None
    if audience == "student" and output_format == "html":
        search_index_path = write_student_site_search_index(
            index=index, language=language, root=root
        )
    build_manifest_path, dependency_manifest_path, leakage_report_path = write_build_reports(
        assembly=assembly,
        command=command,
        output_path=output_path,
        search_index_path=search_index_path,
        root=root,
    )

    return BuildArtifact(
        target_id=target_id,
        target_kind=assembly.target.kind,
        output_format=output_format,
        audience=audience,
        language=language,
        source_path=assembly.generated_path,
        output_path=output_path,
        command=command,
        build_manifest_path=build_manifest_path,
        dependency_manifest_path=dependency_manifest_path,
        leakage_report_path=leakage_report_path,
        search_index_path=search_index_path,
    )


def build_env(root: Path) -> dict[str, str]:
    cache_dir = root / "build" / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (root / "site_libs" / "quarto-search").mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("QUARTO_CACHE_DIR", str(cache_dir))
    env.setdefault("XDG_CACHE_HOME", str(cache_dir))
    return env


def sync_site_libs(root: Path, output_dir: Path) -> None:
    source_candidates = [
        output_dir / "site_libs",
        root / "site_libs",
    ]
    source = next((candidate for candidate in source_candidates if candidate.exists()), None)
    if source is None:
        return
    destination = root / "build" / "site_libs"
    shutil.copytree(source, destination, dirs_exist_ok=True)


def write_build_reports(
    *,
    assembly: AssemblyDocument,
    command: list[str],
    output_path: Path,
    search_index_path: Path | None,
    root: Path,
) -> tuple[Path, Path, Path]:
    report_dir = (
        reports_dir(root)
        / "builds"
        / assembly.audience
        / assembly.language
        / assembly.output_format
        / assembly.target.output_category
        / assembly.target.identifier
    )
    report_dir.mkdir(parents=True, exist_ok=True)

    build_manifest_path = report_dir / "build-manifest.json"
    dependency_manifest_path = report_dir / "dependency-manifest.json"
    leakage_report_path = report_dir / "teacher-leakage-report.json"

    build_manifest_payload = assembly.build_manifest_payload()
    generated_artifacts = collect_generated_artifacts(assembly=assembly, root=root)
    build_manifest_payload.update(
        {
            "command": command,
            "output_path": str(output_path.relative_to(root)),
            "build_manifest_path": str(build_manifest_path.relative_to(root)),
            "dependency_manifest_path": str(dependency_manifest_path.relative_to(root)),
            "leakage_report_path": str(leakage_report_path.relative_to(root)),
            "search_index_path": (
                str(search_index_path.relative_to(root)) if search_index_path else None
            ),
            "generated_artifacts": generated_artifacts,
        }
    )
    assignment_details = assignment_manifest_details(assembly, generated_artifacts)
    if assignment_details is not None:
        build_manifest_payload["assignment"] = assignment_details
    dependency_manifest_payload = assembly.dependency_manifest_payload()
    leakage_report_payload = build_leakage_report(assembly, output_path, root)

    build_manifest_path.write_text(
        json.dumps(build_manifest_payload, indent=2),
        encoding="utf-8",
    )
    dependency_manifest_path.write_text(
        json.dumps(dependency_manifest_payload, indent=2),
        encoding="utf-8",
    )
    leakage_report_path.write_text(
        json.dumps(leakage_report_payload, indent=2),
        encoding="utf-8",
    )
    return build_manifest_path, dependency_manifest_path, leakage_report_path


def build_leakage_report(
    assembly: AssemblyDocument,
    output_path: Path,
    root: Path,
) -> dict[str, object]:
    generated_source_text = assembly.generated_path.read_text(encoding="utf-8")
    output_text = output_path.read_text(encoding="utf-8", errors="ignore")
    teacher_blocks_found = sum(item.teacher_blocks_found for item in assembly.leakage_observations)
    teacher_blocks_removed = sum(
        item.teacher_blocks_removed for item in assembly.leakage_observations
    )
    solution_files_found = len(assembly.solution_observations)
    solution_files_included = sum(
        1 for item in assembly.solution_observations if item.included_in_output
    )

    generated_source_has_marker = (
        ".teacher-only" in generated_source_text or "teacher-only" in generated_source_text
    )
    output_has_marker = ".teacher-only" in output_text or "teacher-only" in output_text
    generated_source_has_solution_marker = SOLUTION_BLOCK_MARKER in generated_source_text
    output_has_solution_marker = SOLUTION_BLOCK_MARKER in output_text

    status = "not_applicable"
    if assembly.audience == "student":
        status = (
            "clean"
            if teacher_blocks_removed == teacher_blocks_found
            and not generated_source_has_marker
            and not output_has_marker
            and solution_files_included == 0
            and not generated_source_has_solution_marker
            and not output_has_solution_marker
            else "leak-detected"
        )

    return {
        "target": {
            "id": assembly.target.identifier,
            "kind": assembly.target.kind,
        },
        "audience": assembly.audience,
        "language": assembly.language,
        "format": assembly.output_format,
        "status": status,
        "teacher_blocks_found": teacher_blocks_found,
        "teacher_blocks_removed": teacher_blocks_removed,
        "solution_files_found": solution_files_found,
        "solution_files_included": solution_files_included,
        "generated_source_contains_teacher_marker": generated_source_has_marker,
        "output_contains_teacher_marker": output_has_marker,
        "generated_source_contains_solution_marker": generated_source_has_solution_marker,
        "output_contains_solution_marker": output_has_solution_marker,
        "generated_source_path": str(assembly.generated_path.relative_to(root)),
        "output_path": str(output_path.relative_to(root)),
        "details": [
            {
                "source_path": item.source_path,
                "teacher_blocks_found": item.teacher_blocks_found,
                "teacher_blocks_removed": item.teacher_blocks_removed,
                "student_blocks_found": item.student_blocks_found,
                "student_blocks_removed": item.student_blocks_removed,
            }
            for item in assembly.leakage_observations
        ],
        "solution_details": [
            {
                "exercise_id": item.exercise_id,
                "source_path": item.source_path,
                "visibility": item.visibility,
                "included_in_output": item.included_in_output,
                "reason": item.reason,
            }
            for item in assembly.solution_observations
        ],
    }


def write_student_site_search_index(
    *,
    index: RepositoryIndex,
    language: str,
    root: Path,
) -> Path:
    output_path = student_search_index_path(root, language)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    site_root = exports_dir(root) / "student" / language / "html"
    payload = {
        "language": language,
        "entries": [
            {
                "id": "home",
                "kind": "home",
                "title": "LearnForge",
                "description": (
                    "Browse courses, topics, and featured resources."
                    if language == "en"
                    else "Bla gjennom kurs, temaer og utvalgte ressurser."
                ),
                "topics": [],
                "tags": [],
                "courses": [],
                "href": str(
                    planned_target_output_path(
                        root,
                        audience="student",
                        language=language,
                        output_format="html",
                        target_kind="home",
                        target_id="home",
                    ).relative_to(site_root)
                ),
            },
            *course_search_entries(index=index, language=language, root=root, site_root=site_root),
            *object_search_entries(index=index, language=language, root=root, site_root=site_root),
            *topic_search_entries(index=index, language=language, root=root, site_root=site_root),
            *resource_listing_search_entries(
                index=index,
                language=language,
                root=root,
                site_root=site_root,
            ),
        ],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def course_search_entries(
    *,
    index: RepositoryIndex,
    language: str,
    root: Path,
    site_root: Path,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for record in sorted(index.courses.values(), key=lambda item: item.model.id):
        if record.model.visibility in {"private", "teacher"}:
            continue
        if record.model.status not in {"approved", "published"}:
            continue
        if language not in record.model.languages:
            continue
        entries.append(
            {
                "id": record.model.id,
                "kind": "course",
                "title": record.model.title[language],
                "description": record.model.summary[language],
                "topics": [],
                "tags": [],
                "courses": [record.model.id],
                "href": str(
                    planned_target_output_path(
                        root,
                        audience="student",
                        language=language,
                        output_format="html",
                        target_kind="course",
                        target_id=record.model.id,
                    ).relative_to(site_root)
                ),
            }
        )
    return entries


def object_search_entries(
    *,
    index: RepositoryIndex,
    language: str,
    root: Path,
    site_root: Path,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for record in sorted(index.objects.values(), key=lambda item: item.model.id):
        if not is_student_visible_in_language(record, language):
            continue
        if "html" not in record.model.outputs:
            continue
        kind = record.model.kind if record.model.kind != "collection" else "collection"
        description = ""
        if record.model.kind == "resource":
            description = record.model.why_selected[language]
        elif record.model.kind == "exercise":
            description = f"{record.model.exercise_type} exercise"
        elif record.model.kind == "concept":
            description = record.model.level
        elif record.model.kind == "figure":
            description = record.model.caption[language]
        elif isinstance(record.model, Collection):
            description = localized_collection_description(
                record.model.collection_kind,
                language=language,
                item_count=len(record.model.items),
            )
        entries.append(
            {
                "id": record.model.id,
                "kind": kind,
                "title": record.model.title[language],
                "description": description,
                "topics": record.model.topics,
                "tags": record.model.tags,
                "courses": record.model.courses,
                "href": str(
                    planned_target_output_path(
                        root,
                        audience="student",
                        language=language,
                        output_format="html",
                        target_kind=kind,
                        target_id=record.model.id,
                    ).relative_to(site_root)
                ),
            }
        )
    return entries


def topic_search_entries(
    *,
    index: RepositoryIndex,
    language: str,
    root: Path,
    site_root: Path,
) -> list[dict[str, object]]:
    visible_objects = [
        record
        for record in index.objects.values()
        if is_student_visible_in_language(record, language)
    ]
    entries: list[dict[str, object]] = []
    for topic in collect_topics(visible_objects):
        entries.append(
            {
                "id": f"topic-{topic}",
                "kind": "topic-listing",
                "title": humanize_slug(topic),
                "description": ("Topic listing" if language == "en" else "Temaoversikt"),
                "topics": [topic],
                "tags": [],
                "courses": sorted(
                    {
                        course_id
                        for record in visible_objects
                        if topic in record.model.topics
                        for course_id in record.model.courses
                    }
                ),
                "href": str(
                    planned_target_output_path(
                        root,
                        audience="student",
                        language=language,
                        output_format="html",
                        target_kind="topic-listing",
                        target_id=f"topic-{topic}",
                    ).relative_to(site_root)
                ),
            }
        )
    return entries


def resource_listing_search_entries(
    *,
    index: RepositoryIndex,
    language: str,
    root: Path,
    site_root: Path,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for course_record in sorted(index.courses.values(), key=lambda item: item.model.id):
        if course_record.model.visibility in {"private", "teacher"}:
            continue
        if course_record.model.status not in {"approved", "published"}:
            continue
        if language not in course_record.model.languages:
            continue
        has_resources = any(
            isinstance(record.model, Resource)
            and course_record.model.id in record.model.courses
            and is_student_visible_in_language(record, language)
            for record in index.objects.values()
        )
        if not has_resources:
            continue
        entries.append(
            {
                "id": f"resources-{course_record.model.id}",
                "kind": "resource-listing",
                "title": (
                    f"Resources for {course_record.model.title[language]}"
                    if language == "en"
                    else f"Ressurser for {course_record.model.title[language]}"
                ),
                "description": (
                    "Course resource listing" if language == "en" else "Kursressursoversikt"
                ),
                "topics": [],
                "tags": ["resources"],
                "courses": [course_record.model.id],
                "href": str(
                    planned_target_output_path(
                        root,
                        audience="student",
                        language=language,
                        output_format="html",
                        target_kind="resource-listing",
                        target_id=f"resources-{course_record.model.id}",
                    ).relative_to(site_root)
                ),
            }
        )
    return entries


def is_student_visible_in_language(record: IndexedObject, language: str) -> bool:
    if record.model.visibility in {"private", "teacher"}:
        return False
    if record.model.status not in {"approved", "published"}:
        return False
    if language not in record.model.languages:
        return False
    return record.model.translation_status.get(language) == "approved"


def collect_generated_artifacts(
    *,
    assembly: AssemblyDocument,
    root: Path,
) -> list[dict[str, str]]:
    candidate_formats = ["html", "pdf", "revealjs", "handout", "exercise-sheet"]
    if assembly.target.kind == "home":
        candidate_formats = ["html"]

    artifacts: list[dict[str, str]] = []
    for output_format in candidate_formats:
        output_path = planned_target_output_path(
            root,
            audience=assembly.audience,
            language=assembly.language,
            output_format=output_format,
            target_kind=assembly.target.kind,
            target_id=assembly.target.identifier,
        )
        if not output_path.exists():
            continue
        artifacts.append(
            {
                "format": output_format,
                "path": str(output_path.relative_to(root)),
            }
        )
    return artifacts


def assignment_manifest_details(
    assembly: AssemblyDocument,
    generated_artifacts: list[dict[str, str]],
) -> dict[str, object] | None:
    included_exercise_ids = sorted(
        {
            edge.target_id
            for edge in assembly.dependency_edges
            if edge.source_id == assembly.target.identifier
            and edge.relationship == "assignment-item"
        }
    )
    if not included_exercise_ids:
        return None

    return {
        "included_exercise_ids": included_exercise_ids,
        "course_context_ids": sorted(
            {
                edge.target_id
                for edge in assembly.dependency_edges
                if edge.source_id == assembly.target.identifier
                and edge.relationship == "used-in-course"
            }
        ),
        "linked_concept_ids": sorted(
            {
                edge.target_id
                for edge in assembly.dependency_edges
                if edge.source_id == assembly.target.identifier
                and edge.relationship == "assignment-concept"
            }
        ),
        "linked_resource_ids": sorted(
            {
                edge.target_id
                for edge in assembly.dependency_edges
                if edge.source_id == assembly.target.identifier
                and edge.relationship == "assignment-resource"
            }
        ),
        "discovered_solution_files": sorted(
            {item.source_path for item in assembly.solution_observations}
        ),
        "included_solution_files": sorted(
            {
                item.source_path
                for item in assembly.solution_observations
                if item.included_in_output
            }
        ),
        "generated_artifacts": generated_artifacts,
    }


def localized_collection_description(
    collection_kind: str,
    *,
    language: str,
    item_count: int,
) -> str:
    if language == "nb":
        labels = {
            "lecture": "Forelesning",
            "assignment": "Oppgaveark",
            "module": "Modul",
            "reading-list": "Leseliste",
        }
        return f"{labels.get(collection_kind, 'Samling')} med {item_count} innslag"

    labels = {
        "lecture": "Lecture",
        "assignment": "Assignment",
        "module": "Module",
        "reading-list": "Reading list",
    }
    return f"{labels.get(collection_kind, 'Collection')} with {item_count} items"

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import yaml

from app.config import REPO_ROOT, deliveries_build_dir, deliveries_dir
from app.indexer import (
    IndexedDelivery,
    RepositoryIndex,
    load_repository,
    load_yaml,
)
from app.models import DeliveryManifest


def scaffold_delivery(
    course_id: str,
    *,
    term: str,
    language: str = "en",
    start_date: date | None = None,
    root: Path = REPO_ROOT,
) -> Path:
    course_path = root / "courses" / course_id / "course.yml"
    plan_path = root / "courses" / course_id / "plan.yml"
    if not course_path.exists():
        raise ValueError(f"course {course_id} not found at {course_path}")
    if not plan_path.exists():
        raise ValueError(f"course plan not found at {plan_path}")

    plan_data = load_yaml(plan_path)
    lectures = plan_data.get("lectures", [])
    assignments = plan_data.get("assignments", [])

    manifest_id = f"{course_id}-{term}"
    out_dir = deliveries_dir(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / f"{manifest_id}.yml"
    if manifest_path.exists():
        raise ValueError(f"delivery manifest already exists: {manifest_path}")

    current_date = start_date or date.today()
    lecture_entries = []
    for lecture_id in lectures:
        lecture_entries.append(
            {
                "lecture": lecture_id,
                "date": current_date.isoformat(),
                "ready": False,
            }
        )
        current_date += timedelta(weeks=1)

    assignment_entries = []
    for assignment_id in assignments:
        assignment_entries.append(
            {
                "assignment": assignment_id,
                "due_date": current_date.isoformat(),
                "ready": False,
            }
        )
        current_date += timedelta(weeks=2)

    payload = {
        "id": manifest_id,
        "course": course_id,
        "term": term,
        "language": language,
        "status": "active",
        "created": date.today().isoformat(),
        "updated": date.today().isoformat(),
        "lectures": lecture_entries,
        "assignments": assignment_entries,
        "default_formats": ["html", "revealjs", "pdf", "handout"],
        "default_audiences": ["student", "teacher"],
    }
    manifest_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return manifest_path


def _load_delivery(
    manifest_id: str,
    *,
    root: Path = REPO_ROOT,
    index: RepositoryIndex | None = None,
) -> tuple[IndexedDelivery, RepositoryIndex]:
    if index is None:
        index, _ = load_repository(root, collect_errors=True)
    delivery = index.deliveries.get(manifest_id)
    if delivery is None:
        raise ValueError(f"delivery manifest not found: {manifest_id}")
    return delivery, index


def format_delivery_status(
    manifest_id: str,
    *,
    root: Path = REPO_ROOT,
    index: RepositoryIndex | None = None,
) -> str:
    delivery, index = _load_delivery(manifest_id, root=root, index=index)
    manifest = delivery.model
    course = index.courses.get(manifest.course)
    course_title = course.model.title.get("en", manifest.course) if course else manifest.course

    lines = [
        f"Delivery: {manifest.id} ({course_title})",
        f"Term: {manifest.term} | Language: {manifest.language} | Status: {manifest.status}",
        "",
    ]

    ready_lectures = 0
    total_lectures = len(manifest.lectures)
    next_unready = None

    if manifest.lectures:
        lines.append("Lectures:")
        for entry in manifest.lectures:
            record = index.objects.get(entry.lecture)
            title = (
                record.model.title.get(manifest.language, entry.lecture)
                if record
                else entry.lecture
            )
            icon = "\u2705" if entry.ready else "\u2b1c"
            status_label = "ready" if entry.ready else "not ready"
            lines.append(f"  {icon} {entry.date}  {entry.lecture}  {title}  [{status_label}]")
            if entry.ready:
                ready_lectures += 1
            elif next_unready is None:
                next_unready = f"{entry.lecture} ({entry.date})"
        lines.append("")

    ready_assignments = 0
    total_assignments = len(manifest.assignments)

    if manifest.assignments:
        lines.append("Assignments:")
        for entry in manifest.assignments:
            record = index.objects.get(entry.assignment)
            title = (
                record.model.title.get(manifest.language, entry.assignment)
                if record
                else entry.assignment
            )
            icon = "\u2705" if entry.ready else "\u2b1c"
            status_label = "ready" if entry.ready else "not ready"
            lines.append(
                f"  {icon} {entry.due_date}  {entry.assignment}  {title}  [{status_label}]"
            )
            if entry.ready:
                ready_assignments += 1
        lines.append("")

    lines.append(
        f"Summary: {ready_lectures}/{total_lectures} lectures ready, "
        f"{ready_assignments}/{total_assignments} assignments ready"
    )
    if next_unready:
        lines.append(f"Next unready: {next_unready}")

    return "\n".join(lines)


def delivery_status_json(
    manifest_id: str,
    *,
    root: Path = REPO_ROOT,
    index: RepositoryIndex | None = None,
) -> dict:
    delivery, index = _load_delivery(manifest_id, root=root, index=index)
    manifest = delivery.model
    return {
        "id": manifest.id,
        "course": manifest.course,
        "term": manifest.term,
        "language": manifest.language,
        "status": manifest.status,
        "lectures": [
            {
                "lecture": e.lecture,
                "date": e.date.isoformat(),
                "ready": e.ready,
            }
            for e in manifest.lectures
        ],
        "assignments": [
            {
                "assignment": e.assignment,
                "due_date": e.due_date.isoformat(),
                "ready": e.ready,
            }
            for e in manifest.assignments
        ],
        "summary": {
            "ready_lectures": sum(1 for e in manifest.lectures if e.ready),
            "total_lectures": len(manifest.lectures),
            "ready_assignments": sum(1 for e in manifest.assignments if e.ready),
            "total_assignments": len(manifest.assignments),
        },
    }


@dataclass(slots=True)
class DeliveryBuildResult:
    manifest_id: str
    built_lectures: list[str] = field(default_factory=list)
    built_assignments: list[str] = field(default_factory=list)
    skipped_lectures: list[str] = field(default_factory=list)
    skipped_assignments: list[str] = field(default_factory=list)
    artifacts: list = field(default_factory=list)
    delivery_report_path: Path | None = None


def build_delivery(
    manifest_id: str,
    *,
    root: Path = REPO_ROOT,
    ready_only: bool = False,
    lecture_filter: str | None = None,
    index: RepositoryIndex | None = None,
) -> DeliveryBuildResult:
    from app.assembly import DeliveryContext
    from app.build import BuildError, build_target

    delivery, index = _load_delivery(manifest_id, root=root, index=index)
    manifest = delivery.model
    delivery_output_root = deliveries_build_dir(root) / manifest.id

    result = DeliveryBuildResult(manifest_id=manifest.id)

    lectures = list(manifest.lectures)
    if lecture_filter:
        lectures = [e for e in lectures if e.lecture == lecture_filter]
        if not lectures:
            raise ValueError(f"lecture {lecture_filter} not found in delivery {manifest_id}")
    if ready_only:
        skipped = [e for e in lectures if not e.ready]
        result.skipped_lectures = [e.lecture for e in skipped]
        lectures = [e for e in lectures if e.ready]

    for entry in lectures:
        context = DeliveryContext(
            date=entry.date,
            term=manifest.term,
            manifest_id=manifest.id,
            title_override=entry.title_override,
            additions=list(entry.additions),
            removals=list(entry.removals),
        )
        built_any = False
        for audience in manifest.default_audiences:
            for fmt in manifest.default_formats:
                try:
                    artifact = build_target(
                        entry.lecture,
                        audience=audience,
                        language=manifest.language,
                        output_format=fmt,
                        root=root,
                        index=index,
                        delivery_context=context,
                        delivery_output_root=delivery_output_root,
                        sync_html_shell_assets=False,
                        sync_student_search_index=False,
                    )
                    result.artifacts.append(artifact)
                    built_any = True
                except (BuildError, Exception) as exc:
                    if "not support" in str(exc) or "unsupported" in str(exc).lower():
                        continue
                    raise
        if built_any:
            result.built_lectures.append(entry.lecture)

    assignments = list(manifest.assignments)
    if lecture_filter:
        assignments = []
    if ready_only:
        skipped_a = [e for e in assignments if not e.ready]
        result.skipped_assignments = [e.assignment for e in skipped_a]
        assignments = [e for e in assignments if e.ready]

    assignment_formats = [f for f in ("html", "exercise-sheet") if f in manifest.default_formats]
    for entry in assignments:
        built_any = False
        for audience in manifest.default_audiences:
            for fmt in assignment_formats:
                try:
                    artifact = build_target(
                        entry.assignment,
                        audience=audience,
                        language=manifest.language,
                        output_format=fmt,
                        root=root,
                        index=index,
                        delivery_output_root=delivery_output_root,
                        sync_html_shell_assets=False,
                        sync_student_search_index=False,
                    )
                    result.artifacts.append(artifact)
                    built_any = True
                except (BuildError, Exception) as exc:
                    if "not support" in str(exc) or "unsupported" in str(exc).lower():
                        continue
                    raise
        if built_any:
            result.built_assignments.append(entry.assignment)

    report_path = write_delivery_report(result, manifest, root)
    result.delivery_report_path = report_path
    return result


def write_delivery_report(
    result: DeliveryBuildResult,
    manifest: DeliveryManifest,
    root: Path,
) -> Path:
    report_dir = deliveries_build_dir(root) / manifest.id
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "delivery-report.json"
    payload = {
        "manifest_id": manifest.id,
        "course": manifest.course,
        "term": manifest.term,
        "language": manifest.language,
        "built_lectures": result.built_lectures,
        "built_assignments": result.built_assignments,
        "skipped_lectures": result.skipped_lectures,
        "skipped_assignments": result.skipped_assignments,
        "artifact_count": len(result.artifacts),
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path

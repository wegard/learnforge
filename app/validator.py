from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from app.config import REPO_ROOT, reports_dir
from app.indexer import LoadError, load_repository, write_search_index
from app.models import Collection, Concept, Exercise, Figure, Resource

TEACHER_BLOCK_RE = re.compile(r":::\s*\{\.teacher-only\}")


@dataclass(slots=True)
class ValidationIssue:
    code: str
    message: str
    path: str
    object_id: str | None = None
    severity: str = "error"


@dataclass(slots=True)
class ValidationReport:
    issue_count: int
    object_count: int
    course_count: int
    issues: list[ValidationIssue]
    search_index_path: str | None = None

    @property
    def ok(self) -> bool:
        return not self.issues


def _error_from_load_error(error: LoadError, root: Path) -> ValidationIssue:
    return ValidationIssue(
        code="load-error",
        message=error.message,
        path=str(error.path.relative_to(root)),
    )


def _add_issue(
    issues: list[ValidationIssue],
    *,
    code: str,
    message: str,
    path: Path,
    root: Path,
    object_id: str | None = None,
) -> None:
    issues.append(
        ValidationIssue(
            code=code,
            message=message,
            path=str(path.relative_to(root)),
            object_id=object_id,
        )
    )


def validate_repository(root: Path = REPO_ROOT) -> ValidationReport:
    index, load_errors = load_repository(root, collect_errors=True)
    issues = [_error_from_load_error(error, root) for error in load_errors]
    search_index_path: str | None = None

    object_ids = set(index.objects)
    course_ids = set(index.courses)

    for record in index.objects.values():
        model = record.model
        record_path = record.meta_path

        if not isinstance(model, Collection):
            for language in model.languages:
                note_path = record.note_path(language)
                if not note_path.exists():
                    _add_issue(
                        issues,
                        code="missing-note",
                        message=f"missing note for language {language}",
                        path=note_path,
                        root=root,
                        object_id=model.id,
                    )

        if model.visibility in {"student", "public"} and model.status in {"approved", "published"}:
            approved_languages = [
                language
                for language in model.languages
                if model.translation_status.get(language) == "approved"
            ]
            if not approved_languages:
                _add_issue(
                    issues,
                    code="missing-approved-language",
                    message="approved student-visible content needs at least one approved language",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                )

        for course_id in model.courses:
            if course_id not in course_ids:
                _add_issue(
                    issues,
                    code="missing-course",
                    message=f"references unknown course {course_id}",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                )

        if isinstance(model, Concept):
            for reference in [*model.prerequisites, *model.related]:
                if reference not in object_ids:
                    _add_issue(
                        issues,
                        code="missing-reference",
                        message=f"references unknown object {reference}",
                        path=record_path,
                        root=root,
                        object_id=model.id,
                    )

        if isinstance(model, Exercise):
            for reference in model.concepts:
                if reference not in object_ids:
                    _add_issue(
                        issues,
                        code="missing-concept",
                        message=f"references unknown concept {reference}",
                        path=record_path,
                        root=root,
                        object_id=model.id,
                    )
            for language in model.languages:
                note_path = record.note_path(language)
                if note_path.exists() and TEACHER_BLOCK_RE.search(
                    note_path.read_text(encoding="utf-8")
                ):
                    _add_issue(
                        issues,
                        code="exercise-note-contains-teacher-block",
                        message=(
                            "exercise notes must not contain teacher-only blocks; use "
                            f"solution.{language}.qmd instead"
                        ),
                        path=note_path,
                        root=root,
                        object_id=model.id,
                    )
                solution_path = record.solution_path(language)
                if model.solution_visibility == "teacher" and not solution_path.exists():
                    _add_issue(
                        issues,
                        code="missing-solution",
                        message=f"missing solution note for language {language}",
                        path=solution_path,
                        root=root,
                        object_id=model.id,
                    )

        if isinstance(model, Figure):
            svg_path = record.directory / model.svg_path
            if not svg_path.exists():
                _add_issue(
                    issues,
                    code="missing-figure-asset",
                    message=f"missing SVG asset {model.svg_path}",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                )
            if model.pdf_path and not (record.directory / model.pdf_path).exists():
                _add_issue(
                    issues,
                    code="missing-figure-pdf",
                    message=f"missing PDF asset {model.pdf_path}",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                )
            if model.interactive_path and not (record.directory / model.interactive_path).exists():
                _add_issue(
                    issues,
                    code="missing-figure-interactive",
                    message=f"missing interactive asset {model.interactive_path}",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                )

        if isinstance(model, Resource) and model.visibility in {"student", "public"}:
            if model.status in {"approved", "published"} and (
                not model.approved_by or not model.approved_on
            ):
                _add_issue(
                    issues,
                    code="missing-approval-metadata",
                    message="student-visible approved resources need approved_by and approved_on",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                )

        if isinstance(model, Collection):
            if model.collection_kind == "assignment" and "exercise-sheet" not in model.outputs:
                _add_issue(
                    issues,
                    code="assignment-missing-exercise-sheet-output",
                    message="assignment collections must declare exercise-sheet output",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                )
            for item_id in model.items:
                item_record = index.objects.get(item_id)
                if item_record is None:
                    _add_issue(
                        issues,
                        code="missing-collection-item",
                        message=f"collection references unknown object {item_id}",
                        path=record_path,
                        root=root,
                        object_id=model.id,
                    )
                    continue
                if model.collection_kind == "assignment":
                    if not isinstance(item_record.model, Exercise):
                        _add_issue(
                            issues,
                            code="assignment-item-not-exercise",
                            message=f"assignment collections may only include exercises: {item_id}",
                            path=record_path,
                            root=root,
                            object_id=model.id,
                        )
                    elif "exercise-sheet" not in item_record.model.outputs:
                        _add_issue(
                            issues,
                            code="exercise-not-sheet-eligible",
                            message=(
                                f"exercise {item_id} is missing exercise-sheet output eligibility"
                            ),
                            path=item_record.meta_path,
                            root=root,
                            object_id=item_id,
                        )

    for record in index.courses.values():
        model = record.model
        for language in model.languages:
            syllabus_path = record.syllabus_path(language)
            if not syllabus_path.exists():
                _add_issue(
                    issues,
                    code="missing-syllabus",
                    message=f"missing syllabus for language {language}",
                    path=syllabus_path,
                    root=root,
                    object_id=model.id,
                )
        for lecture_id in record.plan.lectures:
            collection_record = index.objects.get(lecture_id)
            if collection_record is None or not isinstance(collection_record.model, Collection):
                _add_issue(
                    issues,
                    code="missing-lecture",
                    message=f"course plan references unknown lecture collection {lecture_id}",
                    path=record.plan_path,
                    root=root,
                    object_id=model.id,
                )
            elif collection_record.model.collection_kind != "lecture":
                _add_issue(
                    issues,
                    code="invalid-lecture-kind",
                    message=f"course plan lecture entry must be a lecture collection: {lecture_id}",
                    path=record.plan_path,
                    root=root,
                    object_id=model.id,
                )
        for assignment_id in record.plan.assignments:
            assignment_record = index.objects.get(assignment_id)
            if assignment_record is None or not isinstance(assignment_record.model, Collection):
                _add_issue(
                    issues,
                    code="missing-assignment",
                    message=(
                        "course plan references unknown assignment collection "
                        f"{assignment_id}"
                    ),
                    path=record.plan_path,
                    root=root,
                    object_id=model.id,
                )
                continue
            if assignment_record.model.collection_kind != "assignment":
                _add_issue(
                    issues,
                    code="invalid-assignment-kind",
                    message=(
                        "course plan assignment entry must be an assignment collection: "
                        f"{assignment_id}"
                    ),
                    path=record.plan_path,
                    root=root,
                    object_id=model.id,
                )
            if "html" not in assignment_record.model.outputs:
                _add_issue(
                    issues,
                    code="assignment-missing-html-output",
                    message=(
                        "course-planned assignments must declare html output for "
                        f"stable student navigation: {assignment_id}"
                    ),
                    path=assignment_record.meta_path,
                    root=root,
                    object_id=assignment_id,
                )
            if model.id not in assignment_record.model.courses:
                _add_issue(
                    issues,
                    code="assignment-course-mismatch",
                    message=(
                        f"assignment {assignment_id} is listed in course {model.id} plan but "
                        "does not declare that course in its metadata"
                    ),
                    path=assignment_record.meta_path,
                    root=root,
                    object_id=assignment_id,
                )

    if not issues:
        search_index_path = str(write_search_index(index, root).relative_to(root))

    return ValidationReport(
        issue_count=len(issues),
        object_count=len(index.objects),
        course_count=len(index.courses),
        issues=issues,
        search_index_path=search_index_path,
    )


def write_validation_report(report: ValidationReport, root: Path = REPO_ROOT) -> Path:
    reports_dir(root).mkdir(parents=True, exist_ok=True)
    output_path = root / "build" / "reports" / "validation-report.json"
    payload = {
        "issue_count": report.issue_count,
        "object_count": report.object_count,
        "course_count": report.course_count,
        "issues": [asdict(issue) for issue in report.issues],
        "search_index_path": report.search_index_path,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path

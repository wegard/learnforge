from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import ValidationError

from app.assembly import collect_topics, planned_target_output_path
from app.build import BuildError, build_target, is_student_visible_in_language
from app.config import LANGUAGES, REPO_ROOT, reports_dir
from app.indexer import IndexedObject, LoadError, load_repository, load_yaml, write_search_index
from app.models import (
    Collection,
    Concept,
    Exercise,
    Figure,
    RepresentativeTarget,
    RepresentativeTargetRegistry,
    Resource,
)

TEACHER_BLOCK_RE = re.compile(r":::\s*\{\.teacher-only\}")
MARKDOWN_LINK_RE = re.compile(r"!\[[^\]]*]\(([^)]+)\)|\[[^\]]*]\(([^)]+)\)")
UNRESOLVED_SHORTCODE_RE = re.compile(r"{{[%<]")
REPRESENTATIVE_TARGETS_PATH = Path("representative-targets.yml")
VALIDATION_REPORT_PATH = Path("build/reports/validation-report.json")
BUILD_SUMMARY_PATH = Path("build/reports/build-summary.json")


class InternalLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[dict[str, str]] = []
        self._ignore_depth = 0
        self._ignore_stack: list[bool] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value for key, value in attrs if value is not None}
        ignore_here = "quarto-alternate-formats" in attributes.get("class", "").split()
        self._ignore_stack.append(ignore_here)
        if ignore_here:
            self._ignore_depth += 1
        if self._ignore_depth > 0:
            return
        self._collect(tag, attributes)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value for key, value in attrs if value is not None}
        if "quarto-alternate-formats" in attributes.get("class", "").split():
            return
        self._collect(tag, attributes)

    def handle_endtag(self, _tag: str) -> None:
        if not self._ignore_stack:
            return
        if self._ignore_stack.pop():
            self._ignore_depth = max(0, self._ignore_depth - 1)

    def _collect(self, tag: str, attributes: dict[str, str]) -> None:
        for attribute in ("href", "src", "data-background-image"):
            value = attributes.get(attribute)
            if value:
                self.references.append({"tag": tag, "attribute": attribute, "value": value})


@dataclass(slots=True)
class ValidationIssue:
    code: str
    message: str
    path: str
    object_id: str | None = None
    severity: str = "error"
    category: str = "general"


@dataclass(slots=True)
class ValidationReport:
    issue_count: int
    error_count: int
    warning_count: int
    object_count: int
    course_count: int
    issues: list[ValidationIssue]
    search_index_path: str | None = None
    build_summary: dict[str, object] = field(default_factory=dict)
    translation_coverage: dict[str, object] = field(default_factory=dict)
    category_counts: dict[str, int] = field(default_factory=dict)
    representative_target_count: int = 0
    representative_target_failure_count: int = 0

    @property
    def ok(self) -> bool:
        return self.error_count == 0

    @property
    def status(self) -> str:
        if self.error_count:
            return "failed"
        if self.warning_count:
            return "passed_with_warnings"
        return "passed"


def _error_from_load_error(error: LoadError, root: Path) -> ValidationIssue:
    return ValidationIssue(
        code="load-error",
        message=error.message,
        path=str(error.path.relative_to(root)),
        category="schema",
    )


def _add_issue(
    issues: list[ValidationIssue],
    *,
    code: str,
    message: str,
    path: Path,
    root: Path,
    object_id: str | None = None,
    severity: str = "error",
    category: str = "general",
) -> None:
    issues.append(
        ValidationIssue(
            code=code,
            message=message,
            path=str(path.relative_to(root)),
            object_id=object_id,
            severity=severity,
            category=category,
        )
    )


def validate_repository(
    root: Path = REPO_ROOT,
    *,
    run_build_checks: bool = True,
) -> ValidationReport:
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
                        category="assets",
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
                    category="editorial",
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
                    category="cross-reference",
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
                        category="cross-reference",
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
                        category="cross-reference",
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
                        category="editorial",
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
                        category="assets",
                    )

        if isinstance(model, Figure):
            for reference in model.concepts:
                if reference not in object_ids:
                    _add_issue(
                        issues,
                        code="missing-figure-concept",
                        message=f"references unknown concept {reference}",
                        path=record_path,
                        root=root,
                        object_id=model.id,
                        category="cross-reference",
                    )
            svg_path = record.directory / model.svg_path
            svg_exists = svg_path.exists()
            pdf_path = record.directory / model.pdf_path
            pdf_exists = pdf_path.exists()
            interactive_exists = True
            if not svg_exists:
                _add_issue(
                    issues,
                    code="missing-figure-asset",
                    message=f"missing SVG asset {model.svg_path}",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                    category="assets",
                )
            if not pdf_exists:
                _add_issue(
                    issues,
                    code="missing-figure-pdf",
                    message=f"missing PDF asset {model.pdf_path}",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                    category="assets",
                )
            if model.interactive_path and not (record.directory / model.interactive_path).exists():
                interactive_exists = False
                _add_issue(
                    issues,
                    code="missing-figure-interactive",
                    message=f"missing interactive asset {model.interactive_path}",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                    category="assets",
                )
            for asset in model.asset_inventory:
                if not (record.directory / asset).exists():
                    _add_issue(
                        issues,
                        code="missing-figure-inventory-asset",
                        message=f"missing figure inventory asset {asset}",
                        path=record_path,
                        root=root,
                        object_id=model.id,
                        category="assets",
                    )
            if model.interactive_path and (not svg_exists or not pdf_exists):
                _add_issue(
                    issues,
                    code="interactive-figure-missing-static-fallback",
                    message="interactive figures must keep both SVG and PDF fallbacks buildable",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                    category="build",
                )
            if any(output in {"html", "revealjs"} for output in model.outputs) and not svg_exists:
                _add_issue(
                    issues,
                    code="figure-output-not-buildable",
                    message="figure declares html/revealjs outputs without a buildable SVG asset",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                    category="build",
                )
            if any(output in {"pdf", "handout"} for output in model.outputs) and not pdf_exists:
                _add_issue(
                    issues,
                    code="figure-output-not-buildable",
                    message="figure declares print outputs without a buildable PDF fallback",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                    category="build",
                )
            if model.interactive_path and not interactive_exists:
                _add_issue(
                    issues,
                    code="figure-output-not-buildable",
                    message="figure declares an interactive path that cannot be loaded",
                    path=record_path,
                    root=root,
                    object_id=model.id,
                    category="build",
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
                    category="editorial",
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
                    category="build",
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
                        category="cross-reference",
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
                            category="cross-reference",
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
                            category="build",
                        )

        _validate_markdown_file_links(record, issues, root)

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
                    category="assets",
                )
            else:
                broken_references = _validate_local_file_references(
                    syllabus_path.read_text(encoding="utf-8"),
                    source_path=syllabus_path,
                    root=root,
                )
                for broken_reference in broken_references:
                    _add_issue(
                        issues,
                        code="missing-local-asset",
                        message=f"references missing local file {broken_reference}",
                        path=syllabus_path,
                        root=root,
                        object_id=model.id,
                        category="assets",
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
                    category="cross-reference",
                )
            elif collection_record.model.collection_kind != "lecture":
                _add_issue(
                    issues,
                    code="invalid-lecture-kind",
                    message=f"course plan lecture entry must be a lecture collection: {lecture_id}",
                    path=record.plan_path,
                    root=root,
                    object_id=model.id,
                    category="cross-reference",
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
                    category="cross-reference",
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
                    category="cross-reference",
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
                    category="build",
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
                    category="cross-reference",
                )

    translation_coverage = _collect_translation_coverage(index=index, root=root, issues=issues)
    representative_targets, representative_target_issues = _load_representative_targets(root)
    issues.extend(representative_target_issues)

    prebuild_error_count = _count_issues(issues, severity="error")
    if prebuild_error_count == 0:
        search_index_path = str(write_search_index(index, root).relative_to(root))

    build_summary = _build_summary_skeleton(root, representative_targets, index=index)
    if run_build_checks and prebuild_error_count == 0 and not representative_target_issues:
        build_summary, build_issues = _run_representative_build_checks(
            root=root,
            index=index,
            targets=representative_targets,
        )
        issues.extend(build_issues)
    elif run_build_checks and prebuild_error_count > 0:
        build_summary = _mark_build_summary_skipped(
            build_summary,
            reason="source-validation-errors",
        )
    elif run_build_checks and representative_target_issues:
        build_summary = _mark_build_summary_skipped(
            build_summary,
            reason="representative-target-registry-invalid",
        )
    else:
        build_summary = _mark_build_summary_skipped(build_summary, reason="build-checks-disabled")

    error_count = _count_issues(issues, severity="error")
    warning_count = _count_issues(issues, severity="warning")
    category_counts = dict(Counter(issue.category for issue in issues))

    return ValidationReport(
        issue_count=len(issues),
        error_count=error_count,
        warning_count=warning_count,
        object_count=len(index.objects),
        course_count=len(index.courses),
        issues=issues,
        search_index_path=search_index_path,
        build_summary=build_summary,
        translation_coverage=translation_coverage,
        category_counts=category_counts,
        representative_target_count=len(representative_targets),
        representative_target_failure_count=int(build_summary.get("failure_count", 0)),
    )


def load_representative_targets(root: Path = REPO_ROOT) -> list[RepresentativeTarget]:
    targets, issues = _load_representative_targets(root)
    if issues:
        messages = "; ".join(issue.message for issue in issues)
        raise ValueError(messages)
    return targets


def _validate_markdown_file_links(
    record: IndexedObject,
    issues: list[ValidationIssue],
    root: Path,
) -> None:
    if isinstance(record.model, Collection):
        return
    for language in record.model.languages:
        note_path = record.note_path(language)
        if note_path.exists():
            for broken_reference in _validate_local_file_references(
                note_path.read_text(encoding="utf-8"),
                source_path=note_path,
                root=root,
            ):
                _add_issue(
                    issues,
                    code="missing-local-asset",
                    message=f"references missing local file {broken_reference}",
                    path=note_path,
                    root=root,
                    object_id=record.model.id,
                    category="assets",
                )
        if isinstance(record.model, Exercise):
            solution_path = record.solution_path(language)
            if solution_path.exists():
                for broken_reference in _validate_local_file_references(
                    solution_path.read_text(encoding="utf-8"),
                    source_path=solution_path,
                    root=root,
                ):
                    _add_issue(
                        issues,
                        code="missing-local-asset",
                        message=f"references missing local file {broken_reference}",
                        path=solution_path,
                        root=root,
                        object_id=record.model.id,
                        category="assets",
                    )


def _validate_local_file_references(
    content: str,
    *,
    source_path: Path,
    root: Path,
) -> list[str]:
    broken: list[str] = []
    for reference in _extract_markdown_references(content):
        if reference.startswith("/"):
            target_path = (root / reference.lstrip("/")).resolve()
        else:
            target_path = (source_path.parent / reference).resolve()
        if target_path.exists():
            continue
        broken.append(reference)
    return broken


def _extract_markdown_references(content: str) -> list[str]:
    references: list[str] = []
    for match in MARKDOWN_LINK_RE.finditer(content):
        candidate = (match.group(1) or match.group(2) or "").strip()
        if not candidate:
            continue
        candidate = candidate.strip("<>")
        candidate = candidate.split(" ", 1)[0]
        parts = urlsplit(candidate)
        if parts.scheme or parts.netloc:
            continue
        candidate = parts.path
        if not candidate or candidate.startswith("#"):
            continue
        references.append(candidate)
    return references


def _collect_translation_coverage(
    *,
    index,
    root: Path,
    issues: list[ValidationIssue],
) -> dict[str, object]:
    missing_variants: list[dict[str, object]] = []
    student_visible_target_count = 0
    fully_approved_target_count = 0

    for record in index.objects.values():
        model = record.model
        if model.visibility not in {"student", "public"}:
            continue
        if model.status not in {"approved", "published"}:
            continue
        student_visible_target_count += 1
        missing_languages = _missing_languages_for_object(record)
        if not missing_languages:
            fully_approved_target_count += 1
            continue
        missing_variants.append(
            {
                "id": model.id,
                "kind": model.kind,
                "path": str(record.meta_path.relative_to(root)),
                "missing_languages": missing_languages,
            }
        )
        approved_languages = [
            language
            for language in LANGUAGES
            if language in model.languages
            and model.translation_status.get(language) == "approved"
            and record.note_path(language).exists()
        ]
        if approved_languages:
            _add_issue(
                issues,
                code="missing-approved-translation",
                message=(
                    "student-visible content is missing approved language variants: "
                    + ", ".join(missing_languages)
                ),
                path=record.meta_path,
                root=root,
                object_id=model.id,
                severity="warning",
                category="editorial",
            )

    for record in index.courses.values():
        model = record.model
        if model.visibility not in {"student", "public"}:
            continue
        if model.status not in {"approved", "published"}:
            continue
        student_visible_target_count += 1
        missing_languages = _missing_languages_for_course(record)
        if not missing_languages:
            fully_approved_target_count += 1
            continue
        missing_variants.append(
            {
                "id": model.id,
                "kind": "course",
                "path": str(record.course_path.relative_to(root)),
                "missing_languages": missing_languages,
            }
        )
        if len(missing_languages) < len(LANGUAGES):
            _add_issue(
                issues,
                code="missing-approved-translation",
                message=(
                    "student-visible content is missing approved language variants: "
                    + ", ".join(missing_languages)
                ),
                path=record.course_path,
                root=root,
                object_id=model.id,
                severity="warning",
                category="editorial",
            )

    return {
        "expected_languages": list(LANGUAGES),
        "student_visible_target_count": student_visible_target_count,
        "fully_approved_target_count": fully_approved_target_count,
        "missing_variant_count": len(missing_variants),
        "missing_variants": missing_variants,
    }


def _missing_languages_for_object(record: IndexedObject) -> list[str]:
    missing: list[str] = []
    for language in LANGUAGES:
        if language not in record.model.languages:
            missing.append(language)
            continue
        if record.model.translation_status.get(language) != "approved":
            missing.append(language)
            continue
        if not isinstance(record.model, Collection) and not record.note_path(language).exists():
            missing.append(language)
    return missing


def _missing_languages_for_course(record) -> list[str]:
    missing: list[str] = []
    for language in LANGUAGES:
        if language not in record.model.languages:
            missing.append(language)
            continue
        if not record.syllabus_path(language).exists():
            missing.append(language)
    return missing


def _load_representative_targets(
    root: Path,
) -> tuple[list[RepresentativeTarget], list[ValidationIssue]]:
    registry_path = root / REPRESENTATIVE_TARGETS_PATH
    issues: list[ValidationIssue] = []
    if not registry_path.exists():
        _add_issue(
            issues,
            code="missing-representative-target-registry",
            message="missing representative target registry",
            path=registry_path,
            root=root,
            category="build",
        )
        return [], issues

    try:
        payload = load_yaml(registry_path)
        registry = RepresentativeTargetRegistry.model_validate(payload)
    except (OSError, ValidationError, ValueError) as exc:
        _add_issue(
            issues,
            code="invalid-representative-target-registry",
            message=str(exc),
            path=registry_path,
            root=root,
            category="build",
        )
        return [], issues

    return registry.targets, issues


def _build_summary_skeleton(
    root: Path,
    targets: list[RepresentativeTarget],
    *,
    index,
) -> dict[str, object]:
    return {
        "status": "pending",
        "registry_path": str(REPRESENTATIVE_TARGETS_PATH),
        "build_summary_path": str(BUILD_SUMMARY_PATH),
        "target_count": len(targets),
        "success_count": 0,
        "failure_count": 0,
        "skipped_count": 0,
        "targets": [
            {
                "label": target.label,
                "target_id": target.id,
                "audience": target.audience,
                "language": target.language,
                "format": target.format,
                "expected_output_path": _representative_expected_output_path(
                    target=target,
                    index=index,
                    root=root,
                ),
                "status": "pending",
            }
            for target in targets
        ],
    }


def _mark_build_summary_skipped(summary: dict[str, object], *, reason: str) -> dict[str, object]:
    summary["status"] = "skipped"
    summary["skipped_count"] = summary["target_count"]
    summary["targets"] = [
        {**target, "status": "skipped", "reason": reason}
        for target in summary.get("targets", [])
    ]
    return summary


def _run_representative_build_checks(
    *,
    root: Path,
    index,
    targets: list[RepresentativeTarget],
) -> tuple[dict[str, object], list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    expected_html_outputs = _expected_html_output_paths(index=index, root=root)
    target_results: list[dict[str, object]] = []
    success_count = 0
    failure_count = 0

    for target in targets:
        target_path = root / REPRESENTATIVE_TARGETS_PATH
        try:
            artifact = build_target(
                target.id,
                audience=target.audience,
                language=target.language,
                output_format=target.format,
                root=root,
            )
        except BuildError as exc:
            _add_issue(
                issues,
                code="representative-build-failed",
                message=f"{target.label}: {exc}",
                path=target_path,
                root=root,
                object_id=target.id,
                category="build",
            )
            target_results.append(
                {
                    "label": target.label,
                    "target_id": target.id,
                    "audience": target.audience,
                    "language": target.language,
                    "format": target.format,
                    "expected_output_path": _representative_expected_output_path(
                        target=target,
                        index=index,
                        root=root,
                    ),
                    "status": "failed",
                    "error": str(exc),
                }
            )
            failure_count += 1
            continue

        integrity_summary, integrity_issues = _check_build_artifact_integrity(
            artifact=artifact,
            expected_html_outputs=expected_html_outputs,
            root=root,
        )
        issues.extend(integrity_issues)

        leakage_payload = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))
        if target.audience == "student" and leakage_payload.get("status") != "clean":
            _add_issue(
                issues,
                code="student-leakage-detected",
                message=f"{target.label}: leakage report status is {leakage_payload['status']}",
                path=artifact.leakage_report_path,
                root=root,
                object_id=target.id,
                category="build",
            )
            integrity_summary["status"] = "failed"

        target_status = "passed" if integrity_summary["status"] == "passed" else "failed"
        if target_status == "passed":
            success_count += 1
        else:
            failure_count += 1

        target_results.append(
            {
                "label": target.label,
                "target_id": target.id,
                "target_kind": artifact.target_kind,
                "audience": target.audience,
                "language": target.language,
                "format": target.format,
                "status": target_status,
                "output_path": str(artifact.output_path.relative_to(root)),
                "build_manifest_path": str(artifact.build_manifest_path.relative_to(root)),
                "dependency_manifest_path": str(
                    artifact.dependency_manifest_path.relative_to(root)
                ),
                "leakage_report_path": str(artifact.leakage_report_path.relative_to(root)),
                "search_index_path": (
                    str(artifact.search_index_path.relative_to(root))
                    if artifact.search_index_path is not None
                    else None
                ),
                "leakage_status": leakage_payload["status"],
                "integrity": integrity_summary,
            }
        )

    return (
        {
            "status": "passed" if failure_count == 0 else "failed",
            "registry_path": str(REPRESENTATIVE_TARGETS_PATH),
            "build_summary_path": str(BUILD_SUMMARY_PATH),
            "target_count": len(targets),
            "success_count": success_count,
            "failure_count": failure_count,
            "skipped_count": 0,
            "targets": target_results,
        },
        issues,
    )


def _check_build_artifact_integrity(
    *,
    artifact,
    expected_html_outputs: set[Path],
    root: Path,
) -> tuple[dict[str, object], list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    manifest_issues: list[str] = []
    broken_links: list[dict[str, str]] = []
    unresolved_markers: list[dict[str, str]] = []

    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    expected_output_path = str(artifact.output_path.relative_to(root))
    if build_manifest.get("output_path") != expected_output_path:
        manifest_issues.append(
            "build manifest output_path does not match rendered artifact path"
        )
    if not artifact.output_path.exists():
        manifest_issues.append("rendered output file is missing")
    if not artifact.build_manifest_path.exists():
        manifest_issues.append("build manifest file is missing")
    if not artifact.dependency_manifest_path.exists():
        manifest_issues.append("dependency manifest file is missing")
    if not artifact.leakage_report_path.exists():
        manifest_issues.append("teacher leakage report file is missing")
    if artifact.search_index_path is not None and not artifact.search_index_path.exists():
        manifest_issues.append("student search index is missing")

    for generated_artifact in build_manifest.get("generated_artifacts", []):
        generated_path = root / generated_artifact["path"]
        if not generated_path.exists():
            manifest_issues.append(
                f"generated artifact listed in manifest is missing: {generated_artifact['path']}"
            )

    generated_source_text = artifact.source_path.read_text(encoding="utf-8")
    if UNRESOLVED_SHORTCODE_RE.search(generated_source_text):
        unresolved_markers.append(
            {
                "where": "generated-source",
                "path": str(artifact.source_path.relative_to(root)),
                "pattern": "{{< or {{%",
            }
        )

    if artifact.output_format in {"html", "revealjs"}:
        output_text = artifact.output_path.read_text(encoding="utf-8", errors="ignore")
        if UNRESOLVED_SHORTCODE_RE.search(output_text):
            unresolved_markers.append(
                {
                    "where": "rendered-output",
                    "path": str(artifact.output_path.relative_to(root)),
                    "pattern": "{{< or {{%",
                }
            )
        broken_links = _find_broken_internal_links(
            html_text=output_text,
            output_path=artifact.output_path,
            expected_html_outputs=expected_html_outputs,
            root=root,
        )

    for message in manifest_issues:
        _add_issue(
            issues,
            code="manifest-integrity-failed",
            message=message,
            path=artifact.build_manifest_path,
            root=root,
            object_id=artifact.target_id,
            category="build",
        )
    for marker in unresolved_markers:
        _add_issue(
            issues,
            code="unresolved-shortcode",
            message=f"{marker['where']} still contains unresolved shortcode markers",
            path=root / marker["path"],
            root=root,
            object_id=artifact.target_id,
            category="build",
        )
    for broken_link in broken_links:
        _add_issue(
            issues,
            code="broken-internal-link",
            message=(
                f"{broken_link['attribute']}={broken_link['value']} does not resolve to a built "
                "artifact, expected HTML target, or local asset"
            ),
            path=artifact.output_path,
            root=root,
            object_id=artifact.target_id,
            category="build",
        )

    status = "passed"
    if manifest_issues or unresolved_markers or broken_links:
        status = "failed"

    return (
        {
            "status": status,
            "manifest_issue_count": len(manifest_issues),
            "manifest_issues": manifest_issues,
            "unresolved_marker_count": len(unresolved_markers),
            "unresolved_markers": unresolved_markers,
            "broken_link_count": len(broken_links),
            "broken_links": broken_links,
        },
        issues,
    )


def _find_broken_internal_links(
    *,
    html_text: str,
    output_path: Path,
    expected_html_outputs: set[Path],
    root: Path,
) -> list[dict[str, str]]:
    parser = InternalLinkParser()
    parser.feed(html_text)
    broken: list[dict[str, str]] = []

    for reference in parser.references:
        parts = urlsplit(reference["value"])
        if parts.scheme or parts.netloc:
            continue
        if not parts.path:
            continue
        resolved_path = _resolve_internal_reference(
            parts.path,
            output_path=output_path,
            root=root,
        )
        if resolved_path is None:
            broken.append(
                {
                    **reference,
                    "resolved_path": parts.path,
                    "reason": "reference escapes repository root",
                }
            )
            continue
        if resolved_path.exists():
            continue
        if _is_expected_html_output(resolved_path, expected_html_outputs):
            continue
        broken.append(
            {
                **reference,
                "resolved_path": str(resolved_path.relative_to(root)),
                "reason": "missing-target",
            }
        )

    return broken


def _resolve_internal_reference(
    value: str,
    *,
    output_path: Path,
    root: Path,
) -> Path | None:
    if value.startswith("/"):
        candidate = (root / value.lstrip("/")).resolve()
    else:
        candidate = (output_path.parent / value).resolve()
    if not candidate.is_relative_to(root.resolve()):
        return None
    return candidate


def _is_expected_html_output(path: Path, expected_html_outputs: set[Path]) -> bool:
    if not path.name.endswith(".html"):
        return False
    if "html" not in path.parts:
        return False
    return path in expected_html_outputs


def _expected_html_output_paths(*, index, root: Path) -> set[Path]:
    expected: set[Path] = set()

    for language in LANGUAGES:
        expected.add(
            planned_target_output_path(
                root,
                audience="student",
                language=language,
                output_format="html",
                target_kind="home",
                target_id="home",
            ).resolve()
        )

    for course_record in index.courses.values():
        for language in LANGUAGES:
            if course_record.model.visibility in {"private", "teacher"}:
                continue
            if course_record.model.status not in {"approved", "published"}:
                continue
            if language not in course_record.model.languages:
                continue
            expected.add(
                planned_target_output_path(
                    root,
                    audience="student",
                    language=language,
                    output_format="html",
                    target_kind="course",
                    target_id=course_record.model.id,
                ).resolve()
            )
            expected.add(
                planned_target_output_path(
                    root,
                    audience="teacher",
                    language=language,
                    output_format="html",
                    target_kind="course",
                    target_id=course_record.model.id,
                ).resolve()
            )

    for record in index.objects.values():
        if "html" not in record.model.outputs:
            continue
        target_kind = "collection" if record.model.kind == "collection" else record.model.kind
        for language in LANGUAGES:
            if is_student_visible_in_language(record, language):
                expected.add(
                    planned_target_output_path(
                        root,
                        audience="student",
                        language=language,
                        output_format="html",
                        target_kind=target_kind,
                        target_id=record.model.id,
                    ).resolve()
                )
            if language in record.model.languages and record.model.visibility != "private":
                expected.add(
                    planned_target_output_path(
                        root,
                        audience="teacher",
                        language=language,
                        output_format="html",
                        target_kind=target_kind,
                        target_id=record.model.id,
                    ).resolve()
                )

    for language in LANGUAGES:
        visible_objects = [
            record
            for record in index.objects.values()
            if is_student_visible_in_language(record, language)
        ]
        for topic in collect_topics(visible_objects):
            expected.add(
                planned_target_output_path(
                    root,
                    audience="student",
                    language=language,
                    output_format="html",
                    target_kind="topic-listing",
                    target_id=f"topic-{topic}",
                ).resolve()
            )

        for course_record in index.courses.values():
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
            expected.add(
                planned_target_output_path(
                    root,
                    audience="student",
                    language=language,
                    output_format="html",
                    target_kind="resource-listing",
                    target_id=f"resources-{course_record.model.id}",
                ).resolve()
            )

    return expected


def _representative_expected_output_path(
    *,
    target: RepresentativeTarget,
    index,
    root: Path,
) -> str | None:
    target_kind = _representative_target_kind(target.id, index=index)
    if target_kind is None:
        return None
    return str(
        planned_target_output_path(
            root,
            audience=target.audience,
            language=target.language,
            output_format=target.format,
            target_kind=target_kind,
            target_id=target.id,
        ).relative_to(root)
    )


def _representative_target_kind(target_id: str, *, index) -> str | None:
    if target_id == "home":
        return "home"
    if target_id in index.courses:
        return "course"
    if target_id in index.objects:
        record = index.objects[target_id]
        return "collection" if record.model.kind == "collection" else record.model.kind
    if target_id.startswith("topic-"):
        return "topic-listing"
    if target_id.startswith("resources-"):
        return "resource-listing"
    return None


def _count_issues(issues: list[ValidationIssue], *, severity: str) -> int:
    return sum(1 for issue in issues if issue.severity == severity)


def write_validation_report(
    report: ValidationReport,
    root: Path = REPO_ROOT,
) -> tuple[Path, Path]:
    reports_dir(root).mkdir(parents=True, exist_ok=True)
    validation_report_path = root / VALIDATION_REPORT_PATH
    build_summary_path = root / BUILD_SUMMARY_PATH

    build_summary_path.write_text(
        json.dumps(report.build_summary, indent=2),
        encoding="utf-8",
    )

    payload = {
        "status": report.status,
        "issue_count": report.issue_count,
        "error_count": report.error_count,
        "warning_count": report.warning_count,
        "object_count": report.object_count,
        "course_count": report.course_count,
        "category_counts": report.category_counts,
        "issues": [asdict(issue) for issue in report.issues],
        "search_index_path": report.search_index_path,
        "build_summary_path": str(build_summary_path.relative_to(root)),
        "translation_coverage": report.translation_coverage,
        "representative_target_count": report.representative_target_count,
        "representative_target_failure_count": report.representative_target_failure_count,
    }
    validation_report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return validation_report_path, build_summary_path

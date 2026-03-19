from __future__ import annotations

import shutil
from datetime import date

import pytest
from pydantic import ValidationError

from app.config import REPO_ROOT
from app.models import Concept, Exercise, Figure, Resource
from app.validator import validate_repository


def test_sample_repository_validates_cleanly() -> None:
    report = validate_repository(REPO_ROOT, run_build_checks=False)
    assert report.ok
    assert report.warning_count >= 14
    assert report.object_count >= 38
    assert report.course_count >= 2
    assert report.search_index_path == "build/index/content-index.json"


def test_concept_schema_rejects_missing_title_language() -> None:
    payload = {
        "id": "demo-concept",
        "kind": "concept",
        "status": "approved",
        "visibility": "student",
        "languages": ["en", "nb"],
        "title": {"en": "Demo concept"},
        "courses": [],
        "topics": [],
        "tags": [],
        "outputs": ["html"],
        "owners": ["vegard"],
        "updated": date(2026, 3, 18),
        "translation_status": {"en": "approved", "nb": "approved"},
        "ai": {"generated_fields": []},
        "level": "intermediate",
        "prerequisites": [],
        "related": [],
    }

    with pytest.raises(ValidationError):
        Concept.model_validate(payload)


def test_exercise_schema_rejects_unknown_solution_storage() -> None:
    payload = {
        "id": "demo-exercise",
        "kind": "exercise",
        "status": "approved",
        "visibility": "student",
        "languages": ["en", "nb"],
        "title": {"en": "Demo exercise", "nb": "Demooppgave"},
        "courses": ["ec202"],
        "topics": ["iv"],
        "tags": ["exercise"],
        "outputs": ["html", "exercise-sheet"],
        "owners": ["vegard"],
        "updated": date(2026, 3, 18),
        "translation_status": {"en": "approved", "nb": "approved"},
        "ai": {"generated_fields": []},
        "exercise_type": "conceptual",
        "difficulty": "easy",
        "estimated_time_minutes": 5,
        "concepts": ["iv-intuition"],
        "solution_storage": "inline",
        "solution_visibility": "teacher",
    }

    with pytest.raises(ValidationError):
        Exercise.model_validate(payload)


def test_figure_schema_rejects_interactive_without_html_output() -> None:
    payload = {
        "id": "demo-figure",
        "kind": "figure",
        "status": "approved",
        "visibility": "student",
        "languages": ["en", "nb"],
        "title": {"en": "Demo figure", "nb": "Demofigur"},
        "courses": ["ec202"],
        "topics": ["iv"],
        "tags": ["figure"],
        "outputs": ["pdf"],
        "owners": ["vegard"],
        "updated": date(2026, 3, 18),
        "translation_status": {"en": "approved", "nb": "approved"},
        "ai": {"generated_fields": []},
        "concepts": ["iv-intuition"],
        "caption": {"en": "Demo caption", "nb": "Demo bildetekst"},
        "alt_text": {"en": "Demo alt text", "nb": "Demo alternativ tekst"},
        "svg_path": "figure.svg",
        "pdf_path": "figure.pdf",
        "interactive_path": "figure.js",
    }

    with pytest.raises(ValidationError):
        Figure.model_validate(payload)


def test_resource_schema_requires_review_after_for_time_sensitive_state() -> None:
    payload = {
        "id": "demo-resource",
        "kind": "resource",
        "status": "approved",
        "visibility": "student",
        "languages": ["en", "nb"],
        "title": {"en": "Demo resource", "nb": "Demoressurs"},
        "courses": ["ec202"],
        "topics": ["iv"],
        "tags": ["resource"],
        "outputs": ["html"],
        "owners": ["vegard"],
        "updated": date(2026, 3, 18),
        "translation_status": {"en": "approved", "nb": "approved"},
        "ai": {"generated_fields": []},
        "resource_kind": "article",
        "authors": ["vegard"],
        "published_on": date(2026, 3, 1),
        "url": "https://example.org/demo-resource",
        "difficulty": "introductory",
        "estimated_time_minutes": 10,
        "summary": {"en": "Demo summary", "nb": "Demosammendrag"},
        "why_selected": {"en": "Why it matters", "nb": "Hvorfor det betyr noe"},
        "instructor_note": {"en": "Teacher note", "nb": "Laerernotat"},
        "freshness": "time-sensitive",
        "approved_by": "vegard",
        "approved_on": date(2026, 3, 18),
        "approval_history": [{"action": "approved", "by": "vegard", "acted_on": "2026-03-18"}],
        "stale_flag": False,
    }

    with pytest.raises(ValidationError):
        Resource.model_validate(payload)


def test_resource_schema_rejects_candidate_with_approval_metadata() -> None:
    payload = {
        "id": "demo-candidate-resource",
        "kind": "resource",
        "status": "candidate",
        "visibility": "student",
        "languages": ["en"],
        "title": {"en": "Demo candidate"},
        "courses": ["ec202"],
        "topics": [],
        "tags": ["resource"],
        "outputs": ["html"],
        "owners": ["vegard"],
        "updated": date(2026, 3, 18),
        "translation_status": {"en": "edited"},
        "ai": {"generated_fields": [], "source": "openai", "review_state": "pending"},
        "resource_kind": "article",
        "authors": ["vegard"],
        "published_on": date(2026, 3, 18),
        "url": "https://example.org/demo-candidate-resource",
        "difficulty": "introductory",
        "estimated_time_minutes": 8,
        "summary": {"en": "Draft summary"},
        "why_selected": {"en": "Draft reason"},
        "instructor_note": {"en": "Review first"},
        "freshness": "evergreen",
        "approved_by": "vegard",
        "approved_on": date(2026, 3, 18),
        "approval_history": [],
        "stale_flag": False,
    }

    with pytest.raises(ValidationError):
        Resource.model_validate(payload)


def test_validator_rejects_missing_exercise_solution_file(tmp_path) -> None:
    copy_repo_subset(tmp_path)
    solution_path = (
        tmp_path / "content" / "exercises" / "ex-iv-concept-check" / "solution.en.qmd"
    )
    solution_path.unlink()

    report = validate_repository(tmp_path, run_build_checks=False)

    assert any(
        issue.code == "missing-solution" and issue.object_id == "ex-iv-concept-check"
        for issue in report.issues
    )


def test_validator_rejects_teacher_blocks_inside_exercise_note(tmp_path) -> None:
    copy_repo_subset(tmp_path)
    note_path = tmp_path / "content" / "exercises" / "ex-iv-concept-check" / "note.en.qmd"
    note_path.write_text(
        note_path.read_text(encoding="utf-8")
        + "\n\n::: {.teacher-only}\nDo not publish.\n:::\n",
        encoding="utf-8",
    )

    report = validate_repository(tmp_path, run_build_checks=False)

    assert any(
        issue.code == "exercise-note-contains-teacher-block"
        and issue.object_id == "ex-iv-concept-check"
        for issue in report.issues
    )


def test_validator_rejects_figure_without_pdf_fallback(tmp_path) -> None:
    copy_repo_subset(tmp_path)
    figure_pdf = tmp_path / "content" / "figures" / "iv-dag-figure" / "figure.pdf"
    figure_pdf.unlink()

    report = validate_repository(tmp_path, run_build_checks=False)

    assert any(
        issue.code == "interactive-figure-missing-static-fallback"
        and issue.object_id == "iv-dag-figure"
        for issue in report.issues
    )


def test_validator_rejects_course_assignment_without_html_output(tmp_path) -> None:
    copy_repo_subset(tmp_path)
    meta_path = tmp_path / "collections" / "assignments" / "assignment-01" / "meta.yml"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace("  - html\n", ""),
        encoding="utf-8",
    )

    report = validate_repository(tmp_path, run_build_checks=False)

    assert any(
        issue.code == "assignment-missing-html-output" and issue.object_id == "assignment-01"
        for issue in report.issues
    )


def test_validator_ignores_course_inbox_material(tmp_path) -> None:
    copy_repo_subset(tmp_path)
    inbox_dir = tmp_path / "course-inbox" / "ec202" / "notes"
    inbox_dir.mkdir(parents=True)
    (inbox_dir / "meta.yml").write_text(
        "id: should-not-load\nkind: concept\nstatus: approved\n",
        encoding="utf-8",
    )
    (inbox_dir / "note.en.qmd").write_text("# Legacy note\n", encoding="utf-8")

    report = validate_repository(tmp_path, run_build_checks=False)

    assert report.object_count >= 26
    assert all(not issue.path.startswith("course-inbox/") for issue in report.issues)


def test_validator_ignores_incomplete_course_shell(tmp_path) -> None:
    copy_repo_subset(tmp_path)
    course_dir = tmp_path / "courses" / "draft-course"
    course_dir.mkdir(parents=True)
    (course_dir / "course.yml").write_text(
        "\n".join(
            [
                "id: draft-course",
                "status: draft",
                "visibility: student",
                "languages:",
                "  - en",
                "title:",
                "  en: Draft course",
                "summary:",
                "  en: Draft summary",
                "owners:",
                "  - vegard",
                "updated: 2026-03-19",
                "",
            ]
        ),
        encoding="utf-8",
    )

    report = validate_repository(tmp_path, run_build_checks=False)

    assert report.ok
    assert report.course_count >= 2
    assert all(issue.path != "courses/draft-course/course.yml" for issue in report.issues)


def copy_repo_subset(target_root) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)
    shutil.copy(
        REPO_ROOT / "representative-targets.yml",
        target_root / "representative-targets.yml",
    )

from __future__ import annotations

import shutil
from datetime import date

import pytest
from pydantic import ValidationError

from app.config import REPO_ROOT
from app.models import Concept, Exercise, Figure
from app.validator import validate_repository


def test_sample_repository_validates_cleanly() -> None:
    report = validate_repository(REPO_ROOT, run_build_checks=False)
    assert report.ok
    assert report.object_count == 7
    assert report.course_count == 1
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


def copy_repo_subset(target_root) -> None:
    for relative_path in ("content", "collections", "courses"):
        shutil.copytree(REPO_ROOT / relative_path, target_root / relative_path)
    shutil.copy(
        REPO_ROOT / "representative-targets.yml",
        target_root / "representative-targets.yml",
    )

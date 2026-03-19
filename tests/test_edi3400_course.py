from __future__ import annotations

import json

from app.assembly import assemble_target
from app.build import build_target
from app.config import REPO_ROOT
from app.indexer import load_repository


def test_edi3400_course_is_indexed_with_first_exercise_slice() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)

    course = index.courses["edi3400"]

    assert course.model.id == "edi3400"
    assert course.model.languages == ["en"]
    assert course.plan.lectures == []
    assert course.plan.assignments == []


def test_edi3400_course_assembles_with_first_exercise_slice() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    assert assembly.target.kind == "course"
    assert assembly.target.identifier == "edi3400"
    assert [entry.identifier for entry in assembly.listing_entries] == [
        "sql-python-problem-set",
        "topic-data-management",
        "topic-databases",
        "topic-sql",
    ]
    assert "EDI 3400 - Programming and Data Management" in assembly.markdown
    assert "SQL and Python problem set" in assembly.markdown
    assert "Data Management" in assembly.markdown
    assert "Databases" in assembly.markdown
    assert "SQL" in assembly.markdown
    assert "Part 4: Databases with SQL and Python" in assembly.markdown
    assert "The assessment model is still draft-level" in assembly.markdown


def test_relational_database_fundamentals_concept_links_to_edi3400() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "relational-database-fundamentals",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Tables model entities" in assembly.markdown
    assert "## Primary keys make rows identifiable" in assembly.markdown
    assert "## Foreign keys make relationships explicit" in assembly.markdown
    assert "sql-query-basics" in related_ids
    assert "python-sql-integration" in related_ids
    assert "sql-python-problem-set" in related_ids
    assert "edi3400" in related_ids


def test_sql_query_basics_concept_links_database_foundations_and_edi3400() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "sql-query-basics",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## `SELECT` and `FROM` define the starting point" in assembly.markdown
    assert "## `WHERE` filters rows" in assembly.markdown
    assert "## Joins reconnect tables through keys" in assembly.markdown
    assert "## `GROUP BY` changes the level of the question" in assembly.markdown
    assert "relational-database-fundamentals" in related_ids
    assert "python-sql-integration" in related_ids
    assert "sql-python-problem-set" in related_ids
    assert "edi3400" in related_ids


def test_python_sql_integration_concept_links_database_foundations_and_edi3400() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-sql-integration",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## `sqlite3` is the simplest bridge" in assembly.markdown
    assert "## Pandas is often the cleanest next step" in assembly.markdown
    assert "## Parameterized queries are safer than string assembly" in assembly.markdown
    assert "## Python can create and populate a database too" in assembly.markdown
    assert "relational-database-fundamentals" in related_ids
    assert "sql-query-basics" in related_ids
    assert "sql-python-problem-set" in related_ids
    assert "edi3400" in related_ids


def test_sql_python_problem_set_links_database_concepts_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "sql-python-problem-set",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "auto_dealership_database.db" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "relational-database-fundamentals" in related_ids
    assert "sql-query-basics" in related_ids
    assert "python-sql-integration" in related_ids
    assert "edi3400" in related_ids


def test_python_sql_integration_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-sql-integration",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python and SQL integration" in html
    assert "Pandas is often the cleanest next step" in html
    assert "Parameterized queries are safer than string assembly" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert "workflow habit" not in html
    assert artifact.output_path.exists()
    assert artifact.build_manifest_path.exists()
    assert artifact.dependency_manifest_path.exists()
    assert artifact.leakage_report_path.exists()
    assert build_manifest["target"]["identifier"] == "python-sql-integration"
    assert leakage_report["status"] == "clean"
    assert leakage_report["teacher_blocks_removed"] == 1


def test_edi3400_course_student_page_builds_with_database_slice() -> None:
    artifact = build_target(
        "edi3400",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")

    assert "EDI 3400 - Programming and Data Management" in html
    assert "Part 4: Databases with SQL and Python" in html
    assert "Assessment Status" in html
    assert "Search LearnForge" in html
    assert "Breadcrumbs:" in html

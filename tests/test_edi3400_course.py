from __future__ import annotations

import json

from app.assembly import assemble_target
from app.build import build_target
from app.config import REPO_ROOT
from app.indexer import load_repository


def test_edi3400_course_is_indexed_with_current_canonical_slices() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)

    course = index.courses["edi3400"]

    assert course.model.id == "edi3400"
    assert course.model.languages == ["en"]
    assert course.plan.lectures == [
        "edi3400-lecture-02",
        "edi3400-lecture-04",
        "edi3400-lecture-04b",
        "edi3400-lecture-05a",
        "edi3400-lecture-05b",
        "edi3400-lecture-05c",
        "edi3400-lecture-11",
        "edi3400-lecture-12",
        "edi3400-lecture-13",
    ]
    assert course.plan.assignments == []


def test_edi3400_course_assembles_with_current_canonical_slices() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    listing_ids = [entry.identifier for entry in assembly.listing_entries]

    assert assembly.target.kind == "course"
    assert assembly.target.identifier == "edi3400"
    assert listing_ids[:8] == [
        "edi3400-lecture-02",
        "edi3400-lecture-04",
        "edi3400-lecture-04b",
        "edi3400-lecture-05a",
        "edi3400-lecture-05b",
        "edi3400-lecture-05c",
        "edi3400-lecture-11",
        "edi3400-lecture-12",
    ]
    assert listing_ids[8] == "edi3400-lecture-13"
    assert "python-basics-problem-set" in listing_ids
    assert "python-control-flow-problem-set" in listing_ids
    assert "python-file-handling-lab" in listing_ids
    assert "python-functions-problem-set" in listing_ids
    assert "python-standard-library-problem-set" in listing_ids
    assert "python-bank-account-class-lab" in listing_ids
    assert "sql-python-problem-set" in listing_ids
    assert "topic-data-management" in listing_ids
    assert "topic-databases" in listing_ids
    assert "topic-python" in listing_ids
    assert "topic-programming" in listing_ids
    assert "topic-sql" in listing_ids
    assert "EDI 3400 - Programming and Data Management" in assembly.markdown
    assert "Lecture 2 - Python basics and containers" in assembly.markdown
    assert "Lecture 4 - Control flow and loops" in assembly.markdown
    assert "Lecture 4B - File handling and local data" in assembly.markdown
    assert "Lecture 5A - Functions and reusable code" in assembly.markdown
    assert "Lecture 5B - Standard-library utilities" in assembly.markdown
    assert "Lecture 5C - Classes and objects" in assembly.markdown
    assert "Lecture 11 - Introduction to relational databases" in assembly.markdown
    assert "Lecture 12 - SQL basics" in assembly.markdown
    assert "Lecture 13 - Python and SQL" in assembly.markdown
    assert "Python basics problem set" in assembly.markdown
    assert "Python control flow problem set" in assembly.markdown
    assert "Python file handling lab" in assembly.markdown
    assert "Python functions problem set" in assembly.markdown
    assert "Python standard-library utilities problem set" in assembly.markdown
    assert "Python bank-account class lab" in assembly.markdown
    assert "SQL and Python problem set" in assembly.markdown
    assert "Programming" in assembly.markdown
    assert "Python" in assembly.markdown
    assert "Data Management" in assembly.markdown
    assert "Databases" in assembly.markdown
    assert "SQL" in assembly.markdown
    assert "Part 1: Programming with basic Python" in assembly.markdown
    assert "Part 4: Databases with SQL and Python" in assembly.markdown
    assert "The assessment model is still draft-level" in assembly.markdown


def test_python_basics_and_containers_concept_links_edi3400_foundations() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-basics-and-containers",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Names let Python reuse values" in assembly.markdown
    assert "## Types determine what operations make sense" in assembly.markdown
    assert "## Built-in functions give quick feedback" in assembly.markdown
    assert "## Lists, tuples, and strings are ordered containers" in assembly.markdown
    assert "## Dictionaries and sets solve different lookup problems" in assembly.markdown
    assert "python-basics-problem-set" in related_ids
    assert "python-control-flow" in related_ids
    assert "python-sql-integration" in related_ids
    assert "edi3400-lecture-02" in related_ids
    assert "edi3400" in related_ids


def test_python_control_flow_concept_links_edi3400_foundations() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-control-flow",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Control flow changes what a program does next" in assembly.markdown
    assert "## `if`, `elif`, and `else` choose one branch" in assembly.markdown
    assert "## `for` loops work best when the data source is known" in assembly.markdown
    assert "## `while` loops need a clear exit condition" in assembly.markdown
    assert "## `try` and `except` turn crashes into handled cases" in assembly.markdown
    assert "python-basics-and-containers" in related_ids
    assert "python-control-flow-problem-set" in related_ids
    assert "python-file-handling" in related_ids
    assert "edi3400-lecture-04" in related_ids
    assert "edi3400" in related_ids


def test_python_file_handling_concept_links_edi3400_foundations() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-file-handling",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Files are one of Python's simplest external data sources" in assembly.markdown
    assert "## A file path tells Python where to look" in assembly.markdown
    assert "## `with open(...)` is the safest default pattern" in assembly.markdown
    assert "## CSV is still just a file, but with structure" in assembly.markdown
    assert "python-control-flow" in related_ids
    assert "python-file-handling-lab" in related_ids
    assert "python-functions" in related_ids
    assert "python-sql-integration" in related_ids
    assert "edi3400-lecture-04b" in related_ids
    assert "edi3400" in related_ids


def test_python_functions_concept_links_edi3400_foundations() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-functions",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Functions package logic so it can be reused" in assembly.markdown
    assert "## `def` creates a named unit of work" in assembly.markdown
    assert "## Parameters are the inputs to the function" in assembly.markdown
    assert "## `return` sends the result back to the caller" in assembly.markdown
    assert "## Functions often wrap control flow" in assembly.markdown
    assert "python-control-flow" in related_ids
    assert "python-file-handling" in related_ids
    assert "python-classes-and-objects" in related_ids
    assert "python-standard-library-utilities" in related_ids
    assert "python-functions-problem-set" in related_ids
    assert "edi3400-lecture-05a" in related_ids
    assert "edi3400" in related_ids


def test_python_standard_library_utilities_concept_links_edi3400_foundations() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-standard-library-utilities",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Modules package reusable tools beyond the built-ins" in assembly.markdown
    assert "## `import` makes library code available" in assembly.markdown
    assert "## `math` covers common numerical functions" in assembly.markdown
    assert "## `random` supports sampling and shuffling" in assembly.markdown
    assert "## `statistics` summarizes small numeric samples" in assembly.markdown
    assert "python-functions" in related_ids
    assert "python-file-handling" in related_ids
    assert "python-classes-and-objects" in related_ids
    assert "python-standard-library-problem-set" in related_ids
    assert "edi3400-lecture-05b" in related_ids
    assert "edi3400" in related_ids


def test_python_classes_and_objects_concept_links_edi3400_foundations() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-classes-and-objects",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Classes bundle related data and behavior" in assembly.markdown
    assert "## A class is a blueprint and an object is one instance" in assembly.markdown
    assert "## `__init__` sets the starting state" in assembly.markdown
    assert "## Attributes belong to each object" in assembly.markdown
    assert "## `self` refers to the current object" in assembly.markdown
    assert "python-functions" in related_ids
    assert "python-standard-library-utilities" in related_ids
    assert "python-bank-account-class-lab" in related_ids
    assert "edi3400-lecture-05c" in related_ids
    assert "edi3400" in related_ids


def test_edi3400_lecture_02_assembly_expands_python_basics_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-02",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["python-basics-and-containers", "python-basics-problem-set"]
    assert "## Names let Python reuse values" in assembly.markdown
    assert "## Problem set brief" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown


def test_edi3400_lecture_04_assembly_expands_control_flow_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-04",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["python-control-flow", "python-control-flow-problem-set"]
    assert "## `if`, `elif`, and `else` choose one branch" in assembly.markdown
    assert "## Problem set brief" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown


def test_edi3400_lecture_04b_assembly_expands_file_handling_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-04b",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["python-file-handling", "python-file-handling-lab"]
    assert "## A file path tells Python where to look" in assembly.markdown
    assert "## Lab brief" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown


def test_edi3400_lecture_05a_assembly_expands_functions_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-05a",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["python-functions", "python-functions-problem-set"]
    assert "## `def` creates a named unit of work" in assembly.markdown
    assert "## Problem set brief" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown


def test_edi3400_lecture_05b_assembly_expands_standard_library_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-05b",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == [
        "python-standard-library-utilities",
        "python-standard-library-problem-set",
    ]
    assert "## `import` makes library code available" in assembly.markdown
    assert "## Problem set brief" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown


def test_edi3400_lecture_05c_assembly_expands_classes_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-05c",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == [
        "python-classes-and-objects",
        "python-bank-account-class-lab",
    ]
    assert "## `__init__` sets the starting state" in assembly.markdown
    assert "## Lab brief" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown


def test_python_basics_problem_set_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-basics-problem-set",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Problem set brief" in assembly.markdown
    assert "Programming with Python" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "python-basics-and-containers" in related_ids
    assert "edi3400-lecture-02" in related_ids
    assert "edi3400" in related_ids


def test_python_control_flow_problem_set_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-control-flow-problem-set",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Problem set brief" in assembly.markdown
    assert "guess_sequence = [3, 9, 7]" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "python-basics-and-containers" in related_ids
    assert "python-control-flow" in related_ids
    assert "edi3400-lecture-04" in related_ids
    assert "edi3400" in related_ids


def test_python_file_handling_lab_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-file-handling-lab",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "assets/study_log.txt" in assembly.markdown
    assert "assets/media_consumption_sample.csv" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "python-control-flow" in related_ids
    assert "python-file-handling" in related_ids
    assert "edi3400-lecture-04b" in related_ids
    assert "edi3400" in related_ids


def test_python_functions_problem_set_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-functions-problem-set",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Problem set brief" in assembly.markdown
    assert "reverse_string(text)" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "python-control-flow" in related_ids
    assert "python-functions" in related_ids
    assert "edi3400-lecture-05a" in related_ids
    assert "edi3400" in related_ids


def test_python_standard_library_problem_set_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-standard-library-problem-set",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Problem set brief" in assembly.markdown
    assert "import math" in assembly.markdown
    assert "re.findall(...)" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "python-functions" in related_ids
    assert "python-standard-library-utilities" in related_ids
    assert "edi3400-lecture-05b" in related_ids
    assert "edi3400" in related_ids


def test_python_bank_account_class_lab_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "python-bank-account-class-lab",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "class BankAccount:" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "python-control-flow" in related_ids
    assert "python-functions" in related_ids
    assert "python-classes-and-objects" in related_ids
    assert "edi3400-lecture-05c" in related_ids
    assert "edi3400" in related_ids


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
    assert "edi3400-lecture-11" in related_ids
    assert "edi3400" in related_ids


def test_edi3400_lecture_11_assembly_expands_relational_database_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-11",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["relational-database-fundamentals"]
    assert (
        "## Relational databases organize data by structure, not by accident"
        in assembly.markdown
    )
    assert "## `SELECT` and `FROM` define the starting point" not in assembly.markdown
    assert "## Python turns SQL work into a reproducible workflow" not in assembly.markdown


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
    assert "edi3400-lecture-12" in related_ids
    assert "edi3400" in related_ids


def test_edi3400_lecture_12_assembly_expands_sql_query_basics() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-12",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["sql-query-basics"]
    assert "## `SELECT` and `FROM` define the starting point" in assembly.markdown
    assert "## `WHERE` filters rows" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown
    assert "## Lab brief" not in assembly.markdown


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
    assert "edi3400-lecture-13" in related_ids
    assert "edi3400" in related_ids


def test_edi3400_lecture_13_assembly_expands_python_sql_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-13",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["python-sql-integration", "sql-python-problem-set"]
    assert "## `sqlite3` is the simplest bridge" in assembly.markdown
    assert "## Pandas is often the cleanest next step" in assembly.markdown
    assert "## Lab brief" in assembly.markdown
    assert "## `SELECT` and `FROM` define the starting point" not in assembly.markdown


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
    assert "edi3400-lecture-13" in related_ids
    assert "edi3400" in related_ids


def test_sql_python_problem_set_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "sql-python-problem-set",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "SQL and Python problem set" in html
    assert "auto_dealership_database.db" in html
    assert "## Solution" not in html
    assert "The safest teacher solution is a small set of representative SQL queries" not in html
    assert build_manifest["target"]["identifier"] == "sql-python-problem-set"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_sql_python_problem_set_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "sql-python-problem-set",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "SQL and Python problem set" in html
    assert "The safest teacher solution is a small set of representative SQL queries" in html
    assert "Representative Python workflow" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "sql-python-problem-set"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


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


def test_python_basics_and_containers_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-basics-and-containers",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python basics and containers" in html
    assert "Names let Python reuse values" in html
    assert "Dictionaries and sets solve different lookup problems" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-basics-and-containers"
    assert leakage_report["status"] == "clean"


def test_python_basics_problem_set_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-basics-problem-set",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python basics problem set" in html
    assert "Programming with Python" in html
    assert "## Solution" not in html
    assert "The strongest teacher solution keeps the exercise close" not in html
    assert build_manifest["target"]["identifier"] == "python-basics-problem-set"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_python_basics_problem_set_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "python-basics-problem-set",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python basics problem set" in html
    assert "Minimal reference implementation" in html
    assert "right container for the task" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-basics-problem-set"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_python_control_flow_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-control-flow",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python control flow" in html
    assert "Control flow changes what a program does next" in html
    assert "List comprehensions are compact loop patterns" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-control-flow"
    assert leakage_report["status"] == "clean"


def test_python_control_flow_problem_set_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-control-flow-problem-set",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python control flow problem set" in html
    assert "guess_sequence = [3, 9, 7]" in html
    assert "## Solution" not in html
    assert "The strongest teacher solution keeps the logic visible" not in html
    assert build_manifest["target"]["identifier"] == "python-control-flow-problem-set"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_python_control_flow_problem_set_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "python-control-flow-problem-set",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python control flow problem set" in html
    assert "Minimal reference implementation" in html
    assert "The strongest teacher solution keeps the logic visible" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-control-flow-problem-set"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_python_file_handling_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-file-handling",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python file handling" in html
    assert "Python’s simplest external data sources" in html
    assert "with open(...)" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-file-handling"
    assert leakage_report["status"] == "clean"


def test_python_file_handling_lab_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-file-handling-lab",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python file handling lab" in html
    assert "assets/study_log.txt" in html
    assert "assets/media_consumption_sample.csv" in html
    assert "## Solution" not in html
    assert "The strongest teacher solution keeps the file workflow explicit" not in html
    assert build_manifest["target"]["identifier"] == "python-file-handling-lab"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_python_file_handling_lab_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "python-file-handling-lab",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python file handling lab" in html
    assert "Minimal reference implementation" in html
    assert "The strongest teacher solution keeps the file workflow explicit" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-file-handling-lab"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_python_functions_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-functions",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python functions" in html
    assert "Functions package logic so it can be reused" in html
    assert "Functions often wrap control flow" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-functions"
    assert leakage_report["status"] == "clean"


def test_python_standard_library_utilities_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-standard-library-utilities",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python standard-library utilities" in html
    assert "Modules package reusable tools beyond the built-ins" in html
    assert "statistics.mean(numbers)" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-standard-library-utilities"
    assert leakage_report["status"] == "clean"


def test_python_classes_and_objects_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-classes-and-objects",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python classes and objects" in html
    assert "Classes bundle related data and behavior" in html
    assert "Attributes belong to each object" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-classes-and-objects"
    assert leakage_report["status"] == "clean"


def test_python_functions_problem_set_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-functions-problem-set",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python functions problem set" in html
    assert "reverse_string(text)" in html
    assert "## Solution" not in html
    assert "The strongest teacher solution keeps each function small" not in html
    assert build_manifest["target"]["identifier"] == "python-functions-problem-set"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_python_bank_account_class_lab_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-bank-account-class-lab",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python bank-account class lab" in html
    assert "Funds unavailable" in html
    assert "## Solution" not in html
    assert "The strongest teacher solution keeps the class small" not in html
    assert build_manifest["target"]["identifier"] == "python-bank-account-class-lab"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_python_standard_library_problem_set_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "python-standard-library-problem-set",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python standard-library utilities problem set" in html
    assert "math.log(...)" in html
    assert "## Solution" not in html
    assert "The strongest teacher solution keeps the imports explicit" not in html
    assert build_manifest["target"]["identifier"] == "python-standard-library-problem-set"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_python_functions_problem_set_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "python-functions-problem-set",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python functions problem set" in html
    assert "Minimal reference implementation" in html
    assert "The strongest teacher solution keeps each function small" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-functions-problem-set"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_python_standard_library_problem_set_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "python-standard-library-problem-set",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python standard-library utilities problem set" in html
    assert "Minimal reference implementation" in html
    assert "The strongest teacher solution keeps the imports explicit" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-standard-library-problem-set"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_python_bank_account_class_lab_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "python-bank-account-class-lab",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Python bank-account class lab" in html
    assert "Minimal reference implementation" in html
    assert "The strongest teacher solution keeps the class small" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "python-bank-account-class-lab"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


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
    assert "Part 1: Programming with basic Python" in html
    assert "Part 4: Databases with SQL and Python" in html
    assert "../../collection/edi3400-lecture-02/edi3400-lecture-02.html" in html
    assert "../../collection/edi3400-lecture-04/edi3400-lecture-04.html" in html
    assert "../../collection/edi3400-lecture-04b/edi3400-lecture-04b.html" in html
    assert "../../collection/edi3400-lecture-05a/edi3400-lecture-05a.html" in html
    assert "../../collection/edi3400-lecture-05b/edi3400-lecture-05b.html" in html
    assert "../../collection/edi3400-lecture-05c/edi3400-lecture-05c.html" in html
    assert "../../collection/edi3400-lecture-11/edi3400-lecture-11.html" in html
    assert "../../collection/edi3400-lecture-12/edi3400-lecture-12.html" in html
    assert "../../collection/edi3400-lecture-13/edi3400-lecture-13.html" in html
    assert "Python basics problem set" in html
    assert "Python control flow problem set" in html
    assert "Python file handling lab" in html
    assert "Python functions problem set" in html
    assert "Python standard-library utilities problem set" in html
    assert "Python bank-account class lab" in html
    assert "Assessment Status" in html
    assert "Search LearnForge" in html
    assert "Breadcrumbs:" in html


def test_edi3400_lecture_02_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-02",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 2 - Python basics and containers" in html
    assert "This lecture includes" in html
    assert "Python basics and containers" in html
    assert "Python basics problem set" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["python-basics-and-containers", "python-basics-problem-set"]


def test_edi3400_lecture_04_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-04",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 4 - Control flow and loops" in html
    assert "This lecture includes" in html
    assert "Python control flow" in html
    assert "Python control flow problem set" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["python-control-flow", "python-control-flow-problem-set"]


def test_edi3400_lecture_04b_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-04b",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 4B - File handling and local data" in html
    assert "This lecture includes" in html
    assert "Python file handling" in html
    assert "Python file handling lab" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["python-file-handling", "python-file-handling-lab"]


def test_edi3400_lecture_05a_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-05a",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 5A - Functions and reusable code" in html
    assert "This lecture includes" in html
    assert "Python functions" in html
    assert "Python functions problem set" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["python-functions", "python-functions-problem-set"]


def test_edi3400_lecture_05b_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-05b",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 5B - Standard-library utilities" in html
    assert "This lecture includes" in html
    assert "Python standard-library utilities" in html
    assert "Python standard-library utilities problem set" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == [
        "python-standard-library-utilities",
        "python-standard-library-problem-set",
    ]


def test_edi3400_lecture_05c_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-05c",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 5C - Classes and objects" in html
    assert "This lecture includes" in html
    assert "Python classes and objects" in html
    assert "Python bank-account class lab" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == [
        "python-classes-and-objects",
        "python-bank-account-class-lab",
    ]


def test_edi3400_lecture_11_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-11",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 11 - Introduction to relational databases" in html
    assert "This lecture includes" in html
    assert "Relational database fundamentals" in html
    assert "SELECT and FROM define the starting point" not in html
    assert "Python turns SQL work into a reproducible workflow" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["relational-database-fundamentals"]


def test_edi3400_lecture_12_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-12",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 12 - SQL basics" in html
    assert "This lecture includes" in html
    assert "SQL query basics" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert "Lab brief" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["sql-query-basics"]


def test_edi3400_lecture_13_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-13",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 13 - Python and SQL" in html
    assert "This lecture includes" in html
    assert "Python and SQL integration" in html
    assert "SQL and Python problem set" in html
    assert "SELECT and FROM define the starting point" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["python-sql-integration", "sql-python-problem-set"]

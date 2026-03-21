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
        "edi3400-lecture-01",
        "edi3400-lecture-02",
        "edi3400-lecture-04",
        "edi3400-lecture-04b",
        "edi3400-lecture-05a",
        "edi3400-lecture-05b",
        "edi3400-lecture-05c",
        "edi3400-lecture-06",
        "edi3400-lecture-07",
        "edi3400-lecture-08",
        "edi3400-lecture-09",
        "edi3400-lecture-10a",
        "edi3400-lecture-10b",
        "edi3400-lecture-11",
        "edi3400-lecture-12",
        "edi3400-lecture-13",
    ]
    assert course.plan.assignments == [
        "edi3400-assignment-01",
        "edi3400-assignment-02",
        "edi3400-assignment-03",
        "edi3400-assignment-04",
    ]


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
    assert listing_ids[:15] == [
        "edi3400-lecture-01",
        "edi3400-lecture-02",
        "edi3400-lecture-04",
        "edi3400-lecture-04b",
        "edi3400-lecture-05a",
        "edi3400-lecture-05b",
        "edi3400-lecture-05c",
        "edi3400-lecture-06",
        "edi3400-lecture-07",
        "edi3400-lecture-08",
        "edi3400-lecture-09",
        "edi3400-lecture-10a",
        "edi3400-lecture-10b",
        "edi3400-lecture-11",
        "edi3400-lecture-12",
    ]
    assert listing_ids[15] == "edi3400-lecture-13"
    assert "python-basics-problem-set" in listing_ids
    assert "python-control-flow-problem-set" in listing_ids
    assert "python-file-handling-lab" in listing_ids
    assert "python-functions-problem-set" in listing_ids
    assert "python-standard-library-problem-set" in listing_ids
    assert "python-bank-account-class-lab" in listing_ids
    assert "numpy-array-and-matrix-lab" in listing_ids
    assert "pandas-dataframe-analysis-lab" in listing_ids
    assert "matplotlib-sales-visualization-lab" in listing_ids
    assert "numpy-pandas-matplotlib-problem-set" in listing_ids
    assert "web-data-extraction-lab" in listing_ids
    assert "time-series-analysis-lab" in listing_ids
    assert "sql-python-problem-set" in listing_ids
    assert "edi3400-assignment-01" in listing_ids
    assert "edi3400-assignment-02" in listing_ids
    assert "edi3400-assignment-03" in listing_ids
    assert "edi3400-assignment-04" in listing_ids
    assert "topic-data-management" in listing_ids
    assert "topic-databases" in listing_ids
    assert "topic-python" in listing_ids
    assert "topic-programming" in listing_ids
    assert "topic-sql" in listing_ids
    assert "EDI 3400 - Programming and Data Management" in assembly.markdown
    assert "Lecture 1 - Course orientation and the Python ecosystem" in assembly.markdown
    assert "Course orientation and the Python ecosystem" in assembly.markdown
    assert "Lecture 2 - Python basics and containers" in assembly.markdown
    assert "Lecture 4 - Control flow and loops" in assembly.markdown
    assert "Lecture 4B - File handling and local data" in assembly.markdown
    assert "Lecture 5A - Functions and reusable code" in assembly.markdown
    assert "Lecture 5B - Standard-library utilities" in assembly.markdown
    assert "Lecture 5C - Classes and objects" in assembly.markdown
    assert "Lecture 6 - NumPy arrays and matrices" in assembly.markdown
    assert "Lecture 7 - Pandas series and data frames" in assembly.markdown
    assert "Lecture 8 - Matplotlib basic plots" in assembly.markdown
    assert "Lecture 9 - IDEs and generative AI for programming" in assembly.markdown
    assert "Lecture 10A - Web data extraction" in assembly.markdown
    assert "Lecture 10B - Time-series analysis and statistics" in assembly.markdown
    assert "Lecture 11 - Introduction to relational databases" in assembly.markdown
    assert "Lecture 12 - SQL basics" in assembly.markdown
    assert "Lecture 13 - Python and SQL" in assembly.markdown
    assert "Python basics problem set" in assembly.markdown
    assert "Python control flow problem set" in assembly.markdown
    assert "Python file handling lab" in assembly.markdown
    assert "Python functions problem set" in assembly.markdown
    assert "Python standard-library utilities problem set" in assembly.markdown
    assert "Python bank-account class lab" in assembly.markdown
    assert "NumPy array and matrix lab" in assembly.markdown
    assert "Pandas dataframe analysis lab" in assembly.markdown
    assert "Matplotlib sales visualization lab" in assembly.markdown
    assert "NumPy, Pandas, and Matplotlib problem set" in assembly.markdown
    assert "Web data extraction lab" in assembly.markdown
    assert "Time-series analysis lab" in assembly.markdown
    assert "Debugging and AI workflow lab" in assembly.markdown
    assert "SQL and Python problem set" in assembly.markdown
    assert "Assignment 1" in assembly.markdown
    assert "Assignment 2" in assembly.markdown
    assert "Assignment 3" in assembly.markdown
    assert "Assignment 4" in assembly.markdown
    assert "Programming" in assembly.markdown
    assert "Python" in assembly.markdown
    assert "Data Management" in assembly.markdown
    assert "Databases" in assembly.markdown
    assert "SQL" in assembly.markdown
    assert "Part 1: Programming with basic Python" in assembly.markdown
    assert "Part 3: Advanced topics" in assembly.markdown
    assert "Part 4: Databases with SQL and Python" in assembly.markdown
    assert "Assignment 1" in assembly.markdown


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


def test_numpy_arrays_and_matrices_concept_links_edi3400_foundations() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "numpy-arrays-and-matrices",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## NumPy makes numerical data explicit and scalable" in assembly.markdown
    assert "## `np.array(...)` creates an `ndarray`" in assembly.markdown
    assert "## Shape and dtype describe structure" in assembly.markdown
    assert "## Vectorized arithmetic works on whole arrays" in assembly.markdown
    assert "## `mean`, `std`, and `dot` support common numerical workflows" in assembly.markdown
    assert "python-standard-library-utilities" in related_ids
    assert "numpy-array-and-matrix-lab" in related_ids
    assert "numpy-pandas-matplotlib-problem-set" in related_ids
    assert "edi3400-lecture-06" in related_ids
    assert "edi3400" in related_ids


def test_pandas_series_and_dataframes_concept_links_edi3400_foundations() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "pandas-series-and-dataframes",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Pandas organizes labeled tabular data" in assembly.markdown
    assert "## A `Series` stores one labeled sequence" in assembly.markdown
    assert "## A `DataFrame` organizes aligned columns" in assembly.markdown
    assert "## `[]`, `loc`, and `iloc` answer different selection questions" in assembly.markdown
    assert (
        "## `read_csv(...)` and parsed dates connect files to analysis workflows"
        in assembly.markdown
    )
    assert "numpy-arrays-and-matrices" in related_ids
    assert "pandas-dataframe-analysis-lab" in related_ids
    assert "numpy-pandas-matplotlib-problem-set" in related_ids
    assert "edi3400-lecture-07" in related_ids
    assert "edi3400" in related_ids


def test_matplotlib_basic_plots_concept_links_edi3400_foundations() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "matplotlib-basic-plots",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Matplotlib turns numeric data into visible patterns" in assembly.markdown
    assert "## `plt.plot(...)` creates a line plot for ordered data" in assembly.markdown
    assert "## `plt.scatter(...)` is useful when comparing two variables" in assembly.markdown
    assert "## `plt.bar(...)` compares grouped values clearly" in assembly.markdown
    assert "## `savefig(...)` turns a plot into a reusable artifact" in assembly.markdown
    assert "pandas-series-and-dataframes" in related_ids
    assert "matplotlib-sales-visualization-lab" in related_ids
    assert "numpy-pandas-matplotlib-problem-set" in related_ids
    assert "edi3400-lecture-08" in related_ids
    assert "edi3400" in related_ids


def test_ide_debugging_testing_and_ai_assistants_concept_links_edi3400_workflow() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "ide-debugging-testing-and-ai-assistants",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## An IDE shortens the programming feedback loop" in assembly.markdown
    assert "## Error messages and tracebacks are the first debugging tool" in assembly.markdown
    assert "## Unit tests turn expectations into repeatable checks" in assembly.markdown
    assert "## AI assistants can accelerate suggestions, not verification" in assembly.markdown
    assert "numpy-pandas-matplotlib-problem-set" in related_ids
    assert "debugging-and-ai-workflow-lab" in related_ids
    assert "python-sql-integration" in related_ids
    assert "edi3400-lecture-09" in related_ids
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


def test_edi3400_lecture_06_assembly_expands_numpy_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-06",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["numpy-arrays-and-matrices", "numpy-array-and-matrix-lab"]
    assert "## `np.array(...)` creates an `ndarray`" in assembly.markdown
    assert "## Lab brief" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown


def test_edi3400_lecture_07_assembly_expands_pandas_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-07",
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
        "pandas-series-and-dataframes",
        "pandas-dataframe-analysis-lab",
    ]
    assert "## A `Series` stores one labeled sequence" in assembly.markdown
    assert "## Lab brief" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown


def test_edi3400_lecture_08_assembly_expands_matplotlib_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-08",
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
        "matplotlib-basic-plots",
        "matplotlib-sales-visualization-lab",
        "numpy-pandas-matplotlib-problem-set",
    ]
    assert "## `plt.plot(...)` creates a line plot for ordered data" in assembly.markdown
    assert "## Lab brief" in assembly.markdown
    assert "## Problem set brief" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown


def test_edi3400_lecture_09_assembly_expands_workflow_support_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-09",
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
        "ide-debugging-testing-and-ai-assistants",
        "debugging-and-ai-workflow-lab",
    ]
    assert "## An IDE shortens the programming feedback loop" in assembly.markdown
    assert "## Exercise brief" in assembly.markdown
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


def test_numpy_array_and_matrix_lab_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "numpy-array-and-matrix-lab",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "np.arange(1, 13).reshape((3, 4))" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "python-functions" in related_ids
    assert "python-standard-library-utilities" in related_ids
    assert "numpy-arrays-and-matrices" in related_ids
    assert "edi3400-lecture-06" in related_ids
    assert "edi3400" in related_ids


def test_pandas_dataframe_analysis_lab_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "pandas-dataframe-analysis-lab",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "assets/campus_store_sales.csv" in assembly.markdown
    assert (
        'pd.read_csv("assets/campus_store_sales.csv", parse_dates=["date"])'
        in assembly.markdown
    )
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "python-file-handling" in related_ids
    assert "numpy-arrays-and-matrices" in related_ids
    assert "pandas-series-and-dataframes" in related_ids
    assert "edi3400-lecture-07" in related_ids
    assert "edi3400" in related_ids


def test_matplotlib_sales_visualization_lab_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "matplotlib-sales-visualization-lab",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "assets/campus_store_plotting_data.csv" in assembly.markdown
    assert "import matplotlib.pyplot as plt" in assembly.markdown
    assert "plt.savefig(...)" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "pandas-series-and-dataframes" in related_ids
    assert "matplotlib-basic-plots" in related_ids
    assert "edi3400-lecture-08" in related_ids
    assert "edi3400" in related_ids


def test_numpy_pandas_matplotlib_problem_set_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "numpy-pandas-matplotlib-problem-set",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Problem set brief" in assembly.markdown
    assert "assets/campus_store_performance.csv" in assembly.markdown
    assert "np.round(average_order_value[:5], 2)" in assembly.markdown
    assert "campus_store_revenue_report.png" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "numpy-arrays-and-matrices" in related_ids
    assert "pandas-series-and-dataframes" in related_ids
    assert "matplotlib-basic-plots" in related_ids
    assert "edi3400-lecture-08" in related_ids
    assert "edi3400" in related_ids


def test_debugging_and_ai_workflow_lab_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "debugging-and-ai-workflow-lab",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Exercise brief" in assembly.markdown
    assert "assets/sales_report_debug_case.py" in assembly.markdown
    assert "pytest -q" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "python-functions" in related_ids
    assert "ide-debugging-testing-and-ai-assistants" in related_ids
    assert "edi3400-lecture-09" in related_ids
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


def test_numpy_arrays_and_matrices_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "numpy-arrays-and-matrices",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "NumPy arrays and matrices" in html
    assert "NumPy makes numerical data explicit and scalable" in html
    assert "Vectorized arithmetic works on whole arrays" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "numpy-arrays-and-matrices"
    assert leakage_report["status"] == "clean"


def test_pandas_series_and_dataframes_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "pandas-series-and-dataframes",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Pandas series and data frames" in html
    assert "Pandas organizes labeled tabular data" in html
    assert "A <code>Series</code> stores one labeled sequence" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "pandas-series-and-dataframes"
    assert leakage_report["status"] == "clean"


def test_matplotlib_basic_plots_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "matplotlib-basic-plots",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Matplotlib basic plots" in html
    assert "Matplotlib turns numeric data into visible patterns" in html
    assert "savefig" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "matplotlib-basic-plots"
    assert leakage_report["status"] == "clean"


def test_ide_debugging_testing_and_ai_assistants_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "ide-debugging-testing-and-ai-assistants",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "IDEs, debugging, testing, and AI assistants" in html
    assert "Error messages and tracebacks are the first debugging tool" in html
    assert "Unit tests turn expectations into repeatable checks" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "ide-debugging-testing-and-ai-assistants"
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


def test_numpy_array_and_matrix_lab_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "numpy-array-and-matrix-lab",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "NumPy array and matrix lab" in html
    assert "matrix multiplication" in html
    assert "## Solution" not in html
    assert "The strongest teacher solution keeps the array structure visible" not in html
    assert build_manifest["target"]["identifier"] == "numpy-array-and-matrix-lab"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_pandas_dataframe_analysis_lab_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "pandas-dataframe-analysis-lab",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Pandas dataframe analysis lab" in html
    assert "assets/campus_store_sales.csv" in html
    assert "## Solution" not in html
    assert (
        "The strongest teacher solution keeps the table small, labeled, and inspectable"
        not in html
    )
    assert build_manifest["target"]["identifier"] == "pandas-dataframe-analysis-lab"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_matplotlib_sales_visualization_lab_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "matplotlib-sales-visualization-lab",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Matplotlib sales visualization lab" in html
    assert "assets/campus_store_plotting_data.csv" in html
    assert "revenue_trend.png" in html
    assert "## Solution" not in html
    assert "The strongest teacher solution keeps the plotting steps explicit" not in html
    assert build_manifest["target"]["identifier"] == "matplotlib-sales-visualization-lab"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_numpy_pandas_matplotlib_problem_set_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "numpy-pandas-matplotlib-problem-set",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "NumPy, Pandas, and Matplotlib problem set" in html
    assert "assets/campus_store_performance.csv" in html
    assert "campus_store_revenue_report.png" in html
    assert "## Solution" not in html
    assert "The strongest teacher solution keeps the full workflow staged" not in html
    assert build_manifest["target"]["identifier"] == "numpy-pandas-matplotlib-problem-set"
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_debugging_and_ai_workflow_lab_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "debugging-and-ai-workflow-lab",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Debugging and AI workflow lab" in html
    assert "assets/sales_report_debug_case.py" in html
    assert "pytest -q" in html
    assert "## Solution" not in html
    assert "The strongest teacher solution keeps the debugging workflow evidence-based" not in html
    assert build_manifest["target"]["identifier"] == "debugging-and-ai-workflow-lab"
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


def test_numpy_array_and_matrix_lab_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "numpy-array-and-matrix-lab",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "NumPy array and matrix lab" in html
    assert "Minimal reference implementation" in html
    assert "The strongest teacher solution keeps the array structure visible" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "numpy-array-and-matrix-lab"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_pandas_dataframe_analysis_lab_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "pandas-dataframe-analysis-lab",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Pandas dataframe analysis lab" in html
    assert "Minimal reference implementation" in html
    assert "The strongest teacher solution keeps the table small, labeled, and inspectable" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "pandas-dataframe-analysis-lab"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_matplotlib_sales_visualization_lab_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "matplotlib-sales-visualization-lab",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Matplotlib sales visualization lab" in html
    assert "Minimal reference implementation" in html
    assert "The strongest teacher solution keeps the plotting steps explicit" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "matplotlib-sales-visualization-lab"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_numpy_pandas_matplotlib_problem_set_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "numpy-pandas-matplotlib-problem-set",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "NumPy, Pandas, and Matplotlib problem set" in html
    assert "Minimal reference implementation" in html
    assert "The strongest teacher solution keeps the full workflow staged" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "numpy-pandas-matplotlib-problem-set"
    assert leakage_report["status"] == "not_applicable"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 1


def test_debugging_and_ai_workflow_lab_teacher_page_builds_with_solution() -> None:
    artifact = build_target(
        "debugging-and-ai-workflow-lab",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Debugging and AI workflow lab" in html
    assert "Minimal reference implementation" in html
    assert "The strongest teacher solution keeps the debugging workflow evidence-based" in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "debugging-and-ai-workflow-lab"
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
    assert "Part 3: Advanced topics" in html
    assert "Part 4: Databases with SQL and Python" in html
    assert "../../collection/edi3400-lecture-01/edi3400-lecture-01.html" in html
    assert "Course orientation and the Python ecosystem" in html
    assert "../../collection/edi3400-lecture-02/edi3400-lecture-02.html" in html
    assert "../../collection/edi3400-lecture-04/edi3400-lecture-04.html" in html
    assert "../../collection/edi3400-lecture-04b/edi3400-lecture-04b.html" in html
    assert "../../collection/edi3400-lecture-05a/edi3400-lecture-05a.html" in html
    assert "../../collection/edi3400-lecture-05b/edi3400-lecture-05b.html" in html
    assert "../../collection/edi3400-lecture-05c/edi3400-lecture-05c.html" in html
    assert "../../collection/edi3400-lecture-06/edi3400-lecture-06.html" in html
    assert "../../collection/edi3400-lecture-07/edi3400-lecture-07.html" in html
    assert "../../collection/edi3400-lecture-08/edi3400-lecture-08.html" in html
    assert "../../collection/edi3400-lecture-09/edi3400-lecture-09.html" in html
    assert "../../collection/edi3400-lecture-10a/edi3400-lecture-10a.html" in html
    assert "../../collection/edi3400-lecture-10b/edi3400-lecture-10b.html" in html
    assert "../../collection/edi3400-lecture-11/edi3400-lecture-11.html" in html
    assert "../../collection/edi3400-lecture-12/edi3400-lecture-12.html" in html
    assert "../../collection/edi3400-lecture-13/edi3400-lecture-13.html" in html
    assert "Python basics problem set" in html
    assert "Python control flow problem set" in html
    assert "Python file handling lab" in html
    assert "Python functions problem set" in html
    assert "Python standard-library utilities problem set" in html
    assert "Python bank-account class lab" in html
    assert "NumPy array and matrix lab" in html
    assert "Pandas dataframe analysis lab" in html
    assert "Matplotlib sales visualization lab" in html
    assert "NumPy, Pandas, and Matplotlib problem set" in html
    assert "Web data extraction lab" in html
    assert "Time-series analysis lab" in html
    assert "Debugging and AI workflow lab" in html
    assert "Assessment Structure" in html
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


def test_edi3400_lecture_06_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-06",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 6 - NumPy arrays and matrices" in html
    assert "This lecture includes" in html
    assert "NumPy arrays and matrices" in html
    assert "NumPy array and matrix lab" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["numpy-arrays-and-matrices", "numpy-array-and-matrix-lab"]


def test_edi3400_lecture_07_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-07",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 7 - Pandas series and data frames" in html
    assert "This lecture includes" in html
    assert "Pandas series and data frames" in html
    assert "Pandas dataframe analysis lab" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["pandas-series-and-dataframes", "pandas-dataframe-analysis-lab"]


def test_edi3400_lecture_08_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-08",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 8 - Matplotlib basic plots" in html
    assert "This lecture includes" in html
    assert "Matplotlib basic plots" in html
    assert "Matplotlib sales visualization lab" in html
    assert "NumPy, Pandas, and Matplotlib problem set" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == [
        "matplotlib-basic-plots",
        "matplotlib-sales-visualization-lab",
        "numpy-pandas-matplotlib-problem-set",
    ]


def test_edi3400_lecture_09_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-09",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 9 - IDEs and generative AI for programming" in html
    assert "This lecture includes" in html
    assert "IDEs, debugging, testing, and AI assistants" in html
    assert "Debugging and AI workflow lab" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == [
        "ide-debugging-testing-and-ai-assistants",
        "debugging-and-ai-workflow-lab",
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


def test_web_data_extraction_with_python_concept_links_edi3400_foundations() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "web-data-extraction-with-python",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## The web is a data source Python can read programmatically" in assembly.markdown
    assert "## URLs behave like file paths for remote data" in assembly.markdown
    assert "## BeautifulSoup turns raw HTML into navigable structure" in assembly.markdown
    assert "## Pandas can read CSV data directly from a URL" in assembly.markdown
    assert "## External data sources are powerful but fragile" in assembly.markdown
    assert "pandas-series-and-dataframes" in related_ids
    assert "matplotlib-basic-plots" in related_ids
    assert "web-data-extraction-lab" in related_ids
    assert "time-series-analysis-with-pandas" in related_ids
    assert "edi3400-lecture-10a" in related_ids
    assert "edi3400" in related_ids


def test_time_series_analysis_with_pandas_concept_links_edi3400_foundations() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "time-series-analysis-with-pandas",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## Time-stamped data needs explicit date handling" in assembly.markdown
    assert "## A DatetimeIndex turns dates into the primary axis" in assembly.markdown
    assert "## Resampling changes the time resolution of a table" in assembly.markdown
    assert "## Time-series plots reveal patterns that summary statistics miss" in assembly.markdown
    assert "## Rolling windows smooth short-term noise" in assembly.markdown
    assert "pandas-series-and-dataframes" in related_ids
    assert "matplotlib-basic-plots" in related_ids
    assert "web-data-extraction-with-python" in related_ids
    assert "time-series-analysis-lab" in related_ids
    assert "edi3400-lecture-10b" in related_ids
    assert "edi3400" in related_ids


def test_web_data_extraction_lab_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "web-data-extraction-lab",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "assets/sample_product_page.html" in assembly.markdown
    assert "assets/quarterly_revenue.csv" in assembly.markdown
    assert "python-file-handling" in related_ids
    assert "pandas-series-and-dataframes" in related_ids
    assert "web-data-extraction-with-python" in related_ids
    assert "edi3400-lecture-10a" in related_ids
    assert "edi3400" in related_ids


def test_time_series_analysis_lab_links_foundations_and_course() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "time-series-analysis-lab",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "exercise"
    assert "## Lab brief" in assembly.markdown
    assert "## Tasks" in assembly.markdown
    assert "## Starter outline" in assembly.markdown
    assert "assets/daily_campus_energy.csv" in assembly.markdown
    assert "pandas-series-and-dataframes" in related_ids
    assert "matplotlib-basic-plots" in related_ids
    assert "time-series-analysis-with-pandas" in related_ids
    assert "edi3400-lecture-10b" in related_ids
    assert "edi3400" in related_ids


def test_edi3400_lecture_10a_assembly_expands_web_data_extraction_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-10a",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["web-data-extraction-with-python", "web-data-extraction-lab"]
    assert "## The web is a data source Python can read programmatically" in assembly.markdown
    assert "## Lab brief" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown


def test_edi3400_lecture_10b_assembly_expands_time_series_analysis_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-10b",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["time-series-analysis-with-pandas", "time-series-analysis-lab"]
    assert "## Time-stamped data needs explicit date handling" in assembly.markdown
    assert "## Lab brief" in assembly.markdown
    assert "## `sqlite3` is the simplest bridge" not in assembly.markdown


def test_edi3400_assignment_collections_are_indexed_with_current_packaging() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)

    assignment_01 = index.objects["edi3400-assignment-01"].model
    assignment_02 = index.objects["edi3400-assignment-02"].model
    assignment_03 = index.objects["edi3400-assignment-03"].model
    assignment_04 = index.objects["edi3400-assignment-04"].model

    assert assignment_01.items == ["python-basics-problem-set"]
    assert assignment_02.items == [
        "python-control-flow-problem-set",
        "python-functions-problem-set",
        "python-standard-library-problem-set",
        "python-bank-account-class-lab",
    ]
    assert assignment_03.items == ["numpy-pandas-matplotlib-problem-set"]
    assert assignment_04.items == ["sql-python-problem-set"]


def test_edi3400_assignment_01_html_assembly_links_course_and_concepts() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-assignment-01",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "collection"
    assert "## Assignment details" in assembly.markdown
    assert "<h2>Included exercises</h2>" in assembly.markdown
    assert "Course context" in assembly.markdown
    assert "edi3400" in related_ids
    assert "python-basics-and-containers" in related_ids


def test_edi3400_assignment_02_html_assembly_links_course_and_concepts() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-assignment-02",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "collection"
    assert "## Assignment details" in assembly.markdown
    assert "<h2>Included exercises</h2>" in assembly.markdown
    assert "Course context" in assembly.markdown
    assert "edi3400" in related_ids
    assert "python-control-flow" in related_ids
    assert "python-functions" in related_ids
    assert "python-classes-and-objects" in related_ids


def test_edi3400_assignment_01_student_sheet_excludes_solution_content() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-assignment-01",
        index=index,
        audience="student",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id
        for edge in assembly.dependency_edges
        if edge.relationship == "assignment-item"
    ]

    assert assembly.target.kind == "collection"
    assert edge_targets == ["python-basics-problem-set"]
    assert "## Exercise 1: Python basics problem set" in assembly.markdown
    assert (
        "The strongest teacher solution keeps the exercise close"
        not in assembly.markdown
    )
    assert all(not item.included_in_output for item in assembly.solution_observations)


def test_edi3400_assignment_02_student_sheet_excludes_solution_content() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-assignment-02",
        index=index,
        audience="student",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id
        for edge in assembly.dependency_edges
        if edge.relationship == "assignment-item"
    ]

    assert assembly.target.kind == "collection"
    assert edge_targets == [
        "python-control-flow-problem-set",
        "python-functions-problem-set",
        "python-standard-library-problem-set",
        "python-bank-account-class-lab",
    ]
    assert "## Exercise 1: Python control flow problem set" in assembly.markdown
    assert "## Exercise 4: Python bank-account class lab" in assembly.markdown
    assert all(not item.included_in_output for item in assembly.solution_observations)


def test_edi3400_assignment_01_student_page_builds_cleanly() -> None:
    build_target(
        "edi3400-assignment-01",
        audience="student",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "edi3400-assignment-01",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Assignment 1 - Python foundations" in html
    assert "Included exercises" in html
    assert "edi3400-assignment-01-exercise-sheet.pdf" in html
    assert "edi3400-assignment-01-solution-sheet.pdf" not in html
    assert build_manifest["target"]["identifier"] == "edi3400-assignment-01"
    assert build_manifest["assignment"]["included_exercise_ids"] == [
        "python-basics-problem-set"
    ]
    assert leakage_report["status"] == "clean"
    assert leakage_report["solution_files_found"] == 1
    assert leakage_report["solution_files_included"] == 0


def test_edi3400_assignment_01_teacher_page_shows_teacher_export_only() -> None:
    build_target(
        "edi3400-assignment-01",
        audience="teacher",
        language="en",
        output_format="exercise-sheet",
        root=REPO_ROOT,
    )
    artifact = build_target(
        "edi3400-assignment-01",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))

    assert "edi3400-assignment-01-solution-sheet.pdf" in html
    assert "edi3400-assignment-01-exercise-sheet.pdf" not in html
    assert build_manifest["assignment"]["included_exercise_ids"] == [
        "python-basics-problem-set"
    ]


def test_edi3400_lecture_10a_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-10a",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 10A - Web data extraction" in html
    assert "This lecture includes" in html
    assert "Web data extraction with Python" in html
    assert "Web data extraction lab" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["web-data-extraction-with-python", "web-data-extraction-lab"]


def test_edi3400_lecture_10b_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-10b",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 10B - Time-series analysis and statistics" in html
    assert "This lecture includes" in html
    assert "Time-series analysis with Pandas" in html
    assert "Time-series analysis lab" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["time-series-analysis-with-pandas", "time-series-analysis-lab"]


def test_course_orientation_and_python_ecosystem_concept_links_edi3400() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "course-orientation-and-python-ecosystem",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    related_ids = [entry.identifier for entry in assembly.related_entries]

    assert assembly.target.kind == "concept"
    assert "## This course teaches data management through Python" in assembly.markdown
    assert "## Python is a general-purpose language with a data-friendly ecosystem" in assembly.markdown
    assert "## The standard library covers common tasks out of the box" in assembly.markdown
    assert "## Third-party libraries extend Python into specialized workflows" in assembly.markdown
    assert "## The course workflow combines writing, running, and inspecting" in assembly.markdown
    assert "## What students should be able to do next" in assembly.markdown
    assert "python-basics-and-containers" in related_ids
    assert "edi3400-lecture-01" in related_ids
    assert "edi3400" in related_ids


def test_edi3400_lecture_01_assembly_expands_orientation_block() -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    assembly = assemble_target(
        "edi3400-lecture-01",
        index=index,
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    edge_targets = [
        edge.target_id for edge in assembly.dependency_edges if edge.relationship == "item"
    ]

    assert edge_targets == ["course-orientation-and-python-ecosystem"]
    assert "## This course teaches data management through Python" in assembly.markdown
    assert "## Names let Python reuse values" not in assembly.markdown


def test_course_orientation_and_python_ecosystem_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "course-orientation-and-python-ecosystem",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    build_manifest = json.loads(artifact.build_manifest_path.read_text(encoding="utf-8"))
    leakage_report = json.loads(artifact.leakage_report_path.read_text(encoding="utf-8"))

    assert "Course orientation and the Python ecosystem" in html
    assert "Python is a general-purpose language" in html
    assert "write-run-inspect cycle" in html
    assert "../../course/edi3400/edi3400.html" in html
    assert "first session sets expectations" not in html
    assert artifact.output_path.exists()
    assert build_manifest["target"]["identifier"] == "course-orientation-and-python-ecosystem"
    assert leakage_report["status"] == "clean"
    assert leakage_report["teacher_blocks_removed"] == 1


def test_edi3400_lecture_01_student_page_builds_cleanly() -> None:
    artifact = build_target(
        "edi3400-lecture-01",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    html = artifact.output_path.read_text(encoding="utf-8")
    dependency_manifest = json.loads(
        artifact.dependency_manifest_path.read_text(encoding="utf-8")
    )

    assert "Lecture 1 - Course orientation and the Python ecosystem" in html
    assert "This lecture includes" in html
    assert "Course orientation and the Python ecosystem" in html
    assert "sqlite3 is the simplest bridge" not in html
    assert [
        edge["target_id"]
        for edge in dependency_manifest["dependency_edges"]
        if edge["relationship"] == "item"
    ] == ["course-orientation-and-python-ecosystem"]

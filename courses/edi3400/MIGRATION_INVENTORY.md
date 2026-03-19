# EDI3400 Migration Inventory

This file tracks the migration of legacy material from
`course-inbox/Programming-and-data-management/` into LearnForge's canonical
course/object structure.

## Locked Decisions

- Canonical course id: `edi3400`
- Course language at migration start: `en` only
- The current README, lecture notebooks, and homework notebooks are reference
  material, not source of truth
- The course outline is still a sketch, so `courses/edi3400/plan.yml` stays empty
  until the first canonical lecture collection exists
- The first canonical slice starts with the database block:
  - Lecture 11: relational databases
  - Lecture 12: SQL basics
  - Lecture 13: Python and SQL
  - Homework problem set 5
- New teaching material should prefer:
  - exposition in `.qmd`
  - reusable code in plain `.py`
  - exercises in LearnForge `exercise` objects
  - teacher guidance in `solution.en.qmd`
- No bulk import of notebook outputs, helper scripts, CSV files, or `.db` files;
  promote only the specific assets that a canonical object actually needs
- No promotion of the nested legacy git repository, editor files, or build/tooling
  noise from the inbox
- Do not add `edi3400` representative targets until at least one lecture collection
  is stable enough to act as a regression target

## Migration Buckets

### Promote First

These items are the strongest self-contained slice in the current inbox material and
can be converted into reusable concepts, exercises, and lecture collections with
moderate rewriting.

| Legacy source | Action | Target kind | Proposed target id |
| --- | --- | --- | --- |
| `Lecture_notebooks/11_Introduction_to_relational_databases.ipynb` | Rewrite into reusable exposition on tables, keys, and relations | concept | `relational-database-fundamentals` |
| `Lecture_notebooks/12_SQL_Basics.ipynb` | Rewrite around the core SQL query workflow | concept | `sql-query-basics` |
| `Lecture_notebooks/13_SQL_with_Python.ipynb` | Rewrite around database access from Python | concept | `python-sql-integration` |
| `Homework_notebooks/Problem_set5_solution.ipynb` | Convert to student coding exercise + teacher solution | exercise | `sql-python-problem-set` |
| `Lecture_notebooks/example_database.db`, `Lecture_notebooks/auto_dealership_database.db`, `Lecture_notebooks/example_queries.sql`, `Lecture_notebooks/isqlite3.py` | Keep only if promoted objects need them as local assets | object-local assets | under promoted database concepts/exercise |

### Rewrite Fresh

These topics exist in the sketch but should be re-authored rather than promoted
directly from a single notebook.

| Topic | Reason | Planned target kind |
| --- | --- | --- |
| Lecture 1 course framing | The current material is mostly orientation and should live primarily in the syllabus and course shell | syllabus + lecture later |
| Lecture 9 IDEs and generative AI | Two overlapping notebook variants suggest the framing is still in flux | concept + exercise later |
| Lecture 10 data extraction, probability, and statistics | The current scope mixes multiple themes that should likely be split more cleanly | concept + exercise later |
| Assessment structure | The sketch does not yet define canonical assignment or grading rules | assignment / course material |

### Defer

These should stay in the inbox until the database slice establishes the promotion
pattern for the course.

| Legacy source | Reason for deferral |
| --- | --- |
| `Lecture_notebooks/02_Variables_expressions_and_statements.ipynb` | Strong candidate later, but the basic-Python block still needs a decision on concept granularity versus exercise-first migration |
| `Lecture_notebooks/03_Built_in_functions_and_containers.ipynb` | Same reason; likely part of a larger foundational Python slice |
| `Lecture_notebooks/04a_Conditional_execution_and_loops.ipynb` | Better promoted together with related coding exercises |
| `Lecture_notebooks/04b_Opening_and_writing_to_files.ipynb` | Useful later, but not part of the first database-focused checkpoint |
| `Lecture_notebooks/05_The_standard_Library_functions_and_classes.ipynb` | Broad notebook that will likely need splitting during promotion |
| `Lecture_notebooks/06_Linear_algebra_with_Numpy.ipynb` | Good later third-party-library content, but not needed for the first canonical slice |
| `Lecture_notebooks/07_Data_analysis_with_Pandas.ipynb` | Depends on how the data-analysis block is ultimately scoped |
| `Lecture_notebooks/08_Data_vizualization_with_Matplotlib.ipynb` | Better promoted after the Pandas block exists |
| `Homework_notebooks/Problem_set2_solution.ipynb` | Keep as reference until the early Python block is promoted |
| `Homework_notebooks/Problem_set3_solution.ipynb` | Keep as reference until the control-flow/files/functions block is promoted |
| `Homework_notebooks/Problem_set4_solution.ipynb` | Keep as reference until the NumPy/Pandas/Matplotlib block is promoted |

### Drop Or Archive

| Legacy source | Reason |
| --- | --- |
| `.git/` inside `course-inbox/Programming-and-data-management/` | Nested repo metadata, not course source |
| `.vscode/` | Editor noise |
| Notebook checkpoints, generated outputs, and scratch files | Tooling artifacts, not canonical teaching content |
| Duplicate helper files kept only for notebook convenience | Keep only one canonical copy when an object explicitly needs it |

## Proposed First Canonical Slice

Build the first LearnForge checkpoint for `edi3400` around the database block.

### First concept candidates

- `relational-database-fundamentals`
- `sql-query-basics`
- `python-sql-integration`

### First exercise candidates

- `sql-python-problem-set`

### First lecture candidates

- `edi3400-lecture-11` relational databases
- `edi3400-lecture-12` SQL basics
- `edi3400-lecture-13` Python and SQL

## Current Canonical Checkpoint

The first database concept block is now scaffolded in canonical LearnForge form.

### Implemented objects

- concept: `relational-database-fundamentals`
- concept: `sql-query-basics`
- concept: `python-sql-integration`
- exercise: `sql-python-problem-set`

## Next Migration Actions

1. Keep the canonical course shell in place, but leave `courses/edi3400/plan.yml`
   empty until the first lecture collection is assembled from promoted objects only.
2. Assemble `edi3400-lecture-11` from promoted objects only.
3. Decide whether `edi3400-lecture-12` should include only `sql-query-basics` or also
   the exercise as a capstone task.
4. Decide which `.db`, `.sql`, and helper `.py` files genuinely belong as canonical
   object-local assets.
4. Convert `Problem_set5_solution.ipynb` into `sql-python-problem-set` with a
   student-facing note and a separate `solution.en.qmd`.
5. Assemble `edi3400-lecture-11`, `edi3400-lecture-12`, and `edi3400-lecture-13`
   only after their referenced concepts/exercises exist canonically.
6. Leave the rest of the Python and third-party-library material in the inbox until
   that database promotion pattern is stable.

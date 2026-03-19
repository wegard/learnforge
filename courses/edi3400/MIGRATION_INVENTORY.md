# EDI3400 Migration Inventory

This file tracks the migration of legacy material from
`course-inbox/Programming-and-data-management/` into LearnForge's canonical
course/object structure.

## Locked Decisions

- Canonical course id: `edi3400`
- Course language at migration start: `en` only
- The current README, lecture notebooks, and homework notebooks are reference
  material, not source of truth
- The course outline is still a sketch, so `courses/edi3400/plan.yml` grows
  incrementally as stable lecture collections are assembled
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
- For the first canonical database slice, keep only
  `auto_dealership_database.db` as a canonical object-local asset
- Leave `example_database.db`, `example_queries.sql`, and `isqlite3.py` in the
  inbox unless a later canonical object explicitly needs them
- Keep Homework problem set 5 as a lecture-linked LearnForge `exercise` for now,
  not a formal assignment collection
- `edi3400-lecture-13` is the representative regression target for the current
  database slice

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

The first database lecture slice is now scaffolded in canonical LearnForge form.

### Implemented objects

- concept: `relational-database-fundamentals`
- concept: `sql-query-basics`
- concept: `python-sql-integration`
- exercise: `sql-python-problem-set`
- lecture collection: `edi3400-lecture-11`
- lecture collection: `edi3400-lecture-12`
- lecture collection: `edi3400-lecture-13`

### Course plan status

- `courses/edi3400/plan.yml` now includes `edi3400-lecture-11`
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-12`
- `edi3400-lecture-12` is scoped to canonical SQL querying material only
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-13`
- `edi3400-lecture-13` combines canonical Python/SQL integration material with the
  promoted problem set as applied follow-up
- The first canonical database lecture block for `edi3400` now spans lectures 11-13
- The retained canonical database asset for this slice is:
  - `content/exercises/sql-python-problem-set/assets/auto_dealership_database.db`
- `edi3400-lecture-13` is now stable enough to remain in
  `representative-targets.yml` as the regression target for the slice
- Homework problem set 5 remains modeled as `sql-python-problem-set`, a lecture-linked
  exercise rather than a formal assignment collection

## Next Migration Actions

1. Decide whether the next canonical slice after the database block should start with
   the early Python foundations or the later data-analysis block.
2. Decide the object granularity for the early Python lectures before promoting
   `Lecture_notebooks/02_...` through `05_...`.
3. Reframe Lecture 9 IDE / generative-AI material only after the foundational Python
   workflow is stable enough to support a clean concept-plus-exercise slice.
4. Keep assessment structure and formal assignments draft-level until more of the
   course scope is canonical.

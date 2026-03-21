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
- For the first early-Python checkpoint, combine lecture 2 and lecture 3 material
  into one canonical foundations slice before deciding whether to split those topics
  more finely later
- Keep `Lecture_notebooks/04b_Opening_and_writing_to_files.ipynb` as its own
  canonical `edi3400-lecture-04b` slice rather than folding it into the broader
  lecture-5 material
- Split `Lecture_notebooks/05_The_standard_Library_functions_and_classes.ipynb`
  by promoting functions first as `edi3400-lecture-05a`, then a small
  standard-library utilities slice as `edi3400-lecture-05b`, then a small
  classes/OOP slice as `edi3400-lecture-05c`
- For the first canonical database slice, keep only
  `auto_dealership_database.db` as a canonical object-local asset
- Leave `example_database.db`, `example_queries.sql`, and `isqlite3.py` in the
  inbox unless a later canonical object explicitly needs them
- Split lecture 10 into two slices: web data extraction (10a) and time-series
  analysis (10b), each with a concept and a lab exercise
- Group existing exercises into 4 assignment collections:
  - Assignment 1: Python foundations (`python-basics-problem-set`)
  - Assignment 2: Control flow, functions, and classes (4 exercises)
  - Assignment 3: Data analysis libraries (`numpy-pandas-matplotlib-problem-set`)
  - Assignment 4: SQL and databases (`sql-python-problem-set`)
- `edi3400-lecture-13` is the representative regression target for the current
  database slice
- Lecture 1 gets a lightweight concept-only collection (`course-orientation-and-
  python-ecosystem`) covering course scope, Python ecosystem overview, and the
  write-run-inspect workflow — no exercise, no installation guides, no Jupyter
  cell-mode details
- Lecture 14 (wrap-up / Q&A) is skipped entirely — it is a live session with no
  canonical teaching content to promote

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
| `Lecture_notebooks/02_Variables_expressions_and_statements.ipynb`, `Lecture_notebooks/03_Built_in_functions_and_containers.ipynb`, and `Homework_notebooks/Problem_set2_solution.ipynb` | Rewrite into the first canonical Python foundations checkpoint on values, built-in functions, and containers | concept + exercise + lecture collection | `python-basics-and-containers`, `python-basics-problem-set`, `edi3400-lecture-02` |
| `Lecture_notebooks/04a_Conditional_execution_and_loops.ipynb` and Topic 1 from `Homework_notebooks/Problem_set3_solution.ipynb` | Rewrite into a control-flow checkpoint on conditionals, loops, and basic exception handling | concept + exercise + lecture collection | `python-control-flow`, `python-control-flow-problem-set`, `edi3400-lecture-04` |
| `Lecture_notebooks/04b_Opening_and_writing_to_files.ipynb` | Rewrite into a file-handling checkpoint on paths, `with open(...)`, writing text files, and reading small CSV data | concept + exercise + lecture collection | `python-file-handling`, `python-file-handling-lab`, `edi3400-lecture-04b` |
| Functions section of `Lecture_notebooks/05_The_standard_Library_functions_and_classes.ipynb` and Topic 4 from `Homework_notebooks/Problem_set3_solution.ipynb` | Rewrite into the first lecture-5 checkpoint on defining and reusing functions | concept + exercise + lecture collection | `python-functions`, `python-functions-problem-set`, `edi3400-lecture-05a` |
| Standard-library section of `Lecture_notebooks/05_The_standard_Library_functions_and_classes.ipynb` and Topic 3 from `Homework_notebooks/Problem_set3_solution.ipynb` | Rewrite into a focused utilities checkpoint on imports and common modules such as `math`, `random`, `datetime`, and `statistics` | concept + exercise + lecture collection | `python-standard-library-utilities`, `python-standard-library-problem-set`, `edi3400-lecture-05b` |
| Classes/OOP section of `Lecture_notebooks/05_The_standard_Library_functions_and_classes.ipynb` and Topic 5 from `Homework_notebooks/Problem_set3_solution.ipynb` | Rewrite into a small classes checkpoint on `__init__`, attributes, methods, and object state using a `BankAccount` example | concept + exercise + lecture collection | `python-classes-and-objects`, `python-bank-account-class-lab`, `edi3400-lecture-05c` |
| `Lecture_notebooks/06_Linear_algebra_with_Numpy.ipynb` | Rewrite into the first NumPy checkpoint on arrays, shape, vectorized operations, summaries, and small matrix multiplication | concept + exercise + lecture collection | `numpy-arrays-and-matrices`, `numpy-array-and-matrix-lab`, `edi3400-lecture-06` |
| `Lecture_notebooks/07_Data_analysis_with_Pandas.ipynb` | Rewrite into the first Pandas checkpoint on Series, DataFrames, selection, filtering, sorting, and CSV/date workflows | concept + exercise + lecture collection | `pandas-series-and-dataframes`, `pandas-dataframe-analysis-lab`, `edi3400-lecture-07` |
| `Lecture_notebooks/08_Data_vizualization_with_Matplotlib.ipynb` | Rewrite into the first plotting checkpoint on line, scatter, and bar plots, labeling, saving figures, and basic Pandas integration | concept + exercise + lecture collection | `matplotlib-basic-plots`, `matplotlib-sales-visualization-lab`, `edi3400-lecture-08` |
| `Homework_notebooks/Problem_set4_solution.ipynb` | Rewrite into the first integrated data-analysis problem set across NumPy arrays, Pandas summaries, and Matplotlib reporting | exercise | `numpy-pandas-matplotlib-problem-set` |
| `Homework_notebooks/Problem_set5_solution.ipynb` | Convert to student coding exercise + teacher solution | exercise | `sql-python-problem-set` |
| `Lecture_notebooks/example_database.db`, `Lecture_notebooks/auto_dealership_database.db`, `Lecture_notebooks/example_queries.sql`, `Lecture_notebooks/isqlite3.py` | Keep only if promoted objects need them as local assets | object-local assets | under promoted database concepts/exercise |

### Rewrite Fresh

These topics exist in the sketch but should be re-authored rather than promoted
directly from a single notebook.

| Topic | Reason | Planned target kind |
| --- | --- | --- |
| ~~Lecture 1 course framing~~ | ~~Implemented as concept-only lecture-01 with course orientation and Python ecosystem overview~~ | ~~done~~ |
| ~~Lecture 10 data extraction, probability, and statistics~~ | ~~Implemented as 10a (web data extraction) and 10b (time-series analysis)~~ | ~~done~~ |
| ~~Assessment structure~~ | ~~Implemented as 4 assignment collections grouping existing exercises~~ | ~~done~~ |
| ~~Lecture 14 wrap-up / Q&A~~ | ~~Skipped — live session only, no canonical content to promote~~ | ~~skipped~~ |

### Defer

No additional inbox items are deferred right now beyond the later rewrite-fresh
topics. The earlier `Problem_set4_solution.ipynb` defer is now resolved.

### Drop Or Archive

| Legacy source | Reason |
| --- | --- |
| `.git/` inside `course-inbox/Programming-and-data-management/` | Nested repo metadata, not course source |
| `.vscode/` | Editor noise |
| Notebook checkpoints, generated outputs, and scratch files | Tooling artifacts, not canonical teaching content |
| Duplicate helper files kept only for notebook convenience | Keep only one canonical copy when an object explicitly needs it |

## Proposed First Canonical Slice

Build the current LearnForge checkpoint for `edi3400` around a growing early-Python
foundations spine plus the database block.

### First concept candidates

- `course-orientation-and-python-ecosystem`
- `python-basics-and-containers`
- `python-control-flow`
- `python-file-handling`
- `python-functions`
- `python-standard-library-utilities`
- `python-classes-and-objects`
- `numpy-arrays-and-matrices`
- `pandas-series-and-dataframes`
- `matplotlib-basic-plots`
- `ide-debugging-testing-and-ai-assistants`
- `web-data-extraction-with-python`
- `time-series-analysis-with-pandas`
- `relational-database-fundamentals`
- `sql-query-basics`
- `python-sql-integration`

### First exercise candidates

- `python-basics-problem-set`
- `python-control-flow-problem-set`
- `python-file-handling-lab`
- `python-functions-problem-set`
- `python-standard-library-problem-set`
- `python-bank-account-class-lab`
- `numpy-array-and-matrix-lab`
- `pandas-dataframe-analysis-lab`
- `matplotlib-sales-visualization-lab`
- `numpy-pandas-matplotlib-problem-set`
- `debugging-and-ai-workflow-lab`
- `web-data-extraction-lab`
- `time-series-analysis-lab`
- `sql-python-problem-set`

### First lecture candidates

- `edi3400-lecture-01` course orientation and Python ecosystem
- `edi3400-lecture-02` Python basics and containers
- `edi3400-lecture-04` control flow and loops
- `edi3400-lecture-04b` file handling and local data
- `edi3400-lecture-05a` functions and reusable code
- `edi3400-lecture-05b` standard-library utilities
- `edi3400-lecture-05c` classes and objects
- `edi3400-lecture-06` NumPy arrays and matrices
- `edi3400-lecture-07` Pandas series and data frames
- `edi3400-lecture-08` Matplotlib basic plots
- `edi3400-lecture-09` IDEs and generative AI for programming
- `edi3400-lecture-10a` web data extraction
- `edi3400-lecture-10b` time-series analysis and statistics
- `edi3400-lecture-11` relational databases
- `edi3400-lecture-12` SQL basics
- `edi3400-lecture-13` Python and SQL

## Current Canonical Checkpoint

The first early-Python foundations spine, first data-analysis and visualization
slices, and first database lecture slice are now scaffolded in canonical LearnForge
form.

### Implemented objects

- concept: `course-orientation-and-python-ecosystem`
- concept: `python-basics-and-containers`
- concept: `python-control-flow`
- concept: `python-file-handling`
- concept: `python-functions`
- concept: `python-standard-library-utilities`
- concept: `python-classes-and-objects`
- concept: `numpy-arrays-and-matrices`
- concept: `pandas-series-and-dataframes`
- concept: `matplotlib-basic-plots`
- concept: `ide-debugging-testing-and-ai-assistants`
- concept: `relational-database-fundamentals`
- concept: `sql-query-basics`
- concept: `web-data-extraction-with-python`
- concept: `time-series-analysis-with-pandas`
- concept: `python-sql-integration`
- exercise: `python-basics-problem-set`
- exercise: `python-control-flow-problem-set`
- exercise: `python-file-handling-lab`
- exercise: `python-functions-problem-set`
- exercise: `python-standard-library-problem-set`
- exercise: `python-bank-account-class-lab`
- exercise: `numpy-array-and-matrix-lab`
- exercise: `pandas-dataframe-analysis-lab`
- exercise: `matplotlib-sales-visualization-lab`
- exercise: `numpy-pandas-matplotlib-problem-set`
- exercise: `debugging-and-ai-workflow-lab`
- exercise: `web-data-extraction-lab`
- exercise: `time-series-analysis-lab`
- exercise: `sql-python-problem-set`
- lecture collection: `edi3400-lecture-01`
- lecture collection: `edi3400-lecture-02`
- lecture collection: `edi3400-lecture-04`
- lecture collection: `edi3400-lecture-04b`
- lecture collection: `edi3400-lecture-05a`
- lecture collection: `edi3400-lecture-05b`
- lecture collection: `edi3400-lecture-05c`
- lecture collection: `edi3400-lecture-06`
- lecture collection: `edi3400-lecture-07`
- lecture collection: `edi3400-lecture-08`
- lecture collection: `edi3400-lecture-09`
- lecture collection: `edi3400-lecture-11`
- lecture collection: `edi3400-lecture-12`
- lecture collection: `edi3400-lecture-10a`
- lecture collection: `edi3400-lecture-10b`
- lecture collection: `edi3400-lecture-13`
- assignment collection: `edi3400-assignment-01`
- assignment collection: `edi3400-assignment-02`
- assignment collection: `edi3400-assignment-03`
- assignment collection: `edi3400-assignment-04`

### Course plan status

- `courses/edi3400/plan.yml` now includes `edi3400-lecture-02`
- `edi3400-lecture-02` combines variables, built-in functions, and core container
  workflows into the first canonical Python foundations checkpoint
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-04`
- `edi3400-lecture-04` adds conditionals, loops, and introductory exception handling
  as the next canonical Python foundations checkpoint
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-04b`
- `edi3400-lecture-04b` adds file paths, safe read/write patterns, and a small CSV
  workflow as a distinct file-handling checkpoint
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-05a`
- `edi3400-lecture-05a` promotes the functions part of lecture 5 without claiming
  the remaining standard-library or classes material is canonical yet
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-05b`
- `edi3400-lecture-05b` promotes the standard-library utilities part of lecture 5
  as a focused imports-and-modules checkpoint while leaving classes/OOP separate
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-05c`
- `edi3400-lecture-05c` completes the lecture-5 split with a small classes-and-
  objects checkpoint centered on `__init__`, attributes, methods, and object state
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-06`
- `edi3400-lecture-06` promotes the first NumPy slice around arrays, shapes,
  vectorized arithmetic, and a small matrix workflow
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-07`
- `edi3400-lecture-07` promotes the first Pandas slice around Series, DataFrames,
  labeled selection, filtering, sorting, and CSV/date workflows
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-08`
- `edi3400-lecture-08` promotes the first visualization slice around line,
  scatter, and bar plots, explicit labels, saving figures, and basic Pandas
  integration
- Homework problem set 4 is now modeled as
  `numpy-pandas-matplotlib-problem-set`, a lecture-linked exercise that turns the
  lecture 6-8 stack into one explicit workflow from arrays to table summaries to
  plotted output
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-09`
- `edi3400-lecture-09` reframes the overlapping legacy lecture-9 notebooks into one
  canonical workflow-support slice on IDE use, debugging, unit tests, documentation,
  and bounded AI assistance for programming
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
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-10a`
- `edi3400-lecture-10a` promotes the web data extraction slice with a concept on
  `urlopen`, BeautifulSoup, and `pd.read_csv(url)` patterns, plus a lab exercise
  using local HTML and CSV assets
- `courses/edi3400/plan.yml` now includes `edi3400-lecture-10b`
- `edi3400-lecture-10b` promotes the time-series analysis slice with a concept on
  `DatetimeIndex`, resampling, rolling windows, and time-series plotting, plus a
  lab exercise using a synthetic daily campus energy CSV
- Existing exercises are now grouped into 4 assignment collections:
  - `edi3400-assignment-01`: Python foundations (1 exercise)
  - `edi3400-assignment-02`: Control flow, functions, and classes (4 exercises)
  - `edi3400-assignment-03`: Data analysis libraries (1 exercise)
  - `edi3400-assignment-04`: SQL and databases (1 exercise)

- `courses/edi3400/plan.yml` now includes `edi3400-lecture-01`
- `edi3400-lecture-01` is a concept-only orientation collection covering course
  scope, the Python ecosystem, and the write-run-inspect workflow
- Course status upgraded from `draft` to `approved` — all planned lectures
  (1-13) are now canonical, lecture 14 (Q&A) is skipped by design

## Migration Complete

The `edi3400` migration is finalized. All 16 concepts, 14 exercises, 16 lecture
collections, and 4 assignment collections are implemented, tested, and wired into
the course plan. The course status is `approved`.

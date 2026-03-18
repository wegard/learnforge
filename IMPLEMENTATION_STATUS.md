# Implementation Status

## Current Milestone

- Phase 3 assembly + metadata listings checkpoint complete:
  - formalized collection and course assembly as first-class compilation inputs
  - generated metadata-driven student listings
  - added related-content blocks
  - emitted build/dependency/leakage manifests
  - verified with tests and representative renders

## Non-Goals For This Run

- No exercise-sheet compiler work
- No teacher solution-sheet implementation
- No approval workflows
- No stale-content commands
- No `teach reindex` unless strictly required by this slice
- No Textual TUI
- No AI draft workflows
- No migration tooling
- No CI/CD or deployment pipeline work

## Decisions Locked

- `ROADMAP.md` is the source of truth
- Python is the control-plane language
- CLI uses `Typer`
- Data models and validation use `Pydantic`
- Norwegian language code is locked to `nb`
- No database in v1
- Thin CLI only in this milestone; no Textual TUI
- Quarto is the build engine for site, slides, and PDF paths
- Source of truth remains plain-text files under git
- One canonical object ID is shared across languages
- Language file convention is `note.en.qmd` + `note.nb.qmd` + shared `meta.yml`
- Teacher/student visibility separation is enforced from the start
- PDF builds are pinned to `pdflatex` for deterministic local export in this bootstrap slice
- Quarto cache is pinned into `build/.cache/` to avoid sandboxed home-directory writes
- Assembly is now centralized in `app/assembly.py`
- Listing target ids are reserved as `topic-<topic-slug>` and `resources-<course-id>`
- Quarto website support files are staged in local `site_libs/` and ignored from git

## Completed Tasks

- Added root project files: `pyproject.toml`, `.gitignore`, `.editorconfig`, `.pre-commit-config.yaml`, `Makefile`, `README.md`
- Added Quarto project config and profiles: `_quarto.yml`, `_quarto-student.yml`, `_quarto-teacher.yml`, `_quarto-en.yml`, `_quarto-nb.yml`, `_variables.yml`
- Added Python control-plane package under `app/` with:
  - thin `teach` CLI
  - repository indexing
  - schema-backed validation
  - search indexing
  - deterministic build materialization
  - scaffolding for `teach new`
  - JSON schema export
- Exported and committed JSON schemas for:
  - base object
  - concept
  - exercise
  - figure
  - resource
  - collection
- Added five hand-made sample objects:
  - `iv-intuition`
  - `ex-iv-concept-check`
  - `iv-dag-figure`
  - `angrist-podcast-iv`
  - `lecture-04`
- Added one sample course:
  - `ec202`
- Added teacher-only content blocks and enforced student stripping during build materialization
- Added Lua visibility filter for Quarto profile-aware conditional content
- Added templates and shell helpers under `templates/` and `scripts/`
- Added tests for:
  - repository validation
  - schema failure behavior
  - scaffolding
  - CLI validate/search
  - representative render path with teacher/student separation
- Generated and verified bootstrap outputs:
  - concept HTML in `en`
  - concept HTML in `nb`
  - lecture Reveal.js in `nb`
  - lecture PDF in `nb`
  - course landing page HTML in `nb`
- Refactored the build flow into a first-class assembly pipeline in `app/assembly.py`
- Added typed assembly for:
  - object pages
  - lecture collections
  - course pages
  - topic listing pages
  - resource listing pages
- Made dependency relationships explicit through:
  - file dependency tracking with SHA-256 fingerprints
  - target-to-target dependency edges
  - build-specific dependency manifests
- Extended course generation so course pages are compiled from `course.yml` + `plan.yml` + metadata-derived lecture/topic/resource sections
- Added metadata-driven listing generation for:
  - `topic-causal-inference`
  - `resources-ec202`
- Added related-content blocks for:
  - concept pages
  - resource pages
- Added build reporting for every build target:
  - `build-manifest.json`
  - `dependency-manifest.json`
  - `teacher-leakage-report.json`
- Hardened student leakage reporting so student builds record:
  - teacher-only blocks found in source
  - teacher-only blocks removed during assembly
  - whether teacher markers remain in generated source or rendered output
- Added new tests for:
  - collection expansion
  - dependency propagation when source notes change
  - listing generation
  - related-content generation
  - manifest/report generation
  - leakage reporting
  - snapshot-style listing output verification

## Remaining Tasks

- Later roadmap work only:
  - broaden collection support beyond lectures
  - add more student-facing pages, navigation, breadcrumbs, and listing coverage
  - extend related-content logic across more object types
  - deepen validation into site-wide manifest/link checks
  - implement Phase 6 exercise compiler and solution separation
  - add later CLI/reporting commands that were explicitly out of scope for this run

## Blockers

- None at checkpoint
- A Quarto `site_libs` staging issue appeared under parallel HTML renders and was resolved by precreating the local staging directory in the build environment

## Files Changed

- `README.md`
- `pyproject.toml`
- `.gitignore`
- `.editorconfig`
- `.pre-commit-config.yaml`
- `Makefile`
- `_quarto.yml`
- `_quarto-student.yml`
- `_quarto-teacher.yml`
- `_quarto-en.yml`
- `_quarto-nb.yml`
- `_variables.yml`
- `IMPLEMENTATION_STATUS.md`
- `app/`
- `app/assembly.py`
- `app/build.py`
- `app/config.py`
- `app/indexer.py`
- `app/validator.py`
- `app/cli.py`
- `schemas/`
- `content/`
- `collections/`
- `courses/`
- `filters/`
- `formats/`
- `templates/`
- `scripts/`
- `tests/`
- `tests/snapshots/`
- `build/.gitkeep` placeholders and generated checkpoint artifacts under ignored build paths

## Commands Run

- `pwd`
- `rg --files`
- `sed -n '1,240p' ROADMAP.md`
- `sed -n '241,520p' ROADMAP.md`
- `sed -n '521,860p' ROADMAP.md`
- `sed -n '861,1200p' ROADMAP.md`
- `python3 --version`
- `quarto --version`
- `pdflatex --version`
- `tectonic --version`
- `UV_CACHE_DIR=/tmp/uv-cache uv venv .venv`
- `UV_CACHE_DIR=/tmp/uv-cache uv pip install --python .venv/bin/python -e '.[dev]'`
- `.venv/bin/python -m app.schema_export`
- `.venv/bin/ruff check app tests`
- `.venv/bin/ruff format app tests`
- `.venv/bin/pytest`
- `.venv/bin/teach validate`
- `.venv/bin/teach search "instrumental variables"`
- `.venv/bin/teach build iv-intuition --audience student --lang en --format html`
- `.venv/bin/teach build iv-intuition --audience student --lang nb --format html`
- `.venv/bin/teach build iv-intuition --audience teacher --lang en --format html`
- `.venv/bin/teach build lecture-04 --audience teacher --lang nb --format revealjs`
- `.venv/bin/teach build lecture-04 --audience teacher --lang nb --format pdf`
- `.venv/bin/teach build ec202 --audience student --lang nb --format html`
- `rg -n "Prompt the room" build/exports/student/en/html/concept/iv-intuition/iv-intuition.html build/exports/teacher/en/html/concept/iv-intuition/iv-intuition.html`
- `sed -n '1,260p' app/build.py`
- `sed -n '1,260p' app/indexer.py`
- `sed -n '1,260p' app/validator.py`
- `sed -n '1,260p' app/models.py`
- `sed -n '1,260p' app/cli.py`
- `.venv/bin/teach build ec202 --audience student --lang en --format html`
- `.venv/bin/teach build topic-causal-inference --audience student --lang en --format html`
- `.venv/bin/teach build resources-ec202 --audience student --lang en --format html`
- `.venv/bin/teach build iv-intuition --audience student --lang en --format html`
- `.venv/bin/teach build angrist-podcast-iv --audience student --lang en --format html`
- `.venv/bin/teach build lecture-04 --audience teacher --lang nb --format revealjs`
- `.venv/bin/teach build lecture-04 --audience teacher --lang nb --format pdf`
- `mkdir -p site_libs/quarto-search`
- `rg -n "Related content|Lecture 4|IV DAG|Instrumental Variables Episode" build/exports/student/en/html/concept/iv-intuition/iv-intuition.html`
- `rg -n "Topics|Resources|All course resources|Full resource listing|topic-causal-inference|resources-ec202" build/exports/student/en/html/course/ec202/ec202.html`
- `rg -n "Topic:|Resources for|Instrumental Variables Episode|IV intuition" build/exports/student/en/html/listing/topic-causal-inference/topic-causal-inference.html build/exports/student/en/html/listing/resources-ec202/resources-ec202.html build/exports/student/en/html/resource/angrist-podcast-iv/angrist-podcast-iv.html`
- `ls build/reports/builds/student/en/html/concept/iv-intuition build/reports/builds/student/en/html/course/ec202 build/reports/builds/student/en/html/listing/topic-causal-inference build/reports/builds/student/en/html/listing/resources-ec202`

## Test / Build Results

- Validation passed:
  - `Validated 5 objects and 1 courses. Issues: 0.`
- Lint passed:
  - `ruff check app tests`
- Tests passed:
  - `12 passed in 4.87s`
- Phase 3 / Phase 5 representative renders passed:
  - Student course page with generated listings:
    - `build/exports/student/en/html/course/ec202/ec202.html`
    - `build/reports/builds/student/en/html/course/ec202/build-manifest.json`
    - `build/reports/builds/student/en/html/course/ec202/dependency-manifest.json`
    - `build/reports/builds/student/en/html/course/ec202/teacher-leakage-report.json`
  - Student topic listing page:
    - `build/exports/student/en/html/listing/topic-causal-inference/topic-causal-inference.html`
    - `build/reports/builds/student/en/html/listing/topic-causal-inference/build-manifest.json`
    - `build/reports/builds/student/en/html/listing/topic-causal-inference/dependency-manifest.json`
    - `build/reports/builds/student/en/html/listing/topic-causal-inference/teacher-leakage-report.json`
  - Student resource listing page:
    - `build/exports/student/en/html/listing/resources-ec202/resources-ec202.html`
    - `build/reports/builds/student/en/html/listing/resources-ec202/build-manifest.json`
    - `build/reports/builds/student/en/html/listing/resources-ec202/dependency-manifest.json`
    - `build/reports/builds/student/en/html/listing/resources-ec202/teacher-leakage-report.json`
  - Concept page with related content and leakage report:
    - `build/exports/student/en/html/concept/iv-intuition/iv-intuition.html`
    - `build/reports/builds/student/en/html/concept/iv-intuition/build-manifest.json`
    - `build/reports/builds/student/en/html/concept/iv-intuition/dependency-manifest.json`
    - `build/reports/builds/student/en/html/concept/iv-intuition/teacher-leakage-report.json`
  - Teacher lecture collection build:
    - `build/exports/teacher/nb/revealjs/collection/lecture-04/lecture-04.html`
    - `build/reports/builds/teacher/nb/revealjs/collection/lecture-04/build-manifest.json`
    - `build/reports/builds/teacher/nb/revealjs/collection/lecture-04/dependency-manifest.json`
    - `build/reports/builds/teacher/nb/revealjs/collection/lecture-04/teacher-leakage-report.json`
- Bootstrap regression check passed:
  - `build/exports/teacher/nb/pdf/collection/lecture-04/lecture-04.pdf`
- Additional sanity render passed:
  - `build/exports/student/en/html/resource/angrist-podcast-iv/angrist-podcast-iv.html`
- Audience separation confirmed:
  - teacher prompt appears in teacher HTML only
  - teacher prompt does not appear in student HTML
- Student leakage reporting confirmed:
  - concept student build report status is `clean`
  - topic listing student build report status is `clean`
  - resource listing student build report status is `clean`

## Next Recommended Step

- Continue within Phase 5 student-site MVP depth:
  - add course-centric and concept-centric navigation pages beyond the current minimal listing set
  - add breadcrumbs / related-links polish and more topic/resource listing coverage
  - extend search/navigation across the generated student pages
  - keep Phase 6 exercise-sheet / solution work deferred until explicitly started

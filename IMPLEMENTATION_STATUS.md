# Implementation Status

## Current Milestone

- Bootstrap milestone checkpoint complete:
  - repo skeleton
  - naming conventions and language policy locked
  - schemas and validator
  - thin CLI
  - sample content objects
  - Quarto baseline with audience/language profiles
  - representative renders and tests

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
- Generated and verified these representative outputs:
  - concept HTML in `en`
  - concept HTML in `nb`
  - lecture Reveal.js in `nb`
  - lecture PDF in `nb`
  - course landing page HTML in `nb`

## Remaining Tasks

- Bootstrap milestone follow-up only:
  - add richer manifest/report outputs for build leakage checks
  - deepen collection/course assembly beyond generated wrapper documents
  - add more student-facing pages and listings from later roadmap phases
  - add approval, stale-content, and coverage commands from later CLI phases
  - add real custom formats for `handout` and `exercise-sheet` instead of the current PDF alias path

## Blockers

- None at checkpoint

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
- `schemas/`
- `content/`
- `collections/`
- `courses/`
- `filters/`
- `formats/`
- `templates/`
- `scripts/`
- `tests/`
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

## Test / Build Results

- Validation passed:
  - `Validated 5 objects and 1 courses. Issues: 0.`
- Lint passed:
  - `ruff check app tests`
- Tests passed:
  - `6 passed in 3.02s`
- Representative renders passed:
  - `build/exports/student/en/html/concept/iv-intuition/iv-intuition.html`
  - `build/exports/student/nb/html/concept/iv-intuition/iv-intuition.html`
  - `build/exports/teacher/en/html/concept/iv-intuition/iv-intuition.html`
  - `build/exports/teacher/nb/revealjs/collection/lecture-04/lecture-04.html`
  - `build/exports/teacher/nb/pdf/collection/lecture-04/lecture-04.pdf`
  - `build/exports/student/nb/html/course/ec202/ec202.html`
- Audience separation confirmed:
  - teacher prompt appears in teacher HTML only
  - teacher prompt does not appear in student HTML

## Next Recommended Step

- Start the next roadmap slice at Phase 3 / Phase 5 depth:
  - formalize collection and course assembly as first-class compilation inputs
  - generate student-facing listings/navigation from metadata
  - extend validation to output manifests and teacher-leakage reports

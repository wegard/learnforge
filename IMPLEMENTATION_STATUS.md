# Implementation Status

## Current Milestone

- Phase 7A complete checkpoint: figure pipeline core

## Non-Goals For This Run

- No full D3 component system
- No broad figure authoring UI
- No resource approval workflow
- No AI draft workflow
- No deployment or publishing target
- No migration tooling
- No Textual TUI

## Decisions Locked

- `ROADMAP.md` remains the source of truth
- Python remains the control-plane language
- The CLI remains thin `Typer`; no TUI
- Pydantic remains the schema/validation layer
- Norwegian stays locked to `nb`
- Quarto remains the build engine for site, slides, and PDF paths
- Source of truth remains plain-text files under git
- One canonical object ID is shared across languages
- Student/teacher visibility separation stays enforced at assembly/build level
- Exercise solutions remain in separate `solution.en.qmd` / `solution.nb.qmd` files
- Representative validation/build targets remain declared in `representative-targets.yml`
- `teach validate` remains the first-class quality-gate command and writes:
  - `build/reports/validation-report.json`
  - `build/reports/build-summary.json`
- Figure objects now use a locked core asset convention:
  - `figure.svg`
  - `figure.pdf`
  - optional `figure.js`
  - optional `data/`
- Figure metadata now carries linked `concepts` plus a normalized `asset_inventory`
- Figure HTML interactivity is a local progressive-enhancement path only
- `revealjs` and PDF/print builds always use static fallbacks
- Build manifests now expose `figure_uses` with source assets, interactive inclusion, and chosen fallback asset per target

## Completed Tasks

- Bootstrap repository, CLI, schemas, sample objects, Quarto project, student/teacher profiles, and representative bootstrap renders
- Centralized assembly in `app/assembly.py` for object pages, lecture collections, course pages, and metadata-driven listings
- Student-site MVP:
  - home page
  - course pages
  - lecture pages
  - exercise pages
  - concept/resource pages
  - topic/resource listings
  - shared navigation, breadcrumbs, search, and language switching
- Exercise compiler core:
  - student exercise-sheet compilation
  - teacher solution-sheet compilation
  - strict solution separation and leakage reporting
- Assignment integration:
  - assignments surfaced on course pages
  - assignment HTML pages
  - assignment manifests and navigation
- Validation + CI hardening:
  - stronger `teach validate`
  - machine-readable validation/build summaries
  - representative target registry
  - GitHub Actions CI for lint, tests, validation, and representative builds
- Phase 7A figure pipeline core:
  - finalized the `figure` model around linked `concepts`, locked asset paths, and normalized `asset_inventory`
  - added figure validation for missing SVG/PDF assets, missing inventory assets, missing linked concepts, and interactive figures without buildable static fallbacks
  - added first-class reusable figure rendering in `app/assembly.py` for:
    - figure pages
    - concept pages
    - lecture collection pages
  - added one local interactive HTML figure path through `content/figures/iv-dag-figure/figure.js`
  - enforced static fallback behavior for:
    - `html` via inline SVG fallback
    - `revealjs` via static SVG only
    - `pdf` / print via `figure.pdf`
  - refactored the sample `iv-dag-figure` object to use:
    - `figure.svg`
    - `figure.pdf`
    - `figure.js`
    - localized note text without page-local image duplication
  - extended build manifests with:
    - `figure_observation_count`
    - `figure_uses`
    - `interactive_included`
    - `fallback_asset_path`
  - added figure representative targets for:
    - student interactive figure HTML
    - teacher figure PDF fallback
  - added/extended tests for:
    - figure schema validation
    - missing fallback detection
    - concept-page figure embedding
    - lecture/reveal fallback behavior
    - figure-page manifest contents
    - representative build coverage
    - snapshot-style figure fragment verification

## Remaining Tasks

- Later figure work remains deferred beyond this narrow slice:
  - broader figure authoring UX
  - richer interactive packaging beyond the first local JS path
  - any full D3 component system
- Later roadmap phases remain deferred:
  - Phase 8 resource approval and stale-content workflows
  - AI workflows
  - migration tooling
  - deployment/publishing targets
  - preview/release publishing jobs
  - broader site-wide validation only where later roadmap slices require it

## Blockers

- None at this checkpoint for the sequential `teach build` / `teach validate` path
- Parallel HTML renders can still trip Quarto's shared `site_libs` staging behavior; the sequential repository workflow passes cleanly

## Files Changed

- `IMPLEMENTATION_STATUS.md`
- `app/assembly.py`
- `app/build.py`
- `app/models.py`
- `app/scaffold.py`
- `app/validator.py`
- `content/figures/iv-dag-figure/meta.yml`
- `content/figures/iv-dag-figure/note.en.qmd`
- `content/figures/iv-dag-figure/note.nb.qmd`
- `content/figures/iv-dag-figure/figure.svg`
- `content/figures/iv-dag-figure/figure.pdf`
- `content/figures/iv-dag-figure/figure.js`
- `content/figures/iv-dag-figure/assets/iv-dag.svg` removed
- `representative-targets.yml`
- `schemas/figure.schema.json`
- `templates/meta.yml.j2`
- `tests/test_assembly.py`
- `tests/test_builds.py`
- `tests/test_schema.py`
- `tests/test_validation.py`
- `tests/snapshots/iv-dag-figure.student.en.html.qmd`

## Commands Run

- `sed -n '1,320p' IMPLEMENTATION_STATUS.md`
- `sed -n '1150,1188p' ROADMAP.md`
- `sed -n '186,210p' ROADMAP.md`
- `sed -n '700,716p' ROADMAP.md`
- `sed -n '880,890p' ROADMAP.md`
- `sed -n '1,240p' app/models.py`
- `sed -n '1,240p' app/scaffold.py`
- `sed -n '1,360p' app/assembly.py`
- `sed -n '360,920p' app/assembly.py`
- `sed -n '920,1245p' app/assembly.py`
- `sed -n '1240,1520p' app/assembly.py`
- `sed -n '1520,2140p' app/assembly.py`
- `sed -n '2140,2860p' app/assembly.py`
- `sed -n '2860,3060p' app/assembly.py`
- `sed -n '1,240p' app/validator.py`
- `sed -n '360,760p' app/validator.py`
- `sed -n '760,1120p' app/validator.py`
- `sed -n '1,320p' app/build.py`
- `sed -n '1,220p' content/figures/iv-dag-figure/meta.yml`
- `sed -n '1,220p' content/figures/iv-dag-figure/note.en.qmd`
- `sed -n '1,220p' content/figures/iv-dag-figure/note.nb.qmd`
- `find content/figures -maxdepth 3 -type f | sort`
- `sed -n '1,240p' tests/test_schema.py`
- `sed -n '1,260p' tests/test_validation.py`
- `sed -n '1,240p' tests/test_assembly.py`
- `sed -n '1,260p' tests/test_builds.py`
- `which rsvg-convert`
- `rsvg-convert -f pdf -o content/figures/iv-dag-figure/figure.pdf content/figures/iv-dag-figure/figure.svg`
- `./.venv/bin/ruff check app/assembly.py app/scaffold.py --fix`
- `./.venv/bin/ruff check app tests`
- `./.venv/bin/python -m app.schema_export`
- `./.venv/bin/python -m pytest -q`
- `./.venv/bin/teach build iv-dag-figure --audience student --lang en --format html`
- `./.venv/bin/teach build iv-dag-figure --audience teacher --lang en --format pdf`
- `./.venv/bin/teach build iv-intuition --audience student --lang en --format html`
- `./.venv/bin/teach build lecture-04 --audience teacher --lang nb --format revealjs`
- `./.venv/bin/teach validate`
- `rg -n "lf-figure|Highlight relevance|figure.js|figure.pdf|IV DAG|Caption" build/exports/student/en/html/figure/iv-dag-figure/iv-dag-figure.html build/exports/student/en/html/concept/iv-intuition/iv-intuition.html build/exports/teacher/nb/revealjs/collection/lecture-04/lecture-04.html`
- `sed -n '1,260p' build/reports/builds/student/en/html/figure/iv-dag-figure/build-manifest.json`
- `sed -n '1,240p' build/reports/builds/student/en/html/concept/iv-intuition/build-manifest.json`
- `pdftotext build/exports/teacher/en/pdf/figure/iv-dag-figure/iv-dag-figure.pdf - | sed -n '1,80p'`

## Test / Build Results

- Validation passed:
  - `Validated 7 objects and 1 courses. Errors: 0. Warnings: 0.`
  - `Representative targets: 10/10 passed`
- Lint passed:
  - `All checks passed!`
- Tests passed:
  - `46 passed in 302.31s (0:05:02)`
- Validation JSON report:
  - `build/reports/validation-report.json`
- Build summary JSON:
  - `build/reports/build-summary.json`
- Figure representative outputs verified:
  - Concept page with reusable figure:
    - `build/exports/student/en/html/concept/iv-intuition/iv-intuition.html`
    - `build/reports/builds/student/en/html/concept/iv-intuition/build-manifest.json`
    - `build/reports/builds/student/en/html/concept/iv-intuition/dependency-manifest.json`
    - `build/reports/builds/student/en/html/concept/iv-intuition/teacher-leakage-report.json`
  - Lecture collection page reusing the same figure:
    - `build/exports/teacher/nb/revealjs/collection/lecture-04/lecture-04.html`
    - `build/reports/builds/teacher/nb/revealjs/collection/lecture-04/build-manifest.json`
    - `build/reports/builds/teacher/nb/revealjs/collection/lecture-04/dependency-manifest.json`
    - `build/reports/builds/teacher/nb/revealjs/collection/lecture-04/teacher-leakage-report.json`
  - Student HTML figure page with interactive path:
    - `build/exports/student/en/html/figure/iv-dag-figure/iv-dag-figure.html`
    - `build/reports/builds/student/en/html/figure/iv-dag-figure/build-manifest.json`
    - `build/reports/builds/student/en/html/figure/iv-dag-figure/dependency-manifest.json`
    - `build/reports/builds/student/en/html/figure/iv-dag-figure/teacher-leakage-report.json`
  - PDF fallback output:
    - `build/exports/teacher/en/pdf/figure/iv-dag-figure/iv-dag-figure.pdf`
    - `build/reports/builds/teacher/en/pdf/figure/iv-dag-figure/build-manifest.json`
    - `build/reports/builds/teacher/en/pdf/figure/iv-dag-figure/dependency-manifest.json`
    - `build/reports/builds/teacher/en/pdf/figure/iv-dag-figure/teacher-leakage-report.json`
  - Figure asset usage report:
    - `build/reports/builds/student/en/html/figure/iv-dag-figure/build-manifest.json`
    - `figure_observation_count: 1`
    - `interactive_included: true`
    - `fallback_asset_path: content/figures/iv-dag-figure/figure.svg`
- Existing representative outputs still passed:
  - Student assignment HTML:
    - `build/exports/student/en/html/collection/assignment-01/assignment-01.html`
  - Student exercise-sheet PDF:
    - `build/exports/student/en/exercise-sheet/collection/assignment-01/assignment-01-exercise-sheet.pdf`
  - Teacher solution-sheet PDF:
    - `build/exports/teacher/en/exercise-sheet/collection/assignment-01/assignment-01-solution-sheet.pdf`
- Student safety rules remain clean:
  - representative student targets report `leakage_status: clean`
  - figure HTML pages do not introduce teacher-only leakage
  - validation finished with `error_count: 0` and `warning_count: 0`

## CI Workflow Files Added

- `.github/workflows/ci.yml`

## Next Recommended Step

- Stop at this clean Phase 7A checkpoint
- If the roadmap continues with figures next, keep the next slice narrow:
  - expand figure reuse beyond the current concept/lecture path only where roadmap scope requires it
  - add richer interactive packaging only after the static-fallback policy remains fully protected
- Otherwise resume with the next explicitly chosen later phase:
  - Phase 8 resource approval and stale-content workflows
  - a later deployment/publishing slice when preview/release jobs are in scope

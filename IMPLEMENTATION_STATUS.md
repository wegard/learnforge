# Implementation Status

## Current Milestone

- Phase 8A complete checkpoint: resource curation workflow core
- Repository maintenance: course inbox staging for legacy-course intake
- Phase 11 kickoff complete checkpoint: `tem0052` migration inventory + canonical course shell

## Non-Goals For This Run

- No AI-generated resource suggestion ingestion workflow
- No translation draft workflow
- No public deployment or publishing job
- No bulk migration tooling
- No notebook auto-conversion pipeline
- No mass import from `course-inbox/`
- No Textual TUI
- No broad redesign of existing student navigation beyond what resource workflow required

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
- Figure objects remain on the locked `figure.svg` / `figure.pdf` / optional `figure.js` convention with static fallback protection
- Resource workflow states are now explicit and validated:
  - `candidate`
  - `reviewed`
  - `approved`
  - `published`
- Resource approval history now lives in metadata as `approval_history` entries with:
  - `action`
  - `by`
  - `acted_on`
- Time-sensitive resources must declare `review_after`
- Candidate/reviewed resources must not carry `approved_by` / `approved_on`
- Approved/published resources must carry:
  - `summary`
  - `why_selected`
  - `approved_by`
  - `approved_on`
- Student builds hide stale approved resources in this slice rather than surfacing a warning banner
- Teacher-facing resource triage uses the synthetic target id `resource-inbox`
- Resource approval transitions are kept explicit:
  - `candidate -> reviewed`
  - `reviewed -> approved`
  - `approved -> published`
- The CLI currently implements the narrow editorial controls needed for this slice:
  - `teach approve <resource-id>`
  - `teach approve <resource-id> --publish`
  - `teach stale resources`

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
- Figure pipeline core:
  - reusable figure objects
  - local HTML interactivity with static SVG/PDF fallback
  - figure usage reporting in manifests
- Phase 8A resource curation workflow core:
  - finalized the resource workflow model around `candidate`, `reviewed`, `approved`, and `published`
  - added approval-history support with deterministic `acted_on` metadata
  - relaxed candidate/reviewed metadata while enforcing stricter approved/published requirements
  - enforced course/topic linkage for every resource
  - added repo-level resource workflow reporting to `teach validate`
  - added stale-resource detection and reporting
  - added teacher-facing `resource-inbox` HTML assembly target
  - tightened student publication rules so student outputs exclude:
    - candidate resources
    - reviewed resources
    - stale approved resources
    - resources that fail publication metadata rules
  - added `teach approve` for explicit reviewed->approved and approved->published transitions
  - added `teach stale resources` and `build/reports/stale-resources.json`
  - added sample resource states covering:
    - one candidate resource
    - one reviewed resource
    - one approved stale resource
    - one published student-visible resource
  - extended representative targets with:
    - student approved resource page
    - teacher resource inbox
  - extended tests for:
    - resource schema validation
    - stale detection
    - student exclusion of non-approved/stale resources
    - teacher inbox rendering
    - approval CLI behavior
    - stale-report CLI behavior
    - validation/build report contents for the resource workflow
- Added a git-ignored `course-inbox/` staging area for legacy course material intake
- Locked the intake rule that `course-inbox/` is never scanned as canonical content,
  indexed for search, or used as a build input
- Added written intake conventions for per-course subfolders and coarse sorting
  buckets in `course-inbox/README.md`
- Added regression coverage to prove validation ignores stray `meta.yml` files under
  `course-inbox/`
- Added a tracked `tem0052` migration-stage course shell:
  - `courses/tem0052/course.yml`
  - `courses/tem0052/plan.yml`
  - `courses/tem0052/syllabus.en.qmd`
- Added a tracked migration inventory in `courses/tem0052/MIGRATION_INVENTORY.md`
  mapping legacy notebooks, exercises, slide material, and datasets into:
  - promote first
  - rewrite fresh
  - defer
  - drop or archive
- Locked the migration-start decisions for `tem0052`:
  - canonical course id is `tem0052`
  - migration starts with `en` only
  - legacy notebooks remain reference material, not source of truth
  - new canonical material should prefer `.qmd` for exposition and `.py` for reusable code
- Hardened the Quarto/build path so `course-inbox/` is excluded from project rendering
- Fixed single-file Quarto build handling to:
  - keep project rendering compatible with the inbox exclusion
  - move rendered `*_files` support directories into exported HTML / Reveal.js outputs
  - keep PDF-family outputs on `pdflatex`
- Added regression coverage for the migration-stage course shell:
  - repository validation now expects two tracked courses
  - `tem0052` student HTML builds without dead resource-listing links

## Remaining Tasks

- Stop at this clean `tem0052` migration kickoff checkpoint
- Later resource-workflow work remains deferred:
  - broader course/topic filtering controls beyond the current inbox/listing path
  - richer approval workflows beyond the narrow `approve` transition command
  - any AI-assisted resource suggestion ingestion
- Legacy migration remains deferred beyond inbox staging:
  - no bulk import scripts/templates yet
  - no automatic conversion from `course-inbox/` into canonical objects
  - no first promoted `tem0052` concept/exercise objects yet
  - no `tem0052` lecture collections yet
  - no `tem0052` project/assignment materials yet
- Later roadmap phases remain deferred:
  - Phase 9 AI-assisted draft workflows
  - migration tooling
  - deployment/publishing targets
  - preview/release publishing jobs
  - Textual TUI work

## Blockers

- None at this checkpoint for the sequential `teach build` / `teach validate` / `teach stale resources` path
- Quarto still expects sequential HTML builds because of shared `site_libs` staging; the repository workflow and CI path remain stable when builds run sequentially

## Files Changed

- `IMPLEMENTATION_STATUS.md`
- `README.md`
- `.gitignore`
- `course-inbox/.gitkeep`
- `course-inbox/README.md`
- `_quarto.yml`
- `app/assembly.py`
- `app/build.py`
- `app/cli.py`
- `app/models.py`
- `app/resource_workflow.py`
- `app/validator.py`
- `content/resources/angrist-podcast-iv/meta.yml`
- `content/resources/iv-candidate-newsletter/meta.yml`
- `content/resources/iv-candidate-newsletter/note.en.qmd`
- `content/resources/iv-candidate-newsletter/note.nb.qmd`
- `content/resources/iv-reviewed-primer/meta.yml`
- `content/resources/iv-reviewed-primer/note.en.qmd`
- `content/resources/iv-reviewed-primer/note.nb.qmd`
- `content/resources/iv-policy-brief-stale/meta.yml`
- `content/resources/iv-policy-brief-stale/note.en.qmd`
- `content/resources/iv-policy-brief-stale/note.nb.qmd`
- `courses/tem0052/course.yml`
- `courses/tem0052/plan.yml`
- `courses/tem0052/syllabus.en.qmd`
- `courses/tem0052/MIGRATION_INVENTORY.md`
- `representative-targets.yml`
- `schemas/resource.schema.json`
- `templates/meta.yml.j2`
- `tests/test_assembly.py`
- `tests/test_builds.py`
- `tests/test_cli.py`
- `tests/test_schema.py`
- `tests/test_validation.py`

## Commands Run

- Repository/status inspection and roadmap review:
  - `git status --short`
  - `sed -n '1,260p' IMPLEMENTATION_STATUS.md`
  - `rg -n "Phase 8|resource approval|candidate|reviewed|published|review_after|stale|approve|resource curation|inbox" ROADMAP.md`
  - `sed -n '1178,1228p' ROADMAP.md`
  - `sed -n '780,854p' ROADMAP.md`
  - `sed -n '1380,1442p' ROADMAP.md`
- Code inspection:
  - `sed -n '1,240p' app/models.py`
  - `sed -n '1,260p' app/cli.py`
  - `sed -n '1,420p' app/validator.py`
  - `sed -n '1,260p' app/indexer.py`
  - `sed -n '1,260p' app/build.py`
  - `sed -n '1,220p' templates/meta.yml.j2`
  - `find content/resources -maxdepth 2 -type f | sort`
- Validation/debugging:
  - `./.venv/bin/python - <<'PY' ... validate_repository(...) ... PY`
  - `./.venv/bin/python - <<'PY' ... load_repository(...) ... PY`
- Formatting/schema/tests/build verification:
  - `./.venv/bin/python -m app.schema_export`
  - `./.venv/bin/ruff check app tests`
  - `./.venv/bin/python -m pytest -q`
  - `./.venv/bin/teach validate`
  - `./.venv/bin/teach build angrist-podcast-iv --audience student --lang en --format html`
  - `./.venv/bin/teach build resources-ec202 --audience student --lang en --format html`
  - `./.venv/bin/teach build resource-inbox --audience teacher --lang en --format html`
  - `./.venv/bin/teach stale resources --today 2026-03-18`
- Artifact/report inspection:
  - `./.venv/bin/python - <<'PY' ... inspect validation/build/stale JSON payloads ... PY`
  - `rg -n "angrist-podcast-iv|iv-candidate-newsletter|iv-reviewed-primer|iv-policy-brief-stale|Resource Inbox|Candidate resources|Reviewed resources|Stale resources" build/exports/student/en/html/listing/resources-ec202/resources-ec202.html build/exports/student/en/html/resource/angrist-podcast-iv/angrist-podcast-iv.html build/exports/teacher/en/html/listing/resource-inbox/resource-inbox.html`
- Course inbox staging:
  - `sed -n '1,220p' .gitignore`
  - `sed -n '1,220p' README.md`
  - `sed -n '1,260p' app/indexer.py`
  - `sed -n '1,260p' app/config.py`
  - `sed -n '1,220p' tests/test_schema.py`
  - `./.venv/bin/python -m pytest -q tests/test_schema.py`
  - `mkdir -p course-inbox/ec202/notes && printf 'temporary\n' > course-inbox/ec202/notes/sample.txt && git check-ignore -v course-inbox/ec202/notes/sample.txt && rm course-inbox/ec202/notes/sample.txt`
  - `./.venv/bin/teach validate`
- `tem0052` migration kickoff:
  - `find course-inbox/predictive-modelling-with-machine-learning -maxdepth 3 -type f | sort`
  - `find course-inbox/predictive-modelling-with-machine-learning -maxdepth 3 -type d | sort`
  - `python3 - <<'PY' ... count extensions and sizes ... PY`
  - `sed -n '1,220p' course-inbox/predictive-modelling-with-machine-learning/README.md`
  - `sed -n '1,220p' course-inbox/predictive-modelling-with-machine-learning/tex2026/course_plan_2026.tex`
  - `sed -n '1,220p' course-inbox/predictive-modelling-with-machine-learning/tex2026/presentation_plan.md`
  - `python3 - <<'PY' ... inspect notebook titles/imports/dataset references ... PY`
  - `sed -n '200,245p' app/models.py`
  - `sed -n '760,860p' app/assembly.py`
  - `sed -n '2985,3045p' app/assembly.py`
  - `quarto render --help`
  - `./.venv/bin/teach build tem0052 --audience student --lang en --format html`
  - `./.venv/bin/python -m pytest -q tests/test_schema.py tests/test_builds.py`
  - `./.venv/bin/ruff check app tests`
  - `./.venv/bin/python -m pytest -q`
  - `./.venv/bin/teach validate`

## Test / Build Results

- Validation passed with warnings:
  - `Validated 10 objects and 2 courses. Errors: 0. Warnings: 2.`
  - `Representative targets: 12/12 passed`
  - Warnings are expected in this slice for the sample stale approved resource:
    - `resource-hidden-from-student-site`
    - `stale-resource`
- Lint passed:
  - `All checks passed!`
- Tests passed:
  - `59 passed in 130.34s (0:02:10)`
- Course inbox regression checks passed:
  - `11 passed in 0.31s` for `tests/test_schema.py`
  - `git check-ignore` confirmed `course-inbox/ec202/notes/sample.txt` is ignored by `.gitignore`
  - `teach validate` still passed with `Errors: 0. Warnings: 2. Representative targets: 12/12 passed`
- `tem0052` migration kickoff checks passed:
  - `30 passed in 48.25s` for `tests/test_schema.py tests/test_builds.py`
  - `teach build tem0052 --audience student --lang en --format html` succeeded
  - Quarto render remains isolated from `course-inbox/`
- Validation JSON report:
  - `build/reports/validation-report.json`
- Build summary JSON:
  - `build/reports/build-summary.json`
- Stale-resource report:
  - `build/reports/stale-resources.json`
  - `stale_resource_count: 1`
  - `iv-policy-brief-stale` reported as review-due
- Resource workflow summary in validation report:
  - `status_counts: candidate=1, reviewed=1, approved=1, published=1`
  - `student_visible_resource_ids: ['angrist-podcast-iv']`
  - `student_exclusion_count: 3`
- Representative resource outputs verified:
  - Student approved resource page:
    - `build/exports/student/en/html/resource/angrist-podcast-iv/angrist-podcast-iv.html`
    - `build/reports/builds/student/en/html/resource/angrist-podcast-iv/build-manifest.json`
    - `build/reports/builds/student/en/html/resource/angrist-podcast-iv/dependency-manifest.json`
    - `build/reports/builds/student/en/html/resource/angrist-podcast-iv/teacher-leakage-report.json`
  - Student resource listing with exclusions:
    - `build/exports/student/en/html/listing/resources-ec202/resources-ec202.html`
    - `build/reports/builds/student/en/html/listing/resources-ec202/build-manifest.json`
    - `build/reports/builds/student/en/html/listing/resources-ec202/dependency-manifest.json`
    - `build/reports/builds/student/en/html/listing/resources-ec202/teacher-leakage-report.json`
    - `included_resource_ids: ['angrist-podcast-iv']`
    - `excluded_resources: iv-candidate-newsletter, iv-reviewed-primer, iv-policy-brief-stale`
  - Teacher resource inbox:
    - `build/exports/teacher/en/html/listing/resource-inbox/resource-inbox.html`
    - `build/reports/builds/teacher/en/html/listing/resource-inbox/build-manifest.json`
    - `build/reports/builds/teacher/en/html/listing/resource-inbox/dependency-manifest.json`
    - `build/reports/builds/teacher/en/html/listing/resource-inbox/teacher-leakage-report.json`
- Existing representative outputs remained green through `teach validate`:
  - student concept page
  - student topic listing
  - student assignment HTML
  - student exercise sheet
  - teacher lecture slides
  - teacher figure PDF fallback
  - teacher solution sheet
- `tem0052` migration-stage outputs verified:
  - Student course page:
    - `build/exports/student/en/html/course/tem0052/tem0052.html`
    - `build/reports/builds/student/en/html/course/tem0052/build-manifest.json`
    - `build/reports/builds/student/en/html/course/tem0052/dependency-manifest.json`
    - `build/reports/builds/student/en/html/course/tem0052/teacher-leakage-report.json`
  - Tracked migration inventory:
    - `courses/tem0052/MIGRATION_INVENTORY.md`

## CI Workflow Files Added

- `.github/workflows/ci.yml` (from the earlier validation/CI slice; unchanged in this run)

## Next Recommended Step
- Promote the first real `tem0052` canonical objects from the inventory:
  - 1 concept from the statistical foundations / bias-variance block
  - 1 converted exercise with `solution.en.qmd`
  - 1 lecture collection assembled only from promoted objects

- Stop at this clean Phase 8A checkpoint
- If resource workflow continues next, keep the next slice narrow:
  - add richer teacher editorial views or tighter publication filters only where the roadmap requires them
  - avoid starting AI-assisted ingestion until the review-state and publication rules remain unchanged and well-tested
- Otherwise move to the next explicitly selected roadmap slice after resource governance

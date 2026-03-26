# LearnForge

LearnForge is a git-backed, markdown-first teaching publication system for building reusable course websites, slides, PDFs, assignments, and curated resource pages from a shared pool of learning objects.

The core rule is simple:

> Courses and lectures do not own content. They assemble reusable learning objects.

The system currently supports:

- reusable `concept`, `exercise`, `figure`, `resource`, `collection`, and `course` objects
- Quarto-based builds for student and teacher audiences
- bilingual publishing with `en` / `nb` variants
- HTML, PDF, Reveal.js, slides-PDF, handout, and exercise-sheet outputs
- validation, representative build checks, and machine-readable reports
- explicit resource approval workflow (`candidate` -> `reviewed` -> `approved` -> `published`)
- student-only publish bundling for static deployment
- migration of legacy course material through a controlled `course-inbox/` staging area
- terminal dashboard (`teach tui`) for browsing courses, tracking attention items, and editing content

## Documentation Map

Use the docs by role:

- `README.md` — front door: what the project is, how it is structured, and how to run it
- `ROADMAP.md` — source of truth for product direction, architecture, and locked design decisions
- `IMPLEMENTATION_STATUS.md` — current milestone, completed work, and recent checkpoint history
- `PYTHON_ENVIRONMENT.md` — environment setup, dependencies, and tooling
- `ui-spec.md` — terminal dashboard design and navigation reference

If these files disagree, treat:

1. `ROADMAP.md` as canonical for direction and design
2. `IMPLEMENTATION_STATUS.md` as canonical for what has actually been implemented
3. `README.md` as the concise operator-facing summary

## Current Status

LearnForge is beyond the bootstrap/prototype stage. The core architecture is in place and working:

- Python control plane with `Typer` and `Pydantic`
- Quarto project with `student` / `teacher` and `en` / `nb` profiles
- first-class assembly for course pages, lecture pages, topic listings, assignment pages, and resource listings
- student/teacher separation with leakage checks
- reusable figures with static fallback and optional D3 interactivity
- validation reports, build manifests, dependency manifests, and representative target coverage
- student-site publish bundle under `build/publish/student-site/`
- six approved courses with proven cross-course object reuse
- terminal dashboard (`teach tui`) for browsing and editing content

This repo is now best understood as a working internal publishing system in an active content-refinement phase.

## Repository Shape

```text
learnforge/
├── app/                  # CLI, TUI, assembly, validation, build orchestration
├── content/              # canonical reusable learning objects
├── collections/          # lectures, assignments, and other object groupings
├── courses/              # course metadata, plans, syllabi, migration inventories
├── filters/              # Quarto/Lua filters
├── formats/              # output-format support files
├── schemas/              # metadata schemas and validation conventions
├── build/                # generated outputs, reports, exports, publish bundles
├── course-inbox/         # git-ignored staging area for legacy material
└── scripts/              # environment/bootstrap/build helpers
```

## Locked Conventions

- `ROADMAP.md` is the implementation source of truth
- one canonical object ID is shared across languages
- content files live in `note.en.qmd` / `note.nb.qmd` with shared `meta.yml`
- exercise solutions live in `solution.en.qmd` / `solution.nb.qmd`
- Norwegian is locked to `nb`
- student builds must not expose teacher-only content
- public publishing is student-only by default
- authoring stays terminal-first and file-first

## Requirements

- Python 3.13+
- Quarto 1.8+
- a PDF engine available to Quarto (`tectonic` is the current project default)
- a Chromium-based browser for `--format slides-pdf`

## Environment Setup

The repo can use a repo-local micromamba environment at `.micromamba/`.

```bash
./scripts/bootstrap_micromamba.sh
make install
make test
make validate
```

The `Makefile` targets and helper scripts run through the repo environment wrapper. Quarto, the PDF engine, and the browser requirement still come from the system unless you install them into the environment yourself.

## Core Commands

Most day-to-day work should go through `teach` or the `Makefile` wrappers.

```bash
make validate
make test
./scripts/run-in-env.sh teach tui                              # interactive dashboard
./scripts/run-in-env.sh teach build home --audience student --lang en --format html
./scripts/run-in-env.sh teach build lecture-04 --audience teacher --lang nb --format pdf
./scripts/run-in-env.sh teach build lecture-04 --audience teacher --lang nb --format revealjs
./scripts/run-in-env.sh teach publish
./scripts/run-in-env.sh teach stale resources
```

## Outputs

Generated artifacts are written under:

- `build/exports/` — rendered outputs by audience/language/format/target
- `build/reports/` — validation reports, build manifests, dependency manifests, leakage reports
- `build/index/` — generated search index data
- `build/publish/student-site/` — deployable public student bundle

Student home pages render to:

- `build/exports/student/<lang>/html/index.html`

The public student-site bundle is assembled under:

- `build/publish/student-site/`
- with `/en/` and `/nb/` roots plus a small language chooser at `index.html`

## Migration Workflow

Use `course-inbox/` as a temporary local staging area for legacy material during redesign or migration.

Important rules:

- it is git-ignored by default
- it is excluded from validation, search, and build inputs
- material only becomes canonical after promotion into `content/`, `collections/`, or `courses/`

## Near-Term Priorities

The main engineering challenge is no longer foundational architecture. It is consolidation and content refinement:

- Norwegian translations (especially `edi3400`)
- refining content based on teaching feedback
- tightening representative build checks around real workflows
- refining the student-facing HTML shell without abandoning the static-first approach

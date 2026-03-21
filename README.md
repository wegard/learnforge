# LearnForge

LearnForge is a git-backed, markdown-first teaching publishing system. The current checkpoint covers the roadmap's bootstrap foundation, the student-site MVP, the exercise compiler core, figure reuse, the first resource-curation workflow slice, and the first student-only publish path: reusable content objects, schema validation, first-class assembly, bilingual Quarto builds, separate student/teacher exercise outputs, explicit resource approval/stale reporting, and a reproducible public student-site bundle.

## Current Scope

- Plain-text source of truth under git
- Python control plane with `Typer` and `Pydantic`
- Quarto project with `student` / `teacher` and `en` / `nb` profiles
- Base schemas plus `concept`, `exercise`, `figure`, `resource`, and `collection`
- Ten sample objects, one assignment collection, and one sample course
- Validation, search, open, new, build, and publish CLI commands
- First-class assembly for course pages, lecture pages, topic listings, and resource listings
- Student-site navigation with breadcrumbs, language switching, related links, and search-backed navigation shell
- Exercise compiler path with separate `solution.<lang>.qmd` files and teacher-only solution sheets
- Resource workflow states for `candidate`, `reviewed`, `approved`, and `published`
- Representative renders for home, course, lecture, concept, exercise, resource, topic listing, slides, and PDF export paths
- Student-only publish bundle generation under `build/publish/student-site/`, deployable to GitHub Pages via the manual-dispatch workflow
- A migration-stage `tem0052` course shell and tracked inventory for promoting legacy material from `course-inbox/`

## Direction Locked For Next Web Slice

- Teacher workflow stays terminal-first; browser instructor mode is preview/review only
- Authoring remains markdown/qmd/yaml-first in `nvim`
- HTML should evolve into a responsive app shell through progressive enhancement, not a frontend framework rewrite
- Public deployment should target student mode only by default
- Advanced interactive figures should prefer object-local D3 with mandatory static fallbacks

## Requirements

- Python 3.13+
- Quarto 1.8+
- A PDF engine available to Quarto (`pdflatex` or `tectonic`)
- A Chromium-based browser for `--format slides-pdf`

## Micromamba

The repo can use a repo-local micromamba environment at `.micromamba/`.

```bash
./scripts/bootstrap_micromamba.sh
make test
make validate
```

After bootstrap, the repo's `Makefile` targets plus `scripts/render.sh`,
`scripts/export_pdf.sh`, and `scripts/export_slides_pdf.sh` will run inside
that micromamba environment automatically. Quarto, the PDF engine, and the
browser requirement still come from your system install unless you add them to
the environment yourself.

## Quick Start

```bash
python3 -m pip install -e .[dev]
pre-commit install
teach validate
teach build home --audience student --lang en --format html
teach build iv-intuition --audience student --lang en --format html
teach build iv-intuition --audience student --lang nb --format html
teach build ex-iv-concept-check --audience student --lang en --format html
teach build assignment-01 --audience student --lang en --format exercise-sheet
teach build assignment-01 --audience teacher --lang en --format exercise-sheet
teach build angrist-podcast-iv --audience student --lang en --format html
teach build lecture-04 --audience student --lang en --format html
teach build lecture-04 --audience teacher --lang nb --format revealjs
teach build lecture-04 --audience teacher --lang nb --format pdf
teach build lecture-04 --audience teacher --lang nb --format slides-pdf
teach translation-status bik2551 --lang en
teach build ec202 --audience student --lang en --format html
teach build topic-causal-inference --audience student --lang en --format html
teach build resources-ec202 --audience student --lang en --format html
teach build resource-inbox --audience teacher --lang en --format html
teach publish
teach stale resources
pytest
```

Generated outputs are written under `build/exports/`, publish bundles under `build/publish/`, generated build/validation reports under `build/reports/`, and the filesystem search index under `build/index/`. Student home pages render to `build/exports/student/<lang>/html/index.html`, and the public student-site bundle is assembled under `build/publish/student-site/` with `/en/` and `/nb/` roots plus a small language chooser page at `build/publish/student-site/index.html`.

For migration and redesign work, use `course-inbox/` as a temporary local staging
area for legacy material. It is git-ignored by default and excluded from validation,
search, and build inputs until material is promoted into `content/`, `collections/`,
or `courses/`.

## Conventions Locked

- `ROADMAP.md` is the implementation source of truth
- One canonical object ID across languages
- Content lives in `note.en.qmd` and `note.nb.qmd` with shared `meta.yml`
- Exercise solutions live in `solution.en.qmd` and `solution.nb.qmd`
- Norwegian content is locked to `nb`
- Student builds must not expose teacher-only content

## Current Status

See `IMPLEMENTATION_STATUS.md` for the active milestone, completed work, validation history, and next step.

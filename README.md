# LearnForge

LearnForge is a git-backed, markdown-first teaching publishing system. The current checkpoint covers the roadmap's bootstrap foundation, the student-site MVP, and the first exercise-compiler slice: reusable content objects, schema validation, first-class assembly, bilingual Quarto builds, and separate student/teacher exercise outputs from the same source set.

## Current Scope

- Plain-text source of truth under git
- Python control plane with `Typer` and `Pydantic`
- Quarto project with `student` / `teacher` and `en` / `nb` profiles
- Base schemas plus `concept`, `exercise`, `figure`, `resource`, and `collection`
- Seven sample objects, one assignment collection, and one sample course
- Validation, search, open, new, and build CLI commands
- First-class assembly for course pages, lecture pages, topic listings, and resource listings
- Student-site navigation with breadcrumbs, language switching, related links, and search-backed navigation shell
- Exercise compiler path with separate `solution.<lang>.qmd` files and teacher-only solution sheets
- Representative renders for home, course, lecture, concept, exercise, resource, topic listing, slides, and PDF export paths

## Requirements

- Python 3.13+
- Quarto 1.8+
- A PDF engine available to Quarto (`pdflatex` or `tectonic`)

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
teach build ec202 --audience student --lang en --format html
teach build topic-causal-inference --audience student --lang en --format html
teach build resources-ec202 --audience student --lang en --format html
pytest
```

Generated outputs are written under `build/exports/`, generated build/validation reports under `build/reports/`, and the filesystem search index under `build/index/`. Student home pages render to `build/exports/student/<lang>/html/index.html`.

## Conventions Locked

- `ROADMAP.md` is the implementation source of truth
- One canonical object ID across languages
- Content lives in `note.en.qmd` and `note.nb.qmd` with shared `meta.yml`
- Exercise solutions live in `solution.en.qmd` and `solution.nb.qmd`
- Norwegian content is locked to `nb`
- Student builds must not expose teacher-only content

## Current Status

See `IMPLEMENTATION_STATUS.md` for the active milestone, completed work, validation history, and next step.

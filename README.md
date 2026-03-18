# LearnForge

LearnForge is a git-backed, markdown-first teaching publishing system. The current checkpoint covers the roadmap's bootstrap foundation plus the student-site MVP slice: reusable content objects, schema validation, a thin `teach` CLI, first-class assembly, and bilingual Quarto builds for student and teacher outputs.

## Current Scope

- Plain-text source of truth under git
- Python control plane with `Typer` and `Pydantic`
- Quarto project with `student` / `teacher` and `en` / `nb` profiles
- Base schemas plus `concept`, `exercise`, `figure`, `resource`, and `collection`
- Five hand-made sample objects and one sample course
- Validation, search, open, new, and build CLI commands
- First-class assembly for course pages, lecture pages, topic listings, and resource listings
- Student-site navigation with breadcrumbs, language switching, related links, and search-backed navigation shell
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
- Norwegian content is locked to `nb`
- Student builds must not expose teacher-only content

## Current Status

See `IMPLEMENTATION_STATUS.md` for the active milestone, completed work, validation history, and next step.

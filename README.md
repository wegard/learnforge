# LearnForge

LearnForge is a git-backed, markdown-first teaching publishing system. This bootstrap milestone implements the roadmap's narrow foundation: reusable content objects, schema validation, a thin `teach` CLI, and Quarto-based sample builds in English and Norwegian Bokmal (`nb`).

## Bootstrap Scope

- Plain-text source of truth under git
- Python control plane with `Typer` and `Pydantic`
- Quarto project with `student` / `teacher` and `en` / `nb` profiles
- Base schemas plus `concept`, `exercise`, `figure`, `resource`, and `collection`
- Five hand-made sample objects and one sample course
- Validation, search, open, new, and build CLI commands
- Representative renders for concept, lecture slides, PDF export, and a course landing page

## Requirements

- Python 3.13+
- Quarto 1.8+
- A PDF engine available to Quarto (`pdflatex` or `tectonic`)

## Quick Start

```bash
python3 -m pip install -e .[dev]
pre-commit install
teach validate
teach build iv-intuition --audience student --lang en --format html
teach build iv-intuition --audience student --lang nb --format html
teach build lecture-04 --audience teacher --lang nb --format revealjs
teach build lecture-04 --audience teacher --lang nb --format pdf
teach build ec202 --audience student --lang nb --format html
pytest
```

Generated outputs are written under `build/exports/`, generated validation reports under `build/reports/`, and the filesystem search index under `build/index/`.

## Conventions Locked

- `ROADMAP.md` is the implementation source of truth
- One canonical object ID across languages
- Content lives in `note.en.qmd` and `note.nb.qmd` with shared `meta.yml`
- Norwegian content is locked to `nb`
- Student builds must not expose teacher-only content

## Current Status

See `IMPLEMENTATION_STATUS.md` for the active milestone, completed work, validation history, and next step.

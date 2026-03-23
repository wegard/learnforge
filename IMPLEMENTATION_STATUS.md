# Implementation Status

## Role of This File

This file is the concise implementation-facing status document for LearnForge.

Use the docs as follows:

- `ROADMAP.md` — canonical product direction, architecture, and design decisions
- `IMPLEMENTATION_STATUS.md` — current implementation checkpoint and active constraints
- `README.md` — concise operator-facing overview and setup guide

This file should stay shorter than a full development log. It is meant to answer:

1. What is implemented?
2. What is stable?
3. What is still deferred or risky?
4. What should happen next?

## Current Checkpoint

LearnForge is now a working internal teaching publication system in an active migration and consolidation phase.

The project has moved beyond bootstrap/prototype status. The core architecture is implemented and exercised across multiple real courses.

### Implemented core

- git-backed, plain-text source of truth
- Python control plane using `Typer` and `Pydantic`
- Quarto-based build pipeline for:
  - HTML
  - PDF
  - Reveal.js
  - slides-PDF
  - handout
  - exercise-sheet
- student / teacher build separation
- bilingual output model using `en` / `nb`
- reusable object model covering:
  - `concept`
  - `exercise`
  - `figure`
  - `resource`
  - `collection`
  - `course`
- first-class assembly for:
  - course pages
  - lecture pages
  - assignment pages
  - topic listings
  - resource listings
- validation, representative build checks, and machine-readable reports
- student-only publish bundle under `build/publish/student-site/`
- explicit resource workflow:
  - `candidate`
  - `reviewed`
  - `approved`
  - `published`
- teacher-content leakage checks during builds
- reusable figure pipeline with static fallback and optional D3 interactivity
- migration staging through `course-inbox/`

## Stable Decisions

The following are treated as locked unless the roadmap is explicitly revised:

- `ROADMAP.md` remains the source of truth for direction
- source of truth remains plain-text files under git
- teacher workflow remains terminal-first
- browser instructor mode is preview/review only
- Quarto remains the build engine
- one canonical object ID is shared across languages
- Norwegian remains locked to `nb`
- student builds must not expose teacher-only material
- public publishing is student-only by default
- HTML evolution should remain static-first with progressive enhancement
- D3 is allowed for advanced figures, but static fallbacks remain mandatory
- representative validation/build targets remain declared in `representative-targets.yml`
- PDF-family outputs use `tectonic` as the project default PDF engine

## Current Capability Snapshot

### Content and migration

The system now contains real migration progress rather than only sample data.

Notable status:

- `tem0052` has a substantial promoted canonical slice, including concepts, exercises, lectures, and assignment collections
- `edi3400` has a promoted course shell and substantial migrated content, including database material and assignment structure
- `gra4164` has a broad "promote first" slice in place
- `tem00uu` has a broad Part A migration slice in place
- `gra4150` now has a canonical course shell, lecture collections, exercises, and assignment collections
- cross-course object reuse is already happening across migrated material
- `bik2550` has meaningful figure and assessment-related canonical content wired into the system

### Publishing and quality gates

The project supports:

- validation through `teach validate`
- representative build coverage
- build manifests and dependency manifests
- leakage reports
- stale-resource reporting
- student-site publish bundling suitable for static deployment
- GitHub Pages-oriented student-site deployment path

## Per-Course Migration Snapshot

| Course | Repo status | Migration state | Canonical coverage snapshot | Notes |
|---|---|---|---|---|
| `ec202` | `approved` | Legacy/sample baseline | 1 concept, 2 exercises, 1 figure, 4 resources, 1 assignment, 1 lecture | Stable small reference course; not the main migration focus right now |
| `tem0052` | `draft` | Substantial partial migration | 15 concepts, 8 exercises, 2 figures, 3 assignments, 9 lectures | One of the core migration tracks; strong canonical slice but not yet fully consolidated |
| `edi3400` | `approved` | Substantial migration | 16 concepts, 14 exercises, 4 assignments, 16 lectures | Broadest course-level coverage in the repo; operationally strong even if still evolving |
| `gra4164` | `approved` | Migration complete | 16 concepts, 6 exercises, 4 assignments, 11 lectures | Complete NLP course covering text representation through transformers and prompt engineering |
| `tem00uu` | `draft` | Broad Part A migration complete | 15 concepts, 7 exercises, 8 lectures | Solid canonical slice, but still explicitly partial in scope |
| `gra4150` | `draft` | Major first canonical slice complete | 14 concepts, 8 exercises, 3 assignments, 8 lectures | Recently accelerated; now materially present rather than just staged |
| `bik2550` | `draft` | Selective canonical promotion | 17 concepts, 6 exercises, 7 figures, 1 assignment, 6 lectures | Meaningful content exists, especially around figures and Module 3, but migration looks uneven |
| `bik2551` | `approved` | Early structured course shell + selective content | 11 concepts, 6 exercises, 2 resources, 1 assignment, 4 lectures | Has a usable structure, but not yet presented as a major migration focus |

### Migration-state legend

- **Legacy/sample baseline** — small stable course surface, mainly useful as a reference or seed
- **Selective canonical promotion** — some real canonical content exists, but coverage is uneven
- **Major first canonical slice complete** — the course now has a meaningful reusable core in place
- **Substantial partial migration** — a large share of the course has been promoted, but the course is not yet fully consolidated
- **Broad \"promote first\" slice complete** — the first migration pass is broad and structurally strong, though later cleanup/polish remains
- **Broad Part A migration complete** — a major subsection is canonical, but the whole course is not yet done

## Active Constraints and Risks

The project is healthy, but not fully consolidated.

### Main constraints

- documentation has historically lagged behind implementation
- migration progress is uneven across courses
- some status/history information had grown too verbose and hard to scan
- Quarto-heavy workflows still prefer sequential builds because of shared staging behavior
- broad all-at-once test/build sweeps are less trustworthy than focused validation around the edited slice

### Practical interpretation

LearnForge is not blocked at the architecture level.

The main challenge now is operational and editorial:

- consolidate docs
- reduce drift between intent and implementation
- complete or tighten migration slices
- improve confidence and ergonomics around ongoing course promotion

## Deferred / Not In Scope Right Now

These remain intentionally deferred unless the roadmap changes:

- browser-based editing
- frontend framework rewrite / SPA architecture
- Textual TUI work
- database-backed architecture
- bulk migration tooling from `course-inbox/`
- notebook auto-conversion pipeline
- public teacher deployment target
- richer AI-assisted ingestion/publishing workflows
- automatic publishing of AI-generated content

## What Is Actually Strong Right Now

The strongest parts of the project are:

1. **Architecture coherence**
   - the stack fits the problem well
   - plain text + git + Quarto + thin Python control plane is still the right call

2. **Content model**
   - reusable learning objects are doing real work across courses
   - the system is no longer course-folder glue pretending to be reusable

3. **Build discipline**
   - validation and representative targets are in place
   - publish bundles, manifests, and leakage checks make the system auditable

4. **Migration strategy**
   - `course-inbox/` creates a clean boundary between staging and canonical content
   - promotion into reusable objects is happening in a structured way

## What Needs The Most Attention Next

The next high-value work is consolidation rather than foundational engineering.

Priority order:

1. **Documentation hygiene**
   - keep `README.md`, `IMPLEMENTATION_STATUS.md`, and `ROADMAP.md` in distinct roles
   - avoid stale summaries that undersell or misdescribe the real system

2. **Migration clarity**
   - make it easier to see which courses are:
     - staged
     - partially promoted
     - substantially migrated
     - effectively reference-quality

3. **Reference-course quality**
   - at least one course should become clearly polished end-to-end
   - that matters more than many half-finished migration slices

4. **Build/test confidence**
   - continue tightening deterministic representative checks around the real workflows you use most

## Recent Checkpoint Highlights

Recent work worth preserving at the summary level:

- student-only publish bundle and deployment path established
- resource curation workflow implemented with explicit approval states
- D3 figure path added with vendored asset and static fallback discipline
- multiple courses migrated into canonical LearnForge structures
- cross-course object reuse established
- `gra4150` received a major promotion slice, including assignment collections
- PDF default standardized on `tectonic` and verified with a representative build

## Recommended Next Step

Immediate next step: continue documentation consolidation and then tighten migration visibility.

A good follow-up would be one of:

- add a short per-course migration status table somewhere canonical
- define what qualifies a course as "migrated" vs "partial" vs "staged"
- choose one course to finish as the polished reference implementation

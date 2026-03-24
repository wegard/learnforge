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

LearnForge is a working internal teaching publication system with four approved courses in active use. The core architecture is implemented, validated, and exercised across real teaching content.

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

Four courses have completed migration and are approved:

- `edi3400` — 16 concepts, 14 exercises, 16 lectures, 4 assignments (broadest coverage)
- `gra4164` — 16 concepts, 6 exercises, 11 lectures, 4 assignments (NLP)
- `tem0052` — 16 concepts, 9 exercises, 10 lectures, 3 assignments (ML)
- `gra4150` — 14 concepts, 8 exercises, 9 lectures, 3 assignments (applied ML)

Cross-course object reuse is working at scale — concepts like `logistic-regression-classification` are shared across tem0052, gra4164, and gra4150.

Two courses remain in draft: `tem00uu` (Part A complete) and `bik2550` (selective promotion). `bik2551` is approved as a structured shell. `ec202` is archived as a test fixture.

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
| `ec202` | `archived` | Test fixture only | 1 concept, 2 exercises, 1 figure, 4 resources, 1 assignment, 1 lecture | Sample course used as a test fixture; not an active teaching course |
| `tem0052` | `approved` | Migration complete | 16 concepts, 9 exercises, 2 figures, 3 assignments, 10 lectures | Complete ML course covering regression through gradient boosting and unsupervised learning |
| `edi3400` | `approved` | Migration complete | 16 concepts, 14 exercises, 4 assignments, 16 lectures | Broadest course-level coverage; complete Python programming course from basics through SQL |
| `gra4164` | `approved` | Migration complete | 16 concepts, 6 exercises, 4 assignments, 11 lectures | Complete NLP course covering text representation through transformers and prompt engineering |
| `tem00uu` | `archived` | Broad Part A migration complete | 15 concepts, 7 exercises, 8 lectures | Experimental course, not in active development |
| `gra4150` | `approved` | Migration complete | 14 concepts, 8 exercises, 3 assignments, 9 lectures | Complete applied ML course covering AI foundations through CNNs and ethics |
| `bik2550` | `approved` | Migration complete | 17 concepts, 6 exercises, 7 figures, 1 assignment, 6 lectures | Complete executive AI-in-finance course covering Modules 1 and 3; Module 2 out of scope (guest lecturers) |
| `bik2551` | `approved` | Early structured course shell + selective content | 11 concepts, 6 exercises, 2 resources, 1 assignment, 4 lectures | Has a usable structure, but not yet presented as a major migration focus |

### Migration-state legend

- **Migration complete** — all planned content is implemented, tested, and wired into the course plan
- **Selective canonical promotion** — some real canonical content exists, but coverage is uneven
- **Broad Part A migration complete** — a major subsection is canonical, but the whole course is not yet done
- **Early structured course shell** — course structure exists with selective content, not yet a full migration
- **Test fixture only** — sample course used for test infrastructure, not active teaching content

## Active Constraints and Risks

The project is healthy. Four courses are approved and the migration pipeline is proven.

### Remaining constraints

- Quarto-heavy workflows still prefer sequential builds because of shared staging behavior
- broad all-at-once test/build sweeps are less trustworthy than focused validation around the edited slice
- 3 broken internal links remain in the `confusion-matrix-figure` build output (topic listing targets that do not exist yet)
- two courses (`tem00uu`, `bik2550`) are still in draft with partial migration

### Practical interpretation

LearnForge is not blocked at the architecture or content level. The main remaining work is completing the two draft courses and expanding to Norwegian translations where needed.

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

1. **Four approved courses with real teaching content**
   - edi3400, gra4164, tem0052, gra4150 are all migrated, tested, and approved
   - cross-course object reuse is proven and working at scale

2. **Architecture coherence**
   - plain text + git + Quarto + thin Python control plane remains the right call
   - the content model handles real courses, not just samples

3. **Build discipline**
   - 28/29 representative targets pass
   - validation, publish bundles, manifests, and leakage checks are in place

4. **Migration pipeline**
   - `course-inbox/` staging, per-course `MIGRATION_INVENTORY.md` tracking, and structured promotion are proven through repeated use

## What Needs The Most Attention Next

Priority order:

1. **Complete remaining draft courses**
   - `tem00uu` — Part A is done, assess Part B scope and promote or approve
   - `bik2550` — selective promotion is uneven, Module 2 is out of scope (guest lecturers); review checklist and push toward approved

2. **Fix remaining validation errors**
   - 3 broken internal links in `confusion-matrix-figure` (topic listing targets)
   - 1 remaining failed representative target (29th)

3. **Norwegian translations**
   - `edi3400` has the most translation warnings (31 objects missing `nb` variants)
   - translation batching strategy exists in the edi3400 migration inventory

4. **Build/test confidence**
   - continue tightening representative checks around real workflows

## Recommended Next Step

Push `tem00uu` or `bik2550` toward approved, or begin the `edi3400` Norwegian translation batch.

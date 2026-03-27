# Teaching Knowledge & Publication System — Implementation Roadmap

Status: Draft v1
Owner: Vegard
Primary users: instructor, students
Source of truth: Git repository with plain-text content

---

## 1. Product definition

Build a git-backed, markdown-first teaching publishing system that stores reusable learning objects once and compiles them into multiple outputs:

- course websites for students
- HTML slides
- PDF slides / handouts
- exercises and assignments
- curated resource pages
- teacher-only views and materials
- bilingual outputs in Norwegian and English

The system has two surfaces:

1. **Teacher control plane** in the terminal, optimized for Ghostty + shell + `nvim`
2. **Student display surface** as a Quarto-generated HTML site with PDF export paths

The core design rule is this:

> Courses and lectures do not own content. They assemble reusable learning objects.

---

## 2. Goals

### Primary goals

- Single-source authoring in markdown-like text formats (`.qmd`, `.md`, `.yml`)
- Reusable learning objects across multiple courses
- Bilingual publishing in Norwegian and English
- Strong separation between source content, build logic, and generated artifacts
- Student-facing site generated from the same source as teacher materials
- Resource curation with explicit instructor approval
- AI assistance only in draft states, never in publish states

### Secondary goals

- Good terminal ergonomics
- Searchable metadata and content
- Static-first deployment
- Reliable PDF generation
- Auditable editorial workflow
- Easy migration from existing teaching material

### Non-goals for v1

- Real-time collaborative editing
- Browser-based WYSIWYG editor
- Complex database-backed CMS
- Fine-grained student authentication / LMS replacement
- Automatic publishing of AI-generated content
- Highly dynamic app server unless static Quarto output proves insufficient

---

## 3. Guiding principles

1. **Plain text first.** All human-authored content lives in text files under version control.
2. **Objects before courses.** Concepts, examples, exercises, figures, and resources are first-class units.
3. **Compile, do not copy.** Collections reference object IDs; source text is never duplicated by hand.
4. **Static by default.** Prefer static HTML, SVG, PDF, and local assets before runtime-heavy interactivity.
5. **Approval-gated publishing.** Nothing AI-generated reaches students without explicit instructor review.
6. **Deterministic builds.** The same commit should produce the same site and exports.
7. **Minimal platform surface.** Avoid adding a database, web backend, or custom frontend framework in v1.
8. **Terminal-native authoring.** `nvim` remains the editor. The terminal interface is a control plane, not a replacement editor.
9. **Progressive enhancement before framework.** Prefer a responsive app-like shell on top of static HTML before adding heavier frontend machinery.

---

## 4. High-level architecture

```text
Git repository
├── content objects (concepts, examples, exercises, figures, resources)
├── collections (lectures, modules, assignments, reading lists)
├── course definitions
├── delivery manifests (semester-specific delivery plans)
├── schemas + validation rules
├── Quarto project + custom formats + Lua filters
├── teacher CLI/TUI
├── build scripts and CI
└── generated student/teacher artifacts
```

### Main components

#### A. Content repository
Stores all authoring source files, metadata, assets, and course assembly definitions.

#### B. Validation layer
Validates metadata, language coverage, status rules, cross-references, and output eligibility.

#### C. Build layer
Uses Quarto + profiles + filters + scripts to compile objects and collections into websites, slides, handouts, and PDFs.

#### D. Teacher control plane
Terminal application for search, indexing, validation, build orchestration, preview, approval workflows, and opening files in `nvim`.

#### E. Student display site
Quarto-generated HTML site with navigation, search, listings, language switching, and links to exported PDFs.

#### F. Resource curation pipeline
Maintains candidate resources, approval state, annotations, freshness review dates, and publishing eligibility.

#### G. AI assistance layer
Generates draft translations, summaries, tags, and candidate resources into explicit draft states only.

---

## 5. Core technical decisions

These should be locked before implementation starts.

### 5.1 Source of truth
Use **Git** as the system of record.

- Source files tracked in git
- Generated site and build artifacts excluded from source control, except when intentionally versioning `_freeze` outputs
- Approval actions recorded as normal commits

### 5.2 Publishing engine
Use **Quarto** as the document compiler and project orchestrator.

Use Quarto for:

- websites
- Reveal.js slides
- HTML/PDF/Word exports
- project profiles for `student/teacher` and `en/nb`
- listings and site search
- conditional content
- custom formats and Lua filters
- reproducible computational documents with freeze

### 5.3 Terminal stack
Use **Python** for the teacher control plane.

Recommended structure:

- CLI: `Typer`
- Validation and schema models: `Pydantic`
- Optional later TUI: `Textual`
- Search/indexing: filesystem scan + generated JSON index in v1

Reason:

- easy integration with Quarto and local scripts
- good YAML/JSON tooling
- low-friction packaging
- easy process control for `quarto render`, `nvim`, `ripgrep`, PDF export, checks

### 5.4 Editor model
Do not build a custom editor.

- Author content in `nvim`
- Launch `$EDITOR` from the CLI
- Use the teacher interface for navigation, validation, and build orchestration
- Browser-based instructor views are preview/review surfaces only; editing remains in `nvim`

### 5.5 Data storage
Use **filesystem + YAML metadata + generated JSON index** in v1.

Do **not** add a database in v1.

Revisit only if at least one of these becomes true:

- object count grows beyond what fast local indexing can handle
- approval workflows become multi-user and concurrent
- complex query latency becomes a real problem

### 5.6 Language policy
Use one canonical object ID across languages.

- English file: `note.en.qmd`
- Norwegian file: `note.nb.qmd`
- Shared metadata: `meta.yml`

Lock the Norwegian variant now:

- `nb` for Bokmål
- `nn` for Nynorsk

Do not mix them.

### 5.7 Interactivity policy
Use a three-level figure strategy:

1. static SVG/PDF for most figures
2. object-local JS for light/medium interactivity
3. D3 for cases that genuinely require advanced responsive interaction

Every interactive figure must have a static fallback.

### 5.8 AI policy
AI may:

- suggest tags
- draft translations
- draft summaries
- propose related objects
- suggest candidate resources

AI may not:

- approve content
- publish content
- overwrite approved content without preserving history
- modify solution sets or teacher-only materials silently

---

## 6. Repository layout

```text
teaching/
├── _quarto.yml
├── _variables.yml
├── Makefile
├── pyproject.toml
├── README.md
├── ROADMAP.md
├── .pre-commit-config.yaml
├── .gitignore
│
├── content/
│   ├── concepts/
│   │   └── iv-intuition/
│   │       ├── meta.yml
│   │       ├── note.en.qmd
│   │       ├── note.nb.qmd
│   │       └── assets/
│   ├── examples/
│   ├── exercises/
│   ├── figures/
│   └── resources/
│
├── collections/
│   ├── lectures/
│   ├── modules/
│   ├── assignments/
│   └── reading-lists/
│
├── courses/
│   ├── ec202/
│   │   ├── course.yml
│   │   ├── syllabus.en.qmd
│   │   ├── syllabus.nb.qmd
│   │   └── plan.yml
│   └── ds401/
│
├── deliveries/
│   ├── tem0052-spring-2026.yml
│   └── ...
│
├── schemas/
│   ├── base-object.schema.json
│   ├── concept.schema.json
│   ├── exercise.schema.json
│   ├── figure.schema.json
│   ├── resource.schema.json
│   └── collection.schema.json
│
├── formats/
│   ├── teacher-note/
│   ├── student-handout/
│   ├── exercise-sheet/
│   └── lecture-slides/
│
├── filters/
│   ├── include-object.lua
│   ├── visibility.lua
│   ├── language-switch.lua
│   ├── resource-card.lua
│   └── exercise-assembler.lua
│
├── templates/
│   ├── meta.yml.j2
│   ├── concept.en.qmd.j2
│   ├── concept.nb.qmd.j2
│   └── resource-note.qmd.j2
│
├── app/
│   ├── cli.py
│   ├── config.py
│   ├── indexer.py
│   ├── validator.py
│   ├── build.py
│   ├── search.py
│   ├── approval.py
│   └── tui/
│
├── scripts/
│   ├── bootstrap.sh
│   ├── render.sh
│   ├── export_pdf.sh
│   ├── reindex.py
│   └── migrate_legacy.py
│
├── tests/
│   ├── test_schema.py
│   ├── test_builds.py
│   ├── test_cli.py
│   ├── test_filters.py
│   └── fixtures/
│
├── build/
│   ├── index/
│   ├── reports/
│   └── exports/
│
└── _freeze/
```

---

## 7. Content model

## 7.1 Object types

Implement these object types first:

- `concept`
- `exercise`
- `figure`
- `resource`
- `collection`

Delay until later:

- `example`
- `assignment-template`
- `exam-question`
- `dataset`
- `glossary-term`

## 7.2 Base metadata schema

Every object needs a `meta.yml` with a common base schema.

```yaml
id: iv-intuition
kind: concept
status: approved
visibility: student
languages: [en, nb]
title:
  en: Instrumental Variables Intuition
  nb: Intuisjon for instrumentvariabler
courses: [ec202, ds401]
topics: [causal-inference, endogeneity, identification]
tags: [iv, regression, econometrics]
level: intermediate
prerequisites: [linear-regression, omitted-variable-bias]
related: [iv-assumptions, two-stage-least-squares]
outputs: [html, pdf, revealjs, handout]
owners: [vegard]
updated: 2026-03-18
translation_status:
  en: approved
  nb: approved
ai:
  generated_fields: []
```

## 7.3 Status model

Use explicit lifecycle states.

### Content status

- `draft`
- `review`
- `approved`
- `published`
- `archived`

### Translation status

- `missing`
- `machine_draft`
- `edited`
- `approved`

### Resource status

- `candidate`
- `reviewed`
- `approved`
- `published`
- `archived`

## 7.4 Visibility model

- `private`
- `teacher`
- `student`
- `public`

Rules:

- `private` and `teacher` never appear in student builds
- solution keys default to `teacher`
- `student` means student-visible within the site/export context
- `public` is only used if there is a separate external publishing mode later

## 7.5 Collection model

Collections assemble objects by ID.

Example:

```yaml
id: lecture-04
kind: collection
collection_kind: lecture
status: approved
visibility: student
languages: [en, nb]
courses: [ec202]
title:
  en: Lecture 4 — Endogeneity and IV
  nb: Forelesning 4 — Endogenitet og IV
items:
  - iv-intuition
  - omitted-variable-bias-review
  - iv-dag-figure
  - ex-iv-concept-check
outputs: [html, revealjs, pdf, handout]
```

## 7.6 Resource schema

```yaml
id: angrist-podcast-iv
kind: resource
resource_kind: podcast
status: approved
visibility: student
title:
  en: Instrumental Variables Episode
  nb: Episode om instrumentvariabler
authors: [Joshua Angrist]
published_on: 2025-11-04
url: https://example.org/resource
courses: [ec202]
topics: [causal-inference, iv]
difficulty: introductory
estimated_time_minutes: 32
why_selected:
  en: Gives students an intuitive narrative before formal treatment.
  nb: Gir studentene en intuitiv fortelling før formell behandling.
instructor_note:
  en: Assign before lecture 4.
  nb: Tildel før forelesning 4.
freshness: evergreen
review_after: 2027-01-01
approved_by: vegard
approved_on: 2026-03-18
```

---

## 8. Build matrix

Treat builds as the Cartesian product of:

```text
artifact = object_or_collection × language × audience × format
```

### Supported audiences

- `student`
- `teacher`

### Supported languages

- `en`
- `nb` or `nn`

### Supported formats for v1

- `html`
- `pdf`
- `revealjs`
- `handout`
- `exercise-sheet`

### Example targets

- `lecture-04 × nb × student × revealjs`
- `lecture-04 × en × teacher × pdf`
- `ec202 × nb × student × html`
- `assignment-02 × en × teacher × exercise-sheet`

---

## 9. Build profiles and configuration

Use Quarto project profiles for audience and language.

### Required profiles

- `student`
- `teacher`
- `en`
- `nb`

Profiles can be composed at render time.

Examples:

```bash
quarto render courses/ec202 --profile student,en
quarto render collections/lectures/lecture-04 --profile teacher,nb
```

### Configuration split

- `_quarto.yml` for shared configuration
- `_quarto-student.yml` or profile-specific config for student-specific options
- `_quarto-teacher.yml` for teacher-specific options
- `_quarto-en.yml` and `_quarto-nb.yml` for language-specific options

### Conditional content rules

Use conditional content for:

- hiding teacher notes from student outputs
- switching explanation depth by audience
- format-specific blocks for HTML vs PDF vs slides

### Freeze policy

Use Quarto `freeze: auto` for computational documents once the build is stable.

---

## 10. Teacher interface specification

## 10.1 v1 CLI command surface

```bash
teach init
teach new concept iv-intuition
teach new exercise ex-iv-concept-check
teach search "instrumental variables"
teach list concepts --course ec202 --lang nb
teach open iv-intuition
teach validate
teach build lecture-04 --audience student --lang en --format revealjs
teach build ec202 --audience student --lang nb --format html
teach approve iv-intuition --field translation_status.nb
teach approve-resource angrist-podcast-iv
teach stale resources
teach stale translations
teach doctor
teach reindex
teach report coverage
teach new-delivery tem0052 --term spring-2026 --lang en --start 2026-01-20
teach delivery-status tem0052-spring-2026
teach deliver tem0052-spring-2026 --ready-only
teach deliver tem0052-spring-2026 --lecture tem0052-lecture-03
```

## 10.2 CLI responsibilities

- create new objects from templates
- index metadata and relationships
- open files in `nvim`
- validate schema and references
- render Quarto targets
- generate reports
- manage approval flags
- identify stale resources and missing translations
- generate migration and coverage summaries

## 10.3 CLI implementation notes

### First implementation

Build a thin CLI only.

Do not start with a full TUI.

### Later optional TUI

After the CLI is stable, add a TUI with:

- left pane: filtered object list
- center pane: metadata summary / preview
- right pane: build status / diagnostics
- keybindings for open, build, approve, preview

The TUI is phase-later work, not MVP-critical.

## 10.4 Teacher UX requirements

- must work entirely from terminal
- must be fast on large repositories
- must degrade gracefully when Quarto render fails
- must surface broken references and missing assets clearly
- must allow jumping from validation error to file path + line context where possible

---

## 11. Student interface specification

## 11.1 Information architecture

The student site needs two navigation modes.

### Course-centric navigation

Students can browse:

- course landing page
- syllabus
- modules
- lectures
- assignments
- readings/resources

### Concept-centric navigation

Students can browse:

- concept pages
- prerequisite graphs
- related exercises
- related figures
- related resources
- “used in these courses” listings

## 11.2 Required student features

- full-text search
- language switch between English and Norwegian
- stable page URLs
- clear relation links between concepts/exercises/resources
- export links to PDF where appropriate
- responsive HTML pages
- resource listings by topic and course
- static fallback for interactive figures

## 11.3 Student site pages

Implement these first:

- home
- course page
- lecture page
- concept page
- exercise page
- resource page
- topic listing page
- search-enabled global navigation

## 11.4 Student safety / visibility rules

- teacher notes never render into student builds
- solution keys hidden from student builds
- draft resources not shown
- non-approved translation variants not shown by default

## 11.5 Responsive app-shell strategy

- student HTML should feel like one coherent responsive web app rather than a loose set of document pages
- keep pages static, directly linkable, and audience-scoped; do not require a SPA router
- use one shared HTML shell plus small local CSS/JS assets for navigation, search, and view switching
- prefer progressive enhancement over client-side stateful application logic
- preserve stable URLs and direct-build targets for course, lecture, object, and listing pages

## 11.6 Instructor preview/review surface

- teacher workflow remains terminal-first
- browser instructor mode exists only for preview/review of generated teacher HTML
- no browser-based editing, approval actions, or metadata mutation in v1
- teacher preview builds are local/private by default
- when both student and teacher HTML targets exist, the UI should offer a quick switch between them
- deployment for v1 should support student mode only without requiring teacher artifacts to be published

---

## 12. Figure and media system

## 12.1 Figure object structure

```text
content/figures/ovb-sim/
├── meta.yml
├── figure.svg
├── figure.pdf
├── figure.js
├── data/
└── note.en.qmd
```

## 12.2 Figure rules

- every figure gets a stable ID
- every interactive figure gets a static fallback
- assets stored locally, not pulled from CDN at render time when avoidable
- source data stored with the figure when feasible
- captions and notes localized by language

## 12.3 Interactivity roadmap

### v1

- static SVG/PDF
- embedded local JS only when necessary

### v1.1

- D3-based figures through object-local `figure.js` plus optional `data/`
- shared helper utilities only after repeated reuse justifies them

### later

- reusable figure modules and export helpers
- optional Observable experiments only if they solve a specific problem better than local D3

## 12.4 PDF/export policy

PDF output must never depend on runtime browser state.

If an interactive figure exists:

- include interactive version in HTML
- include static fallback in PDF and print modes

---

## 13. Exercise and assessment pipeline

## 13.1 Exercise object model

Each exercise should include:

- linked concepts
- difficulty
- type
- estimated time
- course suitability
- language coverage
- solution visibility
- output eligibility

Example:

```yaml
id: ex-iv-concept-check
kind: exercise
status: approved
visibility: student
title:
  en: IV intuition check
  nb: Sjekk av IV-intuisjon
exercise_type: conceptual
difficulty: easy
estimated_time_minutes: 8
concepts: [iv-intuition]
courses: [ec202]
solution_visibility: teacher
outputs: [html, pdf, exercise-sheet]
```

## 13.2 Exercise outputs

- standalone exercise page
- weekly problem sheet
- in-class activity handout
- teacher solution sheet
- slide fragment or lecture appendix

## 13.3 Assembly rules

- collections can include exercises directly by ID
- assignment collections can filter by metadata
- solution files must compile separately from student sheets
- no student build should ever include solution content accidentally

---

## 14. Resource curation system

## 14.1 Resource ingestion workflow

### Sources

- academic papers
- news articles
- blogs
- podcasts
- videos
- books / book chapters

### Workflow

1. capture candidate
2. enrich metadata
3. add summary + why selected
4. mark course/topic fit
5. instructor review
6. approve
7. publish to site
8. re-review when stale

## 14.2 Resource review rules

- every student-visible resource must have `approved_by` and `approved_on`
- every time-sensitive resource gets `review_after`
- every resource gets at least one course or topic link
- AI-suggested resources start as `candidate`

## 14.3 Resource page fields

Display on student site:

- title
- type
- authors/source
- date
- topic tags
- why this matters
- expected time cost
- link out

Display only for teacher builds:

- instructor note
- approval history
- stale flag
- AI provenance if applicable

---

## 15. AI assistance plan

## 15.1 Allowed AI workflows in v1

- translation draft generation for missing language variants
- resource candidate discovery into inbox format
- metadata suggestion for tags, topics, related objects
- summary drafts for resources
- exercise variant generation into draft state only

## 15.2 AI output storage

Store AI outputs explicitly in metadata or sidecar files.

Example:

```yaml
ai:
  source: openai
  created_on: 2026-03-18
  generated_fields:
    - summary.en
    - tags
  review_state: pending
```

## 15.3 AI approval protocol

- AI writes only to draft fields or sidecar draft files
- human review required before state transition to `approved`
- approvals recorded in git
- rejected AI drafts preserved or intentionally deleted with traceable commit history

## 15.4 AI guardrails

- do not auto-publish
- do not auto-approve
- do not delete human edits
- do not create hidden student-visible changes
- do not infer citations or bibliographic facts without verification

---

## 16. Validation and quality gates

Validation must be a first-class subsystem.

## 16.1 Required checks

### Schema checks

- required fields present
- values in allowed enums
- date formats valid
- language codes valid

### Cross-reference checks

- referenced IDs exist
- prerequisites exist
- related objects exist
- collection items exist
- course links exist

### Asset checks

- referenced images/files exist
- figure fallbacks exist when interactivity exists
- PDFs exist where promised

### Editorial checks

- approved student content has at least one approved language variant
- published resources have instructor approval metadata
- teacher-only content is not included in student output manifests
- missing translations are surfaced in reports

### Build checks

- Quarto render succeeds for representative targets
- no broken site links
- no unresolved includes/shortcodes/filters
- PDF export succeeds for required core outputs

## 16.2 Validation command outputs

- console report
- machine-readable JSON report
- build summary saved under `build/reports/`

## 16.3 CI gates

Merge should fail when:

- schema invalid
- required references broken
- required render target fails
- student build leaks teacher-only content
- tests fail

---

## 17. Testing strategy

## 17.1 Unit tests

- schema parsing
- status transitions
- translation state rules
- build target resolution
- CLI argument parsing
- report generation

## 17.2 Integration tests

- render a sample concept in `student,en,html`
- render a sample lecture in `teacher,nb,revealjs`
- render an exercise sheet with solutions excluded
- render resource listings by topic and course

## 17.3 Snapshot tests

Use snapshots for:

- generated front matter
- index JSON
- listing JSON
- selected HTML fragments after filters

## 17.4 Manual acceptance checks

- open/edit/build from Ghostty workflow
- view image-heavy pages in terminal preview if implemented
- confirm language switching on site
- confirm PDF exports keep layout integrity

---

## 18. Delivery plan by phase

Each phase below has deliverables, work packages, and exit criteria.

---

## Phase 0 — Foundation and decision lock

### Deliverables

- repo initialized
- base project docs written
- technology decisions locked
- naming conventions locked
- language policy locked

### Work packages

- create repository
- add `README.md`, `ROADMAP.md`, `LICENSE` if desired
- define object naming convention and slug rules
- choose Norwegian language code (`nb` or `nn`)
- decide Python package structure
- add `.editorconfig`, `.gitignore`, pre-commit hooks
- add `pyproject.toml`
- add CI skeleton

### Exit criteria

- repo boots on a fresh machine
- conventions written down
- no unresolved foundational design questions remain

---

## Phase 1 — Schema and validation core

### Deliverables

- object schemas
- metadata parser
- validation engine
- `teach validate`

### Work packages

- define base schema JSON + Pydantic models
- define per-object schemas
- implement YAML parser with rich error output
- implement reference resolution
- implement status rule validation
- implement translation coverage report
- add schema fixtures and tests

### Exit criteria

- invalid content fails loudly
- valid sample repository passes cleanly
- reports identify missing translations, assets, and broken references

---

## Phase 2 — Quarto project baseline

### Deliverables

- working Quarto project
- shared config
- student/teacher and language profiles
- first renderable sample objects

### Work packages

- create `_quarto.yml`
- configure site output directory
- create initial profiles
- configure document language handling
- add theme and navigation skeleton
- render a concept page in both languages
- render a lecture collection into slides and PDF
- enable site search

### Exit criteria

- one sample course builds in `student,en,html`
- one sample lecture builds in `teacher,nb,revealjs`
- basic PDF export works

---

## Phase 3 — Collection assembly system

### Deliverables

- collections resolved from object IDs
- course/module/lecture assembly pipeline
- listings generated from content metadata

### Work packages

- define collection schema
- implement object resolver
- implement collection expansion logic
- create course config format
- generate course pages from plan files
- generate topic listings and resource listings
- implement related-content blocks

### Exit criteria

- collections compile without manual copy-paste
- changing one object updates every dependent collection build

---

## Phase 4 — Teacher CLI MVP

### Deliverables

- installable CLI
- object scaffolding commands
- search/open/build/validate commands
- basic approval commands

### Work packages

- implement `teach init`
- implement `teach new`
- implement `teach search`
- implement `teach open`
- implement `teach build`
- implement `teach validate`
- implement `teach approve`
- implement `teach stale`
- implement `teach reindex`
- add shell completion if straightforward

### Exit criteria

- instructor can perform daily workflow without touching raw build scripts
- build and validation errors are readable and actionable

---

## Phase 5 — Student site MVP

### Deliverables

- course pages
- concept pages
- resource pages
- search-enabled navigation
- language switch

### Work packages

- implement course landing templates
- implement concept template
- implement resource card template
- configure listings for topics/resources
- add breadcrumbs and related-links sections
- add export links where relevant
- ensure teacher-only content excluded

### Exit criteria

- students can navigate by course and concept
- search returns useful results
- bilingual content renders cleanly

---

## Phase 6 — Exercise compiler and teacher/student separation

### Deliverables

- exercise schema
- exercise pages
- assignment/problem sheet compilation
- teacher solution builds

### Work packages

- finalize exercise metadata
- implement solution storage convention
- build exercise-sheet format
- build teacher solution format
- add filters to exclude solutions from student outputs
- test leakage prevention

### Exit criteria

- one assignment sheet and one solution sheet compile from same source set
- no student artifact contains teacher-only content

---

## Phase 7 — Figure pipeline and interactivity

### Deliverables

- figure schema
- asset conventions
- static fallback rules
- first interactive figure path

### Work packages

- define figure object model
- create static figure templates
- add first D3 figure experiment
- add packaging/documentation rule for object-local JS and D3 figures
- document HTML/PDF fallback policy
- test print/PDF behavior

### Exit criteria

- figure objects can be reused across pages and slides
- interactive figures degrade correctly in PDF output

---

## Phase 8 — Resource curation workflow

### Deliverables

- resource candidate inbox
- approval workflow
- stale review reporting
- student-facing resource listings

### Work packages

- build `resource` object templates
- implement `candidate -> reviewed -> approved -> published` transitions
- implement `teach stale resources`
- implement resource listing pages
- add topic/course filters
- add approval metadata checks

### Exit criteria

- resources are traceable, reviewable, and publishable without manual page editing

---

## Phase 9 — AI-assisted draft workflows

### Deliverables

- AI draft import conventions
- translation draft workflow
- metadata suggestion workflow
- resource suggestion inbox

### Work packages

- define sidecar or embedded AI provenance schema
- create CLI entry points for AI draft ingestion
- separate draft fields from approved fields
- generate review reports for AI-created drafts
- test no unreviewed AI content reaches published outputs

### Exit criteria

- AI is useful but structurally constrained
- review burden is manageable
- audit trail exists

---

## Phase 10 — CI/CD and publishing

### Deliverables

- automated validation
- preview builds on pull requests
- release build pipeline
- deployment target configured

### Work packages

- create CI jobs for lint, tests, validation, sample builds
- create publish job for student site
- create artifact export job for PDFs/slides if needed
- add broken link checks
- add dependency caching for faster builds
- define release tag or branch rules

### Exit criteria

- every merge is validated
- deployment is reproducible
- PDFs and site builds can be regenerated from clean state

---

## Phase 11 — Migration of existing material

### Deliverables

- migration inventory
- import scripts/templates
- first real course migrated

### Work packages

- inventory existing notes/slides/assignments/resources
- map legacy files to object types
- split monolithic lecture notes into reusable objects
- normalize titles, tags, and IDs
- backfill metadata
- backfill translations gradually
- identify content worth deleting rather than migrating

### Exit criteria

- one real course runs end-to-end in the new system
- reused objects appear in at least two course contexts

---

## Phase 11.5 — Delivery manifests

### Deliverables

- delivery manifest schema and data model
- semester-specific delivery planning
- classroom readiness tracking
- delivery build pipeline
- `teach deliver`, `teach delivery-status`, `teach new-delivery`

### Work packages

- define delivery manifest schema (`DeliveryManifest`, `DeliveryLecture`, `DeliveryAssignment`)
- add `deliveries/` directory for manifest YAML files
- implement manifest loading and validation in the indexer/validator
- add `DeliveryContext` to the assembly pipeline for per-lecture overrides (additions, removals, date injection, title override)
- implement `teach new-delivery` to scaffold manifests from course plans
- implement `teach delivery-status` for readiness overview
- implement `teach deliver` to build all lectures for a delivery manifest
- delivery build output to `build/deliveries/` (gitignored, separate from ad-hoc builds)
- delivery report generation

### Exit criteria

- instructor can scaffold a delivery manifest from an existing course plan
- delivery status shows per-lecture readiness with warnings for unapproved content
- `teach deliver --ready-only` builds all ready lectures with date injection
- all existing tests continue to pass

---

## Phase 12 — Hardening and documentation

### Deliverables

- contributor docs
- operator docs
- recovery procedures
- stable v1 release criteria

### Work packages

- write authoring guide
- write metadata guide
- write style guide for titles/tags/IDs
- write runbook for common failures
- document backup and restore
- document AI review policy
- document translation workflow

### Exit criteria

- system is usable without relying on undocumented habits
- failures are diagnosable
- v1 can be considered operational

---

## 19. Priority ordering

## Must-have before first real use

- schema validation
- Quarto build profiles
- student/teacher visibility separation
- object IDs and collection assembly
- concept/exercise/resource object types
- teacher CLI for search/open/build/validate
- bilingual file convention
- site search and navigation

## Should-have soon after

- stale resource reporting
- translation coverage reports
- exercise sheet compilation
- teacher solution builds
- interactive figure support with fallbacks
- CI preview builds

## Later

- full Textual TUI
- richer prerequisite graph views
- sophisticated AI workflows
- LMS integration
- analytics
- external public publishing mode

## 19.1 Next staged implementation strategy

The next web-surface slice should be implemented in narrow stages.

Each stage keeps these anti-bloat constraints:

- no browser-based editor
- no database
- no web backend
- no custom frontend framework unless the static approach demonstrably fails
- no new shared JS/CSS layer unless it clearly replaces existing duplication

### Stage 1 - Shell extraction and cleanup

- move the current inline student shell styling/script into shared local assets or templates
- keep Quarto + assembly as the rendering model
- keep the audience/language build matrix unchanged
- remove duplication before adding any new UI behavior

Exit criteria:

- current student pages render through one shared shell path
- no content-model or build-target changes are required
- the site remains fast and fully static

### Stage 2 - Responsive student app shell

- redesign the student HTML shell for mobile and desktop use
- improve navigation, page framing, listings, and search placement so the site feels app-like
- keep page bodies server-rendered/static and URL-addressable
- preserve PDF/export links and language switching

Exit criteria:

- home, course, lecture, concept, exercise, resource, and listing pages share a coherent responsive shell
- stable URLs remain unchanged
- no teacher-only content leaks into student output

### Stage 3 - Instructor preview/review mode

- add a teacher HTML shell that reuses the student shell structure where possible
- expose instructor-only preview affordances such as quick view switching and local context panels
- add student/instructor switch links where counterpart pages exist
- keep editing and approvals in the terminal/CLI

Exit criteria:

- instructor can switch quickly between student and teacher views while authoring in `nvim`
- teacher HTML remains a preview/review surface, not an editing surface
- teacher outputs stay local/private by default

### Stage 4 - Student-only deployment path

- define the student HTML export root as the first-class publish artifact
- add a reproducible publish path for student mode only
- keep teacher HTML, slides, and solution artifacts outside the public deployment by default
- document the release boundary clearly

Exit criteria:

- a public deployment can be produced from a clean student-only build
- teacher artifacts are excluded from the published site by default
- deployment remains static and reproducible

### Stage 5 - D3 figure path

- formalize D3 as the preferred advanced figure path using object-local assets
- keep `figure.svg` and `figure.pdf` mandatory when interactivity exists
- add shared D3 helpers only after at least two figures demonstrate real reuse
- test mobile responsiveness and print/PDF fallback explicitly

Exit criteria:

- at least one canonical D3 figure ships cleanly in HTML
- the same figure still degrades correctly in PDF/print modes
- figure interactivity does not introduce external CDN/runtime dependencies

---

## 20. Immediate implementation backlog

This is the concrete order for the first build cycle.

1. Create repo skeleton
2. Lock naming convention for IDs and folders
3. Choose `nb` or `nn`
4. Write base object schema
5. Write schemas for `concept`, `exercise`, `figure`, `resource`, `collection`
6. Create 5 sample objects by hand
7. Build schema validation command
8. Create minimal Quarto project config
9. Render one concept page in English
10. Render the same concept page in Norwegian
11. Add student and teacher profiles
12. Add one sample lecture collection
13. Render that lecture as Reveal.js slides
14. Export lecture handout/PDF
15. Build one course landing page
16. Add Quarto site search
17. Implement `teach new`
18. Implement `teach search`
19. Implement `teach open`
20. Implement `teach validate`
21. Implement `teach build`
22. Add one resource listing page
23. Add one exercise sheet build
24. Add teacher-only solution separation
25. Add CI validation for schema + representative renders

---

## 21. Definition of done for v1

v1 is done when all of the following are true:

- one real course runs entirely from the new repository
- content is authored and edited only in plain text files
- at least four object types are operational: concept, exercise, figure, resource
- course pages, lecture pages, and concept pages build from reusable objects
- student/teacher visibility separation is enforced automatically
- English and Norwegian outputs can both be built
- one lecture builds to HTML slides and PDF
- one assignment builds to student sheet and teacher solution sheet
- resource curation supports candidate, approved, published states
- AI-assisted drafts exist only behind approval gates
- validation and CI catch broken references and leakage risks

---

## 22. Risks and mitigations

## Risk: metadata complexity becomes burdensome

Mitigation:

- keep base schema small
- scaffold templates with defaults
- automate repeated metadata generation

## Risk: bilingual maintenance doubles editorial work

Mitigation:

- treat translation coverage as an explicit reportable metric
- allow missing translations in drafts, not in publish-critical content
- use AI only for draft acceleration

## Risk: Quarto customization becomes too clever

Mitigation:

- keep custom filters small and well-tested
- prefer simple content conventions over magic transforms
- add custom formats only where reuse is real

## Risk: interactivity breaks PDF workflows

Mitigation:

- static fallback mandatory
- HTML-first interactivity, print-safe PDF path

## Risk: student builds accidentally expose teacher content

Mitigation:

- visibility filter tested in CI
- teacher-only content defaults to hidden
- maintain representative leakage tests

## Risk: resource list becomes noisy or stale

Mitigation:

- approval state required
- stale review dates required for time-sensitive content
- reject auto-publishing

## Risk: migration effort becomes endless

Mitigation:

- migrate one real course first
- delete or archive weak legacy content
- split monoliths only when reuse value is clear

---

## 23. Operational conventions

## File naming

- use lowercase kebab-case IDs
- folder name equals object ID
- no spaces in file or directory names

## Content conventions

- one object per folder
- one shared `meta.yml` per object
- one content file per language per object
- assets live inside the object folder unless truly shared

## Editorial conventions

- never edit generated files manually
- every approval action is committed
- draft state is the default for new content
- publish state is only for material intended for live builds

## Build conventions

- student builds are default-deny for teacher/private content
- representative build targets must stay fast and reliable
- use `_freeze` where computational re-renders are expensive

---

## 24. Suggested internal documentation set

Create these documents after Phase 2 or 3:

- `docs/AUTHORING.md`
- `docs/METADATA.md`
- `docs/BUILD.md`
- `docs/CLI.md`
- `docs/TRANSLATION.md`
- `docs/RESOURCES.md`
- `docs/AI_POLICY.md`
- `docs/MIGRATION.md`
- `docs/TROUBLESHOOTING.md`

---

## 25. Open questions to resolve before hardening

- Which Norwegian standard: `nb` or `nn`?
- Should resources use embedded notes or external metadata-only entries for some types?
- Should lectures be fully generated from collections, or can some remain hand-curated wrappers?
- Do you want one combined site with language switchers, or separate per-language builds?
- If private publishing is ever needed later, should it reuse teacher HTML preview outputs or stay limited to selected artifacts?
- Which static deployment target will host the public student site?
- How much of existing material is worth migrating versus rewriting?

---

## 26. Recommended first milestone

The first milestone should be narrow:

> Build one real course slice end-to-end with 8–12 concept objects, 6–10 exercises, 5–8 resources, one lecture collection, bilingual output, one student site build, one slide build, and one teacher solution build.

That milestone will expose nearly every architectural flaw early, before the system expands.

---

## 27. Tooling references

Official documentation useful during implementation:

- [Quarto](https://quarto.org/)
- [Quarto project profiles](https://quarto.org/docs/projects/profiles.html)
- [Quarto websites](https://quarto.org/docs/websites/)
- [Quarto website search](https://quarto.org/docs/websites/website-search.html)
- [Quarto document language](https://quarto.org/docs/authoring/language.html)
- [Quarto conditional content](https://quarto.org/docs/authoring/conditional.html)
- [Quarto listings](https://quarto.org/docs/websites/website-listings.html)
- [Quarto interactivity](https://quarto.org/docs/interactive/)
- [Quarto Observable JS](https://quarto.org/docs/interactive/ojs/)
- [Quarto custom formats](https://quarto.org/docs/extensions/formats.html)
- [Quarto extensions](https://quarto.org/docs/extensions/creating.html)
- [Quarto managing execution / freeze](https://quarto.org/docs/projects/code-execution.html)
- [Quarto Reveal.js presentations](https://quarto.org/docs/presentations/revealjs/)
- [Ghostty features](https://ghostty.org/docs/features)
- [Typer](https://typer.tiangolo.com/)
- [Textual](https://textual.textualize.io/)
- [Pydantic](https://docs.pydantic.dev/latest/)

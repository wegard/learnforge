# Delivery Manifests — Specification

> **Status:** Proposed
> **Author:** Astra
> **Date:** 2026-03-26
> **Scope:** New subsystem for course-instance delivery planning and classroom readiness tracking

---

## 1. Problem statement

LearnForge's architecture says "objects before courses" — content objects are reusable, and courses assemble them. In practice, however, three problems have emerged:

1. **Content is too course-specific.** Collections are named `tem0052-lecture-01` and carry course IDs in their metadata. The reusable objects (concepts, exercises, figures) exist, but the *assembly layer* (collections) is tightly coupled to specific courses. There is no clean way to reuse the same concept sequence in a different course without creating a new collection.

2. **No "classroom-ready" status.** The `status` field (draft → review → approved → published) tracks editorial quality of content. But there is no way to say "Lecture 3 for Spring 2026 is ready to deliver in the classroom" — meaning all referenced content is approved, outputs are built, dates are set, and any semester-specific adjustments are applied.

3. **Build artifacts leak into the repo.** Finalized lecture packages (with dates, semester-specific ordering, compiled slides) should not live on GitHub. The repo holds source content and course definitions. The *parameterized, semester-specific assembly* is a build-time concern.

---

## 2. Design overview

Introduce **delivery manifests** — YAML files that define how a course is delivered in a specific semester. A delivery manifest is the bridge between reusable content (objects + collections) and a concrete classroom schedule.

### Key concepts

- **Course definition** (`courses/<id>/course.yml` + `plan.yml`): the *canonical* course — what it covers, which collections and assignments it includes. Lives in git. Semester-agnostic.
- **Delivery manifest** (`deliveries/<course-id>-<term>.yml`): a *specific offering* of a course — Spring 2026, Fall 2026, etc. Parameterizes the course plan with dates, lecture-by-lecture readiness, and any per-session overrides. Lives in git (it's just YAML planning data), but the *build output* it produces does not.
- **Delivery build**: `teach deliver <manifest>` compiles all lectures for a delivery manifest, producing the full classroom package. Output goes to `build/deliveries/` (gitignored).

### What changes, what stays

| Aspect | Before | After |
|--------|--------|-------|
| Collection naming | `tem0052-lecture-01` (course-bound) | Collections can be course-agnostic (e.g., `ml-foundations-lecture`) or course-specific — no forced convention |
| Semester dates | Not tracked | Per-lecture date in delivery manifest |
| Classroom readiness | Not tracked | Per-lecture `ready` flag in delivery manifest |
| Course plan | `plan.yml` lists lecture IDs | `plan.yml` remains the canonical lecture sequence; delivery manifest can override or reorder |
| Build output | `build/exports/` (gitignored) | `build/deliveries/<manifest-id>/` (gitignored) — separate from ad-hoc builds |
| `courses` field on objects | Structural (used for assembly) | Informational/tagging only — assembly is driven by collections and delivery manifests |

---

## 3. Data model

### 3.1 Delivery manifest schema

Location: `deliveries/<course-id>-<term>.yml`

```yaml
# deliveries/tem0052-spring-2026.yml
id: tem0052-spring-2026
course: tem0052
term: spring-2026
language: en               # primary delivery language
status: active             # active | archived
created: 2026-01-15
updated: 2026-03-26

# Optional: override the course plan.yml lecture sequence
# If omitted, uses the lecture order from plan.yml
lectures:
  - lecture: tem0052-lecture-01
    date: 2026-01-20
    ready: true
    title_override: null    # optional: override collection title for this delivery
    notes: "First class, intro + logistics"

  - lecture: tem0052-lecture-02
    date: 2026-01-27
    ready: true
    notes: null

  - lecture: tem0052-lecture-03
    date: 2026-02-03
    ready: false            # not yet prepped
    notes: "Need to update cross-validation example"

  - lecture: tem0052-lecture-04
    date: 2026-02-10
    ready: false
    additions: []           # optional: extra content IDs to append for this session only
    removals: []            # optional: content IDs to skip from the collection for this session

# Optional: override assignment sequence
assignments:
  - assignment: tem0052-assignment-01
    due_date: 2026-02-14
    ready: true

  - assignment: tem0052-assignment-02
    due_date: 2026-03-07
    ready: false

# Formats to build for each lecture (overrides per-collection outputs)
default_formats:
  - html
  - revealjs
  - pdf
  - handout

# Audiences to build
default_audiences:
  - student
  - teacher
```

### 3.2 Pydantic model

```python
class DeliveryLecture(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lecture: str                          # collection ID
    date: date
    ready: bool = False
    title_override: str | None = None
    notes: str | None = None
    additions: list[str] = Field(default_factory=list)
    removals: list[str] = Field(default_factory=list)

class DeliveryAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assignment: str                      # collection ID
    due_date: date
    ready: bool = False

class DeliveryManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(pattern=SLUG_PATTERN)
    course: str                          # course ID (must exist in courses/)
    term: str                            # e.g. "spring-2026", "fall-2026"
    language: Language
    status: Literal["active", "archived"] = "active"
    created: date
    updated: date

    lectures: list[DeliveryLecture] = Field(default_factory=list)
    assignments: list[DeliveryAssignment] = Field(default_factory=list)

    default_formats: list[OutputFormat] = Field(
        default_factory=lambda: ["html", "revealjs", "pdf", "handout"]
    )
    default_audiences: list[Audience] = Field(
        default_factory=lambda: ["student", "teacher"]
    )
```

### 3.3 Validation rules

1. `course` must reference an existing course in `courses/`.
2. Each `lecture` ID must reference an existing collection of `collection_kind: lecture`.
3. Each `assignment` ID must reference an existing collection of `collection_kind: assignment`.
4. If `lectures` is empty, fall back to `plan.yml` lecture sequence (dates required if using `teach deliver`).
5. `additions` IDs must reference existing content objects.
6. `removals` IDs must be items in the referenced collection.
7. Dates should be in chronological order (warning, not error).
8. A lecture can only be `ready: true` if all referenced content objects have `status: approved` or `published`.

---

## 4. CLI changes

### 4.1 New commands

```bash
# Build all lectures and assignments for a delivery manifest
teach deliver tem0052-spring-2026

# Build only lectures marked ready: true
teach deliver tem0052-spring-2026 --ready-only

# Build a single lecture from the manifest
teach deliver tem0052-spring-2026 --lecture tem0052-lecture-03

# Show delivery status overview
teach delivery-status tem0052-spring-2026

# Scaffold a new delivery manifest from an existing course plan
teach new-delivery tem0052 --term spring-2026 --lang en
```

### 4.2 `teach deliver` behavior

1. Load the delivery manifest.
2. For each lecture (or filtered subset):
   a. Resolve the collection ID.
   b. Apply `additions` and `removals` if specified.
   c. Build for each combination of `default_audiences × default_formats`.
   d. Inject the lecture date into the build output (frontmatter, title, footer).
3. Write all output to `build/deliveries/<manifest-id>/`.
4. Write a delivery report to `build/reports/deliveries/<manifest-id>/`.

### 4.3 `teach delivery-status` output

```
Delivery: tem0052-spring-2026 (TEM 0052 - Predictive Modelling with Machine Learning)
Term: spring-2026 | Language: en | Status: active

Lectures:
  ✅ 2026-01-20  tem0052-lecture-01  Lecture 1 - Foundations...     [ready]
  ✅ 2026-01-27  tem0052-lecture-02  Lecture 2 - Linear regr...     [ready]
  ⬜ 2026-02-03  tem0052-lecture-03  Lecture 3 - Classificat...     [not ready]
  ⬜ 2026-02-10  tem0052-lecture-04  Lecture 4 - Regularizat...     [not ready]
  ...

Assignments:
  ✅ 2026-02-14  tem0052-assignment-01  Assignment 1               [ready, due in 3 days]
  ⬜ 2026-03-07  tem0052-assignment-02  Assignment 2               [not ready]

Summary: 2/10 lectures ready, 1/2 assignments ready
Next unready: tem0052-lecture-03 (2026-02-03)
```

### 4.4 `teach new-delivery` behavior

1. Read `courses/<course-id>/plan.yml`.
2. Generate a delivery manifest YAML with all lectures and assignments listed, `ready: false`, dates blank (or spaced weekly from a start date if `--start` is given).
3. Write to `deliveries/<course-id>-<term>.yml`.

---

## 5. Build output structure

```
build/deliveries/tem0052-spring-2026/
├── delivery-report.json
├── student/
│   └── en/
│       ├── html/
│       │   ├── tem0052-lecture-01/
│       │   ├── tem0052-lecture-02/
│       │   └── ...
│       ├── pdf/
│       │   ├── tem0052-lecture-01.pdf
│       │   └── ...
│       └── handout/
│           └── ...
└── teacher/
    └── en/
        ├── revealjs/
        │   ├── tem0052-lecture-01/
        │   └── ...
        └── exercise-sheet/
            └── ...
```

This is entirely gitignored. The `.gitignore` entry:

```
build/deliveries/*
!build/deliveries/.gitkeep
```

---

## 6. Date injection

When building via `teach deliver`, the lecture date from the manifest is injected into:

1. **Frontmatter:** `date: 2026-01-20` added to the generated `.qmd` file.
2. **Slide title page:** Date appears below the lecture title in RevealJS/PDF slides.
3. **HTML page header:** Date shown in the lecture metadata panel.
4. **Handout header:** Date in the handout header block.

This is handled in the assembly layer — `assemble_target` gets an optional `delivery_context` parameter:

```python
@dataclass
class DeliveryContext:
    date: date
    term: str
    manifest_id: str
    title_override: str | None = None
    additions: list[str] = field(default_factory=list)
    removals: list[str] = field(default_factory=list)
```

The assembly builder uses `delivery_context` to:
- Filter `items` (apply removals, append additions).
- Set `date` in the frontmatter.
- Override the title if `title_override` is set.

---

## 7. Readiness checking

A lecture's `ready` flag is *manually set by the instructor*. But `teach delivery-status` also performs automatic checks and warns about issues:

### Auto-checks (warnings, do not block `ready: true`)

- Any referenced content object has `status: draft` or `review`.
- Any referenced content object has `translation_status` != `approved` for the delivery language.
- The collection itself has `status` != `approved`.
- Date is in the past but `ready` is `false`.

### The workflow

1. Instructor works on content throughout the semester.
2. Before each lecture, instructor reviews and updates content, sets `status: approved`.
3. Instructor sets `ready: true` in the delivery manifest.
4. Runs `teach deliver <manifest> --ready-only` to build all ready lectures.
5. `teach delivery-status` shows what's left.

This matches the stated workflow: "I usually finish material the week before the lecture."

---

## 8. Decoupling `courses` from content objects

### Current state

Content objects have a `courses` field in `meta.yml`:

```yaml
courses:
  - tem0052
  - gra4150
```

This field is used in:
- Assembly: determining which objects belong to a course page.
- Navigation: showing course context on object pages.
- Search: filtering by course.

### Proposed change

The `courses` field remains but becomes **informational/tagging only**. It answers "which courses is this content relevant for?" — not "which courses own this content."

Assembly of lectures is driven by:
1. **Collections** → which objects appear in a lecture.
2. **Course plan** (`plan.yml`) → which collections form a course.
3. **Delivery manifest** → how a course is delivered in a specific semester.

No code changes are needed for this — the `courses` field already works this way in the assembly layer (collections drive what's included, not the `courses` tag). The change is conceptual: stop thinking of `courses` as structural, and document it as a tag.

### Migration

No data migration needed. The `courses` field stays. Over time, new content objects may list fewer courses (or none) if they're truly generic. Collections remain the structural assembly unit.

---

## 9. Repository layout changes

```
learnforge/
├── deliveries/                    # NEW
│   ├── tem0052-spring-2026.yml
│   ├── bik2550-spring-2026.yml
│   └── ...
├── collections/
│   └── lectures/                  # existing
├── content/                       # existing
├── courses/                       # existing
└── build/
    ├── deliveries/                # NEW (gitignored)
    │   └── tem0052-spring-2026/
    ├── exports/                   # existing
    └── ...
```

---

## 10. Existing code impact

### Files to modify

| File | Change |
|------|--------|
| `app/models.py` | Add `DeliveryLecture`, `DeliveryAssignment`, `DeliveryManifest` models |
| `app/config.py` | Add `DELIVERIES_DIR`, `deliveries_dir()` function |
| `app/indexer.py` | Add delivery manifest loading to `RepositoryIndex` |
| `app/validator.py` | Add delivery manifest validation rules |
| `app/assembly.py` | Add `DeliveryContext` parameter to `assemble_target` and `AssemblyBuilder`; implement additions/removals/date injection |
| `app/build.py` | Add `build_delivery()` function that iterates manifest lectures |
| `app/cli.py` | Add `deliver`, `delivery-status`, `new-delivery` commands |
| `app/scaffold.py` | Add delivery manifest scaffolding |
| `.gitignore` | Add `build/deliveries/*` entry |

### Files that don't change

- `app/search.py` — search operates on content objects, not deliveries.
- `app/translation.py` — translation operates on content objects.
- `app/resource_workflow.py` — resource workflow is content-level.
- `app/publish.py` — student site publishing is separate from delivery builds.
- `app/tui/` — TUI can be extended later but is not in scope here.

### Test additions

| Test file | Coverage |
|-----------|----------|
| `tests/test_delivery_models.py` | Pydantic model validation, schema edge cases |
| `tests/test_delivery_build.py` | End-to-end delivery build with fixtures |
| `tests/test_delivery_cli.py` | CLI commands: deliver, delivery-status, new-delivery |
| `tests/test_delivery_assembly.py` | DeliveryContext integration: additions, removals, date injection |
| `tests/test_delivery_validation.py` | Manifest validation rules |

---

## 11. Implementation phases

### Phase 1: Data model and loading
- Add Pydantic models to `app/models.py`.
- Add `deliveries/` directory config to `app/config.py`.
- Add delivery manifest loading to `app/indexer.py`.
- Add validation rules to `app/validator.py`.
- Tests for model validation.

### Phase 2: Scaffold and CLI skeleton
- Add `teach new-delivery` command.
- Add `teach delivery-status` command.
- Create `deliveries/` directory with `.gitkeep`.
- Update `.gitignore` for `build/deliveries/`.

### Phase 3: Assembly integration
- Add `DeliveryContext` to `app/assembly.py`.
- Implement additions/removals logic in `_assemble_collection`.
- Implement date injection in frontmatter and output.
- Tests for assembly with delivery context.

### Phase 4: Delivery build
- Add `build_delivery()` to `app/build.py`.
- Add `teach deliver` command.
- Implement `--ready-only` and `--lecture` filters.
- Delivery report generation.
- End-to-end tests.

---

## 12. Example workflow

```bash
# Start of semester: scaffold a delivery from the course plan
teach new-delivery tem0052 --term spring-2026 --lang en --start 2026-01-20

# Edit the manifest: set dates, add notes
nvim deliveries/tem0052-spring-2026.yml

# Check status
teach delivery-status tem0052-spring-2026

# Week before Lecture 3: finish content, mark ready
# (edit content, set status: approved on objects)
# Then in the manifest:
#   ready: true
teach deliver tem0052-spring-2026 --lecture tem0052-lecture-03

# Build all ready lectures for the semester
teach deliver tem0052-spring-2026 --ready-only

# End of semester: archive the delivery
# Set status: archived in the manifest
```

---

## 13. Open questions

1. **Should delivery manifests live in git?** They contain no secrets — just dates and readiness flags. Keeping them in git means they're versioned and portable. The alternative is a local-only file (like `.learnforge-schedule.yml`), but that loses version history.

2. **Should `plan.yml` be required if a delivery manifest exists?** The manifest could fully replace the plan, or the plan could remain as the "template" that deliveries instantiate.

3. **Multi-language deliveries?** A manifest has a single `language` field. If you deliver the same course in both EN and NB in the same semester, you'd need two manifests. This seems fine for now.

---

## 14. Testing expectations

All existing tests must pass after implementation. Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check app tests
```

New tests must cover all model validation edge cases, CLI commands, and the assembly integration with DeliveryContext. Aim for the same coverage density as existing test files.

---

## 15. CLAUDE.md note

If the repo has a `CLAUDE.md`, append or update it with:

- New commands: `teach deliver`, `teach delivery-status`, `teach new-delivery`
- New directory: `deliveries/`
- New build output: `build/deliveries/`
- DeliveryContext parameter in assembly
- Testing: `pytest -q` must pass, `ruff check` must pass

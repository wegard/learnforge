# LearnForge TUI — Design Specification

## 1. Purpose

A terminal dashboard for the course instructor to:

- See all active courses at a glance with their status and structure
- Spot content that needs attention (drafts, stale resources)
- Drill into courses, collections, and individual objects
- Open any `.qmd` or `.yml` file in nvim, then return to the dashboard

The TUI is read-only with respect to data — it does not modify metadata,
transition statuses, or run builds. The only mutation is opening files in
an external editor.

---

## 2. Command

```
teach tui [--lang en|nb]
```

- `--lang` sets the default language for opening note files (default: `en`)
- Launches a fullscreen Textual application
- Exits cleanly with `q` or `Ctrl-C`

Added as a new Typer subcommand in `app/cli.py`.

---

## 3. Framework

**Textual** (`>=1.0.0,<2.0.0`) — a Python TUI framework built on Rich.

Reasons:
- Native Python, fits the existing codebase (Typer, Pydantic, PyYAML)
- DataTable, ListView, Tree, CSS layout, keyboard navigation out of the box
- `app.suspend()` for clean editor handoff and return
- Single new dependency

---

## 4. Data Source

All data comes from the existing `load_repository()` in `app/indexer.py`,
which returns a `RepositoryIndex` containing every object and course.

- Loaded once at startup
- Reloaded after returning from the editor (to pick up any changes)
- Archived courses (`status == "archived"`) are excluded from the dashboard
- "Last edited" uses the `updated` field from `meta.yml` (no git queries)

---

## 5. Navigation

Four screens arranged as a push/pop stack. Escape always goes back one
level. The hierarchy mirrors the content model:

```
Dashboard  →  Course  →  Collection  →  Object Detail
   (all courses)  (lectures + assignments)  (items table)  (metadata + edit)
```

### 5.1 Dashboard Screen

Top-level view. Two panels side by side.

```
┌─ LearnForge Dashboard ─────────────────────────────────────────┐
│                                                                │
│  COURSES                          NEEDS ATTENTION              │
│  ┌────────────────────────────┐   ┌───────────────────────────┐│
│  │   bik2550  approved  (1!) ││   │ ! bik2550-m3d1            ││
│  │   bik2551  approved       ││   │   collection — draft      ││
│  │   edi3400  approved  (3!) ││   │ ! random-forests          ││
│  │   gra4150  approved       ││   │   concept — draft         ││
│  │   gra4164  approved       ││   │ ! angrist-podcast-iv      ││
│  │ > tem0052  approved  (2!) ││   │   resource — stale        ││
│  │                           ││   │                           ││
│  └────────────────────────────┘   └───────────────────────────┘│
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  6 courses · 248 objects · 6 need attention       lang: en     │
├────────────────────────────────────────────────────────────────┤
│  Enter: drill in   Tab: switch panel   l: language   q: quit   │
└────────────────────────────────────────────────────────────────┘
```

**Left panel — Course list** (`ListView`):
- One row per non-archived course
- Shows: course ID, status, attention count badge `(N!)`
- Sorted alphabetically by ID
- Cursor-selectable; Enter pushes CourseScreen

**Right panel — Attention list** (`ListView`):
- Flat list of every object needing attention across all courses
- Shows: `!` prefix, object ID, kind, reason (draft/review/stale/candidate)
- Selecting an item and pressing Enter pushes ObjectDetailScreen directly

**Footer**:
- Object/course counts, current language, key hints

### 5.2 Course Screen

Shows the plan for a single course — its lectures and assignments.

```
┌─ Course: edi3400 — Programming and Data Management ───────────┐
│                                                                │
│  LECTURES (16)                    ASSIGNMENTS (4)              │
│  ┌────────────────────────────┐   ┌───────────────────────────┐│
│  │   edi3400-lecture-01       ││   │   edi3400-assignment-01   ││
│  │   edi3400-lecture-02       ││   │   edi3400-assignment-02   ││
│  │ > edi3400-lecture-03  (1!) ││   │   edi3400-assignment-03   ││
│  │   edi3400-lecture-04       ││   │   edi3400-assignment-04   ││
│  │   edi3400-lecture-05       ││   │                           ││
│  │   ...                     ││   │                           ││
│  └────────────────────────────┘   └───────────────────────────┘│
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  approved · 16 lectures · 4 assignments · updated 2026-03-21  │
├────────────────────────────────────────────────────────────────┤
│  Enter: drill in   e: edit syllabus   Tab: switch   Esc: back  │
└────────────────────────────────────────────────────────────────┘
```

**Left panel — Lectures** (`ListView`):
- Each lecture collection from `plan.yml`, in order
- Shows collection ID and attention count badge if any items need attention
- Enter pushes CollectionScreen

**Right panel — Assignments** (`ListView`):
- Same format as lectures, for assignment collections

**Actions**:
- `e` opens the course syllabus (`syllabus.{lang}.qmd`) in nvim
- `Tab` switches focus between panels

### 5.3 Collection Screen

Shows items within a lecture or assignment collection.

```
┌─ Collection: edi3400-lecture-03 ───────────────────────────────┐
│                                                                │
│  ID                          Kind       Status     Updated   ! │
│  ─────────────────────────── ────────── ──────── ────────── ──│
│  python-control-flow         concept    approved   2026-03     │
│  python-functions-basics     concept    approved   2026-03     │
│> python-string-methods       concept    draft      2026-03   ! │
│  python-error-handling       concept    approved   2026-03     │
│  string-manipulation-lab     exercise   approved   2026-03     │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  lecture · 5 items · 1 needs attention                         │
├────────────────────────────────────────────────────────────────┤
│  Enter: details   e: edit meta.yml   Esc: back                 │
└────────────────────────────────────────────────────────────────┘
```

**Main area — Items table** (`DataTable`):
- Columns: ID, Kind, Status (color-coded), Updated (YYYY-MM), Attention flag
- Items listed in plan order (same order as `items` in the collection's `meta.yml`)
- Enter pushes ObjectDetailScreen
- Row cursor for selection

**Color coding in Status column**:
- `approved` / `published` → green
- `draft` → yellow
- `review` → blue
- `candidate` / `reviewed` → yellow
- `archived` → dim/grey

### 5.4 Object Detail Screen

Metadata display and file editing entry point.

```
┌─ Object: python-string-methods ───────────────────────────────┐
│                                                                │
│  Kind:        concept                                          │
│  Status:      draft                                            │
│  Level:       beginner                                         │
│  Languages:   en, nb                                           │
│  Title (en):  Python string methods                            │
│  Updated:     2026-03-19                                       │
│  Courses:     edi3400                                          │
│  Topics:      python, strings                                  │
│  Owners:      vegard                                           │
│  Translation: en=edited, nb=machine_draft                      │
│                                                                │
│  Files:                                                        │
│    note.en.qmd · note.nb.qmd · meta.yml                       │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  e: edit note   m: edit meta.yml   l: language   Esc: back     │
└────────────────────────────────────────────────────────────────┘
```

For **exercises**, an additional key `s` opens the solution file, and
extra metadata is shown (exercise_type, difficulty, estimated_time).

For **figures**, the asset inventory is listed.

For **resources**, url, authors, freshness, review_after, and stale_flag
are shown.

---

## 6. Editing Flow

When the user presses `e`, `m`, or `s`:

1. The TUI calls `app.suspend()` — Textual restores the terminal to normal
2. `subprocess.run([editor, file_path], cwd=REPO_ROOT)` launches nvim
3. The user edits and quits nvim (`:wq`)
4. Textual resumes and redraws the TUI
5. The repository index is reloaded to reflect any changes
6. The current screen refreshes its data

The editor is resolved from `$EDITOR` (default: `nvim`).

Language resolution for note files:
- Use the `--lang` flag value if the object supports that language
- Otherwise fall back to the first language in the object's `languages` list
- The `l` key toggles between `en` and `nb` at any time

---

## 7. "Needs Attention" Logic

An object needs attention if **any** of these conditions hold:

| Condition                                  | Applies to             | Label            |
|--------------------------------------------|------------------------|------------------|
| `status == "draft"`                        | concept, exercise,     | `draft`          |
|                                            | figure, collection     |                  |
| `status == "review"`                       | concept, exercise,     | `review`         |
|                                            | figure, collection     |                  |
| `status == "candidate"`                    | resource               | `candidate`      |
| `status == "reviewed"`                     | resource               | `needs approval` |
| `stale_flag == True`                       | resource               | `stale`          |
| `review_after < today` and not stale_flag  | resource               | `review overdue` |

**Attention bubbles upward:**
- A collection shows `(N!)` if N of its items need attention
- A course shows `(N!)` if N total items across all its collections need attention

---

## 8. Key Bindings

### Global

| Key     | Action                     |
|---------|----------------------------|
| `q`     | Quit the application       |
| `Esc`   | Go back one screen / quit on Dashboard |
| `?`     | Show help overlay          |
| `L`     | Toggle language (en ↔ nb)  |
| `j`/`k` | Navigate down/up (vim-style) |
| `h`/`l` | Go back / drill in (vim-style) |

### Dashboard Screen

| Key     | Action                              |
|---------|-------------------------------------|
| `Enter`/`l` | Drill into selected course     |
| `Tab`   | Switch focus: courses → attention   |
| `Shift+Tab` | Switch focus: attention → courses |

### Course Screen

| Key     | Action                              |
|---------|-------------------------------------|
| `Enter`/`l` | Drill into selected collection |
| `e`     | Edit course syllabus in nvim        |
| `Tab`   | Switch focus: lectures → assignments|
| `Shift+Tab` | Switch focus: assignments → lectures |

### Collection Screen

| Key     | Action                              |
|---------|-------------------------------------|
| `Enter`/`l` | Open object detail             |
| `e`     | Edit collection meta.yml in nvim    |

### Object Detail Screen

| Key     | Action                              |
|---------|-------------------------------------|
| `e`     | Edit note file in nvim              |
| `m`     | Edit meta.yml in nvim               |
| `s`     | Edit solution file (exercises only) |
| `j`/`k` | Scroll content down/up             |

---

## 9. File Structure

```
app/
  tui/
    __init__.py          # launch() entry point
    app.py               # LearnForgeApp(textual.app.App)
    screens.py           # DashboardScreen, CourseScreen,
                         # CollectionScreen, ObjectDetailScreen
    widgets.py           # CourseListItem, AttentionBadge, etc.
    data.py              # TUIIndex, load_tui_index(), needs_attention()
    learnforge.tcss      # Textual CSS for layout and colors
```

### Module Responsibilities

**`data.py`** — Pure data layer, no UI:
- `TUIIndex` dataclass: pre-processed repo data (active courses, attention items)
- `load_tui_index(root)` → `TUIIndex`: loads and filters repository
- `needs_attention(model, today)` → `list[str]`: returns attention reasons
- `collection_attention_count(collection_id, index)` → `int`
- `course_attention_count(course_id, index)` → `int`

**`app.py`** — Application shell:
- Holds `tui_index` and `language` as app state
- `edit_file(path)`: suspend → launch `$EDITOR` → reload index → call `screen.refresh_data()`
- `action_toggle_language()`: cycles between `en` and `nb`, refreshes current screen
- `action_help()`: shows key binding overlay via notification

**`screens.py`** — Four screen classes:
- Each receives its context (course_id, collection_id, object_id) via constructor
- Each implements `refresh_data()` to repopulate after edits or language changes
- Dashboard and Course screens explicitly focus the left panel on mount

**`widgets.py`** — Reusable display components:
- `CourseListItem(ListItem)` — course row with inline attention badge
- `CollectionListItem(ListItem)` — collection row with inline attention badge
- `AttentionListItem(ListItem)` — attention panel row showing object ID, kind, and reasons

**`learnforge.tcss`** — Layout and color rules:
- Two-column layout for Dashboard and Course screens
- Panel focus indication via `:focus-within` (accent border and title on active panel)
- Status colors: `$success` (approved/published), `$warning` (draft/candidate/reviewed), `#5599ff` (review)
- Responsive sizing with `fr` units (works at 80+ column terminals)

---

## 10. Dependency Change

In `pyproject.toml`, add to `dependencies`:

```toml
"textual>=1.0.0,<2.0.0",
```

No other dependency changes needed. Textual pulls in `rich` as a
transitive dependency (already used implicitly by Typer).

---

## 11. Reused Infrastructure

| What                        | From                    | Used for                         |
|-----------------------------|-------------------------|----------------------------------|
| `load_repository()`         | `app/indexer.py`        | All data loading                 |
| `IndexedObject`             | `app/indexer.py`        | Object metadata, file paths      |
| `IndexedCourse`             | `app/indexer.py`        | Course metadata, plan, syllabus  |
| `note_path(lang)`           | `IndexedObject`         | Resolving note file to edit      |
| `solution_path(lang)`       | `IndexedObject`         | Resolving solution file to edit  |
| `syllabus_path(lang)`       | `IndexedCourse`         | Resolving syllabus file to edit  |
| `REPO_ROOT`, `LANGUAGES`    | `app/config.py`         | Root path, language validation   |
| Pydantic models             | `app/models.py`         | Type-safe access to all metadata |

No new data loading code is needed — the existing indexer provides
everything the TUI requires.

---

## 12. Testing Strategy

**`tests/test_tui_data.py`** — Unit tests (no TUI):
- `needs_attention()` returns correct reasons for each status
- `load_tui_index()` excludes archived courses
- Attention counts bubble correctly from items → collections → courses
- Missing object IDs in collections handled gracefully (shown as "missing")

Textual pilot tests for screen navigation are not yet implemented.

---

## 13. Implementation Status

All planned phases are complete:

- Data layer (`app/tui/data.py`), CLI hook (`teach tui`), and unit tests (`tests/test_tui_data.py`)
- All four screens with vim-style navigation and editor integration
- Custom list item widgets with inline attention badges
- Textual CSS with panel focus indication, status colors, and responsive sizing

---

## 14. Non-Goals

These are explicitly out of scope for the TUI:

- Running validation (`teach validate`)
- Scaffolding new content (`teach new`)
- Status transitions (draft → approved, etc.)
- Building targets (`teach build`)
- Search/filtering within the TUI
- Git integration for last-edited dates
- Translation gap reporting

Use the existing `teach` CLI commands for these. The TUI is a
browsing and editing dashboard, not a replacement for the CLI.

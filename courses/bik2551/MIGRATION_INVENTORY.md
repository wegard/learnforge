# BIK2551 Migration Inventory

This file tracks the migration of legacy material from
`course-inbox/ai-produktivitet/` into LearnForge's canonical
course/object structure.

## Locked Decisions

- Canonical course id: `bik2551`
- Course language at migration start: `nb` only
- Lecture notes are reference material, not source of truth
- New teaching material is authored fresh in `.qmd`
- No bulk import of slides, LaTeX, PDFs, or images
- No promotion of editor files, checkpoint folders, or build artifacts
- Exercise type: `conceptual` (practitioner course, not coding)
- Topic taxonomy: `ai-literacy`, `prompt-engineering`, `ai-ethics`, `ai-automation`, `ai-agents`, `ai-strategy`
- Lecture collections map to the 4 campus days: `bik2551-day-01` through `bik2551-day-04`
- Images stay in inbox until a figure pipeline decision is made

## Migration Buckets

### Promote First

These items map directly to the course's four campus days and can be turned
into reusable concepts and exercises with fresh authoring guided by the
lecture notes.

| Legacy source | Action | Target kind | Proposed target id |
| --- | --- | --- | --- |
| Day 1: Hva er Generativ KI (09:30) | Author fresh concept on LLM fundamentals | concept | `generative-ai-fundamentals` |
| Day 1: Prompt Engineering 101 (10:30) | Author fresh concept on structured prompting | concept | `prompt-engineering-basics` |
| Day 1: Etikk, jus og sikkerhet (13:45) | Author fresh concept on AI ethics and regulation | concept | `ai-ethics-law-security` |
| Day 1: Workshop — forbedre prompts (10:30+) | Convert to conceptual exercise | exercise | `prompt-improvement-workshop` |
| Day 2: Kontekstvindu og RAG (09:30) | Author fresh concept on context windows and retrieval | concept | `context-windows-and-rag` |
| Day 2: Chain of Thought / avansert prompting (10:15) | Author fresh concept on advanced prompting | concept | `advanced-prompting-techniques` |
| Day 2: Custom Instructions / KI-assistent (11:15+13:00) | Author fresh concept on custom AI assistants | concept | `custom-ai-assistants` |
| Day 2: Workshop — bygg assistent (13:00) | Convert to conceptual exercise | exercise | `custom-assistant-setup` |
| Day 3: KI-agenter (10:15) | Author fresh concept on AI agents | concept | `ai-agents-introduction` |
| Day 3: Automatiseringsnivåer (12:30) | Author fresh concept on automation levels | concept | `automation-levels` |
| Day 3: Workshop — automatisering (13:00) | Convert to conceptual exercise | exercise | `automation-design-exercise` |
| Day 4: KI-strategi og implementering (09:00) | Author fresh concept on AI strategy | concept | `ai-strategy-implementation` |
| Day 4: Fremtidens arbeidsliv (10:45) | Author fresh concept on AI and future of work | concept | `ai-future-of-work` |

### Rewrite Fresh

These topics needed fresh authoring rather than direct migration from a
single clear legacy source. They are now covered in canonical LearnForge
objects.

| Topic | Canonical coverage | Status |
| --- | --- | --- |
| Kreative KI-verktøy (bilder, presentasjoner) | `creative-ai-tools-overview` | approved |
| NotebookLM og kildebaserte systemer | `context-windows-and-rag`, `notebooklm-source-grounding-guide` | approved |
| Prosjektoppgave og mini-eksperiment | `bik2551-project-brief` + prosjektøvelser | approved |

### Defer

These can stay in the inbox until the core concepts are migrated.

| Legacy source | Reason for deferral |
| --- | --- |
| `Slides/` (12+ LaTeX/PDF slide decks) | Reference only; new content is authored fresh in `.qmd` |
| `Kursplan/kursplan_spring2026.tex` | Already distilled into `syllabus.nb.qmd` |
| `Lecture_notes/Day_01.md`–`Day_04.md` | Reference material for authoring; not promoted directly |
| `Digital_sessions/` content (if any) | Digital session material deferred until campus days are migrated |
| `Images/` (80+ files) | Images stay in inbox until figure pipeline decision |
| `Resources/` reference lists | Candidate resource objects for a later phase |

### Drop or Archive

| Legacy source | Reason |
| --- | --- |
| `.aux`, `.log`, `.nav`, `.snm`, `.synctex.gz`, generated PDFs | LaTeX build artifacts |
| `.idea/`, editor config files | Tooling noise |
| Template files (`Mal_*.docx`, `Skjema_*.pdf`) | Administrative handouts, not canonical teaching content |

## Proposed First Canonical Slice

Build the first LearnForge checkpoint for `bik2551` around Day 1 content.

### First concept candidates

- `generative-ai-fundamentals`
- `prompt-engineering-basics`
- `ai-ethics-law-security`

### First exercise candidates

- `prompt-improvement-workshop`

### First lecture candidates

- `bik2551-day-01` — introduction to generative AI, prompt engineering, ethics

## Promoted in the Current Checkpoint

Day 1 content — 5 objects promoted:

| Object id | Kind | Status |
| --- | --- | --- |
| `generative-ai-fundamentals` | concept | approved |
| `prompt-engineering-basics` | concept | approved |
| `ai-ethics-law-security` | concept | approved |
| `prompt-improvement-workshop` | exercise | approved |
| `bik2551-day-01` | collection (lecture) | approved |

Day 2 content — 5 objects promoted:

| Object id | Kind | Status |
| --- | --- | --- |
| `context-windows-and-rag` | concept | approved |
| `advanced-prompting-techniques` | concept | approved |
| `custom-ai-assistants` | concept | approved |
| `custom-assistant-setup` | exercise | approved |
| `bik2551-day-02` | collection (lecture) | approved |

Day 3 content — 4 objects promoted:

| Object id | Kind | Status |
| --- | --- | --- |
| `ai-agents-introduction` | concept | approved |
| `automation-levels` | concept | approved |
| `automation-design-exercise` | exercise | approved |
| `bik2551-day-03` | collection (lecture) | approved |

Day 4 content — 3 objects promoted:

| Object id | Kind | Status |
| --- | --- | --- |
| `ai-strategy-implementation` | concept | approved |
| `ai-future-of-work` | concept | approved |
| `bik2551-day-04` | collection (lecture) | approved |

Course support and assessment content — 7 objects promoted:

| Object id | Kind | Status |
| --- | --- | --- |
| `creative-ai-tools-overview` | concept | approved |
| `notebooklm-source-grounding-guide` | resource | approved |
| `ki-assistenter-arbeidslivet-guide` | resource | approved |
| `project-problem-and-baseline` | exercise | approved |
| `mini-experiment-measurement-plan` | exercise | approved |
| `final-report-and-video-brief` | exercise | approved |
| `bik2551-project-brief` | collection (assignment) | approved |

## Next Migration Actions

All four campus days are now promoted. Remaining work:

1. Expand the curated resource set if the teaching team wants more pre-reads.
2. Leave all remaining legacy files in the inbox until they are explicitly promoted.

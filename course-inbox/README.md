# Course Inbox

`course-inbox/` is a temporary staging area for legacy course material that has not
been promoted into LearnForge's canonical object model yet.

## Rules

- Everything in this directory is temporary intake material, not source of truth.
- Nothing under `course-inbox/` is scanned by `teach validate`, indexed for search,
  or used as a build input.
- Only this `README.md` and `.gitkeep` are tracked in git. Everything else in this
  directory is intentionally git-ignored.
- Promote material by copying the relevant text and assets into `content/`,
  `collections/`, or `courses/` through the existing LearnForge conventions.
- Do not reference files in `course-inbox/` from canonical metadata.

## Suggested Layout

Use one subfolder per course or legacy source bundle:

```text
course-inbox/
├── ec202/
│   ├── notes/
│   ├── slides/
│   ├── assignments/
│   ├── resources/
│   ├── figures/
│   ├── misc/
│   └── archive/
└── legacy-other-course/
    ├── notes/
    └── misc/
```

If you do not know the final LearnForge course id yet, use a temporary slug such as
`legacy-ec202`.

## Intake Workflow

1. Copy the legacy files into `course-inbox/<course-id>/`.
2. Sort them only into coarse buckets such as `notes/`, `slides/`, and
   `assignments/`.
3. Review each item and decide whether to:
   - promote now
   - split later
   - keep as reference
   - archive/delete
4. When promoting, create the canonical target first, then copy only the needed
   material into the tracked LearnForge object or collection folder.
5. Delete or archive the inbox copy once the promoted material is stable.

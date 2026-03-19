# BIK2551 Translation Guide

This course now uses a bilingual `nb` / `en` workflow with one canonical object
id per teaching object.

## Working Rules

- Keep ids, topics, tags, and file structure unchanged across languages.
- Translate human-facing text, not repository identifiers.
- Use standard professional English for course participants at BI.
- Keep examples, exercises, and task structure aligned across languages unless a
  localized example is clearly more natural.

## Translation States

- `machine_draft`: Fast first pass that still needs human review.
- `edited`: Human-revised and structurally sound, but not yet ready for student publication.
- `approved`: Ready for student-facing builds and search indexing.

For `bik2551`, English is now approved across the current course slice.

## Preferred Term Choices

- `kunstig intelligens` -> `artificial intelligence`
- `generativ KI` -> `generative AI`
- `språkmodell` -> `language model`
- `kunnskapsarbeider` -> `knowledge worker`
- `prompting` -> `prompting`
- `kontekstvindu` -> `context window`
- `hallusinering` -> `hallucination`
- `tilpasset KI-assistent` -> `custom AI assistant`
- `automatisering` -> `automation`
- `måleplan` -> `measurement plan`
- `loggbok` -> `logbook`

## Validation Checklist

Run these before approving a new language slice:

```bash
teach translation-status bik2551 --lang en
teach build bik2551 --audience student --lang en --format html
teach build bik2551-day-01 --audience student --lang en --format html
teach validate
```

## Review Focus

- Check that page titles, summaries, and syllabus language are consistent.
- Check that exercise instructions and teacher solutions describe the same task.
- Prefer clear business English over literal translation of Norwegian phrasing.
- Keep teacher-only notes localized when the surrounding page is localized.

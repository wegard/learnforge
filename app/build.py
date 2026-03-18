from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

from app.config import EXPORTS_DIR, GENERATED_DIR, REPO_ROOT
from app.indexer import IndexedCourse, IndexedObject, RepositoryIndex, load_repository
from app.models import Collection

RenderableFormat = Literal["html", "pdf", "revealjs", "handout", "exercise-sheet"]

FORMAT_TO_QUARTO = {
    "html": "html",
    "pdf": "pdf",
    "revealjs": "revealjs",
    "handout": "pdf",
    "exercise-sheet": "pdf",
}


@dataclass(slots=True)
class BuildArtifact:
    target_id: str
    target_kind: str
    output_format: str
    audience: str
    language: str
    source_path: Path
    output_path: Path
    command: list[str]


class BuildError(RuntimeError):
    pass


MARKDOWN_LINK_RE = re.compile(r"(\!?\[[^\]]*\]\()([^)]+)(\))")
TEACHER_BLOCK_RE = re.compile(r"\n?:::\s*\{\.teacher-only\}\n.*?\n:::\s*\n?", re.DOTALL)
STUDENT_BLOCK_RE = re.compile(r"\n?:::\s*\{\.student-only\}\n.*?\n:::\s*\n?", re.DOTALL)


def build_target(
    target_id: str,
    *,
    audience: str,
    language: str,
    output_format: RenderableFormat,
    root: Path = REPO_ROOT,
) -> BuildArtifact:
    index, errors = load_repository(root, collect_errors=False)
    if errors:
        raise BuildError("repository contains load errors")

    if target_id in index.objects:
        record = index.objects[target_id]
        if isinstance(record.model, Collection):
            source_path = materialize_collection(
                record,
                index,
                audience,
                language,
                output_format,
                root,
            )
            target_kind = "collection"
        else:
            source_path = materialize_object(record, audience, language, output_format, root)
            target_kind = record.model.kind
    elif target_id in index.courses:
        source_path = materialize_course(
            index.courses[target_id],
            index,
            audience,
            language,
            output_format,
            root,
        )
        target_kind = "course"
    else:
        raise BuildError(f"unknown target id: {target_id}")

    output_dir = EXPORTS_DIR / audience / language / output_format / target_kind / target_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_name = build_output_name(target_id, output_format)
    command = [
        "quarto",
        "render",
        str(source_path.relative_to(root)),
        "--profile",
        f"{audience},{language}",
        "--to",
        FORMAT_TO_QUARTO[output_format],
        "--output",
        output_name,
        "--output-dir",
        str(output_dir.relative_to(root)),
    ]
    cache_dir = root / "build" / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("QUARTO_CACHE_DIR", str(cache_dir))
    env.setdefault("XDG_CACHE_HOME", str(cache_dir))
    result = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        raise BuildError(result.stderr.strip() or result.stdout.strip() or "quarto render failed")

    return BuildArtifact(
        target_id=target_id,
        target_kind=target_kind,
        output_format=output_format,
        audience=audience,
        language=language,
        source_path=source_path,
        output_path=output_dir / output_name,
        command=command,
    )


def materialize_object(
    record: IndexedObject,
    audience: str,
    language: str,
    output_format: str,
    root: Path,
) -> Path:
    ensure_visibility(record.model.visibility, audience, record.model.id)
    ensure_language(language, record.model.languages, record.model.id)

    output_path = generated_path(
        "objects",
        record.model.kind,
        record.model.id,
        audience,
        language,
        output_format,
    )
    note_path = record.note_path(language)
    content = rewrite_relative_links(
        note_path.read_text(encoding="utf-8"),
        note_path.parent,
        output_path,
    )
    content = strip_visibility_blocks(content, audience)
    frontmatter = {
        "title": record.model.title[language],
        "lang": language,
        "audience": audience,
        "language_variant": language,
    }
    output_path.write_text(render_frontmatter(frontmatter) + "\n" + content, encoding="utf-8")
    return output_path


def materialize_collection(
    record: IndexedObject,
    index: RepositoryIndex,
    audience: str,
    language: str,
    output_format: str,
    root: Path,
) -> Path:
    ensure_visibility(record.model.visibility, audience, record.model.id)
    ensure_language(language, record.model.languages, record.model.id)

    output_path = generated_path(
        "collections",
        record.model.collection_kind,
        record.model.id,
        audience,
        language,
        output_format,
    )
    parts = [
        render_frontmatter(
            {
                "title": record.model.title[language],
                "lang": language,
                "audience": audience,
                "language_variant": language,
            }
        ),
        "",
        f"## {record.model.title[language]}",
        "",
    ]

    for item_id in record.model.items:
        item_record = index.objects[item_id]
        if audience == "student" and item_record.model.visibility in {"private", "teacher"}:
            continue
        item_note = item_record.note_path(language)
        ensure_language(language, item_record.model.languages, item_id)
        content = rewrite_relative_links(
            item_note.read_text(encoding="utf-8"),
            item_note.parent,
            output_path,
        )
        content = strip_visibility_blocks(content, audience)
        parts.append(content)
        parts.append("")

    output_path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    return output_path


def materialize_course(
    record: IndexedCourse,
    index: RepositoryIndex,
    audience: str,
    language: str,
    output_format: str,
    root: Path,
) -> Path:
    ensure_visibility(record.model.visibility, audience, record.model.id)
    ensure_language(language, record.model.languages, record.model.id)
    if output_format not in {"html", "pdf"}:
        raise BuildError("course builds currently support html and pdf only")

    output_path = generated_path(
        "courses",
        "landing",
        record.model.id,
        audience,
        language,
        output_format,
    )
    syllabus_path = record.syllabus_path(language)
    syllabus_text = rewrite_relative_links(
        syllabus_path.read_text(encoding="utf-8"),
        syllabus_path.parent,
        output_path,
    )
    syllabus_text = strip_visibility_blocks(syllabus_text, audience)

    lecture_lines = []
    for lecture_id in record.plan.lectures:
        lecture_record = index.objects[lecture_id]
        lecture_lines.append(f"- `{lecture_id}`: {lecture_record.model.title[language]}")

    teacher_block = ""
    if audience == "teacher":
        teacher_block = "\n".join(
            [
                "## Teacher Notes",
                "",
                f"Owners: {', '.join(record.model.owners)}",
                f"Tracked lectures: {len(record.plan.lectures)}",
                "",
            ]
        )

    parts = [
        render_frontmatter(
            {
                "title": record.model.title[language],
                "lang": language,
                "audience": audience,
                "language_variant": language,
            }
        ),
        "",
        record.model.summary[language],
        "",
        "## Lectures",
        "",
        *lecture_lines,
        "",
        teacher_block,
        "## Syllabus",
        "",
        syllabus_text,
    ]
    output_path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    return output_path


def generated_path(
    top_level: str,
    kind: str,
    identifier: str,
    audience: str,
    language: str,
    output_format: str,
) -> Path:
    path = (
        GENERATED_DIR
        / top_level
        / kind
        / identifier
        / audience
        / language
        / f"{identifier}.{output_format}.qmd"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def build_output_name(identifier: str, output_format: str) -> str:
    extension = ".pdf" if output_format in {"pdf", "handout", "exercise-sheet"} else ".html"
    suffix = ""
    if output_format == "handout":
        suffix = "-handout"
    elif output_format == "exercise-sheet":
        suffix = "-exercise-sheet"
    return f"{identifier}{suffix}{extension}"


def ensure_visibility(visibility: str, audience: str, identifier: str) -> None:
    if audience == "student" and visibility in {"private", "teacher"}:
        raise BuildError(f"{identifier} is not student-visible")


def ensure_language(language: str, languages: list[str], identifier: str) -> None:
    if language not in languages:
        raise BuildError(f"{identifier} does not support language {language}")


def render_frontmatter(payload: dict[str, str]) -> str:
    return "---\n" + yaml.safe_dump(payload, sort_keys=False, allow_unicode=False).strip() + "\n---"


def rewrite_relative_links(content: str, source_dir: Path, generated_path: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        raw_target = match.group(2)
        if raw_target.startswith(("http://", "https://", "#", "/")):
            return match.group(0)
        target_path = (source_dir / raw_target).resolve()
        if not target_path.exists():
            return match.group(0)
        relative_target = os.path.relpath(target_path, generated_path.parent)
        return f"{match.group(1)}{relative_target}{match.group(3)}"

    return MARKDOWN_LINK_RE.sub(replace, content)


def strip_visibility_blocks(content: str, audience: str) -> str:
    if audience == "student":
        return TEACHER_BLOCK_RE.sub("\n", content)
    if audience == "teacher":
        return STUDENT_BLOCK_RE.sub("\n", content)
    return content

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.assembly import (
    SOLUTION_BLOCK_MARKER,
    AssemblyDocument,
    AssemblyError,
    assemble_target,
    build_output_name,
    collect_topics,
    html_shell_asset_path,
    humanize_slug,
    planned_target_output_path,
    student_search_index_path,
)
from app.config import REPO_ROOT, WEB_ASSETS_DIR, exports_dir, generated_dir, reports_dir
from app.indexer import IndexedCourse, IndexedObject, RepositoryIndex, load_repository
from app.models import Collection, Resource
from app.resource_workflow import resource_student_visibility_decision

RenderableFormat = Literal["html", "pdf", "revealjs", "slides-pdf", "handout", "exercise-sheet"]

FORMAT_TO_QUARTO = {
    "html": "html",
    "pdf": "pdf",
    "revealjs": "revealjs",
    "handout": "pdf",
    "exercise-sheet": "pdf",
}

SLIDES_PDF_OUTPUT_FORMAT = "slides-pdf"
SLIDES_PDF_BROWSER_ENV = "LEARNFORGE_SLIDES_PDF_BROWSER"
SLIDES_PDF_BROWSER_CANDIDATES = (
    "google-chrome-stable",
    "google-chrome",
    "chromium",
    "chromium-browser",
    "chrome",
)


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
    build_manifest_path: Path
    dependency_manifest_path: Path
    leakage_report_path: Path
    search_index_path: Path | None = None


@dataclass(frozen=True, slots=True)
class StudentSiteTarget:
    target_id: str
    target_kind: str


class BuildError(RuntimeError):
    pass


TEACHER_BLOCK_SOURCE_RE = re.compile(r":::\s*\{\.teacher-only\}")
TEACHER_BLOCK_OUTPUT_RE = re.compile(r'class="[^"]*\bteacher-only\b[^"]*"')


def build_target(
    target_id: str,
    *,
    audience: str,
    language: str,
    output_format: RenderableFormat,
    root: Path = REPO_ROOT,
    index: RepositoryIndex | None = None,
    sync_html_shell_assets: bool = True,
    sync_student_search_index: bool = True,
) -> BuildArtifact:
    assembly: AssemblyDocument | None = None
    build_index: RepositoryIndex | None = index
    command: list[str] = []
    commands: list[list[str]] = []
    result: subprocess.CompletedProcess[str] | None = None
    max_attempts = 4
    for attempt in range(max_attempts):
        ensure_generated_staging(root)
        if build_index is None:
            build_index, errors = load_repository(root, collect_errors=False)
            if errors:
                raise BuildError("repository contains load errors")

        try:
            assembly = assemble_target(
                target_id,
                index=build_index,
                audience=audience,
                language=language,
                output_format=output_format,
                root=root,
            )
        except AssemblyError as exc:
            raise BuildError(str(exc)) from exc

        output_dir = assembly.planned_output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = assembly.planned_output_path
        quarto_format = quarto_format_for_output(output_format)
        rendered_output_name = rendered_output_name_for_target(
            target_id,
            output_format=output_format,
            audience=audience,
        )
        prepare_generated_target_dir(assembly.generated_path)
        assembly.generated_path.write_text(assembly.markdown, encoding="utf-8")
        quarto_command = [
            "quarto",
            "render",
            str(assembly.generated_path.relative_to(root)),
            "--profile",
            f"{audience},{language}",
            "--to",
            quarto_format,
            "--output",
            rendered_output_name,
        ]
        if quarto_format == "pdf":
            quarto_command.extend(["-M", "pdf-engine:tectonic"])

        result = subprocess.run(
            quarto_command,
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            env=build_env(root),
        )
        if result.returncode == 0:
            break
        error_message = result.stderr.strip() or result.stdout.strip() or "quarto render failed"
        if attempt < max_attempts - 1 and should_retry_quarto_render(error_message):
            continue
        raise BuildError(error_message)

    if assembly is None:
        raise BuildError("assembly generation failed")
    if build_index is None:
        raise BuildError("repository index unavailable for build")

    rendered_output = locate_rendered_output(
        generated_path=assembly.generated_path,
        output_name=rendered_output_name,
        root=root,
        result=result,
    )
    commands = [quarto_command]

    if output_format == SLIDES_PDF_OUTPUT_FORMAT:
        command = export_revealjs_pdf(
            revealjs_output_path=rendered_output,
            output_path=output_path,
            root=root,
        )
        commands.append(command)
    else:
        command = quarto_command
        if rendered_output.resolve() != output_path.resolve():
            if output_path.exists():
                output_path.unlink()
            shutil.move(str(rendered_output), str(output_path))

        rendered_support_dir = rendered_support_path(
            generated_path=assembly.generated_path,
            output_name=rendered_output_name,
        )
        if rendered_support_dir.exists():
            destination_support_dir = output_dir / rendered_support_dir.name
            if destination_support_dir.exists():
                shutil.rmtree(destination_support_dir)
            # Keep Quarto sidecar assets in the generated staging tree so later
            # renders do not trip over stale generated .qmd files whose *_files
            # directories have already been moved away.
            shutil.copytree(rendered_support_dir, destination_support_dir)

        sync_site_libs(root, output_dir)

    search_index_path = None
    if audience in {"student", "teacher"} and output_format == "html" and sync_html_shell_assets:
        write_html_shell_assets(audience=audience, language=language, root=root)
    if audience == "student" and output_format == "html":
        search_index_path = student_search_index_path(root, language)
        if sync_student_search_index:
            search_index_path = write_student_site_search_index(
                index=build_index, language=language, root=root
            )
    build_manifest_path, dependency_manifest_path, leakage_report_path = write_build_reports(
        assembly=assembly,
        command=command,
        commands=commands,
        output_path=output_path,
        search_index_path=search_index_path,
        root=root,
    )

    return BuildArtifact(
        target_id=target_id,
        target_kind=assembly.target.kind,
        output_format=output_format,
        audience=audience,
        language=language,
        source_path=assembly.generated_path,
        output_path=output_path,
        command=command,
        build_manifest_path=build_manifest_path,
        dependency_manifest_path=dependency_manifest_path,
        leakage_report_path=leakage_report_path,
        search_index_path=search_index_path,
    )


def quarto_format_for_output(output_format: RenderableFormat) -> str:
    if output_format == SLIDES_PDF_OUTPUT_FORMAT:
        return "revealjs"
    return FORMAT_TO_QUARTO[output_format]


def rendered_output_name_for_target(
    target_id: str,
    *,
    output_format: RenderableFormat,
    audience: str,
) -> str:
    if output_format == SLIDES_PDF_OUTPUT_FORMAT:
        return build_output_name(target_id, "revealjs", audience=audience)
    return build_output_name(target_id, output_format, audience=audience)


def locate_rendered_output(
    *,
    generated_path: Path,
    output_name: str,
    root: Path,
    result: subprocess.CompletedProcess[str] | None,
) -> Path:
    rendered_candidates = [
        generated_path.parent / output_name,
        root / output_name,
    ]
    rendered_output = next((path for path in rendered_candidates if path.exists()), None)
    if rendered_output is None:
        if result is not None and should_retry_quarto_render(
            result.stderr.strip() or result.stdout.strip() or "quarto render failed"
        ):
            raise BuildError("expected rendered output missing after retryable quarto render")
        raise BuildError(
            "expected rendered output missing: "
            + ", ".join(str(path.relative_to(root)) for path in rendered_candidates)
        )
    return rendered_output


def rendered_support_path(*, generated_path: Path, output_name: str) -> Path:
    return generated_path.parent / f"{Path(output_name).stem}_files"


def resolve_slides_pdf_browser() -> str:
    configured = os.environ.get(SLIDES_PDF_BROWSER_ENV)
    if configured:
        return configured
    for candidate in SLIDES_PDF_BROWSER_CANDIDATES:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise BuildError(
        "slides-pdf export requires a Chromium-based browser. "
        f"Set {SLIDES_PDF_BROWSER_ENV} or install one of: "
        + ", ".join(SLIDES_PDF_BROWSER_CANDIDATES)
    )


def export_revealjs_pdf(
    *,
    revealjs_output_path: Path,
    output_path: Path,
    root: Path,
) -> list[str]:
    browser = resolve_slides_pdf_browser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print_url = revealjs_output_path.resolve().as_uri() + "?print-pdf"
    commands_to_try = browser_commands_for_slide_pdf(
        browser=browser,
        output_path=output_path,
        print_url=print_url,
    )
    last_error = "slides-pdf export failed"

    for candidate_command in commands_to_try:
        if output_path.exists():
            output_path.unlink()
        result = subprocess.run(
            candidate_command,
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            env=build_env(root),
        )
        if result.returncode == 0 and output_path.exists():
            return candidate_command
        last_error = result.stderr.strip() or result.stdout.strip() or "slides-pdf export failed"

    raise BuildError(last_error)


def browser_commands_for_slide_pdf(
    *,
    browser: str,
    output_path: Path,
    print_url: str,
) -> list[list[str]]:
    common_flags = [
        "--headless=new",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-crash-reporter",
        "--disable-breakpad",
        "--no-first-run",
        "--no-default-browser-check",
        "--allow-file-access-from-files",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=10000",
        f"--print-to-pdf={output_path}",
    ]
    commands = [
        [browser, *common_flags, print_url],
        [browser, *common_flags, "--no-sandbox", print_url],
    ]
    unique_commands: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for command in commands:
        key = tuple(command)
        if key in seen:
            continue
        seen.add(key)
        unique_commands.append(command)
    return unique_commands


def build_env(root: Path) -> dict[str, str]:
    cache_dir = root / "build" / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (root / "site_libs" / "quarto-search").mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("QUARTO_CACHE_DIR", str(cache_dir))
    env.setdefault("XDG_CACHE_HOME", str(cache_dir))
    return env


def ensure_generated_staging(root: Path) -> None:
    generated_root = generated_dir(root)
    generated_root.mkdir(parents=True, exist_ok=True)
    (generated_root / ".gitkeep").write_text("", encoding="utf-8")


def prepare_generated_target_dir(generated_path: Path) -> None:
    target_dir = generated_path.parent
    if target_dir.exists():
        shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(parents=True, exist_ok=True)


def sync_site_libs(root: Path, output_dir: Path) -> None:
    source_candidates = [
        output_dir / "site_libs",
        root / "site_libs",
    ]
    source = next((candidate for candidate in source_candidates if candidate.exists()), None)
    if source is None:
        return
    destination = root / "build" / "site_libs"
    shutil.copytree(source, destination, dirs_exist_ok=True)


def write_build_reports(
    *,
    assembly: AssemblyDocument,
    command: list[str],
    commands: list[list[str]],
    output_path: Path,
    search_index_path: Path | None,
    root: Path,
) -> tuple[Path, Path, Path]:
    report_dir = (
        reports_dir(root)
        / "builds"
        / assembly.audience
        / assembly.language
        / assembly.output_format
        / assembly.target.output_category
        / assembly.target.identifier
    )
    report_dir.mkdir(parents=True, exist_ok=True)

    build_manifest_path = report_dir / "build-manifest.json"
    dependency_manifest_path = report_dir / "dependency-manifest.json"
    leakage_report_path = report_dir / "teacher-leakage-report.json"

    build_manifest_payload = assembly.build_manifest_payload()
    generated_artifacts = collect_generated_artifacts(assembly=assembly, root=root)
    build_manifest_payload.update(
        {
            "command": command,
            "commands": commands,
            "output_path": str(output_path.relative_to(root)),
            "build_manifest_path": str(build_manifest_path.relative_to(root)),
            "dependency_manifest_path": str(dependency_manifest_path.relative_to(root)),
            "leakage_report_path": str(leakage_report_path.relative_to(root)),
            "search_index_path": (
                str(search_index_path.relative_to(root)) if search_index_path else None
            ),
            "generated_artifacts": generated_artifacts,
        }
    )
    assignment_details = assignment_manifest_details(assembly, generated_artifacts)
    if assignment_details is not None:
        build_manifest_payload["assignment"] = assignment_details
    dependency_manifest_payload = assembly.dependency_manifest_payload()
    leakage_report_payload = build_leakage_report(assembly, output_path, root)

    build_manifest_path.write_text(
        json.dumps(build_manifest_payload, indent=2),
        encoding="utf-8",
    )
    dependency_manifest_path.write_text(
        json.dumps(dependency_manifest_payload, indent=2),
        encoding="utf-8",
    )
    leakage_report_path.write_text(
        json.dumps(leakage_report_payload, indent=2),
        encoding="utf-8",
    )
    return build_manifest_path, dependency_manifest_path, leakage_report_path


def should_retry_quarto_render(error_message: str) -> bool:
    return (
        "build/generated" in error_message
        or ".learnforge-generated" in error_message
        or "No valid input files passed to render" in error_message
    )


def build_leakage_report(
    assembly: AssemblyDocument,
    output_path: Path,
    root: Path,
) -> dict[str, object]:
    generated_source_text = assembly.markdown
    output_text = output_path.read_text(encoding="utf-8", errors="ignore")
    teacher_blocks_found = sum(item.teacher_blocks_found for item in assembly.leakage_observations)
    teacher_blocks_removed = sum(
        item.teacher_blocks_removed for item in assembly.leakage_observations
    )
    solution_files_found = len(assembly.solution_observations)
    solution_files_included = sum(
        1 for item in assembly.solution_observations if item.included_in_output
    )

    generated_source_has_marker = bool(TEACHER_BLOCK_SOURCE_RE.search(generated_source_text))
    output_has_marker = bool(TEACHER_BLOCK_OUTPUT_RE.search(output_text))
    generated_source_has_solution_marker = SOLUTION_BLOCK_MARKER in generated_source_text
    output_has_solution_marker = SOLUTION_BLOCK_MARKER in output_text

    status = "not_applicable"
    if assembly.audience == "student":
        status = (
            "clean"
            if teacher_blocks_removed == teacher_blocks_found
            and not generated_source_has_marker
            and not output_has_marker
            and solution_files_included == 0
            and not generated_source_has_solution_marker
            and not output_has_solution_marker
            else "leak-detected"
        )

    return {
        "target": {
            "id": assembly.target.identifier,
            "kind": assembly.target.kind,
        },
        "audience": assembly.audience,
        "language": assembly.language,
        "format": assembly.output_format,
        "status": status,
        "teacher_blocks_found": teacher_blocks_found,
        "teacher_blocks_removed": teacher_blocks_removed,
        "solution_files_found": solution_files_found,
        "solution_files_included": solution_files_included,
        "generated_source_contains_teacher_marker": generated_source_has_marker,
        "output_contains_teacher_marker": output_has_marker,
        "generated_source_contains_solution_marker": generated_source_has_solution_marker,
        "output_contains_solution_marker": output_has_solution_marker,
        "generated_source_path": str(assembly.generated_path.relative_to(root)),
        "output_path": str(output_path.relative_to(root)),
        "details": [
            {
                "source_path": item.source_path,
                "teacher_blocks_found": item.teacher_blocks_found,
                "teacher_blocks_removed": item.teacher_blocks_removed,
                "student_blocks_found": item.student_blocks_found,
                "student_blocks_removed": item.student_blocks_removed,
            }
            for item in assembly.leakage_observations
        ],
        "solution_details": [
            {
                "exercise_id": item.exercise_id,
                "source_path": item.source_path,
                "visibility": item.visibility,
                "included_in_output": item.included_in_output,
                "reason": item.reason,
            }
            for item in assembly.solution_observations
        ],
        "resource_workflow": assembly.resource_workflow_summary,
    }


def write_student_site_search_index(
    *,
    index: RepositoryIndex,
    language: str,
    root: Path,
) -> Path:
    output_path = student_search_index_path(root, language)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    site_root = exports_dir(root) / "student" / language / "html"
    payload = {
        "language": language,
        "entries": student_site_search_entries(
            index=index,
            language=language,
            root=root,
            site_root=site_root,
        ),
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def write_html_shell_assets(*, audience: str, language: str, root: Path) -> list[Path]:
    written_paths: list[Path] = []
    for filename in ("learnforge-shell.css", "learnforge-shell.js"):
        source_path = WEB_ASSETS_DIR / filename
        if not source_path.exists():
            raise BuildError(f"missing html shell asset: {source_path}")
        destination_path = html_shell_asset_path(root, audience, language, filename)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)
        written_paths.append(destination_path)
    return written_paths


def student_site_targets(
    *,
    index: RepositoryIndex,
    language: str,
) -> list[StudentSiteTarget]:
    visible_courses = student_visible_courses(index=index, language=language)
    visible_objects = student_visible_objects(index=index, language=language)
    visible_html_objects = student_visible_html_objects(index=index, language=language)

    targets = [StudentSiteTarget(target_id="home", target_kind="home")]
    targets.extend(
        StudentSiteTarget(target_id=record.model.id, target_kind="course")
        for record in visible_courses
    )
    targets.extend(
        StudentSiteTarget(
            target_id=record.model.id,
            target_kind=student_target_kind_for_object(record),
        )
        for record in visible_html_objects
    )
    targets.extend(
        StudentSiteTarget(target_id=f"topic-{topic}", target_kind="topic-listing")
        for topic in collect_topics(visible_objects)
    )
    targets.extend(
        StudentSiteTarget(
            target_id=f"resources-{record.model.id}",
            target_kind="resource-listing",
        )
        for record in visible_courses
        if course_has_student_visible_resources(
            course_record=record,
            objects=visible_objects,
        )
    )
    return targets


def student_site_search_entries(
    *,
    index: RepositoryIndex,
    language: str,
    root: Path,
    site_root: Path,
) -> list[dict[str, object]]:
    visible_objects = student_visible_objects(index=index, language=language)
    entries: list[dict[str, object]] = []
    for target in student_site_targets(index=index, language=language):
        href = str(
            planned_target_output_path(
                root,
                audience="student",
                language=language,
                output_format="html",
                target_kind=target.target_kind,
                target_id=target.target_id,
            ).relative_to(site_root)
        )
        if target.target_kind == "home":
            entries.append(
                {
                    "id": "home",
                    "kind": "home",
                    "title": "LearnForge",
                    "description": (
                        "Browse courses, topics, and featured resources."
                        if language == "en"
                        else "Bla gjennom kurs, temaer og utvalgte ressurser."
                    ),
                    "topics": [],
                    "tags": [],
                    "courses": [],
                    "href": href,
                }
            )
            continue
        if target.target_kind == "course":
            record = index.courses[target.target_id]
            entries.append(
                {
                    "id": record.model.id,
                    "kind": "course",
                    "title": record.model.title[language],
                    "description": record.model.summary[language],
                    "topics": [],
                    "tags": [],
                    "courses": [record.model.id],
                    "href": href,
                }
            )
            continue
        if target.target_kind == "topic-listing":
            topic = target.target_id.removeprefix("topic-")
            entries.append(
                {
                    "id": target.target_id,
                    "kind": "topic-listing",
                    "title": humanize_slug(topic),
                    "description": ("Topic listing" if language == "en" else "Temaoversikt"),
                    "topics": [topic],
                    "tags": [],
                    "courses": sorted(
                        {
                            course_id
                            for record in visible_objects
                            if topic in record.model.topics
                            for course_id in record.model.courses
                        }
                    ),
                    "href": href,
                }
            )
            continue
        if target.target_kind == "resource-listing":
            course_id = target.target_id.removeprefix("resources-")
            course_record = index.courses[course_id]
            entries.append(
                {
                    "id": target.target_id,
                    "kind": "resource-listing",
                    "title": (
                        f"Resources for {course_record.model.title[language]}"
                        if language == "en"
                        else f"Ressurser for {course_record.model.title[language]}"
                    ),
                    "description": (
                        "Course resource listing" if language == "en" else "Kursressursoversikt"
                    ),
                    "topics": [],
                    "tags": ["resources"],
                    "courses": [course_record.model.id],
                    "href": href,
                }
            )
            continue
        record = index.objects[target.target_id]
        description = ""
        if record.model.kind == "resource":
            description = record.model.summary.get(language) or record.model.why_selected.get(
                language,
                "",
            )
        elif record.model.kind == "exercise":
            description = f"{record.model.exercise_type} exercise"
        elif record.model.kind == "concept":
            description = record.model.level
        elif record.model.kind == "figure":
            description = record.model.caption[language]
        elif isinstance(record.model, Collection):
            description = localized_collection_description(
                record.model.collection_kind,
                language=language,
                item_count=len(record.model.items),
            )
        entries.append(
            {
                "id": record.model.id,
                "kind": target.target_kind,
                "title": record.model.title[language],
                "description": description,
                "topics": record.model.topics,
                "tags": record.model.tags,
                "courses": record.model.courses,
                "href": href,
            }
        )
    return entries


def student_visible_courses(
    *,
    index: RepositoryIndex,
    language: str,
) -> list[IndexedCourse]:
    return [
        record
        for record in sorted(index.courses.values(), key=lambda item: item.model.id)
        if record.model.visibility not in {"private", "teacher"}
        and record.model.status in {"approved", "published"}
        and language in record.model.languages
    ]


def student_visible_objects(
    *,
    index: RepositoryIndex,
    language: str,
) -> list[IndexedObject]:
    return [
        record
        for record in sorted(index.objects.values(), key=lambda item: item.model.id)
        if is_student_visible_in_language(record, language)
    ]


def student_visible_html_objects(
    *,
    index: RepositoryIndex,
    language: str,
) -> list[IndexedObject]:
    return [
        record
        for record in student_visible_objects(index=index, language=language)
        if "html" in record.model.outputs
    ]


def course_has_student_visible_resources(
    *,
    course_record: IndexedCourse,
    objects: list[IndexedObject],
) -> bool:
    return any(
        isinstance(record.model, Resource) and course_record.model.id in record.model.courses
        for record in objects
    )


def student_target_kind_for_object(record: IndexedObject) -> str:
    return record.model.kind if record.model.kind != "collection" else "collection"


def is_student_visible_in_language(record: IndexedObject, language: str) -> bool:
    if record.model.visibility in {"private", "teacher"}:
        return False
    if isinstance(record.model, Resource):
        return resource_student_visibility_decision(
            record,
            language=language,
            require_output_format="html",
        ).visible_to_student
    if record.model.status not in {"approved", "published"}:
        return False
    if language not in record.model.languages:
        return False
    return record.model.translation_status.get(language) == "approved"


def collect_generated_artifacts(
    *,
    assembly: AssemblyDocument,
    root: Path,
) -> list[dict[str, str]]:
    candidate_formats = ["html", "pdf", "revealjs", "slides-pdf", "handout", "exercise-sheet"]
    if assembly.target.kind == "home":
        candidate_formats = ["html"]

    artifacts: list[dict[str, str]] = []
    for output_format in candidate_formats:
        output_path = planned_target_output_path(
            root,
            audience=assembly.audience,
            language=assembly.language,
            output_format=output_format,
            target_kind=assembly.target.kind,
            target_id=assembly.target.identifier,
        )
        if not output_path.exists():
            continue
        artifacts.append(
            {
                "format": output_format,
                "path": str(output_path.relative_to(root)),
            }
        )
    return artifacts


def assignment_manifest_details(
    assembly: AssemblyDocument,
    generated_artifacts: list[dict[str, str]],
) -> dict[str, object] | None:
    included_exercise_ids = sorted(
        {
            edge.target_id
            for edge in assembly.dependency_edges
            if edge.source_id == assembly.target.identifier
            and edge.relationship == "assignment-item"
        }
    )
    if not included_exercise_ids:
        return None

    return {
        "included_exercise_ids": included_exercise_ids,
        "course_context_ids": sorted(
            {
                edge.target_id
                for edge in assembly.dependency_edges
                if edge.source_id == assembly.target.identifier
                and edge.relationship == "used-in-course"
            }
        ),
        "linked_concept_ids": sorted(
            {
                edge.target_id
                for edge in assembly.dependency_edges
                if edge.source_id == assembly.target.identifier
                and edge.relationship == "assignment-concept"
            }
        ),
        "linked_resource_ids": sorted(
            {
                edge.target_id
                for edge in assembly.dependency_edges
                if edge.source_id == assembly.target.identifier
                and edge.relationship == "assignment-resource"
            }
        ),
        "discovered_solution_files": sorted(
            {item.source_path for item in assembly.solution_observations}
        ),
        "included_solution_files": sorted(
            {item.source_path for item in assembly.solution_observations if item.included_in_output}
        ),
        "generated_artifacts": generated_artifacts,
    }


def localized_collection_description(
    collection_kind: str,
    *,
    language: str,
    item_count: int,
) -> str:
    if language == "nb":
        labels = {
            "lecture": "Forelesning",
            "assignment": "Oppgaveark",
            "module": "Modul",
            "reading-list": "Leseliste",
        }
        return f"{labels.get(collection_kind, 'Samling')} med {item_count} innslag"

    labels = {
        "lecture": "Lecture",
        "assignment": "Assignment",
        "module": "Module",
        "reading-list": "Reading list",
    }
    return f"{labels.get(collection_kind, 'Collection')} with {item_count} items"

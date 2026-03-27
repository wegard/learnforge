from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import asdict
from datetime import date
from typing import Annotated

import typer

from app.build import BuildError, build_target
from app.config import AUDIENCES, LANGUAGES, OUTPUT_FORMATS, REPO_ROOT
from app.indexer import load_repository
from app.publish import publish_student_site
from app.resource_workflow import transition_resource_to_state, write_stale_resource_report
from app.scaffold import scaffold_object
from app.search import search_repository
from app.translation import build_course_translation_report
from app.validator import validate_repository, write_validation_report

app = typer.Typer(help="Thin CLI for LearnForge bootstrap workflows.", no_args_is_help=True)
stale_app = typer.Typer(help="Inspect stale-content reports.")
app.add_typer(stale_app, name="stale")


def _parse_iso_date(value: str | None, *, option_name: str) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise typer.BadParameter(f"{option_name} must be an ISO date like 2026-03-18") from exc


@app.command()
def validate(
    json_output: bool = typer.Option(False, "--json", help="Print the validation report as JSON."),
) -> None:
    report = validate_repository(REPO_ROOT)
    report_path, build_summary_path = write_validation_report(report, REPO_ROOT)
    if json_output:
        typer.echo(
            json.dumps(
                {
                    "status": report.status,
                    "issue_count": report.issue_count,
                    "error_count": report.error_count,
                    "warning_count": report.warning_count,
                    "object_count": report.object_count,
                    "course_count": report.course_count,
                    "issues": [asdict(issue) for issue in report.issues],
                    "category_counts": report.category_counts,
                    "search_index_path": report.search_index_path,
                    "build_summary_path": str(build_summary_path.relative_to(REPO_ROOT)),
                    "translation_coverage": report.translation_coverage,
                    "resource_workflow": report.resource_workflow,
                    "representative_target_count": report.representative_target_count,
                    "representative_target_failure_count": (
                        report.representative_target_failure_count
                    ),
                    "report_path": str(report_path.relative_to(REPO_ROOT)),
                },
                indent=2,
            )
        )
    else:
        typer.echo(
            f"Validated {report.object_count} objects and {report.course_count} courses. "
            f"Errors: {report.error_count}. Warnings: {report.warning_count}. "
            f"Report: {report_path.relative_to(REPO_ROOT)}"
        )
        typer.echo(f"Build summary: {build_summary_path.relative_to(REPO_ROOT)}")
        typer.echo(
            "Representative targets: "
            f"{report.representative_target_count - report.representative_target_failure_count}/"
            f"{report.representative_target_count} passed"
        )
        typer.echo(
            "Resource workflow: "
            f"candidate={report.resource_workflow['status_counts']['candidate']}, "
            f"reviewed={report.resource_workflow['status_counts']['reviewed']}, "
            f"approved={report.resource_workflow['status_counts']['approved']}, "
            f"published={report.resource_workflow['status_counts']['published']}, "
            f"stale={report.resource_workflow['stale_resource_count']}"
        )
        if report.search_index_path:
            typer.echo(f"Search index: {report.search_index_path}")
        for issue in report.issues:
            typer.echo(f"[{issue.severity}:{issue.code}] {issue.path}: {issue.message}")
    raise typer.Exit(code=0 if report.ok else 1)


@app.command()
def build(
    target_id: str = typer.Argument(..., help="Object, collection, or course identifier."),
    audience: str = typer.Option("student", "--audience", case_sensitive=False),
    lang: str = typer.Option("en", "--lang", case_sensitive=False),
    format: str = typer.Option("html", "--format", case_sensitive=False),
) -> None:
    if audience not in AUDIENCES:
        raise typer.BadParameter(f"audience must be one of {AUDIENCES}")
    if lang not in LANGUAGES:
        raise typer.BadParameter(f"lang must be one of {LANGUAGES}")
    if format not in OUTPUT_FORMATS:
        raise typer.BadParameter(f"format must be one of {OUTPUT_FORMATS}")

    try:
        artifact = build_target(
            target_id,
            audience=audience,
            language=lang,
            output_format=format,
            root=REPO_ROOT,
        )
    except BuildError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Built {artifact.target_id} -> {artifact.output_path.relative_to(REPO_ROOT)}")
    typer.echo(f"Build manifest: {artifact.build_manifest_path.relative_to(REPO_ROOT)}")
    typer.echo(f"Dependency manifest: {artifact.dependency_manifest_path.relative_to(REPO_ROOT)}")
    typer.echo(f"Teacher leakage report: {artifact.leakage_report_path.relative_to(REPO_ROOT)}")
    if artifact.search_index_path is not None:
        typer.echo(f"Student search index: {artifact.search_index_path.relative_to(REPO_ROOT)}")


@app.command()
def publish(
    lang: Annotated[
        list[str] | None,
        typer.Option(
            "--lang",
            case_sensitive=False,
            help="Repeat to limit publishing to selected languages.",
        ),
    ] = None,
) -> None:
    selected_languages = lang or list(LANGUAGES)
    if any(language not in LANGUAGES for language in selected_languages):
        raise typer.BadParameter(f"lang must be one of {LANGUAGES}")

    try:
        artifact = publish_student_site(
            languages=selected_languages,
            root=REPO_ROOT,
        )
    except BuildError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Published student site -> {artifact.publish_root.relative_to(REPO_ROOT)}")
    typer.echo(f"Publish manifest: {artifact.manifest_path.relative_to(REPO_ROOT)}")
    typer.echo(f"Languages: {', '.join(artifact.languages)}")


@app.command("new")
def new_object(
    kind: str = typer.Argument(..., help="Object kind to scaffold."),
    identifier: str = typer.Argument(..., help="Stable slug id."),
    owner: str = typer.Option("vegard", "--owner"),
    collection_kind: str = typer.Option("lecture", "--collection-kind"),
) -> None:
    supported = {"concept", "exercise", "figure", "resource", "collection"}
    if kind not in supported:
        raise typer.BadParameter(f"kind must be one of {sorted(supported)}")
    try:
        result = scaffold_object(
            kind,
            identifier,
            root=REPO_ROOT,
            owner=owner,
            collection_kind=collection_kind,
        )
    except FileExistsError as exc:
        typer.echo(f"path already exists: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Created {kind} scaffold at {result.target_dir.relative_to(REPO_ROOT)}")


@app.command()
def open(
    target_id: str = typer.Argument(..., help="Object or course identifier."),
    lang: str = typer.Option("en", "--lang", case_sensitive=False),
    meta: bool = typer.Option(False, "--meta", help="Open metadata instead of the language note."),
) -> None:
    index, _ = load_repository(REPO_ROOT, collect_errors=False)
    if target_id in index.objects:
        record = index.objects[target_id]
        path = (
            record.meta_path
            if meta or record.model.kind == "collection"
            else record.note_path(lang)
        )
    elif target_id in index.courses:
        record = index.courses[target_id]
        path = record.course_path if meta else record.syllabus_path(lang)
    else:
        typer.echo(f"unknown target id: {target_id}", err=True)
        raise typer.Exit(code=1)

    editor = os.environ.get("EDITOR", "nvim")
    command = shlex.split(editor) + [str(path)]
    subprocess.run(command, cwd=REPO_ROOT, check=False)


@app.command()
def tui(
    lang: str = typer.Option("en", "--lang", case_sensitive=False),
) -> None:
    """Launch the interactive dashboard."""
    if lang not in LANGUAGES:
        raise typer.BadParameter(f"lang must be one of {LANGUAGES}")
    from app.tui import launch

    launch(default_language=lang)


@app.command()
def search(query: str = typer.Argument(..., help="Free-text query.")) -> None:
    results, index_path = search_repository(query, REPO_ROOT)
    typer.echo(f"Search index: {index_path.relative_to(REPO_ROOT)}")
    if not results:
        typer.echo("No matches.")
        return
    for result in results:
        typer.echo(f"{result.identifier} [{result.kind}] {result.title} :: {result.path}")


@app.command("translation-status")
def translation_status(
    course_id: str = typer.Argument(..., help="Course identifier."),
    lang: str = typer.Option("en", "--lang", case_sensitive=False),
    json_output: bool = typer.Option(False, "--json", help="Print the translation report as JSON."),
) -> None:
    if lang not in LANGUAGES:
        raise typer.BadParameter(f"lang must be one of {LANGUAGES}")
    try:
        report = build_course_translation_report(course_id, language=lang, root=REPO_ROOT)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    if json_output:
        typer.echo(json.dumps(report, indent=2))
        raise typer.Exit(code=0)

    typer.echo(
        f"Course translation status: {report['course_id']} [{report['language']}] "
        f"{report['approved_count']}/{report['entry_count']} approved"
    )
    for entry in report["entries"]:
        note_status = "-"
        if entry["note_exists"] is not None:
            note_status = "yes" if entry["note_exists"] else "no"
        solution_status = "-"
        if entry["solution_exists"] is not None:
            solution_status = "yes" if entry["solution_exists"] else "no"
        source_words = entry["source_word_count_nb"]
        source_display = "-" if source_words is None else str(source_words)
        typer.echo(
            f"{entry['kind']:10} {entry['identifier']:35} "
            f"state={entry['translation_status']:12} "
            f"langs={','.join(entry['languages']):7} "
            f"note={note_status:3} solution={solution_status:3} nb_words={source_display}"
        )


@app.command("approve")
def approve_resource(
    resource_id: str = typer.Argument(..., help="Resource identifier."),
    by: str = typer.Option(os.environ.get("USER", "unknown"), "--by"),
    on: str | None = typer.Option(None, "--on", help="Approval date in YYYY-MM-DD."),
    publish: bool = typer.Option(
        False,
        "--publish",
        help="Transition from approved to published instead of reviewed to approved.",
    ),
) -> None:
    target_state = "published" if publish else "approved"
    acted_on = _parse_iso_date(on, option_name="--on") or date.today()
    try:
        meta_path, model = transition_resource_to_state(
            resource_id,
            target_state=target_state,
            actor=by,
            acted_on=acted_on,
            root=REPO_ROOT,
        )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Updated {model.id} -> {model.status} in {meta_path.relative_to(REPO_ROOT)}")
    if model.approved_by and model.approved_on:
        typer.echo(f"Approval metadata: {model.approved_by} on {model.approved_on.isoformat()}")


@stale_app.command("resources")
def stale_resources(
    json_output: bool = typer.Option(False, "--json", help="Print the stale report as JSON."),
    today: str | None = typer.Option(None, "--today", help="Reference date in YYYY-MM-DD."),
) -> None:
    reference_date = _parse_iso_date(today, option_name="--today")
    try:
        report_path, payload = write_stale_resource_report(REPO_ROOT, today=reference_date)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    if json_output:
        typer.echo(json.dumps(payload, indent=2))
        raise typer.Exit(code=0)

    typer.echo(
        f"Stale resources: {payload['stale_resource_count']} / {payload['resource_count']}. "
        f"Report: {report_path.relative_to(REPO_ROOT)}"
    )
    for item in payload["stale_resources"]:
        typer.echo(
            f"- {item['id']} [{item['status']}] review_after={item['review_after']} "
            f"stale_flag={item['stale_flag']}"
        )


@app.command("new-delivery")
def new_delivery(
    course_id: str = typer.Argument(..., help="Course identifier."),
    term: str = typer.Option(..., "--term", help="Term identifier, e.g. spring-2026."),
    lang: str = typer.Option("en", "--lang", case_sensitive=False),
    start: str | None = typer.Option(None, "--start", help="First lecture date YYYY-MM-DD."),
) -> None:
    """Scaffold a new delivery manifest from an existing course plan."""
    from app.delivery import scaffold_delivery

    if lang not in LANGUAGES:
        raise typer.BadParameter(f"lang must be one of {LANGUAGES}")
    start_date = _parse_iso_date(start, option_name="--start")
    try:
        manifest_path = scaffold_delivery(
            course_id,
            term=term,
            language=lang,
            start_date=start_date,
            root=REPO_ROOT,
        )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Created delivery manifest: {manifest_path.relative_to(REPO_ROOT)}")


@app.command("delivery-status")
def delivery_status_cmd(
    manifest_id: str = typer.Argument(..., help="Delivery manifest identifier."),
    json_output: bool = typer.Option(False, "--json", help="Print as JSON."),
) -> None:
    """Show delivery status overview."""
    from app.delivery import delivery_status_json, format_delivery_status

    try:
        if json_output:
            typer.echo(json.dumps(delivery_status_json(manifest_id, root=REPO_ROOT), indent=2))
        else:
            typer.echo(format_delivery_status(manifest_id, root=REPO_ROOT))
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc


@app.command("deliver")
def deliver(
    manifest_id: str = typer.Argument(..., help="Delivery manifest identifier."),
    ready_only: bool = typer.Option(False, "--ready-only", help="Build only ready lectures."),
    lecture: str | None = typer.Option(None, "--lecture", help="Build a single lecture."),
) -> None:
    """Build all lectures and assignments for a delivery manifest."""
    from app.delivery import build_delivery

    try:
        result = build_delivery(
            manifest_id,
            root=REPO_ROOT,
            ready_only=ready_only,
            lecture_filter=lecture,
        )
    except (ValueError, BuildError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Delivery build: {result.manifest_id}")
    typer.echo(
        f"Built {len(result.built_lectures)} lectures, {len(result.built_assignments)} assignments"
    )
    if result.skipped_lectures:
        typer.echo(f"Skipped lectures: {', '.join(result.skipped_lectures)}")
    if result.skipped_assignments:
        typer.echo(f"Skipped assignments: {', '.join(result.skipped_assignments)}")
    typer.echo(f"Total artifacts: {len(result.artifacts)}")
    if result.delivery_report_path:
        typer.echo(f"Report: {result.delivery_report_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    app()

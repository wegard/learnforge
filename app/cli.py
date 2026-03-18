from __future__ import annotations

import json
import os
import shlex
import subprocess

import typer

from app.build import BuildError, build_target
from app.config import AUDIENCES, LANGUAGES, OUTPUT_FORMATS, REPO_ROOT
from app.indexer import load_repository
from app.scaffold import scaffold_object
from app.search import search_repository
from app.validator import validate_repository, write_validation_report

app = typer.Typer(help="Thin CLI for LearnForge bootstrap workflows.", no_args_is_help=True)


@app.command()
def validate(
    json_output: bool = typer.Option(False, "--json", help="Print the validation report as JSON."),
) -> None:
    report = validate_repository(REPO_ROOT)
    report_path = write_validation_report(report, REPO_ROOT)
    if json_output:
        typer.echo(
            json.dumps(
                {
                    "issue_count": report.issue_count,
                    "object_count": report.object_count,
                    "course_count": report.course_count,
                    "issues": [issue.__dict__ for issue in report.issues],
                    "search_index_path": report.search_index_path,
                    "report_path": str(report_path.relative_to(REPO_ROOT)),
                },
                indent=2,
            )
        )
    else:
        typer.echo(
            f"Validated {report.object_count} objects and {report.course_count} courses. "
            f"Issues: {report.issue_count}. Report: {report_path.relative_to(REPO_ROOT)}"
        )
        if report.search_index_path:
            typer.echo(f"Search index: {report.search_index_path}")
        for issue in report.issues:
            typer.echo(f"[{issue.code}] {issue.path}: {issue.message}")
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
def search(query: str = typer.Argument(..., help="Free-text query.")) -> None:
    results, index_path = search_repository(query, REPO_ROOT)
    typer.echo(f"Search index: {index_path.relative_to(REPO_ROOT)}")
    if not results:
        typer.echo("No matches.")
        return
    for result in results:
        typer.echo(f"{result.identifier} [{result.kind}] {result.title} :: {result.path}")


if __name__ == "__main__":
    app()

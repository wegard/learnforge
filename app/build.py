from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.assembly import (
    AssemblyDocument,
    AssemblyError,
    assemble_target,
    build_output_name,
)
from app.config import REPO_ROOT, exports_dir, reports_dir
from app.indexer import load_repository

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
    build_manifest_path: Path
    dependency_manifest_path: Path
    leakage_report_path: Path


class BuildError(RuntimeError):
    pass


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

    try:
        assembly = assemble_target(
            target_id,
            index=index,
            audience=audience,
            language=language,
            output_format=output_format,
            root=root,
        )
    except AssemblyError as exc:
        raise BuildError(str(exc)) from exc

    output_dir = (
        exports_dir(root)
        / audience
        / language
        / output_format
        / assembly.target.output_category
        / target_id
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_name = build_output_name(target_id, output_format)
    command = [
        "quarto",
        "render",
        str(assembly.generated_path.relative_to(root)),
        "--profile",
        f"{audience},{language}",
        "--to",
        FORMAT_TO_QUARTO[output_format],
        "--output",
        output_name,
        "--output-dir",
        str(output_dir.relative_to(root)),
    ]

    result = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        env=build_env(root),
    )
    if result.returncode != 0:
        raise BuildError(result.stderr.strip() or result.stdout.strip() or "quarto render failed")

    output_path = output_dir / output_name
    build_manifest_path, dependency_manifest_path, leakage_report_path = write_build_reports(
        assembly=assembly,
        command=command,
        output_path=output_path,
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
    )


def build_env(root: Path) -> dict[str, str]:
    cache_dir = root / "build" / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (root / "site_libs" / "quarto-search").mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("QUARTO_CACHE_DIR", str(cache_dir))
    env.setdefault("XDG_CACHE_HOME", str(cache_dir))
    return env


def write_build_reports(
    *,
    assembly: AssemblyDocument,
    command: list[str],
    output_path: Path,
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
    build_manifest_payload.update(
        {
            "command": command,
            "output_path": str(output_path.relative_to(root)),
            "build_manifest_path": str(build_manifest_path.relative_to(root)),
            "dependency_manifest_path": str(dependency_manifest_path.relative_to(root)),
            "leakage_report_path": str(leakage_report_path.relative_to(root)),
        }
    )
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


def build_leakage_report(
    assembly: AssemblyDocument,
    output_path: Path,
    root: Path,
) -> dict[str, object]:
    generated_source_text = assembly.generated_path.read_text(encoding="utf-8")
    output_text = output_path.read_text(encoding="utf-8", errors="ignore")
    teacher_blocks_found = sum(item.teacher_blocks_found for item in assembly.leakage_observations)
    teacher_blocks_removed = sum(
        item.teacher_blocks_removed for item in assembly.leakage_observations
    )

    generated_source_has_marker = (
        ".teacher-only" in generated_source_text or "teacher-only" in generated_source_text
    )
    output_has_marker = ".teacher-only" in output_text or "teacher-only" in output_text

    status = "not_applicable"
    if assembly.audience == "student":
        status = (
            "clean"
            if teacher_blocks_removed == teacher_blocks_found
            and not generated_source_has_marker
            and not output_has_marker
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
        "generated_source_contains_teacher_marker": generated_source_has_marker,
        "output_contains_teacher_marker": output_has_marker,
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
    }

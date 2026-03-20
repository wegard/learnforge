from __future__ import annotations

import json
import shutil
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from html import escape
from pathlib import Path

from app.build import (
    BuildError,
    build_target,
    student_site_targets,
    write_html_shell_assets,
    write_student_site_search_index,
)
from app.config import LANGUAGES, REPO_ROOT, exports_dir, publish_dir, reports_dir
from app.indexer import load_repository


@dataclass(slots=True)
class PublishArtifact:
    publish_root: Path
    manifest_path: Path
    languages: tuple[str, ...]
    total_target_count: int
    target_counts_by_language: dict[str, dict[str, int]]


def publish_student_site(
    *,
    languages: Sequence[str] = LANGUAGES,
    root: Path = REPO_ROOT,
) -> PublishArtifact:
    selected_languages = normalize_publish_languages(languages)
    index, errors = load_repository(root, collect_errors=False)
    if errors:
        raise BuildError("repository contains load errors")

    publish_root = publish_dir(root) / "student-site"
    publish_report_dir = reports_dir(root) / "publish" / "student-site"
    reset_directory(publish_root)
    reset_directory(publish_report_dir)

    target_counts_by_language: dict[str, dict[str, int]] = {}
    language_details: list[dict[str, object]] = []
    total_target_count = 0

    for language in selected_languages:
        export_root = exports_dir(root) / "student" / language / "html"
        reset_directory(export_root)

        targets = student_site_targets(index=index, language=language)
        target_counts = Counter(target.target_kind for target in targets)
        total_target_count += len(targets)

        for target in targets:
            build_target(
                target.target_id,
                audience="student",
                language=language,
                output_format="html",
                root=root,
                index=index,
                sync_html_shell_assets=False,
                sync_student_search_index=False,
            )

        write_html_shell_assets(audience="student", language=language, root=root)
        search_index_path = write_student_site_search_index(
            index=index,
            language=language,
            root=root,
        )

        publish_language_root = publish_root / language
        shutil.copytree(export_root, publish_language_root)
        target_counts_by_language[language] = dict(sorted(target_counts.items()))
        language_details.append(
            {
                "language": language,
                "source_export_root": str(export_root.relative_to(root)),
                "publish_root": str(publish_language_root.relative_to(root)),
                "target_count": len(targets),
                "target_kind_counts": dict(sorted(target_counts.items())),
                "search_index_path": str(search_index_path.relative_to(root)),
            }
        )

    chooser_path = publish_root / "index.html"
    chooser_path.write_text(
        render_publish_root_index(selected_languages),
        encoding="utf-8",
    )
    (publish_root / ".nojekyll").write_text("", encoding="utf-8")

    manifest_path = publish_report_dir / "publish-manifest.json"
    manifest_payload = {
        "publish_root": str(publish_root.relative_to(root)),
        "root_index_path": str(chooser_path.relative_to(root)),
        "languages": list(selected_languages),
        "total_target_count": total_target_count,
        "language_details": language_details,
        "exclusions": {
            "audiences_excluded": ["teacher"],
            "formats_excluded": ["pdf", "revealjs", "slides-pdf", "handout", "exercise-sheet"],
            "policy": "The public bundle copies only build/exports/student/<language>/html.",
        },
    }
    manifest_path.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")

    return PublishArtifact(
        publish_root=publish_root,
        manifest_path=manifest_path,
        languages=selected_languages,
        total_target_count=total_target_count,
        target_counts_by_language=target_counts_by_language,
    )


def normalize_publish_languages(languages: Sequence[str]) -> tuple[str, ...]:
    selected = tuple(dict.fromkeys(languages))
    if not selected:
        raise BuildError("publish requires at least one language")
    invalid = [language for language in selected if language not in LANGUAGES]
    if invalid:
        raise BuildError(f"unsupported publish languages: {', '.join(sorted(invalid))}")
    return selected


def reset_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def render_publish_root_index(languages: Sequence[str]) -> str:
    cards = "\n".join(
        (
            "      <a class=\"lf-language-card\" href=\"./"
            f"{language}/index.html\">"
            f"<span class=\"lf-language-name\">{escape(language_label(language))}</span>"
            f"<span class=\"lf-language-code\">/{escape(language)}</span>"
            "</a>"
        )
        for language in languages
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LearnForge</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: Georgia, "Times New Roman", serif;
      background: #f6f4ef;
      color: #1f2933;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 2rem;
      background:
        radial-gradient(circle at top, rgba(234, 179, 8, 0.12), transparent 30rem),
        linear-gradient(180deg, #fbfaf7 0%, #f0ece2 100%);
    }}
    main {{
      width: min(42rem, 100%);
      background: rgba(255, 255, 255, 0.88);
      border: 1px solid rgba(31, 41, 51, 0.12);
      border-radius: 1rem;
      padding: 2rem;
      box-shadow: 0 1rem 3rem rgba(15, 23, 42, 0.08);
    }}
    h1 {{
      margin: 0 0 0.75rem 0;
      font-size: clamp(2rem, 4vw, 2.7rem);
    }}
    p {{
      margin: 0 0 1.5rem 0;
      line-height: 1.6;
    }}
    .lf-language-grid {{
      display: grid;
      gap: 1rem;
    }}
    .lf-language-card {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 1rem;
      padding: 1rem 1.15rem;
      border-radius: 0.85rem;
      border: 1px solid rgba(31, 41, 51, 0.14);
      background: #fffdf8;
      color: inherit;
      text-decoration: none;
    }}
    .lf-language-card:hover,
    .lf-language-card:focus-visible {{
      outline: none;
      border-color: rgba(180, 83, 9, 0.45);
      box-shadow: 0 0 0 0.18rem rgba(180, 83, 9, 0.12);
    }}
    .lf-language-name {{
      font-size: 1.1rem;
      font-weight: 700;
    }}
    .lf-language-code {{
      color: #52606d;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.95rem;
    }}
  </style>
</head>
<body>
  <main>
    <h1>LearnForge</h1>
    <p>Select the public student site language.</p>
    <div class="lf-language-grid">
{cards}
    </div>
  </main>
</body>
</html>
"""


def language_label(language: str) -> str:
    return {
        "en": "English",
        "nb": "Norsk bokmål",
    }.get(language, language)

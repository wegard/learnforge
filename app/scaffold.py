from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.config import COLLECTION_DIRS, CONTENT_KIND_DIRS, REPO_ROOT, TEMPLATES_DIR


@dataclass(slots=True)
class ScaffoldResult:
    identifier: str
    target_dir: Path
    created_files: list[Path]


def scaffold_object(
    kind: str,
    identifier: str,
    *,
    root: Path = REPO_ROOT,
    owner: str = "vegard",
    collection_kind: str = "lecture",
) -> ScaffoldResult:
    environment = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=False)
    if kind == "collection":
        relative_dir = Path(COLLECTION_DIRS[collection_kind]) / identifier
    else:
        relative_dir = Path(CONTENT_KIND_DIRS[kind]) / identifier
    target_dir = root / relative_dir
    target_dir.mkdir(parents=True, exist_ok=False)

    context = {
        "id": identifier,
        "kind": kind,
        "owner": owner,
        "updated": date.today().isoformat(),
        "title_en": identifier.replace("-", " ").title(),
        "title_nb": identifier.replace("-", " ").title(),
        "collection_kind": collection_kind,
    }
    created_files: list[Path] = []

    meta_path = target_dir / "meta.yml"
    meta_contents = environment.get_template("meta.yml.j2").render(**context)
    meta_path.write_text(meta_contents, encoding="utf-8")
    created_files.append(meta_path)

    if kind == "collection":
        return ScaffoldResult(
            identifier=identifier,
            target_dir=target_dir,
            created_files=created_files,
        )

    if kind == "concept":
        template_names = ("concept.en.qmd.j2", "concept.nb.qmd.j2")
    elif kind == "resource":
        template_names = ("resource-note.en.qmd.j2", "resource-note.nb.qmd.j2")
    else:
        template_names = ("object.en.qmd.j2", "object.nb.qmd.j2")

    for template_name in template_names:
        language = "en" if ".en." in template_name else "nb"
        output_path = target_dir / f"note.{language}.qmd"
        output_path.write_text(
            environment.get_template(template_name).render(**context),
            encoding="utf-8",
        )
        created_files.append(output_path)

    if kind == "figure":
        svg_path = target_dir / "figure.svg"
        svg_path.write_text(
            (
                '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="240" '
                'viewBox="0 0 480 240">\n'
                '  <rect width="480" height="240" fill="#f8f5ef"/>\n'
                '  <circle cx="120" cy="120" r="48" fill="#27548a"/>\n'
                '  <circle cx="360" cy="120" r="48" fill="#d9534f"/>\n'
                '  <text x="120" y="126" fill="#ffffff" text-anchor="middle">Z</text>\n'
                '  <text x="360" y="126" fill="#ffffff" text-anchor="middle">Y</text>\n'
                "</svg>\n"
            ),
            encoding="utf-8",
        )
        created_files.append(svg_path)
        pdf_path = target_dir / "figure.pdf"
        pdf_path.write_bytes(
            
                b"%PDF-1.4\n"
                b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
                b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
                b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 120] "
                b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n"
                b"4 0 obj<< /Length 63 >>stream\n"
                b"BT /F1 16 Tf 48 68 Td (Replace with figure PDF) Tj ET\n"
                b"endstream endobj\n"
                b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
                b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n"
                b"0000000063 00000 n \n0000000122 00000 n \n0000000263 00000 n \n"
                b"0000000376 00000 n \ntrailer<< /Size 6 /Root 1 0 R >>\nstartxref\n"
                b"446\n%%EOF\n"
            
        )
        created_files.append(pdf_path)

    return ScaffoldResult(identifier=identifier, target_dir=target_dir, created_files=created_files)

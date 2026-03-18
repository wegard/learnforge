from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

LANGUAGES = ("en", "nb")
AUDIENCES = ("student", "teacher")
OBJECT_KINDS = ("concept", "exercise", "figure", "resource", "collection")
OUTPUT_FORMATS = ("html", "pdf", "revealjs", "handout", "exercise-sheet")

CONTENT_KIND_DIRS = {
    "concept": "content/concepts",
    "exercise": "content/exercises",
    "figure": "content/figures",
    "resource": "content/resources",
}

COLLECTION_DIRS = {
    "lecture": "collections/lectures",
    "module": "collections/modules",
    "assignment": "collections/assignments",
    "reading-list": "collections/reading-lists",
}

BUILD_DIR = REPO_ROOT / "build"
EXPORTS_DIR = BUILD_DIR / "exports"
GENERATED_DIR = BUILD_DIR / "generated"
INDEX_DIR = BUILD_DIR / "index"
REPORTS_DIR = BUILD_DIR / "reports"
SCHEMAS_DIR = REPO_ROOT / "schemas"
TEMPLATES_DIR = REPO_ROOT / "templates"


def object_note_filename(language: str) -> str:
    return f"note.{language}.qmd"

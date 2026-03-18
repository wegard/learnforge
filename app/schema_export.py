from __future__ import annotations

import json
from pathlib import Path

from app.config import REPO_ROOT, SCHEMAS_DIR
from app.models import BaseContentModel, Collection, Concept, Exercise, Figure, Resource

SCHEMA_MODELS = {
    "base-object.schema.json": BaseContentModel,
    "concept.schema.json": Concept,
    "exercise.schema.json": Exercise,
    "figure.schema.json": Figure,
    "resource.schema.json": Resource,
    "collection.schema.json": Collection,
}


def export_schemas(root: Path = REPO_ROOT) -> list[Path]:
    SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)
    written_paths: list[Path] = []
    for filename, model in SCHEMA_MODELS.items():
        output_path = root / "schemas" / filename
        output_path.write_text(
            json.dumps(model.model_json_schema(), indent=2),
            encoding="utf-8",
        )
        written_paths.append(output_path)
    return written_paths


if __name__ == "__main__":
    export_schemas()

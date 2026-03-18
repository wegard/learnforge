from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from app.config import REPO_ROOT
from app.models import Concept
from app.validator import validate_repository


def test_sample_repository_validates_cleanly() -> None:
    report = validate_repository(REPO_ROOT)
    assert report.ok
    assert report.object_count == 5
    assert report.course_count == 1
    assert report.search_index_path == "build/index/content-index.json"


def test_concept_schema_rejects_missing_title_language() -> None:
    payload = {
        "id": "demo-concept",
        "kind": "concept",
        "status": "approved",
        "visibility": "student",
        "languages": ["en", "nb"],
        "title": {"en": "Demo concept"},
        "courses": [],
        "topics": [],
        "tags": [],
        "outputs": ["html"],
        "owners": ["vegard"],
        "updated": date(2026, 3, 18),
        "translation_status": {"en": "approved", "nb": "approved"},
        "ai": {"generated_fields": []},
        "level": "intermediate",
        "prerequisites": [],
        "related": [],
    }

    with pytest.raises(ValidationError):
        Concept.model_validate(payload)

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.config import REPO_ROOT

TEACHING_FILENAME = ".learnforge-teaching.yml"

TeachingStatus = Literal["active", "upcoming", "discontinued"]


class CourseTeaching(BaseModel):
    model_config = ConfigDict(extra="forbid")

    teaching_status: TeachingStatus
    semester: str | None = None


class TeachingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    courses: dict[str, CourseTeaching] = Field(default_factory=dict)


def teaching_path(root: Path = REPO_ROOT) -> Path:
    return root / TEACHING_FILENAME


def load_teaching(root: Path = REPO_ROOT) -> tuple[TeachingConfig, str | None]:
    """Load the local teaching config file.

    Returns (config, error_message).  If the file is missing an empty
    config is returned with no error.  If the file is malformed an empty
    config is returned with a human-readable error string.
    """
    path = teaching_path(root)
    if not path.exists():
        return TeachingConfig(), None
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return TeachingConfig.model_validate(data), None
    except (yaml.YAMLError, ValidationError) as exc:
        return TeachingConfig(), str(exc)


_TEACHING_TEMPLATE = """\
# LearnForge teaching status — local only, never committed to git.
#
# Categorise courses by your current teaching involvement.
#
# teaching_status values:
#   active       — teaching this semester
#   upcoming     — scheduled for a future semester
#   discontinued — no longer teaching
#
# semester is optional free-form text (e.g. "fall-2026").
#
# Example:
#
# courses:
#   bik2550:
#     teaching_status: active
#   tem0052:
#     teaching_status: upcoming
#     semester: fall-2026
#   edi3400:
#     teaching_status: discontinued

courses: {}
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.config import REPO_ROOT
from app.indexer import RepositoryIndex

SCHEDULE_FILENAME = ".learnforge-schedule.yml"

EventType = Literal[
    "lecture",
    "assignment-deadline",
    "exam",
    "exam-upload-deadline",
    "grading-deadline",
    "other",
]


class ScheduleEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: datetime.date
    time: datetime.time | None = None
    type: EventType
    collection: str | None = None
    label: str | None = None
    room: str | None = None
    note: str | None = None


class CourseSchedule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[ScheduleEvent] = Field(default_factory=list)


class Schedule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    courses: dict[str, CourseSchedule] = Field(default_factory=dict)


@dataclass(slots=True)
class FlatEvent:
    course_id: str
    date: datetime.date
    time: datetime.time | None
    event_type: str
    display_label: str
    collection_id: str | None
    room: str | None
    note: str | None


def schedule_path(root: Path = REPO_ROOT) -> Path:
    return root / SCHEDULE_FILENAME


def load_schedule(root: Path = REPO_ROOT) -> tuple[Schedule, str | None]:
    """Load the local schedule file.

    Returns (schedule, error_message).  If the file is missing an empty
    schedule is returned with no error.  If the file is malformed an empty
    schedule is returned with a human-readable error string.
    """
    path = schedule_path(root)
    if not path.exists():
        return Schedule(), None
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return Schedule.model_validate(data), None
    except (yaml.YAMLError, ValidationError) as exc:
        return Schedule(), str(exc)


def flatten_schedule(
    schedule: Schedule,
    repo_index: RepositoryIndex,
    language: str,
    *,
    future_only: bool = True,
    today: datetime.date | None = None,
) -> list[FlatEvent]:
    """Denormalize per-course events into a flat chronological list."""
    reference = today or datetime.date.today()
    events: list[FlatEvent] = []

    for course_id, course_sched in schedule.courses.items():
        for ev in course_sched.events:
            if future_only and ev.date < reference:
                continue

            display_label = _resolve_label(ev, repo_index, language)

            events.append(
                FlatEvent(
                    course_id=course_id,
                    date=ev.date,
                    time=ev.time,
                    event_type=ev.type,
                    display_label=display_label,
                    collection_id=ev.collection,
                    room=ev.room,
                    note=ev.note,
                )
            )

    events.sort(key=lambda e: (e.date, e.time or datetime.time.min))
    return events


def _resolve_label(ev: ScheduleEvent, repo_index: RepositoryIndex, language: str) -> str:
    """Build a display label from the collection title or the event label."""
    if ev.collection:
        obj = repo_index.objects.get(ev.collection)
        if obj is not None:
            title = obj.model.title.get(language) or next(
                iter(obj.model.title.values()), ev.collection
            )
            return title
        return f"[?] {ev.collection}"
    return ev.label or ev.type


_SCHEDULE_TEMPLATE = """\
# LearnForge teaching schedule — local only, never committed to git.
#
# Structure:
#   courses:
#     <course-id>:
#       events:
#         - date: 2026-08-25
#           time: "10:15"               # optional — always quote times
#           type: lecture                # lecture | exam | exam-upload-deadline
#                                       #   grading-deadline | assignment-deadline | other
#           collection: <collection-id> # optional — links to course material
#           label: "Description"        # optional — for non-collection events
#           room: "B3-020"              # optional
#           note: "Bring USB"           # optional
#
# Example:
#
# courses:
#   edi3400:
#     events:
#       - date: 2026-08-25
#         time: "10:15"
#         type: lecture
#         collection: edi3400-lecture-01
#         room: "B3-020"
#       - date: 2026-12-15
#         type: exam
#         label: "Written exam, 3 hours"
#       - date: 2027-01-15
#         type: grading-deadline
#         label: "Final grades due"

courses: {}
"""

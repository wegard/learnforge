from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.tui.schedule import (
    FlatEvent,
    Schedule,
    ScheduleEvent,
    flatten_schedule,
    load_schedule,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_SCHEDULE = {
    "courses": {
        "edi3400": {
            "events": [
                {
                    "date": "2026-04-07",
                    "time": "10:15",
                    "type": "lecture",
                    "collection": "edi3400-lecture-05b",
                    "room": "B3-020",
                },
                {
                    "date": "2026-03-31",
                    "time": "10:15",
                    "type": "lecture",
                    "collection": "edi3400-lecture-05a",
                },
                {
                    "date": "2026-12-15",
                    "type": "exam",
                    "label": "Written exam",
                },
                {
                    "date": "2026-06-01",
                    "type": "grading-deadline",
                    "label": "Final grades due",
                },
            ],
        },
        "gra4150": {
            "events": [
                {
                    "date": "2026-04-02",
                    "time": "08:15",
                    "type": "lecture",
                    "collection": "gra4150-lecture-05",
                },
            ],
        },
    },
}


def _write_schedule(tmp_path: Path, data: dict) -> None:
    (tmp_path / ".learnforge-schedule.yml").write_text(
        yaml.dump(data, default_flow_style=False), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Minimal stub for RepositoryIndex used in flatten tests
# ---------------------------------------------------------------------------


@dataclass
class _StubModel:
    title: dict[str, str]


@dataclass
class _StubObject:
    model: _StubModel


@dataclass
class _StubIndex:
    objects: dict[str, _StubObject]


def _make_stub_index(titles: dict[str, str] | None = None) -> _StubIndex:
    """Build a stub RepositoryIndex with the given id→title mapping."""
    objects: dict[str, _StubObject] = {}
    for obj_id, title in (titles or {}).items():
        objects[obj_id] = _StubObject(model=_StubModel(title={"en": title}))
    return objects  # type: ignore[return-value]  # duck-typed


# ---------------------------------------------------------------------------
# load_schedule tests
# ---------------------------------------------------------------------------


class TestLoadSchedule:
    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        schedule, error = load_schedule(tmp_path)
        assert schedule == Schedule()
        assert error is None

    def test_valid_file(self, tmp_path: Path) -> None:
        _write_schedule(tmp_path, _VALID_SCHEDULE)
        schedule, error = load_schedule(tmp_path)
        assert error is None
        assert "edi3400" in schedule.courses
        assert len(schedule.courses["edi3400"].events) == 4
        assert schedule.courses["edi3400"].events[0].type == "lecture"

    def test_malformed_yaml_returns_error(self, tmp_path: Path) -> None:
        (tmp_path / ".learnforge-schedule.yml").write_text(
            "courses:\n  edi3400:\n    events: [[[bad", encoding="utf-8"
        )
        schedule, error = load_schedule(tmp_path)
        assert schedule == Schedule()
        assert error is not None

    def test_invalid_event_type_returns_error(self, tmp_path: Path) -> None:
        data = {
            "courses": {
                "x": {
                    "events": [
                        {"date": "2026-01-01", "type": "invalid-type"},
                    ],
                },
            },
        }
        _write_schedule(tmp_path, data)
        schedule, error = load_schedule(tmp_path)
        assert schedule == Schedule()
        assert error is not None

    def test_empty_file_returns_empty(self, tmp_path: Path) -> None:
        (tmp_path / ".learnforge-schedule.yml").write_text("", encoding="utf-8")
        schedule, error = load_schedule(tmp_path)
        assert schedule == Schedule()
        assert error is None

    def test_time_parsed_correctly(self, tmp_path: Path) -> None:
        data = {
            "courses": {
                "x": {
                    "events": [
                        {"date": "2026-05-01", "time": "08:15", "type": "lecture"},
                    ],
                },
            },
        }
        _write_schedule(tmp_path, data)
        schedule, _ = load_schedule(tmp_path)
        ev = schedule.courses["x"].events[0]
        assert ev.time == time(8, 15)


# ---------------------------------------------------------------------------
# flatten_schedule tests
# ---------------------------------------------------------------------------


class TestFlattenSchedule:
    def _load_and_flatten(
        self, tmp_path: Path, *, future_only: bool = False, today: date | None = None
    ) -> list[FlatEvent]:
        _write_schedule(tmp_path, _VALID_SCHEDULE)
        schedule, _ = load_schedule(tmp_path)
        stub_index = _StubIndex(
            objects={
                "edi3400-lecture-05a": _StubObject(
                    model=_StubModel(title={"en": "Lecture 5a — NumPy"})
                ),
                "edi3400-lecture-05b": _StubObject(
                    model=_StubModel(title={"en": "Lecture 5b — Pandas"})
                ),
                "gra4150-lecture-05": _StubObject(
                    model=_StubModel(title={"en": "Lecture 5 — ML Pipelines"})
                ),
            }
        )
        return flatten_schedule(
            schedule,
            stub_index,
            "en",
            future_only=future_only,
            today=today,  # type: ignore[arg-type]
        )

    def test_sorted_chronologically(self, tmp_path: Path) -> None:
        events = self._load_and_flatten(tmp_path)
        dates = [e.date for e in events]
        assert dates == sorted(dates)

    def test_all_events_included_when_not_filtering(self, tmp_path: Path) -> None:
        events = self._load_and_flatten(tmp_path, future_only=False)
        assert len(events) == 5

    def test_future_only_filters_past(self, tmp_path: Path) -> None:
        events = self._load_and_flatten(tmp_path, future_only=True, today=date(2026, 4, 5))
        assert all(e.date >= date(2026, 4, 5) for e in events)
        # Should include Apr 7, Dec 15, Jun 1 from edi3400 — not Mar 31 or Apr 2
        assert len(events) == 3

    def test_collection_titles_resolved(self, tmp_path: Path) -> None:
        events = self._load_and_flatten(tmp_path)
        lecture_5a = next(e for e in events if e.collection_id == "edi3400-lecture-05a")
        assert lecture_5a.display_label == "Lecture 5a — NumPy"

    def test_label_used_for_non_collection_events(self, tmp_path: Path) -> None:
        events = self._load_and_flatten(tmp_path)
        exam = next(e for e in events if e.event_type == "exam")
        assert exam.display_label == "Written exam"
        assert exam.collection_id is None

    def test_missing_collection_shows_placeholder(self, tmp_path: Path) -> None:
        _write_schedule(
            tmp_path,
            {
                "courses": {
                    "x": {
                        "events": [
                            {
                                "date": "2026-01-01",
                                "type": "lecture",
                                "collection": "nonexistent",
                            }
                        ]
                    }
                }
            },
        )
        schedule, _ = load_schedule(tmp_path)
        stub = _StubIndex(objects={})
        events = flatten_schedule(
            schedule,
            stub,
            "en",
            future_only=False,  # type: ignore[arg-type]
        )
        assert events[0].display_label == "[?] nonexistent"

    def test_events_on_same_date_sorted_by_time(self, tmp_path: Path) -> None:
        data = {
            "courses": {
                "x": {
                    "events": [
                        {"date": "2026-05-01", "time": "14:00", "type": "lecture"},
                        {"date": "2026-05-01", "time": "08:00", "type": "lecture"},
                        {"date": "2026-05-01", "type": "other", "label": "All day"},
                    ]
                }
            }
        }
        _write_schedule(tmp_path, data)
        schedule, _ = load_schedule(tmp_path)
        stub = _StubIndex(objects={})
        events = flatten_schedule(
            schedule,
            stub,
            "en",
            future_only=False,  # type: ignore[arg-type]
        )
        times = [e.time for e in events]
        assert times == [None, time(8, 0), time(14, 0)]

    def test_today_is_included_in_future_only(self, tmp_path: Path) -> None:
        data = {
            "courses": {
                "x": {
                    "events": [
                        {"date": "2026-05-01", "type": "lecture"},
                    ]
                }
            }
        }
        _write_schedule(tmp_path, data)
        schedule, _ = load_schedule(tmp_path)
        stub = _StubIndex(objects={})
        events = flatten_schedule(
            schedule,
            stub,
            "en",
            future_only=True,
            today=date(2026, 5, 1),  # type: ignore[arg-type]
        )
        assert len(events) == 1


# ---------------------------------------------------------------------------
# Pydantic validation tests
# ---------------------------------------------------------------------------


class TestScheduleEventValidation:
    def test_minimal_event(self) -> None:
        ev = ScheduleEvent(date=date(2026, 1, 1), type="lecture")
        assert ev.collection is None
        assert ev.time is None

    def test_full_event(self) -> None:
        ev = ScheduleEvent(
            date=date(2026, 1, 1),
            time=time(10, 15),
            type="exam",
            label="Final",
            room="A1",
            note="3 hours",
        )
        assert ev.type == "exam"
        assert ev.room == "A1"

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ScheduleEvent(date=date(2026, 1, 1), type="lecture", unknown="bad")

    def test_invalid_type_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ScheduleEvent(date=date(2026, 1, 1), type="invalid")

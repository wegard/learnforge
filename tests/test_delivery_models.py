from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from app.models import DeliveryAssignment, DeliveryLecture, DeliveryManifest


class TestDeliveryLecture:
    def test_valid_lecture(self) -> None:
        lecture = DeliveryLecture(
            lecture="tem0052-lecture-01",
            date=date(2026, 1, 20),
            ready=True,
            notes="First class",
        )
        assert lecture.lecture == "tem0052-lecture-01"
        assert lecture.date == date(2026, 1, 20)
        assert lecture.ready is True
        assert lecture.notes == "First class"
        assert lecture.additions == []
        assert lecture.removals == []
        assert lecture.title_override is None

    def test_defaults(self) -> None:
        lecture = DeliveryLecture(lecture="lec-01", date=date(2026, 1, 1))
        assert lecture.ready is False
        assert lecture.title_override is None
        assert lecture.notes is None
        assert lecture.additions == []
        assert lecture.removals == []

    def test_with_additions_and_removals(self) -> None:
        lecture = DeliveryLecture(
            lecture="lec-01",
            date=date(2026, 1, 1),
            additions=["extra-concept"],
            removals=["old-concept"],
        )
        assert lecture.additions == ["extra-concept"]
        assert lecture.removals == ["old-concept"]

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError, match="extra"):
            DeliveryLecture(
                lecture="lec-01",
                date=date(2026, 1, 1),
                unexpected_field="value",
            )


class TestDeliveryAssignment:
    def test_valid_assignment(self) -> None:
        assignment = DeliveryAssignment(
            assignment="tem0052-assignment-01",
            due_date=date(2026, 2, 14),
            ready=True,
        )
        assert assignment.assignment == "tem0052-assignment-01"
        assert assignment.due_date == date(2026, 2, 14)
        assert assignment.ready is True

    def test_defaults(self) -> None:
        assignment = DeliveryAssignment(
            assignment="assign-01",
            due_date=date(2026, 2, 1),
        )
        assert assignment.ready is False

    def test_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError, match="extra"):
            DeliveryAssignment(
                assignment="assign-01",
                due_date=date(2026, 2, 1),
                notes="not allowed",
            )


class TestDeliveryManifest:
    def _valid_payload(self) -> dict:
        return {
            "id": "tem0052-spring-2026",
            "course": "tem0052",
            "term": "spring-2026",
            "language": "en",
            "status": "active",
            "created": "2026-01-15",
            "updated": "2026-03-26",
        }

    def test_valid_minimal_manifest(self) -> None:
        manifest = DeliveryManifest.model_validate(self._valid_payload())
        assert manifest.id == "tem0052-spring-2026"
        assert manifest.course == "tem0052"
        assert manifest.term == "spring-2026"
        assert manifest.language == "en"
        assert manifest.status == "active"
        assert manifest.lectures == []
        assert manifest.assignments == []
        assert manifest.default_formats == ["html", "revealjs", "pdf", "handout"]
        assert manifest.default_audiences == ["student", "teacher"]

    def test_valid_full_manifest(self) -> None:
        payload = self._valid_payload()
        payload["lectures"] = [
            {
                "lecture": "tem0052-lecture-01",
                "date": "2026-01-20",
                "ready": True,
                "notes": "First class",
            },
            {
                "lecture": "tem0052-lecture-02",
                "date": "2026-01-27",
                "ready": False,
            },
        ]
        payload["assignments"] = [
            {
                "assignment": "tem0052-assignment-01",
                "due_date": "2026-02-14",
                "ready": True,
            },
        ]
        payload["default_formats"] = ["html", "pdf"]
        payload["default_audiences"] = ["student"]

        manifest = DeliveryManifest.model_validate(payload)
        assert len(manifest.lectures) == 2
        assert manifest.lectures[0].ready is True
        assert manifest.lectures[1].ready is False
        assert len(manifest.assignments) == 1
        assert manifest.default_formats == ["html", "pdf"]
        assert manifest.default_audiences == ["student"]

    def test_status_defaults_to_active(self) -> None:
        payload = self._valid_payload()
        del payload["status"]
        manifest = DeliveryManifest.model_validate(payload)
        assert manifest.status == "active"

    def test_archived_status(self) -> None:
        payload = self._valid_payload()
        payload["status"] = "archived"
        manifest = DeliveryManifest.model_validate(payload)
        assert manifest.status == "archived"

    def test_rejects_invalid_status(self) -> None:
        payload = self._valid_payload()
        payload["status"] = "completed"
        with pytest.raises(ValidationError):
            DeliveryManifest.model_validate(payload)

    def test_rejects_invalid_language(self) -> None:
        payload = self._valid_payload()
        payload["language"] = "fr"
        with pytest.raises(ValidationError):
            DeliveryManifest.model_validate(payload)

    def test_nb_language(self) -> None:
        payload = self._valid_payload()
        payload["language"] = "nb"
        manifest = DeliveryManifest.model_validate(payload)
        assert manifest.language == "nb"

    def test_rejects_invalid_slug(self) -> None:
        payload = self._valid_payload()
        payload["id"] = "TEM0052-Spring"
        with pytest.raises(ValidationError, match="pattern"):
            DeliveryManifest.model_validate(payload)

    def test_missing_required_fields(self) -> None:
        for field in ("id", "course", "term", "language", "created", "updated"):
            payload = self._valid_payload()
            del payload[field]
            with pytest.raises(ValidationError):
                DeliveryManifest.model_validate(payload)

    def test_rejects_extra_fields(self) -> None:
        payload = self._valid_payload()
        payload["unexpected"] = "value"
        with pytest.raises(ValidationError, match="extra"):
            DeliveryManifest.model_validate(payload)

    def test_date_parsing(self) -> None:
        manifest = DeliveryManifest.model_validate(self._valid_payload())
        assert manifest.created == date(2026, 1, 15)
        assert manifest.updated == date(2026, 3, 26)

    def test_rejects_invalid_output_format(self) -> None:
        payload = self._valid_payload()
        payload["default_formats"] = ["html", "docx"]
        with pytest.raises(ValidationError):
            DeliveryManifest.model_validate(payload)

    def test_rejects_invalid_audience(self) -> None:
        payload = self._valid_payload()
        payload["default_audiences"] = ["admin"]
        with pytest.raises(ValidationError):
            DeliveryManifest.model_validate(payload)

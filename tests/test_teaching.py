from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.tui.teaching import (
    CourseTeaching,
    TeachingConfig,
    load_teaching,
)


def _write_teaching(tmp_path: Path, data: dict) -> None:
    (tmp_path / ".learnforge-teaching.yml").write_text(
        yaml.dump(data, default_flow_style=False), encoding="utf-8"
    )


_VALID_CONFIG = {
    "courses": {
        "bik2550": {"teaching_status": "active"},
        "tem0052": {"teaching_status": "upcoming", "semester": "fall-2026"},
        "edi3400": {"teaching_status": "discontinued"},
    },
}


class TestLoadTeaching:
    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        config, error = load_teaching(tmp_path)
        assert config == TeachingConfig()
        assert error is None

    def test_valid_file(self, tmp_path: Path) -> None:
        _write_teaching(tmp_path, _VALID_CONFIG)
        config, error = load_teaching(tmp_path)
        assert error is None
        assert "bik2550" in config.courses
        assert config.courses["bik2550"].teaching_status == "active"
        assert config.courses["tem0052"].semester == "fall-2026"

    def test_malformed_yaml_returns_error(self, tmp_path: Path) -> None:
        (tmp_path / ".learnforge-teaching.yml").write_text(
            "courses:\n  x: [[[bad", encoding="utf-8"
        )
        config, error = load_teaching(tmp_path)
        assert config == TeachingConfig()
        assert error is not None

    def test_invalid_status_returns_error(self, tmp_path: Path) -> None:
        data = {"courses": {"x": {"teaching_status": "invalid"}}}
        _write_teaching(tmp_path, data)
        config, error = load_teaching(tmp_path)
        assert config == TeachingConfig()
        assert error is not None

    def test_empty_file_returns_empty(self, tmp_path: Path) -> None:
        (tmp_path / ".learnforge-teaching.yml").write_text("", encoding="utf-8")
        config, error = load_teaching(tmp_path)
        assert config == TeachingConfig()
        assert error is None

    def test_extra_fields_rejected(self, tmp_path: Path) -> None:
        data = {"courses": {"x": {"teaching_status": "active", "bogus": True}}}
        _write_teaching(tmp_path, data)
        config, error = load_teaching(tmp_path)
        assert config == TeachingConfig()
        assert error is not None


class TestCourseTeachingValidation:
    def test_minimal(self) -> None:
        ct = CourseTeaching(teaching_status="active")
        assert ct.semester is None

    def test_with_semester(self) -> None:
        ct = CourseTeaching(teaching_status="upcoming", semester="fall-2026")
        assert ct.teaching_status == "upcoming"

    def test_invalid_status(self) -> None:
        with pytest.raises(ValidationError):
            CourseTeaching(teaching_status="wrong")

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CourseTeaching(teaching_status="active", unknown="bad")

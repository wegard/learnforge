from __future__ import annotations

from app.build import build_target
from app.config import REPO_ROOT


def test_student_build_hides_teacher_only_content() -> None:
    student_artifact = build_target(
        "iv-intuition",
        audience="student",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )
    teacher_artifact = build_target(
        "iv-intuition",
        audience="teacher",
        language="en",
        output_format="html",
        root=REPO_ROOT,
    )

    student_html = student_artifact.output_path.read_text(encoding="utf-8")
    teacher_html = teacher_artifact.output_path.read_text(encoding="utf-8")

    assert student_artifact.output_path.exists()
    assert teacher_artifact.output_path.exists()
    assert "Prompt the room" not in student_html
    assert "Prompt the room" in teacher_html

from __future__ import annotations

from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


def test_validate_command_succeeds() -> None:
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "Errors: 0" in result.stdout
    assert "Build summary: build/reports/build-summary.json" in result.stdout


def test_validate_command_json_output_includes_build_summary() -> None:
    result = runner.invoke(app, ["validate", "--json"])
    assert result.exit_code == 0
    assert '"status": "passed"' in result.stdout
    assert '"build_summary_path": "build/reports/build-summary.json"' in result.stdout


def test_search_command_finds_iv_content() -> None:
    result = runner.invoke(app, ["search", "instrumental variables"])
    assert result.exit_code == 0
    assert "iv-intuition" in result.stdout

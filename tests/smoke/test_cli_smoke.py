from typer.testing import CliRunner

from mem.cli import app
from mem.constants import RESEARCH_DISCLAIMER

runner = CliRunner()


def test_help_shows_disclaimer() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Research Use Only" in result.stdout


def test_later_stage_command_fails_closed() -> None:
    result = runner.invoke(app, ["train-detector", "--output-dir", "outputs"])
    assert result.exit_code != 0


def test_verify_release_blocked() -> None:
    result = runner.invoke(app, ["verify-release", "--output-dir", "outputs"])
    assert result.exit_code != 0
    assert RESEARCH_DISCLAIMER.split(".")[0] in result.stdout or result.exit_code == 1

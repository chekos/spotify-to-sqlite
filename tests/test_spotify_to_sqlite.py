import pytest
from typer.testing import CliRunner

from spotify_to_sqlite import __app_name__, __version__, cli

runner = CliRunner()


@pytest.mark.parametrize(
    "options",
    (
        ["-v"],
        ["--version"],
    ),
)
def test_version(options):
    result = CliRunner().invoke(cli.cli, options)
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}" in result.output


@pytest.mark.parametrize(
    "options",
    (["--help"],),
)
def test_help(options):
    result = CliRunner().invoke(cli.cli, options)
    assert result.exit_code == 0
    assert result.output.startswith("Usage: ")
    assert "--help" in result.output

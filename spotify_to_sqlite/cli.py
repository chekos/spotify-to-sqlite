from pathlib import Path

import typer

from .constants import __app_name__, __version__
from .utils import _version_callback, convert_export, get_audio_features

cli = typer.Typer()


@cli.callback(invoke_without_command=True)
def main(
    export_zip: Path = typer.Argument(
        "./my_spotify_data.zip",
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    db_path: Path = typer.Argument(
        "./spotify.db", file_okay=True, dir_okay=False, writable=True
    ),
    recreate: bool = typer.Option(
        False, help="Recreate (overwrite) database if db_path already exists."
    ),
    audio_features: bool = typer.Option(
        False,
        help="Retrieve audio features for your library tracks and streaming history.",
    ),
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
):
    """Convert a Spotify export zip to SQLite database."""
    if db_path.exists() and audio_features:
        get_audio_features(db_path)
        typer.Exit()
    else:
        convert_export(export_zip, db_path, recreate)

    if audio_features:
        get_audio_features(db_path)

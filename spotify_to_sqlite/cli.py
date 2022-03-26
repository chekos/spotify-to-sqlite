from pathlib import Path

import typer
from sqlite_utils import Database

from .constants import __app_name__, __version__
from .utils import (
    _version_callback,
    convert_export,
    get_audio_features,
    get_audio_features_from_uri,
)

cli = typer.Typer()


@cli.command()
def enrich(
    db_path: Path = typer.Argument(
        "./spotify.db", file_okay=True, dir_okay=False, writable=True
    ),
    table: str = typer.Argument(
        ...,
    ),
    uri_column: str = typer.Option(
        "spotify_track_uri", help="Column name containing tracks' URIs"
    ),
    new_name: str = typer.Option(
        "", help="Name for new table containing audio features from tracks in `table`"
    ),
):
    """Get audio features for tracks in `table_name`"""
    db = Database(db_path)
    uris = db.execute(
        f"select distinct({uri_column}) from {table} where {uri_column} is not null;"
    ).fetchall()

    if new_name:
        table_name = new_name
    else:
        table_name = f"enriched_{table}"

    get_audio_features_from_uri(uris, table_name, db)


@cli.command()
def convert(
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
):
    """Convert a Spotify export zip to SQLite database."""
    if db_path.exists() and audio_features:
        get_audio_features(db_path)
        typer.Exit()
    else:
        convert_export(export_zip, db_path, recreate)

    if audio_features:
        get_audio_features(db_path)


@cli.callback()
def spotify_to_sqlite(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return

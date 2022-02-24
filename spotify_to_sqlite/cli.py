import json
import re
from pathlib import Path
from zipfile import ZipFile

import typer
from sqlite_utils import Database

from .constants import __app_name__, __version__

cli = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


def _to_snake_case(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("__([A-Z])", r"_\1", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    name = name.replace(".json", "")
    name = re.sub("[0-9]+$", "", name)
    return name.lower()


def _flatten(d):
    for key, value in d.items():
        if isinstance(value, dict):
            for key2, value2 in _flatten(value):
                yield key + "_" + key2, value2
        else:
            yield key, value


def insert_data(db, table_name, data):
    table = db[table_name]
    if data is not None:
        if isinstance(data, list):
            table.insert_all(data, alter=True)
        elif isinstance(data, dict):
            table.insert(data)
        else:
            print(f"Couldn't populate table: {table_name}")


@cli.callback(invoke_without_command=True)
def main(
    export_zip: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False, readable=True
    ),
    db_path: Path = typer.Argument(..., file_okay=True, dir_okay=False, writable=True),
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
):
    export = ZipFile(export_zip)
    files = [file for file in export.namelist() if file.endswith("json")]
    table_names = [_to_snake_case(file.split("/")[-1]) for file in files]
    file_tables = dict(zip(files, table_names))

    spotify_db = Database(db_path, recreate=True)
    for file in file_tables.keys():
        table_name = file_tables[file]
        with export.open(file, "r") as data_file:
            data = json.loads(data_file.read())

        if table_name == "playlist":
            data = data["playlists"]
            for (rowid, pl) in enumerate(data, start=1):
                playlist_tracks = [
                    {
                        **{"playlistId": rowid, "orderInPlaylist": rank},
                        **dict(_flatten(track)),
                    }
                    for (rank, track) in enumerate(pl["items"], start=1)
                ]
                insert_data(spotify_db, "playlist_tracks", playlist_tracks)

        if table_name == "inferences":
            data = [{"inference": value} for value in data["inferences"]]

        if table_name == "your_library":
            for key in data.keys():
                insert_data(spotify_db, f"your_library_{key}", data[key])
            data = None

        insert_data(spotify_db, table_name, data)

    spotify_db["playlist_tracks"].add_foreign_key("playlistId", "playlist", "rowid")

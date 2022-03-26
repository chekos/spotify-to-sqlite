import json
import os
import re
from datetime import datetime as dt
from pathlib import Path
from zipfile import ZipFile

import spotipy
import typer
from dotenv import load_dotenv
from rich.progress import track
from spotipy.oauth2 import SpotifyClientCredentials
from sqlite_utils import Database

from .constants import __app_name__, __version__

load_dotenv()

client_id = os.environ.get("SPOTIPY_CLIENT_ID", " ")
client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET", " ")

sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )
)


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


def insert_data(db, table_name, data, pk=None):
    table = db[table_name]
    if data is not None:
        if isinstance(data, list):
            if pk == "hash_id":
                table.insert_all(data, alter=True, hash_id="_id", ignore=True)
            elif pk:
                table.insert_all(data, alter=True, pk=pk, ignore=True)
            else:
                table.insert_all(data, alter=True, ignore=True)
        elif isinstance(data, dict):
            if pk == "hash_id":
                table.insert(data, hash_id="_id", ignore=True)
            elif pk:
                table.insert(data, pk=pk, ignore=True)
            else:
                table.insert(data, ignore=True)
        else:
            print(f"Couldn't populate table: {table_name}")


def convert_export(export: Path, db_path: Path, recreate: bool = False):
    export = ZipFile(export)
    files = [file for file in export.namelist() if file.endswith("json")]
    table_names = [_to_snake_case(file.split("/")[-1]) for file in files]
    file_tables = dict(zip(files, table_names))

    spotify_db = Database(db_path, recreate=recreate)
    for file in track(file_tables.keys(), description="Converting..."):
        table_name = file_tables[file]
        with export.open(file, "r") as data_file:
            try:
                data = json.loads(data_file.read())
            except:
                print(f"Error loading {file}. Skipping..")

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
                insert_data(
                    spotify_db,
                    "playlist_tracks",
                    playlist_tracks,
                    pk=("playlistId", "orderInPlaylist", "track_trackUri"),
                )

        if table_name == "inferences":
            data = [{"inference": value} for value in data["inferences"]]

        if table_name == "your_library":
            for key in data.keys():
                insert_data(
                    spotify_db,
                    f"your_library_{key}",
                    data[key],
                    pk="uri",
                )
            data = None
        if table_name == "streaming_history":
            insert_data(
                spotify_db,
                table_name,
                data,
                pk="hash_id",
            )
        else:
            insert_data(
                spotify_db,
                table_name,
                data,
            )


def get_audio_features(
    db_path: Path,
):
    spotify_db = Database(db_path)

    # library tracks
    if "library_tracks_audio_features" in spotify_db.table_names():
        lib_tracks = spotify_db.execute(
            "select uri from your_library_tracks where uri not in (select uri from library_tracks_audio_features);"
        ).fetchall()
    elif "your_library_tracks" in spotify_db.table_names():
        lib_tracks = spotify_db.execute(
            f"select uri from your_library_tracks;"
        ).fetchall()
    else:
        pass

    if lib_tracks:
        get_audio_features_from_uri(
            lib_tracks, "library_tracks_audio_features", spotify_db
        )

    # streaming history tracks
    if "streaming_history_audio_features" in spotify_db.table_names():
        streaming_history_q_results = spotify_db.execute(
            """
        select artistName, trackName from streaming_history 
        where artistName || " - " || trackName not in (
            select 
              json_extract(artists_names, "$[0]") || " - " || name
            from streaming_history_audio_features
            );
        """
        )
    else:
        streaming_history_q_results = spotify_db.execute(
            f"select artistName, trackName from streaming_history;"
        ).fetchall()
    search_queries = set()
    for item in streaming_history_q_results:
        _query = f"{item[0]} {item[1]}"
        search_queries.add(_query)

    search_queries = list(search_queries)

    skipped_queries = []
    skipped_audio_features = []
    for query in track(
        search_queries,
        total=len(search_queries),
        description="Working on your streaming history...",
    ):
        track_info = get_track_info(query)
        if track_info:
            track_audio_features = sp.audio_features(track_info["uri"])[0]
            if track_audio_features:
                track_data = {**track_info, **track_audio_features}
                spotify_db["streaming_history_audio_features"].insert(
                    track_data, hash_id="hash_id", ignore=True, alter=True
                )
            skipped_audio_features.append(track_info)
        else:
            skipped_queries.append(query)

    spotify_db.execute(
        f"""
    CREATE TABLE enriched_streaming_history AS
    SELECT
        _id,
        endTime,
        artistName as artist,
        json_extract(artists_uris, "$[0]") as artist_uri,
        name,
        uri,
        msPlayed,
        spotify_url,
        duration_ms,
        explicit,
        popularity,
        preview_url,
        danceability,
        energy,
        [key],
        loudness,
        mode,
        speechiness,
        acousticness,
        instrumentalness,
        liveness,
        valence,
        tempo,
        time_signature
    FROM streaming_history
    JOIN streaming_history_audio_features
        ON artistName || " - " || trackName = json_extract(artists_names, "$[0]") || " - " || name
    """
    )
    spotify_db.vacuum()


def get_track_info(query: str, is_uri: bool = False):
    if not is_uri:
        search_result = sp.search(query, limit=1, type="track")
        if search_result["tracks"]["items"]:
            track_item = search_result["tracks"]["items"][0]
        else:
            return False
    else:
        track_item = sp.track(query)

    _track = {}

    _track["artists_uris"] = []
    _track["artists_names"] = []
    for artist in track_item["artists"]:
        _track["artists_uris"].append(artist["uri"])
        _track["artists_names"].append(artist["name"])

    _track["spotify_url"] = track_item["external_urls"]["spotify"]
    _track["duration_ms"] = track_item["duration_ms"]
    _track["explicit"] = track_item["explicit"]
    _track["name"] = track_item["name"]
    _track["popularity"] = track_item["popularity"]
    _track["preview_url"] = track_item["preview_url"]
    _track["track_number"] = track_item["track_number"]
    _track["type"] = track_item["type"]
    _track["uri"] = track_item["uri"]
    _track["updated_at"] = dt.utcnow()

    return _track


def get_audio_features_from_uri(uris: list, table_name: str, db: Database):
    for lib_track in track(
        uris,
        total=len(uris),
        description=f"Working on tracks for {table_name}...",
    ):
        track_uri = lib_track[0]

        track_info = get_track_info(track_uri, is_uri=True)
        track_audio_features = sp.audio_features(track_uri)[0]

        track_data = {**track_info, **track_audio_features}

        db[table_name].insert(track_data, pk="id", ignore=True)

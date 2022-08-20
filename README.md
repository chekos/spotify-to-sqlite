# spotify-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/spotify-to-sqlite.svg)](https://pypi.org/project/spotify-to-sqlite/)
[![Changelog](https://img.shields.io/github/v/release/chekos/spotify-to-sqlite?include_prereleases&label=changelog)](https://github.com/chekos/spotify-to-sqlite/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/chekos/spotify-to-sqlite/blob/main/LICENSE)

Convert a Spotify export zip to a SQLite database

## Installation

Install this library using `pip`:

    $ pip install spotify-to-sqlite

## Usage

Convert a Spotify export zip to a SQLite database
```shell
spotify-to-sqlite convert my_spotify_data.zip spotify.db
```

You can use Spotify's Web API to retrieve audio features tracks in your `streaming_history` and `your_library_tracks` tables. 
You will need a `CLIENT_ID` and a `CLIENT_SECRET` which you can get when you register an application the [Spotify Developer's site](https://developer.spotify.com/documentation/general/guides/authorization/app-settings/). You can export those as `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` (**notice it's SPOTI*P*Y not SPOTI*F*Y**).
You can also save those on a `.env` file on your working directory as such:
```text
# .env example
SPOTIPY_CLIENT_ID=adfgahjklsdf73932bcdlavsd7892dgfasd
SPOTIPY_CLIENT_SECRET=dabjgsd77507davsd12344dhgvafsdl
```

```shell
# when your converting export
spotify-to-sqlite --audio-features my_spotify_data.zip spotify.db

# if you already had converted your export you can pass a "-"
spotify-to-sqlite --audio-features - spotify.db
```


## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

    cd spotify-to-sqlite
    python -m venv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest

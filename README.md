# spotify-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/spotify-to-sqlite.svg)](https://pypi.org/project/spotify-to-sqlite/)
[![Changelog](https://img.shields.io/github/v/release/chekos/spotify-to-sqlite?include_prereleases&label=changelog)](https://github.com/chekos/spotify-to-sqlite/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/chekos/spotify-to-sqlite/blob/main/LICENSE)

Convert a Spotify export zip to a SQLite database

## Installation

Install this library using `pip`:

    $ pip install spotify-to-sqlite

## Usage

```shell
spotify-to-sqlite my_spotify_data.zip spotify.db
```


## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

    cd spotify-to-sqlite
    python -mvenv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest

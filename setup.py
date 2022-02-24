from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="spotify-to-sqlite",
    description="Convert a Spotify export zip to a SQLite database",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Sergio Sanchez",
    url="https://github.com/chekos/spotify-to-sqlite",
    project_urls={
        "Issues": "https://github.com/chekos/spotify-to-sqlite/issues",
        "CI": "https://github.com/chekos/spotify-to-sqlite/actions",
        "Changelog": "https://github.com/chekos/spotify-to-sqlite/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["spotify_to_sqlite"],
    install_requires=[],
    extras_require={"test": ["pytest"]},
    python_requires=">=3.6",
)

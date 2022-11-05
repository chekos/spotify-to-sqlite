import os

from setuptools import setup

VERSION = "0.2.1"

test_requirements = ["pytest>=7.0.1", "pytest-dotenv>=0.5.2"]
jupyter_extras = ["ipywidgets==7.6.5"]
dev_requirements = [
    "black>=22.1.0",
    "datasette>=0.60.2",
    "ipykernel>=6.9.1",
    "isort>=5.10.1",
]
dev_requirements.extend(test_requirements)
dev_requirements.extend(jupyter_extras)


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
    install_requires=[
        "typer==0.6.1",
        "sqlite-utils==3.30",
        "spotipy==2.19",
        "python-dotenv==0.19.2",
        "rich==12.6.0",
    ],
    extras_require={
        "test": test_requirements,
        "jupyter": jupyter_extras,
        "dev": dev_requirements,
    },
    python_requires=">=3.6",
    entry_points="""
        [console_scripts]
        spotify-to-sqlite=spotify_to_sqlite.cli:cli
    """,
)

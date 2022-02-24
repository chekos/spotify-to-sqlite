from pathlib import Path

from typer import get_app_dir

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

__app_name__ = "spotify-to-sqlite"

app_dir = Path(get_app_dir(__app_name__, force_posix=True))

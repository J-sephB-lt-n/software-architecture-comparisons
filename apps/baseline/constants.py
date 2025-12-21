"""Application global static configuration values."""

from pathlib import Path

DB_FILEPATH: Path = Path("./app_data.sqlite3")

AUTH_LOCAL_SESSION_FILEPATH: Path = Path(".tmp_auth")

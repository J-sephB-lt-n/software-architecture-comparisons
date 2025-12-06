"""Functions for interacting with the application database."""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from logging import getLogger, Logger
from typing import Iterator

logger: Logger = getLogger(__name__)


@contextmanager
def db_conn(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Context manager that yields a SQLite connection with sensible defaults."""
    conn: sqlite3.Connection = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        conn.commit()
    except Exception:
        logger.exception("Database error - rolling back transaction")
        conn.rollback()
        raise
    finally:
        conn.close()

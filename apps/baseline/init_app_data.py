"""Create the database and tables used by the app."""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

logger: logging.Logger = logging.getLogger(__name__)

DB_FILEPATH: Path = Path("./app_data.sqlite3")


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


def create_users_table(conn: sqlite3.Connection) -> None:
    """Create the (empty) users table."""
    conn.execute(
        """
        CREATE TABLE users (
                user_id     INTEGER PRIMARY KEY AUTOINCREMENT
            ,   username    TEXT NOT NULL UNIQUE
            ,   password    TEXT NOT NULL
        )
        """
    )
    logger.info("Created `users` table.")


def populate_users_table(conn: sqlite3.Connection) -> None:
    """Add some users to the `users` table."""
    new_users: list[tuple] = [
        ("joe", "admin1234"),
        ("emily", "ilovejoe"),
    ]
    conn.executemany(
        """
        INSERT INTO users (username, password)
        VALUES (?, ?)
        """,
        new_users,
    )
    logger.info("Added %s users to the `users` table", len(new_users))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    if DB_FILEPATH.exists():
        DB_FILEPATH.unlink()
        logger.warning("Deleted existing database at %s", DB_FILEPATH)

    with db_conn(DB_FILEPATH) as conn:
        create_users_table(conn)
        populate_users_table(conn)

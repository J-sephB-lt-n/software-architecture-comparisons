"""Create the database and tables used by the app."""

import logging
import sqlite3

from constants import DB_FILEPATH
from db import db_conn

logger: logging.Logger = logging.getLogger(__name__)


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


def create_user_login_status_table(conn: sqlite3.Connection) -> None:
    """
    Create the `user_login_status` table, which records which users are
    logged in.
    """
    conn.execute(
        """
        CREATE TABLE user_login_status (
                user_id             INTEGER PRIMARY KEY
            ,   status              TEXT NOT NULL CHECK(status IN ('LOGGED_IN'))
            ,   status_updated_at   TEXT NOT NULL
            ,   FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """
    )
    logger.info("Created `user_login_status` table.")


def db_setup() -> None:
    """Create the database and tables used by the app."""
    if DB_FILEPATH.exists():
        DB_FILEPATH.unlink()
        logger.warning("Deleted existing database at %s", DB_FILEPATH)

    with db_conn(DB_FILEPATH) as conn:
        create_users_table(conn)
        populate_users_table(conn)
        create_user_login_status_table(conn)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    db_setup()
    logging.info("Database creation complete.")

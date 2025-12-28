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
            ,   auth_token          TEXT 
            ,   FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """
    )
    logger.info("Created `user_login_status` table.")


def create_products_table(conn: sqlite3.Connection) -> None:
    """
    Create the `products` table, which contains a list of all
    unique products and their metdata.
    """
    conn.execute(
        """
        CREATE TABLE products (
                product_id      INTEGER PRIMARY KEY AUTOINCREMENT
            ,   name            TEXT NOT NULL
            ,   description     TEXT
            ,   price_cents     INTEGER NOT NULL CHECK (price_cents >= 0)
            ,   is_active       INTEGER NOT NULL DEFAULT 1 CHECK(is_active in (0,1))
        )
        """
    )
    logger.info("Created `products` table.")


def populate_products_table(conn: sqlite3.Connection) -> None:
    """Add some actual products into the `products` table."""
    products: list[tuple] = [
        ("Classic T-Shirt", "Unisex cotton t-shirt", 1999),
        ("Coffee Mug", "Ceramic mug 350ml", 1299),
        ("Zip Hoodie", "Fleece-lined zip hoodie", 4999),
    ]
    conn.executemany(
        """
        INSERT INTO products (name, description, price_cents)
        VALUES (?, ?, ?)
        """,
        products,
    )
    logger.info("Added %s products to the `products` table.", len(products))


def create_active_carts_table(conn: sqlite3.Connection) -> None:
    """Create the `active_carts` table, which lists the items in every users current cart."""
    conn.execute(
        """
        CREATE TABLE active_carts (
                user_id         INTEGER NOT NULL
            ,   product_id      INTEGER NOT NULL
            ,   quantity        INTEGER NOT NULL CHECK(quantity > 0)

            ,   PRIMARY KEY (user_id, product_id)

            ,   FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            ,   FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
        """
    )
    logger.info("Created `active_carts` table.")


def db_setup() -> None:
    """Create the database and tables used by the app."""
    if DB_FILEPATH.exists():
        DB_FILEPATH.unlink()
        logger.warning("Deleted existing database at %s", DB_FILEPATH)

    with db_conn(DB_FILEPATH) as conn:
        conn.execute(
            """
            PRAGMA foreign_keys = ON;
            """
        )
        create_users_table(conn)
        populate_users_table(conn)
        create_user_login_status_table(conn)
        create_products_table(conn)
        populate_products_table(conn)
        create_active_carts_table(conn)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    db_setup()
    logging.info("Database creation complete.")

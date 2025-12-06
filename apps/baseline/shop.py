"""Entrypoint script of the shop application."""

import argparse
import logging
import sqlite3
from collections.abc import Callable
from logging import getLogger, Logger

from constants import DB_FILEPATH
from db import db_conn

logger: Logger = getLogger(__name__)


def build_arg_parser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(prog="shop", description="Shop CLI")

    subparsers = arg_parser.add_subparsers(dest="cmd", required=True)

    auth_parser = subparsers.add_parser("auth", help="User authentication commands")
    auth_subparsers = auth_parser.add_subparsers(dest="auth_cmd", required=True)
    auth_login = auth_subparsers.add_parser("login", help="Log in to the app")
    auth_login.add_argument("--username", required=True)
    auth_login.add_argument("--password", required=True)
    auth_login.set_defaults(func=log_in_user)

    auth_logout = auth_subparsers.add_parser("logout", help="Log out of the app")
    auth_logout.add_argument("--username", required=True)
    auth_logout.set_defaults(func=log_out_user)

    products_parser = subparsers.add_parser("products", help="Product commands")
    products_subparsers = products_parser.add_subparsers(
        dest="products_cmd", required=True
    )
    products_list = products_subparsers.add_parser("list")
    products_view = products_subparsers.add_parser("view")

    return arg_parser


def main():
    arg_parser: argparse.ArgumentParser = build_arg_parser()
    args = arg_parser.parse_args()
    func: Callable = args.func
    kwargs: dict = {
        k: v
        for k, v in vars(args).items()
        if k not in ("cmd", "auth_cmd", "func", "products_cmd")
    }
    func(**kwargs)


def log_in_user(username: str, password: str) -> bool:
    """Authenticate a user against the database.

    Args:
        username (str): The username to authenticate
        password (str): The password to verify

    Returns:
        True if authentication successful, False otherwise
    """
    with db_conn(DB_FILEPATH) as conn:
        cursor: sqlite3.Cursor = conn.execute(
            "SELECT user_id, username, password FROM users WHERE username = ?",
            (username,),
        )
        user: sqlite3.Row | None = cursor.fetchone()

        if user is None or user["password"] != password:
            logger.info("User '%s' failed to log in.", username)
            return False

        user_id: int = user["user_id"]

        # Use UPSERT to avoid race conditions
        conn.execute(
            """
            INSERT INTO user_login_status (user_id, status, status_updated_at)
            VALUES (?, 'LOGGED_IN', datetime('now'))
            ON CONFLICT(user_id) 
            DO UPDATE SET 
                status = 'LOGGED_IN', 
                status_updated_at = datetime('now')
            """,
            (user_id,),
        )

        logger.info("User %s successfully logged in.", username)
        return True


def log_out_user(username: str) -> bool:
    """Log out a user by removing their login status.

    Args:
        username (str): The username to log out

    Returns:
        bool: Always returns True to prevent username enumeration
    """
    with db_conn(DB_FILEPATH) as conn:
        # Use atomic DELETE with JOIN to avoid race conditions
        cursor: sqlite3.Cursor = conn.execute(
            """
            DELETE FROM user_login_status 
            WHERE user_id IN (
                SELECT user_id FROM users WHERE username = ?
            )
            """,
            (username,),
        )

        if cursor.rowcount > 0:
            logger.info("User '%s' successfully logged out.", username)
        else:
            logger.info("Logout attempt for username '%s' (no action taken).", username)

        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    main()

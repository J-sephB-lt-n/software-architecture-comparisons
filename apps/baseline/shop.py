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
    products_list = products_subparsers.add_parser("list", help="List all products")
    products_list.set_defaults(func=list_products)

    products_view = products_subparsers.add_parser(
        "view", help="View a specific product"
    )
    products_view.add_argument("--product_id", required=True, type=int)
    products_view.set_defaults(func=view_product)

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
            print("LOGIN FAILED: username or password is incorrect or does not exist.")
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

        print("Logged in successfully.")
        return True


def log_out_user(username: str) -> bool:
    """Log out a user by removing their login status.

    Args:
        username (str): The username to log out

    Returns:
        bool: Always returns True to prevent username enumeration
    """
    with db_conn(DB_FILEPATH) as conn:
        _: sqlite3.Cursor = conn.execute(
            """
            DELETE FROM user_login_status 
            WHERE user_id IN (
                SELECT user_id FROM users WHERE username = ?
            )
            """,
            (username,),
        )

        print(f"User {username} successfully logged out.")

        return True


def list_products() -> None:
    """List all active products, showing product_id and name for each."""
    with db_conn(DB_FILEPATH) as conn:
        cursor: sqlite3.Cursor = conn.execute(
            "SELECT product_id, name FROM products WHERE is_active = 1 ORDER BY product_id"
        )
        products: list[sqlite3.Row] = cursor.fetchall()

        if not products:
            print("No products available.")
            return

        print("\nAvailable Products:")
        print("-" * 50)
        for product in products:
            print(f"ID: {product['product_id']:<5} Name: {product['name']}")
        print("-" * 50)


def view_product(product_id: int) -> None:
    """View detailed information for a specific product.

    Args:
        product_id (int): The ID of the product to view
    """
    with db_conn(DB_FILEPATH) as conn:
        cursor: sqlite3.Cursor = conn.execute(
            "SELECT * FROM products WHERE product_id = ?",
            (product_id,),
        )
        product: sqlite3.Row | None = cursor.fetchone()

        if product is None:
            print(f"Product with ID {product_id} not found.")
            return

        print("\nProduct Details:")
        print("=" * 50)
        print(f"Product ID:   {product['product_id']}")
        print(f"Name:         {product['name']}")
        print(f"Description:  {product['description']}")
        print(f"Price:        ${product['price_cents'] / 100:.2f}")
        print(f"Active:       {'Yes' if product['is_active'] else 'No'}")
        print("=" * 50)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    main()

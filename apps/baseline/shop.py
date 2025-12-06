"""Entrypoint script of the shop application."""

import argparse
import sqlite3
from collections.abc import Callable
from pathlib import Path

from db import db_conn


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
        k: v for k, v in vars(args).items() if k not in ("cmd", "auth_cmd", "func")
    }
    func(**kwargs)


def log_in_user(username: str, password: str) -> bool:
    """Authenticate a user against the database.
    
    Args:
        username: The username to authenticate
        password: The password to verify
        
    Returns:
        True if authentication successful, False otherwise
    """
    db_path = Path("./app_data.sqlite3")
    
    if not db_path.exists():
        print("Error: Database not found. Please run init_app_data.py first.")
        return False
    
    try:
        with db_conn(db_path) as conn:
            cursor = conn.execute(
                "SELECT user_id, username, password FROM users WHERE username = ?",
                (username,)
            )
            user = cursor.fetchone()
            
            if user is None:
                print(f"Error: User '{username}' not found.")
                return False
            
            # In a real application, you would use proper password hashing
            # (e.g., bcrypt, argon2) instead of storing plaintext passwords
            if user["password"] != password:
                print("Error: Incorrect password.")
                return False
            
            print(f"Successfully logged in as '{username}'.")
            return True
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def log_out_user() -> bool:
    """TODO."""
    print("logged out user")
    return True


if __name__ == "__main__":
    main()

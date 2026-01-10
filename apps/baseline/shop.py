"""Entrypoint script of the shop application."""

import argparse
import logging
import sqlite3
from collections.abc import Callable
from logging import getLogger, Logger
from uuid import UUID, uuid4

from constants import AUTH_LOCAL_SESSION_FILEPATH, DB_FILEPATH
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
    products_view.add_argument("--product-id", required=True, type=int)
    products_view.set_defaults(func=view_product)

    cart_parser = subparsers.add_parser(
        "cart", help="Manage items in current active user cart."
    )
    cart_subparsers = cart_parser.add_subparsers(dest="cart_cmd", required=True)
    cart_add = cart_subparsers.add_parser(
        "add",
        help="Add n items of a specific product_id to the logged in user's active cart.",
    )
    cart_add.add_argument("--product-id", required=True, type=int)
    cart_add.add_argument("--quantity", required=True, type=int)
    cart_add.set_defaults(func=add_item_to_cart)
    cart_remove = cart_subparsers.add_parser(
        "remove",
        help="Remove all items of --product-id from the logged in user's active cart.",
    )
    cart_remove.add_argument("--product-id", required=True, type=int)
    cart_remove.set_defaults(func=remove_item_from_cart)
    cart_update = cart_subparsers.add_parser(
        "update",
        help="Update quantity of item --product-id in logged in user's active cart.",
    )
    cart_update.add_argument("--product-id", required=True, type=int)
    cart_update.add_argument("--quantity", required=True, type=int)
    cart_update.set_defaults(func=update_item_in_cart)

    return arg_parser


def main():
    arg_parser: argparse.ArgumentParser = build_arg_parser()
    args = arg_parser.parse_args()
    func: Callable = args.func
    kwargs: dict = {
        k: v
        for k, v in vars(args).items()
        if k not in ("cmd", "auth_cmd", "func", "products_cmd", "cart_cmd")
    }
    func(**kwargs)


def log_in_user(username: str, password: str) -> bool:
    """Create a login session for a user.
    On successful login, creates a local .tmp_auth file (e.g. like a browser cookie)

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
        session_token_uuid: UUID = uuid4()

        # Use UPSERT to avoid race conditions #
        conn.execute(
            """
            INSERT INTO user_login_status (user_id, status, status_updated_at, auth_token)
            VALUES (?, 'LOGGED_IN', datetime('now'), ?)
            ON CONFLICT(user_id) 
            DO UPDATE SET 
                status = 'LOGGED_IN', 
                status_updated_at = datetime('now'),
                auth_token = excluded.auth_token
            """,
            (user_id, str(session_token_uuid)),
        )

        with open(AUTH_LOCAL_SESSION_FILEPATH, "w", encoding="utf-8") as file:
            file.write(str(session_token_uuid))

        print("Logged in successfully.")
        return True


def log_out_user() -> bool:
    """Log out a user by deleting their local session.

    Returns:
        bool: Always returns True to prevent username enumeration
    """
    user_id: int | None = _get_logged_in_user_id()

    AUTH_LOCAL_SESSION_FILEPATH.unlink(missing_ok=True)

    if user_id:
        with db_conn(DB_FILEPATH) as conn:
            _: sqlite3.Cursor = conn.execute(
                """
                DELETE FROM user_login_status 
                WHERE user_id = ?                
                """,
                (user_id,),
            )

    print("Successfully logged out.")

    return True


def _get_logged_in_user_id() -> int | None:
    """If there is a valid local session, return the logged in user_id, otherwise None."""
    if not AUTH_LOCAL_SESSION_FILEPATH.exists():
        return None

    with open(AUTH_LOCAL_SESSION_FILEPATH, "r", encoding="utf-8") as file:
        session_token: str = file.read().strip()

    if not session_token:
        return None

    with db_conn(DB_FILEPATH) as conn:
        cursor: sqlite3.Cursor = conn.execute(
            "SELECT user_id FROM user_login_status WHERE auth_token = ? AND status = 'LOGGED_IN'",
            (session_token,),
        )
        row: sqlite3.Row | None = cursor.fetchone()

        return row["user_id"] if row else None


def list_products() -> None:
    """List all active products, showing product_id and name for each."""
    with db_conn(DB_FILEPATH) as conn:
        cursor: sqlite3.Cursor = conn.execute(
            "SELECT product_id, name FROM products WHERE is_active = 1 ORDER BY product_id"
        )
        products: list[sqlite3.Row] = cursor.fetchall()

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


def add_item_to_cart(product_id: int, quantity: int) -> None:
    """Add `quantity` items of product `product_id` into the logged in user's cart."""
    if (user_id := _get_logged_in_user_id()) is None:
        print("WARNING: Cannot add item to cart. REASON: User is not logged in.")
        return

    with db_conn(DB_FILEPATH) as conn:
        cursor: sqlite3.Cursor = conn.execute(
            """
            INSERT INTO active_carts (user_id, product_id, quantity)
            SELECT :user_id, :product_id, :quantity
            WHERE EXISTS (SELECT 1 FROM products where product_id = :product_id and is_active=1)
            AND EXISTS (SELECT 1 FROM users where user_id = :user_id)
            ON CONFLICT (user_id, product_id) DO UPDATE
                SET quantity = quantity + excluded.quantity
            RETURNING   user_id, product_id, quantity
            """,
            {
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity,
            },
        )
        result: sqlite3.Row | None = cursor.fetchone()

        if cursor.rowcount == 0:
            print(f"WARNING: product_id='{product_id}' is inactive or does not exist.")
        else:
            print(
                f"SUCCESS: added {quantity} items of product_id={product_id}",
                f"to cart of user_id={user_id}",
            )

        if result is not None:
            updated_quantity = result["quantity"]
        else:
            updated_quantity = 0
        print(
            f"Current quantity of product_id={product_id} is {updated_quantity}",
            f"in active cart of user_id={user_id}",
        )

        return


def remove_item_from_cart(product_id: int) -> None:
    """Remove all items of `product_id` from cart of current logged in user."""
    if (user_id := _get_logged_in_user_id()) is None:
        print("WARNING: Cannot remove items from cart. REASON: User is not logged in.")
        return

    with db_conn(DB_FILEPATH) as conn:
        cursor: sqlite3.Cursor = conn.execute(
            """
            DELETE FROM active_carts
            WHERE   user_id = :user_id
                AND product_id = :product_id
            """,
            {
                "user_id": user_id,
                "product_id": product_id,
            },
        )

        if cursor.rowcount > 0:
            print(
                f"Removed all items of product_id={product_id} from cart of user_id={user_id}"
            )
        else:
            print(
                f"WARNING: No instances of item product_id={product_id} to remove from",
                f"cart of user_id={user_id}",
            )


def update_item_in_cart(product_id: int, quantity: int) -> None:
    """Change quantity of items of `product_id` in cart of current logged in user."""
    if (user_id := _get_logged_in_user_id()) is None:
        print(
            "WARNING: Cannot update item quantity in cart. REASON: User is not logged in."
        )
        return

    if quantity < 1:
        print("WARNING: Cannot update item quantity to less than 1 item.")
        return

    with db_conn(DB_FILEPATH) as conn:
        cursor: sqlite3.Cursor = conn.execute(
            """
            UPDATE      active_carts
            SET         quantity = :quantity
            WHERE       user_id = :user_id
            AND         product_id = :product_id
            RETURNING   quantity
            ;
            """,
            {
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity,
            },
        )

        row = cursor.fetchone()

        if row is None:
            print(
                f"WARNING: No instances of item product_id={product_id}",
                f"in cart of user_id={user_id}",
            )
        else:
            print(
                f"Updated quantity of product_id={product_id} to {row[0]} items",
                f"in cart of user_id={user_id}",
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    main()

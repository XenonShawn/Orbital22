# SQLite3 will be used while prototyping the bot. Once the exact table schemas are finalized, SQLite3 will be replaced.

import sqlite3
from collections import defaultdict
from datetime import datetime
from typing import Optional, Union
from enum import IntEnum

from supperbot.enums import Restaurants


class Stage(IntEnum):
    created = 0
    closed = 1


_con = sqlite3.connect("database.db")
_con.execute("PRAGMA foreign_keys = 1")

# Set up tables
_con.execute(
    """CREATE TABLE IF NOT EXISTS SupperJios (
                    id              INTEGER PRIMARY KEY NOT NULL,
                    description     TEXT NOT NULL,
                    restaurant      TEXT NOT NULL,
                    owner_id        INTEGER NOT NULL,
                    status          INTEGER NOT NULL,
                    chat_id         INTEGER,
                    message_id      INTEGER UNIQUE,
                    timestamp       TEXT NOT NULL)"""
)
_con.execute(
    """CREATE TABLE IF NOT EXISTS Orders (
                    jio_id          INTEGER NOT NULL,
                    user_id         INTEGER NOT NULL,
                    food            TEXT NOT NULL,
                    FOREIGN KEY (jio_id) REFERENCES SupperJios(id))"""
)
_con.execute(
    """CREATE TABLE IF NOT EXISTS Messages (
                    jio_id          INTEGER NOT NULL,
                    message_id      TEXT UNIQUE NOT NULL,
                    FOREIGN KEY(jio_id) REFERENCES SupperJios(id))"""
)
_con.execute(
    """CREATE TABLE IF NOT EXISTS Users (
                    user_id         INTEGER PRIMARY KEY NOT NULL,
                    display_name    TEXT NOT NULL)"""
)


def create_jio(owner_id: int, restaurant: Restaurants, description: str) -> int:
    """
    Creates a new supper jio entry in the database, and returns the supper jio order number.
    """

    with _con:
        _con.execute(
            "INSERT INTO SupperJios(owner_id, restaurant, description, status, timestamp)"
            "VALUES (?, ?, ?, ?, ?)",
            (owner_id, restaurant, description, 0, str(datetime.now())),
        )
        return _con.execute(
            "SELECT id FROM SupperJios WHERE owner_id = ? ORDER BY timestamp DESC",
            (owner_id,),
        ).fetchone()[0]


def get_jio(order_id: int) -> Optional[tuple[str, str]]:
    """
    Gets a supper jio based on its order_id

    :param order_id: The id of the user creating the supper jio.
    :return: The supper jio id.
    """
    with _con:
        row = _con.execute(
            "SELECT restaurant, description FROM SupperJios WHERE id = ? AND status = 0",
            (order_id,),
        ).fetchone()
        return row if row is not None else None


def get_jio_main_message(order_id: int) -> tuple[int, int]:
    with _con:
        return _con.execute(
            "SELECT chat_id, message_id FROM SupperJios WHERE id = ?", (order_id,)
        ).fetchone()


def update_jio_message_id(order_id: int, chat_id: int, message_id: int) -> None:
    with _con:
        _con.execute(
            "UPDATE SupperJios SET message_id = ? WHERE id = ?", (message_id, order_id)
        )
        _con.execute(
            "UPDATE SupperJios SET chat_id = ? WHERE id = ?", (chat_id, order_id)
        )


def get_orders(jio_id: int) -> dict[int, list[str]]:
    """Fetches a list of orders, tagged with the user's display name"""
    with _con:
        rows = _con.execute(
            "SELECT user_id, food FROM Orders WHERE jio_id = ?", (jio_id,)
        ).fetchall()

    result = defaultdict(list)
    for row in rows:
        result[row[0]].append(row[1])

    return result


def new_msg(order_id: int, message_id: str) -> None:
    with _con:
        _con.execute(
            "INSERT INTO Messages(jio_id, message_id) VALUES (?, ?)",
            (order_id, message_id),
        )


def get_msg(order_id: int) -> list[Union[str, int]]:
    # TODO: Add in the original message from SupperJio table as well
    with _con:
        rows = _con.execute(
            "SELECT message_id FROM Messages WHERE jio_id = ?", (order_id,)
        ).fetchall()
    return [r[0] for r in rows]


def add_order(jio_id: int, user_id: int, food: str) -> None:
    with _con:
        _con.execute(
            "INSERT INTO Orders(jio_id, user_id, food) VALUES (?, ?, ?)",
            (jio_id, user_id, food),
        )


def get_user_orders(jio_id: int, user_id: int) -> list[str]:
    with _con:
        rows = _con.execute(
            "SELECT food FROM Orders WHERE jio_id = ? AND user_id = ?",
            (jio_id, user_id),
        ).fetchall()
    return [r[0] for r in rows]


def upsert_user(user_id: int, display_name: str) -> None:
    with _con:
        _con.execute(
            """INSERT INTO Users(user_id, display_name) VALUES (?, ?) 
                        ON CONFLICT(user_id) DO UPDATE SET display_name=excluded.display_name""",
            (user_id, display_name),
        )


def get_user_name(user_id: int) -> Optional[str]:
    with _con:
        row = _con.execute(
            "SELECT display_name FROM Users WHERE user_id = ?", (user_id,)
        ).fetchone()
    return None if row is None else row[0]

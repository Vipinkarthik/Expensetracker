
import sqlite3
from pathlib import Path
from typing import Generator

DATABASE_PATH = Path(__file__).resolve().parent.parent / "expenses.db"


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Provide a database connection for an API request."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
    finally:
        connection.close()


def init_db() -> None:
    """Create the expenses table if it does not exist."""
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL CHECK (amount > 0),
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    finally:
        connection.close()

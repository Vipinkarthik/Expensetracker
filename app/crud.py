
import sqlite3
from datetime import date
from typing import Optional

from app.schemas import ExpenseCreate


def create_expense(
    db: sqlite3.Connection,
    expense: ExpenseCreate,
) -> dict:
    cursor = db.execute(
        """
        INSERT INTO expenses (amount, category, date)
        VALUES (?, ?, ?)
        """,
        (expense.amount, expense.category, expense.date.isoformat()),
    )
    db.commit()

    row = db.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()

    return dict(row)


def list_expenses(
    db: sqlite3.Connection,
    category: Optional[str] = None,
) -> list[dict]:
    if category is not None:
        rows = db.execute(
            """
            SELECT * FROM expenses
            WHERE category = ? COLLATE NOCASE
            ORDER BY date DESC, id DESC
            """,
            (category.strip(),),
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT * FROM expenses
            ORDER BY date DESC, id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_category_totals(
    db: sqlite3.Connection,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[dict]:
    query = """
        SELECT category, ROUND(SUM(amount), 2) AS total
        FROM expenses
        WHERE 1 = 1
    """
    params = []

    if start_date is not None:
        query += " AND date >= ?"
        params.append(start_date.isoformat())

    if end_date is not None:
        query += " AND date <= ?"
        params.append(end_date.isoformat())

    query += " GROUP BY category COLLATE NOCASE ORDER BY category COLLATE NOCASE"

    rows = db.execute(query, params).fetchall()

    return [
        {"category": row["category"], "total": row["total"]}
        for row in rows
    ]


import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app


@pytest.fixture
def client(tmp_path):
    test_db_path = tmp_path / "test_expenses.db"

    connection = sqlite3.connect(test_db_path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL CHECK (amount > 0),
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()
    connection.close()

    def override_get_db():
        db = sqlite3.connect(test_db_path)
        db.row_factory = sqlite3.Row

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def add_sample_expenses(client):
    expenses = [
        {"amount": 250, "category": "food", "date": "2026-10-19"},
        {"amount": 500, "category": "travel", "date": "2026-10-19"},
        {"amount": 300, "category": "food", "date": "2026-10-20"},
    ]

    for expense in expenses:
        response = client.post("/expenses", json=expense)
        assert response.status_code == 201


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_list_expense(client):
    response = client.post(
        "/expenses",
        json={
            "amount": 250,
            "category": "food",
            "date": "2026-10-19",
        },
    )

    assert response.status_code == 201
    assert response.json()["amount"] == 250

    listing = client.get("/expenses")

    assert listing.status_code == 200
    assert len(listing.json()) == 1


@pytest.mark.parametrize("amount", [0, -10])
def test_reject_non_positive_amount(client, amount):
    response = client.post(
        "/expenses",
        json={
            "amount": amount,
            "category": "food",
            "date": "2026-10-19",
        },
    )

    assert response.status_code == 422


def test_reject_missing_fields(client):
    response = client.post(
        "/expenses",
        json={"amount": 250, "category": "food"},
    )

    assert response.status_code == 422


def test_reject_invalid_date(client):
    response = client.post(
        "/expenses",
        json={
            "amount": 250,
            "category": "food",
            "date": "not-a-date",
        },
    )

    assert response.status_code == 422


def test_category_filter(client):
    add_sample_expenses(client)

    response = client.get("/expenses", params={"category": "food"})

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(item["category"] == "food" for item in response.json())


def test_category_totals(client):
    add_sample_expenses(client)

    response = client.get("/expenses/totals")

    assert response.status_code == 200

    totals = {
        item["category"]: item["total"]
        for item in response.json()
    }

    assert totals == {"food": 550, "travel": 500}


def test_totals_with_date_range(client):
    add_sample_expenses(client)

    response = client.get(
        "/expenses/totals",
        params={
            "start_date": "2026-10-20",
            "end_date": "2026-10-20",
        },
    )

    assert response.status_code == 200
    assert response.json() == [{"category": "food", "total": 300}]


def test_reject_invalid_date_range(client):
    response = client.get(
        "/expenses/totals",
        params={
            "start_date": "2026-10-20",
            "end_date": "2026-10-19",
        },
    )

    assert response.status_code == 422

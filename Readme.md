
# Expense Tracker API

A lightweight REST API for recording expenses and calculating
spending totals by category.

## Features

- Create expenses with positive amounts
- List all expenses
- Filter expenses by category
- Calculate category-wise spending totals
- Filter totals by a date range
- Persist data using SQLite
- Interactive API documentation
- Automated tests using pytest

## Technology Stack

- Python
- FastAPI
- SQLite
- pytest

## Setup

Create and activate a virtual environment.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the API

```bash
python -m uvicorn app.main:app --reload
```

Open the API documentation:

http://127.0.0.1:8000/docs

## Run tests

```bash
python -m pytest -v
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | Welcome message |
| GET | /health | Health check |
| POST | /expenses | Create expense |
| GET | /expenses | List expenses |
| GET | /expenses?category=food | Filter expenses |
| GET | /expenses/totals | Category totals |
| GET | /expenses/totals?start_date=2026-10-01&end_date=2026-10-31 | Date-filtered totals |

## Example Expense

```json
{
  "amount": 250,
  "category": "food",
  "date": "2026-10-19"
}
```

## Scope Limitations

This version does not include authentication, a frontend,
editing or deleting expenses, budgets, or multiple currencies.

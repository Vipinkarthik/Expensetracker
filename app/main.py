
from contextlib import asynccontextmanager
from datetime import date
import sqlite3
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status

from app.crud import create_expense, get_category_totals, list_expenses
from app.database import get_db, init_db
from app.schemas import CategoryTotal, ExpenseCreate, ExpenseResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Expense Tracker API",
    description=(
        "A simple expense tracking service with category filtering "
        "and date-range spending summaries."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Expense Tracker API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_expense(
    expense: ExpenseCreate,
    db: Annotated[sqlite3.Connection, Depends(get_db)],
):
    return create_expense(db, expense)


@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    category: Optional[str] = Query(default=None, max_length=50),
):
    if category is not None and not category.strip():
        raise HTTPException(
            status_code=422,
            detail="Category filter cannot be empty",
        )

    return list_expenses(db, category)


@app.get("/expenses/totals", response_model=list[CategoryTotal])
def expense_totals(
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be on or before end_date",
        )

    return get_category_totals(db, start_date, end_date)

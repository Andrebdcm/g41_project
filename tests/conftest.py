"""Shared pytest fixtures and path setup."""

import sqlite3
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GROUP_ROOT = PROJECT_ROOT.parent
CSV_PATH = GROUP_ROOT / "g41_Publishers_Magazines_v2.csv"
DB_PATH = PROJECT_ROOT / "data" / "publishers_magazines.db"

# Make project modules importable in tests.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

EXPECTED_COLUMNS = [
    "publisher_id",
    "magazine_id",
    "transaction_date",
    "amount",
    "publisher_name",
    "created_date",
    "magazine_title",
    "magazine_category",
    "warehouses_id",
    "warehouses_info",
]


@pytest.fixture(scope="session")
def csv_df() -> pd.DataFrame:
    """Return the source CSV loaded with the proper encoding."""
    assert CSV_PATH.exists(), f"CSV file not found at {CSV_PATH}"
    df = pd.read_csv(CSV_PATH, sep=";", dtype=str, encoding="latin-1").fillna("")
    return df


@pytest.fixture(scope="session")
def db_connection() -> sqlite3.Connection:
    """Return a live SQLite connection to the generated database."""
    assert DB_PATH.exists(), f"Database file not found at {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

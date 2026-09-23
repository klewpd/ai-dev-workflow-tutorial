"""Tests for metrics.py.

Two kinds of tests:
- Small hand-made data, where every expected answer can be checked by eye.
- The real data/sales-data.csv, checked against the known values in the
  design spec (docs/superpowers/specs/2026-09-22-sales-dashboard-design.md).
"""

from pathlib import Path

import pandas as pd
import pytest

import metrics

REAL_CSV = Path(__file__).parent.parent / "data" / "sales-data.csv"

CSV_HEADER = "date,order_id,product,category,region,quantity,unit_price,total_amount\n"


def write_csv(tmp_path, text):
    """Write CSV text to a temporary file and return its path."""
    path = tmp_path / "sales.csv"
    path.write_text(text)
    return path


@pytest.fixture(scope="module")
def real_sales():
    """The real sales data, loaded once for all tests in this file."""
    return metrics.load_sales_data(REAL_CSV)


# --- load_sales_data --------------------------------------------------------


def test_load_parses_dates(tmp_path):
    path = write_csv(
        tmp_path, CSV_HEADER + "2024-01-15,ORD-1,Headphones,Audio,North,2,49.99,99.98\n"
    )
    df = metrics.load_sales_data(path)
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df.loc[0, "date"] == pd.Timestamp("2024-01-15")


def test_load_rejects_missing_columns(tmp_path):
    path = write_csv(tmp_path, "date,order_id,total_amount\n2024-01-15,ORD-1,99.98\n")
    with pytest.raises(
        ValueError, match="missing columns: product, category, region, quantity, unit_price"
    ):
        metrics.load_sales_data(path)


def test_load_rejects_missing_date_column_clearly(tmp_path):
    path = write_csv(
        tmp_path,
        "order_id,product,category,region,quantity,unit_price,total_amount\n"
        "ORD-1,Headphones,Audio,North,2,49.99,99.98\n",
    )
    with pytest.raises(ValueError, match="missing columns: date"):
        metrics.load_sales_data(path)


def test_load_rejects_non_numeric_total_amount(tmp_path):
    path = write_csv(
        tmp_path, CSV_HEADER + "2024-01-15,ORD-1,Headphones,Audio,North,2,49.99,$99.98\n"
    )
    with pytest.raises(ValueError, match="total_amount"):
        metrics.load_sales_data(path)


def test_load_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        metrics.load_sales_data(tmp_path / "does-not-exist.csv")


def test_real_csv_loads_all_rows(real_sales):
    assert len(real_sales) == 482
    assert pd.api.types.is_datetime64_any_dtype(real_sales["date"])

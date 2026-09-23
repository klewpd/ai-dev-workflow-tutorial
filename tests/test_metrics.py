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


def test_load_rejects_blank_total_amount(tmp_path):
    # A blank amount would be skipped by the sum, making Total Sales too low.
    path = write_csv(
        tmp_path,
        CSV_HEADER
        + "2024-01-15,ORD-1,Headphones,Audio,North,2,49.99,99.98\n"
        + "2024-01-16,ORD-2,Headphones,Audio,North,1,49.99,\n",
    )
    with pytest.raises(ValueError, match="blank values in columns: total_amount"):
        metrics.load_sales_data(path)


def test_load_rejects_blank_category_and_region(tmp_path):
    # A row with no category or region would be left out of the bar charts,
    # so the bars would no longer add up to Total Sales.
    path = write_csv(
        tmp_path,
        CSV_HEADER
        + "2024-01-15,ORD-1,Headphones,Audio,North,2,49.99,99.98\n"
        + "2024-01-16,ORD-2,Headphones,,,1,49.99,49.99\n",
    )
    with pytest.raises(ValueError, match="blank values in columns: category, region"):
        metrics.load_sales_data(path)


def test_load_rejects_blank_date(tmp_path):
    # A blank date can't be placed in a month, and would crash the page's
    # date-range caption instead of showing a clear error.
    path = write_csv(
        tmp_path,
        CSV_HEADER
        + "2024-01-15,ORD-1,Headphones,Audio,North,2,49.99,99.98\n"
        + ",ORD-2,Headphones,Audio,North,1,49.99,49.99\n",
    )
    with pytest.raises(ValueError, match="blank values in columns: date"):
        metrics.load_sales_data(path)


def test_load_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        metrics.load_sales_data(tmp_path / "does-not-exist.csv")


def test_real_csv_loads_all_rows(real_sales):
    assert len(real_sales) == 482
    assert pd.api.types.is_datetime64_any_dtype(real_sales["date"])


# --- Small hand-made data ---------------------------------------------------


@pytest.fixture
def small_sales():
    """Five rows whose totals are easy to add up by hand.

    Order A3 has two rows (two items in one order), so it must count once.
    Totals: sales 100.0; orders 4; Jan 30, Feb 55, Mar 15;
    Wearables 65, Audio 30, Accessories 5; North 60, South 35, East 5.
    """
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-05", "2024-01-20", "2024-02-03", "2024-02-10", "2024-03-15"]
            ),
            "order_id": ["A1", "A2", "A3", "A3", "A4"],
            "category": ["Audio", "Audio", "Wearables", "Accessories", "Wearables"],
            "region": ["North", "South", "North", "East", "South"],
            "total_amount": [10.0, 20.0, 50.0, 5.0, 15.0],
        }
    )


# --- total_sales / total_orders ---------------------------------------------


def test_total_sales_adds_every_row(small_sales):
    assert metrics.total_sales(small_sales) == 100.0


def test_total_orders_counts_each_order_once(small_sales):
    assert metrics.total_orders(small_sales) == 4


def test_real_csv_totals(real_sales):
    assert metrics.total_sales(real_sales) == pytest.approx(116500.21)
    assert metrics.total_orders(real_sales) == 482


# --- monthly_sales ----------------------------------------------------------


def test_monthly_sales_groups_by_month_in_order(small_sales):
    result = metrics.monthly_sales(small_sales)
    assert list(result.columns) == ["month", "total_amount"]
    assert list(result["month"]) == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
        pd.Timestamp("2024-03-01"),
    ]
    assert list(result["total_amount"]) == [30.0, 55.0, 15.0]


def test_monthly_sales_keeps_years_apart():
    # January 2025 is listed first on purpose: the result must still be in
    # time order, and the two Januaries must not be merged into one row.
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-10", "2024-01-10"]),
            "total_amount": [20.0, 10.0],
        }
    )
    result = metrics.monthly_sales(df)
    assert list(result["month"]) == [pd.Timestamp("2024-01-01"), pd.Timestamp("2025-01-01")]
    assert list(result["total_amount"]) == [10.0, 20.0]


def test_real_csv_has_twelve_months(real_sales):
    result = metrics.monthly_sales(real_sales)
    assert len(result) == 12
    assert result["total_amount"].sum() == pytest.approx(116500.21)


# --- sales_by_category / sales_by_region ------------------------------------


def test_sales_by_category_sorted_highest_first(small_sales):
    result = metrics.sales_by_category(small_sales)
    assert list(result.columns) == ["category", "total_amount"]
    assert list(result["category"]) == ["Wearables", "Audio", "Accessories"]
    assert list(result["total_amount"]) == [65.0, 30.0, 5.0]


def test_sales_by_region_sorted_highest_first(small_sales):
    result = metrics.sales_by_region(small_sales)
    assert list(result.columns) == ["region", "total_amount"]
    assert list(result["region"]) == ["North", "South", "East"]
    assert list(result["total_amount"]) == [60.0, 35.0, 5.0]


def test_real_csv_category_order(real_sales):
    result = metrics.sales_by_category(real_sales)
    assert list(result["category"]) == [
        "Electronics",
        "Wearables",
        "Audio",
        "Smart Home",
        "Accessories",
    ]


def test_real_csv_region_order(real_sales):
    result = metrics.sales_by_region(real_sales)
    assert list(result["region"]) == ["North", "West", "East", "South"]

"""Sales calculations for the ShopSmart dashboard.

Every function here takes a pandas DataFrame and returns plain numbers or a
small DataFrame. Nothing in this file knows about Streamlit or Plotly, so it
can be tested on its own with pytest.
"""

import pandas as pd

# The columns sales-data.csv must contain (see the PRD's Data Specification).
EXPECTED_COLUMNS = [
    "date",
    "order_id",
    "product",
    "category",
    "region",
    "quantity",
    "unit_price",
    "total_amount",
]

# Columns the dashboard adds up or groups by. Pandas reads a blank cell as
# NaN (or NaT for dates) and quietly leaves it out of sums and groups, so a
# blank here would make a total or a chart wrong with no sign of trouble.
NO_BLANKS_COLUMNS = ["date", "total_amount", "category", "region"]


def load_sales_data(path):
    """Read the sales CSV and check it has what the dashboard needs.

    Raises FileNotFoundError if the file doesn't exist, and ValueError if
    columns are missing, total_amount isn't numeric, or date, total_amount,
    category or region has blank values.
    """
    df = pd.read_csv(path)

    # Check the columns before touching any of them, so a missing column
    # gives one clear message instead of a confusing Pandas error.
    missing = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Sales data is missing columns: {', '.join(missing)}")

    # A value like "$99.98" makes Pandas read the whole column as text,
    # and summing text would silently glue the strings together.
    if not pd.api.types.is_numeric_dtype(df["total_amount"]):
        raise ValueError("Sales data column 'total_amount' must contain only numbers")

    blank = [column for column in NO_BLANKS_COLUMNS if df[column].isna().any()]
    if blank:
        raise ValueError(f"Sales data has blank values in columns: {', '.join(blank)}")

    df["date"] = pd.to_datetime(df["date"])
    return df


def total_sales(df):
    """Sum of every transaction's total_amount."""
    return float(df["total_amount"].sum())


def total_orders(df):
    """Number of distinct orders (an order with several rows counts once)."""
    return int(df["order_id"].nunique())


def monthly_sales(df):
    """Total sales for each calendar month, oldest month first.

    Returns columns: month (the first day of that month) and total_amount.
    """
    # to_period("M") keeps the year, so Jan 2024 and Jan 2025 stay separate.
    month = df["date"].dt.to_period("M").dt.to_timestamp().rename("month")
    return df.groupby(month)["total_amount"].sum().reset_index()


def _sales_by(df, column):
    """Total sales for each value in `column`, highest first.

    Shared by sales_by_category and sales_by_region.
    """
    return (
        df.groupby(column)["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


def sales_by_category(df):
    """Total sales per product category, highest first."""
    return _sales_by(df, "category")


def sales_by_region(df):
    """Total sales per region, highest first."""
    return _sales_by(df, "region")

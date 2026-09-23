# ShopSmart Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page Streamlit dashboard showing ShopSmart's 2024 KPIs, monthly sales trend, and sales by category and region, from `data/sales-data.csv`.

**Architecture:** `metrics.py` holds pure Pandas functions (load + calculations) with no Streamlit or Plotly imports, tested by `tests/test_metrics.py`. `app.py` loads the data through a cached wrapper, calls the `metrics` functions, formats the results, and renders `st.metric` cards and Plotly charts top to bottom.

**Tech Stack:** Python 3.11+ (local: 3.14), Streamlit 1.64.0, Pandas 3.0.6, Plotly 7.1.0, pytest 9.1.1, plain `venv/`.

**Spec:** `docs/superpowers/specs/2026-09-22-sales-dashboard-design.md`

## How this plan is numbered

Plan tasks use **letters (A–G)** so they never get confused with the milestone IDs in `TASKS.md` (**TASK-1 … TASK-7**). Every plan task is labeled with the milestone it belongs to:

| Plan task | Milestone | Owner |
|---|---|---|
| A: Environment and app skeleton | TASK-1 | Claude |
| B: Data loading | TASK-2 | Claude |
| C: KPI cards | TASK-3 | Claude |
| D: Monthly sales trend | TASK-4 | Claude |
| E: Category and region breakdowns | TASK-5 | Claude |
| F: Verification and polish | TASK-6 | Claude (+ your visual check) |
| G: Deployment hand-off | TASK-7 | **You**: execution stops before this |

## Global Constraints

- Work on the current branch `feature/sales-dashboard`. Do not create a git worktree or a new branch.
- Plain virtual environment in `venv/` (`python3 -m venv venv`) and `requirements.txt`. No uv, no conda.
- `requirements.txt` pins exact versions: `streamlit==1.64.0`, `pandas==3.0.6`, `plotly==7.1.0`, `pytest==9.1.1`.
- `metrics.py` never imports Streamlit or Plotly. `app.py` does no arithmetic on the data beyond formatting.
- Display formatting lives in `app.py` only: Total Sales as `f"${value:,.0f}"`, Total Orders as `f"{value:,}"`.
- Total Orders = `df["order_id"].nunique()`. The trend is monthly.
- Render charts with `st.plotly_chart(fig, width="stretch")`. **Do not use `use_container_width=True`**: it is deprecated in Streamlit 1.64 and prints a warning, and the PRD requires no warnings. (The spec was updated to match.)
- The CSV path is `Path(__file__).parent / "data" / "sales-data.csv"`.
- Run tools from the project root through the venv explicitly: `venv/bin/python -m pytest`, `venv/bin/streamlit`. Shell activation doesn't persist between agent commands.
- Every commit message starts with its milestone ID (`TASK-N: ...`) and ends with the session's `Co-Authored-By` trailer.
- Do **not** edit `TASKS.md`. Moving milestones between sections and filling in `Commit:` lines is the user's job.
- Simple, readable, commented code. No custom CSS, no `.streamlit/config.toml`.

## Review Focus

Inputs and conditions the spec implies but doesn't spell out, most likely to cause trouble first. Each is pinned by a test or check in the plan task shown:

1. **App launched from a different folder** (e.g. Streamlit Cloud, or `streamlit run path/to/app.py`): must still find the CSV. Pinned by the from-another-directory run in Plan Task F, Step 2.
2. **Months from different years**: January 2024 and January 2025 must stay separate rows, in time order. Pinned by `test_monthly_sales_keeps_years_apart` (Plan Task D).
3. **Non-numeric `total_amount`** (e.g. `$99.98` in the file): Pandas reads it as text, and summing text silently concatenates strings. `load_sales_data` must raise a clear `ValueError` instead. Pinned by `test_load_rejects_non_numeric_total_amount` (Plan Task B).
4. **CSV missing or missing columns**: the user must see a plain sentence, not a stack trace, and `date` missing must say "missing columns", not a Pandas `parse_dates` error. Pinned by `test_load_rejects_missing_columns` and `test_load_missing_file_raises_file_not_found` (Plan Task B); the `st.error` path is in `app.py`.
5. **Floating-point totals**: summing 482 prices gives `116500.21000000002`-style values. Tests use `pytest.approx`, and the display rounds to whole dollars. Pinned by `test_real_csv_totals` (Plan Task C).

---

## File Structure

| File | Responsibility | Created in |
|---|---|---|
| `requirements.txt` | Pinned dependencies (local and Streamlit Cloud) | A |
| `pytest.ini` | Tells pytest where tests live and lets `tests/` import `metrics` from the project root | A |
| `app.py` | Streamlit page: layout, formatting, charts | A (grows in B–E) |
| `metrics.py` | Pure Pandas load + calculation functions | B (grows in C–E) |
| `tests/test_metrics.py` | pytest tests for `metrics.py` | B (grows in C–E) |

---

### Plan Task A — Milestone TASK-1: Environment and app skeleton

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `app.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `venv/` with all packages installed; `app.py` showing the title; `pytest` able to import top-level modules from `tests/`.

- [ ] **Step 1: Create the virtual environment**

Run: `python3 -m venv venv`
Expected: a `venv/` folder appears. Confirm it is ignored: `git status --short` must **not** list `venv/`.

- [ ] **Step 2: Write `requirements.txt`**

```text
streamlit==1.64.0
pandas==3.0.6
plotly==7.1.0
pytest==9.1.1
```

- [ ] **Step 3: Install the requirements**

Run: `venv/bin/pip install -r requirements.txt`
Expected: ends with `Successfully installed ...` and no errors. Then run `venv/bin/pip check`. Expected: `No broken requirements found.`

- [ ] **Step 4: Write `pytest.ini`**

```ini
[pytest]
# Tests live in tests/; the project root goes on the import path so
# tests can simply "import metrics".
testpaths = tests
pythonpath = .
```

- [ ] **Step 5: Write `app.py`**

```python
"""ShopSmart Sales Dashboard.

Run locally with:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")
```

- [ ] **Step 6: Check the app renders**

Run:
```bash
venv/bin/python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py', default_timeout=30).run()
assert not at.exception, at.exception
print('Title:', at.title[0].value)
"
```
Expected: `Title: ShopSmart Sales Dashboard`

- [ ] **Step 7: Check `streamlit run app.py` starts a server**

Run:
```bash
venv/bin/streamlit run app.py --server.headless true --server.port 8501 > "$TMPDIR/streamlit-a.log" 2>&1 &
sleep 5; curl -s http://localhost:8501/_stcore/health; echo; kill $!
```
Expected: `ok`

- [ ] **Step 8: Commit**

```bash
git add requirements.txt pytest.ini app.py
git commit -m "TASK-1: Set up venv requirements and app skeleton"
```
Expected: `git status --short` is empty afterwards (`venv/` stays ignored).

---

### Plan Task B — Milestone TASK-2: Data loading

**Files:**
- Create: `metrics.py`
- Create: `tests/test_metrics.py`
- Modify: `app.py` (replace whole file)

**Interfaces:**
- Consumes: `venv/`, `pytest.ini` from Plan Task A.
- Produces:
  - `metrics.EXPECTED_COLUMNS: list[str]`
  - `metrics.load_sales_data(path) -> pd.DataFrame` with `date` as datetime; raises `ValueError` (missing columns or non-numeric `total_amount`) or `FileNotFoundError`.
  - In `tests/test_metrics.py`: `REAL_CSV` path, `write_csv(tmp_path, text)` helper, `CSV_HEADER` string, and the module-scoped fixture `real_sales`.
  - In `app.py`: `DATA_PATH`, `load_data(path)` (cached), and a loaded `df` available below the loading block.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_metrics.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `venv/bin/python -m pytest -v`
Expected: collection ERROR with `ModuleNotFoundError: No module named 'metrics'`

- [ ] **Step 3: Write `metrics.py`**

```python
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


def load_sales_data(path):
    """Read the sales CSV and check it has what the dashboard needs.

    Raises FileNotFoundError if the file doesn't exist, and ValueError if
    columns are missing or total_amount isn't numeric.
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

    df["date"] = pd.to_datetime(df["date"])
    return df
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `venv/bin/python -m pytest -v`
Expected: `6 passed`

- [ ] **Step 5: Wire loading into `app.py`**

Replace the whole of `app.py` with:

```python
"""ShopSmart Sales Dashboard.

Run locally with:  streamlit run app.py
"""

from pathlib import Path

import streamlit as st

import metrics

# Build the path from this file's location so the app finds the data no
# matter which folder it is launched from (including Streamlit Cloud).
DATA_PATH = Path(__file__).parent / "data" / "sales-data.csv"


@st.cache_data
def load_data(path):
    """Load the sales data once and reuse it on every rerun of the page."""
    return metrics.load_sales_data(path)


st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

try:
    df = load_data(DATA_PATH)
except (FileNotFoundError, ValueError) as error:
    st.error(f"Could not load the sales data: {error}")
    st.stop()

st.caption(f"Sales data: {df['date'].min():%b %Y} – {df['date'].max():%b %Y}")
```

- [ ] **Step 6: Check the app renders with data**

Run:
```bash
venv/bin/python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py', default_timeout=30).run()
assert not at.exception, at.exception
assert not at.error, at.error
print(at.caption[0].value)
"
```
Expected: `Sales data: Jan 2024 – Dec 2024`

- [ ] **Step 7: Commit**

```bash
git add metrics.py tests/test_metrics.py app.py
git commit -m "TASK-2: Load and validate sales data with tests"
```

---

### Plan Task C — Milestone TASK-3: KPI cards

**Files:**
- Modify: `metrics.py` (append two functions)
- Modify: `tests/test_metrics.py` (append)
- Modify: `app.py` (append KPI block)

**Interfaces:**
- Consumes: `metrics.load_sales_data`, `real_sales` fixture, and `df` in `app.py` (Plan Task B).
- Produces:
  - `metrics.total_sales(df) -> float`
  - `metrics.total_orders(df) -> int`
  - The `small_sales` fixture in `tests/test_metrics.py` (5 rows; used again in Plan Tasks D and E).

- [ ] **Step 1: Write the failing tests**

Append to the end of `tests/test_metrics.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `venv/bin/python -m pytest -v`
Expected: 3 FAIL with `AttributeError: module 'metrics' has no attribute 'total_sales'` (or `total_orders`); the 6 earlier tests still pass.

- [ ] **Step 3: Implement**

Append to the end of `metrics.py`:

```python
def total_sales(df):
    """Sum of every transaction's total_amount."""
    return float(df["total_amount"].sum())


def total_orders(df):
    """Number of distinct orders (an order with several rows counts once)."""
    return int(df["order_id"].nunique())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `venv/bin/python -m pytest -v`
Expected: `9 passed`

- [ ] **Step 5: Add the KPI cards to `app.py`**

Append to the end of `app.py`:

```python

# --- KPI cards --------------------------------------------------------------
sales_card, orders_card = st.columns(2)
sales_card.metric("Total Sales", f"${metrics.total_sales(df):,.0f}")
orders_card.metric("Total Orders", f"{metrics.total_orders(df):,}")
```

- [ ] **Step 6: Check the cards show the right values**

Run:
```bash
venv/bin/python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py', default_timeout=30).run()
assert not at.exception, at.exception
for m in at.metric: print(m.label, '=', m.value)
"
```
Expected:
```
Total Sales = $116,500
Total Orders = 482
```

- [ ] **Step 7: Commit**

```bash
git add metrics.py tests/test_metrics.py app.py
git commit -m "TASK-3: Add total sales and orders KPI cards with tests"
```

---

### Plan Task D — Milestone TASK-4: Monthly sales trend

**Files:**
- Modify: `metrics.py` (append one function)
- Modify: `tests/test_metrics.py` (append)
- Modify: `app.py` (add import + constant near top; append trend block)

**Interfaces:**
- Consumes: `small_sales` and `real_sales` fixtures; `df` in `app.py`.
- Produces:
  - `metrics.monthly_sales(df) -> pd.DataFrame` with columns `month` (Timestamp, first of month) and `total_amount`, oldest month first.
  - In `app.py`: `import plotly.express as px` and `ACCENT_COLOR` (used again in Plan Task E).

- [ ] **Step 1: Write the failing tests**

Append to the end of `tests/test_metrics.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `venv/bin/python -m pytest -v`
Expected: 3 FAIL with `AttributeError: module 'metrics' has no attribute 'monthly_sales'`; 9 pass.

- [ ] **Step 3: Implement**

Append to the end of `metrics.py`:

```python
def monthly_sales(df):
    """Total sales for each calendar month, oldest month first.

    Returns columns: month (the first day of that month) and total_amount.
    """
    # to_period("M") keeps the year, so Jan 2024 and Jan 2025 stay separate.
    month = df["date"].dt.to_period("M").dt.to_timestamp().rename("month")
    return df.groupby(month)["total_amount"].sum().reset_index()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `venv/bin/python -m pytest -v`
Expected: `12 passed`

- [ ] **Step 5: Add the trend chart to `app.py`**

At the top of `app.py`, add the Plotly import with the other imports, so the import block reads:

```python
from pathlib import Path

import plotly.express as px
import streamlit as st

import metrics
```

Directly below the `DATA_PATH = ...` line, add:

```python

# One accent color shared by every chart, for a consistent look.
ACCENT_COLOR = "#1f77b4"
```

Append to the end of `app.py`:

```python

# --- Monthly sales trend ----------------------------------------------------
st.subheader("Monthly Sales Trend")
trend_chart = px.line(
    metrics.monthly_sales(df),
    x="month",
    y="total_amount",
    markers=True,
    labels={"month": "Month", "total_amount": "Sales ($)"},
    color_discrete_sequence=[ACCENT_COLOR],
)
# Tooltip shows the month and the exact amount; <extra></extra> hides the
# gray trace-name box Plotly adds by default.
trend_chart.update_traces(hovertemplate="%{x|%b %Y}<br>$%{y:,.2f}<extra></extra>")
trend_chart.update_layout(xaxis_tickformat="%b %Y", yaxis_tickprefix="$", yaxis_tickformat=",")
st.plotly_chart(trend_chart, width="stretch")
```

- [ ] **Step 6: Check the app renders the chart**

Run:
```bash
venv/bin/python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py', default_timeout=30).run()
assert not at.exception, at.exception
print([s.value for s in at.subheader])
"
```
Expected: `['Monthly Sales Trend']`

- [ ] **Step 7: Commit**

```bash
git add metrics.py tests/test_metrics.py app.py
git commit -m "TASK-4: Add monthly sales trend chart with tests"
```

---

### Plan Task E — Milestone TASK-5: Category and region breakdowns

**Files:**
- Modify: `metrics.py` (append three functions)
- Modify: `tests/test_metrics.py` (append)
- Modify: `app.py` (append chart helper + breakdown block)

**Interfaces:**
- Consumes: `small_sales` and `real_sales` fixtures; `df`, `px`, `ACCENT_COLOR` in `app.py`.
- Produces:
  - `metrics._sales_by(df, column) -> pd.DataFrame` (private helper)
  - `metrics.sales_by_category(df) -> pd.DataFrame` with columns `category`, `total_amount`, highest first
  - `metrics.sales_by_region(df) -> pd.DataFrame` with columns `region`, `total_amount`, highest first

- [ ] **Step 1: Write the failing tests**

Append to the end of `tests/test_metrics.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `venv/bin/python -m pytest -v`
Expected: 4 FAIL with `AttributeError: module 'metrics' has no attribute 'sales_by_category'` (or `sales_by_region`); 12 pass.

- [ ] **Step 3: Implement**

Append to the end of `metrics.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `venv/bin/python -m pytest -v`
Expected: `16 passed`

- [ ] **Step 5: Add the bar charts to `app.py`**

Append to the end of `app.py`:

```python

# --- Category and region breakdowns -----------------------------------------


def bar_chart(data, column, label):
    """Horizontal bar chart of sales per group, with the largest bar on top."""
    chart = px.bar(
        data,
        x="total_amount",
        y=column,
        orientation="h",
        labels={"total_amount": "Sales ($)", column: label},
        color_discrete_sequence=[ACCENT_COLOR],
    )
    chart.update_traces(hovertemplate="%{y}<br>$%{x:,.2f}<extra></extra>")
    # Plotly draws horizontal bars bottom-up; "total ascending" puts the
    # smallest at the bottom, so the largest ends up on top.
    chart.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_tickprefix="$",
        xaxis_tickformat=",",
    )
    return chart


category_column, region_column = st.columns(2)

with category_column:
    st.subheader("Sales by Category")
    st.plotly_chart(
        bar_chart(metrics.sales_by_category(df), "category", "Category"), width="stretch"
    )

with region_column:
    st.subheader("Sales by Region")
    st.plotly_chart(
        bar_chart(metrics.sales_by_region(df), "region", "Region"), width="stretch"
    )
```

- [ ] **Step 6: Check the app renders all sections**

Run:
```bash
venv/bin/python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py', default_timeout=30).run()
assert not at.exception, at.exception
print([s.value for s in at.subheader])
"
```
Expected: `['Monthly Sales Trend', 'Sales by Category', 'Sales by Region']`

- [ ] **Step 7: Commit**

```bash
git add metrics.py tests/test_metrics.py app.py
git commit -m "TASK-5: Add category and region breakdown charts with tests"
```

---

### Plan Task F — Milestone TASK-6: Verification and polish

**Files:**
- Modify: only if a check below finds a problem (`app.py` and/or `metrics.py`).

**Interfaces:**
- Consumes: the complete app from Plan Tasks A–E.
- Produces: a verified dashboard ready to merge.

- [ ] **Step 1: Run the full test suite**

Run: `venv/bin/python -m pytest -v`
Expected: `16 passed`, no warnings summary.

- [ ] **Step 2: Run the app from a different folder (Review Focus #1)**

Run:
```bash
PROJECT="$(pwd)"
(cd / && "$PROJECT/venv/bin/python" -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('$PROJECT/app.py', default_timeout=30).run()
assert not at.exception, at.exception
assert not at.error, at.error
print('Title:', at.title[0].value)
print(at.caption[0].value)
for m in at.metric: print(m.label, '=', m.value)
print([s.value for s in at.subheader])
")
```
Expected:
```
Title: ShopSmart Sales Dashboard
Sales data: Jan 2024 – Dec 2024
Total Sales = $116,500
Total Orders = 482
['Monthly Sales Trend', 'Sales by Category', 'Sales by Region']
```

- [ ] **Step 3: Start the real server and check load time and warnings**

Run:
```bash
venv/bin/streamlit run app.py --server.headless true --server.port 8501 > "$TMPDIR/streamlit-f.log" 2>&1 &
sleep 5
time curl -s http://localhost:8501/_stcore/health; echo
grep -iE "warning|deprecat|error|traceback" "$TMPDIR/streamlit-f.log" || echo "log clean"
```
Expected: `ok` in well under 5 seconds, then `log clean`. **Leave the server running** for Step 4.

- [ ] **Step 4: Your visual check (user)**

Ask the user to open http://localhost:8501 in their browser and confirm against the spec:
- Title, date-range caption, then two KPI cards: **$116,500** and **482**.
- Monthly Sales Trend line with 12 points, Jan 2024 – Dec 2024; hovering a point shows the month and an exact dollar amount.
- Category bars (left) with Electronics on top, region bars (right) with North on top; hovering shows exact dollar amounts.
- Axis titles read "Sales ($)", "Category", "Region", "Month". Nothing overlaps; the page reads as professional.
- After interacting with the page, the terminal log still has no warnings: re-run `grep -iE "warning|deprecat|error|traceback" "$TMPDIR/streamlit-f.log" || echo "log clean"`.

Fix anything the user flags (re-running Steps 1–3 after each fix), then stop the server: `pkill -f "streamlit run app.py"`.

- [ ] **Step 5: Commit**

If Step 4 led to changes:
```bash
git add app.py metrics.py tests/test_metrics.py
git commit -m "TASK-6: Polish dashboard after verification"
```
If nothing needed changing, record the verified milestone with an empty commit:
```bash
git commit --allow-empty -m "TASK-6: Verify dashboard against spec (16 tests pass, values match data)"
```
Expected: `git status --short` is empty.

**Execution stops here.** Hand off to the user for merge and Plan Task G.

---

### Plan Task G — Milestone TASK-7: Deploy to Streamlit Community Cloud (**user-owned**)

**Not executed by Claude.** This task is the hand-off. The user deploys from `main` after merging.

**Files:**
- Modify (by user): `README.md` (add the public URL)

Checklist for the user:

- [ ] **Step 1:** Merge `feature/sales-dashboard` into `main` and push `main` to GitHub.
- [ ] **Step 2:** At share.streamlit.io, create a new app: your repository, branch **`main`**, main file path **`app.py`**.
- [ ] **Step 3:** Under **Advanced settings**, choose a Python version of **3.11 or newer** (Pandas 3.0.6 requires it; pick the newest offered). Deploy.
- [ ] **Step 4:** Open the public URL and confirm the same values as Plan Task F, Step 4 ($116,500, 482, Electronics and North on top).
- [ ] **Step 5:** Add the public URL to `README.md` and commit with `TASK-7: Add deployed dashboard URL to README`.

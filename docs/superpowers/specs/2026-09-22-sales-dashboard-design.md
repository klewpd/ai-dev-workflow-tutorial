# ShopSmart Sales Dashboard — Design

**Date:** 2026-09-22
**Source:** `prd/ecommerce-analytics.md` (Phase 1 only)
**Milestones:** `TASKS.md` (TASK-1 … TASK-7)
**Branch:** `feature/sales-dashboard`

## Goal

A single-page Streamlit dashboard that shows ShopSmart's 2024 sales at a glance:
two KPI cards, a monthly sales trend, and sales broken down by category and by
region. It must be accurate (values match the CSV), readable enough for an
executive meeting, and simple enough for a learner to follow line by line.

Phase 2 features (filters, export, auth, database, drill-down) are out of scope.

## Constraints

- Work directly on `feature/sales-dashboard` (no git worktree).
- Plain Python virtual environment in `venv/` with a `requirements.txt` (no uv, no conda).
- Data calculations live in their own module, covered by pytest tests.
- Simple, readable, commented code over clever code.
- Deployment (TASK-7) is done by the user from `main` after merge; it is not part of the build.

## Known data facts

Profiled from `data/sales-data.csv`:

| Fact | Value |
|---|---|
| Rows | 482 |
| Unique `order_id` | 482 |
| Date range | 2024-01-03 to 2024-12-31 (12 months) |
| Total sales | 116,500.21 |
| Categories (high → low) | Electronics, Wearables, Audio, Smart Home, Accessories |
| Regions (high → low) | North, West, East, South |
| `quantity × unit_price == total_amount` | True for every row |

These are the reference values for the integration tests and the TASK-6 check.

## Decisions

| Question | Decision | Why |
|---|---|---|
| Trend granularity | Monthly (12 points) | Readable; matches the PRD mockup's Jan/Feb/Mar axis |
| Total Orders | `order_id.nunique()` | Counts orders, not rows; stays correct if a multi-item order appears |
| Dependency versions | Pinned exactly (`==`) | Streamlit Cloud installs what was tested locally |
| Module split | `metrics.py` + `app.py` | Calculations testable without Streamlit; one page file to read |
| Bar orientation | Horizontal, largest on top | Matches the PRD mockup; long category names fit |
| Theme | Streamlit default + one accent color | Professional with no custom CSS to maintain |

## Architecture

```
ai-dev-workflow-tutorial/
├── app.py              # Streamlit page: layout, KPI cards, Plotly charts
├── metrics.py          # Pure Pandas functions: load + calculations
├── tests/
│   └── test_metrics.py # pytest tests for every function in metrics.py
├── requirements.txt    # Pinned: streamlit, pandas, plotly, pytest
├── data/sales-data.csv # Existing, unchanged
└── venv/               # Local only; already in .gitignore
```

**Data flow (one direction):**
`data/sales-data.csv` → `metrics.load_sales_data()` → DataFrame →
`metrics` calculation functions → numbers / small DataFrames →
`app.py` formats them and renders `st.metric` cards and Plotly charts.

`metrics.py` never imports Streamlit or Plotly. `app.py` never does arithmetic
on the data beyond formatting.

`pytest` is listed in `requirements.txt` alongside the app packages: one file
to install, and it is harmless on Streamlit Cloud.

## `metrics.py`

| Function | Returns | Behavior |
|---|---|---|
| `load_sales_data(path)` | DataFrame | `pd.read_csv(path)`, then raises `ValueError` naming any of the 8 expected columns that are missing, or if `total_amount` isn't numeric; then converts `date` with `pd.to_datetime` |
| `total_sales(df)` | float | Sum of `total_amount` |
| `total_orders(df)` | int | Number of unique `order_id` values |
| `monthly_sales(df)` | DataFrame `month`, `total_amount` | Sum per calendar month, oldest first; `month` is a timestamp (first of the month) |
| `sales_by_category(df)` | DataFrame `category`, `total_amount` | Sum per category, highest first |
| `sales_by_region(df)` | DataFrame `region`, `total_amount` | Sum per region, highest first |

Expected columns: `date, order_id, product, category, region, quantity, unit_price, total_amount`.

`sales_by_category` and `sales_by_region` both call a private helper
`_sales_by(df, column)` that groups, sums, sorts descending, and resets the index.

Functions return raw numbers. All display formatting (`$116,500`, `482`) is done in `app.py`.

## `app.py`

Top to bottom:

1. `st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")`,
   `st.title("ShopSmart Sales Dashboard")`, and a caption with the data's date
   range taken from the data (e.g. "Sales data: Jan 2024 – Dec 2024").
2. **KPI row:** two columns with `st.metric("Total Sales", f"${total:,.0f}")` and
   `st.metric("Total Orders", f"{orders:,}")`.
3. **Monthly Sales Trend:** Plotly line chart with markers; x-axis labels like
   "Jan 2024"; y-axis in dollars.
4. **Breakdowns:** two columns: "Sales by Category" (left) and "Sales by Region"
   (right), horizontal bar charts with the largest bar on top
   (`yaxis.categoryorder = "total ascending"`).

All charts:
- Rendered with `st.plotly_chart(fig, width="stretch")` (`use_container_width` is deprecated in Streamlit 1.64 and would print a warning).
- Readable axis titles (e.g. "Sales ($)", "Category"), not raw column names.
- Hover tooltips with exact values via `hovertemplate` (e.g. `$42,683.67`),
  with `<extra></extra>` to hide the trace-name box.
- One shared accent color.

**Loading:** a small `load_data()` function in `app.py`, decorated with
`@st.cache_data`, calls `metrics.load_sales_data()`. The CSV path is built from
the file's own location: `Path(__file__).parent / "data" / "sales-data.csv"`, so
the app works from any launch directory and on Streamlit Cloud.

**Errors:** if the file is missing (`FileNotFoundError`) or fails column
validation (`ValueError`), the app shows `st.error(<message>)` and calls
`st.stop()`. No stack trace is shown to the user.

## Testing

`tests/test_metrics.py`, run with `pytest` from the project root.

**Hand-made DataFrame tests** (a few rows built in the test, answers checkable by eye):
- `total_sales` sums `total_amount`.
- `total_orders` counts unique IDs (a duplicated `order_id` counts once).
- `monthly_sales` groups rows into the right months, in time order.
- `sales_by_category` / `sales_by_region` sum per group and sort highest first.
- `load_sales_data` raises `ValueError` naming a missing column (using a temporary CSV).

**Real-CSV integration tests** (against the known data facts):
- 482 rows loaded; `date` is a datetime column.
- `total_sales` ≈ 116,500.21 (`pytest.approx`).
- `total_orders` == 482.
- `monthly_sales` has 12 rows whose sum ≈ total sales.
- Category order is Electronics, Wearables, Audio, Smart Home, Accessories.
- Region order is North, West, East, South.

`app.py` is verified manually: `streamlit run app.py`, check values against the
known data facts, no errors or warnings in the terminal, loads within 5 seconds.

Calculation functions are built test-first (write the failing test, run it,
implement, run it again).

## Milestone mapping

| Milestone | Work |
|---|---|
| TASK-1 | Create `venv/`, pinned `requirements.txt`, `app.py` showing the title |
| TASK-2 | `load_sales_data` + validation (test-first), cached `load_data()` and error handling in `app.py` |
| TASK-3 | `total_sales`, `total_orders` (test-first), KPI cards |
| TASK-4 | `monthly_sales` (test-first), trend line chart |
| TASK-5 | `_sales_by`, `sales_by_category`, `sales_by_region` (test-first), bar charts |
| TASK-6 | Full test run, value check against the data facts, visual/load-time check, polish |
| TASK-7 | **User-owned:** deploy to Streamlit Community Cloud from `main` after merge |

Every commit message starts with its milestone ID (e.g. `TASK-3: Add total_sales with tests`).
Moving milestones between `TASKS.md` sections follows its Definition of Done.

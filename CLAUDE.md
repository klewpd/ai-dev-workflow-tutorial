# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A tutorial repo (see `README.md`, `pre-work-setup.md`, `workshop-build-deploy.md`) whose working project is the **ShopSmart Sales Dashboard**: a single-page Streamlit app showing 2024 KPIs, a monthly sales trend, and sales by category and region from `data/sales-data.csv`. Requirements come from `prd/ecommerce-analytics.md`; the design spec and implementation plan live in `docs/superpowers/specs/` and `docs/superpowers/plans/`. The spec is the binding authority when the plan and code disagree.

## Commands

Plain `venv/` + `requirements.txt` (exact pins: streamlit 1.64.0, pandas 3.0.6, plotly 7.1.0, pytest 9.1.1; Python 3.11+). No uv or conda. Call venv binaries by path, since shell activation doesn't persist between agent commands:

```bash
python3 -m venv venv && venv/bin/pip install -r requirements.txt   # setup
venv/bin/python -m pytest -v                                         # all tests (19)
venv/bin/python -m pytest tests/test_metrics.py::test_real_csv_totals  # one test
venv/bin/streamlit run app.py --server.headless true --server.port 8501  # run app
```

- Stop servers with `pkill -f "streamlit run app.py"`. See Lessons before starting one.
- Headless render check without a browser (a plain HTTP GET does not execute the script; it runs over the websocket):
  ```bash
  venv/bin/python -c "from streamlit.testing.v1 import AppTest; at = AppTest.from_file('app.py', default_timeout=30).run(); assert not at.exception; print([m.value for m in at.metric])"
  ```
  The "missing ScriptRunContext" line AppTest prints is harness noise, not an app warning.
- Warning check on a real server log: `grep -iE "warning|deprecat|error|traceback" <log> || echo "log clean"`. The PRD requires no warnings in the terminal.

## Architecture

Two modules with a strict split:

- **`metrics.py`**: pure Pandas. `load_sales_data(path)` validates the CSV (missing columns → `ValueError` listing them, checked *before* date parsing; non-numeric `total_amount` → `ValueError`, since summing a text column silently concatenates strings; blank values in `date`, `total_amount`, `category` or `region` → `ValueError`, since Pandas silently drops NaN/NaT from sums and groups and a blank date crashes the caption) and parses `date`. Calculation functions (`total_sales`, `total_orders`, `monthly_sales`, `sales_by_category`, `sales_by_region`) take a DataFrame and return a number or a small DataFrame. **Never imports Streamlit or Plotly.**
- **`app.py`**: loads data through an `@st.cache_data` wrapper, calls `metrics` functions, formats, and renders top to bottom. It does no arithmetic on the data beyond display formatting. It catches `(FileNotFoundError, ValueError)` and shows `st.error`; Pandas' parse errors (`DateParseError`, `EmptyDataError`, `ParserError`) are `ValueError` subclasses, so every bad-CSV case lands there instead of a traceback.

Conventions that span both files:
- CSV path is `Path(__file__).parent / "data" / "sales-data.csv"` so the app works when launched from any folder (Streamlit Cloud does this).
- Total Orders = `order_id.nunique()` (an order can span rows). Trend is monthly via `to_period("M")`, which keeps years apart.
- Display formatting only in `app.py`: `f"${value:,.0f}"` for sales, `f"{value:,}"` for orders.
- Charts: `st.plotly_chart(fig, width="stretch")`. Do **not** use `use_container_width=True` (deprecated in Streamlit 1.64; prints a warning). All charts share `ACCENT_COLOR`; bar charts are horizontal with `categoryorder="total ascending"` so the largest bar is on top.
- No custom CSS, no `.streamlit/config.toml`.

Tests (`tests/test_metrics.py`, `pytest.ini` puts the repo root on the import path) cover `metrics.py` only, in two styles: a hand-checkable 5-row `small_sales` fixture, and the real CSV via the module-scoped `real_sales` fixture checked against known values (482 rows/orders, total ≈ $116,500.21 — use `pytest.approx`, Electronics top category, North top region, 12 months).

## Workflow and git conventions

- Work is tracked as milestones `TASK-1`…`TASK-7` in `TASKS.md` (To Do → In Progress → Done). Every commit message starts with its milestone ID (`TASK-N: ...`).
- Each milestone lands as a work commit, then a separate `TASK-N: mark done on the board` commit that checks off criteria, sets `Commit:` to the work commit's hash, and adds a `Notes:` line (what Claude got wrong or the user changed, or "clean"). Only edit `TASKS.md` when the user asks.
- Feature work happens on `feature/sales-dashboard`; deployment (TASK-7, Streamlit Community Cloud from `main`) is done by the user, not Claude.

## Lessons

From the `Notes:` lines in `TASKS.md` (TASK-2, 3, 4 and 6 were clean):

- **Start Streamlit headless from an agent.** Always pass `--server.headless true`. Without it, the first run waits on Streamlit's email prompt and exits (TASK-1).
- **Confirm the port is yours before trusting a log.** Before `streamlit run`, check `lsof -iTCP:8501 -sTCP:LISTEN`. If an old server holds the port, the new one can't bind, and the log looks "clean" only because it checked nothing. Stop the old server or use another port, then re-run the check (TASK-5).

# Tasks

This file tracks all work for the ShopSmart Sales Dashboard (see `prd/ecommerce-analytics.md`). Move each milestone from To Do → In Progress → Done as you work.

## Definition of Done

A milestone moves to Done only when:

- All of its acceptance criteria are met
- The app runs locally with `streamlit run app.py` without errors
- Changes are committed with the milestone ID in the commit message (e.g., `TASK-3: Add KPI cards`)

## To Do

### TASK-3: KPI cards
Display Total Sales and Total Orders prominently at the top of the dashboard (FR-1).
- [ ] Total Sales shows as currency (`$X,XXX,XXX`), approximately $116,500
- [ ] Total Orders shows 482 with thousands separators

Commit:

### TASK-4: Sales trend chart
Add an interactive Plotly line chart of sales over time (FR-2).
- [ ] Line chart plots sales by month (or day) with labeled axes
- [ ] Hover tooltips show the exact sales value

Commit:

### TASK-5: Category and region breakdowns
Add side-by-side bar charts for sales by category and by region (FR-3, FR-4).
- [ ] Category chart shows all 5 categories, sorted highest to lowest, with Electronics on top
- [ ] Region chart shows all 4 regions, sorted highest to lowest
- [ ] Both charts have clear labels and hover tooltips with exact values

Commit:

### TASK-6: Testing and refinement
Verify accuracy, performance, and a professional appearance (NFR-1, NFR-2).
- [ ] Dashboard values match calculations done directly from the CSV
- [ ] Dashboard loads within 5 seconds with no errors or warnings in the terminal
- [ ] Layout matches the PRD mockup and is suitable for an executive presentation

Commit:

### TASK-7: Deploy to Streamlit Community Cloud
Publish the dashboard to a public, shareable URL (NFR-5).
- [ ] App is deployed to Streamlit Community Cloud from the GitHub repo
- [ ] Public URL loads the dashboard and is added to the README

Commit:

## In Progress

## Done

### TASK-1: Environment setup and project initialization
Set up the Python environment, dependencies, and a minimal Streamlit app.
- [x] `requirements.txt` lists `streamlit`, `pandas`, and `plotly`
- [x] `app.py` exists and shows a "ShopSmart Sales Dashboard" title
- [x] `streamlit run app.py` opens the app in the browser

Commit: c9174e9
Notes: Claude's first background `streamlit run` exited on Streamlit's first-run email prompt; fixed by adding `--server.headless true`. No changes by me.

### TASK-2: Data loading and basic structure
Load `data/sales-data.csv` into a Pandas DataFrame with correct column types.
- [x] CSV loads with `date` parsed as a date and `quantity`, `unit_price`, `total_amount` as numbers
- [x] All 482 records load, with the 5 categories and 4 regions present
- [x] Loading logic lives in its own function (modular, commented)

Commit: fcd63a1
Notes: clean

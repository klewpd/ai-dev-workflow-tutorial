"""ShopSmart Sales Dashboard.

Run locally with:  streamlit run app.py
"""

from pathlib import Path

import plotly.express as px
import streamlit as st

import metrics

# Build the path from this file's location so the app finds the data no
# matter which folder it is launched from (including Streamlit Cloud).
DATA_PATH = Path(__file__).parent / "data" / "sales-data.csv"

# One accent color shared by every chart, for a consistent look.
ACCENT_COLOR = "#1f77b4"


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

# --- KPI cards --------------------------------------------------------------
sales_card, orders_card = st.columns(2)
sales_card.metric("Total Sales", f"${metrics.total_sales(df):,.0f}")
orders_card.metric("Total Orders", f"{metrics.total_orders(df):,}")

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

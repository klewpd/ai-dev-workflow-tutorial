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

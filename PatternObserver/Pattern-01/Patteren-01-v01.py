import streamlit as st
import psycopg2
import pandas as pd
import numpy_financial as npf
from datetime import datetime
from pathlib import Path
import sys
from sqlalchemy import create_engine, text

# How to run this Streamlit app:

# Option-01: (common)
#   cd "PatternObserver\Pattern-01"
#   streamlit run Patteren-01-v01.py 

# Option-02: (alternative)
#   python -m streamlit run Patteren-01-v01.py


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import utilCommon as utilCommon
from PGQuery import Pattern01

Previous_Setups_query = Pattern01["Previous_Setups"]

# query = """
#     SELECT h.stock_name, h.setup_confirmed_date Date, h.setup_confirmed_price Price,
#     h.status, h.irr
#     FROM public.pattern01_header h
#     WHERE stock_name = %(stock_name)s
# """

st.set_page_config(page_title="Pattern Observer - Streamlit App", page_icon=":cat:")


@st.cache_resource
def get_db_engine():
    return utilCommon.connectPostgres()


@st.dialog("Previous Seup Details")
def show_pattern_details(data):
    # Inject CSS to control popup size
    st.markdown(
        """
        <style>
        [data-testid="stDialog"] {
            height: 90% !important;   /* increase vertical length */
            width: 80% !important;    /* optional: make it wider */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.dataframe(data, use_container_width=True, height=300)


st.title("Pattern Observer - Patteren-01 (Positive Divergence)")

# Gdrive link for setup related information
doc_url = "https://docs.google.com/document/d/127-tpmw7hLkpSyAcQXIXeAKRWnX5vKvjzwfUbYTIvhU/edit?tab=t.0#heading=h.1tn9yqpmd7bc"
st.markdown(f"Access the setup related informations directly on [Google Drive]({doc_url}).")

# Create two side-by-side columns
col1, col2 = st.columns(2)

# Column 1: Market Dropdown
with col1:
    market = st.selectbox(
        "Market",
        options=["USA", "INDIA"],
        index=None,
        placeholder="Select a market..."
    )

# Column 2: Manual Stock Name Input
with col2:
    stock_name = st.text_input(
        "Stock Name",
        value="",  # Left blank by default
        placeholder="e.g., Use the name based on Tradingview"
    )

# Example output to check user selections
if market and stock_name:
    st.write(f"Searching for **{stock_name.upper()}** in the **{market}** market.")
    try:
        engine = get_db_engine()
        # st.success("PostgreSQL connected successfully.")

        data = pd.read_sql(
        Previous_Setups_query,
        engine,
        params={"stock_name": stock_name.upper()},
        )

        if st.button("Previous setup details"):
            show_pattern_details(data)

    except Exception as error:
        st.error(f"Could not connect to PostgreSQL: {error}")
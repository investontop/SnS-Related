import os
import sys
import pandas as pd
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st

def connectPostgres():

    db_url =  "postgresql://postgres:"+os.getenv("postgrespwd")+"@localhost:5432/postgres"
    # Create SQLAlchemy engine
    if db_url:
        try:
            engine = create_engine(db_url)
            connection = engine.connect()  # Test the connection
            print("\n\nPostgres Connected successfully!")
            connection.close()  # Close the test connection
        except SQLAlchemyError as e:
            print(f"\nError: Failed to connect to Postgres. {e}")
            exit(404)
    else:
        print("\n\nError: Environment variable postgresurl not set.")

    return engine

@st.dialog("Warning!!")
def show_warning_dialog(message):
    st.warning(message)
    if st.button("Close"):
        st.rerun()  # Rerun the app to close the dialog

@st.dialog("Confirmation!!")
def show_confirmation_dialog(message):
    st.info(message)
    if st.button("Close"):
        st.rerun()  # Rerun the app to close the dialog


import yfinance as yf

def get_live_cmp(stock_name: str, market: str) -> float:
    """
    Fetches the latest Current Market Price (CMP) using yfinance.
    
    :param stock_name: Stock symbol (e.g., 'AAPL' or 'RELIANCE')
    :param market: Market name ('USA' or 'INDIA')
    :return: Current Market Price as a float, or 0.0 if failed
    """
    try:
        symbol = stock_name.strip().upper()
        
        # Format ticker for Indian stocks (defaulting to NSE)
        if market.strip().upper() == "INDIA" and not symbol.endswith((".NS", ".BO")):
            ticker_symbol = f"{symbol}.NS"
        else:
            ticker_symbol = symbol

        # Fetch ticker data
        ticker = yf.Ticker(ticker_symbol)
        
        # Try fetching real-time price from ticker fast_info or history
        price = ticker.fast_info.get("lastPrice")
        
        if price is None or price == 0.0:
            # Fallback to fetching the latest 1-day closing price
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]

        return round(float(price), 2) if price else 0.0

    except Exception as e:
        print(f"Error fetching CMP for {stock_name} ({market}): {e}")
        return 0.0


import io
import sys
import yfinance as yf


def get_live_cmp_1(stock_name: str, market: str) -> float:
    """Fetches the latest Current Market Price (CMP) using yfinance safely.

    Returns 0.0 if the ticker is invalid or unresolvable.
    """
    try:
        symbol = stock_name.strip().upper()

        # Format ticker for Indian market
        if market.strip().upper() == "INDIA" and not symbol.endswith(
            (".NS", ".BO")
        ):
            ticker_symbol = f"{symbol}.NS"
        else:
            ticker_symbol = symbol

        # Suppress yfinance stderr logging output (stops console spam for invalid tickers)
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()

        try:
            ticker = yf.Ticker(ticker_symbol)

            # 1. Try fast_info primary attribute safely
            fast_info = getattr(ticker, "fast_info", None)
            price = None

            if fast_info:
                price = fast_info.get("lastPrice")

            # 2. Fallback: Fetch latest 1-day bar
            if price is None or price == 0.0 or str(price) == "nan":
                hist = ticker.history(period="1d")
                if not hist.empty and "Close" in hist:
                    price = hist["Close"].iloc[-1]

        finally:
            # Restore standard stderr output
            sys.stderr = old_stderr

        # Check for valid numeric price
        if price is not None and not pd.isna(price) and price > 0.0:
            return round(float(price), 2)

        return 0.0

    except Exception:
        return 0.0
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
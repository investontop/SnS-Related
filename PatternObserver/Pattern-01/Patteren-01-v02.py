import streamlit as st
import psycopg2
import pandas as pd
# import numpy_financial as npf
from datetime import date, datetime
import datetime
from pathlib import Path
import sys
from sqlalchemy import create_engine, text

# How to run this Streamlit app:

# Option-01: (common)
#   cd "PatternObserver\Pattern-01"
#   streamlit run Patteren-01-v02.py 
#   streamlit run PatternObserver/Pattern-01/Patteren-01-v02.py

# Option-02: (alternative)
#   python -m streamlit run Patteren-01-v01.py


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import utilCommon as utilCommon
from PGQuery import Pattern01
Previous_Setups_query = Pattern01["Previous_Setups_query"]
New_setup_Confirmation_insert = Pattern01["New_setup_Confirmation_insert"]
Update_setup = Pattern01["Update_setup"]
Delete_selected_records = Pattern01["Delete_selected_records"]
# Search_stock_names = Pattern01["Search_stock_names"]
Get_stock_lookup = Pattern01["Get_stock_lookup"]


st.set_page_config(page_title="Pattern Observer - Streamlit App", page_icon=":cat:")
st.title("Pattern Observer - Patteren-01 (Positive Divergence)")

# Gdrive link for setup related information
doc_url = "https://docs.google.com/document/d/127-tpmw7hLkpSyAcQXIXeAKRWnX5vKvjzwfUbYTIvhU/edit?tab=t.0#heading=h.1tn9yqpmd7bc"
st.markdown(f"Access the setup related informations directly on [Google Drive]({doc_url}).")

@st.cache_resource
def get_db_engine():
    return utilCommon.connectPostgres()


@st.dialog("Previous Setup Details")
def show_pattern_details(engine, data):
    # Add a checkbox column for deletion
    data["Delete?"] = False


    # Interactive editor with checkboxes
    edited_data = st.data_editor(
        data,
        # use_container_width=True,
        height=300,
        hide_index=True,
        num_rows="fixed",
        disabled=["id", "stock_name", "status", "date", "days", "irr"],  # lock these columns
        column_config={
            "setup_breached": st.column_config.SelectboxColumn(
                "Setup Breached",
                options=["YES", "NO"],   # dropdown values
                required=True
            )
        }
    )

    # Place buttons side by side
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Delete Selected Records"):
            pattern_details_delete_selected_records(engine,edited_data)
            # st.warning("Delete functionality is not implemented yet.")

    with col2:
        if st.button("Save Changes"):
            pattern_details_save_changes(engine, data, edited_data)
            # st.warning(f"This functionality is not implemented yet. : id= {edited_data['id'].tolist()}")


def pattern_details_save_changes(engine, original_data, edited_data):
    # Find rows where setup_breached changed
    changes = edited_data[edited_data["setup_breached"] != original_data["setup_breached"]]

    if not changes.empty:
        st.success(f"Detected edits in {len(changes)} row(s).")

        try:
            with engine.begin() as conn:  # ensures commit/rollback
                for _, row in changes.iterrows():
                    st.write(f"Row id={row['id']} → setup_breached={row['setup_breached']}")
                    conn.execute(
                        text(Update_setup),
                        {"setup_breached": row["setup_breached"], "header_id": row["id"]}
                    )
            st.success("✅ Changes saved successfully!")
        except Exception as e:
            st.error(f"❌ Failed to update records: {e}")
    else:
        st.info("No changes detected.")

def pattern_details_delete_selected_records(engine, edited_data):
    # ToDo: Need to implement the deletion logic here. The function currently identifies rows marked for deletion but does not execute any database operations.
    # Filter rows where Delete? == True
    rows_to_delete = edited_data[edited_data["Delete?"] == True]

    if not rows_to_delete.empty:
        st.success(f"Deleting {len(rows_to_delete)} record(s): {rows_to_delete['id'].tolist()}")
        # Example: run DELETE SQL for each id
        for _, row in rows_to_delete.iterrows():
            st.write(f"Deleting id={row['id']}")
            # engine.execute("DELETE FROM pattern01_header WHERE id = %s", (row['id'],))
            st.warning(f"This functionality is not implemented yet.")
    else:
        st.info("No rows selected for deletion.")


def insert_setup_header(engine, market, stock_name, setup_date, conf_price, setup_breached):
    try:
        insert_query = text(New_setup_Confirmation_insert)  # Use the query from PGQuery.py

        with engine.begin() as conn:  # Context manager handles commit/rollback automatically
            result = conn.execute(
                insert_query,
                {
                    "market": market,
                    "stock_name": stock_name,
                    "setup_date": setup_date,
                    "conf_price": conf_price,
                    "setup_breached": str(setup_breached).upper()
                },
            )
            new_id = result.scalar()  # Fetches the returned header_id

        return new_id

    except Exception as e:
        st.error(f"Error inserting record: {e}")
        return None

# =============================================================================
# SECTION: Previous Setup Details
# =============================================================================
# Create two side-by-side columns
col1, col2 = st.columns(2)
options = ["USA", "INDIA"]

# Column 1: Market Dropdown
with col1:
    market = st.selectbox(
        "Market",
        options=options,
        index=None,
        placeholder="Select a market..."
    )

# Column 2: Manual Stock Name Input
with col2:
    stock_name = st.text_input(
        "Stock Name",
        value="",  # Left blank by default
        placeholder="e.g., Use the name based on Tradingview"
    ).upper()


# "Previous setup details" Button is always visible
if st.button("Previous setup details"):
    if market:  # only require market, stock_name can be empty
        st.write(f"Searching in the **{market}** market"
                 + (f" for **{stock_name}**" if stock_name else ""))

        try:
            engine = get_db_engine()
            data = pd.read_sql(
                Previous_Setups_query,
                engine,
                params={"stock_name": stock_name.upper() if stock_name else "", "market": market}

            )
            show_pattern_details(engine, data)
        except Exception as error:
            st.error(f"Could not connect to PostgreSQL: {error}")
    else:
        st.warning("Please select a market before fetching details.")

# =============================================================================
# SECTION: Setup confirmation
# =============================================================================
with st.expander("➕ **Setup Confirmation**", expanded=False):
    with st.form(key="pattern_confirmation_form"):
        # =============================================================================
        # Setup Confirmation Details
        # =============================================================================
        st.subheader("1. Setup Confirmation Details")
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        
        with col_m1:
            form_market = st.selectbox("Market", options=options, index=options.index(market) if market in options else 1)
        with col_m2:
            form_stock = st.text_input("Stock Name", placeholder="e.g., AAPL, RELIANCE").upper()
        with col_m3:
            # setup_date = st.date_input("Setup Date", value=datetime.datetime.today(),min_value=datetime.date(2000, 1, 1), max_value=datetime.date(2100, 12, 31))
            setup_date = st.date_input("Setup Date",value=datetime.datetime.today(), min_value=date(2000, 1, 1), max_value=date(2100, 12, 31)
)
        with col_m4:
            conf_price = st.number_input("Confirmation Price", min_value=0.0, value=0.0, step=0.01)
        with col_m5:
            setup_breached = st.selectbox("Setup Breached?", options=["NO", "YES"], index=0)

        # Form submission button
        setup_confirmation_submit_btn = st.form_submit_button("Save Setup Details")

        st.divider()

    if setup_confirmation_submit_btn:
        if not form_stock:
            # st.error("Please enter a valid Stock Name before saving!")
            message = "Please enter a valid Stock Name before saving!"
            # show_warning_dialog(message)
            utilCommon.show_warning_dialog(message)
        elif conf_price <= 0.0:
            # st.error("Please enter a valid Confirmation Price greater than 0!")
            message = "Please enter a valid Confirmation Price greater than 0!"
            # show_warning_dialog(message)
            utilCommon.show_warning_dialog(message)
        else:
            try:
                engine = get_db_engine()
                # Execute database insertion via external function
                new_id = insert_setup_header(
                    engine, form_market, form_stock, setup_date, conf_price, setup_breached
                )
                # st.success(f"Setup successfully saved for **{form_stock}** with Record ID: **{new_id}**!")
                message = f"Setup for **{form_stock}** has been saved. Please ensure to add the entry and exit legs in the next steps."
                # show_confirmation_dialog(message)
                utilCommon.show_confirmation_dialog(message)
            except Exception as error:
                st.error(f"Failed to insert record into PostgreSQL: {error}")
# =============================================================================
# SECTION: Setup Entry
# =============================================================================
with st.expander("➕ **New Entry**", expanded=False):
    with st.form(key="pattern_entry_form"):
        # =============================================================================
        # New entry legs (BUY)
        # =============================================================================
        st.subheader("2. Entry Legs (BUY)")

        form_market = st.selectbox("Market", options=options, index=options.index(market) if market in options else 1)

        # First row: Stock Lookup
        col_lookup = st.columns(1)[0]
        with col_lookup:
            stock_lookup = st.text_input("Stock Lookup", placeholder="e.g., AAPL, RELIANCE").upper()
            search_clicked = st.form_submit_button("Search Stock")

            selected_stock = None
            if search_clicked and stock_lookup:
                try:
                    engine = get_db_engine()
                    search_pattern = f"%{stock_lookup}%"
                    search_results = pd.read_sql(
                    Get_stock_lookup,
                    engine,
                    params={"stock_name_pattern": search_pattern, "market": form_market}
                    )

                    if not search_results.empty:
                        selected_stock = st.selectbox(
                            "Matching Stocks:",
                            search_results["stock_name"].tolist(),
                            index=search_results["stock_name"].tolist().index(
                            st.session_state.get("buy_stock", search_results["stock_name"].tolist()[0])
                            )
                        )
                        st.session_state["buy_stock"] = selected_stock
                    else:
                        st.info("No matching stocks found.")

                except Exception as e:
                    st.error(f"Error occurred while searching: {e}")
            else:
                # 🔑 keep showing the previously selected stock
                if "buy_stock" in st.session_state and st.session_state["buy_stock"]:
                    st.selectbox("Matching Stocks:", [st.session_state["buy_stock"]], index=0)

        # Use selected stock if available
        buy_stock = st.session_state.get("buy_stock", "")

        # Second row: Buy Date, Qty, Price
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            buy_date = st.date_input(
                "Buy Date",
                value=datetime.datetime.today(),
                min_value=date(2000, 1, 1),
                max_value=date(2100, 12, 31)
            )
        with col_b2:
            buy_qty = st.number_input("Buy Qty", min_value=0, value=0, step=1)
        with col_b3:
            buy_price = st.number_input("Buy Price", min_value=0.0, value=0.0, step=0.01)

        # 🔑 Buy button + insert logic
        buy_clicked = st.form_submit_button("Buy")
        if buy_clicked and buy_stock and buy_qty > 0 and buy_price > 0.0:
            try:
                # engine = get_db_engine()
                # with engine.begin() as conn:
                #     result = conn.execute(
                #         text(Pattern01["New_setup_Confirmation_insert"]),
                #         {
                #             "market": form_market,
                #             "stock_name": buy_stock,
                #             "setup_date": buy_date,
                #             "conf_price": buy_price,
                #             "setup_breached": "NO"
                #         }
                #     )
                #     new_id = result.scalar()  # header_id returned
                # st.success(f"Buy entry inserted successfully! Header ID: {new_id}")
                message = "This functionality is not implemented yet. The buy entry will be saved in the next version."
                utilCommon.show_warning_dialog(message)
            except Exception as e:
                st.error(f"Error occurred while inserting buy entry: {e}")

        else:
            if buy_clicked:
                message = "Please ensure you have selected a stock and entered valid quantity and price before buying."
                utilCommon.show_warning_dialog(message)

        st.divider()

# =============================================================================
# SECTION: Setup Exit
# =============================================================================
with st.expander("➕ **Exit**", expanded=False):
    with st.form(key="pattern_exit_form"):

        st.subheader("3. Profit Booking / Exit Legs (SELL)")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            book1_qty = st.number_input("Booking-1 Qty", min_value=0, value=0, step=1)
            book1_price = st.number_input("Booking-1 Price", min_value=0.0, value=0.0, step=0.01)
        with col_s2:
            book2_qty = st.number_input("Booking-2 Qty", min_value=0, value=0, step=1)
            book2_price = st.number_input("Booking-2 Price", min_value=0.0, value=0.0, step=0.01)
        with col_s3:
            book3_qty = st.number_input("Booking-3 Qty", min_value=0, value=0, step=1)
            book3_price = st.number_input("Booking-3 Price", min_value=0.0, value=0.0, step=0.01)

        st.divider()
        form_submitted = st.form_submit_button("Preview New Entry")

    if form_submitted:
        if not form_stock:
            message = "Please provide a valid Stock Name before submitting!"
            # show_warning_dialog(message)
            utilCommon.show_warning_dialog(message)
        else:
            st.success(f"Entry preview generated for **{form_stock}** ({form_market})!")
            
            preview_summary = {
                "Market": form_market,
                "Stock": form_stock,
                "Setup Date": str(setup_date),
                "Confirmation Price": conf_price,
                "Setup Breached": setup_breached
            }
            
            preview_legs = [
                {"Leg": "Initial Entry", "Action": "BUY", "Qty": init_qty, "Price": init_price},
                {"Leg": "Add-1 Entry", "Action": "BUY", "Qty": add1_qty, "Price": add1_price},
                {"Leg": "Add-2 Entry", "Action": "BUY", "Qty": add2_qty, "Price": add2_price},
                {"Leg": "Add-3 Entry", "Action": "BUY", "Qty": add3_qty, "Price": add3_price},
                {"Leg": "Booking-1 Exit", "Action": "SELL", "Qty": book1_qty, "Price": book1_price},
                {"Leg": "Booking-2 Exit", "Action": "SELL", "Qty": book2_qty, "Price": book2_price},
                {"Leg": "Booking-3 Exit", "Action": "SELL", "Qty": book3_qty, "Price": book3_price},
            ]
            
            st.write("**Header Setup Summary:**", preview_summary)
            st.write("**Executions Detailed View:**")
            st.dataframe(pd.DataFrame(preview_legs), use_container_width=True)

st.divider()
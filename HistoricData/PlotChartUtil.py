import os
import sys

import pandas as pd
import requests


def hdfcScripts(script):
    # Example dictionary mapping long names to short names
    script_name_map = {
        "ACTION CONSTRUCTION EQUIPMENT LIMITED": "ACE",
        "ANTONY WASTE HANDLING CELL LTD": "AWHCL",
        "AVENUE SUPERMARTS (DMART) LIMITED": "DMART",
        "BAJAJ FINANCE LIMITED": "BAJAJFINANCE",
        "BALRAMPUR CHINI MILLS LTD": "BALRAMPUR",
        "BHAGERIA INDUSTRIES LIMITED": "BHAGERIA",
        "CENTRAL DEPOSITORY SERVICES (INDIA) LTD": "CDSL",
        "COAL INDIA LIMITED": "COALINDIA",
        "COMPUTER AGE MANAGEMENT SERVICES LTD": "CAMS",
        "GLOBAL EDUCATION LIMITED": "GLOBALEDU",
        "HDFC BANK LTD": "HDFCBANK",
        "HINDALCO INDUSTRIES LTD": "HINDALCO",
        "HINDUSTAN UNILEVER LTD": "HUL",
        "INDIAN ENERGY EXCHANGE LIMITD": "IEX",
        "INDIAN RAILWAY CATERING & TOURISM CO LTD": "IRCTC",
        "INDIAN RAILWAY FINANCE CORP LTD": "IRFC",
        "INDRAPRASTHA GAS LTD": "IGL",
        "INDUSIND BANK LIMITED": "INDUSINDBANK",
        "ITC LTD": "ITC",
        "KALYAN JEWELLERS INDIA LIMITED": "KALYAN",
        "KNR Constructions Limited": "KNRCON",
        "KOTAK MAHINDRA BANK LTD": "KOTAKMAH",
        "KPIT TECHNOLOGIES LIMITED": "KPIT",
        "LARSEN & TOUBRO LTD": "LT",
        "LAURUS LABS LIMITED": "LAURUSLAB",
        "MAHANAGAR GAS LIMITED": "MGL",
        "MANAPPURAM FINANCE LIMITED": "MANAPPURAM",
        "NIPPON INDIA ETF GOLD BEES": "GOLDBEES",
        "Nippon India ETF Nifty IT": "ITBEES",
        "NIPPON INDIA ETF NIFTY 50 BEES": "NIFTYBEES",
        "NIPPON INDIA NIFTY PHARMA ETF - GROWTH P": "PHARMABEES",
        "NMDC LIMITED": "NMDC",
        "NTPC GREEN ENERGY LIMITED": "NTPCGREEN",
        "OIL INDIA LIMITED": "OIL",
        "POWER GRID INFRASTRUCTURE INV TRUST": "PGINVIT",
        "PRIMO CHEMICALS LIMITED": "PRIMO",
        "RELIANCE INDUSTRIES LTD": "RELIANCE",
        "RELIANCE COMMUNICATION LTD": "RELCOM",
        "SBI CARDS AND PAYMENT SERVICES LTD": "SBICARDS",
        "SHANKARA BUILDING PRODUCTS LIMITED": "SHANKARABUILD",
        "STATE BANK OF INDIA": "SBI",
        "TATA POWER CO LTD": "TATAPOWER",
        "TECH MAHINDRA LIMITED": "TECHM",
        "VOLTAS LTD": "VOLTAS"

        # Add more mappings as needed
    }

    return(script.map(script_name_map).fillna(script))  # Map names, fallback to original

def FormatTradeDetails(platform, trade_details, trade_details_source, demat):
    # Note: This is used in PlotChart-x.py & CalculateAvgPrice.py

    df_list = []  # List to store individual dataframes

    for dirname, _, filenames in os.walk(trade_details_source):
        source_files = [f for f in filenames if f.startswith("TRADE") and f.endswith(".csv")]

    for f in source_files:
        df = pd.read_csv(os.path.join(trade_details_source, f))
        df_list.append(df)  # Append to the list

    if df_list:  # Check if df_list is not empty
        final_df = pd.concat(df_list, ignore_index=True)
    else:
        final_df = pd.DataFrame()  # Create an empty DataFrame


    if platform == 'KITE':

        # """Create separate files from the Yearly consolidated trade details."""
        # for dirname, _, filenames in os.walk(trade_details_source):
        #     source_files = [f for f in filenames if f.startswith("TRADE")]
        #
        # for f in source_files:
        #     df = pd.read_csv(os.path.join(trade_details_source, f))
        #     df_list.append(df)  # Append to the list
        #
        # if df_list:  # Check if df_list is not empty
        #     final_df = pd.concat(df_list, ignore_index=True)
        # else:
        #     final_df = pd.DataFrame()  # Create an empty DataFrame

        if not final_df.empty:

            file_path = os.path.join(trade_details_source, f"00-TRADE-{demat}.csv")  # This file name is used in CalculateAvgPrice.py
            final_df.to_csv(file_path, index=False)

            # Normalize the 'symbol' column by removing anything after '-'. This is used for example PGINVIT-IF & PGINVIT-IV will be changed to PGINVIT
            final_df["symbol"] = final_df["symbol"].str.split('-').str[0]
            # Group by 'symbol' and save each group to a separate file
            for symbol, group in final_df.groupby("symbol"):
                file_path = os.path.join(trade_details, f"{symbol}.csv")
                group.to_csv(file_path, index=False)

    elif platform == 'HSEC':

        if not final_df.empty:

            # Find the index of 'ScriptName'
            script_name_index = final_df.columns.get_loc('ScriptName')

            # Insert the new column right after 'ScriptName'
            final_df.insert(script_name_index + 1, 'Script', hdfcScripts(final_df["ScriptName"]))  # Example logic

            file_path = os.path.join(trade_details_source, f"00-TRADE-{demat}.csv")
            try:
                final_df.to_csv(file_path, index=False)
            except PermissionError:
                print(f"Error: The file '{file_path}' is open. Please close it and try again.")
                sys.exit("File cannot access")


            # Example dictionary mapping long names to short names
            # script_name_map = {
            #     "ACTION CONSTRUCTION EQUIPMENT LIMITED": "ACE",
            #     "ANTONY WASTE HANDLING CELL LTD": "AWHCL",
            #     "AVENUE SUPERMARTS (DMART) LIMITED": "DMART",
            #     "BAJAJ FINANCE LIMITED": "BAJAJFINANCE",
            #     "BALRAMPUR CHINI MILLS LTD": "BALRAMPUR",
            #     "CENTRAL DEPOSITORY SERVICES (INDIA) LTD": "CDSL",
            #     "COAL INDIA LIMITED": "COALINDIA",
            #     "COMPUTER AGE MANAGEMENT SERVICES LTD": "CAMS",
            #     "GLOBAL EDUCATION LIMITED": "GLOBALEDU",
            #     "HDFC BANK LTD": "HDFCBANK",
            #     "HINDALCO INDUSTRIES LTD":"HINDALCO",
            #     "HINDUSTAN UNILEVER LTD": "HUL",
            #     "INDIAN ENERGY EXCHANGE LIMITD": "IEX",
            #     "INDIAN RAILWAY CATERING & TOURISM CO LTD": "IRCTC",
            #     "INDIAN RAILWAY FINANCE CORP LTD": "IRFC",
            #     "INDRAPRASTHA GAS LTD": "IGL",
            #     "INDUSIND BANK LIMITED": "INDUSINDBANK",
            #     "ITC LTD": "ITC",
            #     "KALYAN JEWELLERS INDIA LIMITED":"KALYAN",
            #     "KNR Constructions Limited": "KNRCON",
            #     "KOTAK MAHINDRA BANK LTD": "KOTAKMAH",
            #     "KPIT TECHNOLOGIES LIMITED": "KPIT",
            #     "LARSEN & TOUBRO LTD": "LT",
            #     "LAURUS LABS LIMITED": "LAURUSLAB",
            #     "MAHANAGAR GAS LIMITED": "MGL",
            #     "MANAPPURAM FINANCE LIMITED": "MANAPPURAM",
            #     "NIPPON INDIA ETF GOLD BEES": "GOLDBEES",
            #     "Nippon India ETF Nifty IT": "ITBEES",
            #     "NIPPON INDIA ETF NIFTY 50 BEES": "NIFTYBEES",
            #     "NIPPON INDIA NIFTY PHARMA ETF - GROWTH P":"PHARMABEES",
            #     "NMDC LIMITED":"NMDC",
            #     "NTPC GREEN ENERGY LIMITED": "NTPCGREEN",
            #     "OIL INDIA LIMITED": "OIL",
            #     "POWER GRID INFRASTRUCTURE INV TRUST": "PGINVIT",
            #     "PRIMO CHEMICALS LIMITED":"PRIMO",
            #     "RELIANCE INDUSTRIES LTD": "RELIANCE",
            #     "SBI CARDS AND PAYMENT SERVICES LTD": "SBICARDS",
            #     "SHANKARA BUILDING PRODUCTS LIMITED": "SHANKARABUILD",
            #     "STATE BANK OF INDIA": "SBI",
            #     "TATA POWER CO LTD": "TATAPOWER",
            #     "TECH MAHINDRA LIMITED": "TECHM",
            #     "VOLTAS LTD": "VOLTAS"
            #
            #     # Add more mappings as needed
            # }

            finalFormatted_df = final_df.assign(
                TRANSACTION_TYPE = 'TRADE',
                # DATE=final_df.get("trDate"),
                DATE = pd.to_datetime(final_df.get("trDate"), format="%d-%b-%y").dt.strftime("%d-%b-%Y"),
                EXCHANGE_CORPORATE_ACTION=final_df.get("Exch"),
                # ACTION=final_df.get("Action"),
                ACTION=final_df.get("Action").map({"B": "Buy", "S": "Sell"}),
                PRODUCT_TYPE = 'CASH',
                QTY = final_df.get("Qty"),
                TRANSACTION_PRICE = final_df.get("MktPrice"), # abs(final_df.get("NetAmt")) / final_df.get("Qty"),
                VALUE_AT_COST = abs(final_df.get("NetAmt")) / final_df.get("Qty") * final_df.get("Qty"),
                REMARKS = '',
                STT = final_df.get("STT"),
                ADDITIONAL_CHARGES = final_df.get("Brokarage")+final_df.get("StampDuty")+final_df.get("TransactionChrg")+final_df.get("SebiTurnoverTax")+final_df.get("HighEduCess"),
                # SCRIPT=final_df["ScriptName"].map(script_name_map).fillna(final_df["ScriptName"])  # Map names, fallback to original
                # SCRIPT=hdfcScripts(final_df["ScriptName"])
                SCRIPT=hdfcScripts(final_df["Script"])
            )[["TRANSACTION_TYPE","DATE", "EXCHANGE_CORPORATE_ACTION", "ACTION", "PRODUCT_TYPE", "QTY", "TRANSACTION_PRICE", "VALUE_AT_COST", "REMARKS", "STT", "ADDITIONAL_CHARGES","SCRIPT"]]

            finalFormatted_df = finalFormatted_df.rename(columns={"TRANSACTION_TYPE": "TRANSACTION TYPE", "TRANSACTION_PRICE": "TRANSACTION PRICE", "VALUE_AT_COST":"VALUE AT COST(Incl. addnl charges)", "EXCHANGE_CORPORATE_ACTION":"EXCHANGE / CORPORATE ACTION"})


            for SCRIPT, group in finalFormatted_df.groupby("SCRIPT"):
                file_path = os.path.join(trade_details, f"{SCRIPT}.csv")
                group.to_csv(file_path, index=False)

def telegramMsg(message):

    BOT_TOKEN = os.getenv("FirstTrialBotToken")  # The Bot_Token is stored in environment variables
    CHAT_ID = os.getenv("MyTeleGramChatID")  # The ChatID is stored in environment variables

    if BOT_TOKEN and CHAT_ID:
        # Telegram API URL
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        # Request parameters
        params = {
            "chat_id": CHAT_ID,
            "text": message
        }

        # Send the request
        response = requests.get(url, params=params)

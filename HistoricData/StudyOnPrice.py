import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
from datetime import datetime
from tinydb import TinyDB, Query
import json
from prettytable import PrettyTable

def get_directory():
    """Get the directories for price and trade details."""
    # base_dir = os.getcwd()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    priceDetailPath = os.path.join(base_dir, "Data", "HistoricalPrice")
    return priceDetailPath


def read_sourceFile(priceDetailPath, stkOrIndices):

    for dirname, _, files in os.walk(priceDetailPath):
        for f in files:
            if stkOrIndices in f:
                df_source = pd.read_csv(os.path.join(dirname, f))
                df_source['Date'] = pd.to_datetime(df_source['Date'], format='%d-%m-%Y')
                df_source['Year'] = df_source['Date'].dt.year
                df_source['day'] = df_source['Date'].dt.day

                # df_source['Price'] = pd.to_numeric(df_source['Price'].astype(str).str.replace(",", ""), errors='coerce')
                fields_to_convert = ['Price', 'Open', 'High', 'Low']  # remove the comma and convert intointeger for the prices
                df_source[fields_to_convert] = df_source[fields_to_convert].apply(lambda x: pd.to_numeric(x.astype(str).str.replace(",", ""), errors='coerce'))
                df_source['Change %'] = pd.to_numeric(df_source['Change %'].astype(str).str.replace("%", ""), errors='coerce')
                df_source = df_source.sort_values(by='Date')
                # df_source['Pct_Change'] = df_source['Price'].pct_change() * 100 # Calculate the percentage change over multiple days

                # Calculate the EMA
                df_source['EMA50'] = df_source['Price'].ewm(span=50, adjust=False).mean()
                df_source['EMA200'] = df_source['Price'].ewm(span=200, adjust=False).mean()

                return(df_source)

def plot_chart(df_source, stkOrIndices):

    plt.figure(figsize=(20, 14))
    plt.plot(df_source['Date'], df_source['Price'], color='b', label='Closing Price')
    plt.plot(df_source['Date'], df_source['EMA50'], label='50-Day EMA', color='orange')
    plt.plot(df_source['Date'], df_source['EMA200'], label='200-Day EMA', color='red')

    min_price = np.floor(df_source['Price'].min() / 100) * 100
    max_price = np.ceil(df_source['Price'].max() / 100) * 100
    price_range = np.linspace(min_price, max_price, num=15)
    plt.yticks(price_range)
    plt.title(f'Stock Price Over Time for {stkOrIndices}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    plt.show()

def investSameDate(df_source, stkOrIndices):
    db = TinyDB('db_SameDate.json')
    fromYear = input('        From what year we need to calculate the investment?: ')
    fromYear_int32 = np.int32(int(fromYear))
    df_sourceFromYear = df_source[df_source['Year'] >= fromYear_int32].copy()
    for date in range (1, 31):
        # Construct the column name
        column_name = 'Day' + str(date) + 'Price'
        # Ensure the column exists by initializing it to 0 if it doesn't
        if column_name not in df_sourceFromYear.columns:
            df_sourceFromYear[column_name] = 0.0

        df_sourceFromYear.loc[df_sourceFromYear['day'] == date,column_name] += df_sourceFromYear['Price']

    latestPrice = df_sourceFromYear.iloc[-1]['Price']
    print(f"\n        Calculating for stock/indices {stkOrIndices}, from year {fromYear} to {datetime.now().date()}. And latest price: {latestPrice}")

    lowestAvgPrice = 0.0
    for col in df_sourceFromYear.columns:
        if col.startswith('Day') and col.endswith('Price'):
            print(f"            Day ({col[3:-5]}) investment, totalDays: {df_sourceFromYear[df_sourceFromYear[col] != 0.0][col].count()}, "
                  f"total Cost: {round(df_sourceFromYear[df_sourceFromYear[col] != 0.0][col].sum(), 2)}, "
                  f"Avg: {round(df_sourceFromYear[df_sourceFromYear[col] != 0.0][col].mean(), 2)}, "
                  f"Current Holding: {round(latestPrice * df_sourceFromYear[df_sourceFromYear[col] != 0.0][col].count(),2)}")
            if lowestAvgPrice >= round(df_sourceFromYear[df_sourceFromYear[col] != 0.0][col].mean(), 2) or lowestAvgPrice == 0.0:
                lowestDay = col[3:-5]
                lowestAvgPrice = round(df_sourceFromYear[df_sourceFromYear[col] != 0.0][col].mean(), 2)

    print(f"\n       LowestDayAvg: {lowestDay}")


    # TinyDB
    User = Query()
    db.remove((User.stkOrIndices == stkOrIndices) & (User.FromYear == fromYear))
    db.insert({'stkOrIndices': stkOrIndices, 'FromYear': fromYear, 'ToDate':datetime.now().date().isoformat(), 'LowestDayAvg': lowestDay, 'LowestAvgPrice': lowestAvgPrice})

    # # DisplayStyle1: Retrive data from TinyDB
    # print("\nDisplayStyle1: as JSON")
    # results = db.search(User.stkOrIndices == stkOrIndices)
    # print(json.dumps(results, indent=4))
    #
    # # DisplayStyle2: Retrive data from TinyDB - Display in a different way
    # print("\nDisplayStyle2: as formatted JSON")
    # results = db.search(User.stkOrIndices == stkOrIndices)
    # for record in results:
    #     for key, value in record.items():
    #         print(f"  {key}: {value}")
    #     print("-" * 40)

    # DisplayStyle3: Retrive data from TinyDB - Display in a different way of PrettyTable
    print("\nDisplayStyle3: as formatted table from tinyDB")
    table = PrettyTable()
    results = db.search(User.stkOrIndices == stkOrIndices)

    if results:
        table.field_names = results[0].keys()
    for record in results:
        table.add_row(record.values())
    print(table)





def main():
    # stkOrIndices = 'NIFTY'
    # print("\nLet us try to study on the price movement")
    stkOrIndices = input(f"\n        Enter stockname / nifty to study: ").upper().strip()

    priceDetailPath = get_directory()

    print(
        f"\n        Folder used for Historic Price: {priceDetailPath}\n")
    
    df_source = read_sourceFile(priceDetailPath, stkOrIndices)

    # plot_chart(df_source, stkOrIndices)
    investSameDate(df_source, stkOrIndices)

if __name__ == "__main__":
    main()

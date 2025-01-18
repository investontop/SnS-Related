# PlotChart
# And more standard formatted - to use main, function etc

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import mplcursors


def get_directories(demat):
    """Get the directories for price and trade details."""
    base_dir = os.getcwd()
    price_details = os.path.join(base_dir, "Data", "PriceDetails")
    trade_details = os.path.join(base_dir, "Data", "TradeDetails", demat)

    if os.path.exists(trade_details):
        return price_details, trade_details
    else:
        print("\n     <<<<<Warning>>>>> Please enter the right demat")
        sys.exit("     Exiting program due to missing trade details directory.")




def read_price_data(price_details, stock_name):
    """Read the price data for a given stock."""
    for dirname, _, filenames in os.walk(price_details):
        for f in filenames:
            if stock_name in f:
                df_price = pd.read_csv(os.path.join(dirname, f))
                df_price['Date'] = pd.to_datetime(df_price['Date'], format='%d-%m-%Y')
                return df_price, f
    return pd.DataFrame(), ""


def read_trade_data(trade_details, stock_name, demat):
    """Read the trade data for a given stock."""
    df_trade = pd.DataFrame()
    for dirname, _, filenames in os.walk(trade_details):
        for f in filenames:
            if f.startswith(stock_name):
                df_temp = pd.read_csv(os.path.join(dirname, f))
                df_trade = pd.concat([df_trade, df_temp], ignore_index=True)

    if demat == 'HSEC':
        df_trade['DATE'] = pd.to_datetime(df_trade['DATE'], format='%d-%b-%Y')
    elif demat == 'ZX4974':
        df_trade['trade_date'] = pd.to_datetime(df_trade['trade_date'], format='%Y-%m-%d')
    return df_trade


def plot_data_hsec(df_price, df_trade, stock_name):
    """Plot the price and trade data."""
    df_buy = df_trade[(df_trade['TRANSACTION TYPE'] == 'TRADE') & (df_trade['ACTION'] == 'Buy')]
    df_sell = df_trade[(df_trade['TRANSACTION TYPE'] == 'TRADE') & (df_trade['ACTION'] == 'Sell')]

    plt.figure(figsize=(12, 7))
    plt.plot(df_price['Date'], df_price['Price'], color='b', label='Price')

    min_price = np.floor(df_price['Price'].min() / 10) * 10
    max_price = np.ceil(df_price['Price'].max() / 10) * 10
    price_range = np.linspace(min_price, max_price, num=15)
    plt.yticks(price_range)

    plt.title(f'Stock Price Over Time for {stock_name}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    plt.scatter(df_buy['DATE'], df_buy['TRANSACTION PRICE'], color='g', marker='o', label='Buy Prices')
    plt.scatter(df_sell['DATE'], df_sell['TRANSACTION PRICE'], color='r', marker='o', label='Sell Prices')

    plt.legend()

    total_buy_price, total_buy_qty, total_sell_price, total_sell_qty, total_dividend = calculate_totals(df_trade)
    text = f"Stock Analysis:\nTotal Bought: {total_buy_qty} qty | {total_buy_price} INR\nTotal Sold: {total_sell_qty} qty | {total_sell_price} INR\nTotal Dividend: {total_dividend} INR"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(0.02, 0.95, text, transform=plt.gca().transAxes, fontsize=10,
             verticalalignment='top', bbox=props)

    plt.show()

def plot_data_kite(df_price, df_trade, stock_name):
    """Plot the price and trade data."""
    df_buy = df_trade[(df_trade['trade_type'] == 'buy')]
    df_sell = df_trade[(df_trade['trade_type'] == 'sell')]

    print(df_buy)

def calculate_totals(df_trade):
    """Calculate total buy, sell, and dividend values."""
    total_buy_price = df_trade.loc[(df_trade['ACTION'] == 'Buy') & (
                df_trade['TRANSACTION TYPE'] == 'TRADE'), 'VALUE AT COST(Incl. addnl charges)'].sum()
    total_buy_qty = df_trade.loc[(df_trade['ACTION'] == 'Buy') & (df_trade['TRANSACTION TYPE'] == 'TRADE'), 'QTY'].sum()
    total_sell_price = df_trade.loc[df_trade['ACTION'] == 'Sell', 'VALUE AT COST(Incl. addnl charges)'].sum()
    total_sell_qty = df_trade.loc[df_trade['ACTION'] == 'Sell', 'QTY'].sum()
    total_dividend = df_trade.loc[(df_trade['EXCHANGE / CORPORATE ACTION'] == 'DIV') & (
                df_trade['TRANSACTION TYPE'] == 'CORPORATE ACTION'), 'VALUE AT COST(Incl. addnl charges)'].sum()
    return total_buy_price, total_buy_qty, total_sell_price, total_sell_qty, total_dividend


def main():
    print("\nUse this module to plot the Stock Price and Trade details\n")
    demat = input('     Which account are we working on? (HSEC / ZX4974): ').upper().strip()
    price_details, trade_details = get_directories(demat)

    print(
        f"\n     Folders used for Historic Price and Trade details:\n         PriceDetails: {price_details}\n         TradePrice: {trade_details}\n")

    stock_name = input('    What stock to plot: ').upper().replace(" ", "")
    df_price, price_file = read_price_data(price_details, stock_name)
    df_trade = read_trade_data(trade_details, stock_name, demat)
    # df_trade = df_trade.drop_duplicates(subset='trade_id')  # This will be used only for zerodha trade files, HSEC trade files doesnot have trade_id

    if demat == 'HSEC':
        plot_data_hsec(df_price, df_trade, stock_name)

        total_buy_price, total_buy_qty, total_sell_price, total_sell_qty, total_dividend = calculate_totals(df_trade)
        print(
            f"Total Bought: {total_buy_qty} qty | {total_buy_price} INR\nTotal Sold: {total_sell_qty} qty | {total_sell_price} INR\nTotal Dividend: {total_dividend} INR")


    elif demat == 'ZX4974':
        df_trade = df_trade.drop_duplicates(subset='trade_id')

        plot_data_kite(df_price, df_trade, stock_name)


    print("Completed")

if __name__ == "__main__":
    main()

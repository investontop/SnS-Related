# PlotChart
# And more standard formatted - to use main, function etc

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys


def get_directories(demat):
    """Get the directories for price and trade details."""
    # base_dir = os.getcwd()
    base_dir = os.path.dirname(os.path.abspath(__file__))
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
    elif demat == 'ZX4974' or demat == 'YY8886':
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

# Function to calculate weighted average price
def weighted_avg_price(x):
    return (x['quantity'] * x['price']).sum() / x['quantity'].sum()


def group_by_date(df):
    # Group by 'symbol' and 'trade_date', sum 'quantity', and calculate weighted average 'price'
    df_temp = df.groupby(['symbol', 'trade_date']).agg(
        quantity = ('quantity', 'sum'),
        price=('quantity', 'sum')
    ).reset_index()

    df_temp['price'] = df.groupby(['symbol', 'trade_date'], group_keys=False).apply(weighted_avg_price).values

    df_temp['totalPrice'] = df_temp['quantity'] * df_temp['price']

    return df_temp

def group_by_date_mean(df):
    # Group by 'symbol' and 'trade_date', sum 'quantity', and calculate weighted average 'price'
    df_temp = df.groupby(['symbol', 'trade_date']).agg(
        quantity = ('quantity', 'sum'),
        price=('price', 'mean')
    ).reset_index()

    df_temp['totalPrice'] = df_temp['quantity'] * df_temp['price']

    return df_temp

def plot_data_kite(df_price, df_trade, stock_name):
    """Plot the price and trade data."""
    df_buy = df_trade[(df_trade['trade_type'] == 'buy')]
    df_sell = df_trade[(df_trade['trade_type'] == 'sell')]

    # df_buy_group = group_by_date(df_buy)
    # df_sell_group = group_by_date(df_sell)
    df_buy_group = group_by_date_mean(df_buy)
    df_sell_group = group_by_date_mean(df_sell)


    # Ensure that 'Price' column in df_price is numeric
    df_price['Price'] = df_price['Price'].astype(str)
    df_price['Price'] = pd.to_numeric(df_price['Price'].str.replace(",", ""), errors='coerce')

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

    plt.scatter(df_buy_group['trade_date'], df_buy_group['price'], color='g', marker='o', s=100, label='Buy Prices')
    plt.scatter(df_sell_group['trade_date'], df_sell_group['price'], color='r', marker='o', s=100, label='Sell Prices')

    plt.legend()

    # Annotate each dot with the corresponding quantity
    for i, row in df_buy_group.iterrows():
        plt.text(row['trade_date'], row['price'], f"{int(row['quantity'])}", color='g', fontsize=9, ha='right', va='bottom', rotation=45)

    for i, row in df_sell_group.iterrows():
        plt.text(row['trade_date'], row['price'], f"{int(row['quantity'])}", color='r', fontsize=9, ha='right', va='top', rotation=45)


    # First buy date for drawing lines
    first_buy_date = df_buy_group['trade_date'].iloc[0]
    first_buy_price = df_buy_group['price'].iloc[0]


    # Plot the first vertical line at the first buy date
    plt.axvline(x=first_buy_date, color='g', linestyle='--', label='First Buy')


    # Plot the second vertical line exactly 1 year after the first buy date
    year_later = first_buy_date + pd.DateOffset(years=1)
    plt.axvline(x=year_later, color='r', linestyle='--', label='1 Year Later')

    plt.show()


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
    demat = input('     Which account are we working on? (HSEC / ZX4974 / YY8886): ').upper().strip()
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


    elif demat == 'ZX4974' or demat == 'YY8886':
        df_trade = df_trade.drop_duplicates(subset='trade_id')

        plot_data_kite(df_price, df_trade, stock_name)


    print("Completed")

if __name__ == "__main__":
    main()

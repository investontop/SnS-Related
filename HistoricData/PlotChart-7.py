# PlotChart
# PlotChart-5.py + Converting the price from str to int in the fun read_price_data
#                + included LongTerm & ShortTermQty in the fun plot_data_hsec

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from datetime import datetime
import numpy_financial as npf
import StockAPI



def get_directories(demat):
    """Get the directories for price and trade details."""
    # base_dir = os.getcwd()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    price_details = os.path.join(base_dir, "Datas", "PriceDetails")
    trade_details = os.path.join(base_dir, "Datas", "TradeDetails", demat)

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
                # df_price['Price'] = pd.to_numeric(df_price['Price'], errors='coerce')
                df_price['Price'] = df_price['Price'].astype(str)
                df_price['Price'] = pd.to_numeric(df_price['Price'].str.replace(",", ""), errors='coerce')
                return df_price, f
    return pd.DataFrame(), ""


def read_trade_data(trade_details, stock_name, platform):
    """Read the trade data for a given stock."""
    df_trade = pd.DataFrame()
    for dirname, _, filenames in os.walk(trade_details):
        for f in filenames:
            if f.startswith(stock_name):
                df_temp = pd.read_csv(os.path.join(dirname, f))
                df_trade = pd.concat([df_trade, df_temp], ignore_index=True)

    #to calculate the todalDays
    current_date = datetime.now()

    if platform == 'HSEC':

        # dateformats = ['%d-%b-%y', '%d-%b-%Y']
        # for fmt in dateformats:
        #     try:
        #         df_trade['DATE'] = pd.to_datetime(df_trade['DATE'], format=fmt, errors='coerce')
        #     except ValueError:
        #         continue

        df_trade['DATE'] = pd.to_datetime(df_trade['DATE'], format='%d-%b-%Y')
        df_trade['totalDays'] = (current_date - df_trade['DATE']).dt.days
    elif platform == 'KITE':
        df_trade['trade_date'] = pd.to_datetime(df_trade['trade_date'], format='%Y-%m-%d')
        df_trade['totalDays'] = (current_date - df_trade['trade_date']).dt.days
    return df_trade


def plot_data_hsec(platform, df_price, df_trade, stock_name):
    """Plot the price and trade data."""
    df_buy = df_trade[(df_trade['TRANSACTION TYPE'] == 'TRADE') & (df_trade['ACTION'] == 'Buy')]
    df_sell = df_trade[(df_trade['TRANSACTION TYPE'] == 'TRADE') & (df_trade['ACTION'] == 'Sell')]

    df_buy_group = group_by_date_mean(platform, df_buy)
    df_sell_group = group_by_date_mean(platform, df_sell)

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

    plt.scatter(df_buy_group['DATE'], df_buy_group['price'], color='g', marker='o', label='Buy Prices')
    plt.scatter(df_sell_group['DATE'], df_sell_group['price'], color='r', marker='o', label='Sell Prices')

    # Annotate each dot with the corresponding quantity
    for i, row in df_buy_group.iterrows():
        plt.text(row['DATE'], row['price'], f"{int(row['quantity'])}", color='g', fontsize=9, ha='right', va='bottom', rotation=45)

    for i, row in df_sell_group.iterrows():
        plt.text(row['DATE'], row['price'], f"{int(row['quantity'])}", color='r', fontsize=9, ha='right', va='bottom', rotation=45)

    # total_buy_price, total_buy_qty, total_sell_price, total_sell_qty, total_dividend = calculate_details(df_trade, platform)
    # text = f"Stock Analysis:\nTotal Bought: {total_buy_qty} qty | {total_buy_price} INR\nTotal Sold: {total_sell_qty} qty | {total_sell_price} INR\nTotal Dividend: {total_dividend} INR"


    # Longterm and Shortterm
    df_remaining, longTerm_qty, shortTerm_qty = fn_baseLongTerm_calc(platform, df_buy_group, df_sell_group)
    text = f"Details:\nLongTermQty: {longTerm_qty} qty \nShortTermQty: {shortTerm_qty} qty"

    avg_price = calculate_avg_price(df_remaining)
    # Create a list of avg_price with the same length as df_price['Date']
    if avg_price > 0:
        avg_price_line = [avg_price] * len(df_price['Date'])
        plt.plot(df_price['Date'], avg_price_line, linestyle='--', color='grey', label='CurrentAvgPrice')

    plt.legend()

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(0.02, 0.95, text, transform=plt.gca().transAxes, fontsize=10,
             verticalalignment='top', bbox=props)

    plt.show()

# Function to calculate weighted average price
def weighted_avg_price(x):
    return (x['quantity'] * x['price']).sum() / x['quantity'].sum()


def group_by_date(df):
    # Group by 'symbol' and 'trade_date', sum 'quantity', and calculate weighted average 'price'
    df_temp = df.groupby(['symbol', 'trade_date', 'totalDays']).agg(
        quantity = ('quantity', 'sum'),
        price=('quantity', 'sum')
    ).reset_index()

    df_temp['price'] = df.groupby(['symbol', 'trade_date'], group_keys=False).apply(weighted_avg_price).values
    df_temp['totalPrice'] = df_temp['quantity'] * df_temp['price']
    df_temp = df_temp.sort_values(by='trade_date')

    return df_temp

def group_by_date_mean(platform, df):

    if platform == 'KITE':
        # Group by 'symbol' and 'trade_date', sum 'quantity', and calculate weighted average 'price'
        df_temp = df.groupby(['symbol', 'trade_date', 'totalDays']).agg(
            quantity = ('quantity', 'sum'),
            price=('price', 'mean')
        ).reset_index()

        df_temp['totalPrice'] = df_temp['quantity'] * df_temp['price']
        df_temp = df_temp.sort_values(by='trade_date')

        return df_temp

    elif platform == 'HSEC':
        # Group by 'symbol' and 'trade_date', sum 'quantity', and calculate weighted average 'price'
        df_temp = df.groupby(['DATE', 'totalDays']).agg(
            quantity = ('QTY', 'sum'),
            price=('TRANSACTION PRICE', 'mean')
        ).reset_index()

        df_temp['totalPrice'] = df_temp['quantity'] * df_temp['price']
        df_temp = df_temp.sort_values(by='DATE')

        return df_temp

def plot_data_kite(platform, df_price, df_trade, stock_name):
    """Plot the price and trade data."""
    df_buy = df_trade[(df_trade['trade_type'] == 'buy')]
    df_sell = df_trade[(df_trade['trade_type'] == 'sell')]

    # df_buy_group = group_by_date(df_buy)
    # df_sell_group = group_by_date(df_sell)
    df_buy_group = group_by_date_mean(platform, df_buy)
    df_sell_group = group_by_date_mean(platform, df_sell)

    # Longterm and Shortterm
    df_remaining, longTerm_qty, shortTerm_qty = fn_baseLongTerm_calc(platform, df_buy_group, df_sell_group)

    avg_price = calculate_avg_price(df_remaining)
    # Create a list of avg_price with the same length as df_price['Date']
    avg_price_line = [avg_price] * len(df_price['Date'])

    text = f"Details:\nLongTermQty: {longTerm_qty} qty \nShortTermQty: {shortTerm_qty} qty"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # stockInfo = StockAPI.getKeyValues(df_trade['symbol'].iloc[0])
    # text = text + f"\nPE: {stockInfo['trailingPE']} | fwdPE: {stockInfo['forwardPE']}"

    # Ensure 'Price' column in df_price is numeric
    df_price['Price'] = df_price['Price'].astype(str)
    df_price['Price'] = pd.to_numeric(df_price['Price'].str.replace(",", ""), errors='coerce')

    plt.figure(figsize=(12, 7))
    plt.plot(df_price['Date'], df_price['Price'], color='b', label='Price')
    plt.plot(df_price['Date'], avg_price_line, linestyle='--', color='grey', label='CurrentAvgPrice')
    # # Annotate the avg price at the end of the line
    # plt.text(df_price['Date'].iloc[-1], avg_price, f"{avg_price:.2f}",
    #          color='grey', fontsize=10, va='top', ha='left', fontweight='bold')

    min_price = np.floor(df_price['Price'].min() / 10) * 10
    max_price = np.ceil(df_price['Price'].max() / 10) * 10
    price_range = np.linspace(min_price, max_price, num=15)
    plt.yticks(price_range)

    plt.title(f'Stock Price Over Time for {stock_name}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    plt.scatter(df_buy_group['trade_date'], df_buy_group['price'], color='g', marker='o', s=50, label='Buy Prices')
    plt.scatter(df_sell_group['trade_date'], df_sell_group['price'], color='r', marker='o', s=50, label='Sell Prices')

    # plot the text
    plt.text(0.02, 0.95, text, transform=plt.gca().transAxes, fontsize=10,
             verticalalignment='top', bbox=props)

    plt.legend()

    # Annotate each dot with the corresponding quantity
    for i, row in df_buy_group.iterrows():
        plt.text(row['trade_date'], row['price'], f"{int(row['quantity'])}", color='g', fontsize=9, ha='right', va='bottom', rotation=45)

    for i, row in df_sell_group.iterrows():
        plt.text(row['trade_date'], row['price'], f"{int(row['quantity'])}", color='r', fontsize=9, ha='right', va='top', rotation=45)


    # First buy date for drawing lines
    first_buy_date = df_buy_group['trade_date'].iloc[0]

    # Plot the first vertical line at the first buy date
    plt.axvline(x=first_buy_date, color='g', linestyle='--', label='First Buy')

    # Plot the second vertical line exactly 1 year after the first buy date
    year_later = first_buy_date + pd.DateOffset(years=1)
    plt.axvline(x=year_later, color='r', linestyle='--', label='1 Year Later')

    plt.show()


def fn_baseLongTerm_calc(platform, df_buy_group, df_sell_group):

    if platform == 'KITE' or platform == 'HSEC':
        df_remaining = df_buy_group.copy()
        totalSoldQty = df_sell_group['quantity'].sum()

        for index, row in df_remaining.iterrows():
            if row['quantity'] <= totalSoldQty:
                totalSoldQty -= row['quantity']
                df_remaining.at[index, 'quantity'] = 0  # Set the current row's quantity to 0
            else:
                df_remaining.at[index, 'quantity'] -= totalSoldQty  # Subtract remaining totalSoldQty
                totalSoldQty = 0  # All sold quantity has been subtracted, stop further deductions
                break  # Exit the loop as totalSoldQty is now 0

        shortTerm_qty = df_remaining.loc[(df_remaining['totalDays'] <= 365), 'quantity'].sum()
        longTerm_qty = df_remaining.loc[(df_remaining['totalDays'] > 365) , 'quantity'].sum()

        return df_remaining, longTerm_qty, shortTerm_qty

def calculate_avg_price(df_remaining):
    # Filter rows where quantity is greater than 0
    df_filtered = df_remaining[df_remaining['quantity'] > 0]

    # Calculate the total weighted price
    total_weighted_price = (df_filtered['quantity'] * df_filtered['price']).sum()

    # Calculate the total remaining quantity
    total_remaining_qty = df_filtered['quantity'].sum()

    # Calculate the average price
    if total_remaining_qty > 0:
        avg_price = total_weighted_price / total_remaining_qty
    else:
        avg_price = 0  # Handle cases where no remaining quantity exists

    return avg_price


def calculate_details(df_trade, platform):

    if platform == 'HSEC':
        """Calculate total buy, sell, and dividend values."""
        total_buy_price = df_trade.loc[(df_trade['ACTION'] == 'Buy') & (
                    df_trade['TRANSACTION TYPE'] == 'TRADE'), 'VALUE AT COST(Incl. addnl charges)'].sum()
        total_buy_qty = df_trade.loc[(df_trade['ACTION'] == 'Buy') & (df_trade['TRANSACTION TYPE'] == 'TRADE'), 'QTY'].sum()
        total_sell_price = df_trade.loc[df_trade['ACTION'] == 'Sell', 'VALUE AT COST(Incl. addnl charges)'].sum()
        total_sell_qty = df_trade.loc[df_trade['ACTION'] == 'Sell', 'QTY'].sum()
        total_dividend = df_trade.loc[(df_trade['EXCHANGE / CORPORATE ACTION'] == 'DIV') & (
                    df_trade['TRANSACTION TYPE'] == 'CORPORATE ACTION'), 'VALUE AT COST(Incl. addnl charges)'].sum()
        return total_buy_price, total_buy_qty, total_sell_price, total_sell_qty, total_dividend

def calculate_irr(df_trade, platform):
    if platform == 'KITE':
        df = df_trade.copy()

        # Ensure the cash flows are sorted by trade_date
        df = df.sort_values(by='trade_date')

        # Display all columns
        # pd.set_option('display.max_columns', None)
        # print(df.head())

        # Calculate cash flow
        df['cash_flow'] = np.where(df['trade_type'] == 'buy',
                                   df['quantity'] * df['price'] * -1,
                                   df['quantity'] * df['price'])

        cash_flows = df['cash_flow'].tolist()
        irr = npf.irr(cash_flows)

        print(irr)

def main():
    print("\nUse this module to plot the Stock Price and Trade details\n")
    demat = input('     Which account are we working on? (HSEC / ZX4974 / YY8886): ').upper().strip()
    price_details, trade_details = get_directories(demat)
    platform = 'KITE' if demat in ('ZX4974', 'YY8886') else 'HSEC' if demat == 'HSEC' else 'unknown'

    print(
        f"\n     Folders used for Historic Price and Trade details:\n         PriceDetails: {price_details}\n         TradePrice: {trade_details}\n")

    stock_name = input('    What stock to plot: ').upper().replace(" ", "")
    df_price, price_file = read_price_data(price_details, stock_name)
    df_trade = read_trade_data(trade_details, stock_name, platform)
    # df_trade = df_trade.drop_duplicates(subset='trade_id')  # This will be used only for zerodha trade files, HSEC trade files doesnot have trade_id

    if platform == 'HSEC':
        plot_data_hsec(platform, df_price, df_trade, stock_name)
        total_buy_price, total_buy_qty, total_sell_price, total_sell_qty, total_dividend = calculate_details(df_trade, platform)
        print(
            f"Total Bought: {total_buy_qty} qty | {total_buy_price} INR\nTotal Sold: {total_sell_qty} qty | {total_sell_price} INR\nTotal Dividend: {total_dividend} INR")


    elif platform == 'KITE':
        df_trade = df_trade.drop_duplicates(subset='trade_id')
        # calculate_irr(df_trade, platform)
        plot_data_kite(platform, df_price, df_trade, stock_name)


    print("Completed")

if __name__ == "__main__":
    main()

import utilCommon
import psycopg2
import pandas as pd
from datetime import datetime
from dateutil import parser
from scipy.optimize import newton

def connectDB():
    #connect to Postgres
    engine = utilCommon.connectPostgres()
    print("\n")
    return engine


def dfCreation(demat, query, engine, stockName):

    if demat == 'HSEC':
        df = pd.read_sql(query, con=engine, params=(stockName,))
        # Normalize date format
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        # Separate buy and sell
        buy_trades = df[df['action'].str.lower() == 'b'].copy()
        sell_trades = df[df['action'].str.lower() == 's'].copy()

        total_sold_quantity = sell_trades['quantity'].sum()

        return buy_trades, sell_trades, total_sold_quantity

def cashFlow(cash_flows, buy_trades, sell_trades, total_sold_quantity):
    # Process buys (negative cash flow)
    for idx, row in buy_trades.iterrows():
        if total_sold_quantity <= 0:
            break
        qty_to_use = min(row['quantity'], total_sold_quantity)
        portion = qty_to_use / row['quantity']
        amount = row['net_amount'] * portion
        cash_flows.append((row['trade_date'], amount))
        total_sold_quantity -= qty_to_use

    # Process sells (positive cash flow)
    for idx, row in sell_trades.iterrows():
        cash_flows.append((row['trade_date'], row['net_amount']))

    # Sort cash flows by date
    cash_flows.sort()

    return cash_flows


# XIRR function using Newton-Raphson method
def xirr(cash_flows):
    def npv(rate):
        return sum(cf / (1 + rate) ** ((d - dates[0]).days / 365) for cf, d in zip(amounts, dates))

    dates = [cf[0] for cf in cash_flows]
    amounts = [cf[1] for cf in cash_flows]
    return newton(npv, 0.1)

def main(platform, demat, stockName):
    engine = connectDB()

    if demat == 'HSEC':

        queryHSEC = f"""
        SELECT trade_date, action, quantity, net_amount
        FROM eq_trade_hsec
        WHERE stock_symbol = %s
        ORDER BY trade_date;
        """

        buy_trades, sell_trades, total_sold_quantity = dfCreation(demat, queryHSEC, engine, stockName)
        cash_flows = []
        cash_flows = cashFlow(cash_flows, buy_trades, sell_trades, total_sold_quantity)

        for dt, amt in cash_flows:
            print(f"{dt.date()}: {'+' if amt > 0 else ''}{amt:.2f}")

        # Calculate XIRR
        # irr = xirr(cash_flows)
        # print(f"IRR for {stockName}: {irr * 100:.2f}%")

if __name__ == "__main__":
    platform = 'HSEC'
    demat = 'HSEC'
    stockName = 'TATAPOWER'
    main(platform, demat, stockName)
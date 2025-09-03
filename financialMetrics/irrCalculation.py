import utilCommon
import psycopg2
import pandas as pd
from datetime import datetime
from dateutil import parser
from scipy.optimize import newton
from sqlalchemy import text

_engine = None

# Parms: Platform, Demat, StockName, NetProfit, irr
_irrLogQuery = """
    SELECT insert_stock_irr(:platform, :demat, :stock_name, :net_profit, :irr_value);
"""

# def connectDB():
#     #connect to Postgres
#     engine = utilCommon.connectPostgres()
#     print("\n")
#     return engine

def connectDB():
    global _engine
    if _engine is None:
        #connect to Postgres
        _engine = utilCommon.connectPostgres()
        print("\n")
    return _engine


def dfCreation(platform, demat, query, engine, stockName):

    if demat == 'HSEC':
        df = pd.read_sql(query, con=engine, params=(stockName,))
        # Normalize date format
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        # Separate buy and sell
        buy_trades = df[df['action'].str.lower() == 'b'].copy()
        sell_trades = df[df['action'].str.lower() == 's'].copy()

        total_sold_quantity = sell_trades['quantity'].sum()

        return buy_trades, sell_trades, total_sold_quantity

    elif platform == 'KITE':
        df = pd.read_sql(query, con=engine, params=(stockName,demat,))
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
        cash_flows.append((row['trade_date'], amount, qty_to_use))
        total_sold_quantity -= qty_to_use

    # Process sells (positive cash flow)
    for idx, row in sell_trades.iterrows():
        cash_flows.append((row['trade_date'], row['net_amount'], row['quantity']))

    # Sort cash flows by date
    cash_flows.sort()

    return cash_flows


# XIRR function using Newton-Raphson method
def xirr(cash_flows):
    def npv(rate):
        return sum(cf / (1 + rate) ** ((d - dates[0]).days / 365) for cf, d in zip(amounts, dates))

    dates = [cf[0] for cf in cash_flows]
    amounts = [cf[1] for cf in cash_flows]
    # return newton(npv, 0.1)
    # Try to call newton with a fallback
    try:
        return newton(npv, 0.1, maxiter=100, tol=1e-6)
    except RuntimeError as e:
        print("Newton-Raphson method failed:", e)
        return 0


def main(platform, demat, stockName, max_length, message_lines):
    engine = connectDB()

    if demat == 'HSEC':

        queryHSEC = f"""
        SELECT trade_date, action, quantity, net_amount
        FROM eq_trade_hsec
        WHERE stock_symbol = %s
        ORDER BY trade_date;
        """

        buy_trades, sell_trades, total_sold_quantity = dfCreation(platform, demat, queryHSEC, engine, stockName)
        cash_flows = []
        cash_flows = cashFlow(cash_flows, buy_trades, sell_trades, total_sold_quantity)

        # for dt, amt, qty in cash_flows:
        #     print(f"{dt.date()}: {qty} : {'+' if amt > 0 else ''}{amt:.2f}")

        # Calculate XIRR
        irr = xirr(cash_flows)
        new_cash_flows = []
        for date, amount, units in cash_flows:
            amount = round(float(amount), 2)  # Convert to normal Python float
            units = int(units)  # Convert to normal Python int
            price = round(amount/units, 2)
            new_cash_flows.append((date, amount, units, abs(price)))

        netProfit = 0
        # Now new_cash_flows has all clean types
        for entry in new_cash_flows:
            # print(entry[1])
            netProfit = netProfit + entry[1]
        # print(f"{stockName}: netProfit: {netProfit} | IRR: {irr * 100:.2f}%")
        engine = connectDB()
        # dfirr = pd.read_sql(_irrLogQuery, con=engine, params=(platform, demat, stockName,netProfit, float(irr)))
        with engine.begin() as conn:
            result = conn.execute(
                text(_irrLogQuery),
                {
                    "platform": platform,
                    "demat": demat,
                    "stock_name": stockName,
                    "net_profit": netProfit,
                    "irr_value": float(irr*100)
                }
            )
        print(f"{stockName:<{max_length}}| netProfit: {netProfit:>{11}.2f} | IRR: {irr * 100:.2f}%")
        formatted_line = f"{stockName:<{max_length}}| netProfit: {netProfit:>{11}.2f} | IRR: {irr * 100:.2f}%"
        message_lines.append(formatted_line)

    elif platform == 'KITE':

        queryKITE = f"""
        SELECT trade_date, upper(substr(k.action,1,1)) action, k.quantity, 
        CASE 
           WHEN k.action = 'buy' THEN -1 * k.net_amount
           ELSE k.net_amount
        END AS net_amount
        FROM eq_trade_kite k
        WHERE k.stock_symbol = %s
        and k.demat_id = %s
        ORDER BY k.trade_date;
        """

        buy_trades, sell_trades, total_sold_quantity = dfCreation(platform, demat, queryKITE, engine, stockName)
        cash_flows = []
        cash_flows = cashFlow(cash_flows, buy_trades, sell_trades, total_sold_quantity)

        # for dt, amt, qty in cash_flows:
        #     print(f"{dt.date()}: {qty} : {'+' if amt > 0 else ''}{amt:.2f}")

        # Calculate XIRR
        irr = xirr(cash_flows)
        new_cash_flows = []
        for date, amount, units in cash_flows:
            amount = round(float(amount), 2)  # Convert to normal Python float
            units = int(units)  # Convert to normal Python int
            price = round(amount / units, 2)
            new_cash_flows.append((date, amount, units, abs(price)))

        netProfit = 0
        # Now new_cash_flows has all clean types
        for entry in new_cash_flows:
            # print(entry[1])
            netProfit = netProfit + entry[1]
        # print(f"{stockName}: netProfit: {netProfit} | IRR: {irr * 100:.2f}%")
        print(f"{stockName:<{max_length}}| netProfit: {netProfit:>{11}.2f} | IRR: {irr * 100:.2f}%")
        formatted_line = f"{stockName:<{max_length}}| netProfit: {netProfit:>{11}.2f} | IRR: {irr * 100:.2f}%"
        message_lines.append(formatted_line)

if __name__ == "__main__":
    platform = 'KITE'
    demat = 'ZX4974'
    stockName = 'ROUTE'
    message_lines = []
    main(platform, demat, stockName, len(stockName), message_lines)
import irrCalculation
import utilCommon
import pandas as pd

def connectDB():
    #connect to Postgres
    engine = utilCommon.connectPostgres()
    print("\n")
    return engine


def main(demat, platform, teleMessage):
    engine = connectDB()
    # print(engine)

    if demat == 'HSEC':

        queryHSEC_SoldStock = f"""
        SELECT h.stock_symbol, max(trade_date) from eq_trade_hsec H
        where h.action = %s
        and h.stock_symbol not in ('RELCOM', 'NTPCGREEN') 
        group by h.stock_symbol
        order by 2;
        """

        # Stock, sell_trades, total_sold_quantity = dfCreation(demat, queryHSEC_SoldStock, engine, stockName)
        df = pd.read_sql(queryHSEC_SoldStock, con=engine, params=('S',))

    elif platform == 'KITE':

        queryKITE_SoldStock = f"""
            SELECT k.stock_symbol, max(k.trade_date) from eq_trade_kite k
            where k.action = %s 
            and k.demat_id = %s
            group by k.stock_symbol
            order by 2;
            """

        # Stock, sell_trades, total_sold_quantity = dfCreation(demat, queryHSEC_SoldStock, engine, stockName)
        df = pd.read_sql(queryKITE_SoldStock, con=engine, params=('sell', demat,))

    print(df)
    message_lines = []
    max_length = df['stock_symbol'].astype(str).str.len().max()
    for idx, row in df.iterrows():
        irrCalculation.main(platform, demat, row['stock_symbol'], max_length, message_lines)

    # Join all lines with newline characters
    final_message = "\n".join(message_lines)

    if teleMessage == 'Y':
        # Send via Telegram
        utilCommon.telegramMsg(final_message)


if __name__ == "__main__":
    # demat = 'ZX4974'
    print("\nUse this module to calculate the irr using the data from DB\n")
    demat = input('     Which account are we working on? (HSEC / ZX4974 / YY8886 / FS2831): ').upper().strip()
    platform = 'KITE' if demat in ('ZX4974', 'YY8886', 'FS2831') else 'HSEC' if demat == 'HSEC' else 'unknown'
    # teleMessage = 'N'
    teleMessage = input('     Do we need send a Message (Y/N): ').upper().strip()
    main(demat, platform, teleMessage)
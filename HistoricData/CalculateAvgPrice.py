import pandas as pd
import PlotChartUtil
import os
import sys

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

def createTotalTradeDf(commonTradePathandFile):

    demats = ['ZX4974', 'YY8886', 'FS2831', 'HSEC']
    csv_files_with_dmat = []

    for demat in demats:
        platform = 'KITE' if demat in ('ZX4974', 'YY8886', 'FS2831') else 'HSEC' if demat == 'HSEC' else 'unknown'
        price_details, trade_details = get_directories(demat)
        PlotChartUtil.FormatTradeDetails(platform, trade_details, os.path.join(trade_details, "TRADE"), demat)

        csv_files = [os.path.splitext(f)[0] for f in os.listdir(trade_details) if f.endswith(".csv")]

        for file in csv_files:
            csv_files_with_dmat.append((file, demat))  # Storing as tuple (filename, DMAT)

    df_source = pd.DataFrame(csv_files_with_dmat, columns=["Script", "DEMAT"])
    # df_source.to_csv(commonTradePathandFile, index=False)

    return df_source


def processSourcedf(year, df_totalTradeSource, tradedetailpath, totalQty, totalPrice, avg):

    # Initialize new columns with appropriate dtypes
    df_totalTradeSource[totalQty] = 0  # Integer
    df_totalTradeSource[totalPrice] = 0.0  # Float
    df_totalTradeSource[avg] = 0.0  # Float

    # sys.exit()

    for index, row in df_totalTradeSource.iterrows():
        platform = 'KITE' if row['DEMAT'] in ('ZX4974', 'YY8886', 'FS2831') else 'HSEC' if row['DEMAT'] == 'HSEC' else 'unknown'
        dematTotalTradeFile = os.path.join(tradedetailpath, row['DEMAT'], "TRADE", "00-TRADE-"+row['DEMAT']+'.csv')

        if platform == 'KITE' and os.path.exists(dematTotalTradeFile):
            dematTradePrice = pd.read_csv(dematTotalTradeFile)
            # Ensure the 'trade_date' column is in datetime format
            dematTradePrice["trade_date"] = pd.to_datetime(dematTradePrice["trade_date"], format="%Y-%m-%d", errors='coerce')
            # Apply initial filters for script and trade type
            dematTradePrice = dematTradePrice[
                (dematTradePrice["symbol"] == row['Script']) &
                (dematTradePrice["trade_type"] == 'buy')
            ]

            # Apply year filter only if the year is not "ALL"
            if year != "ALL":
                dematTradePrice = dematTradePrice[dematTradePrice["trade_date"].dt.year == int(year)]

            if not dematTradePrice.empty:

                calctotalQty = dematTradePrice['quantity'].sum()
                calctotalPrice = (dematTradePrice['quantity'] * dematTradePrice['price']).sum()
                calcavg = calctotalPrice / calctotalQty if calctotalQty > 0 else 0  # Avoid division by zero

                # Update the dataframe with new calculated values
                df_totalTradeSource.at[index, totalQty] = calctotalQty
                df_totalTradeSource.at[index, totalPrice] = calctotalPrice
                df_totalTradeSource.at[index, avg] = calcavg

        elif platform == 'HSEC' and os.path.exists(dematTotalTradeFile):
            dematTradePrice = pd.read_csv(dematTotalTradeFile)
            # Ensure the 'trDate' column is in datetime format
            dematTradePrice["trDate"] = pd.to_datetime(dematTradePrice["trDate"], format="%d-%b-%y", errors='coerce')
            # Apply initial filters for script and trade type
            dematTradePrice = dematTradePrice[
                (PlotChartUtil.hdfcScripts(dematTradePrice["ScriptName"]) == row['Script']) &
                (dematTradePrice["Action"] == 'B')
            ]

            # Apply year filter only if the year is not "ALL"
            if year != "ALL":
                dematTradePrice = dematTradePrice[dematTradePrice["trDate"].dt.year == int(year)]

            if not dematTradePrice.empty:

                calctotalQty = dematTradePrice['Qty'].sum()
                calctotalPrice = (dematTradePrice['Qty'] * dematTradePrice['MktPrice']).sum()
                calcavg = calctotalPrice / calctotalQty if calctotalQty > 0 else 0  # Avoid division by zero

                # Update the dataframe with new calculated values
                df_totalTradeSource.at[index, totalQty] = calctotalQty
                df_totalTradeSource.at[index, totalPrice] = calctotalPrice
                df_totalTradeSource.at[index, avg] = calcavg

    return df_totalTradeSource


def main():

    overAllTrades = 'OverAllTrades.csv'
    tradedetailpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Datas", "TradeDetails")
    commonTradePathandFile = os.path.join(tradedetailpath, overAllTrades)
    df_totalTradeSource = createTotalTradeDf(commonTradePathandFile)

    for year in ["ALL"] + [str(y) for y in range(2020, 2026)]:
        df_totalTradeSource = processSourcedf(year, df_totalTradeSource, tradedetailpath, year+"_totalQty", year+"_totalPrice", year+"_avg")

    # print(df_totalTradeSource)
    df_totalTradeSource.to_csv(commonTradePathandFile, index=False)
    print(f"\n\nCompleted - consolidated file created: {commonTradePathandFile}")

if __name__ == "__main__":
    main()
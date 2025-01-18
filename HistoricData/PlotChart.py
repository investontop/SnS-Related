import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import numpy_financial as npf
import mplcursors

print("")
print("     Use this module to plot the Stock Price and Trade details")
print("")
demat = input('     Which account we are working? (HSEC / ZX4974) : ').upper().strip()
print("")
print("     Folders we are using for Historic Price and Trade details are:" )
baseDir = os.getcwd()
# PriceDetails = r"E:\Programming\projects\python\SnS-Related\HistoricData\Data\PriceDetails"
# PriceDetails = os.getcwd() + r"\Data\PriceDetails"
PriceDetails = os.path.join(baseDir, "Data", "PriceDetails")
# TradeDetails  = r"E:\Programming\projects\python\SnS-Related\HistoricData\Data\TradeDetails"
# TradeDetails = os.getcwd() + r"\Data\TradeDetails\"+demat
TradeDetails = os.path.join(baseDir, "Data", "TradeDetails", demat)
print("     PriceDetails: "+PriceDetails)
print("     TradePrice  : "+TradeDetails)
print("")

StockName = input('     What stock to plot: ')
StockName = StockName.upper().replace(" ", "")


for dirname, _, filenames in os.walk(PriceDetails):
    for f in filenames:
        if StockName in f:
            dfPrice = pd.read_csv(os.path.join(dirname, f))
            PriceFile = f

            break

# Convert the 'Date' column to datetime format
dfPrice['Date'] = pd.to_datetime(dfPrice['Date'], format='%d-%m-%Y')


for dirname, _, filenames in os.walk(TradeDetails):
    for f in filenames:
        if f.startswith(StockName):
            dfTrade = pd.read_csv(os.path.join(dirname, f))
            TradeFile = f

            break

# Convert the 'Date' column to datetime format
dfTrade['DATE'] = pd.to_datetime(dfTrade['DATE'], format='%d-%b-%Y')

df_buy = dfTrade[(dfTrade['TRANSACTION TYPE'] == 'TRADE') & (dfTrade['ACTION'] == 'Buy')]
df_sell = dfTrade[(dfTrade['TRANSACTION TYPE'] == 'TRADE') & (dfTrade['ACTION'] == 'Sell')]

# Plotting the 'Price' over 'Date'
plt.figure(figsize=(12,7))
plt.plot(dfPrice['Date'], dfPrice['Price'], color='b', label='Price')

# Get the minimum and maximum price, rounded to nearest multiples of 10
min_price = np.floor(dfPrice['Price'].min() / 10) * 10
max_price = np.ceil(dfPrice['Price'].max() / 10) * 10
# Customize the y-axis ticks (e.g., create ticks every 10 units or custom spacing)
price_range = np.linspace(min_price, max_price, num=15)  # 10 price points
# Set custom y-axis ticks
plt.yticks(price_range)

# Add labels, title, and legend
plt.title(f'Stock Price Over Time for {PriceFile.split("-")[1]}')
plt.xlabel('Date')
plt.ylabel('Price')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()


# Overlay the traded price details as dots
plt.scatter(df_buy['DATE'], df_buy['TRANSACTION PRICE'], color='g', marker='o', label='Traded Prices')
plt.scatter(df_sell['DATE'], df_sell['TRANSACTION PRICE'], color='r', marker='o', label='Traded Prices')

# Reading the trades
# Sum the prices of 'Buy' transactions directly
total_buy_price = dfTrade.loc[(dfTrade['ACTION'] == 'Buy') & ( dfTrade['TRANSACTION TYPE'] == 'TRADE'), 'VALUE AT COST(Incl. addnl charges)'].sum()
total_buy_qty = dfTrade.loc[(dfTrade['ACTION'] == 'Buy') & ( dfTrade['TRANSACTION TYPE'] == 'TRADE'), 'QTY'].sum()
total_sell_price = dfTrade.loc[dfTrade['ACTION'] == 'Sell', 'VALUE AT COST(Incl. addnl charges)'].sum()
total_sell_qty = dfTrade.loc[dfTrade['ACTION'] == 'Sell', 'QTY'].sum()
total_dividend = dfTrade.loc[(dfTrade['EXCHANGE / CORPORATE ACTION'] == 'DIV') & ( dfTrade['TRANSACTION TYPE'] == 'CORPORATE ACTION'), 'VALUE AT COST(Incl. addnl charges)'].sum()

# XIRR calculation
# Adjust cash flows: negative for 'Buy' and positive for 'Sell'
# dfTrade['CASH_FLOW'] = dfTrade.apply(lambda x: -x['VALUE AT COST(Incl. addnl charges)'] if (x['ACTION'] == 'Buy') & (x['TRANSACTION TYPE'] == 'TRADE') else x['VALUE AT COST(Incl. addnl charges)'], axis=1)
#
# dates = dfTrade['DATE']
# cash_flows = dfTrade['CASH_FLOW']
#
# xirr_value = npf.xirr(cash_flows, dates)

# Adding a text note in a box
textstr = f"Stock Analysis:\n- Total Bought: {total_buy_qty} qty | {total_buy_price} inr\n- Total Sold: {total_sell_qty} qty | {total_sell_price} inr\n- Total Dividend: {total_dividend} inr"
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
plt.text(0.02, 0.95, textstr, transform=plt.gca().transAxes, fontsize=10,
         verticalalignment='top', bbox=props)

plt.show()


print("     Completed")
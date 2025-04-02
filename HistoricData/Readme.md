# Playing with Historic Data

### 1. (PlotChart-n.py) Plot the Trades along with Stock Price in a chart

### What this does?
 - This python code helps to plot the traded stock in a chart.
 - Plotting the "BUY and "SELL" along with the price of the stock.
 - This works for `HdfcSec` & `Zerodha Kite`

### Pre-req to execute this code

#### Folder structures:

|sno| Description         | Path                                        |FileTemplate| Manual(or)System                           |
|---|---------------------|---------------------------------------------|---|--------------------------------------------|
|1| Yearly Traded Files | `$base_dir/Datas/TradeDetails/$demat/TRADE` | `TRADE-yyyy.csv` | Manual Creation - Download from demat site |
|2| Club all Yearly Traded Files | `$base_dir/Datas/TradeDetails/$demat/TRADE` | `00-TRADE.csv` | System Creation - From the `sno:1` this file gets created.<br>This happens in `PlotChartUtil.FormatTradeDetails`|
|3| Stock wise Traded Files | `$base_dir/Datas/TradeDetails/$demat` | `$stockName.csv` | System Creation - From the `sno:1` this file gets created.<br>This happens in `PlotChartUtil.FormatTradeDetails`|
|4| Price Details of stock | `$base_dir/Datas/PriceDetails` | `$stockName-(fromYear-toYear).csv` | Manual Creation - Download this from `https://in.investing.com/` |

##### Notes:
  - `$base_dir`: The directory where this Py code exists.
  - `$demat`: This can be `HSEC` for hdfcsec and `Kite clientID` if it is Zerodha account.


### 2. (CalculateAvgPrice.py) Calculates the Avg price of any stocks that we bought from the year 2020

### What this does?
 - Picks the traded files from respective path
 - Creates a single file for each demat account.
 - and loads that in to POSTGRES DB.
 - And then from the POSTGRES tables, it does some calculations and create a file "OverAllTrades.csv"

### Pre-req to execute this code

#### Folder structures:

|sno| Description         | Path                                        |FileTemplate| Manual(or)System                           |
|---|---------------------|---------------------------------------------|---|--------------------------------------------|
|1| Yearly Traded Files | `$base_dir/Datas/TradeDetails/$demat/TRADE` | `TRADE-yyyy.csv` | Manual Creation - Download from demat site |
|2| Club all Yearly Traded Files | `$base_dir/Datas/TradeDetails/$demat/TRADE` | `00-TRADE.csv` | System Creation - From the `sno:1` this file gets created.<br>This happens in `PlotChartUtil.FormatTradeDetails`|


##### Notes:
  - `$base_dir`: The directory where this Py code exists.
  - `$demat`: This can be `HSEC` for hdfcsec and `Kite clientID` if it is Zerodha account.


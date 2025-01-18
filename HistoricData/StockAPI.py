import yfinance as yf

# stock = yf.Ticker("TATAMOTORS.NS")  # ".NS" for Indian stocks
# stock_info = stock.info
# print(stock_info['trailingPE'])  # P/E ratio
# print(stock_info['operatingMargins'])  # Operating Margin
#
# print(type(stock_info))
# print(stock_info)


def getKeyValues(stockName):

    stockTicker = yf.Ticker(stockName + ".NS")
    stock_info = stockTicker.info

    return stock_info

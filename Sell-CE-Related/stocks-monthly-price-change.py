import os
import sys
import pandas as pd
from datetime import datetime
import feedparser
from urllib.parse import quote


def get_news(stock, start_date, end_date):
    query = quote(f"{stock} stock")   # encode here
    
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    feed = feedparser.parse(url)
    
    results = []
    
    for entry in feed.entries:
        pub_date = datetime(*entry.published_parsed[:6])
        
        if start_date <= pub_date <= end_date:
            results.append({
                "title": entry.title,
                "date": pub_date,
                "link": entry.link
            })
    
    return results

def get_initialized(lookingFor):

    if lookingFor == "Source price path":
        base_dir = os.path.dirname(os.path.abspath(__file__))
        source_price_path = os.path.join(base_dir, "Source")
        if os.path.exists(source_price_path):
            return source_price_path
        else:
            print("\n     <<<<<Warning>>>>> SourcePath missing.")
            sys.exit("     Exiting program due to missing source price directory.\n\n")
    elif lookingFor == "ResultPath":
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ResultPath = os.path.join(base_dir, "Result")
        if not os.path.exists(ResultPath):
            os.makedirs(ResultPath)
        return ResultPath

def whichFile2Process(stock2calculate, source_price_path):
    listOfFiles = []
    # for file in os.listdir(source_price_path):
    #     if file.endswith(".csv") and stock2calculate in file:
    #         listOfFiles.append(file) 
    # return listOfFiles

    for file in os.listdir(source_price_path):
        if file.endswith(".csv") and stock2calculate in file:
            return os.path.join(source_price_path, file)
    print("\n     <<<<<Warning>>>>> No file found for the stock: ", stock2calculate)
    sys.exit("     Exiting program due to missing file for the stock: " + stock2calculate + "\n\n")


def processTheFile(File2Process):
    print("Processing file: ", File2Process)
    # Here you would add the logic to read the CSV file, calculate the monthly price change percentage, and output the results.
    # Monthly price change as in, each month, calculate the percentage change from the first day of the month to the last day of the month.
    # Store that in a new dataframe or a dictionary, and then print it out or save it to a new CSV file.
    # For example, you could use pandas to read the CSV and perform the calculations.

    df = pd.read_csv(File2Process)
    # the CSV file has the data for each day, columns: Date	Price	Open	High	Low	Vol.	Change %
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    df.sort_values('Date', inplace=True)
    print(df.head())

    df_monthly = df.groupby(df['Date'].dt.to_period('M')).agg({'Price': ['first', 'last']})

    df_monthly['MonthlyChange%'] = (df_monthly['Price']['last'] - df_monthly['Price']['first']) / df_monthly['Price']['first'] * 100
    print(df_monthly)

    return df_monthly


def main():
    print("\nThe agenda is to calculate the monthly price change percentage for the stocks")
    print("******************************************************************************")

    stock2calculate = input("\nStock to calculate the monthly price change %: ")
    stock2calculate = stock2calculate.strip().upper()
    source_price_path = get_initialized("Source price path")
    ResultPath = get_initialized("ResultPath")

    File2Process = whichFile2Process(stock2calculate, source_price_path)
    print("File to process: ", File2Process, "\n\n")

    df_monthly = processTheFile(File2Process)

    # Save the results to a CSV file
    result_file = os.path.join(ResultPath, f"{stock2calculate}_monthly_changes.csv")
    # Format the header of the CSV file to be more readable
    df_monthly.columns = ['Price_First', 'Price_Last', 'MonthlyChange%']
    df_monthly.to_csv(result_file, index=True) #include date as a column, not as index
    print(f"Results saved to {result_file}\n\n")

    # Get news for the stock for the month of July 2024
    # news = get_news(stock2calculate, datetime(2024,7,1), datetime(2024,7,31))
    # print(f"News for {stock2calculate} in July 2024:")
    # for item in news:
    #     print(f"{item['date'].strftime('%Y-%m-%d')}: {item['title']} - {item['link']}")

if __name__ == "__main__":
    main()
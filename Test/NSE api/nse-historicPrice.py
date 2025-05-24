import requests
import pandas as pd
from datetime import datetime

# --- Config ---
symbol = "COALINDIA"
from_date = "11-04-2024"
to_date = "11-04-2025"
url = f"https://www.nseindia.com/api/historical/securityArchives?from={from_date}&to={to_date}&symbol={symbol}&dataType=priceVolume&series=ALL"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive"
}

# --- Create session and get cookies ---
session = requests.Session()
session.get("https://www.nseindia.com", headers=headers)

# --- Request data ---
response = session.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    records = data.get("data", [])

    # Extract required fields
    cleaned_data = []
    for record in records:
        date_str = record["CH_TIMESTAMP"]
        formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")

        row = {
            "Date": formatted_date,
            "Price": record["CH_CLOSING_PRICE"],
            "Open": record["CH_OPENING_PRICE"],
            "High": record["CH_TRADE_HIGH_PRICE"],
            "Low": record["CH_TRADE_LOW_PRICE"]
        }
        cleaned_data.append(row)

    # Create and save DataFrame
    df = pd.DataFrame(cleaned_data)
    df.sort_values(by="Date", inplace=True)  # Sort by date (optional)
    df.to_csv("coalindia_prices.csv", index=False)
    print("✅ Data saved to coalindia_prices.csv")

else:
    print("❌ Failed to fetch data:", response.status_code)

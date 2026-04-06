import os
import sys
import csv
from datetime import datetime

def get_directories():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(base_dir, "Source")

    if os.path.exists(source_dir):
        return base_dir, source_dir
    else:
        print("\n     <<<<<Warning>>>>> No source directory found.")
        sys.exit("     Exiting program due to missing directory.")

def read_input_file(file_path, intend):
    if not os.path.exists(file_path):
        sys.exit(f"{intend} Input file not found: {inputFile}")
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Keep only lines that contain non-whitespace characters
    cleaned_Lines = [line.strip() for line in lines if line.strip()]
    return cleaned_Lines

def parse_trades(lines, intend):
    trades=[]
    i=0

    while i < len(lines):
        # stock = lines[i].strip()
        stock = lines[i].strip().replace(",", "")
        status = lines[i+2].strip().lower()  # buy or sell
        # Skip canceled trades
        if "cancel" in status:
            print(f"Skipping canceled trade for {stock}")
            i += 9
            continue
        amount = float(lines[i+6].replace('$',''))
        price = float(lines[i+8].replace('$',''))
        qty = round(amount / price, 4)

        trades.append({
            "stock": stock,
            "type": "buy" if "buy" in status else "sell",
            "qty": qty,
            "amount": amount
        })

        i += 9   # move to next trade block

    return trades

def summarize_trades(trades, intend):
    summary = {}

    for t in trades:
        stock = t["stock"]
        if stock not in summary:
            summary[stock] = {
                "BuyQty": 0.0,
                "BuyAmount": 0.0,
                "SellQty": 0.0,
                "SellAmount": 0.0
            }

        if t["type"] == "buy":
            summary[stock]["BuyQty"] += t["qty"]
            summary[stock]["BuyAmount"] += t["amount"]
        else:
            summary[stock]["SellQty"] += t["qty"]
            summary[stock]["SellAmount"] += t["amount"]

    # Add balance qty
    for stock, data in summary.items():
        data["BalanceQty"] = data["BuyQty"] - data["SellQty"]

    return summary

def main():    
    print("Welcome to INDMoney Trade Tracking!")
    intend = '     '
    base_dir, source_dir = get_directories()
    # print(f"{intend} Base Directory: {base_dir}")

    inputFile = os.path.join(source_dir, "INDMoney-TRADE-20251204.txt") # Manual Input
    lines = read_input_file(inputFile, intend)

    # Parse the trades
    trades = parse_trades(lines, intend)
    
    # Summarize group per stock
    summary = summarize_trades(trades, intend)

    # Print nicely
    print("\nTrade Summary:")
    print(intend+'Stock, BuyQty, BuyAmount, SellQty, SellAmount, BalanceQty')
    for stock, s in summary.items():
        print(f"{intend}{stock}, {s['BuyQty']:.2f}, {s['BuyAmount']:.2f}, "
              f"{s['SellQty']:.2f}, {s['SellAmount']:.2f}, {s['BalanceQty']:.2f}")
        
    
     # -----------------------------------------
    # Write summary as CSV
    # -----------------------------------------
    today = datetime.now().strftime("%Y%m%d")
    csv_file = os.path.join(base_dir, f"summary_{today}.csv")

    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Stock", "BuyQty", "BuyAmount", "SellQty", "SellAmount", "BalanceQty"])

        for stock, s in summary.items():
            writer.writerow([
                stock,
                f"{s['BuyQty']:.2f}",
                f"{s['BuyAmount']:.2f}",
                f"{s['SellQty']:.2f}",
                f"{s['SellAmount']:.2f}",
                f"{s['BalanceQty']:.2f}"
            ])

    print(f"\nCSV summary file created: {csv_file}")

if __name__ == "__main__":
    main()
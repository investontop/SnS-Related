import os
import sys


def get_directories():
    """Get the directories for price and trade details."""
    # base_dir = os.getcwd()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    price_details = os.path.join(base_dir, "Datas", "PriceDetails")
    trade_details = os.path.join(base_dir, "Datas", "TradeDetails")

    if os.path.exists(trade_details):
        return price_details, trade_details
    else:
        print("\n     <<<<<Warning>>>>> Please enter the right demat")
        sys.exit("     Exiting program due to missing trade details directory.")


def main():

    print("     Test as a trial")



if __name__ == "__main__":
    main()
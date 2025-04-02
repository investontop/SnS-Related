import os
import PlotChartUtil
import utilCommon
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import sys

# sys.path.append(r"E:\Programming\projects\python\00-commonUtil")
# # import utilCommon
#
# print(sys.path)
# print(os.listdir(r"E:\Programming\projects\python\00-commonUtil"))

def plotTheChart(plot_df):

    # Plot bar chart
    ax = plot_df.plot(
        x="YYYYMM",
        y=["net_amount"],
        kind="bar",
        figsize=(16, 10),
        title="Financial Buy Data Over Time including other charges"
    )

    plt.xlabel("YYYYMM")
    plt.ylabel("amount")
    plt.xticks(rotation=45)  # Rotate x-axis labels for readability
    plt.legend(title="Metrics")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    #Add more Y-axis ticks
    y_min, y_max = ax.get_ylim()
    yticks = np.linspace(y_min, y_max, num=10)  # 10 evenly spaced ticks
    plt.yticks(yticks)

    plt.show()

def plotTheChartBothBuyandSell(monthly_summary):

    # Plot using Seaborn
    plt.figure(figsize=(20, 6))
    sns.barplot(x="YYYYMM", y="net_amount", hue="action", data=monthly_summary, palette={"B": "blue", "S": "red"})

    # Labels and title
    plt.xlabel("Month (YYYYMM)")
    plt.ylabel("Net Amount")
    plt.ticklabel_format(style="plain", axis="y")  # Disable scientific notation on Y-axis
    plt.title("Net Amount for Buy (B) and Sell (S) Actions")
    plt.xticks(rotation=45)
    plt.legend(title="Action")
    # Enable Grid
    plt.grid(True, linestyle="--", alpha=0.7)  # Dashed grid lines with transparency

    plt.show()


def connectDBandCreateDF(dematList):

    #connect to Postgres
    engine = utilCommon.connectPostgres()
    print("\n")

    for demat, platform in dematList:
        if platform == 'HSEC':
            query = 'select * from eq_trade_hsec;'
            # Read data into a Pandas DataFrame
            df = pd.read_sql(query, engine)

            # Convert trDate to datetime format
            df["trade_date"] = pd.to_datetime(df["trade_date"])
            # Create YYYYMM column
            df["YYYYMM"] = df["trade_date"].dt.strftime("%Y%m")
            # Group by YYYYMM and Action, then sum NetAmt
            # monthly_summary = df.groupby(["YYYYMM", "Action"])["NetAmt"].apply(lambda x: x.abs().sum()).reset_index()
            monthly_summary = df.groupby(["YYYYMM", "action"]).agg({
                "net_amount": lambda x: x.abs().sum(),  # Sum absolute values
                "market_value": "sum"  # Sum normally
            }).reset_index()

            monthly_summary["other_charges"] = (monthly_summary["net_amount"] - monthly_summary["market_value"]).abs()

            # # Convert DataFrame to Markdown text
            # message = "```\n" + monthly_summary.head(10).to_string(index=False) + "\n```"
            # print(message)
            # utilCommon.telegramMsg(message)

            # print(monthly_summary)
            # Filter only for Action = 'B'
            # df_B = monthly_summary[monthly_summary["action"] == "B"]
            # plotTheChart(df_B)

            plotTheChartBothBuyandSell(monthly_summary)



def main():

    print("Remember, this py script gets the data from the PostGres DB which is already loaded"
          "\nIn case if there is any new TRADE files, we need to execute the dependent script to load that in DB "
          "\nCalculateAvgPrice.py is the dependent file you can execute to load the postgres db")

    dematList = PlotChartUtil.initialize_setup('dematList')
    connectDBandCreateDF(dematList)  #connect DB and create df

if __name__ == "__main__":
    main()
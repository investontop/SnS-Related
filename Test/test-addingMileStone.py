import pandas as pd
import matplotlib.pyplot as plt

# Sample data
data = {
    'Year': [2020, 2021, 2022, 2023, 2024],
    'Income': [50000, 55000, 60000, 62000, 70000],
    'Expense': [30000, 35000, 37000, 40000, 42000],
    'Savings': [20000, 20000, 23000, 22000, 28000],
}

df = pd.DataFrame(data)

# Plot Income and Expense
plt.figure(figsize=(10, 6))
plt.plot(df['Year'], df['Income'], label='Income', marker='o')
plt.plot(df['Year'], df['Expense'], label='Expense', marker='o')
plt.plot(df['Year'], df['Savings'], label='Savings', marker='o')

# Add annotations (milestones)
milestones = {
    2021: "Job Change",
    2023: "New Car",
}

for year, event in milestones.items():
    income_value = df[df['Year'] == year]['Income'].values[0]
    plt.annotate(
        event,
        (year, income_value),
        textcoords="offset points",
        xytext=(0, 10),
        ha='center',
        fontsize=9,
        color='red',
        arrowprops=dict(arrowstyle='->', color='gray')
    )

# Decorate
plt.title("Yearly Financial Overview")
plt.xlabel("Year")
plt.ylabel("Amount (₹)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

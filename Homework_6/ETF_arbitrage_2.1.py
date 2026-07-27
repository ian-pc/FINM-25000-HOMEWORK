import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

DATA_PATH = "etf_arb_data.xlsx"

# Load price and NAV data
prices = pd.read_excel(
    DATA_PATH,
    sheet_name="prices",
    index_col=0
)

nav = pd.read_excel(
    DATA_PATH,
    sheet_name="nav",
    index_col=0
)

prices.index = pd.to_datetime(prices.index)
nav.index = pd.to_datetime(nav.index)

# Calculate premium/discount
premium_discount = prices.div(nav).sub(1)

# Select HYG observations from 2020
hyg_2020 = premium_discount.loc["2020", "HYG"].dropna()

# Locate minimum and maximum
deepest_discount_date = hyg_2020.idxmin()
deepest_discount = hyg_2020.min()

largest_premium_date = hyg_2020.idxmax()
largest_premium = hyg_2020.max()

print("HYG premium/discount results for 2020:")

print(
    f"Deepest discount: {deepest_discount:.4%} "
    f"on {deepest_discount_date:%Y-%m-%d}"
)

print(
    f"Largest premium: {largest_premium:.4%} "
    f"on {largest_premium_date:%Y-%m-%d}"
)

# Plot
plt.figure(figsize=(12, 6))

plt.plot(
    hyg_2020.index,
    hyg_2020,
    linewidth=1.5,
    label="HYG premium/discount"
)

plt.axhline(
    y=0,
    linestyle="--",
    linewidth=1,
    label="NAV"
)

# Mark the extreme values
plt.scatter(
    deepest_discount_date,
    deepest_discount,
    s=60,
    label="Deepest discount"
)

plt.scatter(
    largest_premium_date,
    largest_premium,
    s=60,
    label="Largest premium"
)

plt.title("HYG Premium/Discount to NAV During 2020")
plt.xlabel("Date")
plt.ylabel("Premium/Discount")
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
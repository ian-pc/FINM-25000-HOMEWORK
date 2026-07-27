import pandas as pd
import matplotlib.pyplot as plt

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

# Ensure the indexes are dates
prices.index = pd.to_datetime(prices.index)
nav.index = pd.to_datetime(nav.index)

# Premium/discount = Price / NAV - 1
# This calculation is done for every fund
premium_discount = prices.div(nav).sub(1)

print("First five premium/discount observations:")
print(premium_discount.head())

# Select SPY
spy_premium = premium_discount["SPY"].dropna()

# Calculate requested statistics and convert to basis points
spy_stats_bps = (
    spy_premium
    .agg(["mean", "std", "min", "max"])
    .mul(10_000)
)

spy_stats_bps.index = [
    "Mean",
    "Standard deviation",
    "Minimum",
    "Maximum"
]

print("\nSPY premium/discount statistics in basis points:")
print(spy_stats_bps.round(4))

# Plot SPY premium/discount in basis points
plt.figure(figsize=(12, 6))
plt.plot(
    spy_premium.index,
    spy_premium * 10_000,
    linewidth=1
)

plt.axhline(
    y=0,
    linestyle="--",
    linewidth=1
)

plt.title("SPY Daily Premium/Discount to NAV")
plt.xlabel("Date")
plt.ylabel("Premium/Discount (basis points)")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
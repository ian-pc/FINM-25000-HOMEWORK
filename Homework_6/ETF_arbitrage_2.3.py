import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

DATA_PATH = "etf_arb_data.xlsx"

# Load data
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

# Combine the HYG data
hyg = pd.DataFrame({
    "Market Price": prices["HYG"],
    "NAV": nav["HYG"]
}).dropna()

hyg["Premium/Discount"] = (
    hyg["Market Price"] / hyg["NAV"] - 1
)

# Focus on the market disruption and recovery
crisis_period = hyg.loc["2020-02-15":"2020-05-15"]

# March minimum and April maximum
march_data = hyg.loc["2020-03"]
april_data = hyg.loc["2020-04"]

march_discount_date = (
    march_data["Premium/Discount"].idxmin()
)

april_premium_date = (
    april_data["Premium/Discount"].idxmax()
)

print("March 2020 deepest discount:")
print(
    f"{march_data.loc[march_discount_date, 'Premium/Discount']:.4%} "
    f"on {march_discount_date:%Y-%m-%d}"
)

print("\nApril 2020 largest premium:")
print(
    f"{april_data.loc[april_premium_date, 'Premium/Discount']:.4%} "
    f"on {april_premium_date:%Y-%m-%d}"
)

# Plot market price and NAV
plt.figure(figsize=(12, 6))

plt.plot(
    crisis_period.index,
    crisis_period["Market Price"],
    label="HYG market price",
    linewidth=2
)

plt.plot(
    crisis_period.index,
    crisis_period["NAV"],
    label="HYG NAV",
    linewidth=2
)

plt.title("HYG Market Price Compared with NAV")
plt.xlabel("Date")
plt.ylabel("Dollars per share")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# Plot premium/discount separately
plt.figure(figsize=(12, 6))

plt.plot(
    crisis_period.index,
    crisis_period["Premium/Discount"],
    linewidth=2
)

plt.axhline(
    y=0,
    linestyle="--",
    linewidth=1
)

plt.title("HYG Premium/Discount During the 2020 Crisis")
plt.xlabel("Date")
plt.ylabel("Premium/Discount")
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
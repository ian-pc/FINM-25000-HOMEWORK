import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = "etf_arb_data.xlsx"

# Load the data
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

# Combine HYG price and NAV
hyg = pd.DataFrame({
    "Market Price": prices["HYG"],
    "NAV": nav["HYG"]
}).dropna()

hyg["Premium/Discount"] = (
    hyg["Market Price"] / hyg["NAV"] - 1
)

# Select March 2020
hyg_march = hyg.loc["2020-03-01":"2020-03-31"]

# Find the deepest discount
deepest_date = hyg_march["Premium/Discount"].idxmin()
deepest_observation = hyg_march.loc[deepest_date]

print("Deepest March 2020 discount:")
print(f"Date: {deepest_date:%Y-%m-%d}")
print(f"Market price: ${deepest_observation['Market Price']:.2f}")
print(f"NAV: ${deepest_observation['NAV']:.2f}")

print(
    "Premium/discount: "
    f"{deepest_observation['Premium/Discount']:.4%}"
)

apparent_spread = (
    deepest_observation["NAV"]
    - deepest_observation["Market Price"]
)

print(f"Apparent spread per share: ${apparent_spread:.2f}")

# Plot price and NAV
plt.figure(figsize=(12, 6))

plt.plot(
    hyg_march.index,
    hyg_march["Market Price"],
    label="HYG market price",
    linewidth=2
)

plt.plot(
    hyg_march.index,
    hyg_march["NAV"],
    label="HYG NAV",
    linewidth=2
)

plt.title("HYG Market Price and NAV — March 2020")
plt.xlabel("Date")
plt.ylabel("Dollars per share")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
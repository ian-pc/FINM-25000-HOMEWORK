import pandas as pd

DATA_PATH = "spx_returns_weekly.xlsx"
TICKERS = ["NVDA", "AMD", "CMG", "SBUX"]

WINDOW = 26
q = 0.05
z_q = -1.65

# Load weekly returns
returns = pd.read_excel(
    DATA_PATH,
    sheet_name="spx returns"
)

returns = returns.set_index("date")[TICKERS]

# Equally weighted portfolio
weights = pd.Series(
    1 / len(TICKERS),
    index=TICKERS
)

port_ret = returns @ weights
port_ret.name = "EW_Portfolio"

# Volatility estimates available before observing return at time t
expanding_vol = (
    port_ret
    .expanding(min_periods=WINDOW)
    .std()
    .shift(1)
)

rolling_vol = (
    port_ret
    .rolling(WINDOW)
    .std()
    .shift(1)
)

# VaR expressed as a negative return threshold
expanding_var = z_q * expanding_vol
rolling_var = z_q * rolling_vol

# Keep dates where volatility can be calculated
valid_expanding = expanding_var.notna()
valid_rolling = rolling_var.notna()

# A hit occurs when the realized return is below the VaR threshold
expanding_hits = (
    port_ret[valid_expanding]
    < expanding_var[valid_expanding]
)

rolling_hits = (
    port_ret[valid_rolling]
    < rolling_var[valid_rolling]
)

results = pd.DataFrame({
    "Observations": [
        valid_expanding.sum(),
        valid_rolling.sum()
    ],
    "Hits": [
        expanding_hits.sum(),
        rolling_hits.sum()
    ],
    "Hit Percentage": [
        expanding_hits.mean(),
        rolling_hits.mean()
    ]
}, index=[
    "Expanding volatility",
    "Rolling volatility"
])

print("VaR Hit Test Results:")
print(results)

print("\nHit percentages:")
print(
    f"Expanding volatility: "
    f"{expanding_hits.mean():.2%}"
)

print(
    f"Rolling volatility: "
    f"{rolling_hits.mean():.2%}"
)

print(f"Expected hit percentage: {q:.2%}")
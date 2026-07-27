import pandas as pd

DATA_PATH = "etf_arb_data.xlsx"

CREATION_SHARES = 50_000
CREATION_FEE = 3_000
TRADING_COST_RATE = 0.0003  # 3 basis points

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

# Most recent SPY NAV
spy_nav = nav["SPY"].dropna()
latest_nav = spy_nav.iloc[-1]
latest_date = spy_nav.index[-1]

# Value of one 50,000-share creation unit
basket_value = latest_nav * CREATION_SHARES

# Cost of trading the underlying basket
basket_trading_cost = basket_value * TRADING_COST_RATE

# Break-even condition:
# premium profit = creation fee + basket trading cost
break_even_premium = (
    CREATION_FEE + basket_trading_cost
) / basket_value

break_even_percent = break_even_premium * 100
break_even_bps = break_even_premium * 10_000

print(f"Most recent NAV date: {latest_date:%Y-%m-%d}")
print(f"Creation unit value: ${basket_value:,.2f}")
print(f"Creation fee: ${CREATION_FEE:,.2f}")
print(f"Basket trading cost: ${basket_trading_cost:,.2f}")

print(f"\nBreak-even premium: {break_even_percent:.4f}%")
print(f"Break-even premium: {break_even_bps:.4f} basis points")

# Compare the result with the SPY statistics from 1.1
premium_discount = prices.div(nav).sub(1)
spy_premium = premium_discount["SPY"].dropna()

spy_stats_bps = (
    spy_premium
    .agg(["mean", "std", "min", "max"])
    .mul(10_000)
)

comparison = pd.Series({
    "Mean SPY premium": spy_stats_bps["mean"],
    "SPY premium standard deviation": spy_stats_bps["std"],
    "Minimum SPY premium": spy_stats_bps["min"],
    "Maximum SPY premium": spy_stats_bps["max"],
    "Creation break-even premium": break_even_bps
})

print("\nComparison in basis points:")
print(comparison.round(4))

# Verify that profit is approximately zero at break-even
premium_revenue = basket_value * break_even_premium

net_profit = (
    premium_revenue
    - basket_trading_cost
    - CREATION_FEE
)

print(f"\nNet profit at break-even: ${net_profit:,.2f}")
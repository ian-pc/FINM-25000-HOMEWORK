import pandas as pd

DATA_PATH = "etf_arb_data.xlsx"

CREATION_SHARES = 50_000
PREMIUM_RATE = 0.005  # 0.50%

# Load NAV data
nav = pd.read_excel(
    DATA_PATH,
    sheet_name="nav",
    index_col=0
)

nav.index = pd.to_datetime(nav.index)

# Most recent available SPY NAV
spy_nav = nav["SPY"].dropna()

latest_date = spy_nav.index[-1]
latest_nav = spy_nav.iloc[-1]

# Value of the underlying basket needed for one creation unit
basket_purchase_cost = latest_nav * CREATION_SHARES

# Hypothetical SPY market price at a 0.50% premium
spy_market_price = latest_nav * (1 + PREMIUM_RATE)

# Proceeds from selling the newly created SPY shares
sale_proceeds = spy_market_price * CREATION_SHARES

# Gross arbitrage profit before fees and trading costs
gross_profit = sale_proceeds - basket_purchase_cost

print("Authorized participant creation trade:")
print("1. Buy the underlying S&P 500 stock basket.")
print("2. Deliver the basket to the ETF sponsor.")
print("3. Receive 50,000 newly created SPY shares.")
print("4. Sell those SPY shares at the 0.50% premium.")

print(f"\nMost recent NAV date: {latest_date:%Y-%m-%d}")
print(f"SPY NAV per share: ${latest_nav:,.4f}")
print(f"SPY market price at 0.50% premium: ${spy_market_price:,.4f}")

print(f"\nCost of underlying basket: ${basket_purchase_cost:,.2f}")
print(f"Proceeds from selling SPY: ${sale_proceeds:,.2f}")
print(f"Gross arbitrage profit: ${gross_profit:,.2f}")
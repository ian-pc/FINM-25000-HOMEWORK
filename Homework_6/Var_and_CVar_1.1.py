import pandas as pd

DATA_PATH = "spx_returns_weekly.xlsx"
TICKERS = ["NVDA", "AMD", "CMG", "SBUX"]

returns = pd.read_excel(DATA_PATH, sheet_name="spx returns")
returns = returns.set_index("date")[TICKERS]

q = 0.05

vol = returns.std()

var_q = returns.quantile(q)
VaR = -var_q

CVaR = -returns[returns.le(var_q)].mean()

print("Volatility\n", vol)
print("VaR (.05)\n", VaR)
print("CVaR (.05)\n", CVaR)
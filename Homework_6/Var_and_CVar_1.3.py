import pandas as pd

DATA_PATH = "spx_returns_weekly.xlsx"
TICKERS = ["NVDA", "AMD", "CMG", "SBUX"]
q = 0.05

returns = pd.read_excel(DATA_PATH, sheet_name="spx returns")
returns = returns.set_index("date")[TICKERS]

def risk_stats(ret_series, q=0.05):
  vol = ret_series.std()
  var_q = ret_series.quantile(q)
  VaR = -var_q
  CVaR = -ret_series[ret_series.le(var_q)].mean()
  return pd.Series({"Volatility": vol, "VaR (.05)": VaR, "CVaR (.05)": CVaR})

indiv_vol = returns.std()
most_volatile = indiv_vol.idxmax()
print(f"Most volatile asset: {most_volatile} (vol = {indiv_vol[most_volatile]:.4f})")

weights_full = pd.Series(1 / len(TICKERS), index=TICKERS)
port_ret_full = returns @ weights_full
stats_full = risk_stats(port_ret_full)

remaining = [t for t in TICKERS if t != most_volatile]
weights_reduced = pd.Series(1 / len(TICKERS), index=remaining)
port_ret_reduced = returns[remaining] @ weights_reduced
stats_reduced = risk_stats(port_ret_reduced)

compare = pd.DataFrame({
  "1.2 (all 4, EW)": stats_full, f"1.3 (drop {most_volatile}, EW + cash)": stats_reduced,
})

print(compare.round(4))
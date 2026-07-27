import pandas as pd
 
DATA_PATH = "spx_returns_weekly.xlsx"
TICKERS = ["NVDA", "AMD", "CMG", "SBUX"]
q = 0.05
 
returns = pd.read_excel(DATA_PATH, sheet_name="spx returns")
returns = returns.set_index("date")[TICKERS]

weights = pd.Series(1 / len(TICKERS), index=TICKERS)
port_ret = returns @ weights
port_ret.name = "EW_Portfolio"
 
def risk_stats(ret_series, q=0.05):
  vol = ret_series.std()
  var_q = ret_series.quantile(q)
  VaR = -var_q
  CVaR = -ret_series[ret_series.le(var_q)].mean()
  return pd.Series({"Volatility": vol, "VaR (.05)": VaR, "CVaR (.05)": CVaR})
 
indiv_stats = returns.apply(risk_stats).T

port_stats = risk_stats(port_ret)
port_stats.name = "EW_Portfolio"
 
full_table = pd.concat([indiv_stats, port_stats.to_frame().T])

print(port_stats)
avg_of_individual_vol = indiv_stats["Volatility"].mean()
print(f"Simple average of the 4 individual volatilities: {avg_of_individual_vol:.4f}")
print(f"Equally-weighted portfolio volatility: {port_stats['Volatility']:.4f}")
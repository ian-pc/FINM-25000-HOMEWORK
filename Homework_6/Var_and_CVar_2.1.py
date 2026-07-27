import numpy as np
import pandas as pd

DATA_PATH = "spx_returns_weekly.xlsx"
TICKERS = ["NVDA", "AMD", "CMG", "SBUX"]
q = 0.05
z_q = -1.65
WINDOW = 26
WEEKS_PER_YEAR = 52

returns = pd.read_excel(DATA_PATH, sheet_name="spx returns")
returns = returns.set_index("date")[TICKERS]

weights = pd.Series(1 / len(TICKERS), index=TICKERS)
port_ret = returns @ weights
port_ret.name = "EW_Portfolio"

rolling_vol = port_ret.rolling(WINDOW).std().shift(1)
rolling_vol.name = "sigma_t (rolling, m=26)"

sigma_t_end = rolling_vol.iloc[-1]
print(f"Rolling (m=26) forecasted volatility as of end of sample: {sigma_t_end:.4f} (weekly)")

from scipy.stats import norm

VaR_normal = -z_q * sigma_t_end
CVaR_normal = sigma_t_end * norm.pdf(z_q) / q

vol_annualized = sigma_t_end * np.sqrt(WEEKS_PER_YEAR)

print(f"Volatility (weekly):      {sigma_t_end:.4f}")
print(f"Volatility (annualized):  {vol_annualized:.4f}")
print(f"Normal VaR (.05):         {VaR_normal:.4f}")
print(f"Normal CVaR (.05):        {CVaR_normal:.4f}")

vol_uncond = port_ret.std()
var_q_uncond = port_ret.quantile(q)
VaR_uncond = -var_q_uncond
CVaR_uncond = -port_ret[port_ret.le(var_q_uncond)].mean()

compare = pd.DataFrame({
  "1.2 Unconditional (full-sample, empirical)": {
    "Volatility (weekly)": vol_uncond,
    "VaR (.05)": VaR_uncond,
    "CVaR (.05)": CVaR_uncond,
  },
  "2.1 Conditional (rolling m=26, Normal)": {
    "Volatility (weekly)": sigma_t_end,
    "VaR (.05)": VaR_normal,
    "CVaR (.05)": CVaR_normal,
  },
})

print("\nComparison table:")
print(compare.round(4))
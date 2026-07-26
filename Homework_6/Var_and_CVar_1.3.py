import pandas as pd
import numpy as np

df = pd.read_excel('spx_returns_weekly.xlsx', sheet_name='spx returns')
tickers = [c for c in df.columns if c != 'date']
rets = df[tickers]

def stats(r):
  r = r.dropna()
  vol = r.std()
  VaR = -r.quantile(0.05)
  CVaR = -r[r <= r.quantile(0.05)].mean()
  return pd.Series({'vol': vol, 'VaR_05': VaR, 'CVaR_05': CVaR})

vols = rets.std()
most_vol_ticker = vols.idxmax()

port_full = rets.mean(axis=1)

rets_mod = rets.copy()
rets_mod[most_vol_ticker] = 0.0
port_mod = rets_mod.mean(axis=1)

print(stats(port_full))
print(stats(port_mod))
print(stats(rets[most_vol_ticker]))
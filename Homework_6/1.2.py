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

nvda_stats = stats(rets['NVDA'])
nvda_stats['vol_annualized'] = nvda_stats['vol'] * np.sqrt(52)

port = rets.mean(axis=1)
port_stats = stats(port)

indiv_stats = pd.DataFrame({t: stats(rets[t]) for t in tickers}).T
avg_indiv_stats = indiv_stats.mean()

corr = rets.corr()
n = len(tickers)
avg_corr = (corr.values.sum() - n) / (n * (n - 1))

print('NVDA\n', nvda_stats, '\n')
print('Equally-weighted portfolio (503 stocks)\n', port_stats, '\n')
print('Average across individual stocks\n', avg_indiv_stats, '\n')
print('Average pairwise correlation\n', avg_corr, '\n')
print('Check diversification formula: avg_indiv_vol * sqrt(avg_corr) ≈ portfolio_vol\n', avg_indiv_stats['vol'] * np.sqrt(avg_corr), 'vs actual', port_stats['vol'])
import pandas as pd

df = pd.read_excel('spx_returns_weekly.xlsx', sheet_name='spx returns')
r = df['NVDA'].dropna()

vol = r.std()

VaR_05 = -r.quantile(0.05)

CVaR_05 = -r[r <= r.quantile(0.05)].mean()

print('weekly volatility:', vol)
print('annualized volatility:', vol * (52**0.5))
print('VaR (.05):', VaR_05)
print('CVaR (.05):', CVaR_05)

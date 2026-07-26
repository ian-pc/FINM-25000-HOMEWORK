import pandas as pd
import numpy as np

df = pd.read_excel('spx_returns_weekly.xlsx', sheet_name='spx returns')
tickers = [c for c in df.columns if c != 'date']
rets = df[tickers]

port = rets.mean(axis=1)

m = 26
sigma_forecast = port.iloc[-m:].std()
sigma_ann = sigma_forecast * np.sqrt(52)

z = -1.65
q = 0.05
mu = 0.0

VaR_normal = -(mu + z * sigma_forecast)

phi = lambda x: np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
CVaR_normal = -(mu - sigma_forecast * phi(z) / q)

print('Weekly conditional vol :', sigma_forecast)
print('Annualized vol         :', sigma_ann)
print('Normal VaR (.05)       :', VaR_normal)
print('Normal CVaR (.05)      :', CVaR_normal)
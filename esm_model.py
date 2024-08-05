from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pandas as pd
import numpy as np

# Load and prepare data
data = pd.read_csv("./data/BTC-USD.csv", index_col="Date", parse_dates=True)
data["Close"] = pd.to_numeric(data["Close"].replace(",","", regex=True))

diff_data = data["Close"].diff().dropna()

# Split data into train and test sets

train_data, test_data = diff_data[:int(len(diff_data)*0.9)], diff_data[int(len(diff_data)*0.9):]

# Train ESM model
esm_model = ExponentialSmoothing(train_data, seasonal='add', trend="add", seasonal_periods=7).fit()

# Forecast using ESM model
esm_forecast = esm_model.forecast(7)

print(esm_forecast)
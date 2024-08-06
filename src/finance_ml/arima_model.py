import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Load and prepare data
data = pd.read_csv("./data/BTC-USD.csv", index_col="Date", parse_dates=True)
data["Close"] = pd.to_numeric(data["Close"].replace(",","", regex=True))

# Plot original data
plt.figure(figsize=(12,6))
plt.plot(data["Close"])
plt.title("BTC-USD Closing Price")
plt.xlabel("Date")
plt.ylabel("Price in USD")
plt.show()

# Difference the data
diff_data = data["Close"].diff().dropna()

# Plot differenced data
plt.figure(figsize=(12,6))
plt.plot(diff_data)
plt.title("Differenced BTC-USD Closing Price")
plt.xlabel("Date")
plt.ylabel("Price Difference")
plt.show()

# Split data into train and test sets
train_data, test_data = diff_data[:int(len(diff_data)*0.9)], diff_data[int(len(diff_data)*0.9):]

# Auto ARIMA to find the best parameters
model_autoARIMA = auto_arima(train_data, start_p=1, start_q=1,
                             test='adf',
                             max_p=5, max_q=5,
                             m=7,  # Weekly seasonality
                             d=None,
                             seasonal=True,
                             start_P=0, 
                             D=1, 
                             trace=True,
                             error_action='ignore',  
                             suppress_warnings=True, 
                             stepwise=True)

print(model_autoARIMA.summary())

# Get the order and seasonal order from the auto_arima model
order = model_autoARIMA.order
seasonal_order = model_autoARIMA.seasonal_order
print(f"Best SARIMAX order: {order}")
print(f"Best SARIMAX seasonal order: {seasonal_order}")

# Build SARIMAX model with the best order
model = SARIMAX(train_data, order=order, seasonal_order=seasonal_order)
results = model.fit()
print(results.summary())

# Forecast
fc = results.get_forecast(steps=len(test_data))
fc_mean = fc.predicted_mean

# Plot the forecast (differenced data)
plt.figure(figsize=(12,6))
plt.plot(train_data.index, train_data, label='Training Data')
plt.plot(test_data.index, test_data, color='blue', label='Actual Difference')
plt.plot(test_data.index, fc_mean, color='red', label='Predicted Difference')
plt.title('BTC-USD Price Difference Prediction')
plt.xlabel('Date')
plt.ylabel('Price Difference')
plt.legend(loc='upper left')
plt.show()

# Cumulative sum to get back to original scale
fc_cumsum = fc_mean.cumsum()
actual_cumsum = test_data.cumsum()

# Add the last training data point to get back to the original scale
last_train_value = data['Close'].iloc[len(train_data)]
fc_forecast = last_train_value + fc_cumsum
actual_forecast = last_train_value + actual_cumsum

# Plot the forecast in original scale
plt.figure(figsize=(12,6))
plt.plot(data['Close'][:len(train_data)], label='Training Data')
plt.plot(actual_forecast.index, actual_forecast, color='blue', label='Actual Price')
plt.plot(fc_forecast.index, fc_forecast, color='red', label='Predicted Price')
plt.title('BTC-USD Price Prediction')
plt.xlabel('Date')
plt.ylabel('Price in USD')
plt.legend(loc='upper left')
plt.show()

# Evaluate model performance
mse = mean_squared_error(actual_forecast, fc_forecast)
mae = mean_absolute_error(actual_forecast, fc_forecast)
rmse = np.sqrt(mse)
mape = np.mean(np.abs((actual_forecast - fc_forecast) / actual_forecast)) * 100

print('Mean Squared Error (MSE): {:.3f}'.format(mse))
print('Mean Absolute Error (MAE): {:.3f}'.format(mae))
print('Root Mean Squared Error (RMSE): {:.3f}'.format(rmse))
print('Mean Absolute Percentage Error (MAPE): {:.3f}%'.format(mape))
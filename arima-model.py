import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error

data = pd.read_csv("./data/SP.csv")
data["Date"] = pd.to_datetime(data["Date"])

# Remove any commas on the Highs column
data["High"]= data["High"].replace(",","", regex=True)
data["High"] = pd.to_numeric(data["High"])
data.set_index('Date', inplace = True)
plt.plot(data["High"])
plt.title("S&P Trend")
plt.xlabel("Date")
plt.ylabel("Price in USD")
#print(data["High"])
#plt.show()

adf_test = adfuller(data["High"])
print('ADF Statistic: %f' % adf_test[0])
print('p-value: %f' % adf_test[1])
#plot_pacf(data["High"], lags=40)
#plot_acf(data["High"], lags=40)
#plt.show()

# ARIMA Model Building
model = ARIMA(data["High"], order=(1,0,1))
model_fit = model.fit()
forecast = model_fit.get_forecast(steps=30)

# Model evaluation

# Train and test data
train_size = int(len(data) *0.8)
train, test = data[0:train_size], data[train_size:len(data)]
test["High"].to_csv("SPtest.csv")

# Fit ARIMA model onto the training dataset
model_train = ARIMA(train["High"], order= (1,0,1))
model_train_fit = model_train.fit()

# Forecast on the test dataset
test_forecast = model_train_fit.get_forecast(steps=len(test))
test_forecast_series = pd.Series(test_forecast.predicted_mean, index = test.index)

# Calculate the mean squared error
mse = mean_squared_error(test["High"], test_forecast_series)
rmse = mse**0.5

# Plot to compare forecast with the actual test data
plt.figure(figsize=(14,7))
plt.plot(train["High"], label="Training Data")
plt.plot(test["High"], label="Actual Data", color = "orange")
plt.plot(test_forecast_series, label="Forecasted Data", color="green")
plt.fill_between(test.index, 
                 test_forecast.conf_int().iloc[:, 0], 
                 test_forecast.conf_int().iloc[:, 1], 
                 color='k', alpha=.15)
plt.title('ARIMA Model Evaluation')
plt.xlabel('Date')
plt.ylabel('Price / USD')
plt.legend()
plt.show()

print("RMSE: ", rmse )
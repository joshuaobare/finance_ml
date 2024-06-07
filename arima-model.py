import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error

data = pd.read_csv("./data/SP.csv",index_col="Date")
data.fillna(0)
data = data[:(int(.3 * len(data)))]
print(data)
data.index = pd.to_datetime(data.index, format="%b %d, %Y")

# Remove any commas on the Highs column
data["High"] = data["High"].replace(",","", regex=True)
data["High"] = pd.to_numeric(data["High"])
#print(data["High"])

plt.plot(data["High"])
plt.title("S&P Trend")
plt.xlabel("Date")
plt.ylabel("Price in USD")
#print(data["High"])
plt.show()

def test_stationarity(timeseries):
    #Determing rolling statistics
    rolmean = timeseries.rolling(12).mean()
    rolstd = timeseries.rolling(12).std()
    #Plot rolling statistics:
    plt.plot(timeseries, color='blue',label='Original')
    plt.plot(rolmean, color='red', label='Rolling Mean')
    plt.plot(rolstd, color='black', label = 'Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean and Standard Deviation')
    plt.show()
    print("Results of dickey fuller test")
    adft = adfuller(timeseries,autolag='AIC')
    # output for dft will give us without defining what the values are.
    #hence we manually write what values does it explains using a for loop
    output = pd.Series(adft[0:4],index=['Test Statistics','p-value','No. of lags used','Number of observations used'])
    for key,values in adft[4].items():
        output['critical value (%s)'%key] =  values
    print(output)
test_stationarity(data["High"])















































'''
adf_test = adfuller(data["High"])
print('ADF Statistic: %f' % adf_test[0])
print('p-value: %f' % adf_test[1])
plot_pacf(data["High"], lags=40)
plot_acf(data["High"], lags=40)
plt.show()

# ARIMA Model Building
model = ARIMA(data["High"], order=(1,0,1))
model_fit = model.fit()
forecast = model_fit.get_forecast(steps=30)

# Model evaluation

# Train and test data
train_size = int(len(data) *0.8)
train, test = data[0:train_size], data[train_size:len(data)]

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
'''
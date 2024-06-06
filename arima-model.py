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
#plt.show()

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

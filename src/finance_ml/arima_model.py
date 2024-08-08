import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import timedelta
import pickle


def generate_arima_model(series_name):
    # Load and prepare data
    data = pd.read_csv(f"./data/{series_name}.csv",
                       index_col="Date", parse_dates=True)
    data["Close"] = pd.to_numeric(data["Close"].replace(",", "", regex=True))

    # Difference the data
    diff_data = data["Close"].diff().dropna()

    # Split data into train and test sets
    train_data, test_data = diff_data[:int(
        len(diff_data)*0.9)], diff_data[int(len(diff_data)*0.9):]

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

    # Cumulative sum to get back to original scale
    fc_cumsum = fc_mean.cumsum()
    actual_cumsum = test_data.cumsum()

    # Add the last training data point to get back to the original scale
    last_train_value = data['Close'].iloc[len(train_data)]
    fc_forecast = last_train_value + fc_cumsum
    actual_forecast = last_train_value + actual_cumsum

    # Evaluate model performance
    mse = mean_squared_error(actual_forecast, fc_forecast)
    mae = mean_absolute_error(actual_forecast, fc_forecast)
    rmse = np.sqrt(mse)
    mape = np.mean(
        np.abs((actual_forecast - fc_forecast) / actual_forecast)) * 100

    print('Mean Squared Error (MSE): {:.3f}'.format(mse))
    print('Mean Absolute Error (MAE): {:.3f}'.format(mae))
    print('Root Mean Squared Error (RMSE): {:.3f}'.format(rmse))
    print('Mean Absolute Percentage Error (MAPE): {:.3f}%'.format(mape))

    # Get the last date in your dataset
    last_date = data.index[-1]

    # Create a date range for the next day
    future_dates = pd.date_range(
        start=last_date + timedelta(days=1), periods=1)

    # Forecast the differenced value for the next day
    forecast = results.get_forecast(steps=1)
    forecast_mean = forecast.predicted_mean

    # To get the actual price prediction, we need to "undo" the differencing
    # First, get the last actual closing price
    last_price = data['Close'].iloc[-1]

    # Add the forecasted difference to the last price
    next_day_price = last_price + forecast_mean.values[0]

    # Create a DataFrame with the prediction
    prediction_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted_Close': next_day_price
    })

    prediction_df.set_index('Date', inplace=True)

    print(prediction_df)

    # If you want to see the confidence interval of the prediction
    forecast_ci = forecast.conf_int()
    lower_bound = last_price + forecast_ci.iloc[0, 0]
    upper_bound = last_price + forecast_ci.iloc[0, 1]

    print(f"Prediction interval: [{lower_bound:.2f}, {upper_bound:.2f}]")

    plt.figure(figsize=(12, 6))
    plt.plot(data['Close'], label='Historical Close Price')
    plt.plot(prediction_df, color='red', marker='o',
             label='Predicted Close Price')
    plt.title(f'{series_name} Close Price Prediction')
    plt.xlabel('Date')
    plt.ylabel('Price in USD')
    plt.legend()
    plt.show()

    with open(f'src\\finance_ml\\models\\{series_name}.pkl', 'wb') as file:
        pickle.dump(results, file)

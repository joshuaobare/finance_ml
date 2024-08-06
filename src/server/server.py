from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import timedelta
import pickle

# Load your data and model
with open('arima_model.pkl', 'rb') as file:
    model = pickle.load(file)

data = pd.read_csv("./data/ETH-USD.csv", index_col="Date", parse_dates=True)
data["Close"] = pd.to_numeric(data["Close"].replace(",", "", regex=True))


def calculate_mape(actual, predicted):
    return np.mean(np.abs((actual - predicted) / actual)) * 100


class PredictionHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        # This allows CORS for all domains
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        if self.path == '/predict':
            # Get the last date in your dataset
            last_date = data.index[-1]

            # Create a date range for the next day
            future_dates = pd.date_range(
                start=last_date + timedelta(days=1), periods=1)

            # Forecast the differenced value for the next day
            forecast = model.get_forecast(steps=1)
            forecast_mean = forecast.predicted_mean

            # Get the last actual closing price
            last_price = data['Close'].iloc[-1]

            # Add the forecasted difference to the last price
            next_day_price = last_price + forecast_mean.values[0]

            # Get the confidence interval
            forecast_ci = forecast.conf_int()
            lower_bound = last_price + forecast_ci.iloc[0, 0]
            upper_bound = last_price + forecast_ci.iloc[0, 1]

            # Calculate MAPE
            # We'll use the last 30 days for this example
            last_30_days = data['Close'].iloc[-30:]
            last_30_days_forecast = model.get_forecast(steps=30)
            last_30_days_predicted = last_30_days.iloc[0] + \
                last_30_days_forecast.predicted_mean.cumsum()
            mape = calculate_mape(last_30_days.values,
                                  last_30_days_predicted.values)

            # Prepare the response
            response = {
                'date': future_dates[0].strftime('%Y-%m-%d'),
                'predicted_price': float(next_day_price),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                "accuracy": mape
            }

            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)


def run(server_class=HTTPServer, handler_class=PredictionHandler, port=7000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()

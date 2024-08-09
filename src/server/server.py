from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import timedelta
import pickle
from urllib.parse import urlparse, parse_qs
import os


def get_directories():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct paths relative to the current script
    data_path = os.path.join(
        current_dir, '..', 'finance_ml', 'data')

    # Construct paths relative to the current script
    model_path = os.path.join(
        current_dir, '..', 'finance_ml', 'models')

    return data_path, model_path


def load_data(symbol):
    data_path, model_path = get_directories()

    data_path = os.path.join(data_path, f'{symbol}.csv')
    # Load data
    data = pd.read_csv(data_path,
                       index_col="Date", parse_dates=True)
    data['Close'] = pd.to_numeric(data['Close'].replace(",", "", regex=True))

    return data


def load_model(symbol):
    data_path, model_path = get_directories()

    model_path = os.path.join(model_path, f'{symbol}.pkl')
    # Load model
    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    return model


def calculate_mape(actual, predicted):
    return np.mean(np.abs((actual - predicted) / actual)) * 100


def generate_data(symbol, model):
    data = load_data(symbol)
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

    return future_dates, next_day_price, lower_bound, upper_bound, mape


class PredictionHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        def send_cors_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header("Access-Control-Allow-Headers",
                             "X-Requested-With, Content-Type")
        parsed_path = urlparse(self.path)

        path_parts = parsed_path.path.split('/')
        if path_parts[1] == 'predict':
            # Extract symbol from the path
            symbol = None
            for part in path_parts[2:]:
                if part.startswith('symbol='):
                    symbol = part.split('=')[1]
                    break

            if not symbol:
                self.send_error(400, "Missing 'symbol' parameter")
                return

            data = load_data(symbol)

            dataset_dates = data.index.values.tolist()
            # Convert to pandas datetime
            dataset_dates = pd.to_datetime(dataset_dates, unit='ns')

            # Convert to list of strings in ISO format
            dataset_dates = dataset_dates.strftime('%Y-%m-%d').tolist()

            models_available = set(os.listdir(get_directories()[1]))

            if f"{symbol}.pkl" in models_available:
                model = load_model(symbol)

                future_dates, next_day_price, lower_bound, upper_bound, mape = generate_data(
                    symbol, model)

                # Prepare the response
                response = {
                    'data': {"dates": dataset_dates, "data": data['Close'].values.tolist()},
                    'date': future_dates[0].strftime('%Y-%m-%d'),
                    "latest_price": data['Close'].iloc[-1],
                    'predicted_price': float(next_day_price),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    "price_difference": float(next_day_price) - data['Close'].iloc[-1],
                    "accuracy": mape,
                    "verdict": "SELL" if float(next_day_price) - data['Close'].iloc[-1] < 0 else "BUY"
                }

            else:
                # Prepare the response
                response = {
                    'data': {"dates": dataset_dates, "data": data['Close'].values.tolist()},
                    'alert': "Model unavailable"
                }

            self.send_response(200)
            send_cors_headers(self)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)


def run(server_class=HTTPServer, handler_class=PredictionHandler, port=7000):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()

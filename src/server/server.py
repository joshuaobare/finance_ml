from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import timedelta
import pickle
from urllib.parse import urlparse, parse_qs
import os


def load_model(symbol):
        # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct paths relative to the current script
    model_path = os.path.join(current_dir, '..', 'finance_ml', 'models', f'{symbol}.pkl')
    data_path = os.path.join(current_dir, '..', 'finance_ml', 'data', f'{symbol}.csv')
    # Load your data and model
    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    data = pd.read_csv(data_path,
                       index_col="Date", parse_dates=True)

    return model, data


def calculate_mape(actual, predicted):
    return np.mean(np.abs((actual - predicted) / actual)) * 100


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
            self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        parsed_path = urlparse(self.path)
        print(parsed_path)
        path_parts = parsed_path.path.split('/')
        if path_parts[1] == 'predict':
            # Extract symbol from the path
            symbol = None
            for part in path_parts[2:]:
                if part.startswith('symbol='):
                    symbol = part.split('=')[1]
                    break

            model, data = load_model(symbol)
            data["Close"] = pd.to_numeric(data["Close"].replace(",", "", regex=True))

            if not symbol:
                self.send_error(400, "Missing 'symbol' parameter")
                return
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
                'data':{"dates":data["Date"], "data":data},
                'date': future_dates[0].strftime('%Y-%m-%d'),
                'predicted_price': float(next_day_price),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                "accuracy": mape
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

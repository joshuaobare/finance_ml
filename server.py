import http.server
import socketserver
import pickle 
import json
from urllib.parse import parse_qs


with open("arima_model.pkl", "rb") as f:
    arima_model = pickle.load(f)

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        features = data.get('features', [])
        print(dir(arima_model))
        prediction = pickle.load(open('arima_model.pkl', 'rb'))
        results = prediction.fit()
        full_results = results.get_forecast(steps=1).predicted_mean.iloc[0]

        response = {
            'prediction': full_results
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow all origins
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')  # Allow POST and OPTIONS methods
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')  # Allow specific headers
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

PORT = 8080

with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
    print(f"Serving aat port {PORT}")
    httpd.serve_forever()
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import csv
import os
from datetime import datetime, timedelta
import time
import random


class Scraper:
    def __init__(self, symbol, title):
        self.symbol = symbol
        self.title = title
        self.header = ['Date', 'Open', 'High',
                       'Low', 'Close', 'Adj Close', 'Volume']
        self.all_data = []
        self.start_date = None
        self.end_date = int(time.time())
        self.session = self.create_session()
        self.find_start_date()
        self.fetch_data()
        self.write_to_file()

    def find_start_date(self):
        file_path = f"src\\finance_ml\\data\\{self.title}.csv"
        if not os.path.isfile(file_path):
            self.start_date = 0  # Default to earliest possible date
            return

        with open(file_path, "r", encoding="utf-8", newline="") as file:
            final_line = file.readlines()[-1]
            last_date = final_line.split(",")[0]
            print(last_date)
            last_date = datetime.strptime(last_date, "%Y-%m-%d")
            self.start_date = int(time.mktime(
                (last_date + timedelta(days=1)).timetuple()))

    def create_session(self):
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1,
                        status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('https://', adapter)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        return session

    def fetch_data(self):
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{
            self.symbol}"
        params = {
            "period1": self.start_date,
            "period2": self.end_date,
            "interval": "1d",
            "events": "history",
            "includeAdjustedClose": "true"
        }

        try:
            response = self.session.get(url, params=params)
            print(response)
            response.raise_for_status()

            lines = response.text.strip().split("\n")
            for line in lines[2:]:  # Skip header and prev last date
                print(line)
                row = line.split(",")
                self.all_data.append(row)

            # Add a delay between requests
            time.sleep(random.uniform(1, 3))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {self.symbol}: {e}")

    def write_to_file(self):
        file_path = f'src\\finance_ml\\data\\{self.title}.csv'
        mode = "w" if not self.start_date else "a"

        with open(file_path, mode, encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            if mode == "w":
                writer.writerow(self.header)
            else:
                writer.writerow([])
            writer.writerows(self.all_data)


if __name__ == '__main__':
    symbols_and_titles = {
        "%5EGSPC": "SPY-USD",
        "BTC-USD": "BTC-USD",
        "ETH-USD": "ETH-USD",
        "GC=F": "GLD-USD",
        "CL=F": "USO-USD"
    }

    for symbol, title in symbols_and_titles.items():
        Scraper(symbol, title)

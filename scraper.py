from selenium import webdriver
from selenium.webdriver.common.by import By
from xpaths import XPATHS
import csv, os

class Scraper:
    def __init__(self, url):
        self.browser = webdriver.Firefox()
        self.url = url
        self.header = ['Date',	'Open',	'High',	'Low',	'Close*',	'Adj Close**',	'Volume']
        self.all_data = []
        self.start_date = None
        self.find_start_date()
        self.fetch_data()
        self.write_to_file()

    def find_start_date(self):
        file_name = self.url.split("/")[4]
        file_path = f"./data/{file_name}.csv"

        # check if file exists
        if not os.path.isfile(file_path):
            return

        with open(file_path, "r", encoding="utf-8", newline="") as file:
            final_line = file.readlines()[-1]
            self.start_date = final_line.split(",")[0]

    def fetch_data(self):
        self.browser.get(self.url)
        arrow_btn = self.browser.find_element(
            By.XPATH, XPATHS["arrow_btn"])
        arrow_btn.click()
        max_btn = self.browser.find_element(
            By.XPATH, XPATHS["max_btn"])
        max_btn.click()
        done_btn = self.browser.find_element(By.XPATH, XPATHS["done_btn"])
        done_btn.click()

        table_row = 1
        start_height = 0

        while True:
            self.browser.execute_script(
                f"window.scrollTo({start_height}, document.documentElement.scrollHeight);")
            try:
                curr_row = self.browser.find_element(
                    By.XPATH, XPATHS["curr_row"] + f'{table_row}]')
                table_cells = curr_row.find_elements(By.TAG_NAME, 'td')
                row_data = []
                for table_cell in table_cells:
                    row_data.append(table_cell.get_attribute('textContent'))
                self.all_data.append(row_data)
                print(table_row)
            except:
                break
            table_row += 1
            start_height = self.browser.execute_script(
                'return document.documentElement.scrollHeight')

    def write_to_file(self):
        page_title = self.browser.title
        with open(f'./data/{page_title[:2]}.csv', "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.header)
            for data_row in self.all_data:
                writer.writerow(data_row)


sp_url = "https://finance.yahoo.com/quote/%5EGSPC/history?period1=-1325635200&period2=1709510400&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
btc_url = "https://finance.yahoo.com/quote/BTC-USD/history?period1=1410912000&period2=1709856000&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
gold_url = "https://finance.yahoo.com/quote/GC%3DF/history"
eth_url = "https://finance.yahoo.com/quote/ETH-USD/history"
crude_url = "https://finance.yahoo.com/quote/CL%3DF/history"
sp_data = Scraper(sp_url)
btc_data = Scraper("https://finance.yahoo.com/quote/BTC-USD/history/")
'''eth_data = Scraper(eth_url)
crude_data = Scraper(crude_url)'''





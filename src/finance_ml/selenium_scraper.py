from selenium import webdriver
from selenium.webdriver.common.by import By
from xpaths import XPATHS
import csv
import os
from time import sleep
from datetime import datetime


class Scraper:
    def __init__(self, url, title):
        self.browser = webdriver.Firefox()
        self.url = url
        self.title = title
        self.header = ['Date',	'Open',	'High',
                       'Low',	'Close',	'Adj Close',	'Volume']
        self.all_data = []
        self.start_date = None
        self.find_start_date()
        self.fetch_data()
        self.write_to_file()
        self.browser.close()

    def find_start_date(self):
        """
        Find the last recorded date in the existing CSV file, if any.
        """
        file_path = f"src\\finance_ml\\data\\{self.title}.csv"
        print(file_path)
        # check if file exists
        if not os.path.isfile(file_path):
            return

        with open(file_path, "r", encoding="utf-8", newline="") as file:
            final_line = file.readlines()[-1]
            self.start_date = final_line.split(",")[0]

    def fetch_data(self):
        self.browser.get(self.url)
        sleep(5)
        arrow_btn = self.browser.find_element(
            By.XPATH, XPATHS["arrow_btn"])
        arrow_btn.click()
        max_btn = self.browser.find_element(
            By.XPATH, XPATHS["max_btn"])
        max_btn.click()
        sleep(5)

        table_row = 1
        start_height = 0

        while True:
            self.browser.execute_script(
                f"window.scrollTo({start_height}, document.documentElement.scrollHeight);")
            try:
                curr_row = self.browser.find_element(
                    By.XPATH, XPATHS["curr_row"] + f'{table_row}]')
                table_cells = curr_row.find_elements(By.TAG_NAME, 'td')
                break_flag = False
                row_data = []

                for cell_idx in range(len(table_cells)):
                    cell_data = table_cells[cell_idx]
                    cell_data = cell_data.get_attribute('textContent')

                    if cell_idx == 0:
                        date_obj = datetime.strptime(cell_data, "%b %d, %Y")
                        cell_data = date_obj.strftime("%Y-%m-%d")
                        print(cell_data)

                    if self.start_date and cell_data == self.start_date:
                        break_flag = True
                        break
                    row_data.append(cell_data)

                if break_flag:
                    break

                self.all_data.append(row_data)
            except:
                break
            table_row += 1
            start_height = self.browser.execute_script(
                'return document.documentElement.scrollHeight')

    def write_to_file(self):
        """
        Write the collected data to a CSV file.
        """
        page_title = self.title
        with open(f'src\\finance_ml\\data\\{self.title}.csv', "a+", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)

            if not self.start_date:
                writer.writerow(self.header)
            else:
                writer.writerow([])
            all_data_length = len(self.all_data)

            for data_row_idx in range(all_data_length - 1, - 1, -1):
                writer.writerow(self.all_data[data_row_idx])


if __name__ == '__main__':
    urls_and_titles = {
        # "https://finance.yahoo.com/quote/%5EGSPC/history": "SPY-USD",
        "https://finance.yahoo.com/quote/BTC-USD/history": "BTC-USD",
        "https://finance.yahoo.com/quote/ETH-USD/history": "ETH-USD",
        "https://finance.yahoo.com/quote/GC%3DF/history": "GLD-USD",
        "https://finance.yahoo.com/quote/CL%3DF/history": "USO-USD"
    }

    for url, title in urls_and_titles.items():
        Scraper(url, title)

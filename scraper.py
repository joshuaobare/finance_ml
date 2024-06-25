from selenium import webdriver
from selenium.webdriver.common.by import By
import csv

class Scraper:
    def __init__(self, url):
        self.browser = webdriver.Firefox()
        self.url = url
        self.header = ['Date',	'Open',	'High',	'Low',	'Close*',	'Adj Close**',	'Volume']
        self.all_data = []
        self.start_date = None
        self.find_start_date()
        self.fetchData()
        self.write_to_file()

    def find_start_date(self):
        file_name = self.url.split("/")[4]

        with open(f"./data/{file_name}.csv", "r", encoding="utf-8", newline="") as file:
            final_line = file.readlines()[-1]
            self.start_date = final_line.split(",")[0]

    def fetchData(self):
        self.browser.get(self.url)
        arrowBtn = self.browser.find_element(
            By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/div[1]/div[1]/div[1]/button')
        arrowBtn.click()
        maxBtn = self.browser.find_element(
            By.XPATH, '/html/body/div[1]/main/section/section/section/article/div[1]/div[1]/div[1]/div/div/div[2]/section/div[1]/button[8]')
        maxBtn.click()
        doneBtn = self.browser.find_element(By.XPATH, '//*[@id="menu-50"]/div[2]/section/div[3]/button[1]')
        doneBtn.click()

        table_row = 1
        start_height = 0

        while True:
            self.browser.execute_script(
                f"window.scrollTo({start_height}, document.documentElement.scrollHeight);")
            try:
                curr_row = self.browser.find_element(
                    By.XPATH, f'//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr[{table_row}]')
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





from selenium import webdriver
from selenium.webdriver.common.by import By
import csv

browser = webdriver.Firefox()
url = "https://finance.yahoo.com/quote/%5EGSPC/history?period1=-1325635200&period2=1709510400&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
browser.get(url)
arrowBtn = browser.find_element(
    By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div')
arrowBtn.click()
maxBtn = browser.find_element(
    By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[1]/div[1]/div[1]/div/div/div[2]/div/ul[2]/li[4]/button')
maxBtn.click()

header = ['Date',	'Open',	'High',	'Low',	'Close*',	'Adj Close**',	'Volume']
all_data = []
table_row = 1
start_height = 0

while table_row < 100:
    browser.execute_script(
        f"window.scrollTo({start_height}, document.documentElement.scrollHeight);")
    try:
        curr_row = browser.find_element(
            By.XPATH, f'//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr[{table_row}]')
        table_cells = curr_row.find_elements(By.TAG_NAME, 'td')
        row_data = []
        for table_cell in table_cells:
            row_data.append(table_cell.get_attribute('textContent'))
        all_data.append(row_data)
        print(table_row)
    except:
        break
    table_row += 1
    start_height = browser.execute_script(
        'return document.documentElement.scrollHeight')


with open('./data/SP.csv', "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(header)
    for x in all_data:
        writer.writerow(x)

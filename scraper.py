from selenium import webdriver
from selenium.webdriver.common.by import By

browser = webdriver.Firefox()
url = "https://finance.yahoo.com/quote/%5EGSPC/history?period1=-1325635200&period2=1709510400&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
browser.get(url)
arrowBtn = browser.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div')
arrowBtn.click()
maxBtn = browser.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[1]/div[1]/div[1]/div/div/div[2]/div/ul[2]/li[4]/button')
maxBtn.click()
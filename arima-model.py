import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("./data/SP.csv")
data["Date"] = pd.to_datetime(data["Date"])

# Remove any commas on the Highs column
data["High"]= data["High"].replace(",","", regex=True)
data["High"] = pd.to_numeric(data["High"])
data.set_index('Date', inplace = True)
plt.plot(data["High"])
plt.title("S&P Trend")
plt.xlabel("Date")
plt.ylabel("Price in USD")
plt.show()

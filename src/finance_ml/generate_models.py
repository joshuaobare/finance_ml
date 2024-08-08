from arima_model import generate_arima_model


def main():
    symbols = ["SPY-USD",
               "BTC-USD",
               "ETH-USD",
               "GLD-USD",
               "USO-USD"]

    for symbol in symbols:
        generate_arima_model(symbol)


if __name__ == '__main__':
    main()

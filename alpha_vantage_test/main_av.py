from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from config_av import API_KEY

def get_intraday_data(symbol: str, interval: str = "60min", output_size: str = "compact"):
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    data, meta = ts.get_intraday(symbol=symbol, interval=interval, outputsize=output_size)
    return data

def main():
    symbol = input("Welche Aktie möchtest du analysieren? (z.B. AAPL, MSFT, TSLA): ").upper()

    try:
        df = get_intraday_data(symbol)
        df = df[['1. open', '4. close']].head(10)  # Nur Open/Close der letzten 10 Einträge

        print(f"\n Stündliche Open/Close-Daten für {symbol}:\n")
        print(df)
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    main()


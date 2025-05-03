from alpha_vantage_api import get_intraday

def main():
    symbol = input("Welche Aktie möchtest du analysieren? (z. B. AAPL, MSFT, TSLA): ").upper()

    try:
        data = get_intraday(symbol)
        time_series_key = next(k for k in data.keys() if "Time Series" in k)

        print(f"\n Stündliche Open/Close-Daten für {symbol}:\n")
        for time, values in list(data[time_series_key].items())[:10]:  # Zeige die letzten 10 Stunden
            print(f"{time} → Open: {values['1. open']}, Close: {values['4. close']}")
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    main()

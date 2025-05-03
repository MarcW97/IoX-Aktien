from stock_data_yfinance import get_intraday_data_yf

def main():
    symbol = input("Welche Aktie möchtest du analysieren? (z. B. AAPL, MSFT, TSLA): ").upper()

    df = get_intraday_data_yf(symbol)

    if not df.empty:
        print(f"\n Stündliche Open/Close-Daten für {symbol} (letzte 5 Tage):\n")
        print(df.tail(10))  # letzte 10 Einträge anzeigen
    else:
        print("Keine Daten geladen.")

if __name__ == "__main__":
    main()

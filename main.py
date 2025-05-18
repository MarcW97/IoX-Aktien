from stock_data_yfinance import get_intraday_data_yf, get_key_metrics, get_1y_history

def main():
    symbol = input("Welche Aktie möchtest du analysieren? (z.B. AAPL, MSFT, TSLA): ").upper()

    # 1. Fundamentaldaten
    metrics = get_key_metrics(symbol)
    if metrics:
        print(f"\n Fundamentaldaten für {symbol}:\n")
        for key, value in metrics.items():
            print(f"{key}: {value}")
    else:
        print("Keine Fundamentaldaten geladen.")

    # 2. Kursverlauf letztes Jahr
    df_year = get_1y_history(symbol)
    if df_year is not None:
        print(f"\n Kursverlauf (Schlusskurs) für {symbol} – letztes Jahr:\n")
        print(df_year.tail(10))  # letzte 10 Einträge anzeigen
    else:
        print("Keine Kursverlaufsdaten gefunden.")

    # 3. Intraday-Daten
    df_intraday = get_intraday_data_yf(symbol)
    if not df_intraday.empty:
        print(f"\n Intraday Open/Close-Daten für {symbol} (letzte 1 Tag):\n")
        print(df_intraday.tail(10))
    else:
        print("Keine Intraday-Daten geladen.")

if __name__ == "__main__":
    main()
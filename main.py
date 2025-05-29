from db.connection import connect
from db.persistence import save_stock_basic, insert_fundamentals, insert_prices, clear_old_data, is_valid_symbol
from stock_data_yfinance import get_key_metrics, get_1y_history, get_basic_data

def run_data_pipeline(symbol: str):
    conn = connect()

    # 1. Stock-Basisdaten
    basic_data = get_basic_data(symbol)
    save_stock_basic(conn, symbol, basic_data.get("name"), basic_data.get("sector"), basic_data.get("industry"))

    # 2. Fundamentaldaten
    fundamentals = get_key_metrics(symbol)
    if fundamentals:
        insert_fundamentals(conn, symbol, fundamentals)
        print("Fundamentaldaten gespeichert.")

    # 3. Kursverlauf 1 Jahr
    df = get_1y_history(symbol)
    if df is not None:
        insert_prices(conn, symbol, df)
        print("Kursdaten gespeichert.")

    conn.close()

def main():
    symbols = []

    for i in range(2):
        while True:
            symbol = input(f"Aktie {i + 1} eingeben (z.B. AAPL, TSLA): ").upper()
            if is_valid_symbol(symbol):
                symbols.append(symbol)
                break
            else:
                print("Symbol ungültig oder nicht gefunden. Bitte erneut eingeben.")

    conn = connect()
    clear_old_data(conn)
    conn.close()

    for symbol in symbols:
        print(f"\n→ Starte Analyse für {symbol}")
        run_data_pipeline(symbol)

if __name__ == "__main__":
    main()
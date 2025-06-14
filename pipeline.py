# pipeline.py
from db.connection import connect
from db.persistence import clear_old_data, save_stock_basic, insert_fundamentals, insert_prices, is_valid_symbol
from stock_data_yfinance import get_fundamentals, get_1y_history, get_basic_data
import yfinance as yf

def run_data_pipeline(conn, symbol: str):
    if not is_valid_symbol(symbol):
        raise ValueError(f"'{symbol}' ist kein gültiges oder unterstütztes Symbol.")

    # Kursdaten vorab laden
    df = get_1y_history(symbol)
    if df is None:
        raise ValueError(f"Keine Kursdaten für {symbol} gefunden.")

    fundamentals_data = get_fundamentals(symbol)
    basic_data = get_basic_data(symbol)

    insert_prices(conn, symbol, df)
    insert_fundamentals(conn, symbol, fundamentals_data)
    save_stock_basic(
        conn,
        symbol,
        name=basic_data.get("name"),
        sector=basic_data.get("sector"),
        industry=basic_data.get("industry")
    )
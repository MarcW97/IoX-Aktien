# db/persistence.py
# schreiben in die Datenbank

import pandas as pd
import yfinance as yf
from .connection import connect

def save_stock_basic(conn, symbol, name=None, sector=None, industry=None):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO stocks (symbol, name, sector, industry)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (symbol) DO NOTHING;
    """, (symbol, name, sector, industry))
    conn.commit()

def insert_fundamentals(conn, symbol, data):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO fundamentals (
            stock_symbol, market_cap, enterprise_value, revenue, ebitda,
            pe_ratio, dividend_yield, dividend_per_share, beta
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (
        symbol,
        data.get("Marktkapitalisierung (Market Cap)"),
        data.get("Unternehmenswert (Enterprise Value)"),
        data.get("Umsatz (Revenue)"),
        data.get("EBITDA"),
        data.get("KGV (PE Ratio)"),
        data.get("Dividendenrendite (%)"),
        data.get("Dividende je Aktie"),
        data.get("Beta")
    ))
    conn.commit()

def insert_prices(conn, symbol, df):
    cur = conn.cursor()
    for date, row in df.iterrows():
        cur.execute("""
            INSERT INTO prices_daily (
                stock_symbol, date, open, high, low, close, volume
            ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (
            symbol,
            date.date(),
            float_or_none(row.get("Open")),
            float_or_none(row.get("High")),
            float_or_none(row.get("Low")),
            float_or_none(row.get("Close")),
            int(row.get("Volume")) if not pd.isna(row.get("Volume")) else None
        ))
    conn.commit()

def clear_old_data(conn):
    cur = conn.cursor()
    cur.execute("DELETE FROM prices_daily;")
    cur.execute("DELETE FROM fundamentals;")
    conn.commit()

def float_or_none(value):
    return float(value) if pd.notna(value) else None

def is_valid_symbol(symbol: str) -> bool:
    """
    Prüft, ob das eingegebene Symbol gültig ist (d.h. Daten existieren bei yfinance).
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return bool(info and "longName" in info)
    except Exception:
        return False

def get_symbol_name_mapping(conn):
    cur = conn.cursor()
    cur.execute("SELECT symbol, name FROM stocks;")
    rows = cur.fetchall()
    return {symbol: name for symbol, name in rows if name}

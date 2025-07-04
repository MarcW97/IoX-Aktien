import yfinance as yf
import pandas as pd

def get_basic_data(symbol: str):
    """
    Gets name, sector, industry from yfinance.
    """
    try:
        info = yf.Ticker(symbol).get_info()
        return {
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry")
        }
    except Exception as e:
        print(f"Fehler beim Abrufen der Basisdaten: {e}")
        return {}


def get_fundamentals(symbol: str):
    """
    Gets central fundamental data from yfinance.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.get_info()

        if not info:
            raise Exception("Keine Info-Daten verfügbar.")

        return {
            "Marktkapitalisierung (Market Cap)": info.get("marketCap"),
            "Unternehmenswert (Enterprise Value)": info.get("enterpriseValue"),
            "Umsatz (Revenue)": info.get("totalRevenue"),
            "EBITDA": info.get("ebitda"),
            "KGV (PE Ratio)": info.get("trailingPE"),
            "Dividendenrendite (%)": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else None,
            "Dividende je Aktie": info.get("dividendRate"),
            "Beta": info.get("beta"),
        }

    except Exception as e:
        print(f"Fehler beim Abrufen der Fundamentaldaten: {e}")
        return {}

def get_1y_history(symbol: str):
    """
    Get daily price data for last year from yfinance
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1y", interval="1d")  # täglicher Kursverlauf über 1 Jahr

    if df.empty:
        print(f"Keine Kursdaten gefunden für {symbol}.")
        return None

    # Stelle sicher, dass alle erwarteten Spalten vorhanden sind
    return df[["Open", "High", "Low", "Close", "Volume"]].copy()


import yfinance as yf
import pandas as pd

def get_key_metrics(symbol: str):
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
    Get close event data for last year from yfinance
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1y", interval="1d")  # täglicher Kursverlauf über 1 Jahr

    if df.empty:
        print("Keine Daten gefunden.")
        return None

    return df[["Close"]]  # oder ["Open", "High", "Low", "Close", "Volume"]

def get_intraday_data_yf(symbol: str, interval: str = "60m", period: str = "1d"):
    """
    Get Intraday-data for 1 Day from yfinance with interval 60m.
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(interval=interval, period=period)

        if df.empty:
            raise Exception("Keine Daten empfangen – Symbol oder Zeitraum ungültig?")

        return df[["Open", "Close"]]

    except Exception as e:
        print(f"Fehler beim Abrufen der Intraday-Daten: {e}")
        return pd.DataFrame()


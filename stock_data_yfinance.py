import yfinance as yf
import pandas as pd

def get_intraday_data_yf(symbol: str, interval: str = "60m", period: str = "5d"):
    """
    Holt Intraday-Daten über yfinance.
    - interval: z. B. "1m", "5m", "15m", "60m", "90m", "1d"
    - period: z. B. "1d", "5d", "1mo", "3mo"
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(interval=interval, period=period)

        if df.empty:
            raise Exception("Keine Daten empfangen – Symbol oder Zeitraum ungültig?")

        return df[["Open", "Close"]]
    except Exception as e:
        print(f"Fehler beim Abrufen der Daten: {e}")
        return pd.DataFrame()

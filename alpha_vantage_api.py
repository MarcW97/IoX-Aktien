# alpha_vantage_api.py
import requests
from config import API_KEY, BASE_URL

def get_intraday(symbol: str, interval: str = "60min", output_size: str = "compact"):
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "outputsize": output_size,
        "apikey": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"API-Anfrage fehlgeschlagen: {response.status_code}")

    data = response.json()

    # DEBUG-Ausgabe bei Problemen
    if not any("Time Series" in key for key in data.keys()):
        print("⚠️ Debug-Ausgabe der API-Antwort:")
        print(data)
        raise Exception(f"Fehler in der Antwort: {data.get('Note') or data.get('Error Message') or 'Unbekannter Fehler'}")

    return data

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from db.connection import connect
from db.persistence import save_stock_basic
from stock_data_yfinance import get_basic_data

# Absoluter Pfad zur symbols.csv
csv_path = os.path.join(os.path.dirname(__file__), "symbols.csv")
# Daten aus der CSV lesen
symbol_list = pd.read_csv(csv_path, header=None)[0].tolist()

# Verbindung zur Datenbank aufbauen
conn = connect()

# Durch alle Symbole iterieren und speichern
for symbol in symbol_list:
    basic_data = get_basic_data(symbol)
    if basic_data:  # Nur wenn Daten vorhanden sind
        save_stock_basic(
            conn,
            symbol=symbol.upper(),
            name=basic_data.get("name"),
            sector=basic_data.get("sector"),
            industry=basic_data.get("industry")
        )
        print(f"{symbol} erfolgreich gespeichert.")
    else:
        print(f"{symbol} übersprungen (keine Daten).")

conn.close()
print("✅ Import abgeschlossen.")

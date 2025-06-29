# IoX-Aktienanalyse-Tool

Teamprojekt der **IoX Coding Start-Up** Vorlesung an der **HTWG Konstanz**.  
Ziel ist der Aufbau eines einfachen, modularen und erweiterbaren **Aktienanalyse-Tools** in Python.

---

## 🔗 API

Datenquelle ist die kostenlose **[yfinance](https://pypi.org/project/yfinance/)** API.

---

## Dashboard ausführen:
python -m streamlit run dashboard_Aktien_v2.py

## Anreichern von Basis Aktiendaten für die Dropdown Liste:
Liste von Aktiensymbolen in die Datei ´symbols.csv´ speichern.
Dann folgendes Skript ausführen:
python db/import_basic_stocks_from_csv.py

## ⚙️ Installation

Benötigte Python-Pakete installieren:

```bash
pip install yfinance
pip install psycopg2-binary
pip install python-dotenv
pip install pandas
pip install streamlit
pip install plotly
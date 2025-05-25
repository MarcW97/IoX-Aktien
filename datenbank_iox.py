import psycopg2
from dotenv import load_dotenv
import os

# .env-Datei laden
load_dotenv()

#Verbindung zur lokalen Datenbank
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=int(os.getenv("DB_PORT"))
)

print("Verbindung erfolgreich")


# Cursor erstellen
cur = conn.cursor()

# Tabelle erstellen (falls nicht vorhanden)
cur.execute("""
CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
""")

# Daten einfügen (NVDA und TSLA)
stocks_data = [
    ("NVDA", "NVIDIA Corporation", 114.50),
    ("TSLA", "Tesla, Inc.", 287.21)
]

# SQL-Query für INSERT
insert_query = "INSERT INTO stocks (symbol, name, price) VALUES (%s, %s, %s);"

# Daten einfügen
for stock in stocks_data:
    cur.execute(insert_query, stock)

# Daten abrufen
cur.execute("SELECT * FROM stocks;")
rows = cur.fetchall()

# Ausgabe
print("Inhalt der Tabelle 'stocks':")
for row in rows:
    print(row)

# Änderungen bestätigen und Verbindung schließen
conn.commit()
conn.close()

print("Daten erfolgreich eingefügt!")




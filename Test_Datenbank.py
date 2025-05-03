import psycopg2

#Verbindung zur lokalen Datenbank

conn = psycopg2.connect(
    dbname="test_aktien",
    user="postgres",
    password="Benjamin13",
    host="localhost",
    port="5432"
)

print("Verbindung erfolgreich")
conn.close()


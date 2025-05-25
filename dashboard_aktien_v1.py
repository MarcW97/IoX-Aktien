import psycopg2
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import time


# --------------------------
# 1. DATENBANKVERBINDUNG (eigenes Modul wäre besser)
# --------------------------
def init_db_connection():
    """Initialisiert und verwaltet die Datenbankverbindung"""
    if 'db_connection' not in st.session_state:
        st.session_state.db_connection = None
    if 'connection_start_time' not in st.session_state:
        st.session_state.connection_start_time = None
    if 'show_success_msg' not in st.session_state:
        st.session_state.show_success_msg = False

    # Verbindungsaufbau
    try:
        if st.session_state.db_connection is None:
            st.session_state.db_connection = psycopg2.connect(
                host=os.getenv("DB_HOST", "aws-0-eu-central-1.pooler.supabase.com"),
                database=os.getenv("DB_NAME", "postgres"),
                user=os.getenv("DB_USER", "postgres.txhiyzcswuftqgazbuan"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT", "6543")
            )
            st.session_state.connection_start_time = time.time()
            st.session_state.show_success_msg = True
            st.rerun()
    except psycopg2.OperationalError as e:
        st.error(f"❌ Verbindungsfehler: {e}")
    except Exception as e:
        st.error(f"❌ Unerwarteter Fehler: {e}")


# --------------------------
# 2. DASHBOARD LAYOUT
# --------------------------
def setup_ui():
    """Setzt das UI-Layout auf"""
    st.set_page_config(page_title="📊 Aktien Dashboard", layout="wide")

    # Header mit Verbindungsbutton
    col1, col2 = st.columns([8, 1])
    with col1:
        st.title("📈 Aktienanalyse Dashboard")
    with col2:
        if st.session_state.db_connection:
            if st.button("Verbinden/\nTrennen"):
                st.session_state.db_connection.close()
                st.session_state.db_connection = None
                st.session_state.show_success_msg = False
                st.session_state.connection_start_time = None
                #st.rerun()

    # Erfolgsmeldung
    if st.session_state.show_success_msg:
        elapsed = time.time() - st.session_state.connection_start_time
        if elapsed < 2:
            msg = st.empty()
            msg.success("✅ Verbindung zur Datenbank erfolgreich")
            time.sleep(2 - elapsed)
            msg.empty()
        st.session_state.show_success_msg = False


# --------------------------
# 3. DATENABFRAGE
# --------------------------
def load_stock_data():
    """Lädt die Aktiendaten aus der DB"""
    try:
        if st.session_state.db_connection:
            query = "SELECT * FROM stocks;"
            return pd.read_sql(query, st.session_state.db_connection)
        return None
    except Exception as e:
        st.error(f"❌ Fehler beim Datenabruf: {e}")
        return None


# --------------------------
# 4. DASHBOARD INHALTE
# --------------------------
def show_dashboard(df):
    """Zeigt das eigentliche Dashboard an"""
    st.markdown("---")

    # 1. Filter-Sektion
    st.subheader("🔍 Aktienfilter")
    symbols = df["symbol"].unique()
    selected_symbols = st.multiselect(
        "Wähle Aktien",
        symbols,
        default=list(symbols)
    )

    # 2. Gefilterte Daten
    filtered_df = df[df["symbol"].isin(selected_symbols)]

    # 3. Datenanzeige
    st.subheader("📋 Aktientabelle")
    st.dataframe(filtered_df)

    # 4. Visualisierungen
    st.subheader("💹 Aktienpreise")
    st.bar_chart(filtered_df.set_index("symbol")["price"])

    # Hier können weitere Visualisierungen hinzugefügt werden
    # z.B. st.line_chart(), st.map() etc.


# --------------------------
# HAUPTPROGRAMM
# --------------------------
if __name__ == "__main__":
    # 1. Verbindung initialisieren
    load_dotenv()
    init_db_connection()

    # 2. UI aufbauen
    setup_ui()

    # 3. Nur Dashboard anzeigen wenn verbunden
    if st.session_state.db_connection:
        # Daten laden
        df = load_stock_data()

        if df is not None:
            # Dashboard Inhalte anzeigen
            show_dashboard(df)
    else:
        st.warning("Bitte mit der Datenbank verbinden")

    # Sidebar-Status
    with st.sidebar:
        if st.session_state.db_connection:
            st.markdown('<p style="font-size:14px; color:green;">🟢 Verbunden</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="font-size:14px; color:orange;">🔴 Getrennt</p>', unsafe_allow_html=True)
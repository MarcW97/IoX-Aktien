import psycopg2
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import time
from dashboard_inhalte_v2 import show_dashboard


##
# --------------------------
# 1. DATENBANKVERBINDUNG
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
    """Lädt Aktiendaten aus der Datenbank"""
    try:
        if not st.session_state.db_connection:
            return None

        # Tägliche Preisdaten laden - KORREKTE SPALTENNAMEN!
        price_query = """
                      SELECT stock_symbol as symbol, date as datum, close as price, volume, open, high, low
                      FROM prices_daily
                      WHERE date >= CURRENT_DATE - INTERVAL '1 year'
                      ORDER BY stock_symbol, date
                      """
        price_df = pd.read_sql(price_query, st.session_state.db_connection)

        # Fundamentaldaten laden
        fundamental_query = """
                            SELECT stock_symbol       as symbol, \
                                   market_cap         as marktkapitalisierung,
                                   enterprise_value   as unternehmenswert, \
                                   revenue            as umsatz,
                                   ebitda, \
                                   pe_ratio           as kgv, \
                                   dividend_yield     as dividendenrendite,
                                   dividend_per_share as dividende_je_aktie, \
                                   beta
                            FROM fundamentals \
                            """
        try:
            fundamental_df = pd.read_sql(fundamental_query, st.session_state.db_connection)

            # Daten zusammenführen falls beide Datensätze vorhanden
            if not price_df.empty and not fundamental_df.empty:
                merged_df = pd.merge(
                    price_df,
                    fundamental_df,
                    on="symbol",
                    how="left"
                )
                return merged_df
        except Exception as fund_error:
            print(f"Warnung: Fundamentaldaten konnten nicht geladen werden: {fund_error}")
            # Wenn Fundamentaldaten fehlen, nur Preisdaten zurückgeben
            pass

        return price_df if not price_df.empty else None

    except Exception as e:
        st.error(f"Fehler beim Laden der Aktiendaten: {e}")
        print(f"Detaillierter Fehler: {e}")
        return None



# --------------------------
# HAUPTPROGRAMM
# --------------------------
if __name__ == "__main__":
    # 1. Verbindung initialisieren
    load_dotenv()
    init_db_connection()

    # 2. UI aufbauen
    setup_ui()

    # 3. Daten laden und Dashboard anzeigen
    if st.session_state.db_connection:
        df = load_stock_data()
        if df is not None:
            show_dashboard(df)
        else:
            st.warning("Keine Aktiendaten gefunden")
    else:
        st.warning("Bitte mit der Datenbank verbinden")
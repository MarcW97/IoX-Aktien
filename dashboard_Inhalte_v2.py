import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


# --------------------------
# DASHBOARD INHALTE
# --------------------------
def show_dashboard(df):
    """Zeigt das eigentliche Dashboard an"""
    # Seitenleiste mit Navigation
    with st.sidebar:
        st.title("📊 Navigation")

        # Statusanzeige
        if 'db_connection' in st.session_state and st.session_state.db_connection:
            st.markdown('<p style="font-size:14px; color:green;">🟢 Verbunden</p>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<p style="font-size:14px; color:orange;">🔴 Getrennt</p>',
                        unsafe_allow_html=True)

        st.markdown("---")

        # Navigationsmenü
        st.subheader("📌 Hauptmenü")
        selected_page = st.radio(
            "Optionen",
            ["Dashboard", "Technische Analyse", "Fundamentaldaten"],
            index=0,
            key="nav_menu"
        )

        st.markdown("---")
        if st.button("🔁 Filter zurücksetzen"):
            st.session_state.clear()
            st.rerun()

    # Hauptinhalt basierend auf ausgewählter Seite
    if selected_page == "Dashboard":
        show_main_dashboard(df)
    elif selected_page == "Technische Analyse":
        show_technical_analysis(df)
    else:
        show_fundamental_analysis(df)


# Ersetze diese Teile in deiner dashboard_Inhalte_v2.py

def show_main_dashboard(df):
    """Zeigt das Hauptdashboard mit allen Elementen"""
    st.markdown("---")

    # 1. Filter-Sektion
    st.subheader("🔍 Aktienfilter")
    symbols = sorted(df["symbol"].unique())
    selected_symbols = st.multiselect(
        "Wähle Aktien",
        symbols,
        default=list(symbols[:3]) if len(symbols) > 3 else symbols,
        key="main_dash_stock_selector"
    )

    # 2. Zeitfilter - KORRIGIERT!
    if 'datum' in df.columns:
        # Datetime-Konvertierung für PostgreSQL date-Felder
        df['datum'] = pd.to_datetime(df['datum'])

        min_date = df['datum'].min().date()  # .date() statt .to_pydatetime()
        max_date = df['datum'].max().date()  # .date() statt .to_pydatetime()

        # Standardwerte für date_range
        default_start = max_date - timedelta(days=30)
        date_range = st.slider(
            "Zeitraum auswählen",
            min_value=min_date,
            max_value=max_date,
            value=(default_start, max_date),
            format="DD.MM.YYYY",
            key="main_dash_date_selector"
        )

    # 3. Gefilterte Daten
    filtered_df = df[df["symbol"].isin(selected_symbols)]
    if 'datum' in df.columns and len(date_range) == 2:
        # Datum-Vergleich korrigiert
        filtered_df = filtered_df[
            (filtered_df['datum'].dt.date >= date_range[0]) &
            (filtered_df['datum'].dt.date <= date_range[1])
            ]

    # Rest des Codes bleibt gleich...
    # 🔹 OBERES LAYOUT: Tabelle und Kursverlauf
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Aktientabelle")
        # Datum für Anzeige formatieren
        display_df = filtered_df.copy()
        display_df['datum'] = display_df['datum'].dt.strftime('%Y-%m-%d')
        st.dataframe(display_df.sort_values(['symbol', 'datum']))

    with col2:
        st.subheader("📈 Kursverlauf")
        if 'datum' in df.columns:
            fig_line = px.line(
                filtered_df.sort_values(['symbol', 'datum']),
                x="datum",
                y="price",
                color="symbol",
                title="Historischer Kursverlauf",
                labels={"price": "Preis ($)", "datum": "Datum"},
                category_orders={"symbol": sorted(selected_symbols)}
            )
            st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    # 🔹 UNTERES LAYOUT: Handelsvolumen und Candlestick
    lower_col1, lower_col2 = st.columns(2)

    with lower_col1:
        st.subheader("📦 Handelsvolumen")
        fig_vol = px.bar(
            filtered_df,
            x='datum',
            y='volume',
            color='symbol',
            title="Handelsvolumen über Zeit",
            labels={"volume": "Volumen", "datum": "Datum"}
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    with lower_col2:
        st.subheader("🕯️ Candlestick Chart")
        if len(selected_symbols) == 1:
            symbol_df = filtered_df[filtered_df['symbol'] == selected_symbols[0]]
            fig = go.Figure(data=[go.Candlestick(
                x=symbol_df['datum'],
                open=symbol_df['open'],
                high=symbol_df['high'],
                low=symbol_df['low'],
                close=symbol_df['price']
            )])
            fig.update_layout(title=f"Candlestick Chart - {selected_symbols[0]}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Wählen Sie genau eine Aktie für Candlestick-Diagramm")
def show_technical_analysis(df):
    """Zeigt technische Analyse-Tools"""
    st.header("📊 Technische Analyse")

    symbols = sorted(df["symbol"].unique())
    selected_symbol = st.selectbox(
        "Aktie auswählen",
        symbols,
        key="tech_analysis_symbol"
    )

    symbol_df = df[df['symbol'] == selected_symbol].sort_values('datum')

    # Gleitende Durchschnitte berechnen
    symbol_df['MA20'] = symbol_df['price'].rolling(window=20).mean()
    symbol_df['MA50'] = symbol_df['price'].rolling(window=50).mean()

    # Plot mit gleitenden Durchschnitten
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=symbol_df['datum'],
        y=symbol_df['price'],
        name='Kurs',
        line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=symbol_df['datum'],
        y=symbol_df['MA20'],
        name='20-Tage Durchschnitt',
        line=dict(color='orange', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=symbol_df['datum'],
        y=symbol_df['MA50'],
        name='50-Tage Durchschnitt',
        line=dict(color='green', width=1)
    ))
    fig.update_layout(title=f"Technische Analyse - {selected_symbol}")
    st.plotly_chart(fig, use_container_width=True)


def show_fundamental_analysis(df):
    """Zeigt Fundamentaldaten"""
    st.header("🔍 Fundamentaldaten Analyse")

    symbols = sorted(df["symbol"].dropna().unique())
    selected_symbol = st.selectbox(
        "Aktie auswählen",
        symbols,
        key="fundamental_symbol"
    )

    try:
        # Fundamentaldaten für ausgewählte Aktie filtern
        fundamental_df = df[df['symbol'] == selected_symbol].iloc[0]

        # Wichtige Fundamentaldaten
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Marktkapitalisierung", f"{fundamental_df.get('marktkapitalisierung', 0) / 1e9:.2f} Mrd. $")
            st.metric("KGV", f"{fundamental_df.get('kgv', 'N/A')}")

        with col2:
            dividend_yield = fundamental_df.get('dividendenrendite')
            st.metric("Dividendenrendite", f"{dividend_yield:.2f}%" if pd.notnull(dividend_yield) else "N/A")
            st.metric("Beta", f"{fundamental_df.get('beta', 'N/A')}")

        with col3:
            st.metric("52-Wochen Hoch", f"{fundamental_df.get('hoch_52w', 'N/A')} $")
            st.metric("52-Wochen Tief", f"{fundamental_df.get('tief_52w', 'N/A')} $")

        # Detaillierte Fundamentaldaten
        with st.expander("🔎 Alle Fundamentaldaten anzeigen"):
            fundamentals = {
                "Unternehmenswert (EV)": fundamental_df.get('unternehmenswert'),
                "Umsatz (Revenue)": fundamental_df.get('umsatz'),
                "EBITDA": fundamental_df.get('ebitda'),
                "Free Cash Flow": fundamental_df.get('free_cash_flow'),
                "Eigenkapitalrendite (ROE)": fundamental_df.get('roe'),
                "Gewinn je Aktie (EPS)": fundamental_df.get('eps')
            }

            for key, value in fundamentals.items():
                if pd.notnull(value):
                    st.write(f"**{key}:** {value:,}" if isinstance(value, (int, float)) else f"**{key}:** {value}")

    except Exception as e:
        st.error(f"Fehler beim Laden der Fundamentaldaten: {e}")
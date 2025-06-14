import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db.connection import connect
from db.persistence import clear_old_data, get_symbol_name_mapping
from pipeline import run_data_pipeline

###
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


# Ersetze diese Teile in deiner dashboard_inhalte_v2.py

def show_main_dashboard(df):
    """Zeigt das Hauptdashboard mit allen Elementen"""
    st.markdown("---")
    st.subheader("🔍 Aktienfilter")
    st.write("Welche Aktien möchtest du analysieren?")

    with st.form("aktien_eingabe_formular"):
        symbol1 = st.text_input("Aktie 1", value="")
        symbol2 = st.text_input("Aktie 2", value="")
        submitted = st.form_submit_button("Analysieren & Speichern")

    if submitted:
        newSymbols = [symbol1.upper(), symbol2.upper()]
        newSymbols = [s for s in newSymbols if s]

        with st.spinner("Verarbeite Aktien..."):
            conn = connect()
            try:
                clear_old_data(conn)
                for symbol in newSymbols:
                    try:
                        run_data_pipeline(conn, symbol)
                        st.success(f"{symbol} erfolgreich analysiert und gespeichert.")
                    except ValueError as ve:
                        st.warning(str(ve))
                    except Exception as e:
                        st.error(f"Fehler bei {symbol}: {str(e)}")
            finally:
                conn.close()
        st.rerun()

    # Anzeige vorhandener Aktien mit Möglichkeit zum Entfernen
    if not df.empty:
        conn = connect()
        symbol_to_name = get_symbol_name_mapping(conn)
        conn.close()

        available_symbols = sorted(df["symbol"].unique())

        name_to_symbol = {
            symbol_to_name.get(s, s): s for s in available_symbols
        }
        name_options = list(name_to_symbol.keys())

        selected_names = st.multiselect(
            label="",
            options=name_options,
            default=name_options,
            key="main_dash_stock_selector",
            help="Entferne Aktien per 'X' aus der Anzeige"
        )
        selected_symbols = [name_to_symbol[name] for name in selected_names]

        if selected_symbols:
            st.write(f"Angezeigte Aktien: {', '.join(selected_names)}")
        else:
            st.info("Keine Aktien ausgewählt.")
    else:
        st.info("Noch keine Aktien analysiert.")

    # Zeitfilter
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

    # Gefilterte Daten
    filtered_df = df[df["symbol"].isin(selected_symbols)]
    if 'datum' in df.columns and len(date_range) == 2:
        # Datum-Vergleich korrigiert
        filtered_df = filtered_df[
            (filtered_df['datum'].dt.date >= date_range[0]) &
            (filtered_df['datum'].dt.date <= date_range[1])
            ]

    # Rest des Codes bleibt gleich...
    # OBERES LAYOUT: Tabelle und Kursverlauf
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Aktientabelle")
        # Datum für Anzeige formatieren
        display_df = filtered_df.copy()
        display_df['datum'] = display_df['datum'].dt.strftime('%Y-%m-%d')
        st.dataframe(display_df.sort_values(['symbol', 'datum']))

    with col2:
        st.subheader("📈 Kursverlauf")
        if 'datum' in df.columns and len(selected_symbols) == 2:  # Nur wenn 2 Aktien ausgewählt sind
            # Daten vorbereiten
            aktie1, aktie2 = selected_symbols[0], selected_symbols[1]
            df_plot = filtered_df.sort_values(['symbol', 'datum'])

            # Diagramm erstellen
            fig = px.line(
                df_plot,
                x="datum",
                y="price",
                color="symbol",
                title="Kursverlauf mit dualer Y-Achse",
                labels={"price": "Preis ($)", "datum": "Datum"}
            )

            # Zweite Y-Achse hinzufügen
            fig.update_layout(
                yaxis=dict(
                    title=f"Preis {aktie1} ($)",
                    side="left",
                    showgrid=False
                ),
                yaxis2=dict(
                    title=f"Preis {aktie2} ($)",
                    overlaying="y",
                    side="right",
                    showgrid=False
                )
            )

            # Zweite Linie an Y2 binden
            fig.data[1].update(yaxis="y2")  # Index 1 = zweite Aktie

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Wähle genau 2 Aktien für die duale Y-Achse aus.")

    # UNTERES LAYOUT: Handelsvolumen und Candlestick
    lower_col1, lower_col2 = st.columns(2)

    # Column 1: Handelsvolumen chart
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
        fig_vol.update_layout(barmode='group')  # 👈 Important!
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
    """Vergleicht zwei Aktien anhand von Fundamentaldaten nebeneinander"""

    st.header("📊 Fundamentaldaten Vergleich")

    symbols = sorted(df["symbol"].dropna().unique())

    col_select1, col_select2 = st.columns(2)
    with col_select1:
        symbol1 = st.selectbox("Aktie 1 auswählen:", symbols, key="symbol_1")
    with col_select2:
        remaining = [s for s in symbols if s != symbol1]
        symbol2 = st.selectbox("Aktie 2 auswählen:", remaining, key="symbol_2")

    try:
        df1 = df[df['symbol'] == symbol1].iloc[0]
        df2 = df[df['symbol'] == symbol2].iloc[0]

        def fmt(value, typ="raw"):
            try:
                if pd.isnull(value):
                    return "N/A"
                value = float(value)
                if typ == "mrd":
                    return f"{value / 1e9:.2f} Mrd. $"
                elif typ == "%":
                    return f"{value:.2f}%"
                else:
                    return f"{value:.2f}"
            except:
                return "N/A"

        fundamentals = [
            ("Marktkapitalisierung", "marktkapitalisierung", "mrd"),
            ("KGV", "kgv", "raw"),
            ("Dividendenrendite", "dividendenrendite", "%"),
            ("52-Wochen Hoch", "hoch_52w", "raw"),
            ("52-Wochen Tief", "tief_52w", "raw"),
            ("Unternehmenswert (EV)", "unternehmenswert", "mrd"),
            ("Umsatz (Revenue)", "umsatz", "mrd"),
            ("EBITDA", "ebitda", "mrd"),
            ("Free Cash Flow", "free_cash_flow", "mrd"),
            ("ROE", "roe", "%"),
            ("EPS", "eps", "raw"),
            ("Beta", "beta", "raw")
        ]

        # Gleichmäßige horizontale Abstände durch gleich breite Spalten
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.subheader(f"📈 {symbol1}")
        with col2:
            st.subheader("Kennzahl")
        with col3:
            st.subheader(f"📉 {symbol2}")

        for label, key, typ in fundamentals:
            val1 = df1.get(key)
            val2 = df2.get(key)

            if key == "dividendenrendite":
                val1 = (val1 or 0) / 100 if pd.notnull(val1) else None
                val2 = (val2 or 0) / 100 if pd.notnull(val2) else None

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.markdown(f"<div style='font-size: 18px; font-weight: bold'>{fmt(val1, typ)}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='font-size: 18px; font-weight: bold'>{label}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div style='font-size: 18px; font-weight: bold'>{fmt(val2, typ)}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Fehler beim Vergleich: {e}")
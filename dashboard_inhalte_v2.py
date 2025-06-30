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
            ["Dashboard", "Technische Analyse", "Fundamentaldaten", "Tabellarische Datenansicht"],
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
    elif selected_page == "Fundamentaldaten":
        show_fundamental_analysis(df)
    else:
        show_tabellarische_datenansicht(df)


def show_main_dashboard(df):
    """Zeigt das Hauptdashboard mit allen Elementen"""
    st.markdown("---")
    st.subheader("🔍 Welche Aktien möchtest du analysieren?")

    #Symbol-Namen aus Datenbank laden für Dropdown
    conn = connect()
    symbol_to_name = get_symbol_name_mapping(conn)
    conn.close()

    # Mapping und Optionen aufbauen
    options = [f"{symbol} – {symbol_to_name[symbol]}" for symbol in sorted(symbol_to_name)]
    symbol_map = {f"{symbol} – {symbol_to_name[symbol]}": symbol for symbol in symbol_to_name}

    with st.form("aktien_eingabe_formular"):
        col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 2, 2])

        with col1:
            st.markdown("**Aktie 1**")
        with col2:
            auswahl1 = st.selectbox(
                "",
                options=[""] + options,  # leere Option für optional
                key="symbol1_select",
                label_visibility="collapsed"
            )

        with col3:
            st.markdown("**Aktie 2**")
        with col4:
            auswahl2 = st.selectbox(
                "",
                options=[""] + options,
                key="symbol2_select",
                label_visibility="collapsed"
            )

        with col5:
            submitted = st.form_submit_button("Analysieren & Speichern")

    # Symbol aus Mapping extrahieren
    symbol1 = symbol_map.get(auswahl1, "").upper()
    symbol2 = symbol_map.get(auswahl2, "").upper()


    if submitted:
        new_symbols = [symbol1.upper(), symbol2.upper()]
        new_symbols = [s for s in new_symbols if s]

        with st.spinner("Verarbeite Aktien..."):
            conn = connect()
            try:
                clear_old_data(conn)
                for symbol in new_symbols:
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

    # Anzeige vorhandener Aktien
    if not df.empty:
        conn = connect()
        symbol_to_name = get_symbol_name_mapping(conn)
        conn.close()

        available_symbols = sorted(df["symbol"].unique())
        display_names = [symbol_to_name.get(s, s) for s in available_symbols]
        st.markdown(f"**Aktuell analysierte Aktien:** {', '.join(display_names)}")
    else:
        st.info("Noch keine Aktien analysiert.")

    # Zeitfilter
    if 'datum' in df.columns:
        # Datetime-Konvertierung für PostgreSQL date-Felder
        df['datum'] = pd.to_datetime(df['datum'])

        min_date = df['datum'].min().date()  # .date() statt .to_pydatetime()
        max_date = df['datum'].max().date()  # .date() statt .to_pydatetime()

        # Standardwerte für date_range
        default_start = max_date - timedelta(days=365)
        date_range = st.slider(
            "Zeitraum auswählen",
            min_value=min_date,
            max_value=max_date,
            value=(default_start, max_date),
            format="DD.MM.YYYY",
            key="main_dash_date_selector"
        )

    # Gefilterte Daten
    filtered_df = df.copy()
    if 'datum' in df.columns and len(date_range) == 2:
        # Datum-Vergleich korrigiert
        filtered_df = filtered_df[
            (filtered_df['datum'].dt.date >= date_range[0]) &
            (filtered_df['datum'].dt.date <= date_range[1])
            ]

    # OBERES LAYOUT: Kursverlauf
    st.subheader("📈 Kursverlauf")
    unique_symbols = sorted(filtered_df["symbol"].unique())

    if len(unique_symbols) == 0:
        st.info("Keine Daten vorhanden.")
    else:
        aktie1 = unique_symbols[0]
        aktie2 = unique_symbols[1] if len(unique_symbols) >= 2 else None

        selected_symbols = [aktie1]
        if aktie2:
            selected_symbols.append(aktie2)

        df_plot = filtered_df[filtered_df["symbol"].isin(selected_symbols)].sort_values(['symbol', 'datum'])

        fig = px.line(
            df_plot,
            x="datum",
            y="price",
            color="symbol",
            labels={"price": "Preis ($)", "datum": "Datum"},
        )

        # Layout
        title = f"Kursverlauf: {aktie1}" + (f" vs. {aktie2}" if aktie2 else "")
        fig.update_layout(
            title=title,
            yaxis=dict(
                title=f"Preis {aktie1} ($)",
                side="left",
                showgrid=False
            )
        )

        if aktie2 and len(fig.data) > 1:
            fig.update_layout(
                yaxis2=dict(
                    title=f"Preis {aktie2} ($)",
                    overlaying="y",
                    side="right",
                    showgrid=False
                )
            )
            fig.data[1].update(yaxis="y2")  # zweite Linie auf rechte Achse

        st.plotly_chart(fig, use_container_width=True)

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

    # Column 2: Candlestick Chart mit Auswahl der Aktie
    with lower_col2:
        st.subheader("🕯️ Candlestick Chart")

        unique_symbols = sorted(filtered_df["symbol"].unique())

        selected_candle_symbol = st.session_state.get("candle_symbol_select", unique_symbols[0] if unique_symbols else None)

        if selected_candle_symbol:
            symbol_df = filtered_df[filtered_df['symbol'] == selected_candle_symbol]
            fig = go.Figure(data=[go.Candlestick(
                x=symbol_df['datum'],
                open=symbol_df['open'],
                high=symbol_df['high'],
                low=symbol_df['low'],
                close=symbol_df['price']
            )])
            fig.update_layout(title=f"Candlestick Chart - {selected_candle_symbol}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Bitte wähle eine Aktie für den Candlestick-Chart.")

        selected_candle_symbol = st.selectbox(
            "Aktie für Candlestick auswählen",
            unique_symbols,
            index=unique_symbols.index(selected_candle_symbol) if selected_candle_symbol in unique_symbols else 0,
            key="candle_symbol_select"
        )

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

def show_tabellarische_datenansicht(df):
    st.header("📋 Tabellarische Datenansicht")

    if df.empty:
        st.info("Keine Daten vorhanden.")
        return

    # Sicherstellen, dass datum als datetime vorliegt
    display_df = df.copy()
    display_df['datum'] = pd.to_datetime(display_df['datum'], errors='coerce')
    display_df['datum'] = display_df['datum'].dt.strftime('%Y-%m-%d')

    st.dataframe(display_df.sort_values(['symbol', 'datum']))
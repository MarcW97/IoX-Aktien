def create_tables(conn):
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            symbol VARCHAR(10) PRIMARY KEY,
            name TEXT,
            sector TEXT,
            industry TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fundamentals (
            stock_symbol VARCHAR(10) NOT NULL REFERENCES stocks(symbol) ON DELETE CASCADE,
            market_cap BIGINT,
            enterprise_value BIGINT,
            revenue BIGINT,
            ebitda BIGINT,
            pe_ratio FLOAT,
            dividend_yield FLOAT,
            dividend_per_share FLOAT,
            beta FLOAT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS prices_daily (
            id SERIAL PRIMARY KEY,
            stock_symbol VARCHAR(10) NOT NULL REFERENCES stocks(symbol) ON DELETE CASCADE,
            date DATE NOT NULL,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume BIGINT
        );
    """)

    conn.commit()
    print("Tabellen erfolgreich erstellt.")

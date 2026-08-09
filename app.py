import sqlite3
import pandas as pd
import streamlit as st

# Setup Konfigurasi
st.set_page_config(page_title="Jurnal Trading", page_icon="📈", layout="wide")

# Database
conn = sqlite3.connect("journal_trading.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal DATE, instrumen TEXT, sesi TEXT, tipe TEXT,
        lot REAL, entry REAL, exit REAL, sl REAL, tp REAL,
        pnl REAL, pips REAL, catatan TEXT
    )
""")
conn.commit()

st.title("📈 Jurnal Trading")

# Sidebar
st.sidebar.header("📝 Input Trade")
modal_awal = st.sidebar.number_input("Modal Awal ($)", value=1000.0)
with st.sidebar.form("trade_form", clear_on_submit=True):
    tanggal = st.date_input("Tanggal")
    instrumen = st.selectbox("Instrumen", ["XAUUSD (Gold)", "NASDAQ (US100)"])
    sesi = st.selectbox("Sesi", ["London", "New York", "Asia"])
    tipe = st.selectbox("Tipe", ["BUY", "SELL"])
    lot = st.number_input("Lot", value=0.10, format="%.2f")
    entry = st.number_input("Entry", value=2000.0)
    exit_p = st.number_input("Exit", value=2010.0)
    catatan = st.text_area("Catatan")
    if st.form_submit_button("Simpan"):
        pnl = (exit_p - entry) * lot * 100 if tipe == "BUY" else (entry - exit_p) * lot * 100
        cursor.execute("INSERT INTO trades (tanggal, instrumen, sesi, tipe, lot, entry, exit, pnl, catatan) VALUES (?,?,?,?,?,?,?,?,?)",
                       (tanggal, instrumen, sesi, tipe, lot, entry, exit_p, round(pnl, 2), catatan))
        conn.commit()
        st.rerun()

# Dashboard
df_all = pd.read_sql_query("SELECT * FROM trades", conn)

if not df_all.empty:
    # Filter
    selected = st.sidebar.multiselect("Filter Instrumen", options=df_all["instrumen"].unique(), default=df_all["instrumen"].unique())
    df = df_all[df_all["instrumen"].isin(selected)]
    
    if not df.empty:
        # Metrik
        c1, c2, c3 = st.columns(3)
        c1.metric("Total PnL", f"${df['pnl'].sum():,.2f}")
        c2.metric("Win Rate", f"{(len(df[df['pnl']>0])/len(df))*100:.1f}%")
        c3.metric("Total Trade", len(df))
        
        # Grafik
        st.subheader("📊 Grafik Performa")
        st.line_chart(df["pnl"].cumsum())
        
        # Tabel
        st.subheader("📋 Riwayat")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        
        if st.button("Hapus Semua Data"):
            cursor.execute("DELETE FROM trades")
            conn.commit()
            st.rerun()
    else:
        st.warning("Pilih instrumen di sidebar untuk melihat data.")
else:
    st.info("Belum ada data. Silakan input trade di sidebar.")
        

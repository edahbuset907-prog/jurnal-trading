import sqlite3
import pandas as pd
import streamlit as st

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Jurnal Trading", layout="wide")
st.title("📈 Jurnal Trading")

# 2. Inisialisasi Database
conn = sqlite3.connect("journal.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal DATE,
        instrumen TEXT,
        tipe TEXT,
        lot REAL,
        pnl REAL
    )
""")
conn.commit()

# 3. Sidebar Input
with st.sidebar.form("input_form", clear_on_submit=True):
    st.header("Tambah Trade")
    tanggal = st.date_input("Tanggal")
    instrumen = st.selectbox("Instrumen", ["XAUUSD", "NASDAQ"])
    tipe = st.selectbox("Tipe", ["BUY", "SELL"])
    lot = st.number_input("Lot", value=0.10, format="%.2f")
    pnl = st.number_input("PnL ($)", value=0.0)
    submitted = st.form_submit_button("Simpan")
    
    if submitted:
        cursor.execute("INSERT INTO trades (tanggal, instrumen, tipe, lot, pnl) VALUES (?,?,?,?,?)",
                       (tanggal, instrumen, tipe, lot, pnl))
        conn.commit()
        st.rerun()

# 4. Tampilan Data & Dashboard
df = pd.read_sql_query("SELECT * FROM trades", conn)

if not df.empty:
    # Metrik
    c1, c2, c3 = st.columns(3)
    c1.metric("Total PnL", f"${df['pnl'].sum():,.2f}")
    c2.metric("Win Rate", f"{(len(df[df['pnl']>0])/len(df))*100:.1f}%")
    c3.metric("Total Trade", len(df))
    
    # Grafik
    st.subheader("📊 Grafik Performa")
    st.line_chart(df['pnl'].cumsum())
    
    # Tabel
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    
    # Tombol Hapus
    if st.button("Hapus Semua Data"):
        cursor.execute("DELETE FROM trades")
        conn.commit()
        st.rerun()
else:
    st.write("Belum ada data. Silakan input trade di sebelah kiri.")
    

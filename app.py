import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Jurnal Trading", layout="wide")
st.title("📈 Jurnal Trading")

# Inisialisasi Database & Pembuatan Tabel Otomatis
conn = sqlite3.connect("journal_trading.db", check_same_thread=False)
cursor = conn.cursor()

# Perintah ini memastikan tabel 'trades' pasti dibuat jika belum ada
cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal DATE,
        instrumen TEXT,
        pnl REAL
    )
""")
conn.commit()

# Sidebar untuk Input Data Baru
with st.sidebar.form("input_form", clear_on_submit=True):
    st.subheader("Tambah Trade")
    tanggal_input = st.date_input("Tanggal")
    instrumen = st.selectbox("Instrumen", ["XAUUSD", "NASDAQ"])
    pnl_input = st.number_input("PnL ($)", value=0.0, step=10.0)
    
    submitted = st.form_submit_button("Simpan Trade")
    if submitted:
        cursor.execute("INSERT INTO trades (tanggal, instrumen, pnl) VALUES (?, ?, ?)", 
                       (str(tanggal_input), instrumen, pnl_input))
        conn.commit()
        st.success("Berhasil disimpan!")
        st.rerun()

# Membaca Data dari Database
df = pd.read_sql_query("SELECT * FROM trades", conn)

if not df.empty:
    # Metrik Ringkasan
    total_pnl = df['pnl'].sum()
    total_trade = len(df)
    
    col1, col2 = st.columns(2)
    col1.metric("Total PnL", f"${total_pnl:,.2f}")
    col2.metric("Total Trade", total_trade)
    
    st.markdown("---")
    
    # Grafik Pertumbuhan PnL
    st.subheader("📊 Grafik Performa")
    st.line_chart(df['pnl'].cumsum())
    
    # Tabel Riwayat
    st.subheader("📋 Riwayat Trade")
    st.dataframe(df.sort_values(by="id", ascending=False), use_container_width=True)
    
    # Tombol Hapus Semua Data
    if st.button("Hapus Semua Data"):
        cursor.execute("DELETE FROM trades")
        conn.commit()
        st.rerun()
else:
    st.info("Belum ada data trade. Silakan masukkan data melalui form di sidebar kiri.")
    

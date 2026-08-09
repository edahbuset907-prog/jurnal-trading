import sqlite3
import pandas as pd
import streamlit as st

# Setup Konfigurasi Halaman
st.set_page_config(
    page_title="Jurnal Trading XAUUSD", page_icon="📈", layout="wide"
)

# Inisialisasi Database SQLite
conn = sqlite3.connect("journal_xauusd.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal DATE,
        tipe TEXT,
        lot REAL,
        entry REAL,
        exit REAL,
        sl REAL,
        tp REAL,
        pnl REAL,
        pips REAL,
        catatan TEXT
    )
"""
)
conn.commit()

st.title("📈 Jurnal Trading XAUUSD (Emas)")

# Sidebar: Form Input Trade
st.sidebar.header("📝 Input Trade Baru")
with st.sidebar.form("trade_form", clear_on_submit=True):
    tanggal = st.date_input("Tanggal")
    tipe = st.selectbox("Tipe Posisi", ["BUY", "SELL"])
    lot = st.number_input(
        "Lot Size", min_value=0.01, step=0.01, value=0.10, format="%.2f"
    )
    entry = st.number_input("Harga Entry", min_value=0.0, step=0.1, value=2000.0)
    exit_price = st.number_input(
        "Harga Exit", min_value=0.0, step=0.1, value=2010.0
    )
    sl = st.number_input(
        "Stop Loss (SL)", min_value=0.0, step=0.1, value=1990.0
    )
    tp = st.number_input(
        "Take Profit (TP)", min_value=0.0, step=0.1, value=2020.0
    )
    catatan = st.text_area("Catatan / Alasan Entry")

    submitted = st.form_submit_button("Simpan Trade")

    if submitted:
        # Kalkulasi PnL & Pips XAUUSD (1 Lot = $100 per $1 pergerakan)
        if tipe == "BUY":
            pips = (exit_price - entry) * 10
            pnl = (exit_price - entry) * lot * 100
        else:
            pips = (entry - exit_price) * 10
            pnl = (entry - exit_price) * lot * 100

        cursor.execute(
            """
            INSERT INTO trades (tanggal, tipe, lot, entry, exit, sl, tp, pnl, pips, catatan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                tanggal,
                tipe,
                lot,
                entry,
                exit_price,
                sl,
                tp,
                round(pnl, 2),
                round(pips, 1),
                catatan,
            ),
        )
        conn.commit()
        st.sidebar.success("Trade berhasil disimpan!")

# Ringkasan Kinerja (Dashboard)
df = pd.read_sql_query("SELECT * FROM trades", conn)

if not df.empty:
    total_pnl = df["pnl"].sum()
    win_trades = len(df[df["pnl"] > 0])
    loss_trades = len(df[df["pnl"] < 0])
    total_trades = len(df)
    win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0

    # Tampilan Metrik Utama
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total PnL", f"${total_pnl:,.2f}")
    col2.metric("Total Trade", total_trades)
    col3.metric("Win Rate", f"{win_rate:.1f}%")
    col4.metric("Win / Loss", f"{win_trades} / {loss_trades}")

    st.markdown("---")

    # Tabel Riwayat Trade
    st.subheader("📋 Riwayat Trade")
    st.dataframe(
        df.sort_values(by="id", ascending=False), use_container_width=True
    )

    # Tombol Hapus Data
    if st.button("Hapus Semua Data"):
        cursor.execute("DELETE FROM trades")
        conn.commit()
        st.rerun()
else:
    st.info("Belum ada data trade. Silakan masukkan data di sidebar kiri.")
    # --- TOMBOL DOWNLOAD BACKUP EXCEL ---
st.markdown("---")
st.subheader("📥 Backup Data Jurnal")
try:
    df_backup = pd.read_sql_query("SELECT * FROM trades", conn)
    if not df_backup.empty:
        csv_data = df_backup.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data ke Excel/CSV",
            data=csv_data,
            file_name="jurnal_trading_backup.csv",
            mime="text/csv",
        )
    else:
        st.info("Belum ada data untuk di-download.")
except Exception as e:
    st.info("Tombol download akan muncul setelah ada data tersimpan.")
    # --- RINGKASAN & WIN RATE ---
df = pd.read_sql_query("SELECT * FROM trades", conn)

if not df.empty:
    total_pnl = df["pnl"].sum()
    total_trades = len(df)
    win_trades = len(df[df["pnl"] > 0])
    loss_trades = len(df[df["pnl"] < 0])
    win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0

    # Tampilkan Metrik di Atas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total PnL", f"${total_pnl:,.2f}")
    col2.metric("Total Trade", total_trades)
    col3.metric("Win Rate", f"{win_rate:.1f}%")
    col4.metric("Win / Loss", f"{win_trades} / {loss_trades}")
    
    st.markdown("---")
    
    
    
      

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

# Buat Tabel jika belum ada (termasuk kolom sesi)
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
        catatan TEXT,
        sesi TEXT
    )
"""
)
conn.commit()

st.title("📈 Jurnal Trading XAUUSD (Emas)")

# --- Form Input ---
with st.sidebar.form("trade_form", clear_on_submit=True):
    tanggal_input = st.date_input("Tanggal")
    tipe = st.selectbox("Tipe Posisi", ["BUY", "SELL"])
    lot = st.number_input("Lot Size", min_value=0.01, step=0.01, value=0.10, format="%.2f")
    entry = st.number_input("Harga Entry", min_value=0.0, step=0.1, value=2000.0)
    exit_price = st.number_input("Harga Exit", min_value=0.0, step=0.1, value=2010.0)
    sl = st.number_input("Stop Loss (SL)", min_value=0.0, step=0.1, value=1990.0)
    tp = st.number_input("Take Profit (TP)", min_value=0.0, step=0.1, value=2020.0)
    catatan = st.text_area("Catatan / Alasan Entry")
    sesi_input = st.selectbox("Sesi Market", ["Asian Session", "London Session", "New York Session"])
    
    submitted = st.form_submit_button("Simpan Trade")

# --- Blok Simpan ---
if submitted:
    # Kalkulasi
    if tipe == "BUY":
        pips = (exit_price - entry) * 10
        pnl = (exit_price - entry) * lot * 100
    else:
        pips = (entry - exit_price) * 10
        pnl = (entry - exit_price) * lot * 100

    # Simpan ke database
    cursor.execute("""
        INSERT INTO trades (tanggal, tipe, lot, entry, exit, sl, tp, pnl, pips, catatan, sesi) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (str(tanggal_input), tipe, lot, entry, exit_price, sl, tp, pnl, pips, catatan, sesi_input))
    
    conn.commit()
    st.success("Trade berhasil disimpan!")
    st.rerun()

      (
          tanggal,
          tipe,
          lot,
          entry,
          exit_price,
          sl,
          tp,
          pnl,
          pips,
          catatan,
          sesi,
      ),
  )
  conn.commit()
  st.success("Trade berhasil disimpan!")
  st.rerun()

# --- TAMPILAN DATA & FILTER ---
df_all = pd.read_sql_query("SELECT * FROM trades", conn)

if not df_all.empty and "tanggal" in df_all.columns:
  st.sidebar.markdown("---")
  st.sidebar.subheader("📅 Filter Tanggal")
  df_all["tanggal"] = pd.to_datetime(df_all["tanggal"])
  min_date = df_all["tanggal"].min().date()
  max_date = df_all["tanggal"].max().date()

  start_date = st.sidebar.date_input("Dari Tanggal", min_date, min_value=min_date, max_value=max_date)
  end_date = st.sidebar.date_input("Sampai Tanggal", max_date, min_value=min_date, max_value=max_date)

  df = df_all[
      (df_all["tanggal"].dt.date >= start_date)
      & (df_all["tanggal"].dt.date <= end_date)
  ]
else:
  df = df_all

# Metrik Atas
if not df.empty:
  total_trades = len(df)
  total_pnl = df["pnl"].sum()
  win_trades = len(df[df["pnl"] > 0])
  loss_trades = len(df[df["pnl"] < 0])
  win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Total PnL", f"${total_pnl:.2f}")
  col2.metric("Total Trade", total_trades)
  col3.metric("Win Rate", f"{win_rate:.1f}%")
  col4.metric("Win / Loss", f"{win_trades} / {loss_trades}")

  st.markdown("---")
  st.subheader("📊 Tabel Riwayat Trade")
  st.dataframe(df, use_container_width=True)

  # Rekap Performa Berdasarkan Sesi Market
  if "sesi" in df.columns:
    st.markdown("---")
    st.subheader("🌐 Performa Berdasarkan Sesi Market")
    sesi_summary = (
        df.groupby("sesi")
        .agg(
            Total_Trade=("pnl", "count"),
            Total_PnL=("pnl", "sum"),
            Win_Rate=(
                "pnl",
                lambda x: (
                    (sum(x > 0) / len(x)) * 100 if len(x) > 0 else 0
                ),
            ),
        )
        .reset_index()
    )
    st.dataframe(sesi_summary, use_container_width=True)
else:
  st.info("Belum ada data trade yang tersimpan. Silakan input melalui sidebar.")
    

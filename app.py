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
        tanggal TEXT,
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

# Sidebar: Form Input Trade
st.sidebar.header("📝 Input Trade Baru")
with st.sidebar.form("trade_form", clear_on_submit=True):
  tanggal_input = st.date_input("Tanggal")
  tipe = st.selectbox("Tipe Posisi", ["BUY", "SELL"])
  lot = st.number_input(
      "Lot Size", min_value=0.01, step=0.01, value=0.10, format="%.2f"
  )
  entry = st.number_input("Harga Entry", min_value=0.0, step=0.1, value=2000.0)
  exit_price = st.number_input(
      "Harga Exit", min_value=0.0, step=0.1, value=2010.0
  )
  sl = st.number_input("Stop Loss (SL)", min_value=0.0, step=0.1, value=1990.0)
  tp = st.number_input(
      "Take Profit (TP)", min_value=0.0, step=0.1, value=2020.0
  )
  catatan = st.text_area("Catatan / Alasan Entry")
  sesi_input = st.selectbox(
      "Sesi Market", ["Asian Session", "London Session", "New York Session"]
  )

  submitted = st.form_submit_button("Simpan Trade")

if submitted:
  # Kalkulasi PnL & Pips XAUUSD
  if tipe == "BUY":
    pips = (exit_price - entry) * 10
    pnl = (exit_price - entry) * lot * 100
  else:
    pips = (entry - exit_price) * 10
    pnl = (entry - exit_price) * lot * 100

  cursor.execute(
      """
        INSERT INTO trades (tanggal, tipe, lot, entry, exit, sl, tp, pnl, pips, catatan, sesi) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          str(tanggal_input),
          tipe,
          lot,
          entry,
          exit_price,
          sl,
          tp,
          pnl,
          pips,
          catatan,
          sesi_input,
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

  start_date = st.sidebar.date_input(
      "Dari Tanggal", min_date, min_value=min_date, max_value=max_date
  )
  end_date = st.sidebar.date_input(
      "Sampai Tanggal", max_date, min_value=min_date, max_value=max_date
  )

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
    import pandas as pd
import streamlit as st

# --- 1. SETUP HALAMAN ---
st.set_page_config(
    page_title="Pro Trader Journal", page_icon="⚡", layout="wide"
)

# --- 2. CUSTOM CSS (UI KELAS ATAS) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Background & Warna Utama */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    
    /* Styling Card / Container */
    div.stMetric {
        background-color: #111827;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #1f2937;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Tombol Kustom */
    div.stButton > button {
        border-radius: 10px;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 10px 20px;
        transition: 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Header Tabel */
    dataframe {
        border-radius: 12px;
        border: 1px solid #1f2937;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. HEADER UTAMA ---
st.markdown(
    "<h1 style='text-align: center; font-weight: 600; color: #ffffff;'>⚡ PRO"
    " TRADER JOURNAL</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #9ca3af;'>Sistem pencatatan dan"
    " evaluasi performa trading berstandar institusional.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- 4. DASHBOARD STATISTIK (METRIK) ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
  st.metric(label="Total Trades", value="42", delta="+5 minggu ini")
with col_m2:
  st.metric(label="Win Rate", value="64.3%", delta="2.1%")
with col_m3:
  st.metric(label="Net Profit", value="$1,850.00", delta="$340.00")
with col_m4:
  st.metric(label="Profit Factor", value="1.85", delta="Optimal")

st.markdown("---")

# --- 5. INPUT DATA & TABEL RIWAYAT ---
col_form, col_table = st.columns([1, 2])

# Kolom Kiri: Form Input Trade
with col_form:
  st.subheader("📝 Catat Posisi Baru")
  with st.form("trade_form", clear_on_submit=True):
    pair = st.selectbox("Trading Pair", ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD"])
    action = st.radio("Action", ["BUY", "SELL"], horizontal=True)
    lot = st.number_input("Lot Size", min_value=0.01, value=0.10, step=0.01)
    result_pips = st.number_input(
        "Hasil (Pips / $)", value=0.0, format="%.2f"
    )
    setup = st.selectbox(
        "Strategi Setup", ["Breakout", "Supply & Demand", "Trend Following"]
    )
    notes = st.text_area("Catatan Psikologi / Analisis")

    submitted = st.form_submit_button("Simpan ke Jurnal")
    if submitted:
      st.success("Trade berhasil dicatat dengan aman!")

# Kolom Kanan: Tabel Riwayat Profesional
with col_table:
  st.subheader("📊 Riwayat Transaksi")

  # Data Dummy Contoh Tampilan
  data_riwayat = {
      "Tanggal": ["08/08", "08/08", "07/08", "06/08"],
      "Pair": ["XAUUSD", "EURUSD", "XAUUSD", "GBPUSD"],
      "Type": ["BUY", "SELL", "BUY", "SELL"],
      "Lot": [0.20, 0.50, 0.10, 0.30],
      "Hasil ($)": ["+$240.00", "-$85.00", "+$410.00", "+$150.00"],
      "Status": ["🟢 WIN", "🔴 LOSS", "🟢 WIN", "🟢 WIN"],
  }
  df_riwayat = pd.DataFrame(data_riwayat)

  # Menampilkan tabel dengan gaya rapi
  st.dataframe(df_riwayat, use_container_width=True, hide_index=True)

# Footer Elegan
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #4b5563; font-size: 12px;'>Pro Trader"
    " Journal Dashboard v2.0 — Secure & Private</p>",
    unsafe_allow_html=True,
)

    

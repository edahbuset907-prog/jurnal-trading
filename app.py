import calendar
from datetime import datetime
import sqlite3
import pandas as pd
import streamlit as st

# Setup Konfigurasi Halaman
st.set_page_config(
    page_title="Jurnal Trading Multi-Instrumen", page_icon="📈", layout="wide"
)

# Inisialisasi Database SQLite
conn = sqlite3.connect("journal_trading.db", check_same_thread=False)
cursor = conn.cursor()

# Cek & Buat Tabel dengan Kolom 'instrumen'
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal DATE,
        instrumen TEXT,
        sesi TEXT,
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
# Migrasi aman jika tabel lama belum memiliki kolom instrumen/sesi
try:
  cursor.execute("ALTER TABLE trades ADD COLUMN instrumen TEXT")
  conn.commit()
except sqlite3.OperationalError:
  pass

try:
  cursor.execute("ALTER TABLE trades ADD COLUMN sesi TEXT")
  conn.commit()
except sqlite3.OperationalError:
  pass

st.title("📈 Jurnal Trading (XAUUSD & NASDAQ)")

# Sidebar: Pengaturan Akun & Form Input
st.sidebar.header("⚙️ Pengaturan Akun")
modal_awal = st.sidebar.number_input(
    "Modal Awal ($)", min_value=10.0, step=100.0, value=1000.0
)

st.sidebar.header("📝 Input Trade Baru")
with st.sidebar.form("trade_form", clear_on_submit=True):
  tanggal = st.date_input("Tanggal", value=datetime.today())
  instrumen = st.selectbox(
      "Pilih Instrumen", ["XAUUSD (Gold)", "NASDAQ (US100)"]
  )
  sesi = st.selectbox(
      "Sesi Trading", ["London", "New York", "Asia", "London / NY Overlap"]
  )
  tipe = st.selectbox("Tipe Posisi", ["BUY", "SELL"])

  lot = st.number_input(
      "Lot Size", min_value=0.01, step=0.01, value=0.10, format="%.2f"
  )

  st.markdown(
      "<small><i>*XAUUSD: Entry misal 2000.0 | NASDAQ: Entry misal"
      " 18000.0</i></small>",
      unsafe_allow_html=True,
  )
  entry = st.number_input("Harga Entry", min_value=0.0, step=0.1, value=2000.0)
  exit_price = st.number_input(
      "Harga Exit", min_value=0.0, step=0.1, value=2010.0
  )
  sl = st.number_input("Stop Loss (SL)", min_value=0.0, step=0.1, value=1990.0)
  tp = st.number_input("Take Profit (TP)", min_value=0.0, step=0.1, value=2020.0)
  catatan = st.text_area("Catatan / Alasan Entry")

  submitted = st.form_submit_button("Simpan Trade")

  if submitted:
    if "XAUUSD" in instrumen:
      if tipe == "BUY":
        pips = (exit_price - entry) * 10
        pnl = (exit_price - entry) * lot * 100
      else:
        pips = (entry - exit_price) * 10
        pnl = (entry - exit_price) * lot * 100
    else:
      if tipe == "BUY":
        pips = exit_price - entry
        pnl = (exit_price - entry) * lot * 20
      else:
        pips = entry - exit_price
        pnl = (entry - exit_price) * lot * 20

    cursor.execute(
        """
        INSERT INTO trades (tanggal, instrumen, sesi, tipe, lot, entry, exit, sl, tp, pnl, pips, catatan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            str(tanggal),
            instrumen,
            sesi,
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
    st.rerun()

# Membaca Data Utama
df_all = pd.read_sql_query("SELECT * FROM trades", conn)

if not df_all.empty:
  df_all["tanggal"] = pd.to_datetime(df_all["tanggal"])

  # --- FITUR FILTER PAIR / INSTRUMEN ---
  st.sidebar.markdown("---")
  st.sidebar.header("🔍 Filter Dashboard")
  all_instrumen = df_all["instrumen"].unique().tolist()
  selected_instrumen = st.sidebar.multiselect(
      "Pilih Pair / Instrumen", options=all_instrumen, default=all_instrumen
  )

  # Terapkan Filter ke DataFrame Utama Dashboard
  df = df_all[df_all["instrumen"].isin(selected_instrumen)]

  if not df.empty:
    total_pnl = df["pnl"].sum()
    win_trades = len(df[df["pnl"] > 0])
    loss_trades = len(df[df["pnl"] < 0])
    total_trades = len(df)
    win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0

    persen_pertumbuhan = (total_pnl / modal_awal) * 100

    # Tampilan Metrik Utama
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Total PnL",
        f"${total_pnl:,.2f}",
        delta=f"{persen_pertumbuhan:+.2f}% dari Modal",
    )
    col2.metric("Total Trade", total_trades)
    col3.metric("Win Rate", f"{win_rate:.1f}%")
    col4.metric("Win / Loss", f"{win_trades} / {loss_trades}")

    st.markdown("---")

    # --- FITUR PNL CALENDAR ---
    st.subheader("📅 PnL Calendar")
    col_bln, col_thn = st.columns(2)
    with col_bln:
      pilih_bulan = st.selectbox(
          "Pilih Bulan",
          list(range(1, 13)),
          format_func=lambda x: calendar.month_name[x],
          index=datetime.now().month - 1,
      )
    with col_thn:
      pilih_tahun = st.selectbox(
          "Pilih Tahun", [2024, 2025, 2026, 2027], index=2
      )

    # Filter data sesuai bulan dan tahun untuk kalender
    df_calendar = df[
        (df["tanggal"].dt.month == pilih_bulan)
        & (df["tanggal"].dt.year == pilih_tahun)
    ]
    daily_summary = (
        df_calendar.groupby(df_calendar["tanggal"].dt.date)
        .agg(total_pnl=("pnl", "sum"), jumlah_trade=("id", "count"))
        .reset_index()
    )

    calendar_data = {}
    for _, row in daily_summary.iterrows():
      calendar_data[row["tanggal"]] = {
          "pnl": row["total_pnl"],
          "trades": row["jumlah_trade"],
      }

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(pilih_tahun, pilih_bulan)

    header_cols = st.columns(7)
    hari_str = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    for idx, h in enumerate(hari_str):
      header_cols[idx].markdown(
          f"<p align='center'><b>{h}</b></p>", unsafe_allow_html=True
      )

    for week in month_days:
      week_cols = st.columns(7)
      for idx, day in enumerate(week):
        if day == 0:
          week_cols[idx].markdown(
              "<div style='padding: 12px; text-align: center; color:"
              " gray;'>-</div>",
              unsafe_allow_html=True,
          )
        else:
          current_date = pd.to_datetime(
              f"{pilih_tahun}-{pilih_bulan:02d}-{day:02d}"
          ).date()
          if current_date in calendar_data:
            pnl_val = calendar_data[current_date]["pnl"]
            trd_val = calendar_data[current_date]["trades"]
            bg_color = (
                "rgba(0, 255, 128, 0.15)"
                if pnl_val >= 0
                else "rgba(255, 75, 75, 0.15)"
            )
            text_color = "#00ff80" if pnl_val >= 0 else "#ff4b4b"
            sign = "+" if pnl_val > 0 else ""
            week_cols[idx].markdown(
                f"""
                            <div style="background-color: {bg_color}; border: 1px solid {text_color}; border-radius: 6px; padding: 6px; text-align: center; min-height: 65px;">
                                <span style="font-size: 11px; color: #aaa;">{day}</span><br>
                                <span style="font-size: 12px; font-weight: bold; color: {text_color};">{sign}${pnl_val:,.0f}</span><br>
                                <span style="font-size: 9px; color: #888;">{trd_val} trade</span>
                            </div>
                            """,
                unsafe_allow_html=True,
            )
          else:
            week_cols[idx].markdown(
                f"""
                            <div style="background-color: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 6px; padding: 6px; text-align: center; min-height: 65px;">
                                <span style="font-size: 11px; color: #555;">{day}</span><br>
                                <span style="font-size: 10px; color: #444;">-</span>
                            </div>
                            """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # --- Grafik Performa Equity & Persentase ---
    st.subheader("📊 Grafik Performa Equity & Persentase")
    df_chart = df.sort_values(by="id", ascending=True).reset_index(drop=True)
    df_chart["Trade Ke-"] = df_chart.index + 1
    df_chart["Kumulatif PnL"] = df_chart["pnl"].cumsum()
    df_chart["Equity Total"] = modal_awal + df_chart["Kumulatif PnL"]
    df_chart["Persentase (%)"] = (
        df_chart["Kumulatif PnL"] / modal_awal
    ) * 100

    st.line_chart(
        df_chart.set_index("Trade Ke-")[["Equity Total", "Persentase (%)"]]
    )

    st.markdown("---")

    # --- Tabel Riwayat Trade & Tombol Download CSV ---
    st.subheader("📋 Riwayat Trade")

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Data ke CSV",
        data=csv_data,
        file_name="jurnal_trading_multi.csv",
        mime="text/csv",
    )

    st.dataframe(
        df.sort_values(by="id", ascending=False), use_container_width=True
    )

    # Tombol Hapus Data
    if st.button("Hapus Semua Data (Sesuai Filter)"):
        # Jika ingin menghapus semua tanpa filter, ubah query-nya. Ini menghapus data yang sedang tampil.
        cursor.execute("DELETE FROM trades")
        conn.commit()
        st.rerun()
  else:
    st.warning(
        "Tidak ada data untuk instrumen yang dipilih pada filter sidebar."
    )
else:
  st.info("Belum ada data trade. Silakan masukkan data di sidebar kiri.")
        # --- STATISTIK SIGNAL DI BAGIAN PALING BAWAH ---
    st.markdown("---")
    st.subheader("📊 Statistik Signal Frequency")
    
    total_trades = len(df)
    profit_trades = len(df[df["pnl"] > 0])
    loss_trades = len(df[df["pnl"] < 0])
    
    # Hitung rasio untuk progress bar
    p_profit = (profit_trades / total_trades) if total_trades > 0 else 0
    p_loss = (loss_trades / total_trades) if total_trades > 0 else 0
    
    st.write(f"**Profit / Settled:** {profit_trades} dari {total_trades} trade")
    st.progress(p_profit)
    
    st.write(f"**Loss / Settled:** {loss_trades} dari {total_trades} trade")
    st.progress(p_loss)

      

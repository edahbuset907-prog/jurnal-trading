import sqlite3
import pandas as pd
import streamlit as st
import calendar
from datetime import datetime

st.set_page_config(page_title="Jurnal Trading & PnL Calendar", layout="wide")
st.title("📈 Jurnal Trading XAUUSD & NASDAQ")

# Database (Menggunakan database lama Anda agar data aman)
conn = sqlite3.connect("journal_trading.db", check_same_thread=False)
cursor = conn.cursor()

# Pastikan tabel memiliki kolom tanggal dan pnl
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

# Sidebar Input Trade
with st.sidebar.form("input_form", clear_on_submit=True):
    st.header("📝 Tambah Trade")
    tanggal_input = st.date_input("Tanggal", value=datetime.today())
    instrumen = st.selectbox("Instrumen", ["XAUUSD", "NASDAQ"])
    tipe = st.selectbox("Tipe", ["BUY", "SELL"])
    lot = st.number_input("Lot", value=0.10, format="%.2f")
    pnl_input = st.number_input("PnL ($)", value=0.0, step=10.0)
    
    if st.form_submit_button("Simpan Trade"):
        cursor.execute("INSERT INTO trades (tanggal, instrumen, tipe, lot, pnl) VALUES (?, ?, ?, ?, ?)",
                       (str(tanggal_input), instrumen, tipe, lot, pnl_input))
        conn.commit()
        st.sidebar.success("Berhasil disimpan!")
        st.rerun()

# Ambil data dari database
df = pd.read_sql_query("SELECT * FROM trades", conn)

if not df.empty:
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    
    # --- RINGKASAN METRIK ---
    total_pnl = df['pnl'].sum()
    win_trades = len(df[df['pnl'] > 0])
    total_trades = len(df)
    win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total PnL", f"${total_pnl:,.2f}")
    c2.metric("Total Trade", total_trades)
    c3.metric("Win Rate", f"{win_rate:.1f}%")
    c4.metric("Profit/Loss Trade", f"{win_trades} / {total_trades - win_trades}")

    st.markdown("---")

    # --- FITUR PNL CALENDAR (KALENDER BULANAN) ---
    st.subheader("📅 PnL Calendar")
    
    # Pilihan Bulan & Tahun untuk Kalender
    col_bln, col_thn = st.columns(2)
    with col_bln:
        pilih_bulan = st.selectbox("Pilih Bulan", list(range(1, 13)), format_func=lambda x: calendar.month_name[x], index=datetime.now().month - 1)
    with col_thn:
        pilih_tahun = st.selectbox("Pilih Tahun", [2024, 2025, 2026, 2027], index=2) # Default 2026

    # Agregasi PnL harian pada bulan & tahun yang dipilih
    df_bulan = df[(df['tanggal'].dt.month == pilih_bulan) & (df['tanggal'].dt.year == pilih_tahun)]
    
    # Hitung total PnL dan jumlah trade per hari
    daily_summary = df_bulan.groupby(df_bulan['tanggal'].dt.date).agg(
        total_pnl=('pnl', 'sum'),
        jumlah_trade=('id', 'count')
    ).reset_index()

    # Buat mapping data harian ke dictionary {tanggal: {pnl, trades}}
    calendar_data = {}
    for _, row in daily_summary.iterrows():
        calendar_data[row['tanggal']] = {
            'pnl': row['total_pnl'],
            'trades': row['jumlah_trade']
        }

    # Render Kalender (Senin - Minggu)
    cal = calendar.Calendar(firstweekday=0) # 0 = Senin
    month_days = cal.monthdayscalendar(pilih_tahun, pilih_bulan)

    # Header Hari
    header_cols = st.columns(7)
    hari_str = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    for idx, h in enumerate(hari_str):
        header_cols[idx].markdown(f"<p align='center'><b>{h}</b></p>", unsafe_allow_html=True)

    # Baris Tanggal Kalender
    for week in month_days:
        week_cols = st.columns(7)
        for idx, day in enumerate(week):
            if day == 0:
                week_cols[idx].markdown("<div style='padding: 15px; text-align: center; color: gray;'>-</div>", unsafe_allow_html=True)
            else:
                current_date = pd.to_datetime(f"{pilih_tahun}-{pilih_bulan:02d}-{day:02d}").date()
                if current_date in calendar_data:
                    pnl_val = calendar_data[current_date]['pnl']
                    trd_val = calendar_data[current_date]['trades']
                    
                    # Warna hijau jika profit, merah jika loss
                    bg_color = "rgba(0, 255, 128, 0.15)" if pnl_val >= 0 else "rgba(255, 75, 75, 0.15)"
                    text_color = "#00ff80" if pnl_val >= 0 else "#ff4b4b"
                    sign = "+" if pnl_val > 0 else ""
                    
                    week_cols[idx].markdown(
                        f"""
                        <div style="background-color: {bg_color}; border: 1px solid {text_color}; border-radius: 8px; padding: 8px; text-align: center; min-height: 70px;">
                            <span style="font-size: 12px; color: #aaa;">{day}</span><br>
                            <span style="font-size: 13px; font-weight: bold; color: {text_color};">{sign}${pnl_val:,.0f}</span><br>
                            <span style="font-size: 10px; color: #888;">{trd_val} trade</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                else:
                    week_cols[idx].markdown(
                        f"""
                        <div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 8px; text-align: center; min-height: 70px;">
                            <span style="font-size: 12px; color: #666;">{day}</span><br>
                            <span style="font-size: 11px; color: #444;">No Trade</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

    st.markdown("---")

    # --- GRAFIK & TABEL RIWAYAT ---
    st.subheader("📊 Equity Curve")
    df_chart = df.sort_values(by="tanggal", ascending=True).reset_index(drop=True)
    df_chart["Kumulatif PnL"] = df_chart["pnl"].cumsum()
    st.line_chart(df_chart.set_index("tanggal")["Kumulatif PnL"])

    st.subheader("📋 Riwayat Trade")
    st.dataframe(df.sort_values(by="id", ascending=False), use_container_width=True)

    if st.button("Hapus Semua Data"):
        cursor.execute("DELETE FROM trades")
        conn.commit()
        st.rerun()
else:
    st.info("Belum ada data trade. Silakan masukkan data melalui form di sidebar.")
    

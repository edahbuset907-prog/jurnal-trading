import sqlite3
import pandas as pd
import streamlit as st
import calendar
from datetime import datetime

st.set_page_config(page_title="Jurnal Trading", layout="wide")

# Fungsi untuk load data dengan cache yang bisa di-clear
@st.cache_data(ttl=1)
def load_data():
    conn = sqlite3.connect("journal_trading.db", check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM trades", conn)
    conn.close()
    if not df.empty:
        df['tanggal'] = pd.to_datetime(df['tanggal'])
    return df

st.title("📈 Jurnal Trading")

# Sidebar Input
with st.sidebar.form("input_form", clear_on_submit=True):
    tanggal_input = st.date_input("Tanggal", value=datetime.today())
    instrumen = st.selectbox("Instrumen", ["XAUUSD", "NASDAQ"])
    pnl_input = st.number_input("PnL ($)", value=0.0, step=10.0)
    if st.form_submit_button("Simpan Trade"):
        conn = sqlite3.connect("journal_trading.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO trades (tanggal, instrumen, pnl) VALUES (?, ?, ?)", 
                       (str(tanggal_input), instrumen, pnl_input))
        conn.commit()
        conn.close()
        st.rerun()

# Ambil data
df = load_data()

if not df.empty:
    # --- KALENDER PNL ---
    st.subheader("📅 PnL Calendar")
    
    # Filter Tahun/Bulan
    tahun = st.selectbox("Tahun", [2026, 2025], index=0)
    bln = st.selectbox("Bulan", range(1,13), format_func=lambda x: calendar.month_name[x], index=datetime.now().month-1)
    
    df_m = df[(df['tanggal'].dt.month == bln) & (df['tanggal'].dt.year == tahun)]
    daily = df_m.groupby(df_m['tanggal'].dt.day)['pnl'].sum()
    
    # Grid kalender 7 kolom
    cols = st.columns(7)
    for i, day in enumerate(calendar.Calendar().itermonthdays(tahun, bln)):
        if day == 0: continue
        with cols[i % 7]:
            val = daily.get(day, 0)
            color = "#00ff80" if val > 0 else ("#ff4b4b" if val < 0 else "#666")
            st.markdown(f"""<div style="border:1px solid {color}; padding:5px; text-align:center;">
                        <b>{day}</b><br><small style="color:{color}">${val:,.0f}</small></div>""", 
                        unsafe_allow_html=True)
    
    st.markdown("---")
    st.line_chart(df.groupby('tanggal')['pnl'].sum().cumsum())
else:
    st.write("Belum ada data. Tambahkan trade di sidebar.")
    import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Jurnal Trading", layout="wide")
st.title("📈 Jurnal Trading")

# Koneksi Database
conn = sqlite3.connect("journal_trading.db", check_same_thread=False)

# Sidebar Input (Sama seperti sebelumnya)
with st.sidebar.form("input_form", clear_on_submit=True):
    tanggal_input = st.date_input("Tanggal", value=datetime.today())
    instrumen = st.selectbox("Instrumen", ["XAUUSD", "NASDAQ"])
    pnl_input = st.number_input("PnL ($)", value=0.0)
    if st.form_submit_button("Simpan"):
        cursor = conn.cursor()
        cursor.execute("INSERT INTO trades (tanggal, instrumen, pnl) VALUES (?, ?, ?)", 
                       (str(tanggal_input), instrumen, pnl_input))
        conn.commit()
        st.rerun()

# Membaca Data
df = pd.read_sql_query("SELECT * FROM trades", conn)

if not df.empty:
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    
    # --- PENGGANTI KALENDER (Tabel Ringkasan Harian) ---
    st.subheader("📅 Rekap PnL Harian")
    
    # Mengelompokkan data berdasarkan tanggal
    df_daily = df.groupby(df['tanggal'].dt.date)['pnl'].sum().reset_index()
    df_daily = df_daily.sort_values('tanggal', ascending=False)
    
    # Menampilkan dalam bentuk tabel yang mudah dibaca di HP
    st.dataframe(df_daily, use_container_width=True)
    
    # Grafik Pertumbuhan
    st.subheader("📊 Equity Curve")
    st.line_chart(df.groupby('tanggal')['pnl'].sum().cumsum())

    if st.button("Hapus Semua Data"):
        conn.cursor().execute("DELETE FROM trades")
        conn.commit()
        st.rerun()
else:
    st.info("Belum ada data. Tambahkan trade di sidebar.")
    
    

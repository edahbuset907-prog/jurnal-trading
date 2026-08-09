import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Jurnal Trading XAUUSD (Permanen)", layout="wide")

# Konfigurasi Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# GANTI teks di bawah ini dengan nama file .json yang kamu upload ke GitHub
creds = ServiceAccountCredentials.from_json_keyfile_name('nama_file_json_kamu.json', scope)
client = gspread.authorize(creds)
sheet = client.open('JurnalTradingXAUUSD').sheet1

st.title("📈 Jurnal Trading XAUUSD (Permanen di Google Sheets)")

# Sidebar Input
with st.sidebar.form("trade_form", clear_on_submit=True):
    tanggal = str(st.date_input("Tanggal"))
    tipe = st.selectbox("Tipe", ["BUY", "SELL"])
    lot = st.number_input("Lot", value=0.10)
    entry = st.number_input("Entry", value=2000.0)
    exit_price = st.number_input("Exit", value=2010.0)
    catatan = st.text_area("Catatan")
    submitted = st.form_submit_button("Simpan ke Google Sheets")

    if submitted:
        pnl = (exit_price - entry) * lot * 100 if tipe == "BUY" else (entry - exit_price) * lot * 100
        sheet.append_row([tanggal, tipe, lot, entry, exit_price, pnl, catatan])
        st.success("Data berhasil tersimpan!")

# Tampilkan Data
data = sheet.get_all_records()
if data:
    df = pd.DataFrame(data)
    st.dataframe(df)
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
    # --- GRAFIK PERFORMA PNL ---
if not df.empty:
    st.subheader("📊 Grafik Performa PnL")
    # Membuat kolom PnL kumulatif untuk grafik garis
    df_chart = df.copy()
    df_chart = df_chart.sort_values(by="id", ascending=True)
    df_chart["Cumulative_PnL"] = df_chart["pnl"].cumsum()
    
    # Menampilkan grafik garis interaktif bawaan Streamlit
    st.line_chart(df_chart.set_index("id")["Cumulative_PnL"])
    st.markdown("---")
    # --- TAMBAHAN FITUR SESI MARKET DI PALING BAWAH ---
try:
  cursor.execute("ALTER TABLE trades ADD COLUMN sesi TEXT")
  conn.commit()
except:
  pass

# Jika ingin melihat rekap berdasarkan sesi di paling bawah:
df_sesi = pd.read_sql_query("SELECT * FROM trades", conn)
if not df_sesi.empty and "sesi" in df_sesi.columns:
  st.markdown("---")
  st.subheader("🌐 Performa Berdasarkan Sesi Market")
  sesi_summary = (
      df_sesi.groupby("sesi")
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
    
    

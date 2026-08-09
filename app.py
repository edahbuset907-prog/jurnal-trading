import pandas as pd
import streamlit as st

st.set_page_config(page_title="Pro Jurnal XAUUSD", layout="wide")

# --- 1. INISIALISASI DATA ---
if "data_trading" not in st.session_state:
    st.session_state.data_trading = []

# --- 2. SIDEBAR INPUT ---
with st.sidebar:
    st.header("📝 Input Trade")
    with st.form("input_form", clear_on_submit=True):
        sesi = st.selectbox("Sesi Market", ["Asia", "London", "New York"])
        pnl = st.number_input("Hasil ($)", step=1.0)
        submit = st.form_submit_button("Simpan Data")
        
        if submit:
            st.session_state.data_trading.append({"sesi": sesi, "pnl": pnl})
            st.rerun()

# --- 3. LOGIKA & PERHITUNGAN ---
st.title("📈 Jurnal Trading XAUUSD")

if st.session_state.data_trading:
    df = pd.DataFrame(st.session_state.data_trading)
    
    # --- Metrik Win Rate ---
    total_trade = len(df)
    win_trades = len(df[df['pnl'] > 0])
    win_rate = (win_trades / total_trade) * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trade", total_trade)
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Total Profit", f"${df['pnl'].sum():.2f}")
    
    # --- Tabel ---
    st.subheader("📊 Tabel Riwayat")
    st.dataframe(df, use_container_width=True)
    
    # --- Grafik Sesi ---
    st.subheader("🌐 Performa Berdasarkan Sesi")
    sesi_summary = df.groupby("sesi")["pnl"].sum().reset_index()
    st.bar_chart(sesi_summary.set_index("sesi"))
    
    # --- 4. BACKUP DATA (PALING BAWAH & AMAN) ---
    st.markdown("---")
    st.subheader("📥 Backup Data Jurnal")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Data ke CSV",
        data=csv_data,
        file_name="jurnal_xauusd_backup.csv",
        mime="text/csv"
    )
else:
    st.info("Belum ada data. Silakan input trade di sidebar kiri.")
    
    # Backup placeholder agar UI tetap rapi
    st.markdown("---")
    st.subheader("📥 Backup Data Jurnal")
    st.warning("Tombol download akan muncul setelah ada data.")
    

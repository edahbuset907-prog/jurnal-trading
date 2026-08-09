import pandas as pd
import streamlit as st

# --- 1. SETUP HALAMAN ---
st.set_page_config(
    page_title="Pro Trader Journal", page_icon="⚡", layout="wide"
)

# --- 2. CUSTOM CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    
    div.stButton > button {
        border-radius: 10px;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 10px 20px;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. HEADER ---
st.markdown(
    "<h1 style='text-align: center; color: #ffffff;'>⚡ PRO TRADER JOURNAL</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #9ca3af;'>Sistem pencatatan dan"
    " evaluasi performa trading.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- 4. STATISTIK ---
col1, col2, col3, col4 = st.columns(4)
with col1:
  st.metric("Total Trades", "42")
with col2:
  st.metric("Win Rate", "64.3%")
with col3:
  st.metric("Net Profit", "$1,850.00")
with col4:
  st.metric("Profit Factor", "1.85")

st.markdown("---")

# --- 5. FORM & TABEL ---
c_form, c_table = st.columns([1, 2])

with c_form:
  st.subheader("📝 Catat Posisi Baru")
  with st.form("form_trade"):
    pair = st.selectbox("Pair", ["XAUUSD", "EURUSD", "GBPUSD"])
    action = st.radio("Action", ["BUY", "SELL"], horizontal=True)
    lot = st.number_input("Lot Size", value=0.10, step=0.01)
    result = st.number_input("Hasil ($)", value=0.0)

    if st.form_submit_button("Simpan"):
      st.success("Berhasil disimpan!")

with c_table:
  st.subheader("📊 Riwayat Transaksi")
  df = pd.DataFrame({
      "Tanggal": ["08/08", "08/08", "07/08"],
      "Pair": ["XAUUSD", "EURUSD", "XAUUSD"],
      "Type": ["BUY", "SELL", "BUY"],
      "Hasil": ["+$240", "-$85", "+$410"],
      "Status": ["WIN", "LOSS", "WIN"],
  })
  st.dataframe(df, use_container_width=True, hide_index=True)
    

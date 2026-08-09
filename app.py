import sqlite3
import pandas as pd
import streamlit as st

st.title("DEBUG: Cek Database")

try:
    conn = sqlite3.connect("journal_trading.db", check_same_thread=False)
    # 1. Cek apakah tabel ada
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
    st.write("Tabel yang ditemukan di database:", tables)

    # 2. Coba baca semua data
    df = pd.read_sql_query("SELECT * FROM trades", conn)
    
    if df.empty:
        st.error("Tabel 'trades' ditemukan tapi KOSONG (0 data).")
    else:
        st.success(f"Data ditemukan! Jumlah baris: {len(df)}")
        st.dataframe(df)

except Exception as e:
    st.error(f"Terjadi error: {e}")
    

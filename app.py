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
    tanggal = st.date_input("Tanggal")
    instrumen = st.selectbox(
        "Pilih Instrumen", ["XAUUSD (Gold)", "NASDAQ (US100)"]
    )
    sesi = st.selectbox(
        "Sesi Trading", ["London", "New York", "Asia", "London / NY Overlap"]
    )
    tipe = st.selectbox("Tipe Posisi", ["BUY", "SELL"])

    # Nilai default lot dan harga disesuaikan berdasarkan instrumen yang dipilih
    lot = st.number_input(
        "Lot Size", min_value=0.01, step=0.01, value=0.10, format="%.2f"
    )

    # Petunjuk input harga di form
    st.markdown(
        "<small><i>*XAUUSD: Entry misal 2000.0 | NASDAQ: Entry misal 18000.0</i></small>",
        unsafe_allow_html=True,
    )
    entry = st.number_input(
        "Harga Entry", min_value=0.0, step=0.1, value=2000.0
    )
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
        # Kalkulasi PnL & Pips berdasarkan instrumen
        if "XAUUSD" in instrumen:
            # XAUUSD: 1 Lot = $100 per $1 pergerakan
            if tipe == "BUY":
                pips = (exit_price - entry) * 10
                pnl = (exit_price - entry) * lot * 100
            else:
                pips = (entry - exit_price) * 10
                pnl = (entry - exit_price) * lot * 100
        else:
            # NASDAQ (US100): Biasanya pergerakan $1 indeks = $20 per lot (tergantung broker, asumsi standar contract size $20/poin per lot)
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
                tanggal,
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

# Ringkasan Kinerja (Dashboard)
df = pd.read_sql_query("SELECT * FROM trades", conn)

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

    # Grafik Performa Equity & Persentase
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

    # Tabel Riwayat Trade & Tombol Download CSV
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
    if st.button("Hapus Semua Data"):
        cursor.execute("DELETE FROM trades")
        conn.commit()
        st.rerun()
else:
    st.info("Belum ada data trade. Silakan masukkan data di sidebar kiri.")
                

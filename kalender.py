import datetime
import pandas as pd
import streamlit as st

# Setup Konfigurasi Halaman
st.set_page_config(
    page_title="Kalender Ekonomi Forex Factory", page_icon="📅", layout="wide"
)

st.title("📅 Kalender Ekonomi Fundamental (Ala Forex Factory)")
st.markdown(
    "Pantau jadwal rilis berita penting berimpact tinggi untuk antisipasi"
    " pergerakan market (XAUUSD / Forex)."
)

# Simulasi/Contoh Data Kalender Ekonomi Real-time (Bisa diintegrasikan dengan API Forex/FMP nantinya)
# Untuk saat ini kita buat struktur data mingguan yang interaktif
data_dummy = [
    {
        "Waktu (WIB)": "2026-08-10 19:30",
        "Currency": "USD",
        "Event": "CPI m/m",
        "Impact": "High",
        "Actual": "-",
        "Forecast": "0.2%",
        "Previous": "0.1%",
    },
    {
        "Waktu (WIB)": "2026-08-11 14:00",
        "Currency": "GBP",
        "Event": "Employment Change",
        "Impact": "Medium",
        "Actual": "-",
        "Forecast": "15.2K",
        "Previous": "12.0K",
    },
    {
        "Waktu (WIB)": "2026-08-12 19:30",
        "Currency": "USD",
        "Event": "PPI m/m",
        "Impact": "Medium",
        "Actual": "-",
        "Forecast": "0.1%",
        "Previous": "0.0%",
    },
    {
        "Waktu (WIB)": "2026-08-13 01:00",
        "Currency": "USD",
        "Event": "FOMC Meeting Minutes",
        "Impact": "High",
        "Actual": "-",
        "Forecast": "-",
        "Previous": "-",
    },
    {
        "Waktu (WIB)": "2026-08-14 19:30",
        "Currency": "USD",
        "Event": "Retail Sales m/m",
        "Impact": "High",
        "Actual": "-",
        "Forecast": "0.4%",
        "Previous": "0.3%",
    },
]

df = pd.DataFrame(data_dummy)
df["Waktu (WIB)"] = pd.to_datetime(df["Waktu (WIB)"])

# --- SIDEBAR FILTER ---
st.sidebar.header("⚙️ Filter Kalender")
selected_impact = st.sidebar.multiselect(
    "Filter Impact (Dampak)",
    ["High", "Medium", "Low"],
    default=["High", "Medium"],
)
selected_curr = st.sidebar.multiselect(
    "Filter Mata Uang", ["USD", "EUR", "GBP", "AUD", "XAU"], default=["USD"]
)

# Terapkan Filter
if selected_impact:
  df = df[df["Impact"].isin(selected_impact)]
if selected_curr:
  df = df[df["Currency"].isin(selected_curr)]

# --- TAMPILAN UTAMA ---
st.markdown("---")
st.subheader("📊 Jadwal Berita Minggu Ini")

if not df.empty:
  # Fungsi pewarnaan sederhana untuk Impact di Streamlit menggunakan Markdown/Emoji
  def highlight_impact(val):
    if val == "High":
      return "🔴 High"
    elif val == "Medium":
      return "🟠 Medium"
    else:
      return "🟡 Low"

  df["Impact"] = df["Impact"].apply(highlight_impact)

  # Tampilkan tabel interaktif
  st.dataframe(df, use_container_width=True)
else:
  st.warning(
      "Tidak ada data berita yang sesuai dengan filter yang dipilih."
  )

# Informasi Tambahan
st.markdown("---")
st.info(
    "💡 **Tips Trader:** Hindari membuka posisi (terutama di pair XAUUSD)"
    " beberapa menit sebelum dan sesudah berita ber-impact **High (🔴)** rilis"
    " karena volatilitas tinggi."
)

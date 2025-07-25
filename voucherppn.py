import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# Setup akses ke Google Sheets
scope = ["https://docs.google.com/spreadsheets/d/", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["google"], scopes=scope)
client = gspread.authorize(credentials)

# ID Google Spreadsheet
sheet_id = "1THcWHs7BtY7mYtnVfy83TZnv3jgVu7hzBrZ_rn5_y_Y/edit?gid=492131202#gid=492131202"

# Coba buka spreadsheet
try:
    spreadsheet = client.open_by_key(sheet_id)
    st.success(f"✅ Berhasil membuka spreadsheet: {spreadsheet.title}")
except Exception as e:
    st.error("❌ Gagal membuka Google Spreadsheet. Pastikan Sheet ID benar dan service account sudah dibagikan akses.")
    st.stop()

# Tampilkan semua worksheet yang tersedia
worksheet_titles = [ws.title for ws in spreadsheet.worksheets()]
st.info(f"📄 Worksheet tersedia: {worksheet_titles}")

# Coba ambil worksheet satu per satu
try:
    voucher_sheet = spreadsheet.worksheet("OPSI 2 - Data Voucher")
    ticket_sheet = spreadsheet.worksheet("OPSI 2 - Riwayat Klaim Ticketin")
    hotel_sheet = spreadsheet.worksheet("OPSI 2 - Riwayat Klaim Hotel")
except Exception as e:
    st.error("❌ Gagal membuka salah satu worksheet. Pastikan nama worksheet sesuai.")
    st.exception(e)
    st.stop()

# Convert ke DataFrame
voucher_df = pd.DataFrame(voucher_sheet.get_all_records())
ticket_df = pd.DataFrame(ticket_sheet.get_all_records())
hotel_df = pd.DataFrame(hotel_sheet.get_all_records())

st.title("🎫 Dashboard Klaim Voucher SVMTT - Patra Niaga")

# Filter berdasarkan Kode Voucher
search = st.text_input("Cari Kode Voucher")
if search:
    filtered = voucher_df[voucher_df["Kode Voucher"].str.contains(search, case=False, na=False)]

    if not filtered.empty:
        st.subheader("📊 Analisa Voucher")
        st.dataframe(filtered)

        nominal = filtered["Nominal Voucher"].astype(float).sum()
        saldo = filtered["Sisa Saldo"].astype(float).sum()
        nomor_bc = ", ".join(filtered["Nomor BC"].astype(str).unique())

        st.metric("Total Nominal", f"Rp {nominal:,.0f}")
        st.metric("Total Sisa Saldo", f"Rp {saldo:,.0f}")
        st.markdown(f"**Nomor BC:** {nomor_bc}")

        # Pie Chart
        pie_df = pd.DataFrame({
            "Kategori": ["Terpakai", "Sisa"],
            "Jumlah": [nominal - saldo, saldo]
        })
        fig = px.pie(pie_df, names="Kategori", values="Jumlah", title="Distribusi Penggunaan Voucher")
        st.plotly_chart(fig)

        # Riwayat Klaim Ticketing
        st.subheader("🛫 Riwayat Klaim Ticketing")
        filtered_ticket = ticket_df[ticket_df["Kode Voucher"].str.contains(search, case=False, na=False)]
        st.dataframe(filtered_ticket[["Maskapai", "Tanggal Issued", "Kode Booking", "Rute", "Harga"]])

        # Riwayat Klaim Hotel
        st.subheader("🏨 Riwayat Klaim Hotel")
        filtered_hotel = hotel_df[hotel_df["Kode Voucher"].str.contains(search, case=False, na=False)]
        st.dataframe(filtered_hotel[["Nama Hotel", "Check-In", "Check-Out", "Harga"]])
    else:
        st.warning("⚠️ Kode voucher tidak ditemukan.")
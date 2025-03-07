import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from matplotlib.legend_handler import HandlerLine2D

sns.set(style='darkgrid')  # styling profesional

# Load data yang telah dibersihkan dari file notebook.ipynb
hari_df = pd.read_csv("cleaned_hari_data.csv")
jam_df = pd.read_csv("cleaned_jam_data.csv")

# Konversi tipe data tanggal
hari_df['dteday'] = pd.to_datetime(hari_df['dteday'])
jam_df['dteday'] = pd.to_datetime(jam_df['dteday'])

# Sidebar untuk filter tambahan
with st.sidebar:
    st.image('rental_sepeda.jpeg', use_container_width=True)
    st.subheader("📅 **Filter Data**")

    # Filter Rentang Waktu dengan Try-Excep
    min_date = hari_df['dteday'].min().date()
    max_date = hari_df['dteday'].max().date()

    try:
        start_date, end_date = st.date_input(
            "Pilih Rentang Waktu",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

        # Jika pengguna tidak memilih tanggal, maka gunakan nilai default
        if not start_date or not end_date:
            st.warning("Tanggal tidak dipilih, menggunakan rentang waktu default.")
            start_date, end_date = min_date, max_date

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memilih tanggal: {e}")
        start_date, end_date = min_date, max_date  # menggunakan nilai default jika terjadi error

    # Filter Musim (Season)
    season_options = hari_df['season'].unique().tolist()
    selected_season = st.selectbox("Pilih Musim", ["Semua"] + season_options)

    # Filter Cuaca (Weathersit)
    weather_options = hari_df['weathersit'].unique().tolist()
    selected_weather = st.selectbox("Pilih Kondisi Cuaca", ["Semua"] + weather_options)

    # Filter Tipe Pengguna (Casual vs Registered)
    user_type = st.radio("Pilih Jenis Pengguna", ["Semua", "Casual", "Registered"])

# Filter Data Sesuai Pilihan Pengguna
try:
    main_df = hari_df[
        (hari_df['dteday'] >= str(start_date)) & 
        (hari_df['dteday'] <= str(end_date))
    ]

    if selected_season != "Semua":
        main_df = main_df[main_df['season'] == selected_season]

    if selected_weather != "Semua":
        main_df = main_df[main_df['weathersit'] == selected_weather]

    if user_type == "Casual":
        main_df["cnt"] = main_df["casual"]
    elif user_type == "Registered":
        main_df["cnt"] = main_df["registered"]

except Exception as e:
    st.error(f"Terjadi kesalahan saat memfilter data: {e}")
    main_df = hari_df  # Jika error, maka gunakan seluruh data tanpa filter

# DASHBOARD TREND PENYEWAAN SEPEDA
st.title('📊 Bike Rental Dashboard 🚲✨')

casual_total = main_df['casual'].sum()
registered_total = main_df['registered'].sum()
total_rentals = main_df['cnt'].sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Casual User", value=f"{casual_total:,}")

with col2:
    st.metric(label="Registered User", value=f"{registered_total:,}")

with col3:
    st.metric(label="Total User", value=f"{total_rentals:,}")

st.divider()  # Garis pemisah agar tampilan lebih rapi



# Tren Harian Penyewaan Sepeda
st.subheader("Tren Harian Penyewaan Sepeda📈")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x='dteday', y='cnt', data=main_df, ax=ax, color=sns.color_palette("viridis")[2], marker="o")
ax.set_title("Tren Harian Penyewaan Sepeda")
ax.set_xlabel("Tanggal")
ax.set_ylabel("Jumlah Penyewaan")
plt.xticks(rotation=45)
st.pyplot(fig)

# JAM SIBUK PENYEWAAN SEPEDA
st.subheader("Jam Sibuk Penyewaan⏰")
jam_sibuk = jam_df.groupby('hr')['cnt'].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x='hr', y='cnt', data=jam_sibuk, marker="o", color=sns.color_palette("viridis")[4])
ax.set_title("Pola Peminjaman Sepeda per Jam")
ax.set_xlabel("Jam dalam Sehari")
ax.set_ylabel("Rata-rata Penyewaan")
ax.set_xticks(range(0, 24))
st.pyplot(fig)

# PADA HARI APA SEPEDA PALING BANYAK DIGUNAKAN
st.subheader("Pada Hari Apa Sepeda Paling Banyak Digunakan?📆")
hari_terbanyak = main_df.groupby("weekday")["cnt"].sum().reset_index().sort_values(by="cnt", ascending=True)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x="weekday", y="cnt", data=hari_terbanyak, palette="viridis", ax=ax)
ax.set_title("Penyewaan Sepeda Berdasarkan Hari (Ascending)")
ax.set_xlabel("Hari dalam Seminggu")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig)

# PENGARUH CUACA & MUSIM
st.subheader("Pengaruh Cuaca & Musim terhadap Penyewaan🌤️")

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='weathersit', y='cnt', data=main_df, palette="viridis", ax=ax)
ax.set_title("Jumlah Penyewa Berdasarkan Kondisi Cuaca")
ax.set_xlabel("Kondisi Cuaca")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='season', y='cnt', data=main_df, palette="viridis", ax=ax)
ax.set_title("Jumlah Penyewa Berdasarkan Musim")
ax.set_xlabel("Musim")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig)

# PERBANDINGAN HARI KERJA vs AKHIR PEKAN
st.subheader("Perbandingan Akhir Pekan vs Hari Kerja")
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x='workingday', y='cnt', data=main_df, palette="viridis", ax=ax)
ax.set_title("Penyewaan: Akhir Pekan vs Hari Kerja")
ax.set_xlabel("0 = Akhir Pekan, 1 = Hari Kerja")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig)

# Clustering Berdasarkan Waktu (Pagi, Siang, Sore, Malam)
def assign_time_cluster(hr):
    if 6 <= hr < 12:
        return "Pagi"
    elif 12 <= hr < 16:
        return "Siang"
    elif 16 <= hr < 20:
        return "Sore"
    else:
        return "Malam"

jam_df['time_cluster'] = jam_df['hr'].apply(assign_time_cluster)

# VISUALISASI PENYEWAAN SEPEDA BERDASARKAN WAKTU 
st.subheader("Pola Penyewaan Sepeda Berdasarkan Waktu⏳")

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x='time_cluster', y='cnt', data=jam_df, order=["Pagi", "Siang", "Sore", "Malam"], palette="viridis", ax=ax)

ax.set_title("Penyewaan Sepeda Berdasarkan Waktu", fontsize=14)
ax.set_xlabel("Waktu dalam Sehari", fontsize=12)
ax.set_ylabel("Jumlah Penyewaan", fontsize=12)

st.pyplot(fig)

st.caption("Copyright (c) Maxwell Massie")

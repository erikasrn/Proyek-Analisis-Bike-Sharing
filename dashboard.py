import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='dark')

#Membaca file yang akan digunakan
hour_df = pd.read_csv("/workspaces/erikadata/hour.csv")
# Mengubah tipe data di hour_df ke datetime
hour_df['dteday'] = pd.to_datetime(hour_df.dteday)

#Menghapus kolom instant, hum, temp, atemp, dan windspeed di hour_df
drop_col = ['instant','hum','temp','atemp', 'windspeed', 'casual', 'registered']
for i in hour_df.columns:
  if i in drop_col:
    hour_df.drop(labels=i, axis=1, inplace=True)

# Mengkonversi isi kolom agar mudah dipahami
# konversi season menjadi: 1:Spring, 2:Summer, 3:Fall, 4:Winter
hour_df.season.replace((1,2,3,4), ('Spring','Summer','Fall','Winter'), inplace=True)
# konversi mnth menjadi: 1:Jan, 2:Feb, 3:Mar, 4:Apr, 5:May, 6:Jun, 7:Jul, 8:Aug, 9:Sep, 10:Oct, 11:Nov, 12:Dec
hour_df.mnth.replace((1,2,3,4,5,6,7,8,9,10,11,12),('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'), inplace=True)
# konversi weather_situation menjadi: 1:Clear, 2:Misty, 3:Light_RainSnow 4:Heavy_RainSnow
hour_df.weathersit.replace((1,2,3,4), ('Clear/Partly Cloudy','Misty/Cloudy','Light Snow/Rain','Heavy Snow/Rain'), inplace=True)
# konversi weekday menjadi: 0:Sun, 1:Mon, 2:Tue, 3:Wed, 4:Thu, 5:Fri, 6:Sat
hour_df.weekday.replace((0,1,2,3,4,5,6), ('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'), inplace=True)
# konversi yr menjadi: 0:2011, 1:2012
hour_df.yr.replace((0,1), ('2011','2012'), inplace=True)
hour_df.head()

# fungsi yang menyatakan jumlah sepeda yang dirental di rentang jam dan tanggal tertentu di dashboard
def show_rent_by_date(df):
  st.subheader("Jumlah Sepeda yang Disewa Berdasarkan Tanggal")
  selected_date = st.date_input("Pilih Tanggal", value=pd.to_datetime(df['dteday']).min())
  filtered_df = df[df['dteday'] == pd.to_datetime(selected_date)]
  total_rent = filtered_df['cnt'].sum()
  st.markdown(f"#### Total Sepeda yang Disewa pada Tanggal {selected_date}: {total_rent}")
  # Menampilkan grafik jumlah sepeda yang disewa per jam pada tanggal yang dipilih
  hourly_rent = filtered_df.groupby('hr')['cnt'].sum()
  fig, ax = plt.subplots(figsize=(16, 8))
  ax.plot(hourly_rent.index, hourly_rent.values)
  ax.set_xlabel('Jam')
  ax.set_ylabel('Jumlah Sepeda Disewa')
  ax.set_title(f'Jumlah Sepeda yang Disewa Per Jam pada Tanggal {selected_date}')
  st.pyplot(fig)

#fungsi yang menyatakan jumlah sepeda yang dirental di musim tertentu di dashboard
def show_rent_by_season(df):
  """
  Menampilkan jumlah sepeda yang dirental di musim tertentu di dashboard.
  """
  st.subheader("Jumlah Sepeda yang Disewa Berdasarkan Musim")
  season_choice = st.selectbox("Pilih Musim", df['season'].unique())
  filtered_df = df[df['season'] == season_choice]
  total_rent = filtered_df['cnt'].sum()
  st.markdown(f"#### Total Sepeda yang Disewa pada Musim {season_choice}: {total_rent}")

  # Menampilkan grafik jumlah sepeda yang disewa per bulan di musim yang dipilih
  monthly_rent = filtered_df.groupby('mnth')['cnt'].sum()
  fig, ax = plt.subplots(figsize=(16, 8))
  ax.plot(monthly_rent.index, monthly_rent.values)
  ax.set_xlabel('Bulan')
  ax.set_ylabel('Jumlah Sepeda Disewa')
  ax.set_title(f'Jumlah Sepeda yang Disewa Per Bulan pada Musim {season_choice}')
  st.pyplot(fig)

# Streamlit app title
st.title('Bike Sharing Data Analysis Dashboard')

# Sidebar filters
st.sidebar.header('Filters')
selected_year = st.sidebar.selectbox('Select Year', hour_df['yr'].unique())
selected_month = st.sidebar.selectbox('Select Month', hour_df['mnth'].unique())
# Filter data berdasarkan pilihan user
filtered_df = hour_df[(hour_df['yr'] == selected_year) & (hour_df['mnth'] == selected_month)]
filtered_df

# Menambahkan fungsi show_rent_by_date ke dashboard
show_rent_by_date(hour_df)

#Menambahkan fungsi show_rent_by_season ke dashboard
show_rent_by_season(hour_df)

# Visualization 1: Trend Peminjaman Sepeda per jam Sesuai Bulan Yang Dipilih
st.subheader('Tren Peminjaman Sepeda Per Jam di' + ' '+ str(selected_month) + ' '+ str(selected_year))
hourly_counts = filtered_df['cnt'].groupby(filtered_df['hr']).sum()
plt.figure(figsize=(12, 3))
plt.plot(hourly_counts.index, hourly_counts.values)
plt.xlabel('Jam')
plt.ylabel('Jumlah')
plt.title('Grafik Trend Jumlah Penyewaan Per Jam')
st.pyplot(plt)


# Visualization 2: Jumlah Penyewaan Per Hari di Bulan Yang Dipilih
st.subheader('Jumlah Penyewaan Per Hari di' + ' '+ str(selected_month) + ' '+ str(selected_year))
daily_rentals = filtered_df['cnt'].groupby(filtered_df['weekday']).sum()
plt.figure(figsize=(8, 3))
weekday_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
daily_rentals = daily_rentals.reindex(weekday_order)
plt.bar(daily_rentals.index, daily_rentals.values)
plt.xlabel('Hari')
plt.ylabel('Total Penyewaan')
plt.title('Jumlah Penyewaan Per Hari')
st.pyplot(plt)


# Visualization 3: Korelasi Jumlah Peminjaman Sepeda dengan Musim dan Cuaca di Bulan Yang Dipilih
st.subheader('Korelasi Jumlah Peminjaman Sepeda dengan Musim dan Cuaca di ' + ' '+ str(selected_month) + ' '+ str(selected_year))
season_weather_rentals = filtered_df.groupby(['season', 'weathersit'])['cnt'].sum().unstack()
plt.figure(figsize=(10, 5))
sns.heatmap(season_weather_rentals, annot=True, fmt='.0f', cmap='viridis')
plt.title('Korelasi Jumlah Peminjaman Sepeda dengan Musim dan Cuaca')
plt.xlabel('Kondisi Cuaca')
plt.ylabel('Musim')
st.pyplot(plt)

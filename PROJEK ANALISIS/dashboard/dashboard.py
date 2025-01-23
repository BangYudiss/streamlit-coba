import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

df_day = pd.read_csv('../data/day.csv')
df_hour = pd.read_csv('../data/hour.csv')

# Ubah value kolom
season_mapping = {
    1: 'Spring',
    2: 'Summer',
    3: 'Fall',
    4: 'Winter'
}
yr_mapping = {
    0 : 2011,
    1 : 2012
}
mnth_mapping = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}
holiday_mapping = {
    0: 'No Holiday',
    1: 'Holiday'
}
weekday_mapping = {
    0: 'Sunday',
    1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday'
}
workingday_mapping = {
    0: 'No',
    1: 'Yes'
}
weathersit_mapping = {
    1: 'Sunny',
    2 : 'Cloudy',
    3 : 'Light snow',
    4 : 'Extreme'
}

def map_values(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    df['season'] = df['season'].map(season_mapping)
    df['yr'] = df['yr'].map(yr_mapping)
    df['yr'] = df['yr'].astype(int)
    df['mnth'] = df['mnth'].map(mnth_mapping)
    df['holiday'] = df['holiday'].map(holiday_mapping)
    df['weekday'] = df['weekday'].map(weekday_mapping)
    df['workingday'] = df['workingday'].map(workingday_mapping)
    df['weathersit'] = df['weathersit'].map(weathersit_mapping)
    df['temp'] = df['temp'] * 41           # Mengembalikan nilai asli kolom temp (normalisasi dengan 41)
    df['atemp'] = df['atemp'] * 50         # Mengembalikan nilai asli kolom atemp (normalisasi dengan 50)
    df['hum'] = df['hum'] * 100            # Mengembalikan nilai asli kolom hum (normalisasi dengan 100)
    df['windspeed'] = df['windspeed'] * 67 # Mengembalikan nilai asli kolom windspeed (normalisasi dengan 67)
    return df

# Ganti nilai kolom
df_day = map_values(df_day)
df_hour = map_values(df_hour)

# Merge
df_all = pd.merge(
    df_day,
    df_hour,
    on = 'dteday',
    how = 'left'
)

# Bikin daily penyewaan
def create_daily_rental_df(df):
    daily_rental_df = df.resample(rule='D', on='dteday').agg({
        'casual_x' : 'sum',
        'registered_x' : 'sum',
        'cnt_x' : 'sum' 
    }).reset_index()
    
    daily_rental_df.rename(columns={
        'casual_x' : 'Penyewaan tidak terdaftar',
        'registered_x' : 'Penyewaan terdaftar',
        'cnt_x' : "Penyewaan Total"
    }, inplace=True)
    
    return daily_rental_df

# Bikin daily_weather_order_df
weathersit_order = [
    'Sunny', 'Cloudy', 'Light snow', 'Extreme'
]
def create_daily_weather_order_df(df):
    daily_weather_order_df = df.groupby('weathersit_x').agg({
        'casual_x': 'sum',
        'registered_x': 'sum',
        'cnt_x': 'sum'
    }).reindex(weathersit_order).reset_index()

    daily_weather_order_df.rename(columns={
        'weathersit_x' : 'Cuaca',
        'casual_x': 'Penyewaan tidak terdaftar',
        'registered_x': 'Penyewaan terdaftar',
        'cnt_x': "Penyewaan Total"
    }, inplace=True)
    return daily_weather_order_df

# Bikin hourly_weather_order_df
df_all['weathersit_y'] = pd.Categorical(df_all['weathersit_y'], categories=weathersit_order, ordered=True)
def create_hourly_weather_order_df(df):
    hourly_weather_order_df = df.groupby(['weathersit_y', 'yr_y']).agg({
        'cnt_y': 'mean'
    }).reset_index()
    return hourly_weather_order_df

#Bikin  Suhu dan kelembapan berdasarkan bulan
month_order = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]
def create_temp_hum_order_df(df):
    temp_hum_order_df = df.groupby('mnth_y').agg({
     'temp_y': 'mean',
     'atemp_y': 'mean',
     'hum_y': 'mean',
     'windspeed_y': 'mean'
    }).reindex(month_order).reset_index()
    return temp_hum_order_df


# Pengaruh cuaca terhadap penyewaan pada tiap tahun
weathersit_order = [
    'Sunny', 'Cloudy', 'Light snow', 'Extreme'
]

df_all['weathersit_y'] = pd.Categorical(df_all['weathersit_y'], categories=weathersit_order, ordered=True)
def create_weather_yr_order_df(df):
    weather_yr_order_df = df.groupby(['weathersit_y', 'yr_y']).agg({
        'cnt_y': 'mean'
    }).reset_index()
    return weather_yr_order_df

# Penyewaan sepeda pada tiap bulan
month_order = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]
df_all['mnth_x'] = pd.Categorical(df_all['mnth_x'], categories= month_order, ordered=True)
def create_rental_month_order_df(df):
    rental_month_order_df  = df.groupby(['mnth_x', 'yr_x']).agg({
        'cnt_x': 'sum'
    }).reset_index()
    return rental_month_order_df



# Filter data
min_date = df_all["dteday"].min()
max_date = df_all["dteday"].max()

## BIKIN SIDDEBAR
with st.sidebar:
    st.image('GAMBAR.png')
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = df_all[(df_all["dteday"] >= str(start_date)) & 
                (df_all["dteday"] <= str(end_date))]

# # Menyiapkan berbagai dataframe
daily_rental_df = create_daily_rental_df(main_df)
daily_weather_order_df = create_daily_weather_order_df(main_df)
hourly_weather_order_df = create_hourly_weather_order_df(main_df)
temp_hum_order_df = create_temp_hum_order_df(main_df)
weather_yr_order_df = create_weather_yr_order_df(main_df)
rental_month_order_df = create_rental_month_order_df(main_df)


st.header('Dashboard Penyewaan Sepeda')
st.caption('Dibuat oleh: **Ilham Yudistira**')
st.write('')
st.write('')

## Metric Jumlah Penyewaan
from babel.numbers import format_currency
col1, col2, col3, = st.columns(3)
with col1:

    total_casual = format_currency(daily_rental_df['Penyewaan tidak terdaftar'].sum(), currency='', locale= 'id_ID').split(',')[0] # memisah ketika bertemu koma, lalu mengambil index pertama dari array pemisah tadi
    st.metric('Total Penyewaan Tidak Terdaftar', total_casual)

with col2:
    total_registered = format_currency(daily_rental_df['Penyewaan terdaftar'].sum(), currency= '', locale= 'id_ID').split(',')[0] # memisah ketika bertemu k
    st.metric('Total Penyewaan Terdaftar', total_registered)

with col3:
    total_cnt = format_currency(daily_rental_df['Penyewaan Total'].sum(), currency='', locale= 'id_ID').split(',')[0] # memisah ketika bertemu
    st.metric('Total Penyewaan', total_cnt)

# Visualisasi berdasarkan cuaca
st.write('')
st.subheader("Cuaca")
st.write(daily_weather_order_df)
fig, ax = plt.subplots(figsize=(12,8))
sns.barplot(
    data = daily_weather_order_df.melt(
        id_vars=['Cuaca'], #variavle id / kolom patokan
        value_vars= ['Penyewaan tidak terdaftar', 'Penyewaan terdaftar'], # variable nilai / kolom yg dilebur
        var_name='Jenis Penyewaan', #nama variable / nama kolom hasil lebur
        value_name = 'Jumlah Penyewaan' # nama value / nama kolom buat nilai )
        ), 
    x = 'Cuaca',
    y = 'Jumlah Penyewaan',
    hue = 'Jenis Penyewaan', 

)
ax.set_title('Penyewaan Sepeda berdasarkan Cuaca', fontsize = 18, fontweight = 'bold')
st.pyplot(fig)
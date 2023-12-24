import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px

# Load dataset

df = pd.read_csv("dashboard/hour_cleaned.csv")
df['dteday'] = pd.to_datetime(df['dteday'])

st.set_page_config(page_title="Bike-sharing Dashboard",
                   page_icon="bar_chart:",
                   layout="wide")

# Mengubah kolom dan isinya

df['mnth'] = df['mnth'].map({
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
})

df['season'] = df['season'].map({
    1:'Winter', 2:'Spring', 3:'Summer', 4:'Fall'
})

df['weekday'] = df['weekday'].map({
    0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'
})
df['weathersit'] = df['weathersit'].map({
    1: 'Clear',
    2: 'Cloudy',
    3: 'Rainy',
    4: 'Weather'
})

# Membuat fungsi pendukung

def create_monthly_users_df(df):
    monthly_users_df = df.resample(rule='M', on='dteday').agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    monthly_users_df.index = monthly_users_df.index.strftime('%b-%y')
    monthly_users_df = monthly_users_df.reset_index()
    monthly_users_df.rename(columns={
        "dteday": "year_month",
        "cnt": "total_rides",
        "casual": "casual_rides",
        "registered": "registered_rides"
    }, inplace=True)
    
    return monthly_users_df

def create_seasonly_users_df(df):
    seasonly_users_df = df.groupby("season").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    seasonly_users_df = seasonly_users_df.reset_index()
    seasonly_users_df.rename(columns={
        "cnt": "total_rides",
        "casual": "casual_rides",
        "registered": "registered_rides"
    }, inplace=True)
    
    seasonly_users_df = pd.melt(seasonly_users_df,
                                      id_vars=['season'],
                                      value_vars=['casual_rides', 'registered_rides'],
                                      var_name='type_of_rides',
                                      value_name='count_rides')
    
    seasonly_users_df['season'] = pd.Categorical(seasonly_users_df['season'],
                                             categories=['Spring', 'Summer', 'Fall', 'Winter'])
    
    seasonly_users_df = seasonly_users_df.sort_values('season')
    
    return seasonly_users_df

def create_weekday_users_df(df):
    weekday_users_df = df.groupby("weekday").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    weekday_users_df = weekday_users_df.reset_index()
    weekday_users_df.rename(columns={
        "cnt": "total_rides",
        "casual": "casual_rides",
        "registered": "registered_rides"
    }, inplace=True)
    
    weekday_users_df = pd.melt(weekday_users_df,
                                      id_vars=['weekday'],
                                      value_vars=['casual_rides', 'registered_rides'],
                                      var_name='type_of_rides',
                                      value_name='count_rides')
    
    weekday_users_df['weekday'] = pd.Categorical(weekday_users_df['weekday'],
                                             categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    
    weekday_users_df = weekday_users_df.sort_values('weekday')
    
    return weekday_users_df

def create_hourly_users_df(df):
    hourly_users_df = df.groupby("hr").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    hourly_users_df = hourly_users_df.reset_index()
    hourly_users_df.rename(columns={
        "cnt": "total_rides",
        "casual": "casual_rides",
        "registered": "registered_rides"
    }, inplace=True)
    
    return hourly_users_df

# membuat filter

min_date = df["dteday"].min()
max_date = df["dteday"].max()

# membuat sidebar

st.sidebar.header ("Filter")

# mengambil start_date & end_date

start_date, end_date = st.date_input(
    label="Date Filter", min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# menghubungkan filter

main_df = df[
    (df["dteday"] >= str(start_date)) &
    (df["dteday"] <= str(end_date))
]

# memasukkan main_df ke fungsi yang sudah dibuat

monthly_users_df = create_monthly_users_df(main_df)
weekday_users_df = create_weekday_users_df(main_df)
seasonly_users_df = create_seasonly_users_df(main_df)
hourly_users_df = create_hourly_users_df(main_df)

# Halaman utama

st.title("Bike-Sharing Dashboard")


col1, col2, col3 = st.columns(3)

with col1:
    total_all_rides = main_df['cnt'].sum()
    st.metric("Total Rides", value=total_all_rides)
with col2:
    total_casual_rides = main_df['casual'].sum()
    st.metric("Total Casual Rides", value=total_casual_rides)
with col3:
    total_registered_rides = main_df['registered'].sum()
    st.metric("Total Registered Rides", value=total_registered_rides)

fig = px.line(monthly_users_df,
              x='year_month',
              y=['casual_rides', 'registered_rides', 'total_rides'],
              color_discrete_sequence=["green", "blue", "yellow"],
              markers=True,
              title="Count of Bikeshare Rides by Month").update_layout(xaxis_title='', yaxis_title='Total Rides')

st.plotly_chart(fig, use_container_width=True)

fig1 = px.bar(seasonly_users_df,
              x='season',
              y=['count_rides'],
              color='type_of_rides',
              color_discrete_sequence=["green", "blue", "yellow"],
              title='Count of Bikeshare Rides by Season').update_layout(xaxis_title='', yaxis_title='Total Rides')


fig2 = px.bar(weekday_users_df,
              x='weekday',
              y=['count_rides'],
              color='type_of_rides',
              barmode='group',
              color_discrete_sequence=["green", "blue", "yellow"],
              title='Count of Bikeshare Rides by Weekday').update_layout(xaxis_title='', yaxis_title='Total Rides')

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig1, use_container_width=True)
right_column.plotly_chart(fig2, use_container_width=True)

fig = px.line(hourly_users_df,
              x='hr',
              y=['casual_rides', 'registered_rides'],
              color_discrete_sequence=["green", "blue"],
              markers=True,
              title='Count of Bikeshare Rides by Hour of Day').update_layout(xaxis_title='', yaxis_title='Total Rides')

st.plotly_chart(fig, use_container_width=True)
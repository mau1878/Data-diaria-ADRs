import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime as dt
import streamlit as st

# List of tickers and shares outstanding data
tickers = [
    "GGAL", "YPF", "PAM", "TX", "CRESY", "SUPV", "CEPU", "BMA",
    "TGS", "EDN", "LOMA", "BBAR", "VIST", "MELI", "GLOB", "ARGT",
    "IRS", "TEO", "AGRO", "DESP", "BIOX", "SATL"
]

# Function to fetch data
def fetch_data(tickers, start_date):
    data = {}
    latest_dates = {}
    
    for ticker in tickers:
        # Fetch data
        stock_data = yf.Ticker(ticker)
        df = stock_data.history(start=start_date - dt.timedelta(days=30), end=start_date + dt.timedelta(days=1))
        df = df.dropna()

        # Ensure we have at least 2 days of data
        if len(df) < 2:
            print(f"Not enough data for {ticker}")
            continue
        
        # Select the latest two days (the selected day and the previous trading day)
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        # Calculate percentage price variation
        price_variation = (latest_data['Close'] - previous_data['Close']) / previous_data['Close'] * 100
        
        data[ticker] = {
            'price_variation': price_variation,
            'max_min_diff': (latest_data['High'] - latest_data['Low']) / latest_data['Low'] * 100,
            'close_open_diff': (latest_data['Close'] - latest_data['Open']) / latest_data['Open'] * 100
        }
        
        # Store the latest date for this ticker
        latest_dates[ticker] = latest_data.name

    return data, latest_dates

# Set the minimum and maximum dates for the calendar widget
min_date = dt.datetime(2000, 1, 1)
max_date = dt.datetime.now()

# Streamlit: User selects a date with a wider range
st.title("Data en USD de ADRs y otros papeles de WS de origen argentino para la fecha elegida (o de la rueda inmediatamente anterior a dicha fecha en caso de feriados o fines de semana. MTaurus - X: https://x.com/MTaurus_ok")
selected_date = st.date_input(
    "Choose a date",
    value=max_date,  # Default value to today's date
    min_value=min_date,  # Allow dates back to 2000
    max_value=max_date  # Up to the current date
)

# Fetch the data
try:
    data, latest_dates = fetch_data(tickers, selected_date)
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

# Clean data
def clean_data(data):
    clean_data = {}
    for ticker, d in data.items():
        if not np.isnan(d['price_variation']):
            clean_data[ticker] = d
    return clean_data

data = clean_data(data)

# Function to create bar plots
def create_bar_plot(data, metric, title, date):
    # Filter out tickers with no data or zero value for the metric
    data = {ticker: info for ticker, info in data.items() if not np.isnan(info[metric]) and info[metric] != 0}
    
    if not data:
        st.warning(f"No data to display for {title}")
        return
    
    # Convert data to DataFrame for easy plotting
    df = pd.DataFrame(data).T
    df = df.sort_values(by=metric, ascending=False)
    
    plt.figure(figsize=(14, 18))  # Increased height for better label visibility
    sns.barplot(x=df[metric], y=df.index, palette="viridis")
    plt.title(f"{title} (Data as of {date.strftime('%Y-%m-%d')})", fontsize=18)
    plt.xlabel(f'{metric} (%)', fontsize=16)
    plt.ylabel('Ticker', fontsize=16)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, linestyle='--', linewidth=0.7)
        # Add subtle watermark
    plt.text(0.5, 0.5, "MTaurus - X:MTaurus_ok", fontsize=12, color='gray',
             ha='center', va='center', alpha=0.5, transform=plt.gcf().transFigure)
    st.pyplot(plt)

# Create bar plots
try:
    latest_date = max(latest_dates.values())  # Get the most recent date among all tickers
    create_bar_plot(data, 'price_variation', 'Tickers with the Highest Percentage Increase', latest_date)
    create_bar_plot(data, 'max_min_diff', 'Tickers with the Highest Percentage Difference Between Max and Min Prices', latest_date)
    create_bar_plot(data, 'close_open_diff', 'Tickers with the Highest Percentage Difference Between Closing and Opening Prices', latest_date)
except Exception as e:
    st.error(f"Error creating plots: {e}")

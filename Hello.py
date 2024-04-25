import streamlit as st
import requests
import pandas as pd

# Set up the Streamlit page to refresh data every 300 seconds automatically
st.set_page_config(page_title='Stock Data Visualization', page_icon='📈', layout='wide')

# Your AlphaVantage API key
API_KEY = 'U3TZCD5BHFMG8QLG'

def fetch_stock_data(symbol, timespan='daily', interval='5min'):
    base_url = 'https://www.alphavantage.co/query?'
    params = {
        'function': 'TIME_SERIES_DAILY',  # Default function
        'symbol': symbol,
        'apikey': API_KEY,
        'datatype': 'json'
    }

    if timespan == 'intraday':
        params['function'] = 'TIME_SERIES_INTRADAY'
        params['interval'] = interval
    elif timespan == 'weekly':
        params['function'] = 'TIME_SERIES_WEEKLY'
    elif timespan == 'monthly':
        params['function'] = 'TIME_SERIES_MONTHLY'

    response = requests.get(base_url, params=params)
    data = response.json()
    
    # Check if there's an error message key in the response
    if 'Error Message' in data:
        st.error(f"Error fetching data for {symbol}: {data['Error Message']}")
        return pd.DataFrame()
    
    # Extract the time series data if no error
    try:
        time_series_key = [key for key in data.keys() if 'Time Series' in key][0]
        time_series = data.get(time_series_key, {})
        df = pd.DataFrame.from_dict(time_series, orient='index', dtype=float)
        df = df.rename(columns=lambda x: x.split(' ')[1] if len(x.split(' ')) > 1 else x)
        df.index = pd.to_datetime(df.index)
        return df
    except IndexError as e:
        st.error(f"Unexpected API response format for {symbol}: {data}")
        return pd.DataFrame()

def calculate_moving_average(df, window_size):
    """Calculate moving average of the 'close' prices."""
    return df['close'].rolling(window=window_size).mean()

def main():
    st.title('Stock Data Visualization and Analysis')
    # User inputs
    stock_symbols = st.sidebar.text_input("Enter Stock Symbols (comma-separated)", value='IBM')
    timespan = st.sidebar.selectbox("Choose Time Span", options=['daily', 'weekly', 'monthly', 'intraday'], index=0)
    interval = st.sidebar.selectbox("Select Interval", options=['1min', '5min', '15min', '30min', '60min'], index=1) if timespan == 'intraday' else None
    window_size = st.sidebar.number_input("Moving Average Window Size", min_value=1, max_value=200, value=20)
    
    symbols = stock_symbols.split(',')
    
    full_data = []
    
    for symbol in symbols:
        symbol = symbol.strip().upper()  # Clean up any extra whitespace/characters
        df = fetch_stock_data(symbol, timespan, interval)
        
        if not df.empty:
            # Ensure that there is more than one element after split, otherwise return the original column name
            df = df.rename(columns=lambda x: x.split(' ')[1] if len(x.split(' ')) > 1 else x)
            df.index = pd.to_datetime(df.index)
            st.write(f"Data for {symbol}")

            # Display raw data
            st.dataframe(df[['open', 'high', 'low', 'close']])
            
            # Calculate moving average
            df['MA'] = calculate_moving_average(df, window_size)
            
            # Append to full data
            full_data.append(df[['close', 'MA']])
        else:
            st.error(f"No data found for {symbol}. Please check the symbol or try again later.")
    
    if full_data:
        # Combine all data frames into one for plotting
        combined_data = pd.concat(full_data, axis=1)
        # Plotting the data with moving average
        st.line_chart(combined_data)
        
        st.write("The moving averages are shown in the chart as 'MA', which can help identify trends over the specified window size.")

if __name__ == "__main__":
    main()

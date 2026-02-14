import yfinance as yf
import streamlit as st
import pandas as pd

@st.cache_data
def load_data(ticker, start_date="2020-01-01"):
    """
    Fetches historical data for the given ticker from a specific start date.
    Args:
        ticker (str): Ticker symbol.
        start_date (str): Start date in 'YYYY-MM-DD' format.
    Returns:
        pd.DataFrame: DataFrame with Date, Open, High, Low, Close, Volume.
    """
    try:
        data = yf.download(ticker, start=start_date)
        
        # Flatten MultiIndex columns if present (common with recent yfinance versions)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        data.reset_index(inplace=True)
        
        # Ensure Date is datetime
        data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
        
        return data
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {e}")
        return pd.DataFrame()

def get_latest_price(ticker):
    """
    Fetches the single latest price for a ticker.
    """
    data = yf.download(ticker, period="1d")
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    if not data.empty:
        return data['Close'].iloc[-1]
    return None

def convert_to_inr(df_commodity, df_currency, unit_factor=1.0):
    """
    Converts commodity price (USD) to INR based on daily exchange rate.
    Args:
        df_commodity (pd.DataFrame): Data with 'Close' in USD.
        df_currency (pd.DataFrame): Data with 'Close' as USDINR rate.
        unit_factor (float): Multiplier for unit conversion (e.g., oz -> 10g).
    Returns:
        pd.DataFrame: DataFrame with 'Close' converted to INR.
    """
    # Merge on Date
    df_merged = pd.merge(df_commodity, df_currency[['Date', 'Close']], on='Date', how='inner', suffixes=('', '_INR'))
    
    # Calculate INR Price: Price(USD) * Exchange Rate * Unit Factor
    df_merged['Close'] = df_merged['Close'] * df_merged['Close_INR'] * unit_factor
    
    # Update High/Low if available (Assuming proportional change for simplicity in this scope)
    if 'High' in df_merged.columns:
        df_merged['High'] = df_merged['High'] * df_merged['Close_INR'] * unit_factor
    if 'Low' in df_merged.columns:
        df_merged['Low'] = df_merged['Low'] * df_merged['Close_INR'] * unit_factor
        
    return df_merged[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]


import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objs as go
from prophet import Prophet

def test_load():
    print("Downloading data...")
    data = yf.download("GC=F", period="5y")
    print("\n--- Raw Data Info ---")
    print(data.head())
    print("\nColumns:", data.columns)
    print("Index:", data.index)
    
    if isinstance(data.columns, pd.MultiIndex):
        print("\nDetected MultiIndex columns. Flattening...")
        data.columns = data.columns.get_level_values(0)
        print("New Columns:", data.columns)
    
    data.reset_index(inplace=True)
    print("\n--- Processed Data Info ---")
    print(data.head())
    print(data.iloc[-1])
    
    # Simulate the failing line
    try:
        current_price = data['Close'].iloc[-1]
        print(f"\nCurrent Price: {current_price}")
        print(f"Type of Current Price: {type(current_price)}")
        formatted = f"{current_price:.2f}"
        print(f"Formatted: {formatted}")
    except Exception as e:
        print(f"\nERROR simulating metric: {e}")

if __name__ == "__main__":
    test_load()

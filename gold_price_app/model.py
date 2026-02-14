from prophet import Prophet
import pandas as pd
import numpy as np

def train_model(df):
    """
    Trains a Prophet model on the historical data.
    """
    # Prepare data for Prophet
    df_train = df[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
    
    # Initialize and train model
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(df_train)
    return model

def predict_future(model, periods):
    # Ensure last_date is a Timestamp for arithmetic
    last_date = pd.to_datetime(model.history['ds'].max())
    
    # Calculate future dates
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods, freq='D')
    
    future = pd.DataFrame({'ds': future_dates})
    future = pd.concat([model.history[['ds']], future], ignore_index=True)
    forecast = model.predict(future)
    return forecast

def predict_specific_date(model, date_str):
    """
    Predicts price for a specific date (YYYY-MM-DD).
    Returns the predicted price (yhat).
    """
    future_date = pd.to_datetime(date_str)
    
    # created a dataframe with just this date
    future_df = pd.DataFrame({'ds': [future_date]})
    
    forecast = model.predict(future_df)
    
    if not forecast.empty:
        return forecast['yhat'].iloc[0], forecast['yhat_lower'].iloc[0], forecast['yhat_upper'].iloc[0]
    return None, None, None

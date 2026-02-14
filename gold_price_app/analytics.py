import pandas as pd
import calendar

def get_monthly_stats(df, month, year):
    """
    Filters data for a specific month and year, and calculates stats.
    Args:
        df (pd.DataFrame): Historical data.
        month (str): Month name (e.g., 'January').
        year (int): Year (e.g., 2023).
    Returns:
        dict: Stats including total increase/decrease, high, low, trend.
        pd.DataFrame: Filtered data for that month.
    """
    # Map month name to number
    month_num = list(calendar.month_name).index(month)
    
    # Filter data
    # Ensure Date column is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    mask = (df['Date'].dt.month == month_num) & (df['Date'].dt.year == year)
    df_filtered = df.loc[mask].copy()
    
    if df_filtered.empty:
        return None, pd.DataFrame()
        
    # Calculate stats
    first_price = df_filtered['Close'].iloc[0]
    last_price = df_filtered['Close'].iloc[-1]
    highest = df_filtered['High'].max()
    lowest = df_filtered['Low'].min()
    
    price_change = last_price - first_price
    trend = "Uptrend" if price_change > 0 else "Downtrend"
    
    stats = {
        'start_price': first_price,
        'end_price': last_price,
        'change': price_change,
        'highest': highest,
        'lowest': lowest,
        'trend': trend
    }
    
    return stats, df_filtered

def get_yearly_analysis(df, year):
    """
    Calculates month-wise price changes for a specific year.
    Args:
        df (pd.DataFrame): Historical data.
        year (int): Year.
    Returns:
        pd.DataFrame: Monthly aggregation with 'Month', 'Change', 'Highest', 'Lowest'.
        dict: Best and Worst performing months.
    """
    df['Date'] = pd.to_datetime(df['Date'])
    mask = (df['Date'].dt.year == year)
    df_year = df.loc[mask].copy()
    
    if df_year.empty:
        return pd.DataFrame(), {}
    
    results = []
    
    for m in range(1, 13):
        month_name = calendar.month_name[m]
        mask_month = (df_year['Date'].dt.month == m)
        df_month = df_year.loc[mask_month]
        
        if not df_month.empty:
            start = df_month['Close'].iloc[0]
            end = df_month['Close'].iloc[-1]
            change = end - start
            results.append({
                'Month': month_name,
                'Change': change,
                'Highest': df_month['High'].max(),
                'Lowest': df_month['Low'].min()
            })
            
    results_df = pd.DataFrame(results)
    
    if results_df.empty:
        return results_df, {}

    best_month = results_df.loc[results_df['Change'].idxmax()]
    worst_month = results_df.loc[results_df['Change'].idxmin()]
    
    summary = {
        'best_month': best_month['Month'],
        'best_change': best_month['Change'],
        'worst_month': worst_month['Month'],
        'worst_change': worst_month['Change']
    }
    
    return results_df, summary

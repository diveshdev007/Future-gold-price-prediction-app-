import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import date
import calendar

# Custom modules
from data_loader import load_data, get_latest_price, convert_to_inr
from model import train_model, predict_specific_date
from analytics import get_monthly_stats, get_yearly_analysis

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(page_title="Future Gold & Silver Price Prediction", layout="wide", page_icon="📈")

# Custom CSS for Professional UI
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(to right, #ece9e6, #ffffff);
        color: #333;
    }
    
    /* Result Box Styling */
    .result-box {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #FFD700; /* Gold accent */
    }
    .result-title {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 10px;
    }
    .result-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .silver-box {
        border-left: 5px solid #C0C0C0; /* Silver accent */
    }
    
    /* Dashboard Cards */
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #888;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
    
    /* Titles */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to:", ["Date-wise Prediction", "Monthly Dashboard", "Yearly Analysis", "Forecast Trends"])

st.sidebar.markdown("---")
st.sidebar.info("System uses historical data + present market trends for accurate forecasting.")

# --- 3. HELPER: LOAD DATA ---
@st.cache_resource
def get_params_and_models():
    # Load data for both
    with st.spinner("Loading Market Data & Training Models..."):
        df_gold = load_data("GC=F", start_date="2020-01-01")
        df_silver = load_data("SI=F", start_date="2020-01-01")
        df_usdinr = load_data("USDINR=X", start_date="2020-01-01")
        
        # Train models once and cache (Model still runs on USD data for optimal stability)
        model_gold = train_model(df_gold)
        model_silver = train_model(df_silver)
        
    return df_gold, df_silver, df_usdinr, model_gold, model_silver

try:
    df_gold, df_silver, df_usdinr, model_gold, model_silver = get_params_and_models()
except Exception as e:
    st.error(f"Critical Error: {e}")
    st.stop()

# --- 4. MAIN SECTIONS ---

# ==========================================
# SECTION 1: DATE-WISE PREDICTION
# ==========================================
if section == "Date-wise Prediction":
    st.title("🔮 Date-wise Price Prediction")
    st.markdown("Predict the future price of Gold and Silver for any specific date.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        d_day = st.number_input("Day", min_value=1, max_value=31, value=date.today().day)
    with col2:
        d_month = st.selectbox("Month", list(calendar.month_name)[1:], index=date.today().month-1)
    with col3:
        d_year = st.number_input("Year", min_value=date.today().year, max_value=date.today().year+5, value=date.today().year)
        
    if st.button("Predict Price", type="primary"):
        # Construct date
        try:
            month_num = list(calendar.month_name).index(d_month)
            target_date = date(d_year, month_num, d_day)
            
            if target_date < date.today():
                st.warning("⚠️ You selected a past date. Showing historical estimate if available, or theoretical prediction.")
            
            # Predict (USD)
            pred_gold_usd, _, _ = predict_specific_date(model_gold, str(target_date))
            pred_silver_usd, _, _ = predict_specific_date(model_silver, str(target_date))
            
            # Convert to INR/1g using LATEST available exchange rate
            # Note: We use the latest known rate because predicting future exchange rate is a separate complex task.
            latest_usdinr = df_usdinr['Close'].iloc[-1]
            factor_1g = 1 / 31.1035
            
            pred_gold_inr = pred_gold_usd * latest_usdinr * factor_1g
            pred_silver_inr = pred_silver_usd * latest_usdinr * factor_1g
            
            st.markdown("---")
            st.subheader(f"Prediction for: {target_date.strftime('%d-%B-%Y')}")
            
            r_col1, r_col2 = st.columns(2)
            
            with r_col1:
                st.markdown(f"""
                <div class="result-box">
                    <div class="result-title">Gold Price (INR/1g)</div>
                    <div class="result-value">₹ {pred_gold_inr:,.2f}</div>
                    <small>Based on current USDINR rate (~₹{latest_usdinr:.2f})</small>
                </div>
                """, unsafe_allow_html=True)
                
            with r_col2:
                st.markdown(f"""
                <div class="result-box silver-box">
                    <div class="result-title">Silver Price (INR/1g)</div>
                    <div class="result-value">₹ {pred_silver_inr:,.2f}</div>
                    <small>Based on current USDINR rate</small>
                </div>
                """, unsafe_allow_html=True)
                
        except ValueError:
            st.error("Invalid Date selected.")

# ==========================================
# SECTION 2: MONTHLY DASHBOARD
# ==========================================
elif section == "Monthly Dashboard":
    st.title("📊 Monthly Market Dashboard")
    
    c1, c2 = st.columns(2)
    with c1:
        m_month = st.selectbox("Select Month", list(calendar.month_name)[1:], index=date.today().month-1)
    with c2:
        m_year = st.number_input("Select Year", min_value=2020, max_value=date.today().year, value=date.today().year)
        
    if st.button("Show Dashboard"):
        # Convert to INR: Gold (oz -> 1g), Silver (oz -> 1g)
        # 1 oz = 31.1035 g. Factor for 1g = 1 / 31.1035
        
        factor_1g = 1 / 31.1035
        
        df_gold_inr = convert_to_inr(df_gold, df_usdinr, factor_1g)
        df_silver_inr = convert_to_inr(df_silver, df_usdinr, factor_1g)

        st.markdown("### Gold Market Analysis (INR/1g)")
        g_stats, g_data = get_monthly_stats(df_gold_inr, m_month, m_year)
        
        if g_stats:
            # Stats Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Highest Price", f"₹{g_stats['highest']:,.2f}")
            m2.metric("Lowest Price", f"₹{g_stats['lowest']:,.2f}")
            m3.metric("Total Change", f"₹{g_stats['change']:,.2f}", delta=g_stats['trend'])
            m4.metric("Trend", g_stats['trend'])
            
            # Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=g_data['Date'], y=g_data['Close'], mode='lines+markers', name='Gold Price', line=dict(color='#FFD700')))
            fig.update_layout(title=f"Gold Price (INR/1g) - {m_month} {m_year}", xaxis_title="Date", yaxis_title="Price (₹)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Gold data available for this month.")
            
        st.markdown("---")
        st.markdown("### Silver Market Analysis (INR/1g)")
        s_stats, s_data = get_monthly_stats(df_silver_inr, m_month, m_year)
        
        if s_stats:
            # Stats Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Highest Price", f"₹{s_stats['highest']:,.2f}")
            m2.metric("Lowest Price", f"₹{s_stats['lowest']:,.2f}")
            m3.metric("Total Change", f"₹{s_stats['change']:,.2f}", delta=s_stats['trend'])
            m4.metric("Trend", s_stats['trend'])
            
            # Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=s_data['Date'], y=s_data['Close'], mode='lines+markers', name='Silver Price', line=dict(color='#C0C0C0')))
            fig.update_layout(title=f"Silver Price (INR/1g) - {m_month} {m_year}", xaxis_title="Date", yaxis_title="Price (₹)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Silver data available for this month.")

# ==========================================
# SECTION 3: YEARLY ANALYSIS
# ==========================================
elif section == "Yearly Analysis":
    st.title("📅 Yearly Performance Analysis")
    
    y_year = st.number_input("Select Year", min_value=2020, max_value=date.today().year, value=date.today().year-1)
    
    if st.button("Show Yearly Analysis"):
        st.subheader(f"Gold Performance in {y_year}")
        g_res, g_sum = get_yearly_analysis(df_gold, y_year)
        
        if not g_res.empty:
            # Summary
            st.markdown(f"""
            **Best Month:** {g_sum['best_month']} (Change: +${g_sum['best_change']:.2f})  
            **Worst Month:** {g_sum['worst_month']} (Change: ${g_sum['worst_change']:.2f})
            """)
            
            # Bar Chart
            fig = go.Figure(data=[
                go.Bar(name='Price Change', x=g_res['Month'], y=g_res['Change'], marker_color=['#2ecc71' if x > 0 else '#e74c3c' for x in g_res['Change']])
            ])
            fig.update_layout(title=f"Monthly Gold Price Change ({y_year})", yaxis_title="Price Change ($)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found for this year.")
            
        st.markdown("---")
        st.subheader(f"Silver Performance in {y_year}")
        s_res, s_sum = get_yearly_analysis(df_silver, y_year)
        
        if not s_res.empty:
            # Summary
            st.markdown(f"""
            **Best Month:** {s_sum['best_month']} (Change: +${s_sum['best_change']:.2f})  
            **Worst Month:** {s_sum['worst_month']} (Change: ${s_sum['worst_change']:.2f})
            """)
            
            # Bar Chart
            fig = go.Figure(data=[
                go.Bar(name='Price Change', x=s_res['Month'], y=s_res['Change'], marker_color=['#2ecc71' if x > 0 else '#e74c3c' for x in s_res['Change']])
            ])
            fig.update_layout(title=f"Monthly Silver Price Change ({y_year})", yaxis_title="Price Change ($)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found for this year.")

# ==========================================
# SECTION 4: FORECAST TRENDS
# ==========================================
elif section == "Forecast Trends":
    st.title("📈 Forecast Trends")
    st.markdown("Projected price trends for Gold & Silver based on historical data.")
    
    # Selection for Timeframe
    period_option = st.radio("Select Forecast Period:", ["Next 1 Month (30 Days)", "Next 1 Year (365 Days)"], horizontal=True)
    
    periods = 30 if "1 Month" in period_option else 365
    
    if st.button(f"Generate Forecast ({periods} Days)"):
        with st.spinner("Generating Forecast..."):
            # Import helper just to be safe if not global, though likely is
            from model import predict_future
            
            # 1. Fetch Forecast (USD)
            # Returns dataframe with 'ds', 'yhat', 'yhat_lower', 'yhat_upper'
            fc_gold_usd = predict_future(model_gold, periods)
            fc_silver_usd = predict_future(model_silver, periods)
            
            # 2. Convert to INR/1g using LATEST Rate
            latest_usdinr = df_usdinr['Close'].iloc[-1]
            factor_1g = 1 / 31.1035
            
            # Apply conversion to relevant columns
            for df in [fc_gold_usd, fc_silver_usd]:
                df['yhat_inr'] = df['yhat'] * latest_usdinr * factor_1g
                df['yhat_lower_inr'] = df['yhat_lower'] * latest_usdinr * factor_1g
                df['yhat_upper_inr'] = df['yhat_upper'] * latest_usdinr * factor_1g
            
            # Filter for plotting: Last 180 days history + Future
            # Find the cutoff date for history
            # Use pd.Timestamp for robustness
            today_ts = pd.Timestamp.now().normalize()
            history_cutoff = today_ts - pd.Timedelta(days=180)
            
            # 3. Plotting Logic
            def plot_forecast(fc_df, title, color_line, color_fill):
                # Filter data for cleaner view
                plot_df = fc_df[fc_df['ds'] > history_cutoff]
                
                fig = go.Figure()
                
                # Confidence Interval (Upper/Lower)
                fig.add_trace(go.Scatter(
                    x=pd.concat([plot_df['ds'], plot_df['ds'][::-1]]),
                    y=pd.concat([plot_df['yhat_upper_inr'], plot_df['yhat_lower_inr'][::-1]]),
                    fill='toself',
                    fillcolor=color_fill,
                    line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo="skip",
                    showlegend=True,
                    name='Confidence Interval'
                ))
                
                # Main Trend Line
                fig.add_trace(go.Scatter(
                    x=plot_df['ds'],
                    y=plot_df['yhat_inr'],
                    mode='lines',
                    line=dict(color=color_line, width=2),
                    name='Projected Price'
                ))
                
                # Add a vertical line for "Today"
                # Convert timestamp to milliseconds to avoid direct Timestamp arithmetic in Plotly
                today_ms = today_ts.timestamp() * 1000
                fig.add_vline(x=today_ms, line_width=1, line_dash="dash", line_color="black", annotation_text="Today")
                
                fig.update_layout(
                    title=title,
                    xaxis_title="Date",
                    yaxis_title="Price (INR/1g)",
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                return fig
            
            # Plot Gold
            st.subheader("Gold Price Forecast (INR/1g)")
            fig_gold = plot_forecast(fc_gold_usd, f"Gold Price Forecast - Next {periods} Days", '#FFD700', 'rgba(255, 215, 0, 0.2)')
            st.plotly_chart(fig_gold, use_container_width=True)
            
            st.markdown("---")
            
            # Plot Silver
            st.subheader("Silver Price Forecast (INR/1g)")
            fig_silver = plot_forecast(fc_silver_usd, f"Silver Price Forecast - Next {periods} Days", '#C0C0C0', 'rgba(192, 192, 192, 0.2)')
            st.plotly_chart(fig_silver, use_container_width=True)
            
            st.success(f"Forecast generated based on trends from Jan 2020 to Present. (USDINR Rate: ~₹{latest_usdinr:.2f})")

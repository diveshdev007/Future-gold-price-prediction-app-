import sys
import os
import pandas as pd

# Add current directory to path
sys.path.append(os.getcwd())

from data_loader import load_data, convert_to_inr

def verify_conversion():
    print("Verifying INR Conversion...")
    
    # Load Data
    print("Loading data...")
    df_gold = load_data("GC=F", start_date="2023-01-01")
    df_usdinr = load_data("USDINR=X", start_date="2023-01-01")
    
    if df_gold.empty:
        print("❌ Gold data failed.")
    else:
        print(f"Gold Data: {len(df_gold)} rows.")
        print(df_gold[['Date', 'Close']].tail())

    if df_usdinr.empty:
        print("❌ USDINR data failed.")

    if df_gold.empty or df_usdinr.empty:
        return

    # Test Conversion (Gold 10g)
    # Factor: 10 / 31.1035
    factor = 10 / 31.1035
    df_inr = convert_to_inr(df_gold, df_usdinr, factor)
    
    if not df_inr.empty:
        print("Merged Data Head:")
        print(df_inr[['Date', 'Close']].head())
        
        last_usd = df_gold['Close'].iloc[-1]
        last_rate = df_usdinr['Close'].iloc[-1]
        last_price = df_inr['Close'].iloc[-1]
        
        print(f"DEBUG: Last USD Price: ${last_usd:.2f}")
        print(f"DEBUG: Last USDINR Rate: ₹{last_rate:.2f}")
        print(f"DEBUG: Factor (10g): {factor:.4f}")
        
        print(f"✅ Conversion successful.")
        print(f"Latest Gold Price (INR/10g): ₹{last_price:,.2f}")
        
        # Rough sanity check: Gold should be between 50k and 100k roughly
        if 50000 < last_price < 100000:
             print("✅ Price seems reasonable (50k - 100k range).")
        else:
             print("⚠️ Price seems out of expected range. Check factors.")
             
        print(f"Rows: {len(df_inr)}")
    else:
        print("❌ Conversion returned empty DataFrame.")

if __name__ == "__main__":
    verify_conversion()
